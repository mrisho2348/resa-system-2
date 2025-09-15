from calendar import month_name
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash, logout
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.timezone import now
from django.views import View
from django.utils.decorators import method_decorator
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.views.decorators.http import require_GET
from datetime import datetime, timedelta, date
from clinic.forms import LaboratoryOrderForm, StaffProfileForm
from clinic.models import (
    LaboratoryOrder, Reagent, Service, Staffs, Employee, EmployeeDeduction,
    SalaryChangeRecord
)


import logging
logger = logging.getLogger(__name__)



@login_required
def labtechnician_dashboard(request):
    total_lab_orders = LaboratoryOrder.objects.count()
    lab_pending = LaboratoryOrder.objects.filter(result__isnull=True).count()
    lab_completed = LaboratoryOrder.objects.exclude(result__isnull=True).count()

    # Reagent statistics
    reagents_expiring_soon = Reagent.objects.filter(
        expiration_date__range=(date.today(), date.today() + timedelta(days=30))
    ).count()
    
    reagents_out_of_stock = Reagent.objects.filter(remaining_quantity=0).count()
    reagents_low_stock = Reagent.objects.filter(
        remaining_quantity__lte=5, remaining_quantity__gt=0
    ).count()
    
    # Get detailed reagent data for notifications and tables
    low_stock_reagents = Reagent.objects.filter(
        remaining_quantity__lte=5, remaining_quantity__gt=0
    )
    
    expired_reagents = Reagent.objects.filter(
        expiration_date__lt=date.today()
    )
    
    expiring_soon_reagents = Reagent.objects.filter(
        expiration_date__range=(date.today(), date.today() + timedelta(days=30))
    )
    
    # Add calculated properties to reagents
    for reagent in low_stock_reagents:
        reagent.remaining_quantity_percentage = (reagent.remaining_quantity / reagent.quantity_in_stock) * 100
        reagent.is_expired = reagent.expiration_date < date.today() if reagent.expiration_date else False
        reagent.expiring_soon = reagent.expiration_date and (reagent.expiration_date - date.today()).days <= 30
    
    for reagent in expiring_soon_reagents:
        reagent.remaining_quantity_percentage = (reagent.remaining_quantity / reagent.quantity_in_stock) * 100
        reagent.days_until_expiry = (reagent.expiration_date - date.today()).days if reagent.expiration_date else None
    
    # Recent lab orders
    recent_lab_orders = LaboratoryOrder.objects.select_related(
        'patient', 'lab_test'
    ).order_by('-order_date')[:10]

    context = {
        'total_lab_orders': total_lab_orders,
        'lab_pending': lab_pending,
        'lab_completed': lab_completed,
        'reagents_expiring_soon': reagents_expiring_soon,
        'reagents_out_of_stock': reagents_out_of_stock,
        'reagents_low_stock': reagents_low_stock,
        'low_stock_reagents': low_stock_reagents,
        'expired_reagents': expired_reagents,
        'expiring_soon_reagents': expiring_soon_reagents,
        'pending_lab_orders_count': lab_pending,
        'recent_lab_orders': recent_lab_orders,
    }
    return render(request, "labtechnician_template/home_content.html", context)
    

def lab_dashboard_counts(request):
    """Return counts for lab orders and reagents in a single response"""
    if request.method == 'GET':
        # Lab order counts
        without_result = LaboratoryOrder.objects.filter(result__isnull=True).count()
        with_result = LaboratoryOrder.objects.filter(result__isnull=False).count()
        
        # Reagent counts
        today = timezone.now().date()
        expired = Reagent.objects.filter(expiration_date__lt=today).count()
        expiring_soon = Reagent.objects.filter(
            expiration_date__range=(today, today + timedelta(days=30))
        ).count()
        out_of_stock = Reagent.objects.filter(remaining_quantity=0).count()
        
        data = {
            "lab_orders": {
                "without_result": without_result,
                "with_result": with_result
            },
            "reagents": {
                "expired": expired,
                "expiring_soon": expiring_soon,
                "out_of_stock": out_of_stock
            }
        }
        return JsonResponse(data)

@login_required
def test_status_data(request):
    """API endpoint to get lab test status data for charts"""
    pending = LaboratoryOrder.objects.filter(result__isnull=True).count()
    completed = LaboratoryOrder.objects.exclude(result__isnull=True).count()
    
    data = {
        'labels': ['Pending Tests', 'Completed Tests'],
        'data': [pending, completed],
        'colors': ['#f39c12', '#27ae60']
    }
    
    return JsonResponse(data)

@login_required
def reagent_stock_data(request):
    """API endpoint to get reagent stock data for charts"""
    # Get top 10 reagents by stock level
    reagents = Reagent.objects.order_by('-remaining_quantity')[:10]
    
    labels = [reagent.name for reagent in reagents]
    stock_levels = [reagent.remaining_quantity for reagent in reagents]
    
    # Generate colors based on stock level
    colors = []
    for level in stock_levels:
        if level <= 2:
            colors.append('rgba(231, 76, 60, 0.8)')  # Red for critical
        elif level <= 5:
            colors.append('rgba(243, 156, 18, 0.8)')  # Orange for low
        else:
            colors.append('rgba(52, 152, 219, 0.8)')  # Blue for good
    
    data = {
        'labels': labels,
        'stockLevels': stock_levels,
        'colors': colors
    }
    
    return JsonResponse(data)

@login_required
def pending_tests(request):
    """View to show pending lab tests"""
    pending_tests = LaboratoryOrder.objects.filter(
        result__isnull=True
    ).select_related('patient', 'lab_test')
    
    context = {
        'tests': pending_tests,
        'page_title': 'Pending Lab Tests'
    }
    return render(request, 'labtechnician_template/pending_tests.html', context)

@login_required
def completed_tests(request):
    """View to show completed lab tests"""
    completed_tests = LaboratoryOrder.objects.exclude(
        result__isnull=True
    ).select_related('patient', 'lab_test')
    
    context = {
        'tests': completed_tests,
        'page_title': 'Completed Lab Tests'
    }
    return render(request, 'labtechnician_template/completed_tests.html', context)

@login_required
def reagent_expiring_soon(request):
    """View to show reagents expiring soon"""
    expiring_reagents = Reagent.objects.filter(
        expiration_date__range=(date.today(), date.today() + timedelta(days=30))
    )
    
    context = {
        'reagents': expiring_reagents,
        'page_title': 'Reagents Expiring Soon'
    }
    return render(request, 'labtechnician_template/expiring_reagents.html', context)

@login_required
def reagent_out_of_stock(request):
    """View to show out of stock reagents"""
    out_of_stock_reagents = Reagent.objects.filter(remaining_quantity=0)
    
    context = {
        'reagents': out_of_stock_reagents,
        'page_title': 'Out of Stock Reagents'
    }
    return render(request, 'labtechnician_template/out_of_stock_reagents.html', context)

@login_required
def reagent_low_stock(request):
    """View to show low stock reagents"""
    low_stock_reagents = Reagent.objects.filter(
        remaining_quantity__lte=5, remaining_quantity__gt=0
    )
    
    context = {
        'reagents': low_stock_reagents,
        'page_title': 'Low Stock Reagents'
    }
    return render(request, 'labtechnician_template/low_stock_reagents.html', context)

# ------------------------------
# LAB TECHNICIAN PROFILE VIEW
# ------------------------------
@login_required
def labTechnician_profile(request):
    user = request.user
    try:
        staff = Staffs.objects.get(admin=user, role='labTechnician')
        return render(request, 'labtechnician_template/profile.html', {'staff': staff})
    except Staffs.DoesNotExist:
        return render(request, 'labtechnician_template/profile.html', {'error': 'Lab Technician not found.'})

# ------------------------------
# PASSWORD CHANGE VIEW
# ------------------------------
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was successfully updated! Please log in again.")
            logout(request)
            if request.user.staff.work_place == 'kahama':
                return redirect('kahamahmis:kahama')
            return redirect('login')
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'labtechnician_template/change_password.html', {'form': form})

# ------------------------------
# EDIT PROFILE VIEW (CLASS-BASED)
# ------------------------------
@method_decorator(login_required, name='dispatch')
class EditStaffProfileView(View):
    template_name = 'labtechnician_template/edit_profile.html'

    def get(self, request, pk):
        staff = get_object_or_404(Staffs, id=pk, admin=request.user)
        form = StaffProfileForm(instance=staff)
        return render(request, self.template_name, {'form': form, 'staff': staff})

    def post(self, request, pk):
        staff = get_object_or_404(Staffs, id=pk, admin=request.user)
        form = StaffProfileForm(request.POST, request.FILES, instance=staff)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('lab_edit_staff_profile', pk=staff.id)
        return render(request, self.template_name, {'form': form, 'staff': staff})

# ------------------------------
# SINGLE STAFF DETAIL VIEW
# ------------------------------
@login_required
def single_staff_detail(request, staff_id):
    staff = get_object_or_404(Staffs, id=staff_id)
    context = {'staff': staff}
    return render(request, "labtechnician_template/staff_details.html", context)

# ------------------------------
# FETCH LAB COUNTS (WITH AND WITHOUT RESULT)
# ------------------------------
@login_required
def fetch_laborders_counts(request):
    current_technician = request.user.staff
    lab_orders = LaboratoryOrder.objects.filter(data_recorder=current_technician)

    with_result_count = lab_orders.exclude(result__isnull=True).exclude(result__exact='').count()
    without_result_count = lab_orders.filter(result__isnull=True).count() + lab_orders.filter(result__exact='').count()

    return JsonResponse({
        'with_result': with_result_count,
        'without_result': without_result_count,
    })

# ------------------------------
# EDIT LAB RESULT VIEW
# ------------------------------
@login_required
def edit_lab_result(request, lab_id):
    try:
        # Attempt to fetch the lab order
        lab_order = get_object_or_404(LaboratoryOrder, id=lab_id)

        if request.method == 'POST':
            form = LaboratoryOrderForm(request.POST, instance=lab_order)
            if form.is_valid():
                form.save()
                messages.success(request, "Lab result updated successfully.")
                return redirect('lab_todays_lab_results_view')
            else:
                messages.error(request, "Please correct the errors in the form.")
        else:
            form = LaboratoryOrderForm(instance=lab_order)

        return render(request, 'labtechnician_template/edit_lab_result.html', {
            'form': form,
            'lab_order': lab_order,
        })

    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        return redirect('lab_results_view')

# ------------------------------
# ALL LAB RESULTS VIEW
# ------------------------------
def lab_results_view(request):
    # Fetch lab records as usual
    lab_records = LaboratoryOrder.objects.select_related('patient', 'visit', 'lab_test').order_by('-created_at')

    # 1. Generate years range: (current_year - 5) to (current_year + 1)
    current_year = datetime.now().year
    years = list(range(current_year - 5, current_year + 2))  # +2 to include next year

    # 2. Generate months list like [(1, 'January'), ..., (12, 'December')]
    months = [(i, month_name[i]) for i in range(1, 13)]

    # 3. Fetch test names from Service model where department = 'Laboratory'
    test_names = Service.objects.filter(type_service="Laboratory").values_list('name', flat=True).distinct()
    
    context = {
        'lab_records': lab_records,
        'years': years,
        'months': months,
        'test_names': test_names,
    }
    return render(request, 'labtechnician_template/lab_results.html', context)


@login_required
def filter_lab_results_api(request):
    """
    Handles AJAX requests to filter laboratory results based on provided query parameters.

    This API endpoint accepts GET parameters to filter laboratory orders by test name, month, year, and payment form.
    It returns a JSON response containing the filtered lab records or an error message if the request is invalid or an exception occurs.

    Args:
        request (HttpRequest): The HTTP request object, expected to be an AJAX (XMLHttpRequest) GET request.

    Query Parameters:
        test_name (str, optional): Partial or full name of the laboratory test to filter by.
        month (int, optional): Month (1-12) to filter laboratory orders by order date.
        year (int, optional): Year to filter laboratory orders by order date.
        payment_form (str, optional): Payment form to filter laboratory orders by patient's payment method.

    Returns:
        JsonResponse: 
            - On success: JSON object with a list of filtered lab records under the 'lab_records' key.
            - On error: JSON object with an 'error' key and appropriate HTTP status code.
    """
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            test_name = request.GET.get('test_name')
            month = request.GET.get('month')
            year = request.GET.get('year')
            payment_form = request.GET.get('payment_form')

            filters = Q()
            if test_name:
                filters &= Q(name__name__icontains=test_name)
            # Only filter by month if year is also provided
            if year:
                filters &= Q(order_date__year=int(year))
                if month:
                    filters &= Q(order_date__month=int(month))
            elif month:
                # If year is not provided, ignore month filter to avoid ambiguity
                pass
            if payment_form:
                filters &= Q(patient__payment_form__icontains=payment_form)

            labs = LaboratoryOrder.objects.filter(filters).select_related('patient', 'visit', 'lab_test')

            data = []
            for lab in labs:
                data.append({
                    'lab_number': lab.lab_number,
                    'patient_name': f"{lab.patient.first_name} {lab.patient.middle_name} {lab.patient.last_name}",
                    'payment_form': lab.patient.payment_form,
                    'insurance_name': lab.patient.insurance_name,
                    'visit': lab.visit.vst,
                    'test_name': lab.lab_test.name,
                    'description': lab.description,
                    'order_date': lab.order_date.strftime('%Y-%m-%d'),
                    'status': 'Completed' if lab.result else 'Pending',
                    'cost': str(lab.cost),
                    'id': lab.id,
                })
            return JsonResponse({'lab_records': data})

        except Exception as e:
            logger.error(f"[FilterLabAPI] Error: {str(e)}", exc_info=True)
            return JsonResponse({'error': 'Something went wrong while filtering lab records.'}, status=500)

    return JsonResponse({'error': 'Invalid request type'}, status=400)

# ------------------------------
# TODAY'S LAB RESULTS VIEW
# ------------------------------
@login_required
def todays_lab_results_view(request):
    today = now().date()
    lab_records = LaboratoryOrder.objects.select_related('patient', 'visit', 'lab_test').filter(order_date=today).order_by('-created_at')
    return render(request, 'labtechnician_template/todays_lab_results.html', {
        'lab_records': lab_records,
        'today': today
    })

# ------------------------------
# REAGENT LIST VIEW
# ------------------------------
@login_required
def reagent_list(request):
    reagent_list = Reagent.objects.all()
    today = date.today()
        # Annotate each with days left
    for reagent in reagent_list:
        if reagent.expiration_date:
            reagent.days_left = (reagent.expiration_date - today).days
        else:
            reagent.days_left = None

    return render(request, 'labtechnician_template/manage_reagent_list.html', {
        'reagent_list': reagent_list,
      
    })

def reagent_counts_api(request):
    today = now().date()
    soon_threshold = today + timedelta(days=10)

    expired_count = Reagent.objects.filter(expiration_date__lt=today).count()
    expiring_soon_count = Reagent.objects.filter(expiration_date__gte=today, expiration_date__lte=soon_threshold).count()
    out_of_stock_count = Reagent.objects.filter(remaining_quantity__lte=0).count()

    return JsonResponse({
        'expired': expired_count,
        'expiring_soon': expiring_soon_count,
        'out_of_stock': out_of_stock_count,
    })

@login_required
def lab_reagent_expired(request):
    today = now().date()
    expired_reagents = Reagent.objects.filter(expiration_date__lt=today).order_by('expiration_date')
    context = {
        'reagents': expired_reagents,
        'title': 'Expired Reagents',
    }
    return render(request, 'labtechnician_template/reagent_expired_list.html', context)

@login_required
def lab_reagent_expiring_soon(request):
    today = date.today()
    ten_days_from_now = today + timedelta(days=10)
    reagents = Reagent.objects.filter(expiration_date__range=[today, ten_days_from_now])

    # Annotate each with days left
    for reagent in reagents:
        if reagent.expiration_date:
            reagent.days_left = (reagent.expiration_date - today).days
        else:
            reagent.days_left = None

    return render(request, 'labtechnician_template/reagent_expiring_soon_list.html', {'reagents': reagents})

@login_required
def lab_reagent_out_of_stock(request):
    out_of_stock_reagents = Reagent.objects.filter(remaining_quantity__lte=0).order_by('name')
    context = {
        'reagents': out_of_stock_reagents,
        'title': 'Out of Stock Reagents',
    }
    return render(request, 'labtechnician_template/reagent_out_of_stock_list.html', context)

# ------------------------------
# EMPLOYEE DETAIL VIEW
# ------------------------------
@login_required
def employee_detail(request):
    try:
        staff_member = request.user.staff
        employee = get_object_or_404(Employee, name=staff_member)
        employee_deductions = EmployeeDeduction.objects.filter(employee=employee)
        salary_change_records = SalaryChangeRecord.objects.filter(employee=employee)

        context = {
            'staff_member': staff_member,
            'employee': employee,
            'employee_deductions': employee_deductions,
            'salary_change_records': salary_change_records,
        }
    except (Staffs.DoesNotExist, Employee.DoesNotExist) as e:
        context = {'error': str(e)}

    return render(request, 'labtechnician_template/employee_detail.html', context)


@login_required
@require_GET
def technician_stats_api(request):
    """
    API endpoint to fetch laboratory statistics for the lab technician dashboard.
    Returns JSON with counts of lab orders and reagent inventory.
    """
    try:
        # Get the current user (lab technician)
        user = request.user
        
        # Calculate date ranges
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Lab Order Statistics
        lab_orders = LaboratoryOrder.objects.all()
        
        # Reagent Statistics
        reagents = Reagent.objects.all()
        
        # Calculate reagent inventory value properly
        total_inventory_value = 0
        for reagent in reagents:
            total_inventory_value += float(reagent.remaining_quantity) * float(reagent.price_per_unit)
        
        # Prepare statistics
        stats = {
            # Lab Order Counts
            'pending_orders': lab_orders.filter(result__isnull=True).count(),
            'completed_orders': lab_orders.filter(result__isnull=False).count(),
            'total_orders': lab_orders.count(),
            
            # Time-based Lab Order Counts
            'today_orders': lab_orders.filter(created_at__date=today).count(),
            'week_orders': lab_orders.filter(created_at__date__gte=week_ago).count(),
            'month_orders': lab_orders.filter(created_at__date__gte=month_ago).count(),
            
            # Reagent Counts
            'reagent_count': reagents.count(),
            'low_stock_reagents': reagents.filter(remaining_quantity__lte=5).count(),  # Assuming 5 or less is low stock
            'out_of_stock_reagents': reagents.filter(remaining_quantity=0).count(),
            
            # Expiring Reagents (within 30 days)
            'expiring_soon_reagents': reagents.filter(
                expiration_date__lte=today + timedelta(days=30),
                expiration_date__gte=today
            ).count(),
            
            # Expired Reagents
            'expired_reagents': reagents.filter(expiration_date__lt=today).count(),
            
            # Financial Metrics
            'total_revenue': float(lab_orders.aggregate(Sum('cost'))['cost__sum'] or 0),
            'pending_revenue': float(lab_orders.filter(result__isnull=True).aggregate(Sum('cost'))['cost__sum'] or 0),
            'completed_revenue': float(lab_orders.filter(result__isnull=False).aggregate(Sum('cost'))['cost__sum'] or 0),
            
            # Reagent Inventory Value (fixed calculation)
            'reagent_inventory_value': total_inventory_value,
            
            # Most Ordered Tests
            'popular_tests': list(lab_orders.values(
                'lab_test__name'
            ).annotate(
                count=Count('id')
            ).order_by('-count')[:5]),
            
            # Status
            'status': 'success',
            'timestamp': timezone.now().isoformat()
        }
        
        return JsonResponse(stats)
        
    except Exception as e:
        # Return safe default values in case of error
        return JsonResponse({
            'status': 'error',
            'message': str(e),
            'pending_orders': 0,
            'completed_orders': 0,
            'total_orders': 0,
            'today_orders': 0,
            'week_orders': 0,
            'month_orders': 0,
            'reagent_count': 0,
            'low_stock_reagents': 0,
            'out_of_stock_reagents': 0,
            'expiring_soon_reagents': 0,
            'expired_reagents': 0,
            'total_revenue': 0,
            'pending_revenue': 0,
            'completed_revenue': 0,
            'reagent_inventory_value': 0,
            'popular_tests': [],
            'timestamp': timezone.now().isoformat()
        }, status=500)


@login_required
@require_GET
def technician_notifications_api(request):
    """
    API endpoint to fetch notifications for the lab technician.
    Returns JSON with recent notifications.
    """
    try:
        # Get the current user
        user = request.user
        
        # Calculate date ranges
        today = timezone.now().date()
        
        # Get pending lab orders for notifications
        pending_orders = LaboratoryOrder.objects.filter(
            result__isnull=True
        ).order_by('-created_at')[:10]
        
        # Get low stock reagents for notifications
        low_stock_reagents = Reagent.objects.filter(
            remaining_quantity__lte=5,
            remaining_quantity__gt=0
        )[:5]
        
        # Get expiring soon reagents for notifications
        expiring_soon_reagents = Reagent.objects.filter(
            expiration_date__lte=today + timedelta(days=30),
            expiration_date__gte=today
        )[:5]
        
        # Get out of stock reagents for notifications
        out_of_stock_reagents = Reagent.objects.filter(
            remaining_quantity=0
        )[:5]
        
        # Build notifications list
        notifications = []
        
        # Add pending order notifications
        for order in pending_orders:
            notifications.append({
                'type': 'pending_order',
                'icon': 'fas fa-flask',
                'icon_color': 'text-warning',
                'title': 'Pending Lab Order',
                'details': f'{order.lab_test.name} for {order.patient.first_name} {order.patient.last_name}',
                'time_ago': get_time_ago(order.created_at),
                'link': reverse('lab_edit_lab_result', args=[order.id])  # Adjust this URL as needed
            })
        
        # Add low stock notifications
        for reagent in low_stock_reagents:
            notifications.append({
                'type': 'low_stock',
                'icon': 'fas fa-vial',
                'icon_color': 'text-warning',
                'title': 'Reagent Running Low',
                'details': f'{reagent.name} - {reagent.remaining_quantity} remaining',
                'time_ago': get_time_ago(reagent.updated_at),
                'link': reverse('lab_reagent_list')  # Adjust this URL as needed
            })
        
        # Add expiring soon notifications
        for reagent in expiring_soon_reagents:
            days_until_expiry = (reagent.expiration_date - today).days
            notifications.append({
                'type': 'expiring_soon',
                'icon': 'fas fa-calendar-times',
                'icon_color': 'text-danger',
                'title': 'Reagent Expiring Soon',
                'details': f'{reagent.name} expires in {days_until_expiry} days',
                'time_ago': get_time_ago(reagent.updated_at),
                'link': reverse('lab_reagent_expiring_soon')  # Adjust this URL as needed
            })
        
        # Add out of stock notifications
        for reagent in out_of_stock_reagents:
            notifications.append({
                'type': 'out_of_stock',
                'icon': 'fas fa-exclamation-triangle',
                'icon_color': 'text-danger',
                'title': 'Reagent Out of Stock',
                'details': f'{reagent.name} is out of stock',
                'time_ago': get_time_ago(reagent.updated_at),
                'link':  reverse('lab_reagent_out_of_stock')  # Adjust this URL as needed
            })
        
        # Sort notifications by time (most recent first)
        notifications.sort(key=lambda x: x['time_ago'], reverse=True)
        
        return JsonResponse({
            'status': 'success',
            'notifications': notifications[:10],  # Return only the 10 most recent
            'count': len(notifications)
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e),
            'notifications': [],
            'count': 0
        }, status=500)

def get_time_ago(timestamp):
    """
    Helper function to get a human-readable time ago string.
    """
    now = timezone.now()
    diff = now - timestamp
    
    if diff.days > 0:
        return f'{diff.days} days ago'
    elif diff.seconds >= 3600:
        return f'{diff.seconds // 3600} hours ago'
    elif diff.seconds >= 60:
        return f'{diff.seconds // 60} minutes ago'
    else:
        return 'Just now'

