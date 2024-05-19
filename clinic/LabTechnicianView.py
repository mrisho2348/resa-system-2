
from django.utils import timezone
import logging
from django.urls import reverse
from django.db.models import F
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.http import  HttpResponseBadRequest, HttpResponseServerError
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Sum
from django.db.models import Q
from clinic.models import  Consultation,  DiseaseRecode, Medicine, Notification,  PathodologyRecord, Patients, Procedure, Staffs
from django.views.decorators.http import require_POST
from django.contrib.contenttypes.models import ContentType
from .models import ConsultationNotes, ConsultationOrder,Country, Diagnosis,Diagnosis,HealthIssue, ImagingRecord, LaboratoryOrder, Order, PatientVisits, PatientVital, Prescription, Procedure, Patients,Service

@login_required
def labtechnician_dashboard(request):
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
    return render(request, "labtechnician_template/home_content.html", context)



@login_required
def manage_patient(request):
    patient_records=Patients.objects.all().order_by('-created_at') 
    range_121 = range(1, 121)
    all_country = Country.objects.all()
    doctors=Staffs.objects.filter(role='doctor')
    return render(request,"labtechnician_template/manage_patients.html", {
        "patient_records":patient_records,
        "range_121":range_121,
        "doctors":doctors,
        "all_country":all_country,
        })
 
 

@login_required 
def patient_consultation_detail(request, patient_id, visit_id):
    try:        
        
        prescriptions = Prescription.objects.filter(patient_id=patient_id, visit_id=visit_id)     
        try:
            vital = PatientVital.objects.get(patient_id=patient_id, visit_id=visit_id)                     
        except PatientVital.DoesNotExist:
            vital = None
        try:
            visit_history = PatientVisits.objects.get(id=visit_id, patient_id=patient_id)                  
        except PatientVisits.DoesNotExist:
            visit_history = None    
                
        patient = Patients.objects.get(id=patient_id)
         # Fetching services based on coverage and type
        if patient.payment_form == 'insurance':
            # If patient's payment form is insurance, fetch services with matching coverage
            remote_service = Service.objects.filter(
                Q(type_service='Consultation') & Q(coverage=patient.payment_form)
            )
        else:
            # If payment form is cash, fetch all services of type procedure
            remote_service = Service.objects.filter(type_service='Consultation')
        total_price = sum(prescription.total_price for prescription in prescriptions)    
       
        doctors = Staffs.objects.filter(role='doctor')
        return render(request, 'labtechnician_template/patient_consultation_detail.html', {        
            
            'prescriptions': prescriptions,
            'total_price': total_price,
            'visit_history': visit_history,
            'patient': patient,       
            'doctors': doctors,      
            'vital': vital,
            'remote_service': remote_service,
        
        })
    except Exception as e:
        # Handle other exceptions if necessary
        return render(request, '404.html', {'error_message': str(e)})     
    


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
    return render(request,"labtechnician_template/manage_consultation.html",context)

    
@login_required
def manage_laboratory(request):
    doctor = request.user.staff
    lab_records=LaboratoryOrder.objects.filter(doctor=doctor)  
    orders = Order.objects.filter(order_type__in=[lab_record.imaging.name for lab_record in lab_records], is_read=True)          
    return render(request,"labtechnician_template/manage_lab_result.html",{
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

    return render(request, "labtechnician_template/staff_details.html", context)

@login_required
def view_patient(request, patient_id):
    patient = get_object_or_404(Patients, id=patient_id)
    # Fetch additional staff-related data  
    context = {
        'patient': patient,
     
    }

    return render(request, "labtechnician_template/patients_detail.html", context)

@login_required
def all_orders_view(request):
    # Retrieve all orders from the database
    orders = Order.objects.all().order_by('-order_date')    
    # Render the template with the list of orders
    return render(request, 'receptionist_template/order_detail.html', {'orders': orders})

@csrf_exempt
def add_consultation(request):
    if request.method == 'POST':
        try:
            # Assuming your form fields are named appropriately in your template
            patient_id = request.POST.get('patient_id')
            doctor_id = request.POST.get('doctor_id')
            data_recorder = request.user.staff
            visit_id = request.POST.get('visit_id')
            consultation_names = request.POST.getlist('consultation_name[]')
            descriptions = request.POST.getlist('description[]')            
            costs = request.POST.getlist('cost[]')
            order_date = request.POST.get('order_date')

            # Loop through the submitted data and create ImagingRecord objects
            for i in range(len(consultation_names)):
                consultation_record = ConsultationOrder.objects.create(
                    patient_id=patient_id,
                    visit_id=visit_id,
                    order_date=order_date,
                    data_recorder=data_recorder,
                    doctor_id=doctor_id,
                    consultation_id=consultation_names[i],
                    description=descriptions[i],                 
                    cost=costs[i],
                    # Set other fields as needed
                )
                # Save the imaging record to the database
                consultation_record.save()

            # Assuming the imaging records were successfully saved
            return JsonResponse({'status': 'success', 'message': 'consultation records saved successfully'})
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

        return render(request, "labtechnician_template/add_consultation.html", context)

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
    return render(request, 'labtechnician_template/manage_notification.html', context)

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

    return render(request, 'labtechnician_template/manage_patient_procedure.html', context)


@csrf_exempt
def save_procedure(request):
    if request.method == 'POST':
        try:
            # Extract data from the POST request
            procedure_id = request.POST.get('procedure_id')
            result = request.POST.get('result')         
            doctor = request.user.staff

            # Check if the procedure ID is provided
            if procedure_id:
                # Retrieve the procedure record if it exists
                try:
                    procedure_record = Procedure.objects.get(id=procedure_id)
                except Procedure.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'The provided procedure ID is invalid.'})                

                # Update the procedure record with the new data
                procedure_record.result = result
                procedure_record.doctor = doctor              

                # Save the updated procedure record
                procedure_record.save()

                return JsonResponse({'success': True, 'message': f'The procedure record for "{procedure_record.name}" has been updated successfully.'})
        
        except Patients.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'The provided patient ID is invalid.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {e}'})

    return JsonResponse({'success': False, 'message': 'Invalid request method. This endpoint only accepts POST requests.'})


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
def generate_invoice_bill(request,  order_id):
    # Retrieve the patient and visit objects based on IDs
    
    order = Order.objects.get(id=order_id)
     
    context = {
        'order': order,
       
    }
    return render(request, 'labtechnician_template/invoice_bill.html', context)

@login_required
def generate_billing(request, procedure_id):
    procedure = get_object_or_404(Procedure, id=procedure_id)

    context = {
        'procedure': procedure,
    }

    return render(request, 'labtechnician_template/billing_template.html', context)

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
    return render(request, 'labtechnician_template/manage_appointment.html', context)


def fetch_laborders_counts(request):
    # Retrieve the current logged-in doctor
    current_doctor = request.user.staff
    current_date = timezone.now().date() 
    lab_orders = LaboratoryOrder.objects.filter(doctor=current_doctor)   
    # Retrieve the counts of unread and read orders for the current doctor
    unread_count = Order.objects.filter(order_type__in=[lab_order.name.name for lab_order in lab_orders], order_date=current_date).count()
    read_count = Order.objects.filter(order_type__in=[lab_order.name.name for lab_order in lab_orders], is_read=True).count()    
    # Return the counts as JSON response
    return JsonResponse({'unread_count': unread_count, 'read_count': read_count})

@login_required
def lab_unread_orders_view(request):
    template_name = 'labtechnician_template/unread_lab_orders.html'
    doctor = request.user.staff
    # Query to retrieve the latest procedure record for each patient
    lab_orders = LaboratoryOrder.objects.filter(doctor=doctor).order_by('-order_date')    
    unread_orders = Order.objects.filter(order_type__in=[lab_order.name.name for lab_order in lab_orders], is_read=True) 
    print(unread_orders)
    orders = unread_orders 
    unread_orders.update(is_read=True)         
    return render(request, template_name, {'orders': orders})

@login_required
def lab_read_orders_view(request):
    template_name = 'labtechnician_template/read_lab_orders.html'
    doctor = request.user.staff
    # Query to retrieve the latest procedure record for each patient
    lab_orders = LaboratoryOrder.objects.filter(doctor=doctor).order_by('-order_date')    
    read_orders = Order.objects.filter(order_type__in=[lab_order.name.name for lab_order in lab_orders], is_read=False)         
    return render(request, template_name, {'lab_orders': lab_orders})


def save_lab_order_result(request, order_id):
    if request.method == 'POST':
        try:
            # Retrieve the laboratory order object
            lab_order = get_object_or_404(LaboratoryOrder, id=order_id)
            
            # Update the 'result' field with the new result from the form
            lab_order.result = request.POST.get('result')
            
            # Save the updated laboratory order object
            lab_order.save()
            
            # Redirect the user to a success page or back to the same page
            return redirect(reverse('lab_read_orders'))  # Replace 'success_page' with the name of your success page URL pattern
        except Exception as e:
            # Handle any exceptions that may occur during the process
            return HttpResponseServerError(f'An error occurred: {e}')
    else:
        # Handle GET requests or other methods
        # You can customize this part based on your requirements
        pass

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

        doctors = Staffs.objects.filter(role='doctor')
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

        return render(request, 'labtechnician_template/procedure_template.html', {
            'visit_history': visit_history,
            'patient': patient,
            'prescriptions': prescriptions,
            'doctors': doctors,
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

def get_procedure_cost(request):
    if request.method == 'GET':
        procedure_id = request.GET.get('procedure_id')
        try:
            procedure = Service.objects.get(id=procedure_id)
            cost = procedure.cost
            return JsonResponse({'cost': cost})
        except Service.DoesNotExist:
            return JsonResponse({'error': 'Procedure not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
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
                doctor_id = request.POST.get('doctor_id')
                patient_id = request.POST.get('patient_id')
                visit_id = request.POST.get('visit_id')
                order_date = request.POST.get('order_date')
                patient = get_object_or_404(Patients, id=patient_id)
                visit = get_object_or_404(PatientVisits, id=visit_id)
                
                # Retrieve the current user as the doctor
                data_recorder = request.user.staff

                # Create and save the new Procedure instance
                procedure = Procedure.objects.create(
                    patient=patient,
                    visit=visit,
                    doctor_id=doctor_id,
                    data_recorder=data_recorder,
                    order_date=order_date,
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
            


    
    
def get_unit_price(request):
    if request.method == 'GET':
        medicine_id = request.GET.get('medicine_id')
        try:
            medicine = Medicine.objects.get(pk=medicine_id)
            unit_price = medicine.unit_price
            return JsonResponse({'unit_price': unit_price})
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
            imaging_records = ImagingRecord.objects.filter(patient_id=patient_id, visit_id=visit_id)
        except ImagingRecord.DoesNotExist:
            imaging_records = None

        prescriptions = Prescription.objects.filter(patient=patient_id, visit=visit_id)

        try:
            procedures = Procedure.objects.filter(patient=patient_id, visit=visit_id)
        except Procedure.DoesNotExist:
            procedures = None

        doctors=Staffs.objects.filter(role='doctor')
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
        return render(request, 'labtechnician_template/observation_template.html', {
            'visit_history': visit_history,
            'patient': patient,
            'doctors': doctors,
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

@csrf_exempt
def add_imaging(request):
    if request.method == 'POST':
        try:
            
            # Assuming your form fields are named appropriately in your template
            doctor_id= request.POST.get('doctor_id')
            patient_id = request.POST.get('patient_id')
            data_recorder = request.user.staff
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
                    doctor_id=doctor_id,
                    data_recorder=data_recorder,
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
            Investigation = LaboratoryOrder.objects.filter(patient_id=patient_id, visit_id=visit_id)
        except LaboratoryOrder.DoesNotExist:
            Investigation = None

        prescriptions = Prescription.objects.filter(patient=patient_id, visit=visit_id)

        try:
            procedures = Procedure.objects.filter(patient=patient_id, visit=visit_id)
        except Procedure.DoesNotExist:
            procedures = None

        doctors = Staffs.objects.filter(role='doctor')
        total_price = sum(prescription.total_price for prescription in prescriptions)

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
        return render(request, 'labtechnician_template/laboratory_template.html', {
            'visit_history': visit_history,
            'patient': patient,
            'doctors': doctors,
            'prescriptions': prescriptions,
            'total_price': total_price,
            'Investigation': Investigation,
            'procedures': procedures,
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

            # Loop through the submitted data and create LaboratoryOrder objects
            for i in range(len(investigation_names)):
                investigation_record = LaboratoryOrder.objects.create(
                    patient_id=patient_id,
                    visit_id=visit_id,
                    order_date=order_date,
                    doctor=doctor,
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

    return render(request, 'labtechnician_template/manage_patient_visit_history.html', {
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
        return render(request, 'labtechnician_template/manage_patient_health_record.html', {
           
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
    
    return render(request, 'labtechnician_template/manage_prescription_list.html', { 
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
    return render(request, "labtechnician_template/prescription_detail.html", context)

  
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
    
    return render(request, 'labtechnician_template/manage_patient_vital_list.html', context)  

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
    return render(request, 'labtechnician_template/manage_all_patient_vital.html', context)    



@login_required
def new_consultation_order(request):   
    # Retrieve the current logged-in doctor
    data_recorder = request.user.staff    
    # Retrieve all ConsultationOrder instances for the current doctor
    consultation_orders = ConsultationOrder.objects.filter(data_recorder=data_recorder).order_by('-order_date')     
    # Retrieve all unread orders for the ConsultationOrder instances
    unread_orders = Order.objects.filter(order_type__in=[consultation.consultation.name for consultation in consultation_orders], is_read=True)    
    # Mark the retrieved unread orders as read
    orders = unread_orders 
    print(unread_orders)
    unread_orders.update(is_read=True)    
    # Render the template with the fetched unread orders
    return render(request, 'labtechnician_template/new_consultation_order.html', {'orders': orders})


def fetch_order_counts_view(request):
    # Retrieve the current logged-in doctor
    current_doctor = request.user.staff
    consultation_orders = ConsultationOrder.objects.filter(doctor=current_doctor)   
    # Retrieve the counts of unread and read orders for the current doctor
    unread_count = Order.objects.filter(order_type__in=[consultation.consultation.name for consultation in consultation_orders], is_read=False).count()
    read_count = Order.objects.filter(order_type__in=[consultation.consultation.name for consultation in consultation_orders], is_read=True).count()    
    # Return the counts as JSON response
    return JsonResponse({'unread_count': unread_count, 'read_count': read_count})


@login_required
def new_radiology_order(request):
    data_recorder = request.user.staff
    pathodology_records=ImagingRecord.objects.filter(data_recorder=data_recorder.id).order_by('-order_date')   
    unread_orders = Order.objects.filter(order_type__in=[pathology.imaging.name for pathology in pathodology_records], is_read=True)     
    orders = unread_orders   
    unread_orders.update(is_read=True)     
    return render(request,"labtechnician_template/new_radiology_order.html",{
        "orders":unread_orders,       
        }) 
    


@login_required
def new_procedure_order(request):
    template_name = 'labtechnician_template/new_procedure_order.html'
    data_recorder = request.user.staff
    # Query to retrieve the latest procedure record for each patient
    procedures = Procedure.objects.filter(data_recorder=data_recorder).order_by('-order_date')    
    unread_orders = Order.objects.filter(order_type__in=[procedure.name.name for procedure in procedures], is_read=True) 
    print(procedures)
    orders = unread_orders 
    unread_orders.update(is_read=True)         
    return render(request, template_name, {'orders': orders})
    





    













