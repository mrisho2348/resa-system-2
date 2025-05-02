import calendar
from datetime import  datetime
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
from django.db.models import Sum
from django.db import transaction
from django.db.models import Q
import numpy as np
from django.core.exceptions import ObjectDoesNotExist
from clinic.forms import CounselingForm, DischargesNotesForm, ImagingRecordForm, LaboratoryOrderForm, ObservationRecordForm, ProcedureForm, ReferralForm
from django.core.exceptions import ValidationError
from clinic.models import  Consultation,  DiseaseRecode, Medicine, PathodologyRecord, Patients, Procedure, Staffs
from django.views.decorators.http import require_POST
from django.contrib.contenttypes.models import ContentType
from .models import ClinicChiefComplaint, ClinicPrimaryPhysicalExamination, ClinicSecondaryPhysicalExamination, ConsultationNotes,  ConsultationOrder, Counseling, Country, Diagnosis,Diagnosis, DischargesNotes, Employee, EmployeeDeduction, HealthRecord, ImagingRecord, InsuranceCompany, InventoryItem,LaboratoryOrder, ObservationRecord, Order, PatientDiagnosisRecord, PatientVisits, PatientVital, Prescription, PrescriptionFrequency, Procedure, Patients, Reagent, Referral, SalaryChangeRecord,Service
from django.views.decorators.http import require_GET
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import logout
from django.utils.decorators import method_decorator
from kahamahmis.forms import StaffProfileForm
from django.views import View

@login_required
def doctor_dashboard(request):
    try:
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

    except Patients.DoesNotExist:
        messages.error(request, 'Error fetching patient data.')
    except Medicine.DoesNotExist:
        messages.error(request, 'Error fetching medicine data.')
    except LaboratoryOrder.DoesNotExist:
        messages.error(request, 'Error fetching laboratory order data.')
    except DiseaseRecode.DoesNotExist:
        messages.error(request, 'Error fetching disease record data.')
    except Service.DoesNotExist:
        messages.error(request, 'Error fetching service data.')
    except Staffs.DoesNotExist:
        messages.error(request, 'Error fetching staff data.')
    except Exception as e:
        messages.error(request, f'An unexpected error occurred: {e}')

    # Render the template with the context
    return render(request, "doctor_template/home_content.html", context)

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
        "patient_records":patient_records,
        "range_121":range_121,
        "doctors":doctors,
        "all_country":all_country,
        })
    


@login_required
def manage_consultation(request):
    patients=Patients.objects.all() 
    pathology_records=PathodologyRecord.objects.all() 
    doctors=Staffs.objects.filter(role='doctor')
    context = {
        'patients':patients,
        'pathology_records':pathology_records,
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




@login_required
def single_staff_detail(request, staff_id):
    staff = get_object_or_404(Staffs, id=staff_id)
    # Fetch additional staff-related data  
    context = {
        'staff': staff,
     
    }

    return render(request, "doctor_template/staff_details.html", context)

@login_required
def view_patient(request, patient_id):
    patient = get_object_or_404(Patients, id=patient_id)
    # Fetch additional staff-related data  
    context = {
        'patient': patient,
     
    }

    return render(request, "doctor_template/patients_detail.html", context)


    
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

            # Create a notification for the patient
            notification_message = f"New appointment scheduled with Dr. { doctor.admin.get_full_name() } on {date_of_consultation} from {start_time} to {end_time}."
            Notification.objects.create(
                content_type=ContentType.objects.get_for_model(Patients),
                object_id=patient.id,
                message=notification_message
            )

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


@login_required
def generate_invoice_bill(request,  patient_id,visit_id):
    # Retrieve the patient and visit objects based on IDs
    patient = get_object_or_404(Patients, id=patient_id)
    visit = get_object_or_404(PatientVisits, id=visit_id)    
    orders = Order.objects.filter(patient=patient, visit=visit)
     
    context = {
        'orders': orders,
        'patient': patient,
        'visit': visit,
       
    }
    return render(request, 'doctor_template/invoice_bill.html', context)



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


@login_required
def generate_billing(request, procedure_id):
    procedure = get_object_or_404(Procedure, id=procedure_id)

    context = {
        'procedure': procedure,
    }

    return render(request, 'doctor_template/billing_template.html', context)

@login_required
def appointment_list_view(request):
    appointments = Consultation.objects.all() 
    context = {       
        'appointments':appointments,
    }
    return render(request, 'doctor_template/manage_appointment.html', context)


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
    

@login_required
def unread_appointments_view(request):
    try:
        # Get the logged-in doctor
        doctor = request.user.staff
        print(f"Doctor: {doctor}")

        # Get today's date
        today = timezone.now().date()

        # Fetching all consultations for today associated with the doctor
        appointments = Consultation.objects.filter(doctor=doctor, created_at__date=today)

        # Context data to pass to the template
        context = {
            'appointments': appointments,
        }
    except Staffs.DoesNotExist:
        context = {
            'error': "Doctor not found."
        }
    except Exception as e:
        context = {
            'error': str(e)
        }
    
    return render(request, 'doctor_template/unread_appointments.html', context)

@login_required
def read_appointments_view(request):
    doctor = request.user.staff
    # Fetching all read consultations associated with the doctor
    read_appointments = Consultation.objects.filter(doctor=doctor)    
    return render(request, 'doctor_template/read_appointments.html', {'appointments': read_appointments})


@csrf_exempt
def get_item_quantity(request):
    if request.method == 'POST':
        item_id = request.POST.get('itemId')  # Use request.POST.get() instead of request.GET.get()
          
        try:
            item = InventoryItem.objects.get(id=item_id)
            quantity = item.quantity
            
            return JsonResponse({'quantity': quantity})
        except InventoryItem.DoesNotExist:
            return JsonResponse({'error': 'Item not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)
    

def get_chief_complaints(request):
    # Retrieve chief complaints from the HealthRecord model
    chief_complaints = HealthRecord.objects.values_list('name', flat=True)
    
    # Convert the QuerySet to a list
    chief_complaints_list = list(chief_complaints)
    
    # Return the chief complaints as JSON response
    return JsonResponse(chief_complaints_list, safe=False)    

@csrf_exempt
def save_chief_complaint(request):
    try:
        # Ensure the request method is POST
        if request.method == 'POST':
            # Extract data from the POST request
            patient_id = request.POST.get('patient_id')
            visit_id = request.POST.get('visit_id')
            health_record_id = request.POST.get('chief_complain_name')
            other_chief_complaint = request.POST.get('other_chief_complaint')
            duration = request.POST.get('chief_complain_duration')        

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
                    return JsonResponse({'status': False, 'message': 'A ChiefComplaint with the same name already exists for this patient'})
                chief_complaint.other_complaint = other_chief_complaint
            else:
                # Check if a ChiefComplaint with the same health_record_id already exists for the given visit_id
                if ClinicChiefComplaint.objects.filter(health_record_id=health_record_id, visit_id=visit_id).exists():
                    return JsonResponse({'status': False, 'message': 'A ChiefComplaint with the same name  already exists for this patient'})
                chief_complaint.health_record_id = health_record_id          

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

            # Create a modified entry with unified information under the 'health_record' key
            modified_entry = {
                'id': entry['id'],
                'patient_id': entry['patient_id'],
                'visit_id': entry['visit_id'],
                'health_record': display_info,
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
        # Fetch the ChiefComplaint object to delete
        chief_complaint = get_object_or_404(ClinicChiefComplaint, id=chief_complaint_id)
        
        # Delete the ChiefComplaint
        chief_complaint.delete()
        
        # Return a success response
        return JsonResponse({'message': 'Chief complaint deleted successfully'})
    except Exception as e:
        # If an error occurs, return an error response
        return JsonResponse({'error': str(e)}, status=500)   
    
@login_required
def save_remotesconsultation_notes(request, patient_id, visit_id):
    doctor = request.user.staff
    patient = get_object_or_404(Patients, pk=patient_id)
    visit = get_object_or_404(PatientVisits, patient=patient_id, id=visit_id)
    
    try:     
        patient_vitals = PatientVital.objects.filter(patient=patient_id, visit=visit)
        health_records = HealthRecord.objects.all()
        
    except Exception as e:
        patient_vitals = None  
        health_records = None  
        
       
    provisional_diagnoses = Diagnosis.objects.all()
    consultation_note = ConsultationNotes.objects.filter(patient=patient_id, visit=visit).first()
    provisional_record, created = PatientDiagnosisRecord.objects.get_or_create(patient=patient, visit=visit)
    provisional_diagnosis_ids = provisional_record.provisional_diagnosis.values_list('id', flat=True)
    primary_examination = ClinicPrimaryPhysicalExamination.objects.filter(patient=patient_id, visit=visit).first()
    previous_counselings = Counseling.objects.filter(patient=patient_id, visit=visit)
    previous_discharges = DischargesNotes.objects.filter(patient=patient_id, visit=visit)
    previous_observations = ObservationRecord.objects.filter(patient=patient_id, visit=visit)
    previous_lab_orders = LaboratoryOrder.objects.filter(patient=patient_id, visit=visit)
    previous_prescriptions = Prescription.objects.filter(patient=patient_id, visit=visit)
    previous_referrals = Referral.objects.filter(patient=patient_id, visit=visit)
    previous_procedures = Procedure.objects.filter(patient=patient_id, visit=visit)
    secondary_examination = ClinicSecondaryPhysicalExamination.objects.filter(patient_id=patient_id, visit_id=visit_id).first()    
    pathology_records = PathodologyRecord.objects.all()   
    range_51 = range(51)
    range_301 = range(301)
    range_101 = range(101)
    range_15 = range(3, 16)
    integer_range = np.arange(start=0, stop=510, step=1)
    temps = integer_range / 10
    
    context = {
        'secondary_examination': secondary_examination,
        'previous_counselings': previous_counselings,
        'previous_discharges': previous_discharges,
        'previous_observations': previous_observations,
        'previous_lab_orders': previous_lab_orders,
        'previous_prescriptions': previous_prescriptions,
        'previous_referrals': previous_referrals,
        'previous_procedures': previous_procedures,
        'primary_examination': primary_examination,
        'health_records': health_records,
        'pathology_records': pathology_records,    
        'provisional_diagnoses': provisional_diagnoses,
        'provisional_diagnosis_ids': provisional_diagnosis_ids,        
        'patient': patient,
        'visit': visit,
        'patient_vitals': patient_vitals,       
        'range_51': range_51,
        'range_301': range_301,
        'range_101': range_101,
        'range_15': range_15,
        'temps': temps,
        'consultation_note': consultation_note,
    }

    if request.method == 'POST':
        try:
            # Retrieve form fields for consultation note      
            type_of_illness = request.POST.get('type_of_illness')        
            nature_of_current_illness = request.POST.get('nature_of_current_illness')        
            history_of_presenting_illness = request.POST.get('history_of_presenting_illness')        
            doctor_plan = request.POST.get('doctor_plan')       
            pathology = request.POST.getlist('pathology[]')
            
               # Retrieve form fields for secondary examination
            heent = request.POST.get('heent')
            cns = request.POST.get('cns')
            normal_cns = request.POST.get('normal_cns')
            abnormal_cns = request.POST.get('abnormal_cns')
            cvs = request.POST.get('cvs')
            normal_cvs = request.POST.get('normal_cvs')
            abnormal_cvs = request.POST.get('abnormal_cvs')
            rs = request.POST.get('rs')
            normal_rs = request.POST.get('normal_rs')
            abnormal_rs = request.POST.get('abnormal_rs')
            pa = request.POST.get('pa')
            normal_pa = request.POST.get('normal_pa')
            abnormal_pa = request.POST.get('abnormal_pa')
            gu = request.POST.get('gu')
            normal_gu = request.POST.get('normal_gu')
            abnormal_gu = request.POST.get('abnormal_gu')
            mss = request.POST.get('mss')
            normal_mss = request.POST.get('normal_mss')
            abnormal_mss = request.POST.get('abnormal_mss')

            # Retrieve form fields for primary examination
            airway = request.POST.get('airway')
            explanation = request.POST.get('explanation')
            breathing = request.POST.get('breathing')
            normal_breathing = request.POST.getlist('normalBreathing[]')
            abnormal_breathing = request.POST.get('abnormalBreathing')
            circulating = request.POST.get('circulating')
            normal_circulating = request.POST.getlist('normalCirculating[]')
            abnormal_circulating = request.POST.get('abnormalCirculating')
            gcs = request.POST.get('gcs')
            rbg = request.POST.get('rbg')
            pupil = request.POST.get('pupil')
            pain_score = request.POST.get('painScore')
            avpu = request.POST.get('avpu')
            exposure = request.POST.get('exposure')
            normal_exposure = request.POST.getlist('normal_exposure[]')
            abnormal_exposure = request.POST.get('abnormalities')           
        
            provisional_diagnosis = request.POST.getlist('provisional_diagnosis[]')       
            if not provisional_diagnosis:
                provisional_record = PatientDiagnosisRecord.objects.create(patient=patient, visit=visit)
                provisional_record.data_recorder = request.user.staff

            provisional_record.provisional_diagnosis.set(provisional_diagnosis)  
            provisional_record.save()    
            # Handle primary examination model
            if primary_examination:                
                primary_examination.patent_airway = airway
                primary_examination.notpatient_explanation = explanation
                primary_examination.breathing = breathing
                primary_examination.normal_breathing = normal_breathing
                primary_examination.abnormal_breathing = abnormal_breathing
                primary_examination.circulating = circulating
                primary_examination.normal_circulating = normal_circulating
                primary_examination.abnormal_circulating = abnormal_circulating
                primary_examination.gcs = gcs
                primary_examination.rbg = rbg
                primary_examination.pupil = pupil
                primary_examination.pain_score = pain_score
                primary_examination.avpu = avpu
                primary_examination.exposure = exposure
                primary_examination.normal_exposure = normal_exposure
                primary_examination.abnormal_exposure = abnormal_exposure
                primary_examination.save()
            else:
                existing_record = ClinicPrimaryPhysicalExamination.objects.filter(patient_id=patient_id, visit_id=visit_id).first()
                if existing_record:
                    messages.error(request, f'A record already exists for this patient on the specified visit')
                    return render(request, 'doctor_template/add_consultation_notes.html', context)
                ClinicPrimaryPhysicalExamination.objects.create(
                    patient_id=patient_id,
                    visit_id=visit_id,
                    patent_airway = airway,
                    notpatient_explanation = explanation,
                    breathing = breathing,
                    normal_breathing = normal_breathing,
                    abnormal_breathing = abnormal_breathing,
                    circulating = circulating,
                    normal_circulating = normal_circulating,
                    abnormal_circulating = abnormal_circulating,
                    gcs = gcs,
                    rbg = rbg,
                    pupil = pupil,
                    pain_score = pain_score,
                    avpu = avpu,
                    exposure = exposure,
                    normal_exposure = normal_exposure,
                    abnormal_exposure = abnormal_exposure,
                )

            if secondary_examination:  # If record exists, update it
                secondary_examination.heent = heent
                secondary_examination.cns = cns
                secondary_examination.normal_cns = normal_cns
                secondary_examination.abnormal_cns = abnormal_cns
                secondary_examination.cvs = cvs
                secondary_examination.normal_cvs = normal_cvs
                secondary_examination.abnormal_cvs = abnormal_cvs
                secondary_examination.rs = rs
                secondary_examination.normal_rs = normal_rs
                secondary_examination.abnormal_rs = abnormal_rs
                secondary_examination.pa = pa
                secondary_examination.normal_pa = normal_pa
                secondary_examination.abnormal_pa = abnormal_pa
                secondary_examination.gu = gu
                secondary_examination.normal_gu = normal_gu
                secondary_examination.abnormal_gu = abnormal_gu
                secondary_examination.mss = mss
                secondary_examination.normal_mss = normal_mss
                secondary_examination.abnormal_mss = abnormal_mss
                secondary_examination.save()
            else:
                existing_record = ClinicSecondaryPhysicalExamination.objects.filter(patient_id=patient_id, visit_id=visit_id).first()
                if existing_record:
                    messages.error(request, f'A record already exists for this patient on the specified visit')
                    return render(request, 'doctor_template/add_consultation_notes.html', context)
                # If record doesn't exist, create a new one
                ClinicSecondaryPhysicalExamination.objects.create(
                    patient_id=patient_id,
                    visit_id=visit_id,
                    heent=heent,
                    cns=cns,
                    normal_cns=normal_cns,
                    abnormal_cns=abnormal_cns,
                    cvs=cvs,
                    normal_cvs=normal_cvs,
                    abnormal_cvs=abnormal_cvs,
                    rs=rs,
                    normal_rs=normal_rs,
                    abnormal_rs=abnormal_rs,
                    pa=pa,
                    normal_pa=normal_pa,
                    abnormal_pa=abnormal_pa,
                    gu=gu,
                    normal_gu=normal_gu,
                    abnormal_gu=abnormal_gu,
                    mss=mss,
                    normal_mss=normal_mss,
                    abnormal_mss=abnormal_mss
                )             
            

           
            if consultation_note:
                consultation_note.nature_of_current_illness = nature_of_current_illness                
                consultation_note.type_of_illness = type_of_illness                
                consultation_note.history_of_presenting_illness = history_of_presenting_illness                
                consultation_note.doctor_plan = doctor_plan  
                consultation_note.save()            
                consultation_note.pathology.set(pathology)
                try:
                    consultation_note.save()
                except Exception as e:
                    print("Error saving consultation note:", e)
            else:
                existing_record = ConsultationNotes.objects.filter(patient_id=patient_id, visit_id=visit_id).first()
                if existing_record:
                    messages.error(request, f'A record already exists for this patient on the specified visit')
                    return render(request, 'doctor_template/add_consultation_notes.html', context)
                consultation_note = ConsultationNotes()
                consultation_note.doctor = doctor
                consultation_note.patient = patient
                consultation_note.visit = visit
                consultation_note.type_of_illness = type_of_illness             
                consultation_note.nature_of_current_illness = nature_of_current_illness             
                consultation_note.history_of_presenting_illness = history_of_presenting_illness             
                consultation_note.doctor_plan = doctor_plan   
                consultation_note.save()             
                consultation_note.pathology.set(pathology)
                consultation_note.save()
            messages.success(request, 'record added   successfully.')    
            return redirect(reverse('doctor_save_remotesconsultation_notes_next', args=[patient_id, visit_id]))
            # Add similar logic for other plans
            
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            # Return an appropriate response or render a template with an error message
            return render(request, 'doctor_template/add_consultation_notes.html', context)
    else:
        # If GET request, render the template for adding consultation notes
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
                return redirect(reverse('doctor_save_laboratory', args=[patient_id, visit_id]))
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
        return redirect(reverse('doctor_counseling_list'))
   
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
                return redirect(reverse('doctor_discharge_notes_list'))  # Redirect to the next view
            else:
                messages.error(request, 'Please correct the errors in the form.')
        else:
            form = DischargesNotesForm(instance=remote_discharges_notes)        
        # Prepare context for rendering the template
        context['form'] = form
        return render(request, 'doctor_template/disrcharge_template.html', context)    
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return render(request, 'doctor_template/disrcharge_template.html', context)

@login_required
def save_remotereferral(request, patient_id, visit_id):
    try:
        # Retrieve patient and visit objects
        patient = get_object_or_404(Patients, id=patient_id)
        visit = get_object_or_404(PatientVisits, id=visit_id)
        data_recorder = request.user.staff
        referral = Referral.objects.filter(patient=patient, visit=visit).first()
        context = {'patient': patient, 'visit': visit, 'referral': referral}

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
                    return redirect(reverse('doctor_manage_referral'))
                except Exception as e:
                    messages.error(request, f'Error saving referral: {str(e)}')
            else:
                # Add form errors to messages
                form_errors = form.errors.as_json()
                messages.error(request, f'Form validation errors: {form_errors}')
                print(form.errors)  # Print errors to console/log for debugging
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
                return redirect(reverse('doctor_observation_record_list'))
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
        # Retrieve visit history for the specified patient
        try:
            visit_history = PatientVisits.objects.get(id=visit_id, patient_id=patient_id)
        except PatientVisits.DoesNotExist:
            visit_history = None

        prescriptions = Prescription.objects.filter(patient=patient_id, visit=visit_id)

        try:
            procedures = Procedure.objects.filter(patient=patient_id, visit=visit_id)
        except Procedure.DoesNotExist:
            procedures = None

        total_price = sum(prescription.total_price for prescription in prescriptions)

        patient = Patients.objects.get(id=patient_id)

        # Fetching services based on coverage and type
        if patient.payment_form == 'insurance':
            # If patient's payment form is insurance, fetch services with matching coverage
            remote_service = Service.objects.filter(
                Q(type_service='procedure') & Q(coverage=patient.payment_form)
            )
        else:
            # If payment form is cash, fetch all services of type procedure
            remote_service = Service.objects.filter(type_service='procedure')

        # Calculate total amount from all procedures
        total_procedure_cost = Procedure.objects.filter(patient=patient_id, visit=visit_id).aggregate(Sum('cost'))['cost__sum']

        return render(request, 'doctor_template/procedure_template.html', {
            'visit_history': visit_history,
            'patient': patient,
            'prescriptions': prescriptions,
            'total_price': total_price,
            'procedures': procedures,
            'remote_service': remote_service,
            'total_procedure_cost': total_procedure_cost,
        })
    except Exception as e:
        # Handle other exceptions if necessary
        return render(request, '404.html', {'error_message': str(e)})
    
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
        print(remote_service)
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
            # Extract data from the request
            patient_id = request.POST.get('patient_id')
            visit_id = request.POST.get('visit_id')
            medicines = request.POST.getlist('medicine[]')
            doses = request.POST.getlist('dose[]')
            frequencies = request.POST.getlist('frequency[]')
            durations = request.POST.getlist('duration[]')
            quantities = request.POST.getlist('quantity[]')
            total_price = request.POST.getlist('total_price[]')
            entered_by = request.user.staff

            # Retrieve the corresponding patient and visit
            patient = Patients.objects.get(id=patient_id)
            visit = PatientVisits.objects.get(id=visit_id)

            # Save prescriptions only if inventory check passes
            for i in range(len(medicines)):
                medicine = Medicine.objects.get(id=medicines[i])
                quantity_used_str = quantities[i]  # Get the quantity as a string

                if quantity_used_str is None:
                    raise ValueError(f'Invalid quantity for {medicine.drug_name}. Quantity cannot be empty.')

                try:
                    quantity_used = int(quantity_used_str)
                except ValueError:
                    raise ValueError(f'Invalid quantity for {medicine.drug_name}. Quantity must be a valid number.')

                if quantity_used < 0:
                    raise ValueError(f'Invalid quantity for {medicine.drug_name}. Quantity must be a non-negative number.')

                # Retrieve the remaining quantity of the medicine
                remain_quantity = medicine.remain_quantity

                if remain_quantity is not None and quantity_used > remain_quantity:
                    raise ValueError(f'Insufficient stock for {medicine.drug_name}. Only {remain_quantity} available.')

                # Reduce the remain quantity of the medicine
                if remain_quantity is not None:
                    medicine.remain_quantity -= quantity_used
                    medicine.save()

                # Save prescription
                Prescription.objects.create(
                    patient=patient,
                    medicine=medicine,
                    entered_by=entered_by,
                    visit=visit,
                    dose=doses[i],
                    frequency=PrescriptionFrequency.objects.get(id=frequencies[i]),
                    duration=durations[i],
                    quantity_used=quantity_used,
                    total_price=total_price[i]
                )

            return JsonResponse({'status': 'success', 'message': 'Prescription saved.'})
    except ValueError as ve:
        return JsonResponse({'status': 'error', 'message': str(ve)})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred: ' + str(e)})
    
@login_required         
def save_prescription(request, patient_id, visit_id):
    try:
        # Retrieve visit history for the specified patient
        visit = PatientVisits.objects.get(id=visit_id)   
        frequencies = PrescriptionFrequency.objects.all()       
        prescriptions = Prescription.objects.filter(patient=patient_id, visit_id=visit_id)        
        current_date = timezone.now().date()
        patient = Patients.objects.get(id=patient_id)    
        total_price = sum(prescription.total_price for prescription in prescriptions)  
        medicines = Medicine.objects.filter(
            remain_quantity__gt=0,  # Inventory level greater than zero
            expiration_date__gt=current_date  # Not expired
        ).distinct()
        range_31 = range(31)
        return render(request, 'doctor_template/prescription_template.html', {           
            'patient': patient,
            'visit': visit,       
            'medicines': medicines,
            'total_price': total_price,
            'range_31': range_31,
            'prescriptions': prescriptions,
            'frequencies': frequencies,
         
        })
    except Exception as e:
        # Handle other exceptions if necessary
        return render(request, '404.html', {'error_message': str(e)}) 
    

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
            dividable = medicine.dividable
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
        return render(request, 'doctor_template/add_radiology.html', {
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
        # Retrieve visit history for the specified patient
        doctor = request.user.staff
        try:
            visit_history = PatientVisits.objects.get(id=visit_id, patient_id=patient_id)
        except PatientVisits.DoesNotExist:
            visit_history = None
        try:
            Investigation = LaboratoryOrder.objects.filter(patient_id=patient_id, visit_id=visit_id,doctor_id=doctor)
        except LaboratoryOrder.DoesNotExist:
            Investigation = None

        prescriptions = Prescription.objects.filter(patient=patient_id, visit=visit_id)
        consultation_notes = PatientDiagnosisRecord.objects.filter(patient=patient_id, visit=visit_id)
        try:
            procedures = Procedure.objects.filter(patient=patient_id, visit=visit_id, doctor_id=doctor)
        except Procedure.DoesNotExist:
            procedures = None

        total_price = sum(prescription.total_price for prescription in prescriptions)
        doctors = Staffs.objects.filter(role='labTechnician',work_place="resa")
        patient = Patients.objects.get(id=patient_id)

        # Fetching services based on coverage and type
        if patient.payment_form == 'insurance':
            # If patient's payment form is insurance, fetch services with matching coverage
            remote_service = Service.objects.filter(
                Q(type_service='Laboratory') & Q(coverage=patient.payment_form)
            )
        else:
            # If payment form is cash, fetch all services of type procedure
            remote_service = Service.objects.filter(type_service='Laboratory')

        # Calculate total amount from all procedures
        total_procedure_cost = procedures.aggregate(Sum('cost'))['cost__sum']
        total_imaging_cost = Investigation.aggregate(Sum('cost'))['cost__sum']
        return render(request, 'doctor_template/laboratory_template.html', {
            'visit_history': visit_history,
            'patient': patient,
            'prescriptions': prescriptions,
            'total_price': total_price,
            'Investigation': Investigation,
            'procedures': procedures,
            'doctors': doctors,
            'remote_service': remote_service,
            'total_procedure_cost': total_procedure_cost,
            'total_imaging_cost': total_imaging_cost,
            'consultation_notes': consultation_notes,
        })
    except Exception as e:
        # Handle other exceptions if necessary
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
                    name_id=investigation_names[i],
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
def patient_health_record_view(request, patient_id, visit_id):
    try:
        # Retrieve visit history for the specified patient     
        visit = PatientVisits.objects.get(id=visit_id,patient_id=patient_id)        
        prescriptions = Prescription.objects.filter(patient=patient_id, visit=visit_id)
        try:
            consultation_notes = PatientDiagnosisRecord.objects.filter(patient_id=patient_id, visit=visit_id).order_by('-created_at').first()
        except PatientDiagnosisRecord.DoesNotExist:
            consultation_notes = None         
        try:
            vitals = PatientVital.objects.filter(patient=patient_id,visit=visit_id).order_by('-recorded_at')
        except PatientVital.DoesNotExist:
            vitals = None           
        try:
            procedures = Procedure.objects.filter(patient=patient_id, visit=visit_id)            
        except Procedure.DoesNotExist:
            procedures = None          
        try:
            lab_tests = LaboratoryOrder.objects.filter(patient=patient_id, visit=visit_id)
        except LaboratoryOrder.DoesNotExist:
            lab_tests = None  
        total_price = sum(prescription.total_price for prescription in prescriptions)   
        patient = Patients.objects.get(id=patient_id)
           # Calculate total amount from all procedures
        try:
            imaging_records = ImagingRecord.objects.filter(patient_id=patient_id, visit_id=visit_id)
        except ImagingRecord.DoesNotExist:
            imaging_records = None
               
        total_procedure_cost = procedures.aggregate(Sum('cost'))['cost__sum']
        total_imaging_cost = imaging_records.aggregate(Sum('cost'))['cost__sum']
        lab_tests_cost = lab_tests.aggregate(Sum('cost'))['cost__sum']   
    
        return render(request, 'doctor_template/manage_patient_health_record.html', {
           
            'patient': patient,
            'visit': visit,          
            'lab_tests_cost': lab_tests_cost,
            'total_procedure_cost': total_procedure_cost,
            'total_imaging_cost': total_imaging_cost,
            'prescriptions': prescriptions,
            'total_price': total_price,
            'consultation_notes': consultation_notes,      
            'vitals': vitals,          
            'imaging_records': imaging_records,          
            'lab_tests': lab_tests,
            'procedures': procedures,
      
        })
    except Exception as e:
        # Handle other exceptions if necessary
        return render(request, '404.html', {'error_message': str(e)})
    


@login_required
def prescription_list(request):
    
    # Retrieve all prescriptions with related patient and visit
    prescriptions = Prescription.objects.select_related('patient', 'visit')

    visit_total_prices = prescriptions.values(
    'visit__vst', 
    'visit__patient__first_name',
    'visit__created_at', 
    'visit__patient__id', 
    'visit__patient__middle_name', 
    'visit__patient__last_name'
).annotate(
    total_price=Sum('total_price'),
    verified=F('verified'), 
    issued=F('issued'),      
    status=F('status'),    
)

    
    # Calculate total price of all prescriptions
    total_price = sum(prescription.total_price for prescription in prescriptions) 
    
    return render(request, 'doctor_template/manage_prescription_list.html', {     
        'total_price': total_price,
        'visit_total_prices': visit_total_prices,
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
def patient_vital_list(request, patient_id):
    # Retrieve the patient object
    patient = Patients.objects.get(pk=patient_id)  
    patient_vitals = PatientVital.objects.filter(patient=patient).order_by('-recorded_at')

    # Render the template with the patient's vital information
    context = {  
        'patient': patient, 
        'patient_vitals': patient_vitals
    }
    
    return render(request, 'doctor_template/manage_patient_vital_list.html', context) 

@login_required   
def patient_vital_all_list(request):
    # Retrieve the patient object
    patients = Patients.objects.all()   
    # Retrieve all vital information for the patient
    patient_vitals = PatientVital.objects.all().order_by('-recorded_at')    
    context = {       
        'patients': patients, 
        'patient_vitals': patient_vitals
    }
    # Render the template with the patient's vital information
    return render(request, 'doctor_template/manage_all_patient_vital.html', context)  
  

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
    # Retrieve the current logged-in doctor
    current_doctor = request.user.staff    
    # Retrieve all ConsultationOrder instances for the current doctor
    consultation_orders = ConsultationOrder.objects.filter(doctor=current_doctor).order_by('-order_date')     
    # Retrieve all related orders for the ConsultationOrder instances
    orders = Order.objects.filter(order_type__in=[consultation.consultation.name for consultation in consultation_orders], is_read=True)    
    # Render the template with the fetched orders
    return render(request, 'doctor_template/manage_consultation_notes.html', {'orders': orders})

@login_required
def new_consultation_order(request):   
    # Retrieve the current logged-in doctor
    current_doctor = request.user.staff   
    current_date = timezone.now().date() 
    # Retrieve all ConsultationOrder instances for the current doctor
    consultation_orders = ConsultationOrder.objects.filter(doctor=current_doctor).order_by('-order_date')     
    # Retrieve all unread orders for the ConsultationOrder instances
    unread_orders = Order.objects.filter(order_type__in=[consultation.consultation.name for consultation in consultation_orders],  order_date=current_date)    
    # Mark the retrieved unread orders as read
    orders = unread_orders 
    unread_orders.update(is_read=True)    
    # Render the template with the fetched unread orders
    return render(request, 'doctor_template/new_consultation_order.html', {'orders': orders})


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
    template_name = 'doctor_template/manage_procedure.html'
    doctor = request.user.staff
    # Query to retrieve the latest procedure record for each patient
    procedures = Procedure.objects.filter(doctor=doctor).order_by('-order_date')  
    form = ProcedureForm()    
    return render(request, template_name, {'procedures': procedures,'form':form})

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
    doctor = request.user.staff
    # Query to retrieve the latest procedure record for each patient
    procedures = LaboratoryOrder.objects.filter(data_recorder=doctor).order_by('-order_date')      
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
    unread_orders = Order.objects.filter(order_type__in=[procedure.name.name for procedure in procedures],  order_date=current_date)    
    orders = unread_orders 
    unread_orders.update(is_read=True)         
    return render(request, template_name, {'orders': orders})
    



def counseling_list_view(request):
    counselings = Counseling.objects.all().order_by('-created_at')
    return render(request, 'doctor_template/manage_counselling.html', {'counselings': counselings})    

def observation_record_list_view(request):
    observation_records = ObservationRecord.objects.all().order_by('-created_at')
    return render(request, 'doctor_template/manage_observation_record.html', {'observation_records': observation_records})

def discharge_notes_list_view(request):
    discharge_notes = DischargesNotes.objects.all().order_by('-discharge_date')
    return render(request, 'doctor_template/manage_discharge.html', {'discharge_notes': discharge_notes})

    
@login_required
def manage_disease(request):
    disease_records=DiseaseRecode.objects.all() 
    return render(request,"doctor_template/manage_disease.html",{"disease_records":disease_records})

@login_required    
def diagnosis_list(request):
    diagnoses = Diagnosis.objects.all().order_by('-created_at')    
    return render(request, 'doctor_template/manage_diagnosis_list.html', {'diagnoses': diagnoses}) 

@login_required
def manage_service(request):
    services=Service.objects.all()
    insurance_companies=InsuranceCompany.objects.all()
    context = {
        'services':services,
        'insurance_companies':insurance_companies,
    }
    return render(request,"doctor_template/manage_service.html",context)

@login_required
def manage_pathodology(request):
    pathodology_records=PathodologyRecord.objects.all()    
    return render(request,"doctor_template/manage_pathodology.html",{
        "pathodology_records":pathodology_records,        
        })

@login_required
def medicine_list(request):    
    medicines = Medicine.objects.all()
    # Render the template with medicine data and notifications
    return render(request, 'doctor_template/manage_medicine.html', {'medicines': medicines})

@login_required 
def reagent_list(request):
    reagent_list = Reagent.objects.all()
    return render(request, 'doctor_template/manage_reagent_list.html', {'reagent_list': reagent_list})  

@login_required
def health_record_list(request):
    records = HealthRecord.objects.all()
    return render(request, 'doctor_template/healthrecord_list.html', {'records': records})

@login_required
def patient_detail(request, patient_id):
    # Retrieve the patient object using the patient_id
    patient = get_object_or_404(Patients, id=patient_id)
    
    # Context to be passed to the template
    context = {
        'patient': patient,
    }
    
    # Render the patient_detail template with the context
    return render(request, 'doctor_template/patient_detail.html', context)



@login_required
def patient_detail(request, patient_id):
    # Retrieve the patient object using the patient_id
    patient = get_object_or_404(Patients, id=patient_id)    
    # Context to be passed to the template
    context = {
        'patient': patient,
    }    
    # Render the patient_detail template with the context
    return render(request, 'doctor_template/patient_detail.html', context)  

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

@login_required
def patient_visit_details_view(request, patient_id, visit_id):
    try:        
        visit = PatientVisits.objects.get(id=visit_id)
        prescriptions = Prescription.objects.filter(patient=patient_id, visit=visit_id)
        chief_complaints = ClinicChiefComplaint.objects.filter(patient_id=patient_id, visit_id=visit_id)
        primary_physical_examination = ClinicPrimaryPhysicalExamination.objects.filter(patient_id=patient_id, visit_id=visit_id).first()
        secondary_physical_examination = ClinicSecondaryPhysicalExamination.objects.filter(patient=patient_id, visit=visit_id).first()
        consultation_notes = ConsultationNotes.objects.filter(patient_id=patient_id, visit=visit_id).order_by('-created_at').first()
        vitals = PatientVital.objects.filter(patient=patient_id, visit=visit_id).order_by('-recorded_at')
        referral_records  = Referral.objects.filter(patient=patient_id, visit=visit_id).order_by('-created_at')
        counseling_records = Counseling.objects.filter(patient=patient_id, visit=visit_id).order_by('-created_at')        
        procedures = Procedure.objects.filter(patient=patient_id, visit=visit_id)
        imaging_records = ImagingRecord.objects.filter(patient=patient_id, visit=visit_id)
        discharge_notes = DischargesNotes.objects.filter(patient=patient_id, visit=visit_id)
        observation_records = ObservationRecord.objects.filter(patient=patient_id, visit=visit_id)
        lab_tests = LaboratoryOrder.objects.filter(patient=patient_id, visit=visit_id)
        procedure = Procedure.objects.filter(patient=patient_id, visit=visit_id).first()    
        diagnosis_record = PatientDiagnosisRecord.objects.filter(patient_id=patient_id, visit_id=visit_id).first()
        patient = get_object_or_404(Patients, id=patient_id)

        context = {
            'primary_physical_examination': primary_physical_examination,
            'secondary_physical_examination': secondary_physical_examination,
            'visit': visit,
            'counseling_records': counseling_records,
            'observation_records': observation_records,
            'patient': patient,
            'referral_records ': referral_records ,
            'chief_complaints': chief_complaints,              
            'prescriptions': prescriptions,           
            'consultation_notes': consultation_notes,     
            'diagnosis_record': diagnosis_record,            
            'vitals': vitals,     
            'lab_tests': lab_tests,
            'procedures': procedures,
            'procedure': procedure,
            'imaging_records': imaging_records,
            'discharge_notes': discharge_notes,
        }

        return render(request, 'doctor_template/manage_patient_visit_detail_record.html', context)
    except Patients.DoesNotExist:
        raise Http404("Patient does not exist")
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)})

     






