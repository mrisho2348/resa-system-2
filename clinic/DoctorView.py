import calendar
from datetime import  date, datetime, timedelta
import json
from django.utils import timezone
import logging
from django.urls import reverse
from django.db.models import F
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404, JsonResponse
from django.db.models import Sum, Max, Count
from django.db.models import OuterRef, Subquery
from django.db import transaction
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from clinic.forms import CounselingForm, DischargesNotesForm, ImagingRecordForm, LaboratoryOrderForm, ObservationRecordForm, ProcedureForm, ReferralForm, StaffProfileForm
from django.core.exceptions import ValidationError
from clinic.models import  Consultation,   Medicine,   Staffs
from django.views.decorators.http import require_POST, require_GET
from .models import ClinicChiefComplaint,   ConsultationNotes,  ConsultationOrder, Counseling, Country, CustomUser, Diagnosis, DischargesNotes, Employee, EmployeeDeduction, HealthRecord, ImagingRecord,  LaboratoryOrder, MedicineDosage, MedicineRoute, ObservationRecord, Order, PatientDiagnosisRecord, PatientVisits, PatientVital, Prescription, PrescriptionFrequency, Procedure, Patients,  Referral, SalaryChangeRecord,Service
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import logout
from django.utils.decorators import method_decorator
from django.views import View

@login_required
def doctor_dashboard(request):
    try:
        today = date.today()
       
        total_patients_count = Patients.objects.count()

        # Today's Visits
        today_visits = PatientVisits.objects.filter(updated_at__date=today)
        today_total_patients = today_visits.count()

        # Today's Consultations
        today_notes = ConsultationNotes.objects.filter(updated_at__date=today)
        completed_notes = today_notes.filter(doctor_plan__in=["Discharge", "Referral"])
        in_progress_notes = today_notes.exclude(doctor_plan__in=["Discharge", "Referral"])
        today_completed_patients = completed_notes.values('patient').distinct().count()
        today_in_progress_patients = in_progress_notes.values('patient').distinct().count()

        # Lab Orders
        today_lab_orders = LaboratoryOrder.objects.filter(created_at__date=today)
        today_lab_patients_count = today_lab_orders.values('patient').distinct().count()
        in_progress_lab_patients_count = today_lab_orders.filter(Q(result__isnull=True) | Q(result__exact='')).values('patient').distinct().count()
        completed_lab_patients_count = today_lab_patients_count - in_progress_lab_patients_count if today_lab_patients_count else 0

        # Prescriptions
        today_prescriptions = Prescription.objects.filter(created_at__date=today)
        today_today_prescription_count = today_prescriptions.values('patient').distinct().count()

        # Procedures
        today_procedures = Procedure.objects.filter(created_at__date=today)
        today_procedure_patients_count = today_procedures.values('patient').distinct().count()
        in_progress_procedure_patients_count = today_procedures.filter(Q(result__isnull=True) | Q(result__exact='')).values('patient').distinct().count()
        completed_procedure_patients_count = today_procedure_patients_count - in_progress_procedure_patients_count if today_procedure_patients_count else 0

        # Imaging
        today_imagings = ImagingRecord.objects.filter(created_at__date=today)
        today_imaging_patients_count = today_imagings.values('patient').distinct().count()
        in_progress_imaging_patients_count = today_imagings.filter(Q(result__isnull=True) | Q(result__exact='')).values('patient').distinct().count()
        completed_imaging_patients_count = today_imaging_patients_count - in_progress_imaging_patients_count if today_imaging_patients_count else 0

        # Recent consultations (last 10)
        recent_consultations = ConsultationNotes.objects.select_related('patient').order_by('-created_at')[:10]

        # Upcoming appointments (next 7 days)
        upcoming_appointments = Consultation.objects.filter(
            appointment_date__gte=today,
            appointment_date__lte=today + timedelta(days=7)
        ).select_related('patient').order_by('appointment_date')[:10]

        context = {
            # General
            'total_patients_count': total_patients_count,
            'today_total_patients': today_total_patients,

            # Consultations
            'today_in_progress_patients': today_in_progress_patients,
            'today_completed_patients': today_completed_patients,

            # Lab Orders
            'today_lab_orders': today_lab_patients_count,
            'in_progress_lab_orders': in_progress_lab_patients_count,
            'completed_lab_orders': completed_lab_patients_count,

            # Prescriptions
            'today_today_prescription_count': today_today_prescription_count,

            # Procedures
            'today_procedure_patients': today_procedure_patients_count,
            'in_progress_procedures': in_progress_procedure_patients_count,
            'completed_procedures': completed_procedure_patients_count,

            # Imaging
            'today_imaging_patients': today_imaging_patients_count,
            'in_progress_imagings': in_progress_imaging_patients_count,
            'completed_imagings': completed_imaging_patients_count,

            # Additional data for the premium dashboard
            'recent_consultations': recent_consultations,
            'upcoming_appointments': upcoming_appointments,
        }

    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        context = {
            'total_patients_count': 0,
            'today_total_patients': 0,
            'today_in_progress_patients': 0,
            'today_completed_patients': 0,
            'today_lab_orders': 0,
            'in_progress_lab_orders': 0,
            'completed_lab_orders': 0,
            'today_today_prescription_count': 0,
            'today_procedure_patients': 0,
            'in_progress_procedures': 0,
            'completed_procedures': 0,
            'today_imaging_patients': 0,
            'in_progress_imagings': 0,
            'completed_imagings': 0,
            'recent_consultations': [],
            'upcoming_appointments': [],
        }

    return render(request, "doctor_template/home_content.html", context)


@login_required
@require_GET
def doctor_fetch_lab_stats(request):
    """
    View to fetch comprehensive laboratory statistics for the currently logged-in doctor.
    Returns JSON with various lab order metrics.
    """
    try:
        # Get the current doctor/staff member
        doctor = request.user.staff
        
        # Calculate date ranges
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Base queryset for this doctor
        doctor_orders = LaboratoryOrder.objects.filter(doctor=doctor)
        
        # Count lab orders by status
        stats = {
            # Basic counts
            'pending_count': doctor_orders.filter(result__isnull=True).count(),
            'completed_count': doctor_orders.filter(result__isnull=False).count(),
            'total_count': doctor_orders.count(),
            
            # Time-based counts
            'today_count': doctor_orders.filter(created_at__date=today).count(),
            'week_count': doctor_orders.filter(created_at__date__gte=week_ago).count(),
            'month_count': doctor_orders.filter(created_at__date__gte=month_ago).count(),
            
            # Financial metrics
            'total_revenue': float(doctor_orders.aggregate(Sum('cost'))['cost__sum'] or 0),
            'pending_revenue': float(doctor_orders.filter(result__isnull=True).aggregate(Sum('cost'))['cost__sum'] or 0),
            'completed_revenue': float(doctor_orders.filter(result__isnull=False).aggregate(Sum('cost'))['cost__sum'] or 0),
            
            # Recent pending orders (for notifications)
            'recent_pending': list(doctor_orders.filter(
                result__isnull=True
            ).order_by('-created_at')[:5].values(
                'id', 'patient__first_name', 'patient__last_name', 
                'patient__mrn', 'lab_test__name', 'created_at'
            )),
            
            # Most ordered tests
            'popular_tests': list(doctor_orders.values(
                'lab_test__name'
            ).annotate(
                count=Count('id')
            ).order_by('-count')[:5])
        }
        
        return JsonResponse(stats)
        
    except Exception as e:
        # Return safe default values in case of error
        return JsonResponse({
            'error': str(e),
            'pending_count': 0,
            'completed_count': 0,
            'total_count': 0,
            'today_count': 0,
            'week_count': 0,
            'month_count': 0,
            'total_revenue': 0,
            'pending_revenue': 0,
            'completed_revenue': 0,
            'recent_pending': [],
            'popular_tests': []
        }, status=500)

@login_required
def doctor_today_patients(request):
    today = date.today()
    doctor = request.user.staff  # Assuming the user is linked to Staffs model
    
    # Get today's patients for this doctor
    today_patients = Patients.objects.filter(
        Q(consultation__doctor=doctor, consultation__appointment_date=today) |
        Q(consultationnotes__doctor=doctor, consultationnotes__created_at__date=today) |
        Q(imagingrecord__doctor=doctor, imagingrecord__order_date=today) |
        Q(procedure__doctor=doctor, procedure__order_date=today) |
        Q(laboratoryorder__doctor=doctor, laboratoryorder__order_date=today)
    ).distinct()
    
    context = {
        'patients': today_patients,
        'page_title': "Today's Patients"
    }
    return render(request, 'doctor_template/today_patients.html', context)

@login_required
def doctor_in_progress_consultations(request):
    doctor = request.user.staff
    
    # Get in-progress consultations for this doctor
    in_progress_consultations = ConsultationNotes.objects.filter(
        doctor=doctor
    ).exclude(
        Q(doctor_plan__in=["Discharge", "Referral"])
    ).order_by('-created_at')
    
    context = {
        'consultations': in_progress_consultations,
        'page_title': "In Progress Consultations"
    }
    return render(request, 'doctor_template/in_progress_consultations.html', context)

@login_required
def doctor_completed_consultations(request):
    doctor = request.user.staff
    today = date.today()
    
    # Get completed consultations for today for this doctor
    completed_consultations = ConsultationNotes.objects.filter(
        doctor=doctor,
        created_at__date=today,
        doctor_plan__in=["Discharge", "Referral"]
    ).order_by('-created_at')
    
    context = {
        'consultations': completed_consultations,
        'page_title': "Completed Consultations"
    }
    return render(request, 'doctor_template/completed_consultations.html', context)

@login_required
def doctor_today_lab_orders(request):
    doctor = request.user.staff
    today = date.today()
    
    # Get today's lab orders for this doctor
    today_lab_orders = LaboratoryOrder.objects.filter(
        doctor=doctor,
        order_date=today
    ).order_by('-created_at')
    
    context = {
        'lab_orders': today_lab_orders,
        'page_title': "Today's Lab Orders"
    }
    return render(request, 'doctor_template/today_lab_orders.html', context)

@login_required
def doctor_today_imaging_orders(request):
    doctor = request.user.staff
    today = date.today()
    
    # Get today's imaging orders for this doctor
    today_imaging_orders = ImagingRecord.objects.filter(
        doctor=doctor,
        order_date=today
    ).order_by('-created_at')
    
    context = {
        'imaging_orders': today_imaging_orders,
        'page_title': "Today's Imaging Orders"
    }
    return render(request, 'doctor_template/today_imaging_orders.html', context)

@login_required
def doctor_pending_imaging(request):
    doctor = request.user.staff
    
    # Get pending imaging results for this doctor
    pending_imaging = ImagingRecord.objects.filter(
        doctor=doctor
    ).filter(
        Q(result__isnull=True) | Q(result__exact='')
    ).order_by('-created_at')
    
    context = {
        'imaging_records': pending_imaging,
        'page_title': "Pending Imaging Results"
    }
    return render(request, 'doctor_template/pending_imaging.html', context)

@login_required
def doctor_completed_imaging(request):
    doctor = request.user.staff
    
    # Get completed imaging for this doctor
    completed_imaging = ImagingRecord.objects.filter(
        doctor=doctor
    ).exclude(
        Q(result__isnull=True) | Q(result__exact='')
    ).order_by('-created_at')
    
    context = {
        'imaging_records': completed_imaging,
        'page_title': "Completed Imaging"
    }
    return render(request, 'doctor_template/completed_imaging.html', context)

@login_required
def doctor_today_procedures(request):
    doctor = request.user.staff
    today = date.today()
    
    # Get today's procedures for this doctor
    today_procedures = Procedure.objects.filter(
        doctor=doctor,
        order_date=today
    ).order_by('-created_at')
    
    context = {
        'procedures': today_procedures,
        'page_title': "Today's Procedures"
    }
    return render(request, 'doctor_template/today_procedures.html', context)

@login_required
def doctor_pending_procedures(request):
    doctor = request.user.staff
    
    # Get pending procedures for this doctor
    pending_procedures = Procedure.objects.filter(
        doctor=doctor
    ).filter(
        Q(result__isnull=True) | Q(result__exact='')
    ).order_by('-created_at')
    
    context = {
        'procedures': pending_procedures,
        'page_title': "Pending Procedures"
    }
    return render(request, 'doctor_template/pending_procedures.html', context)

@login_required
def doctor_completed_procedures(request):
    doctor = request.user.staff
    
    # Get completed procedures for this doctor
    completed_procedures = Procedure.objects.filter(
        doctor=doctor
    ).exclude(
        Q(result__isnull=True) | Q(result__exact='')
    ).order_by('-created_at')
    
    context = {
        'procedures': completed_procedures,
        'page_title': "Completed Procedures"
    }
    return render(request, 'doctor_template/completed_procedures.html', context)

@login_required
def doctor_consultation_list(request):
    doctor = request.user.staff
    
    # Get all consultations for this doctor
    consultations = ConsultationNotes.objects.filter(
        doctor=doctor
    ).order_by('-created_at')
    
    context = {
        'consultations': consultations,
        'page_title': "All Consultations"
    }
    return render(request, 'doctor_template/consultation_list.html', context)


def dashboard_stats_api(request):
    """
    API endpoint to fetch statistics for the doctor dashboard
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        # Get today's date
        today = timezone.now().date()
        
        # Count today's appointments
        today_appointments = Consultation.objects.filter(
            doctor=request.user.doctor if hasattr(request.user, 'doctor') else None,
            appointment_date__date=today,
            status__in=['Scheduled', 'Confirmed']
        ).count()
        
        # Count pending consultations
        pending_consultations = ConsultationOrder.objects.filter(
            doctor=request.user.doctor if hasattr(request.user, 'doctor') else None,
            order_status='pending'
        ).count()
        
        # Count total patients (optional)
        total_patients = Patients.objects.filter(
            doctor=request.user.doctor if hasattr(request.user, 'doctor') else None
        ).count()
        
        # Count upcoming appointments in next 7 days
        seven_days_later = today + timedelta(days=7)
        upcoming_appointments = Consultation.objects.filter(
            doctor=request.user.doctor if hasattr(request.user, 'doctor') else None,
            appointment_date__date__range=[today, seven_days_later],
            status__in=['Scheduled', 'Confirmed']
        ).count()
        
        return JsonResponse({
            'today_appointments': today_appointments,
            'pending_consultations': pending_consultations,
            'total_patients': total_patients,
            'upcoming_appointments': upcoming_appointments,
            'status': 'success'
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)


@login_required
def doctor_profile(request):
    # Get the currently logged-in user
    user = request.user
    
    try:
        # Fetch the doctor's details from the Staffs model (assuming the doctor is a staff member)
        staff = Staffs.objects.get(admin=user, role='doctor')
        
        # Pass the doctor details to the template
        return render(request, 'doctor_template/profile.html', {'staff': staff})

    except Staffs.DoesNotExist:
        # Handle case if no staff member with the role 'doctor' is found
        return render(request, 'doctor_template/profile.html', {'error': 'Doctor not found.'})

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

    return render(request, 'doctor_template/change_password.html', {'form': form})          

@method_decorator(login_required, name='dispatch')
class EditStaffProfileView(View):
    template_name = 'doctor_template/edit_profile.html'

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
            return redirect('doctor_edit_staff_profile', pk=staff.id)


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
    range_121 = range(1, 121)
    all_country = Country.objects.all()
    doctors=Staffs.objects.filter(role='doctor')
    return render(request,"doctor_template/manage_patients.html", {
        "patients":patient_records,
        "range_121":range_121,
        "doctors":doctors,
        "all_country":all_country,
        })
    


@login_required
def manage_consultation(request):
    patients=Patients.objects.all()
    doctors=Staffs.objects.filter(role='doctor')
    context = {
        'patients':patients,   
        'doctors':doctors,
    }
    return render(request,"doctor_template/manage_consultation.html",context)

    
@login_required
def manage_laboratory(request):
    doctor = request.user.staff
    lab_records=LaboratoryOrder.objects.filter(doctor=doctor)  
    orders = Order.objects.filter(order_type__in=[lab_record.imaging.name for lab_record in lab_records], is_read=True)          
    return render(request,"doctor_template/manage_lab_result.html",{
        "orders":orders,       
        "lab_records":lab_records,       
        })


logger = logging.getLogger(__name__)


    
@csrf_exempt
def appointment_view_remote(request, patient_id):
    try:
        if request.method == 'POST':
            # Extract data from the request
            doctor_id = request.POST.get('doctor')
            date_of_consultation = request.POST.get('date_of_consultation')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            description = request.POST.get('description')

            # Check if all required fields are present
            if not (doctor_id and date_of_consultation and start_time and end_time):
                return JsonResponse({'status': 'error', 'message': 'Missing required fields'})

            # Retrieve doctor and patient instances
            doctor = get_object_or_404(Staffs, id=doctor_id)
            patient = get_object_or_404(Patients, id=patient_id)

            # Create a Consultation instance
            consultation = Consultation(
                doctor=doctor,
                patient=patient,
                appointment_date=date_of_consultation,
                start_time=start_time,
                end_time=end_time,
                description=description
            )
            consultation.save()
            messages.success(request, "Appointment created successfully.")
            return JsonResponse({'status': 'success'})
       
    except IntegrityError as e:
        # Handle integrity error (e.g., duplicate entry)
        messages.error(request, f"Error creating appointment: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)})
    except Exception as e:
        # Handle other exceptions
        messages.error(request, f"An unexpected error occurred: {str(e)}")
        return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred'})

    # Handle invalid request method
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})





def confirm_meeting(request, appointment_id):
    try:
        # Retrieve the appointment
        appointment = get_object_or_404(Consultation, id=appointment_id)

        if request.method == 'POST':
            # Get the selected status from the form
            selected_status = int(request.POST.get('status'))

            # Check if the appointment is not already confirmed
            if not appointment.status:
                # Perform the confirmation action (e.g., set status to selected status)
                appointment.status = selected_status
                appointment.save()
                
            elif appointment.status:
                # Perform the confirmation action (e.g., set status to selected status)
                appointment.status = selected_status
                appointment.save()

                # Add a success message
                messages.success(request, f"Meeting with {appointment.patient.mrn} confirmed.")
            else:
                messages.warning(request, f"Meeting with {appointment.patient.mrn} is already confirmed.")
        else:
            messages.warning(request, "Invalid request method for confirming meeting.")

    except IntegrityError as e:
        # Handle IntegrityError (e.g., database constraint violation)
        messages.error(request, f"Error confirming meeting: {str(e)}")

    return redirect('doctor_read_appointments')  # Adjust the URL name based on your actual URL structure

def edit_meeting(request, appointment_id):
    try:
        if request.method == 'POST':
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')

            appointment = get_object_or_404(Consultation, id=appointment_id)

            # Perform the edit action (e.g., update start time and end time)
            appointment.start_time = start_time
            appointment.end_time = end_time
            appointment.save()

            messages.success(request, f"Meeting time for {appointment.patient} edited successfully.")
    except Exception as e:
        messages.error(request, f"Error editing meeting time: {str(e)}")

    return redirect('doctor_read_appointments')

@login_required
def patient_procedure_history_view(request, mrn):
    patient = get_object_or_404(Patients, mrn=mrn)    
    # Retrieve all procedures for the specific patient
    procedures = Procedure.objects.filter(patient=patient)
    
    context = {
        'patient': patient,
        'procedures': procedures,
    }

    return render(request, 'doctor_template/manage_patient_procedure.html', context)


def save_procedure(request):
    if request.method == 'POST':
        procedure_id = request.POST.get('procedure_id')
        procedure = get_object_or_404(Procedure, id=procedure_id)
        form = ProcedureForm(request.POST, instance=procedure)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Procedure updated successfully.'})
        else:
            return JsonResponse({'success': False, 'message': 'Form is not valid.'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


@csrf_exempt
def save_radiology(request):
    if request.method == 'POST':
        try:
            # Extract data from the POST request
            radiology_id = request.POST.get('radiology_id')
            result = request.POST.get('result')         
            doctor = request.user.staff

            # Check if the radiology_record ID is provided
            if radiology_id:
                # Retrieve the procedure record if it exists
                try:
                    radiology_record = ImagingRecord.objects.get(id=radiology_id)
                except Procedure.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'The provided radiology ID is invalid.'})                

                # Update the radiology_record record with the new data
                radiology_record.result = result
                radiology_record.doctor = doctor              

                # Save the updated radiology_record record
                radiology_record.save()

                return JsonResponse({'success': True, 'message': f'The radiology record for "{radiology_record.imaging.name}" has been updated successfully.'})
        
        except Patients.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'The provided patient ID is invalid.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {e}'})

    return JsonResponse({'success': False, 'message': 'Invalid request method. This endpoint only accepts POST requests.'})



@csrf_exempt
def change_referral_status(request):
    if request.method == 'POST':
        try:
            referral_id = request.POST.get('referralId')
            new_status = request.POST.get('newStatus')
            
            # Update referral record with new status
            referral_record = Referral.objects.get(id=referral_id)
            referral_record.status = new_status
            referral_record.save()

            return JsonResponse({'success': True, 'message': f'Status for {referral_record} changed successfully.'})
        except Referral.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid Referral ID.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {e}'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

@login_required
def manage_referral(request):
    referrals = Referral.objects.all()
    patients = Patients.objects.all()
    return render(request, 'doctor_template/manage_referral.html', {'referrals': referrals,'patients':patients})


def appointment_list_view(request):
    """
    View for displaying all appointments assigned to the current doctor
    """
    # Get the current doctor (staff member)
    doctor = get_object_or_404(Staffs, admin=request.user)
    
    # Get all appointments for this doctor
    appointments = Consultation.objects.filter(doctor=doctor).order_by('-appointment_date', '-created_at')
    
    # Get counts for different statuses
    status_counts = {
        'total': appointments.count(),
        'pending': appointments.filter(status=0).count(),
        'completed': appointments.filter(status=1).count(),
        'canceled': appointments.filter(status=2).count(),
        'rescheduled': appointments.filter(status=3).count(),
        'noshow': appointments.filter(status=4).count(),
        'in_progress': appointments.filter(status=5).count(),
        'confirmed': appointments.filter(status=6).count(),
        'arrived': appointments.filter(status=7).count(),
    }
    
    context = {
        'appointments': appointments,
        'status_counts': status_counts,
    }
    
    return render(request, 'doctor_template/manage_appointment.html', context)

@require_POST
def edit_meeting(request, appointment_id):
    """
    View for editing/rescheduling an appointment
    """
    appointment = get_object_or_404(Consultation, id=appointment_id, doctor__admin=request.user)
    
    if request.method == 'POST':
        try:
            # Update appointment details
            appointment.appointment_date = request.POST.get('appointment_date')
            appointment.start_time = request.POST.get('start_time')
            appointment.end_time = request.POST.get('end_time')
            appointment.save()
            
            messages.success(request, 'Appointment rescheduled successfully.')
        except Exception as e:
            messages.error(request, f'Error rescheduling appointment: {str(e)}')
    
    return redirect('doctor_appointment_list')

@require_POST
def confirm_meeting(request, appointment_id):
    """
    View for confirming an appointment status
    """
    appointment = get_object_or_404(Consultation, id=appointment_id, doctor__admin=request.user)
    
    if request.method == 'POST':
        try:
            new_status = int(request.POST.get('status'))
            appointment.status = new_status
            appointment.save()
            
            status_name = dict(Consultation.STATUS_CHOICES).get(new_status, 'Unknown')
            messages.success(request, f'Appointment status updated to {status_name}.')
        except (ValueError, Exception) as e:
            messages.error(request, f'Error updating appointment status: {str(e)}')
    
    return redirect('doctor_appointment_list')

@require_POST
def start_consultation(request, appointment_id):
    """
    Starts a consultation: ensures a PatientVisits exists for this appointment,
    then redirects to save remote consultation notes.
    """
    # Fetch appointment; ensure user has permission (doctor/admin)
    appointment = get_object_or_404(Consultation, id=appointment_id, doctor__admin=request.user)

    try:
        # Check if a visit already exists for this appointment
        if appointment.visit:
            visit = appointment.visit
        else:
            # Create a new PatientVisits record
            visit = PatientVisits.objects.create(
                patient=appointment.patient,
                data_recorder=request.user,  # if you want to track who started it
                visit_type='Normal',         # or some default type
                primary_service='Consultation'  # adjust as needed
            )
            appointment.visit = visit
            appointment.save()

        # Redirect to the remote notes saving URL
        return redirect('doctor_save_remotesconsultation_notes', patient_id=appointment.patient.id, visit_id=visit.id)

    except Exception as e:
        messages.error(request, f'Error starting consultation: {str(e)}')
        return redirect('doctor_appointment_list')

        
@require_POST
def complete_consultation(request, appointment_id):
    """
    View for completing a consultation
    """
    appointment = get_object_or_404(Consultation, id=appointment_id, doctor__admin=request.user)
    
    if request.method == 'POST':
        try:
            # Update status to Completed
            appointment.status = 1  # Completed
            final_notes = request.POST.get('final_notes', '')
            prescription = request.POST.get('prescription', '')
            
            # Update the patient visit record
            if appointment.visit:
                appointment.visit.status = 'completed'
                appointment.visit.notes = final_notes
                appointment.visit.prescription = prescription
                appointment.visit.save()
            
            appointment.save()
            
            messages.success(request, 'Consultation completed successfully.')
        except Exception as e:
            messages.error(request, f'Error completing consultation: {str(e)}')
    
    return redirect('doctor_appointment_list')

@require_POST
def cancel_appointment(request, appointment_id):
    """
    View for canceling an appointment
    """
    appointment = get_object_or_404(Consultation, id=appointment_id, doctor__admin=request.user)
    
    if request.method == 'POST':
        try:
            # Update status to Canceled
            appointment.status = 2  # Canceled
            cancel_reason = request.POST.get('cancel_reason', '')
            
            # Store cancellation reason in description
            if cancel_reason:
                original_desc = appointment.description or ''
                appointment.description = f"{original_desc}\n\nCANCELLATION REASON: {cancel_reason}"
            
            appointment.save()
            
            messages.success(request, 'Appointment canceled successfully.')
        except Exception as e:
            messages.error(request, f'Error canceling appointment: {str(e)}')
    
    return redirect('doctor_appointment_list')

def get_appointment_details(request, appointment_id):
    """
    API view to get appointment details (for AJAX requests)
    """
    appointment = get_object_or_404(Consultation, id=appointment_id, doctor__admin=request.user)
    
    data = {
        'id': appointment.id,
        'appointment_number': appointment.appointment_number,
        'patient_name': f"{appointment.patient.first_name} {appointment.patient.last_name}",
        'patient_mrn': appointment.patient.mrn,
        'appointment_date': appointment.appointment_date.strftime('%d-%m-%Y'),
        'start_time': appointment.start_time.strftime('%H:%M') if appointment.start_time else '',
        'end_time': appointment.end_time.strftime('%H:%M') if appointment.end_time else '',
        'description': appointment.description or 'No description provided',
        'status': appointment.status,
        'status_display': appointment.get_status_display(),
        'created_at': appointment.created_at.strftime('%d-%m-%Y %H:%M'),
    }
    
    return JsonResponse(data)

@require_POST
def bulk_update_appointments(request):
    """
    View for bulk updating appointment statuses
    """
    if request.method == 'POST':
        try:
            appointment_ids = request.POST.getlist('appointment_ids')
            new_status = int(request.POST.get('status'))
            
            # Update all selected appointments
            updated_count = Consultation.objects.filter(
                id__in=appointment_ids, 
                doctor__admin=request.user
            ).update(status=new_status)
            
            status_name = dict(Consultation.STATUS_CHOICES).get(new_status, 'Unknown')
            messages.success(request, f'Updated {updated_count} appointments to {status_name}.')
        except (ValueError, Exception) as e:
            messages.error(request, f'Error updating appointments: {str(e)}')
    
    return redirect('doctor_appointment_dashboard') 




@login_required
def fetch_consultation_counts(request):
    try:
        # Get the currently logged-in doctor staff
        doctor = request.user.staff  # Assuming user has a profile linked with Staffs model

        # Get today's date
        today = timezone.now().date()

        # Get the counts of consultations for today and not today for the current doctor
        today_count = Consultation.objects.filter(doctor=doctor, created_at__date=today).count()
        not_today_count = Consultation.objects.filter(doctor=doctor).exclude(created_at__date=today).count()

        # Return the counts as JSON response
        return JsonResponse({'unreadCount': today_count, 'readCount': not_today_count})
    
    except Staffs.DoesNotExist:
        return JsonResponse({'error': "Doctor not found."}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
  

@csrf_exempt
def save_chief_complaint(request):
    try:
        # Ensure the request method is POST
        if request.method == 'POST':
            # Extract data from the POST request
            patient_id = request.POST.get('patient_id')
            visit_id = request.POST.get('visit_id')
            health_record_id = request.POST.get('chief_complain_name')
            other_chief_complaint = request.POST.get('other_complaint')          
            if request.POST.get('chief_complain_duration'):
                duration = request.POST.get('chief_complain_duration')  
            else:
                duration = request.POST.get('other_complain_duration')       

            # Create a new ChiefComplaint object
            chief_complaint = ClinicChiefComplaint(
                duration=duration,
                patient_id=patient_id,
                visit_id=visit_id
            )

            # Set the appropriate fields based on the provided data
            if health_record_id == "other":
                # Check if a ChiefComplaint with the same other_complaint already exists for the given visit_id
                if ClinicChiefComplaint.objects.filter(visit_id=visit_id, other_complaint=other_chief_complaint).exists():
                    return JsonResponse({'status': False, 'message': 'A Other ChiefComplaint with the same name already exists for this patient'})
                chief_complaint.other_complaint = other_chief_complaint
            else:
                # Check if a ChiefComplaint with the same health_record_id already exists for the given visit_id
                if ClinicChiefComplaint.objects.filter(health_record_id=health_record_id, visit_id=visit_id).exists():
                    return JsonResponse({'status': False, 'message': 'A ChiefComplaint with the same name  already exists for this patient'})
                chief_complaint.health_record_id = health_record_id          

            chief_complaint.data_recorder = request.user.staff  
            # Save the ChiefComplaint object
            chief_complaint.save()

            # Initialize health_record_data to None
            health_record_data = None

            # Serialize the HealthRecord object if applicable
            if health_record_id and health_record_id != "other":
                health_record = HealthRecord.objects.get(pk=health_record_id)
                # Extract the name of the health record
                health_record_data = {'name': health_record.name}
            
            # Return the saved data as a JSON response
            response_data = {
                'status': True,
                'id': chief_complaint.id,
                'health_record': health_record_data,
                'duration': chief_complaint.duration,
            }

            # Include other_complaint in the response data if present
            if other_chief_complaint:
                response_data['other_complaint'] = other_chief_complaint

            return JsonResponse(response_data)

        # If request method is not POST, return an error response
        return JsonResponse({'status': False, 'message': 'Invalid request method'})
    except Exception as e:
        # Catch any exceptions and return an error response
        return JsonResponse({'status': False, 'message': str(e)})
    
def update_chief_complaint(request, chief_complaint_id):
    if request.method == 'POST':
        try:
            # Fetch the complaint record
            chief_complaint = get_object_or_404(ClinicChiefComplaint, id=chief_complaint_id)
            
            # Parse the JSON data from the request body
            data = json.loads(request.body)            
            chief_complain_duration = data.get('chief_complain_duration')
            other_complaint = data.get('other_complaint')           

            if chief_complain_duration:
                chief_complaint.duration = chief_complain_duration
            if other_complaint:
                chief_complaint.other_complaint = other_complaint

            # Save the updated record
            chief_complaint.save()

            # Return a success response
            return JsonResponse({'status': True, 'message': 'Chief complaint updated successfully.'})
        
        except ClinicChiefComplaint.DoesNotExist:
            # Handle the case where the chief complaint record does not exist
            return JsonResponse({'status': False, 'message': 'Chief complaint not found.'})
        
        except ValueError as e:
            # Handle invalid data errors
            return JsonResponse({'status': False, 'message': f'Invalid data: {str(e)}'})
        
        except Exception as e:
            # Handle any other unexpected errors
            return JsonResponse({'status': False, 'message': f'An unexpected error occurred: {str(e)}'})

    # If not a POST request, return a method not allowed response
    return JsonResponse({'status': False, 'message': 'Invalid request method.'})
  

def fetch_existing_data(request):
    try:
        # Extract patient_id and visit_id from the request parameters
        patient_id = request.GET.get('patient_id')
        visit_id = request.GET.get('visit_id')

        # Query the database to fetch existing chief complaints based on patient_id and visit_id
        existing_data = ClinicChiefComplaint.objects.filter(patient_id=patient_id, visit_id=visit_id).values()
        
        # Create a list to hold the modified data with unified information
        modified_data = []

        # Iterate through each entry in the existing data
        for entry in existing_data:
            # Determine the information to display based on whether the health record is null or not
            display_info = None
            if entry['health_record_id'] is not None:
                try:
                    health_record = HealthRecord.objects.get(pk=entry['health_record_id'])
                    display_info = health_record.name
                except ObjectDoesNotExist:
                    # Handle the case where the HealthRecord object does not exist
                    display_info = "Unknown Health Record"
            else:
                # Use the "other complaint" field if health record is null
                display_info = entry['other_complaint'] if entry['other_complaint'] else "Unknown"
 
            # Create a modified entry with unified information under the 'health_record' key Staff.objects.get(admin=request.user.staff)
            admin = CustomUser.objects.get(id=request.user.id)
            staff = Staffs.objects.get(admin=admin)  # Tumia object ya `admin` moja kwa moja
         
            modified_entry = {
                'id': entry['id'],
                'patient_id': entry['patient_id'],
                'visit_id': entry['visit_id'],
                'data_recorder_id': entry['data_recorder_id'],
                'staff_id':staff.id,
                'health_record': display_info,
                'health_record_id': health_record.id,
                'duration': entry['duration'],
                'created_at': entry['created_at'],
                'updated_at': entry['updated_at']
            }

            # Add the modified entry to the list
            modified_data.append(modified_entry)

        # Return the modified data as a JSON response
        return JsonResponse(modified_data, safe=False)
    
    except Exception as e:
        # If an error occurs, return an error response with status code 500
        return JsonResponse({'error': str(e)}, status=500)
    

@csrf_exempt
def delete_chief_complaint(request, chief_complaint_id):
    try:
        if request.method == 'POST' and request.POST.get('_method') == 'DELETE':
            # Fetch the ChiefComplaint object to delete
            chief_complaint = get_object_or_404(ClinicChiefComplaint, id=chief_complaint_id)
            
            # Delete the ChiefComplaint
            chief_complaint.delete()
            
            # Return a success response
            return JsonResponse({'message': 'Chief complaint deleted successfully'})
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    except Exception as e:
        # Return detailed error message for client-side display
        return JsonResponse({'error': f"Error: {str(e)}"}, status=500)

    
@login_required
def save_remotesconsultation_notes(request, patient_id, visit_id):
    import numpy as np
    doctor = request.user.staff
    patient = get_object_or_404(Patients, pk=patient_id)
    visit = get_object_or_404(PatientVisits, patient=patient, id=visit_id)
    patient_visits = PatientVisits.objects.filter(patient=patient)
    
    # Retrieve patient vitals and health records
    try:
        patient_vitals = PatientVital.objects.filter(patient=patient, visit=visit)
        health_records = HealthRecord.objects.all()
    except Exception:
        patient_vitals = None
        health_records = None

    # Get existing consultation note or None
    consultation_note = ConsultationNotes.objects.filter(patient=patient, visit=visit).first()
    previous_referrals = Referral.objects.filter(patient=patient_id, visit=visit)
    # Get or create provisional diagnosis record
    provisional_record, _ = PatientDiagnosisRecord.objects.get_or_create(patient=patient, visit=visit)
    previous_discharges = DischargesNotes.objects.filter(patient=patient_id, visit=visit)
    provisional_diagnosis_ids = provisional_record.provisional_diagnosis.values_list('id', flat=True)
    final_provisional_diagnosis= provisional_record.final_diagnosis.values_list('id', flat=True)
    # Numeric ranges for form inputs
    context = {
        'patient': patient,
        'visit': visit,
        'previous_discharges': previous_discharges,
        'previous_referrals': previous_referrals,
        'health_records': health_records,
        'patient_visits': patient_visits,
        'patient_vitals': patient_vitals,
        'final_provisional_diagnosis': final_provisional_diagnosis,
        'provisional_diagnoses': Diagnosis.objects.all(),
        'provisional_diagnosis_ids': provisional_diagnosis_ids,
        'range_51': range(51),
        'range_301': range(301),
        'range_101': range(101),
        'range_15': range(3, 16),
        'temps': np.arange(0, 510, 1) / 10,
        'consultation_note': consultation_note,
    }

    if request.method == 'POST':
        try:
            # Collect data from form submission
            history = request.POST.get('history_of_presenting_illness')
            doctor_plan = request.POST.get('doctor_plan')
            plan_note = request.POST.get('doctor_plan_note')
            ros = request.POST.get('review_of_systems')
            exam_notes = request.POST.get('physical_examination')
            allergy_summary = request.POST.get('allergy_summary')
            comorbidity_summary = request.POST.get('known_comorbidities_summary')
            provisional_ids = request.POST.getlist('provisional_diagnosis[]')

            # Save provisional diagnosis
            if not provisional_ids:
                provisional_record.data_recorder = doctor
            provisional_record.provisional_diagnosis.set(provisional_ids)
            provisional_record.save()

            # Create or update consultation note
            if consultation_note:
                consultation_note.history_of_presenting_illness = history
                consultation_note.doctor_plan = doctor_plan
                consultation_note.doctor_plan_note = plan_note
                consultation_note.review_of_systems = ros
                consultation_note.physical_examination = exam_notes
                consultation_note.allergy_summary = allergy_summary
                consultation_note.known_comorbidities_summary = comorbidity_summary
                consultation_note.save()
            else:
                # Prevent duplicate consultation for same visit
                if ConsultationNotes.objects.filter(patient=patient, visit=visit).exists():
                    messages.error(request, 'A consultation note already exists for this patient and visit.')
                    return render(request, 'doctor_template/add_consultation_notes.html', context)

               
                # Create a new consultation note
                consultation_note = ConsultationNotes.objects.create(
                    doctor=doctor,
                    patient=patient,
                    visit=visit,
                    history_of_presenting_illness=history,
                    doctor_plan=doctor_plan,
                    doctor_plan_note=plan_note,
                    review_of_systems=ros,
                    physical_examination=exam_notes,
                    allergy_summary=allergy_summary,
                    known_comorbidities_summary=comorbidity_summary
                )

            if doctor_plan == "Laboratory":
                messages.success(request, 'Consultation record saved successfully.')
                return redirect(reverse('doctor_save_laboratory', args=[patient_id, visit_id]))
            else:
                messages.success(request, 'Consultation record saved successfully.')
                return redirect(reverse('doctor_save_remotesconsultation_notes_next', args=[patient_id, visit_id]))            


        except Exception as e:
            messages.error(request, f'Error saving consultation note: {str(e)}')
            return render(request, 'doctor_template/add_consultation_notes.html', context)

    # If GET request, render form
    return render(request, 'doctor_template/add_consultation_notes.html', context)

    
@login_required
def save_remotesconsultation_notes_next(request, patient_id, visit_id):
    try:
    # Retrieve the patient and visit objects
        patient = get_object_or_404(Patients, pk=patient_id)
        visit = get_object_or_404(PatientVisits, patient=patient_id, id=visit_id)
        doctor_plan_note = ConsultationNotes.objects.filter(patient=patient_id, visit=visit).first()
        data_recorder = request.user.staff

        # Retrieve the consultation note object if it exists, otherwise create a new one
        consultation_note, created = PatientDiagnosisRecord.objects.get_or_create(patient=patient, visit=visit)

        # Retrieve all provisional and final diagnoses
        provisional_diagnoses = Diagnosis.objects.all()
        final_diagnoses = Diagnosis.objects.all()

        # Get the IDs of the provisional and final diagnoses associated with the consultation note
        provisional_diagnosis_ids = consultation_note.provisional_diagnosis.values_list('id', flat=True)
        final_diagnosis_ids = consultation_note.final_diagnosis.values_list('id', flat=True)

        # Retrieve the doctor plan from the query string
        if request.method == 'POST':          
            final_diagnosis = request.POST.getlist('final_diagnosis[]')
            doctor_plan = request.POST.get('doctor_plan')            
            if not consultation_note:
                consultation_note = PatientDiagnosisRecord.objects.create(patient=patient, visit=visit)
                consultation_note.data_recorder = data_recorder
            consultation_note.final_diagnosis.set(final_diagnosis)
            consultation_note.save()
            # Add success message
            messages.success(request, 'Consultation notes saved successfully.')

            # Redirect based on the doctor's plan
            if doctor_plan == 'Prescription':
                return redirect(reverse('doctor_save_prescription', args=[patient_id, visit_id]))
            elif doctor_plan == 'Laboratory':
                return redirect(reverse('doctor_save_remotesconsultation_notes',  args=[patient_id, visit_id]))
            elif doctor_plan == 'Referral':
                return redirect(reverse('doctor_save_remotereferral', args=[patient_id, visit_id]))
            elif doctor_plan == 'Counselling':
                return redirect(reverse('doctor_save_remote_counseling', args=[patient_id, visit_id]))
            elif doctor_plan == 'Procedure':
                return redirect(reverse('doctor_save_remoteprocedure', args=[patient_id, visit_id]))
            elif doctor_plan == 'Observation':
                return redirect(reverse('doctor_save_observation', args=[patient_id, visit_id]))
            elif doctor_plan == 'Discharge':
                return redirect(reverse('doctor_save_remote_discharges_notes', args=[patient_id, visit_id]))
            elif doctor_plan == 'Radiology':
                return redirect(reverse('doctor_add_radiology', args=[patient_id, visit_id]))

    except Exception as e:
        messages.error(request, f'Error: {str(e)}')

    # If an exception occurs or if the request method is not POST, render the form again
    context = {
        'provisional_diagnoses': provisional_diagnoses,
        'final_diagnoses': final_diagnoses,
        'patient': patient,
        'visit': visit,
        'consultation_note': consultation_note,
        'provisional_diagnosis_ids': provisional_diagnosis_ids,
        'final_diagnosis_ids': final_diagnosis_ids,
        'doctor_plan_note': doctor_plan_note,
    }
    return render(request, 'doctor_template/add_patientprovisional_diagnosis.html', context)    
    

@login_required    
def save_counsel(request, patient_id, visit_id):
    # Retrieve patient and visit objects
    patient = get_object_or_404(Patients, id=patient_id)
    visit = get_object_or_404(PatientVisits, id=visit_id)              
    data_recorder = request.user.staff
    # Retrieve existing remote counseling record if it exists
    remote_counseling = Counseling.objects.filter(patient=patient, visit=visit).first()
    consultation_notes = PatientDiagnosisRecord.objects.filter(patient=patient_id, visit=visit_id)  
    # Prepare context for rendering the template
    context = {
        'patient': patient, 
        'visit': visit,
        'remote_counseling': remote_counseling,
        'consultation_notes': consultation_notes,
    }
    
    # Handle form submission
    if request.method == 'POST':        
        form = CounselingForm(request.POST, instance=remote_counseling)
        
        # Check if a record already exists for the patient and visit
        if remote_counseling:
            # If a record exists, update it
            if form.is_valid():
                try:
                    form.save()
                    messages.success(request, 'counseling updated successfully.')
                except ValidationError as e:
                    messages.error(request, f'Validation Error: {e}')
            else:
                messages.error(request, 'Please correct the errors in the form.')
        else:
            # If no record exists, create a new one
            form.instance.patient = patient
            form.instance.data_recorder = data_recorder
            form.instance.visit = visit
            if form.is_valid():
                try:
                    form.save()
                    messages.success(request, 'counseling saved successfully.')
                except ValidationError as e:
                    messages.error(request, f'Validation Error: {e}')
            else:
                messages.error(request, 'Please correct the errors in the form.')

        # Redirect to the appropriate page after saving
        return redirect(reverse('doctor_save_remotesconsultation_notes',  args=[patient_id, visit_id]))
   
    else:
        # If it's a GET request, initialize the form with existing data (if any)
        form = CounselingForm(instance=remote_counseling)   
    # Add the form to the context
    context['form'] = form    
    return render(request, 'doctor_template/counsel_template.html', context)

@login_required    
def save_remote_discharges_notes(request, patient_id, visit_id):
    patient = get_object_or_404(Patients, id=patient_id)
    visit = get_object_or_404(PatientVisits, id=visit_id)
    consultation_notes = PatientDiagnosisRecord.objects.filter(patient=patient_id, visit=visit_id)    
    remote_discharges_notes = DischargesNotes.objects.filter(patient=patient, visit=visit).first()  
    context = {
            'patient': patient,
            'visit': visit,
            'consultation_notes': consultation_notes,
            'remote_discharges_notes': remote_discharges_notes,         
        }
        
    try:      
        # Check if the request user is staff
        data_recorder = request.user.staff      
        # Handle form submission
        if request.method == 'POST':
            form = DischargesNotesForm(request.POST, instance=remote_discharges_notes)
            if form.is_valid():
                remote_discharges_notes = form.save(commit=False)
                remote_discharges_notes.patient = patient
                remote_discharges_notes.visit = visit
                remote_discharges_notes.data_recorder = data_recorder
                remote_discharges_notes.save()
                messages.success(request, 'discharge notes saved successfully.')
                return redirect(reverse('doctor_save_remotesconsultation_notes',  args=[patient_id, visit_id]))  # Redirect to the next view
            else:
                messages.error(request, 'Please correct the errors in the form.')
        else:
            form = DischargesNotesForm(instance=remote_discharges_notes)        
        # Prepare context for rendering the template
        context['form'] = form
        return render(request, 'doctor_template/discharge_template.html', context)    
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return render(request, 'doctor_template/discharge_template.html', context)
        

@login_required
def save_remotereferral(request, patient_id, visit_id):
    try:
        # Retrieve patient and visit objects
        patient = get_object_or_404(Patients, id=patient_id)
        visit = get_object_or_404(PatientVisits, id=visit_id)
        data_recorder = request.user.staff
        referral = Referral.objects.filter(patient=patient, visit=visit).first()
        consultation_notes = PatientDiagnosisRecord.objects.filter(patient=patient_id, visit=visit_id)    
        context = {'patient': patient, 'visit': visit, 'referral': referral,'consultation_notes':consultation_notes}

        if request.method == 'POST':
            form = ReferralForm(request.POST, instance=referral)
            if form.is_valid():
                try:
                    referral = form.save(commit=False)
                    referral.patient = patient
                    referral.visit = visit
                    referral.data_recorder = data_recorder
                    # Ensure source_location is set
                    if not referral.source_location:
                        referral.source_location = "Default Source Location"
                    referral.save()
                    messages.success(request, 'Referral saved successfully.')
                    return redirect(reverse('doctor_save_remotesconsultation_notes',  args=[patient_id, visit_id]))
                except Exception as e:
                    messages.error(request, f'Error saving referral: {str(e)}')
            else:
                # Add form errors to messages
                form_errors = form.errors.as_json()
                messages.error(request, f'Form validation errors: {form_errors}')               
        else:
            form = ReferralForm(instance=referral)

        context['form'] = form
        return render(request, 'doctor_template/save_remotereferral.html', context)
    except Exception as e:
        messages.error(request, f'An unexpected error occurred: {str(e)}')
        return render(request, 'doctor_template/save_remotereferral.html', context)
    
    
    
@login_required
def save_observation(request, patient_id, visit_id):
    patient = get_object_or_404(Patients, id=patient_id)
    visit = get_object_or_404(PatientVisits, id=visit_id)
    data_recorder = request.user.staff
    record_exists = ObservationRecord.objects.filter(patient_id=patient_id, visit_id=visit_id).first()
    consultation_notes = PatientDiagnosisRecord.objects.filter(patient=patient_id, visit=visit_id)    
    context = {'patient': patient, 
               'visit': visit, 
               'consultation_notes': consultation_notes, 
               'record_exists': record_exists
               }
    if request.method == 'POST':
        form = ObservationRecordForm(request.POST)
        if form.is_valid():
            description = form.cleaned_data['observation_notes']
            try:
                if record_exists:
                    # If a record exists, update it
                    observation_record = ObservationRecord.objects.get(patient_id=patient_id, visit_id=visit_id)
                    observation_record.observation_notes = description
                    observation_record.data_recorder = data_recorder
                    observation_record.save()
                    messages.success(request, 'observation record updated successfully.')
                else:
                    # If no record exists, create a new one
                    ObservationRecord.objects.create(
                        patient=patient,
                        visit=visit,
                        data_recorder=data_recorder,
                        observation_notes=description,
                    )
                    messages.success(request, 'observation record saved successfully.')
                return redirect(reverse('doctor_save_remotesconsultation_notes',  args=[patient_id, visit_id]))
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            messages.error(request, 'Please fill out all required fields.')
    else:
        form = ObservationRecordForm(initial={'observation_notes': record_exists.observation_notes if record_exists else ''})

    context['form'] = form
    return render(request, 'doctor_template/observation_template.html', context)    

@login_required
def save_remoteprocedure(request, patient_id, visit_id):
    try:
        # Get patient and visit objects early
        try:
            patient = Patients.objects.get(id=patient_id)
        except Patients.DoesNotExist:
            return render(request, '404.html', {'error_message': "Patient not found."})

        try:
            visit = PatientVisits.objects.get(id=visit_id, patient_id=patient_id)
        except PatientVisits.DoesNotExist:
            return render(request, '404.html', {'error_message': "Visit not found."})

        # Fetch related data
        prescriptions = Prescription.objects.filter(patient=patient, visit=visit)
        previous_procedures = Procedure.objects.filter(patient=patient, visit=visit)
        consultation_note = ConsultationNotes.objects.filter(patient=patient, visit=visit).first()
        
        provisional_record, _ = PatientDiagnosisRecord.objects.get_or_create(patient=patient, visit=visit)
        final_provisional_diagnosis = provisional_record.final_diagnosis.values_list('id', flat=True)

        procedures = Procedure.objects.filter(patient=patient, visit=visit)
        total_price = sum(p.total_price for p in prescriptions)

        # Fetch procedure services based on payment form
        if patient.payment_form == 'insurance':
            remote_service = Service.objects.filter(
                Q(type_service='procedure') & Q(coverage='insurance')
            )
        else:
            remote_service = Service.objects.filter(type_service='procedure')

        # Calculate total cost of procedures
        total_procedure_cost = procedures.aggregate(Sum('cost'))['cost__sum'] or 0

        return render(request, 'doctor_template/procedure_template.html', {
            'visit': visit,
            'patient': patient,
            'prescriptions': prescriptions,
            'total_price': total_price,
            'previous_procedures': previous_procedures,
            'final_provisional_diagnosis': final_provisional_diagnosis,
            'consultation_note': consultation_note,
            'procedures': procedures,
            'remote_service': remote_service,
            'total_procedure_cost': total_procedure_cost,
        })

    except Exception as e:
        return render(request, '404.html', {'error_message': f"Oop's sorry we can't find that page! ({str(e)})"})
    
@csrf_exempt    
def get_patient_details(request, patient_id):
    try:
        patient = Patients.objects.get(id=patient_id)
        # Fetching services based on coverage and type
        if patient.payment_form == 'insurance':
            # If patient's payment form is insurance, fetch services with matching coverage
            remote_service = Service.objects.filter(
                type_service='procedure',
                coverage=patient.payment_form
            ).values('id', 'name')
        else:
            # If payment form is cash, fetch all services of type procedure
            remote_service = Service.objects.filter(
                type_service='procedure'
            ).values('id', 'name')        
        return JsonResponse({'success': True, 'patient': patient, 'remote_service': list(remote_service)})
    except Patients.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Patient not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@csrf_exempt
def get_procedure_cost(request):
    if request.method == 'POST':  # Change to POST method
        procedure_id = request.POST.get('procedure_id')
        patient_id = request.POST.get('patient_id')  # Receive patient ID        
        try:
            procedure = Service.objects.get(id=procedure_id)            
            # Get the patient
            patient = Patients.objects.get(id=patient_id)            
            # Check the patient's payment form
            payment_form = patient.payment_form            
            # Initialize cost variable
            cost = None            
            # If payment form is cash, fetch cash cost
            if payment_form == 'Cash':
                cost = procedure.cash_cost
            elif payment_form == 'Insurance':
                # Check if insurance company name is NHIF
                if patient.insurance_name == 'NHIF':
                    cost = procedure.nhif_cost
                else:
                    cost = procedure.insurance_cost
            
            if cost is not None:
                return JsonResponse({'cost': cost})
            else:
                return JsonResponse({'error': 'Cost not available for this payment form'}, status=404)
        
        except Service.DoesNotExist:
            return JsonResponse({'error': 'Procedure not found'}, status=404)
        except Patients.DoesNotExist:
            return JsonResponse({'error': 'Patient not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required    
def add_procedure(request):
    if request.method == 'POST':
        procedures_data = zip(
            request.POST.getlist('procedure_name[]'),
            request.POST.getlist('description[]'),
            request.POST.getlist('equipments_used[]'),
            request.POST.getlist('cost[]')
        )
        created_procedures = []

        for name_id, description, equipments_used, cost in procedures_data:
            try:
                # Extract patient and visit objects
                patient_id = request.POST.get('patient_id')
                visit_id = request.POST.get('visit_id')
                orderDate = request.POST.get('order_date')
                patient = get_object_or_404(Patients, id=patient_id)
                visit = get_object_or_404(PatientVisits, id=visit_id)
                
                # Retrieve the current user as the doctor
                doctor = request.user.staff

                # Create and save the new Procedure instance
                procedure = Procedure.objects.create(
                    patient=patient,
                    visit=visit,
                    doctor=doctor,
                    data_recorder=doctor,
                    order_date=orderDate,
                    name_id=name_id,
                    description=description,
                    equipments_used=equipments_used,
                    cost=cost
                )
                created_procedures.append({
                    'id': procedure.id,
                    'name': procedure.name.name,
                    'description': procedure.description,
                    'equipments_used': procedure.equipments_used,
                    'cost': procedure.cost,
                })
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        
        return JsonResponse({'status': 'success', 'message': 'Procedures added successfully', 'created_procedures': created_procedures})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
            


@csrf_exempt
@require_POST
def add_remoteprescription(request):
    try:
        with transaction.atomic():
            # ----------------- Extract data -----------------
            patient_id = request.POST.get('patient_id')
            visit_id = request.POST.get('visit_id')
            medicines = request.POST.getlist('medicine[]')
            formulations = request.POST.getlist('formulation[]')
            dosages = request.POST.getlist('dosage[]')
            frequencies = request.POST.getlist('frequency[]')
            durations = request.POST.getlist('duration[]')
            quantities = request.POST.getlist('quantity[]')
            routes = request.POST.getlist('route[]')
            total_prices = request.POST.getlist('total_price[]')
            entered_by = getattr(request.user, "staff", None)

            # ----------------- Validation: Patient & Visit -----------------
            if not all([patient_id, visit_id]):
                return JsonResponse({'status': 'error', 'message': 'Patient and visit information are required.'})

            try:
                patient = Patients.objects.get(id=patient_id)
                visit = PatientVisits.objects.get(id=visit_id)
            except (Patients.DoesNotExist, PatientVisits.DoesNotExist):
                return JsonResponse({'status': 'error', 'message': 'Invalid patient or visit information.'})

            # ----------------- Business Rule: Prevent adding after payment -----------------
            existing_status = Prescription.get_visit_status(visit)
            if existing_status.get("status") == "paid":
                return JsonResponse({
                    'status': 'error',
                    'message': 'This visit is already fully paid. No additional prescriptions can be added.'
                })

            # ----------------- Validation: At least one medicine -----------------
            if not medicines:
                return JsonResponse({'status': 'error', 'message': 'At least one medicine is required.'})

            prescriptions_to_create = []
            today = timezone.now().date()

            # ----------------- Loop through all medicines -----------------
            for i in range(len(medicines)):
                # Get medicine
                try:
                    medicine = Medicine.objects.get(id=medicines[i])
                except Medicine.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': f'Medicine at position {i+1} does not exist.'})

                # Check if expired
                if medicine.expiration_date and medicine.expiration_date < today:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'{medicine.drug_name} is expired (Expiry: {medicine.expiration_date}).'
                    })

                # Validate quantity
                quantity_used_str = quantities[i]
                if not quantity_used_str:
                    return JsonResponse({'status': 'error', 'message': f'Quantity required for {medicine.drug_name}.'})

                try:
                    quantity_used = int(quantity_used_str)
                except ValueError:
                    return JsonResponse({'status': 'error', 'message': f'Invalid quantity for {medicine.drug_name}.'})

                if quantity_used <= 0:
                    return JsonResponse({'status': 'error', 'message': f'Quantity must be greater than zero for {medicine.drug_name}.'})

                if medicine.remain_quantity is not None and quantity_used > medicine.remain_quantity:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Insufficient stock for {medicine.drug_name}. Only {medicine.remain_quantity} available.'
                    })

                # Get dosage object (optional)
                try:
                    dosage_obj = MedicineDosage.objects.get(id=dosages[i]) if dosages[i] else None
                except MedicineDosage.DoesNotExist:
                    dosage_obj = None

                # Get frequency object (required)
                try:
                    frequency_obj = PrescriptionFrequency.objects.get(id=frequencies[i])
                except PrescriptionFrequency.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': f'Invalid frequency for {medicine.drug_name}.'})

                # Get route object (optional)
                route_obj = None
                if routes and i < len(routes) and routes[i]:
                    try:
                        route_obj = MedicineRoute.objects.get(id=routes[i])
                    except MedicineRoute.DoesNotExist:
                        route_obj = None

                # ----------------- Create prescription object -----------------
                prescription = Prescription(
                    patient=patient,
                    visit=visit,
                    medicine=medicine,
                    entered_by=entered_by,
                    formulation_dose=formulations[i],
                    dosage=dosage_obj.dosage_value if dosage_obj else None,
                    frequency=frequency_obj,
                    duration=durations[i],
                    quantity_used=quantity_used,
                    total_price=total_prices[i] if total_prices and i < len(total_prices) else None,
                    route=route_obj.name if route_obj else None,

                    # Default statuses
                    verified="not_verified",
                    issued="not_issued",
                    status="unpaid",
                )
                prescriptions_to_create.append(prescription)

            # ----------------- Save all prescriptions -----------------
            for prescription in prescriptions_to_create:
                prescription.save()

            return JsonResponse({'status': 'success', 'message': 'Prescription saved successfully. Inventory will be deducted upon payment.'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'An unexpected error occurred: {str(e)}'})
    
    
@login_required
def save_prescription(request, patient_id, visit_id):
    try:
        # Get patient and visit objects first
        try:
            patient = Patients.objects.get(id=patient_id)
        except Patients.DoesNotExist:
            return render(request, '404.html', {'error_message': "Patient not found."})

        try:
            visit = PatientVisits.objects.get(id=visit_id, patient_id=patient_id)
        except PatientVisits.DoesNotExist:
            return render(request, '404.html', {'error_message': "Visit not found."})

        # Check if prescriptions already exist and their status
        prescriptions = Prescription.objects.filter(patient=patient, visit=visit)
        can_add_prescriptions = True
        restriction_reason = ""
        
        if prescriptions.exists():
            status_info = Prescription.get_visit_status(visit)
            
            # Check if any prescription is verified, issued, or paid
            if status_info["verified"] != "not_verified":
                can_add_prescriptions = False
                restriction_reason = "Prescriptions have already been verified."
            elif status_info["issued"] != "not_issued":
                can_add_prescriptions = False
                restriction_reason = "Medications have already been issued."
            elif status_info["status"] != "unpaid":
                can_add_prescriptions = False
                restriction_reason = "Prescriptions have already been paid for."

        # Retrieve related data
        frequencies = PrescriptionFrequency.objects.all()

        provisional_record, _ = PatientDiagnosisRecord.objects.get_or_create(patient=patient, visit=visit)
        consultation_note = ConsultationNotes.objects.filter(patient=patient, visit=visit).first()
        final_provisional_diagnosis = provisional_record.final_diagnosis.values_list('id', flat=True)

        current_date = timezone.now().date()
        total_price = sum(p.total_price for p in prescriptions)

        medicines = Medicine.objects.filter(
            remain_quantity__gt=0,
            expiration_date__gt=current_date
        ).distinct()

        range_31 = range(31)

        return render(request, 'doctor_template/prescription_template.html', {
            'patient': patient,
            'visit': visit,
            'final_provisional_diagnosis': final_provisional_diagnosis,
            'consultation_note': consultation_note,
            'medicines': medicines,
            'total_price': total_price,
            'range_31': range_31,
            'prescriptions': prescriptions,
            'frequencies': frequencies,
            'can_add_prescriptions': can_add_prescriptions,
            'restriction_reason': restriction_reason,
        })

    except Exception as e:
        return render(request, '404.html', {
            'error_message': f"Oop's sorry we can't find that page! ({str(e)})"
        })
    

@require_POST
@csrf_exempt
def get_unit_price(request):
    medicine_id = request.POST.get('medicine_id')
    patient_id = request.POST.get('patient_id')

    if not medicine_id or not patient_id:
        return JsonResponse({'error': 'Medicine ID and Patient ID are required'}, status=400)

    try:
        patient = Patients.objects.get(id=patient_id)
        medicine = Medicine.objects.get(pk=medicine_id)
    except Patients.DoesNotExist:
        return JsonResponse({'error': 'Patient not found'}, status=404)
    except Medicine.DoesNotExist:
        return JsonResponse({'error': 'Medicine not found'}, status=404)

    unit_price = None

    if patient.payment_form == 'Cash':
        unit_price = medicine.cash_cost
    elif patient.payment_form == 'Insurance':
        if patient.insurance_name == 'NHIF':
            unit_price = medicine.nhif_cost
        else:
            unit_price = medicine.insurance_cost

    if unit_price is not None:
        return JsonResponse({'unit_price': unit_price})
    else:
        return JsonResponse({'error': 'Cost not available for this payment form'}, status=404)
    
    
def get_drug_division_status(request):
    if request.method == 'GET':
        medicine_id = request.GET.get('medicine_id')
        try:
            medicine = Medicine.objects.get(pk=medicine_id)
            dividable = medicine.is_dividable
            return JsonResponse({'dividable': dividable})
        except Medicine.DoesNotExist:
            return JsonResponse({'error': 'Medicine not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method or missing parameter'}, status=400) 
    
def get_medicine_formulation(request):
    if request.method == 'GET':
        medicine_id = request.GET.get('medicine_id')
        try:
            medicine = Medicine.objects.get(pk=medicine_id)
            formulation = medicine.formulation_unit
            return JsonResponse({'formulation': formulation})
        except Medicine.DoesNotExist:
            return JsonResponse({'error': 'Medicine not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method or missing parameter'}, status=400) 
    
def get_formulation_unit(request):
    if request.method == 'GET':
        medicine_id = request.GET.get('medicine_id')
        try:
            medicine = Medicine.objects.get(pk=medicine_id)
            formulation_unit = medicine.formulation_unit
            return JsonResponse({'formulation_unit': formulation_unit})
        except Medicine.DoesNotExist:
            return JsonResponse({'error': 'Medicine not found'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)    
    
def get_frequency_name(request):
    if request.method == 'GET' and 'frequency_id' in request.GET:
        frequency_id = request.GET.get('frequency_id')
        try:
            frequency = PrescriptionFrequency.objects.get(pk=frequency_id)
            frequency_name = frequency.name
            return JsonResponse({'frequency_name': frequency_name})
        except PrescriptionFrequency.DoesNotExist:
            return JsonResponse({'error': 'Frequency not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)  
    

    
def medicine_dosage(request):
    if request.method == 'GET' and 'medicine_id' in request.GET:
        medicine_id = request.GET.get('medicine_id')

        try:
            medicine = Medicine.objects.get(id=medicine_id)
            dosage = medicine.dosage
            return JsonResponse({'dosage': dosage})
        except Medicine.DoesNotExist:
            return JsonResponse({'error': 'Medicine not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)  
        
       
   
@login_required   
def save_observations(request, patient_id, visit_id):
    try:
        # Retrieve visit history for the specified patient
        doctor = request.user.staff
        try:
            visit_history = PatientVisits.objects.get(id=visit_id, patient_id=patient_id)
        except PatientVisits.DoesNotExist:
            visit_history = None
        try:
            imaging_records = ImagingRecord.objects.filter(patient_id=patient_id, visit_id=visit_id,doctor_id=doctor)
        except ImagingRecord.DoesNotExist:
            imaging_records = None

        prescriptions = Prescription.objects.filter(patient=patient_id, visit=visit_id)
        consultation_notes = PatientDiagnosisRecord.objects.filter(patient=patient_id, visit=visit_id)
        try:
            procedures = Procedure.objects.filter(patient=patient_id, visit=visit_id, doctor_id=doctor)
        except Procedure.DoesNotExist:
            procedures = None

        total_price = sum(prescription.total_price for prescription in prescriptions)

        patient = Patients.objects.get(id=patient_id)

        # Fetching services based on coverage and type
        if patient.payment_form == 'insurance':
            # If patient's payment form is insurance, fetch services with matching coverage
            remote_service = Service.objects.filter(
                Q(type_service='Imaging') & Q(coverage=patient.payment_form)
            )
        else:
            # If payment form is cash, fetch all services of type procedure
            remote_service = Service.objects.filter(type_service='Imaging')

        # Calculate total amount from all procedures
        total_procedure_cost = procedures.aggregate(Sum('cost'))['cost__sum']
        total_imaging_cost = imaging_records.aggregate(Sum('cost'))['cost__sum']
        return render(request, 'doctor_template/observation_template.html', {
            'visit_history': visit_history,
            'patient': patient,
            'prescriptions': prescriptions,
            'total_price': total_price,
            'imaging_records': imaging_records,
            'procedures': procedures,
            'remote_service': remote_service,
            'total_procedure_cost': total_procedure_cost,
            'total_imaging_cost': total_imaging_cost,
            'consultation_notes': consultation_notes,
        })
    except Exception as e:
        # Handle other exceptions if necessary
        return render(request, '404.html', {'error_message': str(e)})
        

# Get an instance of a logger
logger = logging.getLogger(__name__)

@login_required
def add_radiology(request, patient_id, visit_id):
    try:    
        try:
            visit = PatientVisits.objects.get(id=visit_id, patient_id=patient_id)
        except PatientVisits.DoesNotExist:
            visit = None
       
        doctors=Staffs.objects.filter(role='doctor', work_place = 'resa')
        patient = Patients.objects.get(id=patient_id)
        consultation_notes = PatientDiagnosisRecord.objects.filter(patient=patient_id, visit=visit_id)
        radiology_record = ImagingRecord.objects.filter(patient=patient_id, visit=visit_id)
        consultation_note = ConsultationNotes.objects.filter(patient=patient, visit=visit).first()
        provisional_record, _ = PatientDiagnosisRecord.objects.get_or_create(patient=patient, visit=visit)     
        final_provisional_diagnosis= provisional_record.final_diagnosis.values_list('id', flat=True)
        # Fetching services based on coverage and type
        if patient.payment_form == 'insurance':
            # If patient's payment form is insurance, fetch services with matching coverage
            remote_service = Service.objects.filter(
                Q(type_service='Imaging') & Q(coverage=patient.payment_form)
            )
        else:
            # If payment form is cash, fetch all services of type procedure
            remote_service = Service.objects.filter(type_service='Imaging')
       
        return render(request, 'doctor_template/add_radiology.html', {
            'visit': visit,
            'patient': patient,
            'radiology_record': radiology_record,          
            'final_provisional_diagnosis': final_provisional_diagnosis,          
            'doctors': doctors,          
            'consultation_note': consultation_note,          
            'consultation_notes': consultation_notes,          
            'remote_service': remote_service,
        
        })
    except Exception as e:
        # Handle other exceptions if necessary
        return render(request, '404.html', {'error_message': str(e)})
        

@login_required
@csrf_exempt
def add_imaging(request):
    if request.method == 'POST':
        try:
            # Assuming your form fields are named appropriately in your template
            patient_id = request.POST.get('patient_id')
            doctor = request.user.staff
            visit_id = request.POST.get('visit_id')
            imaging_names = request.POST.getlist('imaging_name[]')
            descriptions = request.POST.getlist('description[]')            
            costs = request.POST.getlist('cost[]')
            order_date = request.POST.get('order_date')

            # Loop through the submitted data and create ImagingRecord objects
            for i in range(len(imaging_names)):
                imaging_record = ImagingRecord.objects.create(
                    patient_id=patient_id,
                    visit_id=visit_id,
                    order_date=order_date,
                    doctor=doctor,
                    data_recorder=doctor,
                    imaging_id=imaging_names[i],
                    description=descriptions[i],                 
                    cost=costs[i],
                    # Set other fields as needed
                )
                # Save the imaging record to the database
                imaging_record.save()

            # Assuming the imaging records were successfully saved
            return JsonResponse({'status': 'success', 'message': 'Imaging records saved successfully'})
        except IntegrityError as e:
            # Handle integrity errors, such as unique constraint violations
            return JsonResponse({'status': 'error', 'message': 'Integrity error occurred: ' + str(e)})
        except Exception as e:
            # Handle other unexpected errors
            return JsonResponse({'status': 'error', 'message': 'An error occurred: ' + str(e)})
    else:
        # If the request method is not POST, return an error response
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def save_laboratory(request, patient_id, visit_id):
    try:
        doctor = request.user.staff

        # Get patient and visit objects
        patient = get_object_or_404(Patients, id=patient_id)
        visit = get_object_or_404(PatientVisits, id=visit_id, patient_id=patient_id)

        # Fetch lab investigations for this visit
        investigations = LaboratoryOrder.objects.filter(patient_id=patient_id, visit_id=visit_id)

        # Fetch consultation notes for this visit
        consultation_note = ConsultationNotes.objects.filter(patient=patient, visit=visit).first()

        # Get available lab technicians
        lab_technicians = Staffs.objects.filter(role='labTechnician', work_place="resa")

        # Filter laboratory services based on payment form
        if patient.payment_form == 'insurance':
            remote_service = Service.objects.filter(
                type_service='Laboratory',
                coverage=patient.payment_form
            )
        else:
            remote_service = Service.objects.filter(type_service='Laboratory')

        # Calculate total lab cost
        total_lab_cost = investigations.aggregate(total=Sum('cost'))['total']

        context = {
            'visit': visit,
            'patient': patient,
            'Investigation': investigations,
            'previous_results': investigations,
            'doctors': lab_technicians,
            'remote_service': remote_service,
            'total_imaging_cost': total_lab_cost,
            'consultation_note': consultation_note,
        }

        return render(request, 'doctor_template/laboratory_template.html', context)

    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}) 
    
@csrf_exempt
def add_investigation(request):
    if request.method == 'POST':
        try:
            # Assuming your form fields are named appropriately in your template
            patient_id = request.POST.get('patient_id')
            doctor = request.user.staff
            visit_id = request.POST.get('visit_id')
            investigation_names = request.POST.getlist('investigation_name[]')
            descriptions = request.POST.getlist('description[]')            
            costs = request.POST.getlist('cost[]')
            order_date = request.POST.get('order_date')
            doctor_id = request.POST.get('doctor_id')

            # Loop through the submitted data and create LaboratoryOrder objects
            for i in range(len(investigation_names)):
                investigation_record = LaboratoryOrder.objects.create(
                    patient_id=patient_id,
                    doctor_id=doctor_id,
                    visit_id=visit_id,
                    order_date=order_date,                 
                    data_recorder=doctor,
                    lab_test_id=investigation_names[i],
                    description=descriptions[i],                 
                    cost=costs[i],
                    # Set other fields as needed
                )
                # Save the LaboratoryOrder record to the database
                investigation_record.save()

            # Assuming the LaboratoryOrder records were successfully saved
            return JsonResponse({'status': 'success', 'message': 'Laboratory records saved successfully'})
        except IntegrityError as e:
            # Handle integrity errors, such as unique constraint violations
            return JsonResponse({'status': 'error', 'message': 'Integrity error occurred: ' + str(e)})
        except Exception as e:
            # Handle other unexpected errors
            return JsonResponse({'status': 'error', 'message': 'An error occurred: ' + str(e)})
    else:
        # If the request method is not POST, return an error response
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}) 
    

@login_required
def patient_visit_history_view(request, patient_id):
    # Retrieve visit history for the specified patient
    visits = PatientVisits.objects.filter(patient_id=patient_id) 
    patient = Patients.objects.get(id=patient_id)
    return render(request, 'doctor_template/manage_patient_visit_history.html', {
        'visits': visits,
        'patient':patient,     
        })
    


    
@login_required
def prescription_detail(request, visit_number, patient_id):
    patient = Patients.objects.get(id=patient_id)
    prescriptions = Prescription.objects.filter(visit__vst=visit_number, visit__patient__id=patient_id)
    prescriber = None
    if prescriptions.exists():
        prescriber = prescriptions.first().entered_by
    context = {
        'patient': patient, 
        'prescriptions': prescriptions,
        'prescriber': prescriber,
        'visit_number': visit_number,
        }
    return render(request, "doctor_template/prescription_detail.html", context)

@login_required
def prescription_billing(request, visit_number, patient_id):
    patient = Patients.objects.get(id=patient_id)
    visit = PatientVisits.objects.get(vst=visit_number)
    prescriptions = Prescription.objects.filter(visit__vst=visit_number, visit__patient__id=patient_id)
    prescriber = None
    if prescriptions.exists():
        prescriber = prescriptions.first().entered_by
    context = {
        'patient': patient, 
        'prescriptions': prescriptions,
        'prescriber': prescriber,
        'visit_number': visit_number,
        'visit': visit,
        }
    return render(request, "doctor_template/prescription_bill.html", context)

@login_required
def prescription_notes(request, visit_number, patient_id):
    patient = Patients.objects.get(id=patient_id)
    visit = PatientVisits.objects.get(vst=visit_number)
    prescriptions = Prescription.objects.filter(visit__vst=visit_number, visit__patient__id=patient_id)
    prescriber = None
    if prescriptions.exists():
        prescriber = prescriptions.first().entered_by
    context = {
        'patient': patient, 
        'prescriptions': prescriptions,
        'prescriber': prescriber,
        'visit_number': visit_number,
        'visit': visit,
        }
    return render(request, "doctor_template/prescription_notes.html", context)



@login_required
@csrf_exempt
@require_POST
def save_remotepatient_vital(request):
    try:
        # Extract data from the request
        vital_id = request.POST.get('vital_id')
        patient_id = request.POST.get('patient_id')
        visit_id = request.POST.get('visit_id')
        respiratory_rate = request.POST.get('respiratory_rate')
        pulse_rate = request.POST.get('pulse_rate')
        sbp = request.POST.get('sbp')
        dbp = request.POST.get('dbp')
        spo2 = request.POST.get('spo2')
        temperature = request.POST.get('temperature')
        gcs = request.POST.get('gcs')
        avpu = request.POST.get('avpu')
        weight = request.POST.get('weight')
        doctor = request.user.staff

        try:
            # Retrieve the patient
            patient = Patients.objects.get(id=patient_id)
        except Patients.DoesNotExist:
            return JsonResponse({'status': False, 'message': 'Patient does not exist'})

        try:
            # Retrieve the visit
            visit = PatientVisits.objects.get(id=visit_id)
        except PatientVisits.DoesNotExist:
            return JsonResponse({'status': False, 'message': 'Visit does not exist'})

        # Check for duplicate records
        blood_pressure = f"{sbp}/{dbp}"
        if not vital_id:
            duplicate_vitals = PatientVital.objects.filter(
                patient=patient,
                visit=visit,
                respiratory_rate=respiratory_rate,
                pulse_rate=pulse_rate,
                blood_pressure=blood_pressure,
                spo2=spo2,
                sbp=sbp,
                dbp=dbp,
                temperature=temperature,
                gcs=gcs,
                avpu=avpu,
                weight=weight,
            )
            if duplicate_vitals.exists():
                return JsonResponse({'status': False, 'message': 'A similar vital record already exists for this patient during this visit.'})

        if vital_id:
            try:
                # Editing existing vital
                vital = PatientVital.objects.get(pk=vital_id)
                vital.blood_pressure = blood_pressure if sbp and dbp else vital.blood_pressure  # Use existing SBP/DBP if not provided
                message = 'Patient vital updated successfully'
            except PatientVital.DoesNotExist:
                return JsonResponse({'status': False, 'message': 'Vital record does not exist'})
        else:
            # Creating new vital
            vital = PatientVital()
            vital.blood_pressure = blood_pressure
            message = 'Patient vital created successfully'

        # Update or set values for other fields
        vital.visit = visit
        vital.respiratory_rate = respiratory_rate
        vital.pulse_rate = pulse_rate
        vital.recorded_by = doctor
        vital.blood_pressure = blood_pressure
        vital.sbp = sbp
        vital.dbp = dbp
        vital.spo2 = spo2
        vital.gcs = gcs
        vital.temperature = temperature
        vital.avpu = avpu
        vital.weight = weight
        vital.patient = patient
        vital.save()

        return JsonResponse({'status': True, 'message': message})
    except Patients.DoesNotExist:
        return JsonResponse({'status': False, 'message': 'Patient does not exist'})
    except PatientVisits.DoesNotExist:
        return JsonResponse({'status': False, 'message': 'Visit does not exist'})
    except Exception as e:
        return JsonResponse({'status': False, 'message': str(e)})
    
 
    
@login_required
def consultation_notes_view(request):
    # Get all patients who have consultation notes
    patient_records = Patients.objects.filter(
        consultationnotes__isnull=False
    ).distinct().order_by('-consultationnotes__updated_at')

    return render(request, 'doctor_template/manage_consultation_notes.html', {
        'patient_records': patient_records
    })


@login_required
def new_consultation_order(request):
    # Get today's date
    today = timezone.now().date()

    # Filter consultation orders for today
    today_orders = ConsultationOrder.objects.filter(order_date=today).select_related('patient')

    # Get unique patients from today's consultation orders
    patients = Patients.objects.filter(id__in=today_orders.values_list('patient_id', flat=True)).distinct()

    return render(request, 'doctor_template/new_consultation_order.html', {
        'orders': today_orders,
        'patient_records': patients
    })



def fetch_order_counts_view(request):
    # Retrieve the current logged-in doctor
    current_doctor = request.user.staff
    consultation_orders = ConsultationOrder.objects.filter(doctor=current_doctor)  
    current_date = timezone.now().date()  
    # Retrieve the counts of unread and read orders for the current doctor
    unread_count = Order.objects.filter(order_type__in=[consultation.consultation.name for consultation in consultation_orders], order_date=current_date).count()
    read_count = Order.objects.filter(order_type__in=[consultation.consultation.name for consultation in consultation_orders], is_read=True).count()    
    # Return the counts as JSON response
    return JsonResponse({'unread_count': unread_count, 'read_count': read_count})

def fetch_radiology_order_counts_view(request):
    # Retrieve the current logged-in doctor
    current_doctor = request.user.staff
    pathodology_records=ImagingRecord.objects.filter(doctor=current_doctor) 
    current_date = timezone.now().date()   
    # Retrieve the counts of unread and read orders for the current doctor
    unread_count = Order.objects.filter(order_type__in=[pathology.imaging.name for pathology in pathodology_records],order_date=current_date) .count()
    read_count = Order.objects.filter(order_type__in=[pathology.imaging.name for pathology in pathodology_records], is_read=True) .count()    
    # Return the counts as JSON response
    return JsonResponse({'unread_count': unread_count, 'read_count': read_count})

def fetch_procedure_order_counts_view(request):
    # Retrieve the current logged-in doctor
    current_doctor = request.user.staff
    procedures = Procedure.objects.filter(doctor=current_doctor)
    current_date = timezone.now().date() 
    # Retrieve the counts of unread and read orders for the current doctor
    unread_count = Order.objects.filter(order_type__in=[procedure.name.name for procedure in procedures], order_date=current_date).count()    
    read_count = Order.objects.filter(order_type__in=[procedure.name.name for procedure in procedures], is_read=True).count()    
    # Return the counts as JSON response
    return JsonResponse({'unread_count': unread_count, 'read_count': read_count})


def fetch_lab_order_counts_view(request):
    # Retrieve the current logged-in doctor
    current_doctor = request.user.staff
    procedures = LaboratoryOrder.objects.filter(data_recorder=current_doctor)
    current_date = timezone.now().date() 
    # Retrieve the counts of unread and read orders for the current doctor
    unread_count = Order.objects.filter(order_type__in=[procedure.name.name for procedure in procedures], order_date=current_date).count()
    
    read_count = Order.objects.filter(order_type__in=[procedure.name.name for procedure in procedures], is_read=True).count()    
    # Return the counts as JSON response
    return JsonResponse({'unread_count': unread_count, 'read_count': read_count})

@login_required
def radiology_order(request):
    doctor = request.user.staff
    pathodology_records=ImagingRecord.objects.filter(doctor=doctor).order_by('-order_date')  
    return render(request,"doctor_template/manage_radiology.html",{
        "pathodology_records":pathodology_records,       
        }) 
    
@login_required
def new_radiology_order(request):
    doctor = request.user.staff
    current_date = timezone.now().date() 
    pathodology_records=ImagingRecord.objects.filter(doctor=doctor).order_by('-order_date')   
    unread_orders = Order.objects.filter(order_type__in=[pathology.imaging.name for pathology in pathodology_records],  order_date=current_date) 
    orders = unread_orders   
    unread_orders.update(is_read=True)     
    return render(request,"doctor_template/new_radiology_order.html",{
        "orders":orders,       
        }) 
    
@login_required
def patient_procedure_view(request):
    # Retrieve distinct patient and visit combinations from RemoteProcedure
    patient_procedures = (
        Procedure.objects.values('patient__mrn', 'visit__vst',
                                       'doctor__admin__first_name',
                                          'doctor__middle_name',
                                          'doctor__role',
                                          'doctor__admin__first_name',
                                       ) 
        .annotate(
            latest_date=Max('created_at'),  # Get the latest procedure date for each patient and visit
            procedure_name=Subquery(
                Procedure.objects.filter(
                    patient__mrn=OuterRef('patient__mrn'),  # Match patient MRN
                    visit__vst=OuterRef('visit__vst')       # Match visit number
                )
                .order_by('-created_at')  # Order by most recent procedure
                .values('name__name')[:1]  # Retrieve the latest procedure name
            )
        )
        .order_by('-latest_date')  # Order by the latest procedure date
    )

    context = {
        'patient_procedures': patient_procedures,
    }
    return render(request, 'doctor_template/manage_procedure.html', context)

@login_required
def patient_procedure_detail_view(request, mrn, visit_number):
    """ View to display procedure details for a specific patient and visit. """
    
    # Fetch patient and visit in one go
    patient = get_object_or_404(Patients, mrn=mrn)
    visit = get_object_or_404(PatientVisits, vst=visit_number)
    
    # Retrieve procedures related to this patient and visit
    procedures = Procedure.objects.filter(patient=patient, visit=visit).select_related('doctor')

    # Get the doctor who performed the first procedure (if exists)
    procedure_done_by = procedures[0].doctor if procedures else None

    context = {
        'procedure_done_by': procedure_done_by,
        'patient': patient,
        'visit': visit,
        'procedure': procedures,
    }

    return render(request, 'doctor_template/manage_procedure_detail_view.html', context)


@login_required    
def edit_procedure_result(request, patient_id, visit_id, procedure_id):
    # Retrieve patient and visit objects
    patient = get_object_or_404(Patients, id=patient_id)
    visit = get_object_or_404(PatientVisits, id=visit_id)            

    procedures = Procedure.objects.filter(patient=patient, visit=visit, id=procedure_id).first()
    
    # Prepare context for rendering the template
    context = {
        'patient': patient, 
        'visit': visit,
        'procedures': procedures,
    }
    
    # Handle form submission
    if request.method == 'POST':        
        form = ProcedureForm(request.POST, instance=procedures)
        
        # Check if a record already exists for the patient and visit
        if procedures:
            # If a record exists, update it
            if form.is_valid():
                try:
                    form.save()
                    messages.success(request, 'Remote counseling updated successfully.')
                except ValidationError as e:
                    messages.error(request, f'Validation Error: {e}')
            else:
                messages.error(request, 'Please correct the errors in the form.')
        else:
            # If no record exists, create a new one
            form.instance.patient = patient          
            form.instance.visit = visit
            if form.is_valid():
                try:
                    form.save()
                    messages.success(request, 'Remote counseling saved successfully.')
                except ValidationError as e:
                    messages.error(request, f'Validation Error: {e}')
            else:
                messages.error(request, 'Please correct the errors in the form.')

        # Redirect to the appropriate page after saving
        return redirect(reverse('doctor_patient_procedure_view'))
   
    else:
        # If it's a GET request, initialize the form with existing data (if any)
        form = ProcedureForm(instance=procedures)   
    # Add the form to the context
    context['form'] = form    
    return render(request, 'doctor_template/edit_procedure_result.html', context)

@login_required    
def edit_radiology_result(request, patient_id, visit_id, radiology_id):
    # Retrieve patient and visit objects
    patient = get_object_or_404(Patients, id=patient_id)
    visit = get_object_or_404(PatientVisits, id=visit_id)            

    procedures = ImagingRecord.objects.filter(patient=patient, visit=visit, id=radiology_id).first()
    
    # Prepare context for rendering the template
    context = {
        'patient': patient, 
        'visit': visit,
        'procedures': procedures,
    }
    
    # Handle form submission
    if request.method == 'POST':        
        form = ImagingRecordForm(request.POST, instance=procedures)
        
        # Check if a record already exists for the patient and visit
        if procedures:
            # If a record exists, update it
            if form.is_valid():
                try:
                    form.save()
                    messages.success(request, 'Remote radiology updated successfully.')
                except ValidationError as e:
                    messages.error(request, f'Validation Error: {e}')
            else:
                messages.error(request, 'Please correct the errors in the form.')
        else:
            # If no record exists, create a new one
            form.instance.patient = patient          
            form.instance.visit = visit
            if form.is_valid():
                try:
                    form.save()
                    messages.success(request, 'Remote radiology saved successfully.')
                except ValidationError as e:
                    messages.error(request, f'Validation Error: {e}')
            else:
                messages.error(request, 'Please correct the errors in the form.')

        # Redirect to the appropriate page after saving
        return redirect(reverse('doctor_radiology_order'))
   
    else:
        # If it's a GET request, initialize the form with existing data (if any)
        form = ImagingRecordForm(instance=procedures)   
    # Add the form to the context
    context['form'] = form    
    return render(request, 'doctor_template/edit_radiology_result.html', context)

@login_required    
def edit_lab_result(request, patient_id, visit_id, lab_id):
    # Retrieve patient and visit objects
    patient = get_object_or_404(Patients, id=patient_id)
    visit = get_object_or_404(PatientVisits, id=visit_id)            

    procedures = LaboratoryOrder.objects.filter(patient=patient, visit=visit, id=lab_id).first()
    
    # Prepare context for rendering the template
    context = {
        'patient': patient, 
        'visit': visit,
        'procedures': procedures,
    }
    
    # Handle form submission
    if request.method == 'POST':        
        form = LaboratoryOrderForm(request.POST, instance=procedures)
        
        # Check if a record already exists for the patient and visit
        if procedures:
            # If a record exists, update it
            if form.is_valid():
                try:
                    form.save()
                    messages.success(request, 'Remote Lab result updated successfully.')
                except ValidationError as e:
                    messages.error(request, f'Validation Error: {e}')
            else:
                messages.error(request, 'Please correct the errors in the form.')
        else:
            # If no record exists, create a new one
            form.instance.patient = patient          
            form.instance.visit = visit
            if form.is_valid():
                try:
                    form.save()
                    messages.success(request, 'Remote Lab result saved successfully.')
                except ValidationError as e:
                    messages.error(request, f'Validation Error: {e}')
            else:
                messages.error(request, 'Please correct the errors in the form.')

        # Redirect to the appropriate page after saving
        return redirect(reverse('doctor_patient_lab_view'))
   
    else:
        # If it's a GET request, initialize the form with existing data (if any)
        form = LaboratoryOrderForm(instance=procedures)   
    # Add the form to the context
    context['form'] = form    
    return render(request, 'doctor_template/edit_lab_result.html', context)


@login_required
def patient_lab_view(request):
    template_name = 'doctor_template/lab_order_result.html'
    # Query to retrieve the latest procedure record for each patient
    procedures = LaboratoryOrder.objects.order_by('-order_date')      
    return render(request, template_name, {'procedures': procedures})

@login_required
def new_procedure_order(request):
    template_name = 'doctor_template/new_procedure_order.html'
    doctor = request.user.staff
    current_date = timezone.now().date() 
    # Query to retrieve the latest procedure record for each patient
    procedures = Procedure.objects.filter(doctor=doctor).order_by('-order_date')    
    unread_orders = Order.objects.filter(order_type__in=[procedure.name.name for procedure in procedures],  order_date=current_date)    
    orders = unread_orders 
    unread_orders.update(is_read=True)         
    return render(request, template_name, {'orders': orders})

@login_required
def new_lab_order(request):
    template_name = 'doctor_template/new_lab_order.html'
    doctor = request.user.staff
    current_date = timezone.now().date() 
    # Query to retrieve the latest procedure record for each patient
    procedures = LaboratoryOrder.objects.filter(data_recorder=doctor).order_by('-order_date')    
    unread_orders = Order.objects.filter(order_type__in=[procedure.lab_test.name for procedure in procedures],  order_date=current_date)    
    orders = unread_orders 
    unread_orders.update(is_read=True)         
    return render(request, template_name, {'orders': orders})
    



def counseling_list_view(request):
    counselings = Counseling.objects.all().order_by('-created_at')
    return render(request, 'doctor_template/manage_counselling.html', {'counselings': counselings})    

def observation_record_list_view(request):
    observation_records = ObservationRecord.objects.all().order_by('-created_at')
    return render(request, 'doctor_template/manage_observation_record.html', {'observation_records': observation_records})



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
    
    return render(request, 'doctor_template/employee_detail.html', context)

