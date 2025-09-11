import calendar
from collections import defaultdict
from datetime import  date, datetime, timedelta
from decimal import Decimal
from io import BytesIO
import json
from django.utils import timezone
import logging
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django.db.models import F
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.mail import send_mail
from clinic.forms import StaffProfileForm
from clinic.models import Consultation,  CustomUser, DiseaseRecode,  Medicine,  PathodologyRecord,  Procedure, Staffs
from django.db import IntegrityError
from django.db import transaction
from django.db import models
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views import View
from .models import  Activity, AmbulanceActivity, AmbulanceOrder, AmbulanceRoute, AmbulanceVehicleOrder, ClinicChiefComplaint, ConsultationNotes,  ConsultationOrder, Counseling,   Diagnosis, DischargesNotes, Employee, EmployeeDeduction, Equipment,  HealthRecord,  HospitalVehicle, ImagingRecord, LaboratoryOrder, MedicineBatch, MedicineDosage,  MedicineRoute, MedicineType, MedicineUnitMeasure, ObservationRecord, Order,  PatientVisits, PatientVital, Prescription, PrescriptionFrequency, Procedure, Patients,  Reagent,  Referral, SalaryChangeRecord, SalaryPayment,  Service, WalkInPrescription, WalkInVisit
from django.db.models import Max,Sum,Q,Count, F, Case, When, Value, CharField, Prefetch
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import logout
from weasyprint import HTML
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from django.db.models.functions import Concat, TruncDate, TruncWeek, TruncMonth
from django.contrib.postgres.aggregates import ArrayAgg
import os 
import xlwt
from django_mysql.models import GroupConcat

@login_required
def dashboard(request):
    # Count total records for different models
    total_patients_count = Patients.objects.count()
    total_medicines_count = Medicine.objects.count()
    total_lab_orders_count = LaboratoryOrder.objects.count()
    total_disease_records_count = DiseaseRecode.objects.count()
    total_services_count = Service.objects.count()

    # Fetch the most recently added patients (limit to 6)
    recently_added_patients = Patients.objects.order_by('-created_at')[:6]

    # Count staff by roles
    total_doctors_count = Staffs.objects.filter(role='doctor', work_place="resa").count()
    total_nurses_count = Staffs.objects.filter(role='nurse', work_place="resa").count()
    total_physiotherapists_count = Staffs.objects.filter(role='physiotherapist', work_place="resa").count()
    total_lab_technicians_count = Staffs.objects.filter(role='labTechnician', work_place="resa").count()
    total_pharmacists_count = Staffs.objects.filter(role='pharmacist', work_place="resa").count()
    total_receptionists_count = Staffs.objects.filter(role='receptionist', work_place="resa").count()

    # Prepare the context dictionary
    context = {
        'total_patients_count': total_patients_count,
        'total_medicines_count': total_medicines_count,
        'total_lab_orders_count': total_lab_orders_count,
        'total_disease_records_count': total_disease_records_count,
        'total_services_count': total_services_count,
        'recently_added_patients': recently_added_patients,
        'total_doctors_count': total_doctors_count,
        'total_nurses_count': total_nurses_count,
        'total_physiotherapists_count': total_physiotherapists_count,
        'total_lab_technicians_count': total_lab_technicians_count,
        'total_pharmacists_count': total_pharmacists_count,
        'total_receptionists_count': total_receptionists_count,
        # 'gender_based_monthly_counts': gender_based_monthly_counts,  # Uncomment and implement if needed
    }

    # Render the template with the context
    return render(request, "hod_template/home_content.html", context)


def get_earnings_data(request):
    try:
        today = date.today()
        current_month = today.month
        current_year = today.year

        def to_float(value):
            """Convert value to float safely"""
            try:
                return float(value)
            except (TypeError, ValueError):
                return 0.0

        def aggregate_earnings(querysets, field='cost'):
            earnings = {'insurance': 0.0, 'cash': 0.0, 'other': 0.0}
            for qs in querysets:
                # Insurance
                insurance = qs.filter(
                    patient__payment_form='insurance'
                ).aggregate(total=Sum(field))['total'] or 0.0
                earnings['insurance'] += to_float(insurance)
                
                # Cash
                cash = qs.filter(
                    patient__payment_form='cash'
                ).aggregate(total=Sum(field))['total'] or 0.0
                earnings['cash'] += to_float(cash)
                
                # Other payment forms
                other = qs.exclude(
                    patient__payment_form__in=['insurance', 'cash']
                ).aggregate(total=Sum(field))['total'] or 0.0
                earnings['other'] += to_float(other)
                
            return earnings

        def aggregate_walkin_earnings(queryset, field='total_price'):
            earnings = {'insurance': 0.0, 'cash': 0.0, 'other': 0.0}
            
            # Insurance
            insurance = queryset.filter(
                visit__customer__payment_form='insurance'
            ).aggregate(total=Sum(field))['total'] or 0.0
            earnings['insurance'] += to_float(insurance)
            
            # Cash
            cash = queryset.filter(
                visit__customer__payment_form='cash'
            ).aggregate(total=Sum(field))['total'] or 0.0
            earnings['cash'] += to_float(cash)
            
            # Other payment forms
            other = queryset.exclude(
                visit__customer__payment_form__in=['insurance', 'cash']
            ).aggregate(total=Sum(field))['total'] or 0.0
            earnings['other'] += to_float(other)
            
            return earnings

        def aggregate_order_earnings(queryset):
            earnings = {'insurance': 0.0, 'cash': 0.0, 'other': 0.0}
            
            # Insurance
            insurance = queryset.filter(
                patient__payment_form='insurance'
            ).aggregate(total=Sum('cost'))['total'] or 0.0
            earnings['insurance'] += to_float(insurance)
            
            # Cash
            cash = queryset.filter(
                patient__payment_form='cash'
            ).aggregate(total=Sum('cost'))['total'] or 0.0
            earnings['cash'] += to_float(cash)
            
            # Other payment forms
            other = queryset.exclude(
                patient__payment_form__in=['insurance', 'cash']
            ).aggregate(total=Sum('cost'))['total'] or 0.0
            earnings['other'] += to_float(other)
            
            return earnings

        def compile_total(data):
            return data['insurance'] + data['cash'] + data['other']

        # Get only paid orders and prescriptions
        paid_filter = {'status': 'Paid'}
        paid_prescription_filter = {'status': 'paid'}
        
        # Define hospital order types
        hospital_order_types = ['Laboratory', 'Procedure', 'Imaging', 'Consultation']
        
        # DAILY
        daily_orders = Order.objects.filter(
            order_date=today, 
            status='Paid',
            type_of_order__in=hospital_order_types
        )
        daily_prescription_qs = [
            Prescription.objects.filter(created_at__date=today, **paid_prescription_filter),
        ]
        daily_walkin_qs = WalkInPrescription.objects.filter(
            created_at__date=today, **paid_prescription_filter
        )

        daily_order_data = aggregate_order_earnings(daily_orders)
        daily_prescription_data = aggregate_earnings(daily_prescription_qs, field='total_price')
        daily_walkin_data = aggregate_walkin_earnings(daily_walkin_qs)

        # MONTHLY
        monthly_orders = Order.objects.filter(
            order_date__month=current_month, 
            order_date__year=current_year,
            status='Paid',
            type_of_order__in=hospital_order_types
        )
        monthly_prescription_qs = [
            Prescription.objects.filter(created_at__month=current_month, created_at__year=current_year, **paid_prescription_filter),
        ]
        monthly_walkin_qs = WalkInPrescription.objects.filter(
            created_at__month=current_month, created_at__year=current_year, **paid_prescription_filter
        )

        monthly_order_data = aggregate_order_earnings(monthly_orders)
        monthly_prescription_data = aggregate_earnings(monthly_prescription_qs, field='total_price')
        monthly_walkin_data = aggregate_walkin_earnings(monthly_walkin_qs)

        # YEARLY
        yearly_orders = Order.objects.filter(
            order_date__year=current_year,
            status='Paid',
            type_of_order__in=hospital_order_types
        )
        yearly_prescription_qs = [
            Prescription.objects.filter(created_at__year=current_year, **paid_prescription_filter),
        ]
        yearly_walkin_qs = WalkInPrescription.objects.filter(
            created_at__year=current_year, **paid_prescription_filter
        )

        yearly_order_data = aggregate_order_earnings(yearly_orders)
        yearly_prescription_data = aggregate_earnings(yearly_prescription_qs, field='total_price')
        yearly_walkin_data = aggregate_walkin_earnings(yearly_walkin_qs)

        # ALL-TIME
        alltime_orders = Order.objects.filter(
            status='Paid',
            type_of_order__in=hospital_order_types
        )
        alltime_prescription_qs = [
            Prescription.objects.filter(**paid_prescription_filter),
        ]
        alltime_walkin_qs = WalkInPrescription.objects.filter(**paid_prescription_filter)

        alltime_order_data = aggregate_order_earnings(alltime_orders)
        alltime_prescription_data = aggregate_earnings(alltime_prescription_qs, field='total_price')
        alltime_walkin_data = aggregate_walkin_earnings(alltime_walkin_qs)

        # Combine hospital and walk-in data
        def combine_hospital_walkin(hospital_data, walkin_data):
            return {
                'insurance': hospital_data['insurance'] + walkin_data['insurance'],
                'cash': hospital_data['cash'] + walkin_data['cash'],
                'other': hospital_data['other'] + walkin_data['other'],
                'walkin': compile_total(walkin_data),
                'total': compile_total(hospital_data) + compile_total(walkin_data),
            }

        return JsonResponse({
            'daily': {
                'hospital': combine_hospital_walkin(daily_order_data, daily_walkin_data),
                'prescription': {
                    'insurance': daily_prescription_data['insurance'],
                    'cash': daily_prescription_data['cash'],
                    'other': daily_prescription_data['other'],
                    'total': compile_total(daily_prescription_data),
                },
                'grand_total': compile_total(daily_order_data) + compile_total(daily_walkin_data) + compile_total(daily_prescription_data),
            },
            'monthly': {
                'hospital': combine_hospital_walkin(monthly_order_data, monthly_walkin_data),
                'prescription': {
                    'insurance': monthly_prescription_data['insurance'],
                    'cash': monthly_prescription_data['cash'],
                    'other': monthly_prescription_data['other'],
                    'total': compile_total(monthly_prescription_data),
                },
                'grand_total': compile_total(monthly_order_data) + compile_total(monthly_walkin_data) + compile_total(monthly_prescription_data),
            },
            'yearly': {
                'hospital': combine_hospital_walkin(yearly_order_data, yearly_walkin_data),
                'prescription': {
                    'insurance': yearly_prescription_data['insurance'],
                    'cash': yearly_prescription_data['cash'],
                    'other': yearly_prescription_data['other'],
                    'total': compile_total(yearly_prescription_data),
                },
                'grand_total': compile_total(yearly_order_data) + compile_total(yearly_walkin_data) + compile_total(yearly_prescription_data),
            },
            'alltime': {
                'hospital': combine_hospital_walkin(alltime_order_data, alltime_walkin_data),
                'prescription': {
                    'insurance': alltime_prescription_data['insurance'],
                    'cash': alltime_prescription_data['cash'],
                    'other': alltime_prescription_data['other'],
                    'total': compile_total(alltime_prescription_data),
                },
                'grand_total': compile_total(alltime_order_data) + compile_total(alltime_walkin_data) + compile_total(alltime_prescription_data),
            },
        })

    except Exception as e:
        logger.error(f"Error in get_earnings_data view: {str(e)}")
        return JsonResponse({'error': f'An error occurred while retrieving earnings data. {str(e)}'}, status=500)
    

def financial_chart_data(request):
    timeframe = request.GET.get('timeframe', 'daily')
    today = timezone.now()  # aware datetime
    data = {"labels": [], "hospital": [], "prescription": []}

    # --- DAILY ---
    if timeframe == 'daily':
        hours = range(8, 20)  # 8 AM to 8 PM
        for hour in hours:
            # Build aware start/end time for each hour
            start_time = timezone.make_aware(
                datetime.combine(today.date(), datetime.min.time()).replace(hour=hour)
            )
            end_time = start_time + timedelta(hours=1)

            # Hospital earnings
            hospital_earnings = (
                (LaboratoryOrder.objects.filter(order_date__gte=start_time, order_date__lt=end_time).aggregate(total=Sum('cost'))['total'] or 0) +
                (Procedure.objects.filter(order_date__gte=start_time, order_date__lt=end_time).aggregate(total=Sum('cost'))['total'] or 0) +
                (ImagingRecord.objects.filter(order_date__gte=start_time, order_date__lt=end_time).aggregate(total=Sum('cost'))['total'] or 0) +
                (ConsultationOrder.objects.filter(order_date__gte=start_time, order_date__lt=end_time).aggregate(total=Sum('cost'))['total'] or 0)
            )

            # Prescription earnings
            prescription_earnings = (
                Prescription.objects.filter(created_at__gte=start_time, created_at__lt=end_time)
                .aggregate(total=Sum('total_price'))['total'] or 0
            )

            data['labels'].append(f"{hour}:00")
            data['hospital'].append(float(hospital_earnings))
            data['prescription'].append(float(prescription_earnings))

    # --- MONTHLY ---
    elif timeframe == 'monthly':
        for week in range(1, 5):
            start_of_week = today - timedelta(days=today.weekday() + (week - 1) * 7)
            end_of_week = start_of_week + timedelta(days=6)

            # Make timezone-aware
            start_of_week = timezone.make_aware(datetime.combine(start_of_week.date(), datetime.min.time()))
            end_of_week = timezone.make_aware(datetime.combine(end_of_week.date(), datetime.max.time()))

            # Hospital earnings
            hospital_earnings = (
                (LaboratoryOrder.objects.filter(order_date__gte=start_of_week, order_date__lte=end_of_week).aggregate(total=Sum('cost'))['total'] or 0) +
                (Procedure.objects.filter(order_date__gte=start_of_week, order_date__lte=end_of_week).aggregate(total=Sum('cost'))['total'] or 0) +
                (ImagingRecord.objects.filter(order_date__gte=start_of_week, order_date__lte=end_of_week).aggregate(total=Sum('cost'))['total'] or 0) +
                (ConsultationOrder.objects.filter(order_date__gte=start_of_week, order_date__lte=end_of_week).aggregate(total=Sum('cost'))['total'] or 0)
            )

            # Prescription earnings
            prescription_earnings = (
                Prescription.objects.filter(created_at__gte=start_of_week, created_at__lte=end_of_week)
                .aggregate(total=Sum('total_price'))['total'] or 0
            )

            data['labels'].append(f"Week {week}")
            data['hospital'].append(float(hospital_earnings))
            data['prescription'].append(float(prescription_earnings))

    # --- YEARLY ---
    elif timeframe == 'yearly':
        for month in range(1, 13):
            start_of_month = datetime(today.year, month, 1)
            if month == 12:
                end_of_month = datetime(today.year + 1, 1, 1) - timedelta(days=1)
            else:
                end_of_month = datetime(today.year, month + 1, 1) - timedelta(days=1)

            # Make timezone-aware
            start_of_month = timezone.make_aware(datetime.combine(start_of_month.date(), datetime.min.time()))
            end_of_month = timezone.make_aware(datetime.combine(end_of_month.date(), datetime.max.time()))

            # Hospital earnings
            hospital_earnings = (
                (LaboratoryOrder.objects.filter(order_date__gte=start_of_month, order_date__lte=end_of_month).aggregate(total=Sum('cost'))['total'] or 0) +
                (Procedure.objects.filter(order_date__gte=start_of_month, order_date__lte=end_of_month).aggregate(total=Sum('cost'))['total'] or 0) +
                (ImagingRecord.objects.filter(order_date__gte=start_of_month, order_date__lte=end_of_month).aggregate(total=Sum('cost'))['total'] or 0) +
                (ConsultationOrder.objects.filter(order_date__gte=start_of_month, order_date__lte=end_of_month).aggregate(total=Sum('cost'))['total'] or 0)
            )

            # Prescription earnings
            prescription_earnings = (
                Prescription.objects.filter(created_at__gte=start_of_month, created_at__lte=end_of_month)
                .aggregate(total=Sum('total_price'))['total'] or 0
            )

            data['labels'].append(start_of_month.strftime('%b'))
            data['hospital'].append(float(hospital_earnings))
            data['prescription'].append(float(prescription_earnings))

    return JsonResponse(data)

class ActivityLogView(View):
    template_name = 'hod_template/activity_log.html'

    def get(self, request):
        """
        Display activity logs safely.
        Handles cases where related models are missing or unrelated to patients.
        """

        # === 1. Fetch activity log with related fields ===
        activities = (
            Activity.objects
            .select_related('user', 'patient', 'content_type')
            .order_by('-timestamp')[:500]  # Limit for performance
        )

        # === 2. Annotate safe display fields ===
        for activity in activities:
            # --- USER INFO ---
            activity.user_role = "System"
            activity.user_workplace = "N/A"

            if activity.user:
                staff_obj = getattr(activity.user, 'staff', None)
                if staff_obj:
                    activity.user_role = staff_obj.role or "N/A"
                    activity.user_workplace = staff_obj.work_place or "N/A"
                elif activity.user.is_superuser:
                    activity.user_role = "Administrator"
                    activity.user_workplace = "System"

            # --- PATIENT INFO (may not exist for some models) ---
            patient_obj = getattr(activity, 'patient', None)
            activity.patient_name = patient_obj.full_name if patient_obj else "N/A"
            activity.patient_mrn = patient_obj.mrn if patient_obj else "N/A"

            # --- CONTENT TYPE NAME (e.g., DiseaseRecord, Prescription) ---
            content_type_obj = getattr(activity, 'content_type', None)
            activity.content_type_name = content_type_obj.name if content_type_obj else "N/A"

            # --- SAFE CONTENT OBJECT STRING ---
            activity.safe_object_str = "N/A"
            if activity.content_type and activity.object_id:
                model_class = activity.content_type.model_class()

                if model_class:
                    try:
                        # Attempt to fetch the actual object
                        obj = model_class._base_manager.get(pk=activity.object_id)
                        activity.safe_object_str = str(obj)
                    except model_class.DoesNotExist:
                        activity.safe_object_str = "Object deleted"
                    except Exception:
                        activity.safe_object_str = "Object not found"
                else:
                    activity.safe_object_str = "Model not found"

        # === 3. Get users for dropdown filter (future use) ===
        User = get_user_model()
        users = User.objects.filter(
            Q(staff__isnull=False) | Q(is_superuser=True)
        ).distinct()

        # === 4. Render context ===
        context = {
            'activities': activities,
            'users': users,
        }
        return render(request, self.template_name, context)

class TodayActivitiesView(View):
    def get(self, request):
        today = timezone.now().date()
        activities = Activity.objects.filter(
            timestamp__date=today
        ).select_related('user', 'patient', 'content_type').order_by('-timestamp')[:20]
        
        results = []
        for activity in activities:
            # Get patient name if available
            patient_name = activity.patient.full_name if activity.patient and hasattr(activity.patient, 'full_name') else ''
            
            # Get staff/user name
            staff_name = ''
            if activity.user:
                if hasattr(activity.user, 'get_full_name'):
                    staff_name = activity.user.get_full_name()
                elif hasattr(activity.user, 'username'):
                    staff_name = activity.user.username
            
            # Get activity description based on type
            description = self.get_activity_description(activity)
            
            results.append({
                'type': activity.activity_type,
                'title': self.get_activity_title(activity),
                'description': description,
                'time': activity.timestamp.strftime("%I:%M %p"),
                'patient': patient_name,
                'staff': staff_name,
                'icon': self.get_icon(activity),
                'url': self.get_detail_url(activity)
            })
        
        return JsonResponse({'activities': results})
    
    def get_activity_title(self, activity):
        """Generate a human-readable title based on activity type"""
        activity_type = activity.activity_type
        model_name = activity.content_type.model_class().__name__ if activity.content_type else 'Record'
        
        titles = {
            'login': 'User Login',
            'logout': 'User Logout',
            'create': f'New {model_name} Created',
            'update': f'{model_name} Updated',
            'delete': f'{model_name} Deleted',
        }
        return titles.get(activity_type, 'Activity')
    
    def get_activity_description(self, activity):
        """Generate a description based on activity details"""
        if activity.activity_type in ['create', 'update', 'delete']:
            if activity.content_object:
                return f"{activity.content_type.name} - {str(activity.content_object)}"
            return f"{activity.content_type.name} record modified"
        
        if activity.activity_type in ['login', 'logout']:
            ip = activity.details.get('ip', '') if activity.details else ''
            return f"From IP: {ip}" if ip else "Authentication activity"
        
        return ""
    
    def get_icon(self, activity):
        """Get appropriate icon based on activity type and content type"""
        # First try content type specific icons
        if activity.content_type:
            model_icons = {
                'Patient': 'fa-user-injured',
                'Consultation': 'fa-user-md',
                'LaboratoryOrder': 'fa-vial',
                'Prescription': 'fa-prescription-bottle',
                'Procedure': 'fa-procedures',
                'ImagingRecord': 'fa-x-ray',
                'Payment': 'fa-credit-card',
                'Invoice': 'fa-file-invoice',
                'Employee': 'fa-user-tie',
                'Medicine': 'fa-pills',
            }
            
            model_name = activity.content_type.model_class().__name__
            if model_name in model_icons:
                return model_icons[model_name]
        
        # Fallback to activity type icons
        activity_icons = {
            'login': 'fa-sign-in-alt',
            'logout': 'fa-sign-out-alt',
            'create': 'fa-plus-circle',
            'update': 'fa-edit',
            'delete': 'fa-trash-alt',
        }
        return activity_icons.get(activity.activity_type, 'fa-tasks')
    
    def get_detail_url(self, activity):
        """Generate URL to the detail view of the related object"""
        if not activity.content_type or not activity.object_id:
            return '#'
        
        model_name = activity.content_type.model
        obj_id = activity.object_id
        
        # Map content types to detail URLs
        url_patterns = {
            'patient': f"/patients/{obj_id}",
            'consultation': f"/consultations/{obj_id}",
            'laboratoryorder': f"/laboratory/orders/{obj_id}",
            'prescription': f"/pharmacy/prescriptions/{obj_id}",
            'procedure': f"/procedures/{obj_id}",
            'imagingrecord': f"/imaging/{obj_id}",
            'invoice': f"/billing/invoices/{obj_id}",
            'employee': f"/hr/employees/{obj_id}",
            'medicine': f"/inventory/medicines/{obj_id}",
        }
        
        # Try direct match first
        if model_name in url_patterns:
            return url_patterns[model_name]
        
        # Try plural versions (Django often uses plural model names in URLs)
        plural_model = f"{model_name}s"
        if plural_model in url_patterns:
            return url_patterns[plural_model]
        
        # Fallback for unknown models
        return '#'
        

def get_monthly_earnings_by_year(request):
    try:
        year = int(request.GET.get('year', datetime.today().year))
        print(year)
        def monthly_insurance_totals(model, date_field, value_field):
            monthly = {
                'nhif': [0] * 12,
                'cash': [0] * 12,
                'other': [0] * 12
            }

            for month in range(1, 13):
                # NHIF totals
                nhif_qs = model.objects.filter(
                    **{
                        f"{date_field}__year": year,
                        f"{date_field}__month": month,
                        "patient__payment_form": "Insurance",
                        "patient__insurance_name__icontains": "nhif"
                    }
                )
                monthly['nhif'][month - 1] = nhif_qs.aggregate(total=Sum(value_field))['total'] or 0

                # Cash totals
                cash_qs = model.objects.filter(
                    **{
                        f"{date_field}__year": year,
                        f"{date_field}__month": month,
                        "patient__payment_form": "Cash"
                    }
                )
                monthly['cash'][month - 1] = cash_qs.aggregate(total=Sum(value_field))['total'] or 0

                # Other Insurance totals (not NHIF)
                other_qs = model.objects.filter(
                    **{
                        f"{date_field}__year": year,
                        f"{date_field}__month": month,
                        "patient__payment_form": "Insurance"
                    }
                ).exclude(patient__insurance_name__icontains="nhif")
                monthly['other'][month - 1] = other_qs.aggregate(total=Sum(value_field))['total'] or 0

            return monthly

        hospital_nhif = [0] * 12
        hospital_cash = [0] * 12
        hospital_other = [0] * 12

        hospital_sources = [
            (LaboratoryOrder, 'order_date', 'cost'),
            (Procedure, 'order_date', 'cost'),
            (ImagingRecord, 'order_date', 'cost'),
            (ConsultationOrder, 'order_date', 'cost')
        ]

        for model, date_field, value_field in hospital_sources:
            monthly = monthly_insurance_totals(model, date_field, value_field)
            hospital_nhif = [x + y for x, y in zip(hospital_nhif, monthly['nhif'])]
            hospital_cash = [x + y for x, y in zip(hospital_cash, monthly['cash'])]
            hospital_other = [x + y for x, y in zip(hospital_other, monthly['other'])]

        presc_monthly = monthly_insurance_totals(Prescription, 'created_at', 'total_price')

        return JsonResponse({
            'hospital_nhif': hospital_nhif,
            'hospital_cash': hospital_cash,
            'hospital_other': hospital_other,
            'prescription_nhif': presc_monthly['nhif'],
            'prescription_cash': presc_monthly['cash'],
            'prescription_other': presc_monthly['other']
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def admin_profile(request):
    # Get the logged-in user
    user = request.user
    
    try:
        # Fetch the admin's details from the Staffs model
        staff = Staffs.objects.get(admin=user, role='admin')
        
        # Pass the admin details to the template
        return render(request, 'hod_template/profile.html', {'staff': staff})

    except Staffs.DoesNotExist:
        # In case no admin data is found, return an error message
        return render(request, 'hod_template/profile.html', {'error': 'Admin not found.'})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Prevent user logout before redirecting
            messages.success(request, "Your password was successfully updated! Please log in again.")
            logout(request)  # Log out the user
            
            # Redirect based on workplace
            if request.user.staff.work_place == 'kahama':
                return redirect('kahamahmis:kahama')  # Redirect to Kahama login page
            else:
                return redirect('login')  # Redirect to default login page (Resa)

        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'hod_template/change_password.html', {'form': form})       

@method_decorator(login_required, name='dispatch')
class EditStaffProfileView(View):
    template_name = 'hod_template/edit_profile.html'

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
            return redirect('hod_edit_staff_profile', pk=staff.id)         

    
def get_gender_yearly_data(request):
    if request.method == 'GET':
        selected_year = request.GET.get('year')
        
        # Query the database to get the total number of male and female patients for the selected year
        male_count = Patients.objects.filter(gender='Male', created_at__year=selected_year).count()
        female_count = Patients.objects.filter(gender='Female', created_at__year=selected_year).count()

        # Create a dictionary with the total male and female counts
        yearly_gender_data = {
            'Male': male_count,
            'Female': female_count
        }

        return JsonResponse(yearly_gender_data)
    else:
        # Return an error response if the request method is not GET or if it's not an AJAX request
        return JsonResponse({'error': 'Invalid request'})
    
def get_gender_monthly_data(request):
    if request.method == 'GET':
        selected_year = request.GET.get('year')       
        # Initialize a dictionary to store gender-wise monthly data
        gender_monthly_data = {}

        # Loop through each month and calculate gender-wise counts
        for month in range(1, 13):
            # Get the number of males and females for the current month and year
            male_count = Patients.objects.filter(
                gender='Male',
                created_at__year=selected_year,
                created_at__month=month
            ).count()            
            female_count = Patients.objects.filter(
                gender='Female',
                created_at__year=selected_year,
                created_at__month=month
            ).count()

            # Store the counts in the dictionary
            month_name = calendar.month_name[month]
            gender_monthly_data[month_name] = {'Male': male_count, 'Female': female_count}

        return JsonResponse(gender_monthly_data)
    else:
        return JsonResponse({'error': 'Invalid request'})


@login_required
def manage_patient(request):
    patient_records=Patients.objects.all().order_by('-created_at')   
    return render(request,"hod_template/manage_patients.html", {
        "patients":patient_records,     
        })
    



@login_required
def manage_disease(request):
    disease_records=DiseaseRecode.objects.all() 
    return render(request,"hod_template/manage_disease.html",{"disease_records":disease_records})

@login_required
def manage_staff(request):     
    # Retrieve all staff and order by joining_date or created_at
    staffs = Staffs.objects.all().order_by('created_at')  # Change 'joining_date' to 'created_at' if that's what you use

    return render(request, "hod_template/manage_staff.html", {"staffs": staffs})



@login_required
def resa_report(request):
    return render(request,"hod_template/resa_reports.html")

@login_required
def manage_service(request):
    services=Service.objects.all()   
    context = {
        'services':services,       
    }
    return render(request,"hod_template/manage_service.html",context)


@login_required
def reports_adjustments(request):
    return render(request,"hod_template/reports_adjustments.html")

@login_required
def reports_by_visit(request):
    return render(request,"hod_template/reports_by_visit.html")

@login_required
def reports_comprehensive(request):
    return render(request,"hod_template/reports_comprehensive.html")

@login_required
def reports_patients_visit_summary(request):
    return render(request,"hod_template/reports_patients_visit_summary.html")

@login_required
def reports_patients(request):
    return render(request,"hod_template/reports_patients.html")

@login_required
def reports_service(request):
    return render(request,"hod_template/reports_service.html")

@login_required
def reports_stock_ledger(request):
    return render(request,"hod_template/reports_stock_ledger.html")

def reports_stock_level(request):
    return render(request,"hod_template/reports_stock_level.html")

@login_required
def reports_orders(request):
    return render(request,"hod_template/reports_orders.html")

@login_required
def individual_visit(request):
    return render(request,"hod_template/reports_individual_visit.html")

@login_required
def product_summary(request):
    return render(request,"hod_template/product_summary.html")

@login_required
def manage_pathodology(request):
    pathodology_records=PathodologyRecord.objects.all()    
    return render(request,"hod_template/manage_pathodology.html",{
        "pathodology_records":pathodology_records,        
        })

@login_required
def health_record_list(request):
    records = HealthRecord.objects.all()
    return render(request, 'hod_template/healthrecord_list.html', {'records': records})

@login_required
@csrf_exempt
def save_health_record(request):
    if request.method == 'POST':
        try:
            # Extract data from POST request
            name = request.POST.get('name').strip()
            health_record_id = request.POST.get('health_record_id')
            
            if health_record_id:  # If health record ID is provided, it's an edit operation
                # Get the existing health record object
                health_record = HealthRecord.objects.get(pk=health_record_id)
                
                # Check if the provided name already exists in the database
                if HealthRecord.objects.exclude(pk=health_record_id).filter(name=name).exists():
                    return JsonResponse({'success': False, 'message': f'A record with the name "{name}" already exists.'})
                
                # Update the existing health record
                health_record.name = name
                health_record.save()
            else:  # If no health record ID is provided, it's an add operation
                # Check if the provided name already exists in the database
                if HealthRecord.objects.filter(name=name).exists():
                    return JsonResponse({'success': False, 'message': f'A record with the name "{name}" already exists.'})
                
                # Create a new health record
                HealthRecord.objects.create(name=name)
            
            # Return success response
            return JsonResponse({'success': True, 'message': 'Successfully saved.'})
        except Exception as e:
            # Return error response if an exception occurs
            return JsonResponse({'success': False, 'message': str(e)})
    else:
        # Return error response for invalid requests
        return JsonResponse({'success': False, 'message': 'Invalid request'})

    
    
@require_POST
def delete_healthrecord(request):
    try:
        health_record_id = request.POST.get('health_record_id')

        if not health_record_id:
            return JsonResponse({
                'success': False,
                'message': 'Missing health record ID.'
            })

        # Fetch the record
        health_record = get_object_or_404(HealthRecord, pk=health_record_id)

        # Store name before deletion
        record_name = health_record.name

        # Delete the record
        health_record.delete()

        return JsonResponse({
            'success': True,
            'message': f'Health record "{record_name}" deleted successfully.'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {e}'
        })

logger = logging.getLogger(__name__)

@csrf_exempt
@login_required
def save_staff_view(request):
    if request.method == 'POST':
        try:
            # Retrieve form data from the POST request
            first_name = request.POST.get('firstName')
            middle_name = request.POST.get('middleName')
            lastname = request.POST.get('lastname') 
            first_name = first_name.capitalize() if first_name else None
            middle_name = middle_name.capitalize() if middle_name else None
            last_name = lastname.capitalize() if lastname else None           
            gender = request.POST.get('gender')
            dob = request.POST.get('dob')
            phone = request.POST.get('phone')
            profession = request.POST.get('profession')            
            marital_status = request.POST.get('maritalStatus')
            email = request.POST.get('email')
            password = request.POST.get('password')            
            user_role = request.POST.get('userRole')
            Workingplace = request.POST.get('Workingplace')
            joiningDate = request.POST.get('joiningDate')

            # Create a new CustomUser instance (if not exists) and link it to Staffs
            user = CustomUser.objects.create_user(username=email, password=password, email=email, first_name=first_name, last_name=last_name, user_type=2)

            # Create a new Staffs instance and link it to the user
            
            user.staff.middle_name = middle_name
            user.staff.date_of_birth = dob
            user.staff.gender = gender            
            user.staff.phone_number = phone            
            user.staff.marital_status = marital_status
            user.staff.profession = profession
            user.staff.role = user_role
            user.staff.work_place = Workingplace
            user.staff.joining_date = joiningDate
        
            # Save the staff record
            user.save()

            # For demonstration purposes, you can log the saved data
            logger.info(f'Data saved successfully: {user.staff.__dict__}')

            # Return a success response to the user
            return JsonResponse({'message': 'Data saved successfully'}, status=200)
        except Exception as e:
            # Handle exceptions and log the error
            logger.error(f'Error saving data: {str(e)}')
            return JsonResponse({'error': str(e)}, status=400)

    # Return an error response if the request is not POST
    return JsonResponse({'error': 'Invalid request method'}, status=405)
 

@login_required
@require_POST
def update_staff_status(request):
    try:
        user_id = request.POST.get('user_id')
        is_active = request.POST.get('is_active')

        if not user_id or is_active is None:
            return JsonResponse({
                'success': False,
                'message': 'Invalid request data.'
            })

        staff = get_object_or_404(CustomUser, id=user_id)
        
        # Convert the string value to boolean
        is_active_bool = (is_active == '1')
        
        # Only update if the status is actually changing
        if staff.is_active != is_active_bool:
            staff.is_active = is_active_bool
            staff.save()
            
            message_text = f'{staff.username} has been {"activated" if is_active_bool else "deactivated"}.'
            
            return JsonResponse({
                'success': True,
                'message': message_text
            })
        else:
            return JsonResponse({
                'success': True,
                'message': 'No change needed - status is already set correctly.'
            })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        })
    

@login_required
def update_vehicle_status(request):
    try:
        if request.method == 'POST':
            # Get the user_id and is_active values from POST data
            vehicle_id = request.POST.get('vehicle_id')
            is_active = request.POST.get('is_active')

            # Retrieve the staff object or return a 404 response if not found
            vehicle = get_object_or_404(HospitalVehicle, id=vehicle_id)

            # Toggle the is_active status based on the received value
            if is_active == '1':
                vehicle.is_active = False
            elif is_active == '0':
                vehicle.is_active = True
            else:
                messages.error(request, 'Invalid request')
                return redirect('clinic:hospital_vehicle_list')  # Make sure 'hospital_vehicle_lists' is the name of your staff list URL

            vehicle.save()
            messages.success(request, 'Status updated successfully')
        else:
            messages.error(request, 'Invalid request method')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
    # Redirect back to the staff list page
    return redirect('clinic:hospital_vehicle_list')  # Make sure 'hospital_vehicle_lists' is the name of your staff list URL

@login_required
@require_POST
def update_equipment_status(request):
    try:
        equipment_id = request.POST.get('equipment_id')
        is_active = request.POST.get('is_active')

        # Validate input
        if equipment_id is None or is_active is None:
            return JsonResponse({
                'success': False,
                'message': 'Invalid request data'
            })

        # Convert is_active to boolean
        is_active_bool = True if str(is_active) == '1' else False

        # Get equipment object
        equipment = get_object_or_404(Equipment, id=equipment_id)

        # Update status
        equipment.is_active = is_active_bool
        equipment.save()

        return JsonResponse({
            'success': True,
            'message': 'Equipment status updated successfully'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })


@login_required
def edit_staff(request, staff_id):
    # Check if the staff with the given ID exists, or return a 404 page
    staff = get_object_or_404(Staffs, id=staff_id)  
    # If staff exists, proceed with the rest of the view
    request.session['staff_id'] = staff_id
    return render(request, "update/edit_staff.html", {"id": staff_id, "username": staff.admin.username, "staff": staff})   


@login_required
def edit_staff_save(request):
    if request.method == "POST":
        try:
            # Retrieve the staff ID from the session
            staff_id = request.session.get('staff_id')
            if staff_id is None:
                messages.error(request, "Staff ID not found")
                return redirect("resa_admin_edit_staff")

            # Retrieve the staff instance from the database
            try:
                staff = Staffs.objects.get(id=staff_id)
            except ObjectDoesNotExist:
                messages.error(request, "Staff not found")
                return redirect("resa_admin_edit_staff")

            # Extract form data
            first_name = request.POST.get('firstName', '').capitalize()
            middle_name = request.POST.get('middleName', '').capitalize()
            last_name = request.POST.get('lastname', '').capitalize()
            gender = request.POST.get('gender')
            dob = request.POST.get('date_of_birth')
            phone = request.POST.get('phone')
            profession = request.POST.get('profession')
            marital_status = request.POST.get('maritalStatus')
            email = request.POST.get('email')
            username = request.POST.get('username')
            user_role = request.POST.get('userRole')
            joining_date = request.POST.get('joiningDate')
            working_place = request.POST.get('Workingplace')
            mct_number = request.POST.get('mct_number')

            # Ensure unique email and username
            if CustomUser.objects.filter(email=email).exclude(id=staff.admin.id).exists():
                messages.error(request, "Email already exists. Try another email.")
                return redirect("resa_admin_edit_staff", staff_id=staff_id)

            if CustomUser.objects.filter(username=username).exclude(id=staff.admin.id).exists():
                messages.error(request, "Username already exists. Try another username.")
                return redirect("resa_admin_edit_staff", staff_id=staff_id)
            
            if Staffs.objects.filter(admin__first_name=first_name, middle_name=middle_name, admin__last_name=last_name).exclude(id=staff_id).exists():
                messages.error(request, "A staff member with this full name already exists. Try another name or contact the administrator for support.")
                return redirect("resa_admin_edit_staff", staff_id=staff_id)

            # Ensure unique MCT number if provided
            if mct_number and Staffs.objects.filter(mct_number=mct_number).exclude(id=staff_id).exists():
                messages.error(request, "MCT number already exists. Provide a unique MCT number.")
                return redirect("resa_admin_edit_staff", staff_id=staff_id)

            # Ensure staff is above 18 years
            if dob:
                dob_date = datetime.strptime(dob, "%Y-%m-%d").date()
                today = datetime.today().date()
                age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
                if age < 18:
                    messages.error(request, "Staff must be at least 18 years old.")
                    return redirect("resa_admin_edit_staff", staff_id=staff_id)

            # Ensure joining date is not in the future
            if joining_date:
                joining_date_obj = datetime.strptime(joining_date, "%Y-%m-%d").date()
                if joining_date_obj > datetime.today().date():
                    messages.error(request, "Joining date cannot be in the future.")
                    return redirect("resa_admin_edit_staff", staff_id=staff_id)

            # Save the staff details
            staff.admin.first_name = first_name
            staff.admin.last_name = last_name
            staff.admin.email = email
            staff.admin.username = username
            staff.middle_name = middle_name
            staff.joining_date = joining_date
            staff.work_place = working_place
            staff.role = user_role
            staff.profession = profession
            staff.marital_status = marital_status
            staff.date_of_birth = dob
            staff.phone_number = phone
            staff.gender = gender
            staff.mct_number = mct_number
            staff.admin.save()
            staff.save()

            messages.success(request, "Staff details updated successfully.")
            return redirect("resa_admin_manage_staff")

        except Exception as e:
            messages.error(request, f"Error updating staff details: {str(e)}")
            return redirect("resa_admin_edit_staff", staff_id=staff_id)

    return redirect("resa_admin_manage_staff")


@login_required
def medicine_types_management(request):
    """
    View for displaying all medicine types
    """
    # Get all medicine types ordered by name
    medicine_types = MedicineType.objects.all().order_by('name')
    
    # Pass the medicine types to the template
    context = {
        'medicine_types': medicine_types,
    }
    
    return render(request, 'hod_template/manage_medicine_types.html', context)


@csrf_exempt
@require_POST
@login_required
def add_medicine_type(request):
    """
    View for adding a new medicine type via AJAX
    """
    response_data = {}
    
    try:
        # Get the current user's staff record
        staff = Staffs.objects.get(admin=request.user)
        
        # Get form data
        name = request.POST.get('name')
        explanation = request.POST.get('explanation', '').strip()
        
        # Validate required fields
        if not name:
            response_data['success'] = False
            response_data['message'] = 'Medicine type name is required.'
            return JsonResponse(response_data)
        
        # Create new medicine type
        medicine_type = MedicineType(
            name=name,
            explanation=explanation if explanation else None,
            data_recorder=staff
        )
        
        # Validate and save
        medicine_type.full_clean()
        medicine_type.save()
        
        response_data['success'] = True
        response_data['message'] = 'Medicine type added successfully.'
        
    except IntegrityError:
        response_data['success'] = False
        response_data['message'] = 'A medicine type with this name already exists.'
    
    except ValidationError as e:
        response_data['success'] = False
        response_data['message'] = 'Validation error: ' + ', '.join(e.messages)
    
    except Staffs.DoesNotExist:
        response_data['success'] = False
        response_data['message'] = 'Staff record not found for the current user.'
    
    except Exception as e:
        response_data['success'] = False
        response_data['message'] = f'An error occurred: {str(e)}'
    
    return JsonResponse(response_data)

@csrf_exempt
@require_POST
@login_required
def edit_medicine_type(request):
    """
    View for editing an existing medicine type via AJAX
    """
    response_data = {}
    
    try:
        # Get the current user's staff record
        staff = Staffs.objects.get(admin=request.user)
        
        # Get form data
        medicine_type_id = request.POST.get('medicine_type_id')
        name = request.POST.get('name')
        explanation = request.POST.get('explanation', '').strip()
        
        # Validate required fields
        if not medicine_type_id or not name:
            response_data['success'] = False
            response_data['message'] = 'Medicine type ID and name are required.'
            return JsonResponse(response_data)
        
        # Get the medicine type to edit
        medicine_type = get_object_or_404(MedicineType, id=medicine_type_id)
        
        # Update fields
        medicine_type.name = name
        medicine_type.explanation = explanation if explanation else None
        medicine_type.data_recorder = staff
        
        # Validate and save
        medicine_type.full_clean()
        medicine_type.save()
        
        response_data['success'] = True
        response_data['message'] = 'Medicine type updated successfully.'
        
    except IntegrityError:
        response_data['success'] = False
        response_data['message'] = 'A medicine type with this name already exists.'
    
    except ValidationError as e:
        response_data['success'] = False
        response_data['message'] = 'Validation error: ' + ', '.join(e.messages)
    
    except Staffs.DoesNotExist:
        response_data['success'] = False
        response_data['message'] = 'Staff record not found for the current user.'
    
    except Exception as e:
        response_data['success'] = False
        response_data['message'] = f'An error occurred: {str(e)}'
    
    return JsonResponse(response_data)

@csrf_exempt
@require_POST
@login_required
def delete_medicine_type(request):
    """
    View for deleting a medicine type via AJAX
    """
    response_data = {}
    
    try:
        # Get medicine type ID
        medicine_type_id = request.POST.get('medicine_type_id')
        
        if not medicine_type_id:
            response_data['success'] = False
            response_data['message'] = 'Medicine type ID is required.'
            return JsonResponse(response_data)
        
        # Get the medicine type to delete
        medicine_type = get_object_or_404(MedicineType, id=medicine_type_id)
        
        # Delete the medicine type
        medicine_type.delete()
        
        response_data['success'] = True
        response_data['message'] = 'Medicine type deleted successfully.'
        
    except Exception as e:
        response_data['success'] = False
        response_data['message'] = f'An error occurred: {str(e)}'
    
    return JsonResponse(response_data)


@login_required
def medicine_list(request):
    # Prefetch related data to avoid N+1 queries
    medicine_units = MedicineUnitMeasure.objects.all().only('id', 'name', 'short_name')
    medicine_types = MedicineType.objects.all().only('id', 'name')
    medicine_routes = MedicineRoute.objects.all().only('id', 'name')
    
    # Optimize medicine query with select_related and only necessary fields
    medicines = Medicine.objects.select_related(
        'drug_type', 'formulation_unit', 'route', 'data_recorder'
    ).only(
        'id', 'drug_name', 'formulation_value', 'manufacturer', 
        'quantity', 'remain_quantity', 'is_dividable', 'batch_number',
        'expiration_date', 'cash_cost', 'insurance_cost', 'nhif_cost',
        'buying_price', 'total_buying_price', 'created_at', 'updated_at',
        'drug_type__name', 'formulation_unit__short_name', 'route__name',
        'data_recorder__admin__username'
    ).order_by('drug_name')
    
    # Calculate total investment (sum of all total_buying_price values)
    total_investment = medicines.aggregate(
        total=Sum('total_buying_price')
    )['total'] or 0
    
    # Check for expired and expiring soon medicines
    today = timezone.now().date()
    soon_threshold = today + timedelta(days=30)
    
    # Annotate medicines with status information
    for medicine in medicines:
        # Check if expired
        medicine.is_expired = medicine.expiration_date < today
        
        # Check if expiring soon (within 30 days but not expired)
        medicine.expiring_soon = (
            not medicine.is_expired and 
            medicine.expiration_date <= soon_threshold
        )
        
        # Calculate days until expiration
        if medicine.is_expired:
            medicine.days_until_expire = 0
        else:
            medicine.days_until_expire = (medicine.expiration_date - today).days
    
    # Render the template with medicine data and notifications
    return render(
        request,
        'hod_template/manage_medicine.html',
        {
            'medicines': medicines,
            'medicine_units': medicine_units,
            'medicine_types': medicine_types,
            'medicine_routes': medicine_routes,
            'total_investment': total_investment,
        }
    )


@csrf_exempt
@login_required
def add_medicine(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request method"})

    try:
        # Get all form data
        medicine_id = request.POST.get("medicine_id")
        drug_name = request.POST.get("drug_name", "").strip()
        drug_type_id = request.POST.get("drug_type")
        formulation_value = request.POST.get("formulation_value")
        formulation_unit_id = request.POST.get("formulation_unit")
        route_id = request.POST.get("route")
        manufacturer = request.POST.get("manufacturer", "").strip()
        quantity = request.POST.get("quantity")
        remain_quantity = request.POST.get("remain_quantity")
        is_dividable = request.POST.get("is_dividable", "False").lower() == "true"
        batch_number = request.POST.get("batch_number", "").strip()
        expiration_date = request.POST.get("expiration_date")
        cash_cost = request.POST.get("cash_cost")
        insurance_cost = request.POST.get("insurance_cost")
        nhif_cost = request.POST.get("nhif_cost")
        buying_price = request.POST.get("buying_price")

        # --- VALIDATIONS ---

        # Required fields
        required_fields = {
            "drug_name": drug_name,
            "formulation_value": formulation_value,
            "formulation_unit": formulation_unit_id,
            "quantity": quantity,
            "batch_number": batch_number,
            "expiration_date": expiration_date,
            "buying_price": buying_price
        }
        
        missing_fields = [field for field, value in required_fields.items() if not value]
        if missing_fields:
            return JsonResponse({"success": False, "message": f"Missing required fields: {', '.join(missing_fields)}"})

        # Parse and validate numeric fields
        try:
            formulation_value = float(formulation_value)
            quantity = int(quantity)
            remain_quantity = int(remain_quantity) if remain_quantity else quantity
            buying_price = float(buying_price)
            cash_cost = float(cash_cost) if cash_cost else buying_price * 1.2  # Default markup
            insurance_cost = float(insurance_cost) if insurance_cost else buying_price * 1.15
            nhif_cost = float(nhif_cost) if nhif_cost else buying_price * 1.1
        except ValueError:
            return JsonResponse({"success": False, "message": "Invalid numeric values provided."})

        # Expiration date validation
        try:
            expiration_date_obj = datetime.strptime(expiration_date, "%Y-%m-%d").date()
            if expiration_date_obj <= timezone.now().date():
                return JsonResponse({"success": False, "message": "Expiration date must be in the future."})
        except ValueError:
            return JsonResponse({"success": False, "message": "Invalid expiration date format. Use YYYY-MM-DD."})

        # Get related objects
        try:
            formulation_unit = MedicineUnitMeasure.objects.get(pk=formulation_unit_id)
        except ObjectDoesNotExist:
            return JsonResponse({"success": False, "message": "Invalid formulation unit."})
            
        # Get drug type if provided
        drug_type = None
        if drug_type_id:
            try:
                drug_type = MedicineType.objects.get(pk=drug_type_id)
            except ObjectDoesNotExist:
                return JsonResponse({"success": False, "message": "Invalid drug type."})
                
        # Get route if provided
        route = None
        if route_id:
            try:
                route = MedicineRoute.objects.get(pk=route_id)
            except ObjectDoesNotExist:
                return JsonResponse({"success": False, "message": "Invalid route of administration."})

        # Recorder (current staff)
        staff_member = getattr(request.user, "staff", None)

        # --- CREATE OR UPDATE ---

        if medicine_id:  # Update
            try:
                medicine = Medicine.objects.get(pk=medicine_id)

                # Check for duplicates (excluding current medicine)
                if Medicine.objects.exclude(pk=medicine_id).filter(
                    drug_name=drug_name, 
                    formulation_value=formulation_value,
                    formulation_unit=formulation_unit
                ).exists():
                    return JsonResponse({"success": False, "message": "A medicine with this name and formulation already exists."})
                    
                if Medicine.objects.exclude(pk=medicine_id).filter(batch_number=batch_number).exists():
                    return JsonResponse({"success": False, "message": "A medicine with this batch number already exists."})

                # Update medicine fields
                medicine.drug_name = drug_name
                medicine.drug_type = drug_type
                medicine.formulation_value = formulation_value
                medicine.formulation_unit = formulation_unit
                medicine.route = route
                medicine.manufacturer = manufacturer
                medicine.quantity = quantity
                medicine.remain_quantity = quantity
                medicine.is_dividable = is_dividable
                medicine.batch_number = batch_number
                medicine.expiration_date = expiration_date_obj
                medicine.cash_cost = cash_cost
                medicine.insurance_cost = insurance_cost
                medicine.nhif_cost = nhif_cost
                medicine.buying_price = buying_price
                
                if staff_member:
                    medicine.data_recorder = staff_member

                medicine.save()
                return JsonResponse({"success": True, "message": "Medicine updated successfully."})
                
            except Medicine.DoesNotExist:
                return JsonResponse({"success": False, "message": "Medicine not found."})

        else:  # Create
            # Check for duplicates
            if Medicine.objects.filter(
                drug_name=drug_name, 
                formulation_value=formulation_value,
                formulation_unit=formulation_unit
            ).exists():
                return JsonResponse({"success": False, "message": "A medicine with this name and formulation already exists."})
                
            if Medicine.objects.filter(batch_number=batch_number).exists():
                return JsonResponse({"success": False, "message": "A medicine with this batch number already exists."})

            # Create new medicine
            medicine = Medicine(
                drug_name=drug_name,
                drug_type=drug_type,
                formulation_value=formulation_value,
                formulation_unit=formulation_unit,
                route=route,
                manufacturer=manufacturer,
                quantity=quantity,
                remain_quantity=quantity,
                is_dividable=is_dividable,
                batch_number=batch_number,
                expiration_date=expiration_date_obj,
                cash_cost=cash_cost,
                insurance_cost=insurance_cost,
                nhif_cost=nhif_cost,
                buying_price=buying_price,
                data_recorder=staff_member,
            )
            medicine.save()
            return JsonResponse({"success": True, "message": "Medicine added successfully."})

    except ValidationError as ve:
        return JsonResponse({"success": False, "message": f"Validation error: {str(ve)}"})
    except Exception as e:
        logger.error(f"Error in add_medicine view: {str(e)}")
        return JsonResponse({"success": False, "message": "An unexpected error occurred. Please try again."})


@csrf_exempt
@require_POST
def restock_medicine(request):
    try:
        # Get form data
        medicine_id = request.POST.get('medicine_id')
        add_quantity = int(request.POST.get('add_quantity'))
        batch_number = request.POST.get('batch_number')
        expiration_date = request.POST.get('expiration_date')
        buying_price = request.POST.get('buying_price', None)

        # Validate required fields
        if not all([medicine_id, add_quantity, batch_number, expiration_date]):
            return JsonResponse({
                'success': False, 
                'message': 'All required fields must be provided.'
            })

        # Get the medicine object
        try:
            medicine = Medicine.objects.get(id=medicine_id)
        except Medicine.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'message': 'Medicine not found.'
            })

        # Create or update batch
        batch, created = MedicineBatch.objects.get_or_create(
            medicine=medicine,
            batch_number=batch_number,
            defaults={
                'expiration_date': expiration_date,
                'quantity': add_quantity,
                'remain_quantity': add_quantity,
                'buying_price': buying_price
            }
        )

        if not created:
            # Update existing batch
            batch.quantity += add_quantity
            batch.remain_quantity += add_quantity
            batch.expiration_date = expiration_date  # optional: maybe warn if different
            if buying_price:
                batch.buying_price = buying_price
            batch.save()

        # Update totals in the main medicine record
        total_quantity = medicine.batches.aggregate(total=models.Sum('quantity'))['total'] or 0
        total_remain = medicine.batches.aggregate(total=models.Sum('remain_quantity'))['total'] or 0
        medicine.quantity = total_quantity
        medicine.remain_quantity = total_remain
        medicine.save()

        return JsonResponse({
            'success': True,
            'message': f'Successfully restocked {add_quantity} units of {medicine.drug_name} (Batch: {batch_number}).'
        })

    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'An error occurred: {str(e)}'
        })


def medicine_expired_list(request):
    # Get all medicines
    all_medicines = Medicine.objects.all()

    # Filter medicines with less than or equal to 10 days remaining for expiration
    medicines = []
    for medicine in all_medicines:
        days_remaining = (medicine.expiration_date - timezone.now().date()).days
        if days_remaining <= 10:
            medicines.append({
                'name': medicine.drug_name,
                'expiration_date': medicine.expiration_date,
                'days_remaining': days_remaining,
            })

    return render(request, 'hod_template/manage_medicine_expired.html', {'medicines': medicines})

@login_required
def patient_procedure_view(request):
    # Get all distinct (patient, visit) pairs that have at least one procedure
    distinct_procedure_sets = (
        Procedure.objects
        .values('patient_id', 'visit_id')
        .annotate(latest_date=Max('created_at'))
        .order_by('-latest_date')
    )

    # Prepare data structure for template
    patient_procedures = []

    for entry in distinct_procedure_sets:
        patient_id = entry['patient_id']
        visit_id = entry['visit_id']
        latest_date = entry['latest_date']

        procedures = Procedure.objects.filter(
            patient_id=patient_id,
            visit_id=visit_id
        ).select_related('patient', 'visit', 'doctor__admin', 'name', 'data_recorder')

        if procedures.exists():
            first_proc = procedures.first()
            patient_procedures.append({
                'patient': first_proc.patient,
                'visit': first_proc.visit,
                'latest_date': latest_date,
                'doctor': first_proc.doctor,
                'procedure_done_by': first_proc.data_recorder,
                'procedures': procedures  # All procedures for that visit
            })

    context = {
        'patient_procedures': patient_procedures,
    }
    return render(request, 'hod_template/manage_procedure.html', context)


@login_required
def patient_laboratory_view(request):
    # Get distinct (patient, visit) combinations with latest result date
    distinct_lab_sets = (
        LaboratoryOrder.objects
        .values('patient_id', 'visit_id')
        .annotate(latest_date=Max('created_at'))
        .order_by('-latest_date')
    )

    patient_lab_data = []

    for entry in distinct_lab_sets:
        patient_id = entry['patient_id']
        visit_id = entry['visit_id']
        latest_date = entry['latest_date']

        lab_tests = LaboratoryOrder.objects.filter(
            patient_id=patient_id,
            visit_id=visit_id
        ).select_related('patient', 'visit', 'data_recorder__admin')

        if lab_tests.exists():
            first_lab = lab_tests.first()
            patient_lab_data.append({
                'patient': first_lab.patient,
                'visit': first_lab.visit,
                'latest_date': latest_date,
                'lab_done_by': first_lab.data_recorder,
                'lab_tests': lab_tests
            })

    context = {
        'patient_labs': patient_lab_data,
    }

    return render(request, 'hod_template/manage_lab_result.html', context)


@login_required
def manage_referral(request):
    referrals = Referral.objects.all()
    return render(request, 'hod_template/manage_referral.html', {'referrals': referrals})



@login_required
def appointment_list_view(request):
    appointments = Consultation.objects.all() 
    context = {       
        'appointments':appointments,
    }
    return render(request, 'hod_template/manage_appointment.html', context)



@csrf_exempt
@login_required
def add_disease(request):
    if request.method == 'POST':
        try:
            # Extract data from the request
            disease_id = request.POST.get('disease_id')
            disease_name = request.POST.get('name').strip()
            code = request.POST.get('code').strip()

            # If disease ID is provided, it's an edit operation
            if disease_id:
                # Check if the disease with the given ID exists
                disease = DiseaseRecode.objects.get(pk=disease_id)
                if disease:
                    # Check if updating the disease name and code will cause a duplicate entry error
                    if DiseaseRecode.objects.exclude(pk=disease_id).filter(disease_name=disease_name).exists():
                        return JsonResponse({'success': False, 'message': 'Another disease with the same name already exists'})                    
                    if DiseaseRecode.objects.exclude(pk=disease_id).filter(code=code).exists():
                        return JsonResponse({'success': False, 'message': 'Another disease with the same code already exists'})
                    
                    # Update disease data
                    disease.disease_name = disease_name
                    disease.code = code
                    disease.save()
                    return JsonResponse({'success': True, 'message': 'Disease updated successfully'})
                else:
                    return JsonResponse({'success': False, 'message': 'Disease does not exist'})

            # Check if the disease already exists
            if DiseaseRecode.objects.filter(disease_name=disease_name).exists():
                return JsonResponse({'success': False, 'message': 'Disease already exists'})            
            if DiseaseRecode.objects.filter(code=code).exists():
                return JsonResponse({'success': False, 'message': 'Disease already exists'})

            # Save data to the model for new disease
            DiseaseRecode.objects.create(disease_name=disease_name, code=code)
            return JsonResponse({'success': True, 'message': 'Disease added successfully'})

        except IntegrityError:
            # Handle the specific IntegrityError raised when a duplicate entry occurs
            return JsonResponse({'success': False, 'message': 'Disease already exists'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
 


@csrf_exempt
@login_required
def add_pathodology_record(request):
    if request.method == 'POST':
        try:
            # Extract data from the request
            name = request.POST.get('Name').strip()
            description = request.POST.get('Description')
            pathology_record_id = request.POST.get('pathology_record_id')
            
            # If pathology record ID is provided, it's an edit operation
            if pathology_record_id:             
                
                # Check if the provided name already exists in the database excluding the current record
                if PathodologyRecord.objects.exclude(pk=pathology_record_id).filter(name=name).exists():
                    return JsonResponse({'success': False, 'message':  f'Another pathology record with the name "{name}" already exists'})
                 # Get the existing pathology record object
                pathology_record = PathodologyRecord.objects.get(pk=pathology_record_id)
                # Update the existing pathology record
                pathology_record.name = name
                pathology_record.description = description
                pathology_record.save()
                return JsonResponse({'success': True, 'message': 'Patholody updated successfully'})
            else:  # If no pathology record ID is provided, it's an add operation
                # Check if the provided name already exists in the database
                if PathodologyRecord.objects.filter(name=name).exists():
                    return JsonResponse({'success': False, 'message':  f'A pathology record with the name "{name}" already exists'})

                # Save data to the model for a new pathology record
                pathodology_record = PathodologyRecord.objects.create(
                    name=name,
                    description=description
                )
                return JsonResponse({'success': True, 'message': f'{name} added successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
    

def get_out_of_stock_count_reagent(request):
    count = Reagent.objects.filter(remaining_quantity=0).count()
    
    return JsonResponse({'count': count})


    
def out_of_stock_medicines(request):
    try:
        # Query the database for the count of out-of-stock medicines
        out_of_stock_count = Medicine.objects.filter(remain_quantity=0).count()
        
        # Return the count in JSON format
        return JsonResponse({'count': out_of_stock_count})
    
    except Exception as e:
        # Handle any errors and return an error response
        return JsonResponse({'error': str(e)}, status=500)    

@login_required    
def out_of_stock_medicines_view(request):
    try:
        # Query the database for out-of-stock medicines
        out_of_stock_medicines = Medicine.objects.filter(remain_quantity=0)
        
        # Render the template with the out-of-stock medicines data
        return render(request, 'hod_template/manage_out_of_stock_medicines.html', {'out_of_stock_medicines': out_of_stock_medicines})    
    except Exception as e:
        # Handle any errors and return an error response
        return render(request, '404.html', {'error_message': str(e)}) 


    
@login_required    
def in_stock_medicines_view(request):
    # Retrieve medicines with inventory levels above zero
    in_stock_medicines = Medicine.objects.filter(remain_quantity__gt=0)

    return render(request, 'hod_template/manage_in_stock_medicines.html', {'in_stock_medicines': in_stock_medicines})  



@login_required
def equipment_list(request):
    equipment_list = Equipment.objects.all()
    return render(request, 'hod_template/manage_equipment_list.html', {'equipment_list': equipment_list})  

 
@csrf_exempt
@require_POST
def add_equipment(request):
    try:
        equipment_id = request.POST.get('equipment_id')
        manufacturer = request.POST.get('manufacturer').strip()
        serial_number = request.POST.get('serial_number').strip()
        acquisition_date = request.POST.get('acquisition_date') or None
        warranty_expiry_date = request.POST.get('warranty_expiry_date') or None
        location = request.POST.get('location')
        description = request.POST.get('description')
        name = request.POST.get('name').strip()

       

        if equipment_id:
             # Check for duplicate equipment by serial number
            if Equipment.objects.filter(serial_number=serial_number).exclude(id=equipment_id).exists():
                return JsonResponse({'success': False, 'message': 'Equipment with this serial number already exists.'})
            try:
                equipment = Equipment.objects.get(pk=equipment_id)
                equipment.manufacturer = manufacturer
                equipment.serial_number = serial_number
                equipment.acquisition_date = acquisition_date
                equipment.warranty_expiry_date = warranty_expiry_date
                equipment.description = description
                equipment.location = location
                equipment.name = name
                equipment.save()
                return JsonResponse({'success': True, 'message': 'Equipment updated successfully.'})
            except ObjectDoesNotExist:
                return JsonResponse({'success': False, 'message': 'Equipment not found.'})
        else:
            if Equipment.objects.filter(serial_number=serial_number).exists():
                return JsonResponse({'success': False, 'message': 'Equipment with this serial number already exists.'})
            
            equipment = Equipment(
                name=name,
                manufacturer=manufacturer,
                serial_number=serial_number,
                acquisition_date=acquisition_date,
                warranty_expiry_date=warranty_expiry_date,
                description=description,
                location=location
            )
            equipment.save()
            return JsonResponse({'success': True, 'message': 'Equipment added successfully.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
    

@login_required 
def reagent_list(request):
    reagent_list = Reagent.objects.all()
    return render(request, 'hod_template/manage_reagent_list.html', {'reagent_list': reagent_list})    

@csrf_exempt
@require_POST
def add_reagent(request):
    try:
        reagent_id = request.POST.get('reagent_id')
        name = request.POST.get('name').strip()
        manufacturer = request.POST.get('manufacturer').strip()
        lot_number = request.POST.get('lot_number').strip()
        storage_conditions = request.POST.get('storage_conditions')
        quantity_in_stock = int(request.POST.get('quantity_in_stock'))
        price_per_unit = float(request.POST.get('price_per_unit'))
        
        # Optional fields
        expiration_date = request.POST.get('expiration_date')
        if expiration_date:
            expiration_date = datetime.strptime(expiration_date, '%Y-%m-%d').date()
      
        if reagent_id:
            if Reagent.objects.filter(lot_number=lot_number).exclude(id=reagent_id).exists():
                return JsonResponse({'success': False, 'message': 'Reagent with this lot number already exists.'})
            reagent = Reagent.objects.get(pk=reagent_id)
            reagent.name = name
            reagent.manufacturer = manufacturer
            reagent.lot_number =  lot_number
            reagent.storage_conditions = storage_conditions
            reagent.quantity_in_stock = quantity_in_stock
            reagent.price_per_unit = price_per_unit
            if expiration_date:
                reagent.expiration_date = expiration_date
            reagent.remaining_quantity = quantity_in_stock
            reagent.save()
            return JsonResponse({'success': True, 'message': 'Reagent updated successfully.'})
        else:
            if Reagent.objects.filter(lot_number=lot_number).exists():
                return JsonResponse({'success': False, 'message': 'Reagent with this lot number already exists.'})
            
            reagent = Reagent(
                name=name,
                manufacturer=manufacturer,
                lot_number=lot_number,
                storage_conditions=storage_conditions,
                quantity_in_stock=quantity_in_stock,
                price_per_unit=price_per_unit,
                remaining_quantity=quantity_in_stock
            )
            if expiration_date:
                reagent.expiration_date = expiration_date
            reagent.save()
            return JsonResponse({'success': True, 'message': 'Reagent added successfully.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})





@login_required
def prescription_list(request):
    """View for prescription list"""
    # Step 1: Fetch prescriptions grouped by visit
    grouped_visits = (
        Prescription.objects
        .values(
            'visit__id',
            'visit__vst',
            'visit__created_at',
            'visit__patient__id',
            'visit__patient__first_name',
            'visit__patient__middle_name',
            'visit__patient__last_name',
            'visit__patient__gender',
            'visit__patient__dob',
            'visit__patient__mrn',
            'visit__patient__payment_form',
            'visit__patient__insurance_name',
        )
        .annotate(
            total_price=Sum('total_price')
        )
        .order_by('-visit__created_at')
    )

    # Step 2: Attach related prescriptions to each grouped visit and get status
    visit_list = []
    for visit in grouped_visits:
        visit_id = visit['visit__id']
        visit_instance = PatientVisits.objects.get(id=visit_id)
        
        # Get the status using the model method
        status = Prescription.get_visit_status(visit_instance)
        
        # Get all prescriptions for this visit
        prescriptions = Prescription.objects.filter(visit_id=visit_id).select_related('medicine', 'frequency')
        
        # Create a new dictionary with all the data
        visit_data = {
            **visit,
            'prescriptions': prescriptions,
            'verified_status': status['verified'],
            'issued_status': status['issued'],
            'payment_status': status['status']
        }
        
        visit_list.append(visit_data)

    return render(request, 'hod_template/manage_prescription_list.html', {
        'visit_total_prices': visit_list,
    })


@login_required
def walkin_prescription_list(request):
    """View for walk-in prescription list grouped by visit, including visit status."""
    try:
        # Step 1: Fetch grouped visits with aggregated total price
        grouped_visits = (
            WalkInPrescription.objects
            .values(
                'visit__id',
                'visit__visit_number',
                'visit__visit_date',
                'visit__customer__id',
                'visit__customer__first_name',
                'visit__customer__middle_name',
                'visit__customer__last_name',
                'visit__customer__gender',
                'visit__customer__age',
                'visit__customer__pharmacy_number',
                'visit__customer__address',
                'visit__customer__phone_number',
                'visit__customer__payment_form',
            )
            .annotate(total_price=Sum('total_price'))
            .order_by('-visit__visit_date')
        )

        # Step 2: Fetch prescriptions for those visits
        visit_ids = [v['visit__id'] for v in grouped_visits]
        prescriptions = (
            WalkInPrescription.objects
            .filter(visit_id__in=visit_ids)
            .select_related('medicine', 'frequency', 'entered_by')
        )

        # Step 3: Group prescriptions by visit ID
        prescriptions_by_visit = defaultdict(list)
        for p in prescriptions:
            prescriptions_by_visit[p.visit_id].append(p)

        # Step 4: Attach prescriptions + visit status to each grouped visit
        for visit in grouped_visits:
            visit_id = visit['visit__id']
            related_prescriptions = prescriptions_by_visit.get(visit_id, [])
            visit['prescriptions'] = related_prescriptions

            # Get visit object to compute status
            try:
                visit_obj = WalkInVisit.objects.get(id=visit_id)
                visit['visit_status'] = WalkInPrescription.get_visit_status(visit_obj)
            except WalkInVisit.DoesNotExist:
                visit['visit_status'] = {
                    "verified": "visit_not_found",
                    "issued": "visit_not_found",
                    "status": "visit_not_found"
                }

        return render(request, 'hod_template/manage_walkin_prescription_list.html', {
            'visit_total_prices': grouped_visits,
        })

    except Exception as e:
        return render(request, '404.html', {
            'error_message': f"An error occurred: {str(e)}"
        })


@login_required
def generate_walkin_receipt_pdf(request, visit_id):
    """Generate PDF receipt for a walk-in visit"""
    try:
        # --- 1. Get visit and prescriptions ---
        visit = WalkInVisit.objects.get(id=visit_id)
        prescriptions = WalkInPrescription.objects.filter(visit=visit)

        # --- 2. Check if visit is paid and needs receipt number ---
        has_paid = prescriptions.filter(status="paid").exists()
        if has_paid and not visit.receipt_number:
            visit.generate_receipt_number()  # auto-generate receipt

        # --- 3. Calculate totals ---
        total_price = sum(p.total_price for p in prescriptions if p.total_price)
        tax_rate = Decimal("0.10")  # 10% tax
        tax = total_price * tax_rate
        grand_total = total_price + tax

        context = {
            "visit": visit,
            "prescriptions": prescriptions,
            "total_price": total_price,
            "tax": tax,
            "grand_total": grand_total,
            'pharmacist': request.user.staff if hasattr(request.user, 'staff') else None,
        }

        # --- 4. Render HTML template ---
        html_string = render_to_string(
            "hod_template/walkin_receipt_pdf.html", context
        )

        # --- 5. Generate PDF with WeasyPrint ---
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        result = html.write_pdf()

        # --- 6. Create response ---
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="receipt_{visit.visit_number}.pdf"'
        )
        response.write(result)
        return response

    except WalkInVisit.DoesNotExist:
        return HttpResponse("Visit not found", status=404)
    except Exception as e:
        return HttpResponse(f"Error generating PDF: {str(e)}", status=500)

@login_required
def download_prescription_notes(request, visit_id):
    """
    Generate or download prescription notes PDF for a visit.
    Auto-generates prescription_notes_id if it doesn't exist.
    """
    # 1. Get the visit
    visit = get_object_or_404(WalkInVisit, id=visit_id)

    # 2. Generate prescription_notes_id if missing
    if not visit.prescription_notes_id:
        visit.generate_prescription_notes_id()  # This will save the ID in DB

    # 3. Get prescriptions for this visit
    prescriptions = WalkInPrescription.objects.filter(visit=visit)

    # 4. Prepare context for template
    context = {
        'visit': visit,
        'prescriptions': prescriptions,
         'pharmacist': request.user.staff if hasattr(request.user, 'staff') else None,
    }

    # 5. Render HTML template
    html_string = render_to_string('hod_template/prescription_notes_pdf.html', context)

    # 6. Create PDF in memory
    buffer = BytesIO()
    HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(buffer)
    pdf_content = buffer.getvalue()
    buffer.close()

    # 7. Create HTTP response
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="prescription_notes_{visit.prescription_notes_id}.pdf"'

    return response 

def financial_analytics(request):
    # Get date range from request or default to last 30 days
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    report_type = request.GET.get('report_type', 'daily')
    
    if not start_date or not end_date:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Base queryset
    orders = Order.objects.filter(
        order_date__range=[start_date, end_date]
    ).select_related('patient', 'visit')
    
    # Calculate metrics
    metrics = orders.aggregate(
        total_revenue=Sum('cost', filter=Q(status='Paid')),
        paid_orders_count=Count('id', filter=Q(status='Paid')),
        pending_orders_count=Count('id', filter=Q(status='Unpaid')),
        total_orders_count=Count('id')
    )
    
    total_revenue = metrics['total_revenue'] or 0
    paid_orders_count = metrics['paid_orders_count'] or 0
    pending_orders_count = metrics['pending_orders_count'] or 0
    total_orders_count = metrics['total_orders_count'] or 0
    
    average_order_value = total_revenue / paid_orders_count if paid_orders_count > 0 else 0
    conversion_rate = (paid_orders_count / total_orders_count * 100) if total_orders_count > 0 else 0
    
    # Group orders by patient and visit
    grouped_orders = orders.values(
        'patient__id', 'visit__id', 'patient__mrn', 'patient__dob', 
        'patient__gender', 'patient__payment_form', 'patient__insurance_name', 
        'visit__vst'
    ).annotate(
        full_name=Concat(
            F('patient__first_name'), Value(' '), 
            F('patient__middle_name'), Value(' '), 
            F('patient__last_name')
        ),
        total_cost=Sum('cost'),
        statuses=GroupConcat('status', distinct=True, separator=',')
    ).order_by('-visit__vst')
    
    # Add orders list to each group
    grouped_orders_list = []
    for group in grouped_orders:
        group_orders = orders.filter(
            patient__id=group['patient__id'], 
            visit__id=group['visit__id']
        ).values('order_type', 'type_of_order', 'order_date', 'cost', 'order_number')
        
        group_dict = dict(group)
        group_dict['orders'] = list(group_orders)
        # Optional: turn "Paid,Unpaid" string into list
        group_dict['statuses'] = group_dict['statuses'].split(',') if group_dict['statuses'] else []
        grouped_orders_list.append(group_dict)
    
    # Prepare data for charts
    revenue_data = get_revenue_trend_data(start_date, end_date, report_type)
    payment_methods_data = get_payment_methods_data(orders)
    
    context = {
        'grouped_orders': grouped_orders_list,
        'total_revenue': total_revenue,
        'paid_orders_count': paid_orders_count,
        'pending_orders_count': pending_orders_count,
        'total_orders_count': total_orders_count,
        'average_order_value': average_order_value,
        'conversion_rate': conversion_rate,
        'start_date': start_date,
        'end_date': end_date,
        'report_type': report_type,
        'revenue_data_json': json.dumps(revenue_data),
        'payment_methods_json': json.dumps(payment_methods_data),
    }
    
    return render(request, 'hod_template/financial_analytics.html', context)

def get_revenue_trend_data(start_date, end_date, report_type):
    # Aggregate revenue by time period
    if report_type == 'daily':
        trunc_func = TruncDate('order_date')
    elif report_type == 'weekly':
        trunc_func = TruncWeek('order_date')
    else:  # monthly
        trunc_func = TruncMonth('order_date')
    
    revenue_data = Order.objects.filter(
        order_date__range=[start_date, end_date],
        status='Paid'
    ).annotate(
        period=trunc_func
    ).values('period').annotate(
        revenue=Sum('cost')
    ).order_by('period')
    
    # Format for chart
    labels = []
    data = []
    
    for item in revenue_data:
        if report_type == 'daily':
            labels.append(item['period'].strftime('%b %d'))
        elif report_type == 'weekly':
            labels.append(f"Week {item['period'].isocalendar()[1]}")
        else:
            labels.append(item['period'].strftime('%b %Y'))
        
        data.append(float(item['revenue'] or 0))
    
    return {
        'labels': labels,
        'data': data
    }

def get_payment_methods_data(orders):
    # Count orders by payment method
    payment_data = orders.values('patient__payment_form').annotate(
        count=Count('id')
    ).order_by('patient__payment_form')
    
    labels = []
    data = []
    
    for item in payment_data:
        labels.append(item['patient__payment_form'])
        data.append(item['count'])
    
    return {
        'labels': labels,
        'data': data
    }

def export_financial_report(request):
    if request.method == 'POST':
        # Get filter parameters
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        report_type = request.POST.get('report_type')
        
        # Create response object with Excel MIME type
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = f'attachment; filename="financial_report_{start_date}_to_{end_date}.xls"'
        
        # Create Excel workbook
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Financial Report')
        
        # Add headers
        row_num = 0
        columns = ['Order Number', 'Patient', 'Visit Number', 'Total Cost', 'Payment Method', 'Status', 'Order Date']
        
        for col_num, column_title in enumerate(columns):
            ws.write(row_num, col_num, column_title)
        
        # Get data
        orders = Order.objects.filter(
            order_date__range=[start_date, end_date]
        ).select_related('patient', 'visit')
        
        # Add data rows
        for order in orders:
            row_num += 1
            ws.write(row_num, 0, order.order_number)
            ws.write(row_num, 1, f"{order.patient.first_name} {order.patient.last_name}")
            ws.write(row_num, 2, order.visit.vst if order.visit else 'N/A')
            ws.write(row_num, 3, str(order.cost))
            ws.write(row_num, 4, order.patient.payment_form)
            ws.write(row_num, 5, order.status)
            ws.write(row_num, 6, order.order_date.strftime('%Y-%m-%d'))
        
        wb.save(response)
        return response

@login_required
def all_orders_view(request):
    grouped_orders = (
        Order.objects
        .values(
            'patient__id',
            'patient__first_name',
            'patient__middle_name',
            'patient__last_name',
            'patient__gender',
            'patient__dob',
            'patient__mrn',
            'patient__payment_form',
            'patient__insurance_name',
            'visit__id',
            'visit__vst',
            'visit__updated_at',
        )
        .annotate(
            total_cost=Sum('cost'),
            latest_order_date=Max('order_date'),
        )
        .order_by('-latest_order_date')
    )

    for group in grouped_orders:
        patient_id = group['patient__id']
        visit_id = group['visit__id']
        orders_qs = Order.objects.filter(patient_id=patient_id, visit_id=visit_id).order_by('order_date')
        group['orders'] = list(orders_qs)

        # Precompute statuses for template use
        unique_statuses = orders_qs.values_list('status', flat=True).distinct()
        group['statuses'] = list(unique_statuses)

        # Combine full name
        group['full_name'] = f"{group.get('patient__first_name', '')} {group.get('patient__middle_name', '')} {group.get('patient__last_name', '')}".strip()

    return render(request, 'hod_template/order_detail.html', {
        'grouped_orders': grouped_orders,
    })

@login_required
def orders_by_date(request, date):
    # Query orders based on the provided date
    orders = Order.objects.filter(order_date=date)
    # Pass orders and date to the template
    context = {
        'orders': orders,
        'date': date,
    }
    return render(request, 'hod_template/orders_by_date.html', context)

@login_required
def prescription_frequency_list(request):
    frequencies = PrescriptionFrequency.objects.all()
    return render(request, 'hod_template/prescription_frequency_list.html', {'frequencies': frequencies})

@require_POST
def delete_frequency(request):
    try:
        # Get the frequency ID from the POST data
        frequency_id = request.POST.get('frequency_id')
        # Delete the frequency from the database
        frequency = PrescriptionFrequency.objects.get(pk=frequency_id)
        frequency.delete()

        return JsonResponse({'status': 'success', 'message': 'Frequency deleted successfully'})
    except PrescriptionFrequency.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Frequency not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    
def add_frequency(request):
    if request.method == 'POST':
        try:
            frequency_id = request.POST.get('frequency_id')
            name = request.POST.get('name').strip()
            interval = request.POST.get('interval').strip()
            description = request.POST.get('description')
            
            # Check for duplicates
            if frequency_id:
                # Editing existing frequency
                frequency = PrescriptionFrequency.objects.get(pk=frequency_id)
                
                # Ensure no duplicate name or interval (excluding the current record)
                if PrescriptionFrequency.objects.filter(name=name).exclude(pk=frequency_id).exists():
                    return JsonResponse({'success': False, 'message': 'Prescription frequency with this name already exists'})
                if PrescriptionFrequency.objects.filter(interval=interval).exclude(pk=frequency_id).exists():
                    return JsonResponse({'success': False,  'message': 'Prescription frequency with this interval already exists'})
                
                frequency.name = name
                frequency.interval = interval
                frequency.description = description
                frequency.save()
                return JsonResponse({'success': True,  'message': 'Prescription frequency updated successfully'})
            else:
                # Adding new frequency
                if PrescriptionFrequency.objects.filter(name=name).exists():
                    return JsonResponse({'success': False,  'message': 'Prescription frequency with this name already exists'})
                if PrescriptionFrequency.objects.filter(interval=interval).exists():
                    return JsonResponse({'success': False,  'message': 'Prescription frequency with this interval already exists'})
                
                frequency = PrescriptionFrequency.objects.create(name=name, interval=interval, description=description)
                return JsonResponse({'success': True, 'message': 'Prescription frequency added successfully', 'id': frequency.id})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    else:
        return JsonResponse({'success': False,  'message': 'Invalid request method'})



@login_required    
def diagnosis_list(request):
    diagnoses = Diagnosis.objects.all().order_by('-created_at')    
    return render(request, 'hod_template/manage_diagnosis_list.html', {'diagnoses': diagnoses}) 


@login_required
@csrf_exempt
@require_POST
def save_diagnosis(request):
    try:
        # Extract and trim data from the request
        diagnosis_name = request.POST.get('diagnosis_name', '').strip()
        diagnosis_code = request.POST.get('diagnosis_code', '').strip()
        diagnosis_id = request.POST.get('diagnosis_id', '')

        if diagnosis_id:
            # Editing existing diagnosis
            try:
                diagnosis = Diagnosis.objects.get(pk=diagnosis_id)
            except Diagnosis.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Diagnosis not found.'})

            # Check for uniqueness excluding the current diagnosis
            if Diagnosis.objects.exclude(pk=diagnosis_id).filter(diagnosis_name=diagnosis_name).exists():
                return JsonResponse({'success': False, 'message': 'Diagnosis with this name already exists.'})
            
            if Diagnosis.objects.exclude(pk=diagnosis_id).filter(diagnosis_code=diagnosis_code).exists():
                return JsonResponse({'success': False, 'message': 'Diagnosis with this code already exists.'})

            # Update fields
            diagnosis.diagnosis_name = diagnosis_name
            diagnosis.diagnosis_code = diagnosis_code
            diagnosis.save()
            return JsonResponse({'success': True, 'message': 'Diagnosis updated successfully.'})
        else:
            # Adding new diagnosis
            # Check for uniqueness
            if Diagnosis.objects.filter(diagnosis_name=diagnosis_name).exists():
                return JsonResponse({'success': False, 'message': 'Diagnosis with this name already exists.'})
            if Diagnosis.objects.filter(diagnosis_code=diagnosis_code).exists():
                return JsonResponse({'success': False, 'message': 'Diagnosis with this code already exists.'})

            # Create new diagnosis
            diagnosis = Diagnosis.objects.create(diagnosis_name=diagnosis_name, diagnosis_code=diagnosis_code)
            return JsonResponse({'success': True, 'message': 'Diagnosis added successfully.'})

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required 
def ambulance_order_view(request):
    template_name = 'hod_template/ambulance_order_template.html'
    # Retrieve all ambulance records with the newest records appearing first
    ambulance_orders = AmbulanceOrder.objects.all().order_by('-id')
    return render(request, template_name, {'ambulance_orders': ambulance_orders})
    
@csrf_exempt  # Use csrf_exempt decorator for simplicity in this example. For a production scenario, consider using csrf protection.
def delete_ambulancecardorder(request):
    if request.method == 'POST':
        try:
            order_id = request.POST.get('order_id')
            # Delete procedure record
            record = get_object_or_404(AmbulanceVehicleOrder, pk=order_id)
            record.delete()

            return JsonResponse({'success': True, 'message': f' record for {record} deleted successfully.'})
        except AmbulanceVehicleOrder.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid record ID.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {e}'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

@csrf_exempt  # Use csrf_exempt decorator for simplicity in this example. For a production scenario, consider using csrf protection.
def delete_ambulancedorder(request):
    if request.method == 'POST':
        try:
            order_id = request.POST.get('order_id')
            # Delete procedure record
            record = get_object_or_404(AmbulanceOrder, pk=order_id)
            record.delete()

            return JsonResponse({'success': True, 'message': f' record for {record} deleted successfully.'})
        except AmbulanceVehicleOrder.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid record ID.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {e}'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

    
@login_required    
def vehicle_detail(request, order_id):
    # Retrieve the ambulance vehicle order object using the provided order_id
    order = get_object_or_404(AmbulanceVehicleOrder, pk=order_id)    
    # Render the vehicle detail template with the order object
    return render(request, 'hod_template/vehicle_detail.html', {'order': order})     



@login_required
def vehicle_ambulance_view(request):
    orders = AmbulanceVehicleOrder.objects.all().order_by('-id')  # Retrieve all AmbulanceVehicleOrder ambulance records, newest first
    template_name = 'hod_template/vehicle_ambulance.html'
    return render(request, template_name, {'orders': orders})


@login_required
def hospital_vehicle_list(request):
    vehicles = HospitalVehicle.objects.all()
    return render(request, 'hod_template/hospital_vehicle_list.html', {'vehicles': vehicles})

@csrf_exempt
def add_vehicle(request):
    if request.method == 'POST':
        try:
            vehicle_id = request.POST.get('vehicle_id')
            number = request.POST.get('vehicleNumber')
            plate_number = request.POST.get('plateNumber')
            vehicle_type = request.POST.get('vehicleType')

            # Check if required fields are present
            if not number or not plate_number or not vehicle_type:
                return JsonResponse({'success': False, 'message': 'All fields are required'})

            # Strip input values
            number = number.strip()
            plate_number = plate_number.strip()
            vehicle_type = vehicle_type.strip()

            if vehicle_id:
                # Editing existing vehicle
                vehicle = HospitalVehicle.objects.get(pk=vehicle_id)
                
                # Check for duplicates
                if HospitalVehicle.objects.filter(number=number).exclude(pk=vehicle_id).exists():
                    return JsonResponse({'success': False, 'message': 'Vehicle with this number already exists'})
                if HospitalVehicle.objects.filter(plate_number=plate_number).exclude(pk=vehicle_id).exists():
                    return JsonResponse({'success': False, 'message': 'Vehicle with this plate number already exists'})

                # Update vehicle details
                vehicle.number = number
                vehicle.plate_number = plate_number
                vehicle.vehicle_type = vehicle_type
                vehicle.save()
                return JsonResponse({'success': True, 'message': 'Hospital vehicle updated successfully'})
            else:
                # Check for duplicates when adding new vehicle
                if HospitalVehicle.objects.filter(number=number).exists():
                    return JsonResponse({'success': False, 'message': 'Vehicle with this number already exists'})
                if HospitalVehicle.objects.filter(plate_number=plate_number).exists():
                    return JsonResponse({'success': False, 'message': 'Vehicle with this plate number already exists'})

                # Add new vehicle
                new_vehicle = HospitalVehicle.objects.create(number=number, plate_number=plate_number, vehicle_type=vehicle_type)
                return JsonResponse({'success': True, 'message': 'Hospital vehicle added successfully', 'id': new_vehicle.id})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})



@require_POST
def delete_vehicle(request):
    try:
        # Get the frequency ID from the POST data
        vehicle_id = request.POST.get('vehicle_id')
        # Delete the frequency from the database
        vehicle = HospitalVehicle.objects.get(pk=vehicle_id)
        vehicle.delete()
        return JsonResponse({'success': True,'message': 'vehicle deleted successfully'})
    except HospitalVehicle.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'vehicle not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
    
@require_POST
def delete_ambulance_route(request):
    try:
        # Get the frequency ID from the POST data
        route_id = request.POST.get('route_id')
        # Delete the frequency from the database
        route = AmbulanceRoute.objects.get(id=route_id)
        route.delete()
        return JsonResponse({'status': 'success', 'message': 'route deleted successfully'})
    except AmbulanceRoute.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'route not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
@require_POST
def delete_ambulance_activity(request):
    try:
        # Get the frequency ID from the POST data
        activity_id = request.POST.get('activity_id')
        # Delete the frequency from the database
        activity = AmbulanceActivity.objects.get(id=activity_id)
        activity.delete()
        return JsonResponse({'status': 'success', 'message': 'activity deleted successfully'})
    except AmbulanceActivity.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'activity not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def ambulance_route_list(request):
    ambulance_routes = AmbulanceRoute.objects.all()
    return render(request, 'hod_template/ambulance_route_list.html', {'ambulance_routes': ambulance_routes})   

 

def add_or_edit_ambulance_route(request):
    if request.method == 'POST':
        try:
            # Retrieve data from POST request
            from_location = request.POST.get('from_location')
            to_location = request.POST.get('to_location')
            distance = request.POST.get('distance')
            cost = request.POST.get('cost')
            profit = request.POST.get('profit')
            advanced_ambulance_cost = request.POST.get('advanced_ambulance_cost')

            # Check if an AmbulanceRoute ID is provided for editing
            ambulance_route_id = request.POST.get('route_id')
            
            # Check for existing route with the same from_location and to_location
            

            if ambulance_route_id:
                existing_route = AmbulanceRoute.objects.filter(from_location=from_location, to_location=to_location).exclude(pk=ambulance_route_id).first()
                if existing_route:
                    return JsonResponse({'success': False, 'message': 'An ambulance route with the same From Location and To Location already exists.'})
                # Edit existing AmbulanceRoute
                ambulance_route = get_object_or_404(AmbulanceRoute, pk=ambulance_route_id)
                ambulance_route.from_location = from_location
                ambulance_route.to_location = to_location
                ambulance_route.distance = distance
                ambulance_route.cost = cost
                ambulance_route.profit = profit
                ambulance_route.advanced_ambulance_cost = advanced_ambulance_cost
                ambulance_route.save()
                return JsonResponse({'success': True,  'message': 'Ambulance route updated successfully'})
            else:
                existing_route = AmbulanceRoute.objects.filter(from_location=from_location, to_location=to_location).first()
                if existing_route:
                    return JsonResponse({'success': False, 'message': 'An ambulance route with the same From Location and To Location already exists.'})
                # Create new AmbulanceRoute
                ambulance_route = AmbulanceRoute.objects.create(
                    from_location=from_location,
                    to_location=to_location,
                    distance=distance,
                    cost=cost,
                    profit=profit,
                    advanced_ambulance_cost=advanced_ambulance_cost
                )
                return JsonResponse({'success': True,  'message': 'Ambulance route added successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    else:
        return JsonResponse({'success': False,  'message': 'Invalid request method'})

@csrf_exempt  
def add_ambulance_activity(request):
    if request.method == 'POST':
        try:
            # Retrieve data from POST request
            activity_id = request.POST.get('activity_id')  # For editing existing activity
            name = request.POST.get('name')
            cost = request.POST.get('cost')
            profit = request.POST.get('profit')

            # Perform data validation
            if not all([name, cost, profit]):
                return JsonResponse({'success': False, 'message': 'All fields are required'})

            # Check for duplicates
            if activity_id:
                # Editing existing activity
                if AmbulanceActivity.objects.filter(name=name).exclude(id=activity_id).exists():
                    return JsonResponse({'success': False, 'message': 'An activity with this name already exists'})

                activity = AmbulanceActivity.objects.get(id=activity_id)
                activity.name = name
                activity.cost = cost
                activity.profit = profit
                activity.save()
                return JsonResponse({'success': True, 'message': 'Ambulance activity updated successfully'})
            else:
                # Adding new activity
                if AmbulanceActivity.objects.filter(name=name).exists():
                    return JsonResponse({'success': False, 'message': 'An activity with this name already exists'})

                AmbulanceActivity.objects.create(name=name, cost=cost, profit=profit)
                return JsonResponse({'success': True, 'message': 'Ambulance activity added successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})


@login_required    
def ambulance_activity_list(request):
    ambulance_activities = AmbulanceActivity.objects.all()
    return render(request, 'hod_template/ambulance_activity_list.html', {'ambulance_activities': ambulance_activities}) 

@login_required
def consultation_notes_view(request):
    # Get all patients who have consultation notes
    patient_records = Patients.objects.filter(
        consultationnotes__isnull=False
    ).distinct().order_by('-consultationnotes__updated_at')

    return render(request, 'hod_template/manage_consultation_notes.html', {
        'patient_records': patient_records
    })





@login_required
def patient_imaging_view(request):
    # Get distinct (patient, visit) combinations with the latest imaging record date
    distinct_imaging_sets = (
        ImagingRecord.objects
        .values('patient_id', 'visit_id')
        .annotate(latest_date=Max('created_at'))
        .order_by('-latest_date')
    )

    patient_imaging_data = []

    for entry in distinct_imaging_sets:
        patient_id = entry['patient_id']
        visit_id = entry['visit_id']
        latest_date = entry['latest_date']

        imaging_records = ImagingRecord.objects.filter(
            patient_id=patient_id,
            visit_id=visit_id
        ).select_related('patient', 'visit', 'data_recorder__admin', 'imaging')

        if imaging_records.exists():
            first_imaging = imaging_records.first()
            patient_imaging_data.append({
                'patient': first_imaging.patient,
                'visit': first_imaging.visit,
                'latest_date': latest_date,
                'imaging_done_by': first_imaging.data_recorder,
                'imaging_records': imaging_records
            })

    context = {
        'patient_imaging': patient_imaging_data,
    }

    return render(request, 'hod_template/manage_imaging_result.html', context)


  

def fetch_order_counts_view(request):
    consultation_orders = ConsultationOrder.objects.all() 
    current_date = timezone.now().date()  
    # Retrieve the counts of unread and read orders for the current doctor
    unread_count = Order.objects.filter(order_type__in=[consultation.consultation.name for consultation in consultation_orders], order_date=current_date).count()
    read_count = Order.objects.filter(order_type__in=[consultation.consultation.name for consultation in consultation_orders], is_read=True).count()    
    # Return the counts as JSON response
    return JsonResponse({'unread_count': unread_count, 'read_count': read_count})

def fetch_radiology_order_counts_view(request):  
    pathodology_records=ImagingRecord.objects.all()
    current_date = timezone.now().date()   
    # Retrieve the counts of unread and read orders for the current doctor
    unread_count = Order.objects.filter(order_type__in=[pathology.imaging.name for pathology in pathodology_records],order_date=current_date) .count()
    read_count = Order.objects.filter(order_type__in=[pathology.imaging.name for pathology in pathodology_records], is_read=True) .count()    
    # Return the counts as JSON response
    return JsonResponse({'unread_count': unread_count, 'read_count': read_count})

def fetch_procedure_order_counts_view(request):  
    procedures = Procedure.objects.all()
    current_date = timezone.now().date() 
    # Retrieve the counts of unread and read orders for the current doctor
    unread_count = Order.objects.filter(order_type__in=[procedure.name.name for procedure in procedures], order_date=current_date).count()
    
    read_count = Order.objects.filter(order_type__in=[procedure.name.name for procedure in procedures], is_read=True).count()    
    # Return the counts as JSON response
    return JsonResponse({'unread_count': unread_count, 'read_count': read_count})

def fetch_prescription_counts_view(request):
    # Get the current date
    current_date = timezone.now().date()
    # Query the Prescription model for prescriptions created on the current date
    prescription_count = Prescription.objects.filter(created_at__date=current_date).count()
    # Construct the response data
    response_data = {
        'total_prescriptions': prescription_count
    }
    # Return the response as JSON
    return JsonResponse(response_data)


def add_service(request):
    try:
        if request.method == 'POST':
            # Get form data
            name = request.POST.get('name')
            description = request.POST.get('description')
            type_service = request.POST.get('type_service')
            coverage = request.POST.get('coverage')
            cash_cost = request.POST.get('cash_cost')
            nhif_cost = request.POST.get('nhif_cost')
            insurance_cost = request.POST.get('insurance_cost')
            
            # Check if service ID is provided (for editing existing service)
            service_id = request.POST.get('service_id')
            
            if service_id:
                if Service.objects.filter(name=name).exclude(id=service_id).exists():
                    return JsonResponse({'success': False, 'message': 'Service with this name already exists'})
                service = Service.objects.get(pk=service_id)
                # Update existing service
                service.name = name
                service.description = description
                service.type_service = type_service
                service.coverage = coverage
                service.cash_cost = cash_cost
                
                # Add nhif_cost and insurance_cost only if coverage is insurance
                if coverage == 'Insurance':
                    service.nhif_cost = nhif_cost
                    service.insurance_cost = insurance_cost
                else:
                    # If coverage is not insurance, set nhif_cost and insurance_cost to 0
                    service.nhif_cost = 0
                    service.insurance_cost = 0
                
                service.save()
                return JsonResponse({'success': True, 'message': 'Service updated successfully'})
            else:
                # Check if the service name already exists
                if Service.objects.filter(name=name).exists():
                    return JsonResponse({'success': False, 'message': 'Service with this name already exists'})
                
                # Add new service
                new_service = Service.objects.create(name=name, description=description, type_service=type_service, 
                                                      coverage=coverage, cash_cost=cash_cost)
                # Add nhif_cost and insurance_cost only if coverage is insurance
                if coverage == 'Insurance':
                    new_service.nhif_cost = nhif_cost
                    new_service.insurance_cost = insurance_cost
                
                else:
                    new_service.nhif_cost = 0
                    new_service.insurance_cost = 0  
                      
                new_service.save()
                    
                return JsonResponse({'success': True, 'message': 'Service added successfully'})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid request method'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})



@login_required
def medicine_dosage_managements(request):
    """
    View for managing medicine dosages
    """
    # Prefetch related data
    medicine_units = MedicineUnitMeasure.objects.all().only('id', 'name', 'short_name')
    
    # Get medicines that have dosages
    medicines_with_dosages = Medicine.objects.prefetch_related(
        Prefetch('dosages', queryset=MedicineDosage.objects.select_related('unit'))
    ).annotate(dosage_count=Count('dosages')).filter(dosage_count__gt=0)
    
    # Get all medicines for the dropdown
    all_medicines = Medicine.objects.all().select_related('formulation_unit')
    
    # Calculate statistics
    total_dosages = MedicineDosage.objects.count()
    default_dosages = MedicineDosage.objects.filter(is_default=True).count()
    
    context = {
        'medicines_with_dosages': medicines_with_dosages,
        'all_medicines': all_medicines,
        'medicine_units': medicine_units,
        'total_dosages': total_dosages,
        'default_dosages': default_dosages,
    }
    
    return render(request, 'hod_template/manage_medicine_dosages.html', context)

@csrf_exempt
@require_POST
@login_required
def add_medicine_dosage(request):
    """
    View for adding a new medicine dosage via AJAX
    """
    response_data = {}
    
    try:
        # Get form data
        medicine_id = request.POST.get('medicine_id')
        dosage_value = request.POST.get('dosage_value')
        unit_id = request.POST.get('unit')
        is_default = request.POST.get('is_default') == 'on'
        
        # Validate required fields
        if not all([medicine_id, dosage_value, unit_id]):
            response_data['success'] = False
            response_data['message'] = 'All fields are required.'
            return JsonResponse(response_data)
        
        # Get related objects
        try:
            medicine = Medicine.objects.get(pk=medicine_id)
            unit = MedicineUnitMeasure.objects.get(pk=unit_id)
        except (Medicine.DoesNotExist, MedicineUnitMeasure.DoesNotExist):
            response_data['success'] = False
            response_data['message'] = 'Invalid medicine or unit.'
            return JsonResponse(response_data)
        
        # Check if dosage already exists
        if MedicineDosage.objects.filter(medicine=medicine, dosage_value=dosage_value, unit=unit).exists():
            response_data['success'] = False
            response_data['message'] = 'This dosage already exists for this medicine.'
            return JsonResponse(response_data)
        
        # If setting as default, remove default from other dosages for this medicine
        if is_default:
            MedicineDosage.objects.filter(medicine=medicine, is_default=True).update(is_default=False)
        
        # Create new dosage
        dosage = MedicineDosage(
            medicine=medicine,
            dosage_value=dosage_value,
            unit=unit,
            is_default=is_default
        )
        dosage.save()
        
        response_data['success'] = True
        response_data['message'] = 'Dosage added successfully.'
        
    except Exception as e:
        response_data['success'] = False
        response_data['message'] = f'An error occurred: {str(e)}'
    
    return JsonResponse(response_data)

@csrf_exempt
@require_POST
@login_required
def update_medicine_dosage(request):
    """
    View for updating a medicine dosage via AJAX
    """
    response_data = {}
    
    try:
        # Get form data
        dosage_id = request.POST.get('dosage_id')
        dosage_value = request.POST.get('dosage_value')
        unit_id = request.POST.get('unit')
        is_default = request.POST.get('is_default') == 'on'
        
        # Validate required fields
        if not all([dosage_id, dosage_value, unit_id]):
            response_data['success'] = False
            response_data['message'] = 'All fields are required.'
            return JsonResponse(response_data)
        
        # Get the dosage to update
        try:
            dosage = MedicineDosage.objects.get(pk=dosage_id)
            unit = MedicineUnitMeasure.objects.get(pk=unit_id)
        except (MedicineDosage.DoesNotExist, MedicineUnitMeasure.DoesNotExist):
            response_data['success'] = False
            response_data['message'] = 'Invalid dosage or unit.'
            return JsonResponse(response_data)
        
        # Check if dosage already exists (excluding current dosage)
        if MedicineDosage.objects.exclude(pk=dosage_id).filter(
            medicine=dosage.medicine, 
            dosage_value=dosage_value, 
            unit=unit
        ).exists():
            response_data['success'] = False
            response_data['message'] = 'This dosage already exists for this medicine.'
            return JsonResponse(response_data)
        
        # If setting as default, remove default from other dosages for this medicine
        if is_default:
            MedicineDosage.objects.filter(medicine=dosage.medicine, is_default=True).update(is_default=False)
        
        # Update dosage
        dosage.dosage_value = dosage_value
        dosage.unit = unit
        dosage.is_default = is_default
        dosage.save()
        
        response_data['success'] = True
        response_data['message'] = 'Dosage updated successfully.'
        
    except Exception as e:
        response_data['success'] = False
        response_data['message'] = f'An error occurred: {str(e)}'
    
    return JsonResponse(response_data)

@csrf_exempt
@require_POST
@login_required
def set_default_dosages(request):
    """
    View for setting a dosage as default via AJAX
    """
    response_data = {}
    
    try:
        dosage_id = request.POST.get('dosage_id')
        
        if not dosage_id:
            response_data['success'] = False
            response_data['message'] = 'Dosage ID is required.'
            return JsonResponse(response_data)
        
        # Get the dosage
        try:
            dosage = MedicineDosage.objects.get(pk=dosage_id)
        except MedicineDosage.DoesNotExist:
            response_data['success'] = False
            response_data['message'] = 'Dosage not found.'
            return JsonResponse(response_data)
        
        # Remove default from other dosages for this medicine
        MedicineDosage.objects.filter(medicine=dosage.medicine, is_default=True).update(is_default=False)
        
        # Set this dosage as default
        dosage.is_default = True
        dosage.save()
        
        response_data['success'] = True
        response_data['message'] = 'Default dosage set successfully.'
        
    except Exception as e:
        response_data['success'] = False
        response_data['message'] = f'An error occurred: {str(e)}'
    
    return JsonResponse(response_data)

@csrf_exempt
@require_POST
@login_required
def delete_medicine_dosage(request):
    """
    View for deleting a medicine dosage via AJAX
    """
    response_data = {}
    
    try:
        dosage_id = request.POST.get('dosage_id')
        
        if not dosage_id:
            response_data['success'] = False
            response_data['message'] = 'Dosage ID is required.'
            return JsonResponse(response_data)
        
        # Get the dosage to delete
        try:
            dosage = MedicineDosage.objects.get(pk=dosage_id)
        except MedicineDosage.DoesNotExist:
            response_data['success'] = False
            response_data['message'] = 'Dosage not found.'
            return JsonResponse(response_data)
        
        # Check if this is the default dosage
        if dosage.is_default:
            response_data['success'] = False
            response_data['message'] = 'Cannot delete the default dosage. Set another dosage as default first.'
            return JsonResponse(response_data)
        
        # Delete the dosage
        dosage.delete()
        
        response_data['success'] = True
        response_data['message'] = 'Dosage deleted successfully.'
        
    except Exception as e:
        response_data['success'] = False
        response_data['message'] = f'An error occurred: {str(e)}'
    
    return JsonResponse(response_data)


@login_required
def medicine_dosage_management(request, medicine_id):
    """
    View to display dosage management page for a specific medicine
    """
    units=MedicineUnitMeasure.objects.all()
    medicine = get_object_or_404(Medicine, id=medicine_id)
    dosages = MedicineDosage.objects.filter(medicine=medicine).order_by('dosage_value')
    
    context = {
        'medicine': medicine,
        'dosages': dosages,
        'units': units,
    }
    
    return render(request, 'hod_template/manage_dosage.html', context)

@csrf_exempt
@require_POST
def add_dosage(request):
    """
    AJAX view to add multiple dosage options at once,
    ensuring no duplicates are created.
    """
    try:
        medicine_id = request.POST.get('medicine_id')
        dosage_values = request.POST.getlist('dosage_value[]')
        units = request.POST.getlist('unit[]')
        is_defaults = [val == 'True' for val in request.POST.getlist('is_default[]')]
        
        medicine = get_object_or_404(Medicine, id=medicine_id)

        # --- Normalize inputs ---
        # Convert pairs to tuples: (value, unit)
        new_dosages = list(zip(dosage_values, units, is_defaults))

        # --- Step 1: Check duplicates within the request itself ---
        seen = set()
        duplicates = []
        for value, unit, _ in new_dosages:
            key = (value.strip(), unit)
            if key in seen:
                duplicates.append(key)
            seen.add(key)

        if duplicates:
            return JsonResponse({
                'success': False,
                'message': f'Duplicate entries found in request: {duplicates}'
            })

        # --- Step 2: Check against existing records in DB ---
        existing = MedicineDosage.objects.filter(
            medicine=medicine,
            dosage_value__in=dosage_values,
            unit_id__in=units
        ).values_list("dosage_value", "unit_id")

        existing_set = {(val, str(unit)) for val, unit in existing}

        conflicts = [
            (val, unit) for val, unit, _ in new_dosages
            if (val, unit) in existing_set
        ]
        if conflicts:
            return JsonResponse({
                'success': False,
                'message': f'These dosages already exist: {conflicts}'
            })

        # --- Step 3: Handle default flag ---
        has_default = any(is_defaults)
        if has_default:
            MedicineDosage.objects.filter(medicine=medicine, is_default=True).update(is_default=False)

        # --- Step 4: Insert records safely ---
        with transaction.atomic():
            dosages = []
            default_set = False
            for value, unit, default_flag in new_dosages:
                # Only one default allowed
                is_default = default_flag and not default_set
                if is_default:
                    default_set = True

                dosages.append(MedicineDosage(
                    medicine=medicine,
                    dosage_value=value.strip(),
                    unit_id=unit,
                    is_default=is_default
                ))

            MedicineDosage.objects.bulk_create(dosages)

        return JsonResponse({
            'success': True,
            'message': f'{len(dosages)} dosage options added successfully!'
        })

    except IntegrityError:
        return JsonResponse({
            'success': False,
            'message': 'Integrity error: duplicate or invalid dosage detected.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error adding dosages: {str(e)}'
        })



@csrf_exempt
@require_POST
@login_required
def edit_dosage(request):
    """
    AJAX view to edit an existing dosage
    """
    try:
        dosage_id = request.POST.get('dosage_id')
        dosage_value = request.POST.get('dosage_value')
        unit_id = request.POST.get('unit')  # This is the ID, not the instance
        is_default = request.POST.get('is_default') == 'True'
        
        dosage = get_object_or_404(MedicineDosage, id=dosage_id)
        medicine = dosage.medicine
        
        # Get the MedicineUnitMeasure instance
        unit_instance = get_object_or_404(MedicineUnitMeasure, id=unit_id)
        
        # If setting as default, remove default status from other dosages
        if is_default and not dosage.is_default:
            MedicineDosage.objects.filter(medicine=medicine, is_default=True).update(is_default=False)
        
        # Update dosage
        dosage.dosage_value = dosage_value
        dosage.unit = unit_instance  # Assign the instance, not the ID
        dosage.is_default = is_default
        dosage.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Dosage updated successfully!'
        })
        
    except IntegrityError:
        return JsonResponse({
            'success': False,
            'message': 'A dosage with these values already exists for this medicine.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error updating dosage: {str(e)}'
        })

@csrf_exempt
@require_POST
@login_required
def delete_dosage(request):
    """
    AJAX view to delete a dosage
    """
    try:
        dosage_id = request.POST.get('dosage_id')
        dosage = get_object_or_404(MedicineDosage, id=dosage_id)
        
        # Don't allow deletion of default dosage
        if dosage.is_default:
            return JsonResponse({
                'success': False,
                'message': 'Cannot delete the default dosage. Set another dosage as default first.'
            })
            
        dosage.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Dosage deleted successfully!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error deleting dosage: {str(e)}'
        })

@csrf_exempt
@require_POST
@login_required
def set_default_dosage(request):
    """
    AJAX view to set a dosage as default
    """
    try:
        dosage_id = request.POST.get('dosage_id')
        dosage = get_object_or_404(MedicineDosage, id=dosage_id)
        
        # Remove default status from other dosages
        MedicineDosage.objects.filter(
            medicine=dosage.medicine, 
            is_default=True
        ).update(is_default=False)
        
        # Set this dosage as default
        dosage.is_default = True
        dosage.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Default dosage updated successfully!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error setting default dosage: {str(e)}'
        })        

@login_required    
def medicine_routes(request):
    routes = MedicineRoute.objects.all()
    return render(request, 'hod_template/medicine_routes.html', {'routes': routes}) 

@csrf_exempt
@require_POST
@login_required
def add_medicine_route(request):
    try:
        # Get form data
        name = request.POST.get('name', '').strip()
        explanation = request.POST.get('explanation')
        medicine_route_id = request.POST.get('route_id')  # For editing existing route

        if not name:
            return JsonResponse({'success': False, 'message': 'Name is required'})

        # Track the staff member
        staff_member = request.user.staff 
        
        if not staff_member:
            return JsonResponse({'success': False, 'message': 'Staff member not found for this user'})

        # If editing an existing record
        if medicine_route_id:
            if MedicineRoute.objects.filter(name=name).exclude(id=medicine_route_id).exists():
                return JsonResponse({'success': False, 'message': 'Medicine route with this name already exists'})
            
            medicine_route = get_object_or_404(MedicineRoute, pk=medicine_route_id)
            medicine_route.name = name
            medicine_route.explanation = explanation
            medicine_route.data_recorder = staff_member  # Track who last modified
            medicine_route.save()
            return JsonResponse({'success': True, 'message': 'Medicine route updated successfully'})
        
        # Creating a new record
        if MedicineRoute.objects.filter(name=name).exists():
            return JsonResponse({'success': False, 'message': 'Medicine route with this name already exists'})
        
        MedicineRoute.objects.create(
            name=name,
            explanation=explanation,
            data_recorder=staff_member
        )
        return JsonResponse({'success': True, 'message': 'Medicine route added successfully'})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

    
def delete_medicine_route(request):
    try:
        if request.method == 'POST':
            route_id = request.POST.get('route_id')
            
            if route_id:
                try:
                    route = MedicineRoute.objects.get(pk=route_id)
                    route.delete()
                    return JsonResponse({'success': True, 'message': 'Medicine route deleted successfully'})
                except MedicineRoute.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Medicine route does not exist'})
            else:
                return JsonResponse({'success': False, 'message': 'Invalid route ID'})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid request method'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})    

@login_required    
def medicine_unit_measures(request):
    measures = MedicineUnitMeasure.objects.all()
    return render(request, 'hod_template/medicine_unit_measures.html', {'measures': measures}) 


@csrf_exempt
@require_POST
@login_required
def add_medicine_unit_measure(request):
    """
    Create or update a MedicineUnitMeasure entry.
    Tracks the staff/HOD who recorded or updated the entry.
    """
    try:
        # =======================
        # 1. Get form data
        # =======================
        name = request.POST.get('name')
        short_name = request.POST.get('short_name')
        unit_measure_id = request.POST.get('unit_measure_id')  # for updates

        if not name or not short_name:
            return JsonResponse({
                'success': False,
                'message': 'Both name and short name are required.'
            })

        # =======================
        # 2. Identify staff member
        # =======================
        staff_member = request.user.staff 

        if not staff_member:
            return JsonResponse({
                'success': False,
                'message': 'Unable to determine staff member for this user.'
            })

        # =======================
        # 3. Update existing record
        # =======================
        if unit_measure_id:
            unit_measure = get_object_or_404(MedicineUnitMeasure, pk=unit_measure_id)

            # Check duplicates excluding current record
            if MedicineUnitMeasure.objects.filter(name=name).exclude(pk=unit_measure_id).exists():
                return JsonResponse({'success': False, 'message': 'A unit with this name already exists.'})
            if MedicineUnitMeasure.objects.filter(short_name=short_name).exclude(pk=unit_measure_id).exists():
                return JsonResponse({'success': False, 'message': 'A unit with this short name already exists.'})

            # Update fields
            unit_measure.name = name
            unit_measure.short_name = short_name
            unit_measure.data_recorder = staff_member  # track who updated
            unit_measure.save()

            return JsonResponse({'success': True, 'message': 'Medicine unit measure updated successfully.'})

        # =======================
        # 4. Create new record
        # =======================
        else:
            # Check duplicates
            if MedicineUnitMeasure.objects.filter(name=name).exists():
                return JsonResponse({'success': False, 'message': 'A unit with this name already exists.'})
            if MedicineUnitMeasure.objects.filter(short_name=short_name).exists():
                return JsonResponse({'success': False, 'message': 'A unit with this short name already exists.'})

            # Create new entry
            MedicineUnitMeasure.objects.create(
                name=name,
                short_name=short_name,
                data_recorder=staff_member
            )

            return JsonResponse({'success': True, 'message': 'Medicine unit measure added successfully.'})

    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
    

      
   
def delete_medicine_unit_measure(request):
    try:
        if request.method == 'POST':
            unit_measure_id = request.POST.get('unit_measure_id')
            
            if unit_measure_id:
                try:
                    unit_measure = MedicineUnitMeasure.objects.get(pk=unit_measure_id)
                    unit_measure.delete()
                    return JsonResponse({'success': True, 'message': 'Medicine unit_measure deleted successfully'})
                except MedicineUnitMeasure.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Medicine unit_measure does not exist'})
            else:
                return JsonResponse({'success': False, 'message': 'Invalid unit_measure ID'})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid request method'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})  

@login_required
def employee_detail(request):
    try:
        # Get the logged-in staff member
        staff_member = request.user.staff        
        # Get the employee record for the logged-in staff member
        employee = get_object_or_404(Employee, name=staff_member)       
        # Fetch the related employee deductions and salary change records
        employee_deductions = EmployeeDeduction.objects.filter(employee=employee)
        salary_change_records = SalaryChangeRecord.objects.filter(employee=employee)

        # Context data to pass to the template
        context = {
            'staff_member': staff_member,
            'employee': employee,
            'employee_deductions': employee_deductions,
            'salary_change_records': salary_change_records,
        }
    except Staffs.DoesNotExist:
        context = {
            'error': "Staff member not found."
        }
    except Employee.DoesNotExist:
        context = {
            'error': "Employee record not found."
        }
    except Exception as e:
        context = {
            'error': str(e)
        }
    
    return render(request, 'hod_template/employee_detail.html', context)

def counseling_list_view(request):
    counselings = Counseling.objects.all().order_by('-created_at')
    return render(request, 'hod_template/manage_counselling.html', {'counselings': counselings})  



def discharge_notes_list_view(request):
    discharge_notes = DischargesNotes.objects.all().order_by('-discharge_date')
    return render(request, 'hod_template/manage_discharge.html', {'discharge_notes': discharge_notes}) 


def observation_record_list_view(request):
    observation_records = ObservationRecord.objects.all().order_by('-created_at')
    return render(request, 'hod_template/manage_observation_record.html', {'observation_records': observation_records}) 

def download_observation_pdf(request, patient_id, visit_id):
    # Fetch the required patient and visit
    visit = get_object_or_404(PatientVisits, id=visit_id)
    patient = get_object_or_404(Patients, id=patient_id)
    observation_record = get_object_or_404(ObservationRecord, patient=patient, visit=visit)

    # Prepare context for the template
    context = {
        'observation_record': observation_record,
        'visit': visit,
    }

    # Render HTML template
    html_content = render_to_string('hod_template/observation_notes_detail.html', context)

    # Create a temporary directory and file path
    temp_dir = os.path.join(os.path.expanduser("~"), "pdf_temp")
    os.makedirs(temp_dir, exist_ok=True)
    file_name = f'observation_{patient.full_name}_{visit.vst}.pdf'
    file_path = os.path.join(temp_dir, file_name)

    # Delete old file if it exists
    if os.path.exists(file_path):
        os.remove(file_path)

    # Generate PDF
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(file_path)

    # Return file as response
    with open(file_path, 'rb') as f:
        pdf_data = f.read()

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response

def download_discharge_pdf(request, patient_id, visit_id):
    # Fetch patient, visit, and discharge note
    visit = get_object_or_404(PatientVisits, id=visit_id)
    patient = get_object_or_404(Patients, id=patient_id)
    discharge_note = get_object_or_404(DischargesNotes, patient=patient, visit=visit)

    # Prepare context
    context = {
        'discharge_note': discharge_note,
        'patient': patient,
        'visit': visit,
    }

    # Render HTML content using a dedicated template
    html_content = render_to_string('hod_template/discharge_note_detail.html', context)

    # Prepare file path
    temp_dir = os.path.join(os.path.expanduser("~"), "pdf_temp")
    os.makedirs(temp_dir, exist_ok=True)
    file_name = f'discharge_{patient.full_name}_{visit.vst}.pdf'
    file_path = os.path.join(temp_dir, file_name)

    # Remove old file if exists
    if os.path.exists(file_path):
        os.remove(file_path)

    # Generate PDF
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(file_path)

    # Return PDF response
    with open(file_path, 'rb') as f:
        pdf_data = f.read()

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response   

def download_counseling_pdf(request, patient_id, visit_id):
    # Fetch patient, visit, and counseling note
    visit = get_object_or_404(PatientVisits, id=visit_id)
    patient = get_object_or_404(Patients, id=patient_id)
    counseling = get_object_or_404(Counseling, patient=patient, visit=visit)

    # Prepare context
    context = {
        'counseling': counseling,
        'patient': patient,
        'visit': visit,
    }

    # Render HTML content from a dedicated counseling note template
    html_content = render_to_string('hod_template/counseling_notes_details.html', context)

    # Prepare PDF file path
    temp_dir = os.path.join(os.path.expanduser("~"), "pdf_temp")
    os.makedirs(temp_dir, exist_ok=True)
    file_name = f'counseling_{patient.full_name}_{visit.vst}.pdf'
    file_path = os.path.join(temp_dir, file_name)

    # Delete existing PDF if present
    if os.path.exists(file_path):
        os.remove(file_path)

    # Generate PDF using WeasyPrint
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(file_path)

    # Serve PDF as download
    with open(file_path, 'rb') as f:
        pdf_data = f.read()

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response    

def download_referral_pdf(request, patient_id, visit_id):
    # Fetch patient, visit, and referral
    visit = get_object_or_404(PatientVisits, id=visit_id)
    patient = get_object_or_404(Patients, id=patient_id)
    referral = get_object_or_404(Referral, patient=patient, visit=visit)

    # Prepare context
    context = {
        'referral': referral,
        'patient': patient,
        'visit': visit,
    }

    # Render HTML content from a dedicated referral note template
    html_content = render_to_string('hod_template/view_referral.html', context)

    # Prepare PDF file path
    temp_dir = os.path.join(os.path.expanduser("~"), "pdf_temp")
    os.makedirs(temp_dir, exist_ok=True)
    file_name = f'referral_{patient.full_name}_{visit.vst}.pdf'
    file_path = os.path.join(temp_dir, file_name)

    # Delete existing PDF if present
    if os.path.exists(file_path):
        os.remove(file_path)

    # Generate PDF using WeasyPrint
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(file_path)

    # Serve PDF as download
    with open(file_path, 'rb') as f:
        pdf_data = f.read()

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response


def download_prescription_notes_pdf(request, patient_id, visit_id):
    # Fetch patient and visit
    patient = get_object_or_404(Patients, id=patient_id)
    visit = get_object_or_404(PatientVisits, id=visit_id)

    # Get all prescriptions for this patient and visit
    prescriptions = Prescription.objects.filter(patient=patient, visit=visit)

    # Prepare context
    context = {
        'patient': patient,
        'visit': visit,
        'prescriptions': prescriptions,
    }

    # Render HTML content using a dedicated template
    html_content = render_to_string('hod_template/prescription_notes.html', context)

    # Prepare PDF file path
    temp_dir = os.path.join(os.path.expanduser("~"), "pdf_temp")
    os.makedirs(temp_dir, exist_ok=True)
    file_name = f'prescription_notes_{patient.full_name}_{visit.vst}.pdf'
    file_path = os.path.join(temp_dir, file_name)

    # Remove old file if exists
    if os.path.exists(file_path):
        os.remove(file_path)

    # Generate PDF using WeasyPrint
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(file_path)

    # Serve file as HTTP response
    with open(file_path, 'rb') as f:
        pdf_data = f.read()

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response

def download_prescription_bill_pdf(request, patient_id, visit_id):
    # Fetch patient and visit
    patient = get_object_or_404(Patients, id=patient_id)
    visit = get_object_or_404(PatientVisits, id=visit_id)

    # Get all prescriptions for this visit and patient
    prescriptions = Prescription.objects.filter(patient=patient, visit=visit)

    # Prepare context
    context = {
        'patient': patient,
        'visit': visit,
        'prescriptions': prescriptions,
    }

    # Render HTML content using template
    html_content = render_to_string('hod_template/prescription_bill.html', context)

    # Create temporary folder and define file path
    temp_dir = os.path.join(os.path.expanduser("~"), "pdf_temp")
    os.makedirs(temp_dir, exist_ok=True)
    file_name = f'prescription_bill_{patient.full_name}_{visit.vst}.pdf'
    file_path = os.path.join(temp_dir, file_name)

    # Remove old file if it exists
    if os.path.exists(file_path):
        os.remove(file_path)

    # Generate PDF using WeasyPrint
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(file_path)

    # Return PDF as downloadable response
    with open(file_path, 'rb') as f:
        pdf_data = f.read()

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response


@login_required
def download_procedure_result_pdf(request, procedure_id):
    # Fetch procedure or return 404
    procedure = get_object_or_404(Procedure.objects.select_related('patient', 'visit', 'name'), id=procedure_id)

    # Prepare context for template
    context = {
        'procedure': procedure,
    }

    # Render the HTML content using template
    html_content = render_to_string('hod_template/pdf_procedure_result.html', context)

    # Create temporary directory for storing the PDF
    temp_dir = os.path.join(os.path.expanduser("~"), "pdf_temp")
    os.makedirs(temp_dir, exist_ok=True)

    # Define safe file name and full path
    file_name = f"procedure_result_{procedure.patient.full_name}_{procedure.procedure_number}.pdf"
    file_path = os.path.join(temp_dir, file_name)

    # Remove file if it already exists
    if os.path.exists(file_path):
        os.remove(file_path)

    # Generate PDF using WeasyPrint
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(file_path)

    # Return the PDF as downloadable response
    with open(file_path, 'rb') as f:
        pdf_data = f.read()

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response    

@login_required
def download_all_procedures_pdf(request, patient_mrn, visit_vst):
    # Get patient and visit
    patient = get_object_or_404(Patients, mrn=patient_mrn)
    visit = get_object_or_404(PatientVisits, vst=visit_vst)

    # Fetch all related procedures
    procedures = Procedure.objects.filter(patient=patient, visit=visit).select_related('name', 'data_recorder')

    if not procedures.exists():
        return HttpResponse("No procedures found for this visit.", status=404)

    context = {
        'patient': patient,
        'visit': visit,
        'procedures': procedures
    }

    # Render the template
    html_content = render_to_string('hod_template/pdf_all_procedures.html', context)

    # Generate file
    file_name = f"all_procedures_{patient.full_name}_{visit.vst}.pdf"
    temp_dir = os.path.join(os.path.expanduser("~"), "pdf_temp")
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file_name)

    # Remove existing file
    if os.path.exists(file_path):
        os.remove(file_path)

    # Write PDF
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(file_path)

    # Return file
    with open(file_path, 'rb') as f:
        pdf_data = f.read()

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response    


@login_required
def download_lab_result_pdf(request, lab_id):
    # Fetch the lab order or return 404 if not found
    lab = get_object_or_404(
                    LaboratoryOrder.objects.select_related('patient', 'visit', 'data_recorder', 'lab_test'),
        id=lab_id
    )

    # Prepare context for PDF rendering
    context = {
        'lab': lab,
    }

    # Render HTML from template
    html_content = render_to_string('hod_template/pdf_lab_result.html', context)

    # Setup temporary directory
    temp_dir = os.path.join(os.path.expanduser("~"), "pdf_temp")
    os.makedirs(temp_dir, exist_ok=True)

    # Safe file name and path
    safe_name = lab.patient.full_name.replace(" ", "_")
    file_name = f"lab_result_{safe_name}_{lab.lab_number}.pdf"
    file_path = os.path.join(temp_dir, file_name)

    # Delete if file exists
    if os.path.exists(file_path):
        os.remove(file_path)

    # Generate PDF with WeasyPrint
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(file_path)

    # Serve the PDF as an HTTP response
    with open(file_path, 'rb') as f:
        pdf_data = f.read()

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response


@login_required
def download_all_lab_results_pdf(request, patient_mrn, visit_vst):
    # Fetch patient and visit objects
    patient = get_object_or_404(Patients, mrn=patient_mrn)
    visit = get_object_or_404(PatientVisits, vst=visit_vst)

    # Fetch all laboratory orders for this patient and visit
    lab_tests = LaboratoryOrder.objects.filter(patient=patient, visit=visit).select_related(
        'lab_test', 'data_recorder'
    )

    if not lab_tests.exists():
        return HttpResponse("No lab results found for this visit.", status=404)

    # Prepare the template context
    context = {
        'patient': patient,
        'visit': visit,
        'lab_tests': lab_tests
    }

    # Render HTML template
    html_content = render_to_string('hod_template/pdf_all_lab_results.html', context)

    # Define a safe filename and temporary path
    temp_dir = os.path.join(os.path.expanduser("~"), "pdf_temp")
    os.makedirs(temp_dir, exist_ok=True)
    safe_name = patient.full_name.replace(" ", "_")
    file_name = f"all_lab_results_{safe_name}_{visit.vst}.pdf"
    file_path = os.path.join(temp_dir, file_name)

    # Remove existing file if it exists
    if os.path.exists(file_path):
        os.remove(file_path)

    # Generate the PDF file
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(file_path)

    # Serve the file as an HTTP response
    with open(file_path, 'rb') as f:
        pdf_data = f.read()

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response


@login_required
def download_imaging_result_pdf(request, imaging_id):
    # Fetch the imaging record or return 404
    imaging = get_object_or_404(
        ImagingRecord.objects.select_related('patient', 'visit', 'data_recorder', 'imaging'),
        id=imaging_id
    )

    # Prepare context for rendering
    context = {
        'imaging': imaging,
    }

    # Render HTML content from template
    html_content = render_to_string('hod_template/pdf_imaging_result.html', context)

    # Temporary directory
    temp_dir = os.path.join(os.path.expanduser("~"), "pdf_temp")
    os.makedirs(temp_dir, exist_ok=True)

    # Safe filename
    safe_name = imaging.patient.full_name.replace(" ", "_")
    file_name = f"imaging_result_{safe_name}_{imaging.id}.pdf"
    file_path = os.path.join(temp_dir, file_name)

    # Delete existing file if present
    if os.path.exists(file_path):
        os.remove(file_path)

    # Generate PDF using WeasyPrint
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(file_path)

    # Serve PDF
    with open(file_path, 'rb') as f:
        pdf_data = f.read()

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response


@login_required
def download_all_imaging_results_pdf(request, patient_mrn, visit_vst):
    # Fetch patient and visit instances
    patient = get_object_or_404(Patients, mrn=patient_mrn)
    visit = get_object_or_404(PatientVisits, vst=visit_vst)

    # Fetch all imaging records for this visit
    imaging_records = ImagingRecord.objects.filter(patient=patient, visit=visit).select_related(
        'imaging', 'data_recorder'
    )

    if not imaging_records.exists():
        return HttpResponse("No imaging records found for this visit.", status=404)

    # Prepare context for rendering
    context = {
        'patient': patient,
        'visit': visit,
        'imaging_records': imaging_records
    }

    # Render HTML content
    html_content = render_to_string('hod_template/pdf_all_imaging_results.html', context)

    # Prepare temporary directory and file path
    temp_dir = os.path.join(os.path.expanduser("~"), "pdf_temp")
    os.makedirs(temp_dir, exist_ok=True)
    safe_name = patient.full_name.replace(" ", "_")
    file_name = f"all_imaging_results_{safe_name}_{visit.vst}.pdf"
    file_path = os.path.join(temp_dir, file_name)

    # Delete existing file if any
    if os.path.exists(file_path):
        os.remove(file_path)

    # Generate PDF
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(file_path)

    # Serve PDF response
    with open(file_path, 'rb') as f:
        pdf_data = f.read()

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response


@login_required
def download_consultation_summary_pdf(request, patient_id, visit_id):
    # Fetch core patient and visit info
    patient = get_object_or_404(Patients, id=patient_id)
    visit = get_object_or_404(PatientVisits, id=visit_id)

    # Query all related models for that visit
    counseling = Counseling.objects.filter(patient=patient, visit=visit).last()
    prescriptions = Prescription.objects.filter(patient=patient, visit=visit)
    observations = ObservationRecord.objects.filter(patient=patient, visit=visit).last()
    discharge_note = DischargesNotes.objects.filter(patient=patient, visit=visit).last()
    referral = Referral.objects.filter(patient=patient, visit=visit).last()
    complaints = ClinicChiefComplaint.objects.filter(patient=patient, visit=visit)
    vitals = PatientVital.objects.filter(patient=patient, visit=visit).last()

    # NEW: Add Consultation Notes
    consultation_note = ConsultationNotes.objects.filter(patient=patient, visit=visit).last()

    # NEW: Add Imaging Records
    imaging_records = ImagingRecord.objects.filter(patient=patient, visit=visit).select_related('imaging', 'data_recorder')

    # NEW: Add Laboratory Orders
    lab_tests = LaboratoryOrder.objects.filter(patient=patient, visit=visit).select_related('lab_test', 'data_recorder')

    # Prepare context
    context = {
        'patient': patient,
        'visit': visit,
        'counseling': counseling,
        'prescriptions': prescriptions,
        'observation_record': observations,
        'discharge_note': discharge_note,
        'referral': referral,
        'complaints': complaints,
        'vitals': vitals,
        'consultation_note': consultation_note,
        'imaging_records': imaging_records,
        'lab_tests': lab_tests,
    }

    # Render the HTML template
    html_content = render_to_string('hod_template/pdf_consultation_summary.html', context)

    # Save to a temp directory
    safe_name = patient.full_name.replace(" ", "_")
    file_name = f"consultation_summary_{safe_name}_{visit.vst}.pdf"
    temp_dir = os.path.join(os.path.expanduser("~"), "pdf_temp")
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file_name)

    if os.path.exists(file_path):
        os.remove(file_path)

    # Generate PDF
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(file_path)

    # Return the file as a response
    with open(file_path, 'rb') as f:
        pdf_data = f.read()

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response


@login_required
def download_invoice_bill_pdf(request, patient_id, visit_id):
    # Fetch patient and visit objects
    patient = get_object_or_404(Patients, id=patient_id)
    visit = get_object_or_404(PatientVisits, id=visit_id)

    # Get all orders for this patient and visit
    orders = Order.objects.filter(patient=patient, visit=visit)

    if not orders.exists():
        return HttpResponse("No orders found for this visit.", status=404)

    # Calculate total cost
    total_cost = orders.aggregate(total=Sum('cost'))['total'] or 0

    # Prepare context
    context = {
        'patient': patient,
        'visit': visit,
        'orders': orders,
        'total_cost': total_cost,
    }

    # Render HTML content
    html_content = render_to_string('hod_template/invoice_template.html', context)

    # Define PDF storage path
    temp_dir = os.path.join(os.path.expanduser("~"), "pdf_temp")
    os.makedirs(temp_dir, exist_ok=True)
    safe_name = patient.full_name.replace(" ", "_")
    file_name = f"invoice_bill_{safe_name}_{visit.vst}.pdf"
    file_path = os.path.join(temp_dir, file_name)

    # Remove old file if it exists
    if os.path.exists(file_path):
        os.remove(file_path)

    # Generate PDF with WeasyPrint
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(file_path)

    # Return file as download
    with open(file_path, 'rb') as f:
        pdf_data = f.read()

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response          