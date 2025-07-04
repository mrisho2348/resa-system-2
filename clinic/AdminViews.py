import calendar
from datetime import  date, datetime
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
from clinic.models import Consultation,  CustomUser, DiseaseRecode,  Medicine,  PathodologyRecord,  Procedure, Staffs
from django.db import IntegrityError
from django.views.decorators.http import require_POST
from django.db.models import OuterRef, Subquery
from django.utils.decorators import method_decorator
from kahamahmis.forms import StaffProfileForm
from django.views import View
from .models import AmbulanceActivity, AmbulanceOrder, AmbulanceRoute, AmbulanceVehicleOrder, ClinicChiefComplaint, ConsultationNotes,  ConsultationOrder, Counseling,   Diagnosis, DischargesNotes, Employee, EmployeeDeduction, Equipment,  HealthRecord,  HospitalVehicle, ImagingRecord, LaboratoryOrder,  MedicineRoute, MedicineUnitMeasure, ObservationRecord, Order, PatientDiagnosisRecord, PatientVisits, PatientVital, Prescription, PrescriptionFrequency, Procedure, Patients,  Reagent,  Referral, SalaryChangeRecord, SalaryPayment,  Service
from django.db.models import Max,Sum,Q,Count
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import logout
from weasyprint import HTML
from django.template.loader import render_to_string
import os 

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

        def aggregate_earnings(querysets, field='cost'):
            earnings = {'nhif': 0, 'cash': 0, 'other': 0}
            for qs in querysets:
                earnings['nhif'] += qs.filter(
                    patient__payment_form='Insurance',
                    patient__insurance_name__icontains='nhif'
                ).aggregate(total=Sum(field))['total'] or 0

                earnings['cash'] += qs.filter(
                    patient__payment_form='Cash'
                ).aggregate(total=Sum(field))['total'] or 0

                earnings['other'] += qs.filter(
                    patient__payment_form='Insurance'
                ).exclude(patient__insurance_name__icontains='nhif'
                ).aggregate(total=Sum(field))['total'] or 0
            return earnings

        def compile_total(data):
            return data['nhif'] + data['cash'] + data['other']

        # DAILY
        daily_hospital_qs = [
            LaboratoryOrder.objects.filter(order_date=today),
            Procedure.objects.filter(order_date=today),
            ImagingRecord.objects.filter(order_date=today),
            ConsultationOrder.objects.filter(order_date=today),
        ]

        daily_prescription_qs = [
            Prescription.objects.filter(created_at__date=today),
        ]

        daily_hospital_data = aggregate_earnings(daily_hospital_qs)
        daily_prescription_data = aggregate_earnings(daily_prescription_qs, field='total_price')

        # MONTHLY
        monthly_hospital_qs = [
            LaboratoryOrder.objects.filter(order_date__month=current_month, order_date__year=current_year),
            Procedure.objects.filter(order_date__month=current_month, order_date__year=current_year),
            ImagingRecord.objects.filter(order_date__month=current_month, order_date__year=current_year),
            ConsultationOrder.objects.filter(order_date__month=current_month, order_date__year=current_year),
        ]

        monthly_prescription_qs = [
            Prescription.objects.filter(created_at__month=current_month, created_at__year=current_year),
        ]

        monthly_hospital_data = aggregate_earnings(monthly_hospital_qs)
        monthly_prescription_data = aggregate_earnings(monthly_prescription_qs, field='total_price')

        # YEARLY
        yearly_hospital_qs = [
            LaboratoryOrder.objects.filter(order_date__year=current_year),
            Procedure.objects.filter(order_date__year=current_year),
            ImagingRecord.objects.filter(order_date__year=current_year),
            ConsultationOrder.objects.filter(order_date__year=current_year),
        ]

        yearly_prescription_qs = [
            Prescription.objects.filter(created_at__year=current_year),
        ]

        yearly_hospital_data = aggregate_earnings(yearly_hospital_qs)
        yearly_prescription_data = aggregate_earnings(yearly_prescription_qs, field='total_price')

        # ALL-TIME
        alltime_hospital_qs = [
            LaboratoryOrder.objects.all(),
            Procedure.objects.all(),
            ImagingRecord.objects.all(),
            ConsultationOrder.objects.all(),
        ]

        alltime_prescription_qs = [
            Prescription.objects.all(),
        ]

        alltime_hospital_data = aggregate_earnings(alltime_hospital_qs)
        alltime_prescription_data = aggregate_earnings(alltime_prescription_qs, field='total_price')

        return JsonResponse({
            'daily': {
                'hospital': {
                    'nhif': daily_hospital_data['nhif'],
                    'cash': daily_hospital_data['cash'],
                    'other': daily_hospital_data['other'],
                    'total': compile_total(daily_hospital_data),
                },
                'prescription': {
                    'nhif': daily_prescription_data['nhif'],
                    'cash': daily_prescription_data['cash'],
                    'other': daily_prescription_data['other'],
                    'total': compile_total(daily_prescription_data),
                },
                'grand_total': compile_total(daily_hospital_data) + compile_total(daily_prescription_data),
            },
            'monthly': {
                'hospital': {
                    'nhif': monthly_hospital_data['nhif'],
                    'cash': monthly_hospital_data['cash'],
                    'other': monthly_hospital_data['other'],
                    'total': compile_total(monthly_hospital_data),
                },
                'prescription': {
                    'nhif': monthly_prescription_data['nhif'],
                    'cash': monthly_prescription_data['cash'],
                    'other': monthly_prescription_data['other'],
                    'total': compile_total(monthly_prescription_data),
                },
                'grand_total': compile_total(monthly_hospital_data) + compile_total(monthly_prescription_data),
            },
            'yearly': {
                'hospital': {
                    'nhif': yearly_hospital_data['nhif'],
                    'cash': yearly_hospital_data['cash'],
                    'other': yearly_hospital_data['other'],
                    'total': compile_total(yearly_hospital_data),
                },
                'prescription': {
                    'nhif': yearly_prescription_data['nhif'],
                    'cash': yearly_prescription_data['cash'],
                    'other': yearly_prescription_data['other'],
                    'total': compile_total(yearly_prescription_data),
                },
                'grand_total': compile_total(yearly_hospital_data) + compile_total(yearly_prescription_data),
            },
            'alltime': {
                'hospital': {
                    'nhif': alltime_hospital_data['nhif'],
                    'cash': alltime_hospital_data['cash'],
                    'other': alltime_hospital_data['other'],
                    'total': compile_total(alltime_hospital_data),
                },
                'prescription': {
                    'nhif': alltime_prescription_data['nhif'],
                    'cash': alltime_prescription_data['cash'],
                    'other': alltime_prescription_data['other'],
                    'total': compile_total(alltime_prescription_data),
                },
                'grand_total': compile_total(alltime_hospital_data) + compile_total(alltime_prescription_data),
            },
        })

    except Exception as e:
        logger.error(f"Error in get_earnings_data view: {str(e)}")
        return JsonResponse({'error': f'An error occurred while retrieving earnings data. {str(e)}'}, status=500)


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

    
    
@csrf_exempt  # Use csrf_exempt decorator for simplicity in this example. For a production scenario, consider using csrf protection.
def delete_healthrecord(request):
    if request.method == 'POST':
        try:
            health_record_id = request.POST.get('health_record_id')

            # Delete procedure record
            health_record = get_object_or_404(HealthRecord, pk=health_record_id)
            health_record.delete()

            return JsonResponse({'success': True, 'message': f'health_record record for {health_record.name} deleted successfully.'})
        except HealthRecord.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid health_record ID.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {e}'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

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
def update_staff_status(request):
    try:
        if request.method == 'POST':
            # Get the user_id and is_active values from POST data
            user_id = request.POST.get('user_id')
            is_active = request.POST.get('is_active')

            # Retrieve the staff object or return a 404 response if not found
            staff = get_object_or_404(CustomUser, id=user_id)

            # Toggle the is_active status based on the received value
            if is_active == '1':
                staff.is_active = False
                messages.success(request, f'{staff.username} has been deactivated.')
            elif is_active == '0':
                staff.is_active = True
                messages.success(request, f'{staff.username} has been activated.')

                # Send activation email to the user
                login_url = request.build_absolute_uri(reverse('clinic:login'))
                email_content = (
                    f"Dear {staff.first_name} {staff.last_name},\n\n"
                    f"MRISHO HAMISI is pleased to inform you that your account has been activated successfully. "
                    f"You can now log in to your account using the following link:\n\n"
                    f"{login_url}\n\n"
                    f"Your login details are as follows:\n"
                    f"Email: {staff.email}\n"                   
                    f"If you have any questions or need further assistance, please do not hesitate to contact the administrator.\n\n"
                    f"Best regards,\n"
                    f"RESA Team"
                )
                send_mail(
                    'Account Activation Notice',
                    email_content,
                    'admin@example.com',
                    [staff.email],
                    fail_silently=False,
                )
            else:
                messages.error(request, 'Invalid request')
                return redirect('admin_manage_staff')  

            staff.save()
        else:
            messages.error(request, 'Invalid request method')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')

    # Redirect back to the staff list page
    return redirect('admin_manage_staff') 


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
def update_equipment_status(request):
    try:
        if request.method == 'POST':
            # Get the user_id and is_active values from POST data
            equipment_id = request.POST.get('equipment_id')
            is_active = request.POST.get('is_active')

            # Retrieve the staff object or return a 404 response if not found
            equipment = get_object_or_404(Equipment, id=equipment_id)

            # Toggle the is_active status based on the received value
            if is_active == '1':
                equipment.is_active = False
            elif is_active == '0':
                equipment.is_active = True
            else:
                messages.error(request, 'Invalid request')
                return redirect('admin_equipment_list')  

            equipment.save()
            messages.success(request, 'equipment updated successfully')
        else:
            messages.error(request, 'Invalid request method')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')

    # Redirect back to the staff list page
    return redirect('admin_equipment_list') 

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
                return redirect("admin_edit_staff")

            # Retrieve the staff instance from the database
            try:
                staff = Staffs.objects.get(id=staff_id)
            except ObjectDoesNotExist:
                messages.error(request, "Staff not found")
                return redirect("admin_edit_staff")

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
                return redirect("admin_edit_staff", staff_id=staff_id)

            if CustomUser.objects.filter(username=username).exclude(id=staff.admin.id).exists():
                messages.error(request, "Username already exists. Try another username.")
                return redirect("admin_edit_staff", staff_id=staff_id)
            
            if Staffs.objects.filter(admin__first_name=first_name, middle_name=middle_name, admin__last_name=last_name).exclude(id=staff_id).exists():
                messages.error(request, "A staff member with this full name already exists. Try another name or contact the administrator for support.")
                return redirect("admin_edit_staff", staff_id=staff_id)

            # Ensure unique MCT number if provided
            if mct_number and Staffs.objects.filter(mct_number=mct_number).exclude(id=staff_id).exists():
                messages.error(request, "MCT number already exists. Provide a unique MCT number.")
                return redirect("admin_edit_staff", staff_id=staff_id)

            # Ensure staff is above 18 years
            if dob:
                dob_date = datetime.strptime(dob, "%Y-%m-%d").date()
                today = datetime.today().date()
                age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
                if age < 18:
                    messages.error(request, "Staff must be at least 18 years old.")
                    return redirect("admin_edit_staff", staff_id=staff_id)

            # Ensure joining date is not in the future
            if joining_date:
                joining_date_obj = datetime.strptime(joining_date, "%Y-%m-%d").date()
                if joining_date_obj > datetime.today().date():
                    messages.error(request, "Joining date cannot be in the future.")
                    return redirect("admin_edit_staff", staff_id=staff_id)

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
            return redirect("admin_manage_staff")

        except Exception as e:
            messages.error(request, f"Error updating staff details: {str(e)}")
            return redirect("admin_edit_staff", staff_id=staff_id)

    return redirect("admin_manage_staff")



@login_required
def medicine_list(request):
    # Retrieve medicines and check for expired ones
    medicines = Medicine.objects.all()
    # Render the template with medicine data and notifications
    return render(request, 'hod_template/manage_medicine.html', {'medicines': medicines})


@csrf_exempt
@login_required
def add_medicine(request):
    if request.method == 'POST':
        try:
            # Extract data from request
            medicine_id = request.POST.get('medicine_id')
            drug_name = request.POST.get('drug_name').strip()
            drug_type = request.POST.get('drug_type')
            dividing_unit = int(request.POST.get('dividing_unit') or 125)
            formulation_unit = request.POST.get('formulation_unit')
            manufacturer = request.POST.get('manufacturer').strip()
            quantity = request.POST.get('quantity')
            is_dividable = request.POST.get('is_dividable')
            batch_number = request.POST.get('batch_number').strip()
            expiration_date = request.POST.get('expiration_date')
            cash_cost = request.POST.get('cash_cost')
            insurance_cost = request.POST.get('insurance_cost')
            nhif_cost = request.POST.get('nhif_cost')
            buying_price = request.POST.get('buying_price')

            # Validate expiration_date
            if expiration_date:
                expiration_date_obj = datetime.strptime(expiration_date, '%Y-%m-%d').date()
                if expiration_date_obj <= datetime.now().date():
                    return JsonResponse({'success': False, 'message':  'Expiration date must be in the future.'})

             # Check if required fields are provided
            if not (drug_name and quantity and buying_price):
                return JsonResponse({'success': False, 'message': 'Missing required fields'})

            # Convert quantity and buying_price to integers .exclude(pk=disease_id)
            try:
                quantity = int(quantity)
                buying_price = float(buying_price)
            except ValueError:
                return JsonResponse({'success': False, 'message': 'Invalid quantity or buying price'})
            # Check if this is an edit operation
            if medicine_id:
                if Medicine.objects.exclude(pk=medicine_id).filter(drug_name=drug_name).exists():
                    return JsonResponse({'success': False, 'message':  'The medicine drug with the same name  already exists.'})
                if Medicine.objects.exclude(pk=medicine_id).filter(batch_number=batch_number).exists():
                    return JsonResponse({'success': False, 'message': 'The  medicine drug with the same bath number  already exists.'})
                
                medicine = Medicine.objects.get(pk=medicine_id)
                medicine.drug_name = drug_name
                medicine.drug_type = drug_type
                medicine.formulation_unit = formulation_unit
                medicine.manufacturer = manufacturer
                medicine.quantity = quantity
                medicine.dividing_unit = dividing_unit
                medicine.remain_quantity = quantity
                medicine.is_dividable = is_dividable
                medicine.batch_number = batch_number
                medicine.expiration_date = expiration_date
                medicine.cash_cost = cash_cost
                medicine.insurance_cost = insurance_cost
                medicine.nhif_cost = nhif_cost
                medicine.buying_price = buying_price
                medicine.save()
                return JsonResponse({'success': True, 'message': 'medicine drug is updated successfully'})
            else:
                # Check for uniqueness
                if Medicine.objects.filter(drug_name=drug_name).exists():
                    return JsonResponse({'success': False, 'message': 'The  medicine drug with the same name  already exists.'})
                if Medicine.objects.filter(batch_number=batch_number).exists():
                    return JsonResponse({'success': False, 'message':  'The  medicine drug with the same bath number  already exists.'})

                # Create a new Medicine instance
                medicine = Medicine(
                    drug_name=drug_name,
                    drug_type=drug_type,
                    formulation_unit=formulation_unit,
                    manufacturer=manufacturer,
                    quantity=quantity,
                    remain_quantity=quantity,
                    is_dividable=is_dividable,
                    dividing_unit=dividing_unit,
                    batch_number=batch_number,
                    expiration_date=expiration_date,
                    cash_cost=cash_cost,
                    insurance_cost=insurance_cost,
                    nhif_cost=nhif_cost,
                    buying_price=buying_price,
                )

            # Save the medicine instance
            medicine.save()
            return JsonResponse({'success': True, 'message': 'medicine drug is added successfully'})
        except ObjectDoesNotExist:
            return JsonResponse({'success': False, 'message':  'Medicine not found.'})
        except ValidationError as ve:
            return JsonResponse({'success': False, 'message':  ve.message})
        except Exception as e:
            return JsonResponse({'success': False, 'message':  str(e)})
    return JsonResponse({'success': False, 'message':  'Invalid request method'})



def medicine_expired_list(request):
    # Get all medicines
    all_medicines = Medicine.objects.all()

    # Filter medicines with less than or equal to 10 days remaining for expiration
    medicines = []
    for medicine in all_medicines:
        days_remaining = (medicine.expiration_date - timezone.now().date()).days
        if days_remaining <= 10:
            medicines.append({
                'name': medicine.name,
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
            disease_name = request.POST.get('Disease').strip()
            code = request.POST.get('Code').strip()

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
        manufacturer = request.POST.get('Manufacturer').strip()
        serial_number = request.POST.get('SerialNumber').strip()
        acquisition_date = request.POST.get('AcquisitionDate') or None
        warranty_expiry_date = request.POST.get('warrantyExpiryDate') or None
        location = request.POST.get('Location')
        description = request.POST.get('description')
        name = request.POST.get('Name').strip()

       

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

    # Step 2: Attach related prescriptions to each grouped visit
    for visit in grouped_visits:
        prescriptions = Prescription.objects.filter(visit__id=visit['visit__id']).select_related('medicine')
        visit['prescriptions'] = prescriptions

        # Optional: Derive consistent status, issued, verified if all match
        statuses = prescriptions.values_list('status', flat=True).distinct()
        issued = prescriptions.values_list('issued', flat=True).distinct()
        verified = prescriptions.values_list('verified', flat=True).distinct()

        visit['status'] = statuses[0] if len(statuses) == 1 else "Mixed"
        visit['issued'] = issued[0] if len(issued) == 1 else "Mixed"
        visit['verified'] = verified[0] if len(verified) == 1 else "Mixed"

    return render(request, 'hod_template/manage_prescription_list.html', {
        'visit_total_prices': grouped_visits,
    })



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
def medicine_routes(request):
    routes = MedicineRoute.objects.all()
    return render(request, 'hod_template/medicine_routes.html', {'routes': routes}) 

def add_medicine_route(request):
    try:
        if request.method == 'POST':
            # Get form data
            name = request.POST.get('names').strip()
            explanation = request.POST.get('explanation')
            medicine_route_id = request.POST.get('route_id')  # Check for the ID
            
            # If ID is provided, check if it's an existing medicine route
            if medicine_route_id:
                if MedicineRoute.objects.filter(name=name).exclude(id=medicine_route_id).exists():
                    return JsonResponse({'success': False, 'message': 'Medicine route with this name already exists'})
                try:
                    medicine_route = MedicineRoute.objects.get(pk=medicine_route_id)
                    # Update existing medicine route
                    medicine_route.name = name
                    medicine_route.explanation = explanation
                    medicine_route.save()
                    return JsonResponse({'success': True, 'message': 'Medicine route updated successfully'})
                except MedicineRoute.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Medicine route does not exist'})
            else:
                # Check if the name already exists
                if MedicineRoute.objects.filter(name=name).exists():
                    return JsonResponse({'success': False, 'message': 'Medicine route with this name already exists'})
                
                # Create new MedicineRoute
                MedicineRoute.objects.create(name=name, explanation=explanation)
                return JsonResponse({'success': True, 'message': 'Medicine route added successfully'})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid request method'})
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
def add_medicine_unit_measure(request):
    try:
        # Get form data
        name = request.POST.get('name')
        short_name = request.POST.get('short_name')
        application_user = request.POST.get('application_user')
        
        if not name or not short_name or not application_user:
            return JsonResponse({'success': False, 'message': 'All fields are required'})

        # Check if the medicine unit measure ID is provided (for editing existing record)
        unit_measure_id = request.POST.get('unit_measure_id')

        if unit_measure_id:
            # Get the existing medicine unit measure instance
            unit_measure = get_object_or_404(MedicineUnitMeasure, pk=unit_measure_id)
            
            # Check if the name or short_name already exists for another instance
            if MedicineUnitMeasure.objects.filter(name=name).exclude(pk=unit_measure_id).exists():
                return JsonResponse({'success': False, 'message': 'Medicine unit measure with this name already exists'})
            if MedicineUnitMeasure.objects.filter(short_name=short_name).exclude(pk=unit_measure_id).exists():
                return JsonResponse({'success': False, 'message': 'Medicine unit measure with this short name already exists'})
            
            # Update the existing instance
            unit_measure.name = name
            unit_measure.short_name = short_name
            unit_measure.application_user = application_user
            unit_measure.save()
            return JsonResponse({'success': True, 'message': 'Medicine unit measure updated successfully'})
        else:
            # Check if the name or short_name already exists
            if MedicineUnitMeasure.objects.filter(name=name).exists():
                return JsonResponse({'success': False, 'message': 'Medicine unit measure with this name already exists'})
            if MedicineUnitMeasure.objects.filter(short_name=short_name).exists():
                return JsonResponse({'success': False, 'message': 'Medicine unit measure with this short name already exists'})
            
            # Create new MedicineUnitMeasure
            MedicineUnitMeasure.objects.create(name=name, short_name=short_name, application_user=application_user)
            return JsonResponse({'success': True, 'message': 'Medicine unit measure added successfully'})

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}) 
    

      
   
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
        LaboratoryOrder.objects.select_related('patient', 'visit', 'data_recorder', 'name'),
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
        'name', 'data_recorder'
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
    lab_tests = LaboratoryOrder.objects.filter(patient=patient, visit=visit).select_related('name', 'data_recorder')

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