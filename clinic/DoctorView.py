from datetime import  datetime
from django.utils import timezone
import logging
from django.urls import reverse
from django.db.models import F
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.http import  HttpResponseBadRequest
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Sum
from django.db.models import Q
from clinic.forms import ImagingRecordForm, LaboratoryOrderForm, ProcedureForm
from django.core.exceptions import ValidationError
from clinic.models import  Consultation,  DiseaseRecode, Medicine, Notification,  PathodologyRecord, Patients, Procedure, Staffs
from django.views.decorators.http import require_POST
from django.contrib.contenttypes.models import ContentType
from .models import ConsultationFee, ConsultationNotes, ConsultationNotification, ConsultationOrder, Counseling, Country, Diagnosis,Diagnosis,HealthIssue, ImagingRecord, InventoryItem,LaboratoryOrder, Order, PatientVisits, PatientVital, Prescription, PrescriptionFrequency, Procedure, Patients, Referral,Service
from django.views.decorators.http import require_GET

@login_required
def doctor_dashboard(request):
    # Fetch the currently logged-in staff or doctor
    current_doctor = request.user.staff
    # Total number of consultations for the current doctor
    total_consultations = Consultation.objects.filter(doctor=current_doctor).count()
    # Number of patients appointed to the current doctor
    patients_appointed = Patients.objects.filter(consultation__doctor=current_doctor).distinct().count()
    # Other data you may want to fetch
    total_patients = Patients.objects.count()
    recently_added_patients = Patients.objects.order_by('-created_at')[:6]
    doctors = Staffs.objects.filter(role='doctor')

    context = {
        'total_patients': total_patients,
        'recently_added_patients': recently_added_patients,
        'doctors': doctors,
        'total_consultations': total_consultations,
        'patients_appointed': patients_appointed,
        # Add other context data as needed
    }
    return render(request, "doctor_template/home_content.html", context)



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

@login_required
def appointment_view(request, patient_id):
    try:
        if request.method == 'POST':
            # Extract data from the request
            doctor_id = request.POST.get('doctor')
            date_of_consultation = request.POST.get('date_of_consultation')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            description = request.POST.get('description')

            # Create a Consultation instance
            doctor = get_object_or_404(Staffs, id=doctor_id)
            patient = get_object_or_404(Patients, id=patient_id)
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
            notification_message = f"New appointment scheduled with Dr. { doctor.admin.first_name } { doctor.middle_name } { doctor.admin.last_name } on {date_of_consultation} from {start_time} to {end_time}."
            Notification.objects.create(
                content_type=ContentType.objects.get_for_model(Patients),
                object_id=patient.id,
                message=notification_message
            )

            messages.success(request, "Appointment created successfully.")
            return redirect('appointment_view', patient_id=patient_id)

        # If the request is not a POST, handle the GET request
        patient = get_object_or_404(Patients, id=patient_id)
        doctors = Staffs.objects.filter(role='doctor')

        context = {
            'patient': patient,
            'doctors': doctors,
        }

        return render(request, "doctor_template/add_consultation.html", context)

    except IntegrityError as e:
        # Handle integrity error (e.g., duplicate entry)
        messages.error(request, f"Error creating appointment: {str(e)}")
        return redirect('appointment_view', patient_id=patient_id)
    except Exception as e:
        # Handle other exceptions
        messages.error(request, f"An unexpected error occurred: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)})
    
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


@login_required    
def notification_view(request):
    notifications = Notification.objects.filter(is_read=False)
    
    # Mark notifications as read when the user accesses them
    for notification in notifications:
        notification.is_read = True
        notification.save()
    
    context = {'notifications': notifications}
    return render(request, 'doctor_template/manage_notification.html', context)


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

    return redirect('read_appointments')  # Adjust the URL name based on your actual URL structure

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

            messages.success(request, f"Meeting time for {appointment.patient.fullname} edited successfully.")
    except Exception as e:
        messages.error(request, f"Error editing meeting time: {str(e)}")

    return redirect('appointment_list')

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
def save_referral(request):
    if request.method == 'POST':
        try:
            referral_id = request.POST.get('referral_id')  # Check if referral ID is provided
            visit_id = request.POST.get('visit_id')
            patient_id = request.POST.get('patient_id')      
            destination_location = request.POST.get('destination_location')
            reason = request.POST.get('reason')
            doctor = request.user.staff 

            if referral_id:  # If referral ID is provided, update existing referral record
                referral_record = Referral.objects.get(id=referral_id)
                referral_record.destination_location = destination_location
                referral_record.reason = reason
                referral_record.save()
                return JsonResponse({'success': True, 'message': f'{referral_record} updated successfully.'})
            else:  # If no referral ID is provided, create a new referral record
                referral_record = Referral.objects.create(
                    patient_id=patient_id,
                    visit_id=visit_id,
                    doctor=doctor,
                    destination_location=destination_location,
                    reason=reason,
                )
                return JsonResponse({'success': True, 'message': f'{referral_record} saved successfully.'})
        except Patients.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid patient ID.'})
        except Referral.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid referral ID.'})
        except IntegrityError:
            return JsonResponse({'success': False, 'message': 'Duplicate entry. Referral record not saved.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {e}'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


@csrf_exempt
def save_counseling(request):
    if request.method == 'POST':
        try:
            counsel_id = request.POST.get('counsel_id')  # Check if referral ID is provided
            visit_id = request.POST.get('visit_id')
            patient_id = request.POST.get('patient_id')      
            counseling_topic = request.POST.get('counseling_topic')      
            counseling_description = request.POST.get('counseling_description')            
            counselor = request.user.staff 

            if counsel_id:  # If referral ID is provided, update existing referral record
                counseling_record = Counseling.objects.get(id=counsel_id)
                counseling_record.counseling_topic = counseling_topic              
                counseling_record.counseling_description = counseling_description              
                counseling_record.save()
                return JsonResponse({'success': True, 'message': f'{counseling_record} updated successfully.'})
            else:  # If no referral ID is provided, create a new referral record
                counseling_record = Counseling.objects.create(
                    patient_id=patient_id,
                    visit_id=visit_id,
                    counselor=counselor,
                    topic=counseling_topic,
                    description=counseling_description,
               
                )
                return JsonResponse({'success': True, 'message': f'{counseling_record} saved successfully.'})
        except Patients.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid patient ID.'})
        except Counseling.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid referral ID.'})
        except IntegrityError:
            return JsonResponse({'success': False, 'message': 'Duplicate entry. Counseling record not saved.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {e}'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


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
    unread_notification_count = Notification.objects.filter(is_read=False).count()
    patients=Patients.objects.all() 
    pathology_records=PathodologyRecord.objects.all() 
    doctors=Staffs.objects.filter(role='doctor')
    context = {
        'patients':patients,
        'pathology_records':pathology_records,
        'doctors':doctors,
        'unread_notification_count':unread_notification_count,
        'appointments':appointments,
    }
    return render(request, 'doctor_template/manage_appointment.html', context)


@login_required
def fetch_consultation_counts(request):
    # Get the currently logged-in doctor staff
    doctor = request.user.staff  # Assuming user has a profile linked with Staffs model

    # Get the counts of unread and read consultations for the current doctor
    unread_count = ConsultationNotification.objects.filter(doctor=doctor, is_read=False).count()
    read_count = ConsultationNotification.objects.filter(doctor=doctor, is_read=True).count()

    # Return the counts as JSON response
    return JsonResponse({'unreadCount': unread_count, 'readCount': read_count})

@login_required
def unread_appointments_view(request):
    doctor = request.user.staff
    # Fetching all unread consultations associated with the doctor
    unread_notifications = ConsultationNotification.objects.filter(doctor=doctor, is_read=False)
    unread_appointments = [notification.consultation for notification in unread_notifications]
    
    # Update the notifications as read once the user opens them
    for notification in unread_notifications:
        notification.is_read = True
        notification.save()
    
    return render(request, 'doctor_template/unread_appointments.html', {'appointments': unread_appointments})

@login_required
def read_appointments_view(request):
    doctor = request.user.staff
    # Fetching all read consultations associated with the doctor
    read_notifications = ConsultationNotification.objects.filter(doctor=doctor, is_read=True)
    read_appointments = [notification.consultation for notification in read_notifications]
    
    return render(request, 'doctor_template/read_appointments.html', {'appointments': read_appointments})

@csrf_exempt
@login_required
def add_pathodology_record(request):
    try:
        if request.method == 'POST':
            name = request.POST.get('Name')
            description = request.POST.get('Description')
            related_diseases_ids = request.POST.getlist('RelatedDiseases')

            # Save data to the model
            pathodology_record = PathodologyRecord.objects.create(
                name=name,
                description=description
            )

            # Add related diseases
            for disease_id in related_diseases_ids:
                disease = DiseaseRecode.objects.get(pk=disease_id)
                pathodology_record.related_diseases.add(disease)

            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid request method'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    
@csrf_exempt
def save_edited_patient(request):
    if request.method == 'POST':
        try:
            # Extract the form data
            patient_id = request.POST.get('patient_id')
            edited_patient = Patients.objects.get(id=patient_id)
            edited_patient.first_name = request.POST.get('edit_first_name')
            edited_patient.middle_name = request.POST.get('edit_middle_name')
            edited_patient.last_name = request.POST.get('edit_last_name')
            edited_patient.gender = request.POST.get('edit_gender')
            if not request.POST.get('edit_age'):
                edited_patient.age = None
            else:
                edited_patient.age = int(request.POST.get('edit_age'))
            
            if not request.POST.get('edit_dob'):
                edited_patient.dob = None
            else:
                edited_patient.dob = request.POST.get('edit_dob')               
            edited_patient.phone = request.POST.get('edit_phone')
            edited_patient.address = request.POST.get('edit_Address')
            edited_patient.nationality_id = request.POST.get('edit_nationality')
            edited_patient.payment_form = request.POST.get('edit_payment_type')
            if request.POST.get('edit_payment_type') == 'insurance':
                edited_patient.insurance_name = request.POST.get('insurance_name')
                edited_patient.insurance_number = request.POST.get('edit_insurance_number')           
            
            edited_patient.emergency_contact_name = request.POST.get('edit_emergency_contact_name')
            edited_patient.emergency_contact_relation = request.POST.get('edit_emergency_contact_relation')
            edited_patient.emergency_contact_phone = request.POST.get('edit_emergency_contact_phone')
            edited_patient.marital_status = request.POST.get('marital_status')
            edited_patient.patient_type = request.POST.get('edit_patient_type')

            # Save the edited patient
            edited_patient.save()

            # Return JSON response for success
            return JsonResponse({'message': 'Patient data updated successfully.'})
        except Exception as e:
            # Return JSON response for error
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)
    
@csrf_exempt
def add_patient(request):
    try:
        if request.method == 'POST':
            # Extract data from the request
            first_name = request.POST.get('first_name')
            middle_name = request.POST.get('middle_name')
            last_name = request.POST.get('last_name')
            emergency_contact_name = request.POST.get('emergency_contact_name')
            emergency_contact_relation = request.POST.get('emergency_contact_relation')         
            emergency_contact_phone = request.POST.get('emergency_contact_phone')
            nationality_id = request.POST.get('nationality')            
            dob = request.POST.get('dob')
            gender = request.POST.get('gender')
            phone = request.POST.get('phone')
            address = request.POST.get('Address')                       
            marital_status = request.POST.get('maritalStatus')
            patient_type = request.POST.get('patient_type')
            payment_type = request.POST.get('payment_type')
            insurance_name = request.POST.get('insurance_name')
            insurance_number = request.POST.get('insurance_number')
            age = request.POST.get('age')
            if not dob:
                dob = None
            if not age:
                age = None

            # Generate the medical record number (mrn)
            mrn = generate_mrn()

            # Create an instance of the Patient model
            patient_instance = Patients(
                mrn=mrn,
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,             
                dob=dob,
                age=age,
                gender=gender,
                phone=phone,
                address=address,
                emergency_contact_name=emergency_contact_name,
                emergency_contact_relation=emergency_contact_relation,                
                emergency_contact_phone=emergency_contact_phone,
                nationality_id=nationality_id,                
                marital_status=marital_status,
                patient_type=patient_type,
                payment_form=payment_type,
            )

            # If payment type is insurance, save insurance details
            if payment_type == 'insurance':
                patient_instance.insurance_name = insurance_name
                patient_instance.insurance_number = insurance_number
               

            # Save the instance to the database
            patient_instance.save()

            # Return a JsonResponse with a success message
            return JsonResponse({'message': 'Patient added successfully'}, status=200)

    except Exception as e:
        # Log or print the error for tracking
        logger.error(f"Error adding patient: {str(e)}")

    # Return an error response if there's an exception or if the request method is not POST
    return JsonResponse({'error': 'Failed to add patient'}, status=500)

def generate_mrn():
    # Retrieve the last patient's MRN from the database
    last_patient = Patients.objects.last()

    # Extract the numeric part from the last MRN, or start from 0 if there are no patients yet
    last_mrn_number = int(last_patient.mrn.split('-')[-1]) if last_patient else 0

    # Increment the numeric part for the new patient
    new_mrn_number = last_mrn_number + 1

    # Format the MRN with leading zeros and concatenate with the prefix "PAT-"
    new_mrn = f"RES-{new_mrn_number:07d}"

    return new_mrn









@require_POST
def save_consultation_data(request):
    try:
        # Retrieve data from the form
        doctor_id = request.POST.get('doctor')
        patient_id = request.POST.get('patient')
        appointment_date = request.POST.get('appointmentDate')
        start_time = request.POST.get('startTime')
        end_time = request.POST.get('endTime')
        description = request.POST.get('description')        
        pathodology_record_id = request.POST.get('pathodologyRecord')

        # Convert date and time strings to datetime objects
        # appointment_datetime = datetime.combine(datetime.strptime(appointment_date, '%Y-%m-%d').date(), datetime.strptime(start_time, '%H:%M').time())
        # end_datetime = datetime.combine(datetime.strptime(appointment_date, '%Y-%m-%d').date(), datetime.strptime(end_time, '%H:%M').time())

        # Create or update Consultation object
        consultation, created = Consultation.objects.update_or_create(
            doctor=Staffs.objects.get(id=doctor_id),
            patient=Patients.objects.get(id=patient_id),
            appointment_date=appointment_date,
            start_time=start_time,
            end_time=end_time,
            description=description,
            pathodology_record= PathodologyRecord.objects.get(id=pathodology_record_id),
            
        )

        return redirect('appointment_list')
    except Exception as e:
        return HttpResponseBadRequest(f"Error: {str(e)}")

@login_required
def consultation_fee_list(request):
    # Get distinct patients who have consultations
    patients = Patients.objects.filter(consultation__isnull=False).distinct()

    # Get distinct doctors who have consultations
    doctors = Staffs.objects.filter(consultation__isnull=False).distinct()

    # Get all consultation fees
    consultation_fees = ConsultationFee.objects.all()

    # Get all consultations
    consultations = Consultation.objects.all()

    return render(request, 'doctor_template/manage_consultation_fee_list.html', {
        'consultation_fees': consultation_fees,
        'patients': patients,
        'doctors': doctors,
        'consultations': consultations,
    })

@require_POST
def save_consultation_fee(request):
    try:
        # Extract form data from the request
        doctor_id = request.POST.get('doctor')
        patient_id = request.POST.get('patient')
        fee_amount = request.POST.get('feeAmount')
        consultation_id = request.POST.get('consultation')

        # Create ConsultationFee instance
        consultation_fee = ConsultationFee.objects.create(
            doctor=Staffs.objects.get(id=doctor_id),
            patient=Patients.objects.get(id=patient_id),
            fee_amount=fee_amount,
            consultation=Consultation.objects.get(id=consultation_id),
        )

        # Return a JsonResponse to indicate success
        return redirect('consultation_fee_list') 
    except Exception as e:
        # Return a JsonResponse with an error message
        return HttpResponseBadRequest(f"Error: {str(e)}")  
    
    




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
    

    
@login_required    
def patient_consultation_detail(request, patient_id, visit_id):
    try:        
        
        prescriptions = Prescription.objects.filter(patient_id=patient_id, visit_id=visit_id)
        try:
            consultation_notes = ConsultationNotes.objects.filter(patient_id=patient_id, visit_id=visit_id).order_by('-created_at').first()
        except ConsultationNotes.DoesNotExist:
            consultation_notes = None
        try:
            vital = PatientVital.objects.get(patient_id=patient_id, visit_id=visit_id)                     
        except PatientVital.DoesNotExist:
            vital = None
        try:
            visit_history = PatientVisits.objects.get(id=visit_id, patient_id=patient_id)                  
        except PatientVisits.DoesNotExist:
            visit_history = None        
        pathology_records = PathodologyRecord.objects.all()  # Fetch all consultation notes from the database        
        provisional_diagnoses = Diagnosis.objects.all()
        final_diagnoses = Diagnosis.objects.all()

        total_price = sum(prescription.total_price for prescription in prescriptions)
        range_31 = range(31)
        current_date = timezone.now().date()
        patient = Patients.objects.get(id=patient_id)
        remote_service = Service.objects.all()
        range_51 = range(51)
        range_301 = range(301)
        range_101 = range(101)
        range_15 = range(3, 16)
        medicines = Medicine.objects.filter(
            medicineinventory__remain_quantity__gt=0,  # Inventory level greater than zero
            expiration_date__gt=current_date  # Not expired
        ).distinct()
        
        return render(request, 'doctor_template/patient_consultation_detail.html', {        
            'patient': patient,           
            'range_31': range_31,
            'medicines': medicines,
            'prescriptions': prescriptions,
            'total_price': total_price,
            'visit_history': visit_history,
            'consultation_notes': consultation_notes,
            'pathology_records': pathology_records,            
            'provisional_diagnoses': provisional_diagnoses,
            'final_diagnoses': final_diagnoses,
            'vital': vital,
            'remote_service': remote_service,
            'range_51': range_51,
            'range_301': range_301,
            'range_101': range_101,
            'range_15': range_15,
        })
    except Exception as e:
        # Handle other exceptions if necessary
        return render(request, '404.html', {'error_message': str(e)})    
    
    
@login_required
def save_remotesconsultation_notes(request, patient_id, visit_id):
    try:
        # Fetch required data from the database
        patient = Patients.objects.get(pk=patient_id)
        visit = PatientVisits.objects.get(id=visit_id)      

        if request.method == 'POST':
            # Retrieve form data
            chief_complaints = request.POST.get('chief_complaints')
            history_of_presenting_illness = request.POST.get('history_of_presenting_illness')            
            physical_examination = request.POST.get('physical_examination')
            allergy_to_medications = request.POST.get('allergy_to_medications')
            doctor_plan = request.POST.get('doctor_plan')
            provisional_diagnosis = request.POST.getlist('provisional_diagnosis[]')
            final_diagnosis = request.POST.getlist('final_diagnosis[]')
            pathology = request.POST.getlist('pathology[]')

            # Get the currently logged-in staff (assuming you are using Django's authentication system)
            doctor = request.user.staff  # Assuming the user model has a foreign key to Staff model
            
            # Check if notes_id is provided for editing existing consultation notes
            notes_id = request.POST.get('notes_id')
            if notes_id:
                # Editing existing consultation notes
                consultation_notes = ConsultationNotes.objects.get(pk=notes_id)
                consultation_notes.chief_complaints = chief_complaints
                consultation_notes.history_of_presenting_illness = history_of_presenting_illness                
                consultation_notes.physical_examination = physical_examination
                consultation_notes.allergy_to_medications = allergy_to_medications
                consultation_notes.doctor_plan = doctor_plan
                consultation_notes.provisional_diagnosis.set(provisional_diagnosis)
                consultation_notes.final_diagnosis.set(final_diagnosis)
                consultation_notes.pathology.set(pathology)
                consultation_notes.save()
                messages.success(request, "consultation notes edited successfully.")  
            else:
                # Adding new consultation notes
                consultation_notes = ConsultationNotes.objects.create(
                    doctor=doctor,
                    patient=patient,
                    visit=visit,
                    chief_complaints=chief_complaints,
                    history_of_presenting_illness=history_of_presenting_illness,                
                    physical_examination=physical_examination,
                    allergy_to_medications=allergy_to_medications,
                    doctor_plan=doctor_plan
                )
                consultation_notes.provisional_diagnosis.set(provisional_diagnosis)
                consultation_notes.final_diagnosis.set(final_diagnosis)
                consultation_notes.pathology.set(pathology)
                messages.success(request, "consultation notes saved successfully.")    
            # Redirect to the appropriate page based on doctor's plan
            redirect_url = {
                'Prescription': reverse('save_prescription', args=[patient_id, visit_id]),
                'Laboratory': reverse('save_laboratory', args=[patient_id, visit_id]),
                'Referral': reverse('patient_consultation_detail', args=[patient_id, visit_id]),
                'Counsel': reverse('patient_consultation_detail', args=[patient_id, visit_id]),
                'Procedure': reverse('save_remoteprocedure', args=[patient_id, visit_id]),
                'Observation': reverse('save_observation', args=[patient_id, visit_id]),
                'Consultation': reverse('patient_consultation_detail', args=[patient_id, visit_id]),
            }
            return redirect(redirect_url.get(doctor_plan, reverse('patient_consultation_detail', args=[patient_id, visit_id])))

    except Exception as e:
        # Handle any exceptions here
        messages.error(request, f'Error adding/editing patient consultation record: {str(e)}')  
        return redirect(reverse('patient_consultation_detail', args=[patient_id, visit_id]))

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
            

@login_required
def save_remotereferral(request, patient_id, visit_id):
    try:
        # Retrieve visit history for the specified patient
        visits = PatientVisits.objects.get(id=visit_id)
        visit_history = PatientVisits.objects.filter(patient_id=patient_id)       
        
        prescriptions = Prescription.objects.filter(patient=patient_id, visit=visit_id)
        try:
            consultation_notes = ConsultationNotes.objects.filter(patient_id=patient_id, visit=visit_id).order_by('-created_at').first()
        except ConsultationNotes.DoesNotExist:
            consultation_notes = None
        try:
            vital = PatientVital.objects.get(patient=patient_id, visit=visit_id)
        except PatientVital.DoesNotExist:
            vital = None
        try:
            referral = Referral.objects.get(patient=patient_id, visit=visit_id)
        except Referral.DoesNotExist:
            referral = None
        pathology_records = PathodologyRecord.objects.all()  # Fetch all consultation notes from the database
        doctors = Staffs.objects.filter(role='doctor')
        provisional_diagnoses = Diagnosis.objects.all()
        final_diagnoses = Diagnosis.objects.all()

        total_price = sum(prescription.total_price for prescription in prescriptions)
        range_31 = range(31)
        current_date = timezone.now().date()
        patient = Patients.objects.get(id=patient_id)
        remote_service = Service.objects.all()
        range_51 = range(51)
        range_301 = range(301)
        range_101 = range(101)
        range_15 = range(3, 16)
        medicines = Medicine.objects.filter(
            medicineinventory__remain_quantity__gt=0,  # Inventory level greater than zero
            expiration_date__gt=current_date  # Not expired
        ).distinct()

        return render(request, 'doctor_template/save_remotereferral.html', {
            'visit_history': visit_history,
            'patient': patient,
            'visits': visits,
            'range_31': range_31,
            'medicines': medicines,
            'prescriptions': prescriptions,
            'total_price': total_price,
            'consultation_notes': consultation_notes,
            'pathology_records': pathology_records,
            'doctors': doctors,
            'provisional_diagnoses': provisional_diagnoses,
            'final_diagnoses': final_diagnoses,
            'vital': vital,
            'referral': referral,
            'remote_service': remote_service,
            'range_51': range_51,
            'range_301': range_301,
            'range_101': range_101,
            'range_15': range_15,
        })
    except Exception as e:
        # Handle other exceptions if necessary
        return render(request, '404.html', {'error_message': str(e)})    
    
    
  
    
@csrf_exempt
@require_POST
def add_remoteprescription(request):
    try:
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
                return JsonResponse({'status': 'error', 'message': f'Invalid quantity for {medicine.drug_name}. Quantity cannot be empty.'})

            try:
                quantity_used = int(quantity_used_str)
            except ValueError:
                return JsonResponse({'status': 'error', 'message': f'Invalid quantity for {medicine.drug_name}. Quantity must be a valid number.'})

            if quantity_used < 0:
                return JsonResponse({'status': 'error', 'message': f'Invalid quantity for {medicine.drug_name}. Quantity must be a non-negative number.'})

            # Retrieve the remaining quantity of the medicine
            remain_quantity = medicine.remain_quantity

            if remain_quantity is not None and quantity_used > remain_quantity:
                return JsonResponse({'status': 'error', 'message': f'Insufficient stock for {medicine.drug_name}. Only {remain_quantity} available.'})

            # Reduce the remain quantity of the medicine
            if remain_quantity is not None:
                medicine.remain_quantity -= quantity_used
                medicine.save()

            # Save prescription
            prescription = Prescription.objects.create(
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
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    
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
def save_observation(request, patient_id, visit_id):
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
        })
    except Exception as e:
        # Handle other exceptions if necessary
        return render(request, '404.html', {'error_message': str(e)})
        

# Get an instance of a logger
logger = logging.getLogger(__name__)

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
    
       
             
@csrf_exempt
@require_POST
def save_remoteconsultation_notes(request):
    try:
        # Extract data from the request
        notes_id = request.POST.get('notes_id')       
        visit_id = request.POST.get('visit_id')       
        patient_id = request.POST.get('patient_id')               
        chief_complaints = request.POST.get('chief_complaints')        
        history_of_presenting_illness = request.POST.get('history_of_presenting_illness')
        physical_examination = request.POST.get('physical_examination')
        allergy_to_medications = request.POST.get('allergy_to_medications')
        provisional_diagnosis = request.POST.getlist('provisional_diagnosis[]')
        final_diagnosis = request.POST.getlist('final_diagnosis[]')
        pathology_ids = request.POST.getlist('pathology[]')  # Assuming pathology is a ManyToMany field
        doctor_plan = request.POST.get('doctor_plan')
        doctor = request.user.staff 
        # Retrieve the corresponding patient and doctor objects
        patient = Patients.objects.get(id=patient_id)       
        visit = PatientVisits.objects.get(id=visit_id)       
        

        # Check if the notes ID is provided for editing
        if notes_id:
            # Editing existing consultation notes
            consultation_notes = ConsultationNotes.objects.get(pk=notes_id)
        else:
            # Creating new consultation notes
            consultation_notes = ConsultationNotes()

        # Update or set values for consultation notes fields
        
        consultation_notes.visit = visit        
        consultation_notes.patient = patient        
        consultation_notes.doctor = doctor        
        consultation_notes.chief_complaints = chief_complaints
        consultation_notes.history_of_presenting_illness = history_of_presenting_illness
        consultation_notes.physical_examination = physical_examination
        consultation_notes.allergy_to_medications = allergy_to_medications
        consultation_notes.doctor_plan = doctor_plan
        consultation_notes.save()
        
        # Update ManyToMany fields
        consultation_notes.pathology.set(pathology_ids)
        consultation_notes.provisional_diagnosis.set(provisional_diagnosis)
        consultation_notes.final_diagnosis.set(final_diagnosis)

        return JsonResponse({'status': 'success','message': 'Successfully saved.'})    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    


    
@csrf_exempt
@require_POST
def add_prescription(request):
    try:
        # Extract data from the request
        prescription_id = request.POST.get('prescription_id')
        patient_id = request.POST.get('patient')
        medicine_id = request.POST.get('medicine')
        route = request.POST.get('route')
        medicine_used = int(request.POST.get('quantity'))
        frequency = request.POST.get('frequency')
        duration = request.POST.get('duration')
        dose = request.POST.get('dose')

        # Retrieve the corresponding patient and medicine
        patient = Patients.objects.get(id=patient_id)
        medicine = Medicine.objects.get(id=medicine_id)
        
        # Check if there is sufficient stock
        medicine_inventory = medicine.medicineinventory_set.first()
        if medicine_inventory and medicine_used > medicine_inventory.remain_quantity:
            return JsonResponse({'success': False, 'message': f'Insufficient stock. Only {medicine_inventory.remain_quantity} {medicine.name} available.'})

        # Check if the usageHistoryId is provided for editing
        if prescription_id:
            # Editing existing prescription
            prescription = Prescription.objects.get(pk=prescription_id)
            # Get the previous quantity used
            previous_quantity_used = prescription.quantity_used
            
            # Calculate the difference in quantity
            quantity_difference = medicine_used - previous_quantity_used
            
            # Update the stock level of the corresponding item
            if medicine_inventory:
                medicine_inventory.remain_quantity -= quantity_difference
                medicine_inventory.save()
            # Recalculate total price
            total_price = medicine_used * medicine.unit_price
            prescription.total_price = total_price
        else:
            # Creating new prescription
            prescription = Prescription()
            prs_no = generate_prescription_id()
            prescription.prs_no = prs_no

        # Update or set values for other fields
        prescription.patient = patient
        prescription.medicine = medicine
        prescription.route = route
        prescription.dose = dose
        prescription.frequency = frequency
        prescription.duration = duration
        prescription.quantity_used = medicine_used

        # Save the changes to both models
        prescription.save()

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})    
    
def generate_prescription_id():
    last_prescription = Prescription.objects.last()
    last_sample_number = int(last_prescription.prs_no.split('-')[-1]) if last_prescription else 0
    new_prescription_id = last_sample_number + 1
    return f"PRS-{new_prescription_id:07d}"


@csrf_exempt     
@require_POST
def add_patient_visit(request):
    try:
        visit_id = request.POST.get('visit_id')
        visitType = request.POST.get('visitType')        
        insuranceName = request.POST.get('insuranceName')
        insuranceNumber = request.POST.get('insuranceNumber')
        verificationCode = request.POST.get('verificationCode')
        visitReason = request.POST.get('visitReason')
        patient_id = request.POST.get('patient_id')    
        referral_number = request.POST.get('visitReason')    
        primary_service = request.POST.get('primary_service')  
        
        patient = Patients.objects.get(pk=patient_id)
        if visit_id:
            # Editing existing HealthIssue item
            visit = PatientVisits.objects.get(pk=visit_id)
            visit.visit_type = visitType         
            visit.patient = patient
            visit.primary_service = primary_service
            visit.insurance_name = insuranceName
            visit.insurance_number =  insuranceNumber            
            visit.authorization_code = verificationCode
            visit.visit_reason = visitReason
            visit.referral_number = referral_number
                            
            visit.save()
        else:
            # Adding new PatientVisit item
            vst = generate_vst() 
            
            visit = PatientVisits(
            patient=patient,
            visit_type=visitType,
            vst=vst,
            primary_service=primary_service,
            insurance_name=insuranceName,
            insurance_number=insuranceNumber,
            authorization_code=verificationCode,
            visit_reason=visitReason,
            referral_number=referral_number
                          
               
            )
            visit.save()

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}) 
    

def generate_vst():
    # Retrieve the last patient's VST from the database
    last_patient_visit = PatientVisits.objects.last()

    # Extract the numeric part from the last VST, or start from 0 if there are no patients yet
    last_vst_number = int(last_patient_visit.vst.split('-')[-1]) if last_patient_visit else 0

    # Increment the numeric part for the new patient
    new_vst_number = last_vst_number + 1

    # Format the VST with leading zeros and concatenate with the prefix "PAT-"
    new_vst = f"VST-{new_vst_number:07d}"

    return new_vst 

@csrf_exempt     
@require_POST
def add_remotepatient_visit(request):
    try:
        visit_id = request.POST.get('visit_id')
        visitType = request.POST.get('visitType')      
        patient_id = request.POST.get('patient_id')   
        primary_service = request.POST.get('primary_service')  
        
        patient = Patients.objects.get(pk=patient_id)
        if visit_id:
            # Editing existing HealthIssue item
            visit = PatientVisits.objects.get(pk=visit_id)
            visit.visit_type = visitType         
            visit.patient = patient
            visit.primary_service = primary_service
    
                            
            visit.save()
        else:
            # Adding new PatientVisit item
            vst = remotegenerate_vst() 
            
            visit = PatientVisits(
            patient=patient,
            visit_type=visitType,
            vst=vst,
            primary_service=primary_service,
         
                          
               
            )
            visit.save()

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}) 
    

def remotegenerate_vst():
    # Retrieve the last patient's VST from the database
    last_patient_visit = PatientVisits.objects.last()

    # Extract the numeric part from the last VST, or start from 0 if there are no patients yet
    last_vst_number = int(last_patient_visit.vst.split('-')[-1]) if last_patient_visit else 0

    # Increment the numeric part for the new patient
    new_vst_number = last_vst_number + 1

    # Format the VST with leading zeros and concatenate with the prefix "PAT-"
    new_vst = f"VST-{new_vst_number:07d}"

    return new_vst 
 

    


   
def fetch_model_data(request):
    selected_option = request.GET.get('selected_option')
    data = []

    if selected_option == 'disease':
        data = list(DiseaseRecode.objects.values_list('id', 'disease_name'))
    elif selected_option == 'pathology':
        data = list(PathodologyRecord.objects.values_list('id', 'name'))
    elif selected_option == 'health_issue':
        data = list(HealthIssue.objects.values_list('id', 'name'))

    return JsonResponse({'data': data})    

@login_required
def patient_visit_history_view(request, patient_id):
    # Retrieve visit history for the specified patient
    visit_history = PatientVisits.objects.filter(patient_id=patient_id)
    current_date = timezone.now().date()
    patient = Patients.objects.get(id=patient_id)
    medicines = Medicine.objects.filter(
        medicineinventory__remain_quantity__gt=0,  # Inventory level greater than zero
        expiration_date__gt=current_date  # Not expired
    ).distinct() 

    return render(request, 'doctor_template/manage_patient_visit_history.html', {
        'visit_history': visit_history,
        'patient':patient,
        'medicines':medicines,
        })
    



@login_required
def patient_health_record_view(request, patient_id, visit_id):
    try:
        # Retrieve visit history for the specified patient
        doctor = request.user.staff
        visits = PatientVisits.objects.get(id=visit_id,patient_id=patient_id)        
        prescriptions = Prescription.objects.filter(patient=patient_id, visit=visit_id)
        try:
            consultation_notes = ConsultationNotes.objects.filter(patient_id=patient_id, visit=visit_id ,doctor_id=doctor).order_by('-created_at').first()
        except ConsultationNotes.DoesNotExist:
            consultation_notes = None         
        try:
            previous_vitals = PatientVital.objects.filter(patient=patient_id,visit=visit_id, recorded_by=doctor).order_by('-recorded_at')
        except PatientVital.DoesNotExist:
            previous_vitals = None           
        try:
            procedures = Procedure.objects.filter(patient=patient_id, visit=visit_id,doctor=doctor)            
        except Procedure.DoesNotExist:
            procedures = None          
        try:
            lab_tests = LaboratoryOrder.objects.filter(patient=patient_id, visit=visit_id,doctor=doctor)
        except LaboratoryOrder.DoesNotExist:
            lab_tests = None  
        total_price = sum(prescription.total_price for prescription in prescriptions)   
        patient = Patients.objects.get(id=patient_id)
           # Calculate total amount from all procedures
        try:
            imaging_records = ImagingRecord.objects.filter(patient_id=patient_id, visit_id=visit_id,doctor=doctor)
        except ImagingRecord.DoesNotExist:
            imaging_records = None
               
        total_procedure_cost = procedures.aggregate(Sum('cost'))['cost__sum']
        total_imaging_cost = imaging_records.aggregate(Sum('cost'))['cost__sum']
        lab_tests_cost = lab_tests.aggregate(Sum('cost'))['cost__sum']    
        provisional_diagnoses = Diagnosis.objects.all()
        final_diagnoses = Diagnosis.objects.all()
        pathology_records = PathodologyRecord.objects.all()
        return render(request, 'doctor_template/manage_patient_health_record.html', {
           
            'provisional_diagnoses': provisional_diagnoses,
            'final_diagnoses': final_diagnoses,
            'pathology_records': pathology_records,
            'patient': patient,
            'visit': visits,          
            'lab_tests_cost': lab_tests_cost,
            'total_procedure_cost': total_procedure_cost,
            'total_imaging_cost': total_imaging_cost,
            'prescriptions': prescriptions,
            'total_price': total_price,
            'consultation_notes': consultation_notes,      
            'previous_vitals': previous_vitals,          
            'imaging_records': imaging_records,          
            'lab_tests': lab_tests,
            'procedures': procedures,
      
        })
    except Exception as e:
        # Handle other exceptions if necessary
        return render(request, '404.html', {'error_message': str(e)})
    


@login_required
def prescription_list(request):
    # Retrieve all patients
    patients = Patients.objects.all()

    # Retrieve current date
    current_date = timezone.now().date()
    
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
    verified=F('verified'),  # Access verified field directly from Prescription
    issued=F('issued'),      # Access issued field directly from Prescription
    status=F('status'),      # Access status field directly from Prescription
)
    
    # Retrieve medicines with inventory levels not equal to zero or greater than zero, and not expired
    medicines = Medicine.objects.filter(
        medicineinventory__remain_quantity__gt=0,  # Inventory level greater than zero
        expiration_date__gt=current_date  # Not expired
    ).distinct() 
    
    # Calculate total price of all prescriptions
    total_price = sum(prescription.total_price for prescription in prescriptions) 
    
    return render(request, 'doctor_template/manage_prescription_list.html', { 
        'medicines': medicines,
        'patients': patients,
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
    range_51 = range(51)
    range_301 = range(301)
    range_101 = range(101)
    range_15 = range(3, 16)
    # Retrieve all vital information for the patient
    patient_vitals = PatientVital.objects.filter(patient=patient).order_by('-recorded_at')

    # Render the template with the patient's vital information
    context = {
        'range_51': range_51,
        'range_301': range_301,
        'range_101': range_101,
        'range_15': range_15,
        'patient': patient, 
        'patient_vitals': patient_vitals
    }
    
    return render(request, 'doctor_template/manage_patient_vital_list.html', context) 

@login_required   
def patient_vital_all_list(request):
    # Retrieve the patient object
    patients = Patients.objects.all()
    range_51 = range(51)
    range_301 = range(301)
    range_101 = range(101)
    range_15 = range(3, 16)
    # Retrieve all vital information for the patient
    patient_vitals = PatientVital.objects.all().order_by('-recorded_at')
    
    context = {
        'range_51': range_51,
        'range_301': range_301,
        'range_101': range_101,
        'range_15': range_15,
        'patients': patients, 
        'patient_vitals': patient_vitals
    }
    # Render the template with the patient's vital information
    return render(request, 'doctor_template/manage_all_patient_vital.html', context)    

@csrf_exempt
@require_POST
def save_patient_vital(request):
    try:
        # Extract data from the request
        vital_id = request.POST.get('vital_id')
        visit_id = request.POST.get('visit_id')
        patient_id = request.POST.get('patient_id')
        respiratory_rate = request.POST.get('respiratory_rate')
        pulse_rate = request.POST.get('pulse_rate')
        blood_pressure = request.POST.get('blood_pressure')
        spo2 = request.POST.get('spo2')
        temperature = request.POST.get('temperature')
        weight = request.POST.get('Weight')
        gcs = request.POST.get('gcs')
        avpu = request.POST.get('avpu')

        # Retrieve the corresponding InventoryItem
        patient = Patients.objects.get(id=patient_id)
        visit = PatientVisits.objects.get(id=visit_id)
        recorded_by = request.user.staff
              


        # Check if the usageHistoryId is provided for editing
        if vital_id:
            # Editing existing usage history
            vital = PatientVital.objects.get(pk=vital_id)
          
        else:
            # Creating new usage history
            vital = PatientVital()
         

        # Update or set values for other fields
        vital.visit = visit
        vital.recorded_by = recorded_by
        vital.respiratory_rate = respiratory_rate
        vital.pulse_rate = pulse_rate
        vital.blood_pressure = blood_pressure
        vital.weight = weight
        vital.spo2 = spo2
        vital.gcs = gcs
        vital.temperature = temperature
        vital.avpu = avpu
        vital.patient = patient

    
        vital.save()
        return JsonResponse({'status': 'success','message': 'vitals saved successfully'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    
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
def manage_pathodology(request):
    doctor = request.user.staff
    pathodology_records=ImagingRecord.objects.filter(doctor=doctor).order_by('-order_date')   
    orders = Order.objects.filter(order_type__in=[pathology.imaging.name for pathology in pathodology_records], is_read=True)       
    return render(request,"doctor_template/manage_pathodology.html",{
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
        return redirect(reverse('patient_procedure_view'))
   
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
        return redirect(reverse('manage_pathodology'))
   
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
        return redirect(reverse('patient_lab_view'))
   
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
    
@csrf_exempt
@require_POST
def save_consultation_notes(request):
    try:
        # Extract data from the request
        notes_id = request.POST.get('notes_id')
        doctor_id = request.POST.get('doctor')
        patient_id = request.POST.get('patient')
        chief_complaints = request.POST.get('chief_complaints')
        history_of_presenting_illness = request.POST.get('history_of_presenting_illness')
        physical_examination = request.POST.get('physical_examination')
        allergy_to_medications = request.POST.get('allergy_to_medications')
        provisional_diagnosis = request.POST.getlist('provisional_diagnosis')
        final_diagnosis = request.POST.getlist('final_diagnosis')
        pathology_ids = request.POST.getlist('pathology')  # Assuming pathology is a ManyToMany field
        doctor_plan = request.POST.get('doctor_plan')

        # Retrieve the corresponding patient and doctor objects
        patient = Patients.objects.get(id=patient_id)
        doctor = Staffs.objects.get(id=doctor_id)

        # Check if the notes ID is provided for editing
        if notes_id:
            # Editing existing consultation notes
            consultation_notes = ConsultationNotes.objects.get(pk=notes_id)
        else:
            # Creating new consultation notes
            consultation_notes = ConsultationNotes()

        # Update or set values for consultation notes fields
        consultation_notes.doctor = doctor
        consultation_notes.patient = patient
        consultation_notes.chief_complaints = chief_complaints
        consultation_notes.history_of_presenting_illness = history_of_presenting_illness
        consultation_notes.physical_examination = physical_examination
        consultation_notes.allergy_to_medications = allergy_to_medications
        consultation_notes.doctor_plan = doctor_plan
        consultation_notes.save()
        
        # Update ManyToMany fields
        consultation_notes.pathology.set(pathology_ids)
        consultation_notes.provisional_diagnosis.set(provisional_diagnosis)
        consultation_notes.final_diagnosis.set(final_diagnosis)

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    




    













