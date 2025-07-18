
from datetime import datetime
import json
from django.db import IntegrityError
from django.http import  JsonResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from clinic.forms import RemoteCounselingForm, RemoteDischargesNotesForm, RemoteObservationRecordForm, RemoteReferralForm
from clinic.models import ChiefComplaint, ClinicCompany, CustomUser,  Diagnosis, FamilyMedicalHistory, HealthRecord, PathodologyRecord, PatientHealthCondition, PatientLifestyleBehavior, PatientMedicationAllergy, PatientSurgery, PrescriptionFrequency,  RemoteCompany, RemoteConsultation, RemoteConsultationNotes, RemoteCounseling, RemoteDischargesNotes,  RemoteLaboratoryOrder, RemoteMedicine, RemoteObservationRecord, RemotePatient, RemotePatientDiagnosisRecord, RemotePatientVisits, RemotePatientVital, RemotePrescription, RemoteProcedure,  RemoteReferral, RemoteService,  Service, Staffs
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.db.models import Subquery, OuterRef
from django.db.models import Count
from django.db.models import Sum, Max
from django.core.exceptions import ValidationError
from django.db.models.functions import ExtractMonth  # Add this import
from django.template.loader import render_to_string
from kahamahmis.forms import RemoteLaboratoryOrderForm, RemoteProcedureForm

from django.db.models import Q


@login_required
def save_patient_health_information(request, patient_id):
    try:
        # Retrieve the patient object using the patient_id from URL parameters
        patient = get_object_or_404(RemotePatient, pk=patient_id)
        try:
            all_medicines = RemoteMedicine.objects.all()
        except RemoteMedicine.DoesNotExist:
            # Handle the case where no medicines are found
            all_medicines = []
        if request.method == 'POST':
            # Check if the patient has allergies to medication
            medication_allergy = request.POST.get('medication_allergy')
            family_medical_history = request.POST.get('family_medical_history')
            surgery_history = request.POST.get('surgery_history')
            chronic_illness = request.POST.get('chronic_illness')
                        
            smoking = request.POST.get('smoking')
            alcohol_consumption = request.POST.get('alcohol_consumption')
            weekly_exercise_frequency = request.POST.get('weekly_exercise_frequency')
            healthy_diet = request.POST.get('healthy_diet')
            stress_management = request.POST.get('stress_management')
            sufficient_sleep = request.POST.get('sufficient_sleep')
            data_recorder=request.user.staff 
            # Create PatientLifestyleBehavior object
            lifestyle_behavior = PatientLifestyleBehavior.objects.create(
                patient=patient,
                smoking=smoking,
                alcohol_consumption=alcohol_consumption,
                weekly_exercise_frequency=weekly_exercise_frequency,
                healthy_diet=healthy_diet,
                stress_management=stress_management,
                sufficient_sleep=sufficient_sleep,
                data_recorder=data_recorder,
            )

            # Check if the patient has surgery history
            if surgery_history == 'yes':
                surgery_names = request.POST.getlist('surgery_name[]')
                surgery_dates = request.POST.getlist('date_of_surgery[]')
                for name, date in zip(surgery_names, surgery_dates):
                    surgery = PatientSurgery.objects.create(
                        patient=patient,
                        surgery_name=name,
                        data_recorder=data_recorder,
                        surgery_date=date,
                    )

            # Check if the patient has chronic illness
            if chronic_illness == 'yes':
                health_conditions = request.POST.getlist('health_condition[]')
                health_condition_notes = request.POST.getlist('health_condition_notes[]')
                for condition, notes in zip(health_conditions, health_condition_notes):
                    patient_health_condition = PatientHealthCondition.objects.create(
                        patient=patient,
                        data_recorder=data_recorder,
                        health_condition=condition,
                        health_condition_notes=notes
                    )

            # Check if the patient has family medical history
            if family_medical_history == 'yes':
                conditions = request.POST.getlist('condition[]')
                relationships = request.POST.getlist('relationship[]')
                comments = request.POST.getlist('comments[]')
                for condition, relationship, comment in zip(conditions, relationships, comments):
                    family_medical_history = FamilyMedicalHistory.objects.create(
                        patient=patient,
                        data_recorder=data_recorder,
                        condition=condition,
                        relationship=relationship,
                        comments=comment
                    )

            # Check if the patient has medication allergies
            if medication_allergy == 'yes':
                medicine_names = request.POST.getlist('medicine_name[]')
                reactions = request.POST.getlist('reaction[]')
                for medicine_name, reaction in zip(medicine_names, reactions):
                    medicine_name_id = RemoteMedicine.objects.get(id=medicine_name)           
                    medication_allergy = PatientMedicationAllergy.objects.create(
                        patient=patient,
                        data_recorder=data_recorder,
                        medicine_name_id=medicine_name_id.id,
                        reaction=reaction
                    )

            # Redirect to the appropriate URL upon successful data saving
            return redirect(reverse('kahama_save_patient_visit_save', args=[patient_id]))

    except RemotePatient.DoesNotExist:
        # Handle the case where the patient ID is not valid
        messages.error(request, 'Patient not found.')
        return redirect(reverse('kahama_save_patient_health_information', args=[patient_id])) 

    except Exception as e:
        # Handle other exceptions
        messages.error(request, f'Error adding patient health information: {str(e)}')

    # If the request method is not POST or if there's an error, render the form again
    return render(request, 'kahama_template/add_patient_health_condition_form.html', {'patient': patient,'all_medicines':all_medicines})



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
            chief_complaint = ChiefComplaint(
                duration=duration,
                patient_id=patient_id,
                visit_id=visit_id
            )

            # Set the appropriate fields based on the provided data
            if health_record_id == "other":
                # Check if a ChiefComplaint with the same other_complaint already exists for the given visit_id
                if ChiefComplaint.objects.filter(visit_id=visit_id, other_complaint=other_chief_complaint).exists():
                    return JsonResponse({'status': False, 'message': 'A Other ChiefComplaint with the same name already exists for this patient'})
                chief_complaint.other_complaint = other_chief_complaint
            else:
                # Check if a ChiefComplaint with the same health_record_id already exists for the given visit_id
                if ChiefComplaint.objects.filter(health_record_id=health_record_id, visit_id=visit_id).exists():
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
            chief_complaint = get_object_or_404(ChiefComplaint, id=chief_complaint_id)
            
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
        
        except ChiefComplaint.DoesNotExist:
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
        existing_data = ChiefComplaint.objects.filter(patient_id=patient_id, visit_id=visit_id).values()
        
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
            chief_complaint = get_object_or_404(ChiefComplaint, id=chief_complaint_id)
            
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
    patient = get_object_or_404(RemotePatient, pk=patient_id)
    visit = get_object_or_404(RemotePatientVisits, patient=patient, id=visit_id)
    patient_visits = RemotePatientVisits.objects.filter(patient=patient)

    # Fetch patient health-related data
    try:
        context_data = {
            'patient_vitals': RemotePatientVital.objects.filter(patient=patient, visit=visit),
            'health_records': HealthRecord.objects.all(),
            'health_conditions': PatientHealthCondition.objects.filter(patient=patient),
            'surgery_info': PatientSurgery.objects.filter(patient=patient),
            'family_history': FamilyMedicalHistory.objects.filter(patient=patient),
            'allergies': PatientMedicationAllergy.objects.filter(patient=patient),
            'behaviors': PatientLifestyleBehavior.objects.get(patient=patient),
        }
    except Exception:
        context_data = {
            'patient_vitals': None, 'health_records': None,
            'health_conditions': None, 'surgery_info': None,
            'family_history': None, 'allergies': None, 'behaviors': None,
        }

    consultation_note = RemoteConsultationNotes.objects.filter(patient=patient, visit=visit).first()
    previous_referrals = RemoteReferral.objects.filter(patient=patient, visit=visit)
    previous_discharges = RemoteDischargesNotes.objects.filter(patient=patient, visit=visit)

    provisional_record, _ = RemotePatientDiagnosisRecord.objects.get_or_create(patient=patient, visit=visit)
    provisional_diagnosis_ids = provisional_record.provisional_diagnosis.values_list('id', flat=True)
    final_diagnosis_ids = provisional_record.final_diagnosis.values_list('id', flat=True)

    pathology_records = PathodologyRecord.objects.all()

    context = {
        'patient': patient,
        'visit': visit,
        'consultation_note': consultation_note,
        'previous_referrals': previous_referrals,
        'previous_discharges': previous_discharges,
        'patient_visits': patient_visits,
        'pathology_records': pathology_records,
        'provisional_diagnoses': Diagnosis.objects.all(),
        'provisional_diagnosis_ids': provisional_diagnosis_ids,
        'final_provisional_diagnosis': final_diagnosis_ids,
        'range_51': range(51),
        'range_101': range(101),
        'range_301': range(301),
        'range_15': range(3, 16),
        'temps': np.arange(0, 510, 1) / 10,
    }
    context.update(context_data)

    if request.method == 'POST':
        try:
            history = request.POST.get('history_of_presenting_illness')
            doctor_plan = request.POST.get('doctor_plan')
            plan_note = request.POST.get('doctor_plan_note')
            ros = request.POST.get('review_of_systems')
            exam_notes = request.POST.get('physical_examination')
            allergy_summary = request.POST.get('allergy_summary')
            comorbidity_summary = request.POST.get('known_comorbidities_summary')
            provisional_ids = request.POST.getlist('provisional_diagnosis[]')
            pathology_ids = request.POST.getlist('pathology[]')

            # Update provisional diagnosis
            if not provisional_ids:
                provisional_record.data_recorder = doctor
            provisional_record.provisional_diagnosis.set(provisional_ids)
            provisional_record.save()

            if consultation_note:
                # Update existing note
                consultation_note.history_of_presenting_illness = history
                consultation_note.doctor_plan = doctor_plan
                consultation_note.doctor_plan_note = plan_note
                consultation_note.review_of_systems = ros
                consultation_note.physical_examination = exam_notes
                consultation_note.allergy_summary = allergy_summary
                consultation_note.known_comorbidities_summary = comorbidity_summary
                consultation_note.pathology.set(pathology_ids)
                consultation_note.save()
            else:
                if RemoteConsultationNotes.objects.filter(patient=patient, visit=visit).exists():
                    messages.error(request, 'A consultation note already exists for this visit.')
                    return render(request, 'kahama_template/add_consultation_notes.html', context)

                consultation_note = RemoteConsultationNotes.objects.create(
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
                consultation_note.pathology.set(pathology_ids)
                consultation_note.save()

            messages.success(request, 'Consultation record saved successfully.')

            if doctor_plan == "Laboratory":
                return redirect(reverse('kahama_save_laboratory', args=[patient_id, visit_id]))
            else:
                return redirect(reverse('kahama_save_remotesconsultation_notes_next', args=[patient_id, visit_id]))

        except Exception as e:
            messages.error(request, f'Error saving consultation note: {str(e)}')

    return render(request, 'kahama_template/add_consultation_notes.html', context)

    

@login_required    
def save_counsel(request, patient_id, visit_id):
    # Retrieve patient and visit objects
    patient = get_object_or_404(RemotePatient, id=patient_id)
    visit = get_object_or_404(RemotePatientVisits, id=visit_id)              
    data_recorder = request.user.staff
    # Retrieve existing remote counseling record if it exists
    remote_counseling = RemoteCounseling.objects.get(patient=patient, visit=visit)
    consultation_notes = RemotePatientDiagnosisRecord.objects.filter(patient=patient_id, visit=visit_id)  
    # Prepare context for rendering the template
    context = {
        'patient': patient, 
        'visit': visit,
        'remote_counseling': remote_counseling,
        'consultation_notes': consultation_notes,
    }
    
    # Handle form submission
    if request.method == 'POST':        
        form = RemoteCounselingForm(request.POST, instance=remote_counseling)
        
        # Check if a record already exists for the patient and visit
        if remote_counseling:
            # If a record exists, update it
            if form.is_valid():
                try:
                    form.save()
                    messages.success(request, '')
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
                    messages.success(request, '')
                except ValidationError as e:
                    messages.error(request, f'Validation Error: {e}')
            else:
                messages.error(request, 'Please correct the errors in the form.')

        # Redirect to the appropriate page after saving
        return redirect(reverse('kahama_save_remotesconsultation_notes', args=[patient_id, visit_id]))
   
    else:
        # If it's a GET request, initialize the form with existing data (if any)
        form = RemoteCounselingForm(instance=remote_counseling)   
    # Add the form to the context
    context['form'] = form    
    return render(request, 'kahama_template/counsel_template.html', context)

@login_required
def save_remotereferral(request, patient_id, visit_id):
    try:
        # Retrieve patient and visit objects
        patient = get_object_or_404(RemotePatient, id=patient_id)
        visit = get_object_or_404(RemotePatientVisits, id=visit_id)        
        data_recorder = request.user.staff
        referral = RemoteReferral.objects.filter(patient=patient, visit=visit).first()   
        consultation_notes = RemotePatientDiagnosisRecord.objects.filter(patient=patient_id, visit=visit_id)  
        context = {'patient': patient,
         'visit': visit, 
         'referral': referral,
         'consultation_notes': consultation_notes,
         }  

        if request.method == 'POST':
            # Process the form data if it's a POST request
            form = RemoteReferralForm(request.POST, instance=referral)
            
            if form.is_valid():
                # If a referral record exists, update it
                if referral:
                    referral = form.save(commit=False)
                    referral.patient = patient
                    referral.visit = visit
                    referral.data_recorder = data_recorder
                    referral.save()
                    messages.success(request, '')
                else:
                    # If no referral record exists, create a new one
                    form.instance.patient = patient
                    form.instance.visit = visit
                    form.instance.data_recorder = data_recorder
                    form.save()
                    messages.success(request, '')
                
                # Redirect to a success page or another view
                return redirect(reverse('kahama_save_remotesconsultation_notes', args=[patient_id, visit_id]))
            else:
                messages.error(request, 'Please correct the errors in the form.')
        else:
            # If it's a GET request, initialize the form with existing data (if any)
            form = RemoteReferralForm(instance=referral)
        
        context['form'] = form
        return render(request, 'kahama_template/save_remotereferral.html', context)
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return render(request, 'kahama_template/save_remotereferral.html', context)
    
    
@login_required    
def save_remoteprocedure(request, patient_id, visit_id):
    patient = get_object_or_404(RemotePatient, id=patient_id)
    visit = get_object_or_404(RemotePatientVisits, id=visit_id)
    procedures = RemoteService.objects.filter(category='Procedure')
    consultation_notes = RemotePatientDiagnosisRecord.objects.filter(patient=patient_id, visit=visit_id)  
    previous_procedures = RemoteProcedure.objects.filter(patient_id=patient_id)
    context = {
        'patient': patient, 
        'visit': visit, 
        'procedures': procedures,
        'previous_procedures': previous_procedures,
        'consultation_notes': consultation_notes,
    }   
    try:
        if request.method == 'POST':
            # Get the list of procedure names, descriptions, and images from the form
            names = request.POST.getlist('name[]')
            descriptions = request.POST.getlist('description[]')
            images = request.FILES.getlist('image[]')  # Get list of image files

            # Validate if all required fields are present
            if not all(names) or not all(descriptions):
                messages.error(request, 'Please fill out all required fields.')
                return render(request, 'kahama_template/procedure_template.html', context)            

            # Loop through the submitted data to add or update each procedure
            for name, description, image in zip(names, descriptions, images):
                # Check if a RemoteProcedure record already exists for this patient on the specified visit
                existing_procedure = RemoteProcedure.objects.filter(patient_id=patient_id, visit_id=visit_id, name_id=name).first()

                if existing_procedure:
                    # If a procedure exists, update it
                    existing_procedure.description = description                  
                    existing_procedure.doctor = request.user.staff                 
                    existing_procedure.image = image  # Update image field
                    existing_procedure.save()
                    messages.success(request, '')
                else:
                    RemoteProcedure.objects.create(
                        patient_id=patient_id,
                        visit_id=visit_id,
                        doctor = request.user.staff ,
                        name_id=name,
                        description=description,
                        image=image,  # Add image field
                    )                    
            messages.success(request, '')
            return redirect(reverse('kahama_save_remotesconsultation_notes', args=[patient_id, visit_id]))  # Change 'success_page' to your success page URL name
        else:
            # If request method is not POST, render the corresponding template
            return render(request, 'kahama_template/procedure_template.html', context)
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')        
        return render(request, 'kahama_template/procedure_template.html', context)
    


@login_required
def save_observation(request, patient_id, visit_id):
    patient = get_object_or_404(RemotePatient, id=patient_id)
    visit = get_object_or_404(RemotePatientVisits, id=visit_id)
    data_recorder = request.user.staff
    record_exists = RemoteObservationRecord.objects.filter(patient_id=patient_id, visit_id=visit_id).first()
    consultation_notes = RemotePatientDiagnosisRecord.objects.filter(patient=patient_id, visit=visit_id)    
    context = {'patient': patient, 
               'visit': visit, 
               'consultation_notes': consultation_notes, 
               'record_exists': record_exists
               }
    if request.method == 'POST':
        form = RemoteObservationRecordForm(request.POST)
        if form.is_valid():
            description = form.cleaned_data['observation_notes']
            try:
                if record_exists:
                    # If a record exists, update it
                    observation_record = RemoteObservationRecord.objects.get(patient_id=patient_id, visit_id=visit_id)
                    observation_record.observation_notes = description
                    observation_record.data_recorder = data_recorder
                    observation_record.save()
                    messages.success(request, '')
                else:
                    # If no record exists, create a new one
                    RemoteObservationRecord.objects.create(
                        patient=patient,
                        visit=visit,
                        data_recorder=data_recorder,
                        observation_notes=description,
                    )
                    messages.success(request, '')
                return redirect(reverse('kahama_save_remotesconsultation_notes', args=[patient_id, visit_id]))
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            messages.error(request, 'Please fill out all required fields.')
    else:
        form = RemoteObservationRecordForm(initial={'observation_notes': record_exists.observation_notes if record_exists else ''})

    context['form'] = form
    return render(request, 'kahama_template/observation_template.html', context)

@login_required
def save_laboratory(request, patient_id, visit_id):
    patient = get_object_or_404(RemotePatient, id=patient_id)
    visit = get_object_or_404(RemotePatientVisits, id=visit_id)
    remote_service = RemoteService.objects.filter(category='Laboratory')
    data_recorder = request.user.staff
    previous_results = RemoteLaboratoryOrder.objects.filter(patient=patient)
    consultation_notes = RemotePatientDiagnosisRecord.objects.filter(patient=patient_id, visit=visit_id)  
    # Check if the laboratory order already exists for this patient on the specified visit
    laboratory_order = RemoteLaboratoryOrder.objects.filter(patient=patient, visit=visit).first()
    context = {'patient': patient,
               'visit': visit, 
               'previous_results': previous_results, 
               'consultation_notes': consultation_notes, 
               'remote_service': remote_service
               } 

    if request.method == 'POST':
        # Retrieve the list of investigation names, descriptions, and results from the form data
        investigation_names = request.POST.getlist('investigation_name[]')
        descriptions = request.POST.getlist('description[]')

        try:
            for name, description in zip(investigation_names, descriptions):
                # If the laboratory order already exists, update it
                if laboratory_order:
                    laboratory_order.data_recorder = data_recorder         
                    laboratory_order.name_id = name         
                    laboratory_order.result = description
                    laboratory_order.data_recorder=data_recorder
                    laboratory_order.save()
                    messages.success(request, '')
                else:
                    # If no laboratory order exists, create a new one
                    RemoteLaboratoryOrder.objects.create(
                        data_recorder=data_recorder,
                        patient=patient,
                        visit=visit,
                        name_id=name,
                        result=description
                    )
                    messages.success(request, '')
            # Redirect to a success page or another view
            return redirect(reverse('kahama_save_remotesconsultation_notes_next', args=[patient_id, visit_id])) 
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

    return render(request, 'kahama_template/laboratory_template.html', context)


    
@csrf_exempt
@require_POST
def add_remoteprescription(request):
    try:
        patient_id = request.POST.get('patient_id')
        visit_id = request.POST.get('visit_id')
        medicines = request.POST.getlist('medicine[]')
        doses = request.POST.getlist('dose[]')
        frequencies = request.POST.getlist('frequency[]')
        durations = request.POST.getlist('duration[]')
        quantities = request.POST.getlist('quantity[]')
        entered_by = request.user.staff

        patient = RemotePatient.objects.get(id=patient_id)
        visit = RemotePatientVisits.objects.get(id=visit_id)

        for i in range(len(medicines)):
            medicine = RemoteMedicine.objects.get(id=medicines[i])
            quantity_used_str = quantities[i]

            if quantity_used_str is None:
                return JsonResponse({'status': 'error', 'message': f'Invalid quantity for {medicine.drug_name}. Quantity cannot be empty.'})

            try:
                quantity_used = int(quantity_used_str)
            except ValueError:
                return JsonResponse({'status': 'error', 'message': f'Invalid quantity for {medicine.drug_name}. Quantity must be a valid number.'})

            if quantity_used < 0:
                return JsonResponse({'status': 'error', 'message': f'Invalid quantity for {medicine.drug_name}. Quantity must be a non-negative number.'})

            if medicine.is_clinic_stock:
                remain_quantity = medicine.remain_quantity

                if remain_quantity is not None and quantity_used > remain_quantity:
                    return JsonResponse({'status': 'error', 'message': f'Insufficient stock for {medicine.drug_name}. Only {remain_quantity} available.'})

                if remain_quantity is not None:
                    medicine.remain_quantity -= quantity_used
                    medicine.save()

            RemotePrescription.objects.create(
                patient=patient,
                medicine=medicine,
                entered_by=entered_by,
                visit=visit,
                dose=doses[i],
                frequency=PrescriptionFrequency.objects.get(id=frequencies[i]),
                duration=durations[i],
                quantity_used=quantity_used,
            )

        return JsonResponse({'status': 'success', 'message': 'Prescription saved.'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    

    
@login_required
def patient_observation_view(request):
    template_name = 'kahama_template/manage_observation.html'    
    # Query to retrieve the latest procedure record for each patient
    observations = RemoteObservationRecord.objects.filter(
        patient=OuterRef('id')
    ).order_by('-created_at')
    # Query to retrieve patients with their corresponding procedure (excluding patients without observations)
    patients_with_observations = RemotePatient.objects.annotate(
        observation_name=Subquery(observations.values('imaging__name')[:1]),      
    ).filter(observation_name__isnull=False)    
  
    data = patients_with_observations.values(
        'id', 'mrn', 'observation_description',
       
    )
    return render(request, template_name, {'data': data})

@login_required
def patient_observation_history_view(request, mrn):
    patient = get_object_or_404(RemotePatient, mrn=mrn)    
    # Retrieve all procedures for the specific patient
    observations = RemoteObservationRecord.objects.filter(patient=patient)
    patient_observations =  Service.objects.filter(type_service='Imaging')    
    context = {
        'patient': patient,
        'observations': observations,
        'patient_observations': patient_observations,
    }
    return render(request, 'kahama_template/manage_patient_observation.html', context)


@login_required
def patient_laboratory_view(request):
    # Get distinct (patient, visit) combinations with latest result date
    distinct_lab_sets = (
        RemoteLaboratoryOrder.objects
        .values('patient_id', 'visit_id')
        .annotate(latest_date=Max('created_at'))
        .order_by('-latest_date')
    )

    patient_lab_data = []

    for entry in distinct_lab_sets:
        patient_id = entry['patient_id']
        visit_id = entry['visit_id']
        latest_date = entry['latest_date']

        lab_tests = RemoteLaboratoryOrder.objects.filter(
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

    return render(request, 'kahama_template/manage_lab_result.html', context)



@login_required
def patient_lab_details_view(request, mrn, visit_number):
    # Fetch the patient with a prefetch query to reduce database hits
    patient = get_object_or_404(RemotePatient.objects.prefetch_related('remotelaboratoryorder_set'), mrn=mrn)
    visit = get_object_or_404(RemotePatientVisits, vst=visit_number)
    
    # Retrieve lab results efficiently
    lab_results = list(patient.remotelaboratoryorder_set.filter(visit__vst=visit_number))

    # Get the first data recorder if lab results exist
    lab_done_by = lab_results[0].data_recorder if lab_results else None

    context = {
        'patient': patient,
        'visit': visit,
        'lab_done_by': lab_done_by,
        'lab_results': lab_results,
    }

    return render(request, 'kahama_template/lab_details.html', context)

@login_required
def discharge_details_view(request, patient_id, visit_id):
    # Fetch the patient
    patient = get_object_or_404(RemotePatient, id=patient_id)

    # Fetch the visit
    visit = get_object_or_404(RemotePatientVisits, id=visit_id)
    consultation_notes = RemotePatientDiagnosisRecord.objects.filter(patient=patient_id, visit=visit_id)  
    
    # Fetch the discharge note related to this visit
    discharge_note = get_object_or_404(RemoteDischargesNotes, patient=patient, visit=visit)

    context = {
        'patient': patient,
        'visit': visit,
        'consultation_notes': consultation_notes,
        'discharge_note': discharge_note,
    }

    return render(request, 'kahama_template/discharge_details.html', context)


@login_required
def patient_lab_result_history_view(request, mrn):
    patient = get_object_or_404(RemotePatient, mrn=mrn)    
    # Retrieve all procedures for the specific patient
    lab_results = RemoteLaboratoryOrder.objects.filter(patient=patient)
    patient_lab_results =  Service.objects.filter(type_service='Laboratory')    
    context = {
        'patient': patient,
        'lab_results': lab_results,
        'patient_lab_results': patient_lab_results,
    }
    return render(request, 'kahama_template/manage_patient_lab_result.html', context)


    
@login_required
def save_remotesconsultation_notes_next(request, patient_id, visit_id):
    try:
        # Retrieve the patient and visit objects
        patient = get_object_or_404(RemotePatient, pk=patient_id)
        visit = get_object_or_404(RemotePatientVisits, patient=patient_id, id=visit_id)
        doctor_plan_note = RemoteConsultationNotes.objects.filter(patient=patient_id, visit=visit).first()
        data_recorder = request.user.staff

        # Retrieve the consultation note object if it exists, otherwise create a new one
        consultation_note, created = RemotePatientDiagnosisRecord.objects.get_or_create(patient=patient, visit=visit)

        # Retrieve all provisional and final diagnoses
        provisional_diagnoses = Diagnosis.objects.all()
        final_diagnoses = Diagnosis.objects.all()

        # Get the IDs of the provisional and final diagnoses associated with the consultation note
        provisional_diagnosis_ids = consultation_note.provisional_diagnosis.values_list('id', flat=True)
        final_diagnosis_ids = consultation_note.final_diagnosis.values_list('id', flat=True)

        # Initialize doctor_plan to None to avoid UnboundLocalError
        doctor_plan = None

        # Retrieve the doctor plan from the query string
        if request.method == 'POST':
            final_diagnosis = request.POST.getlist('final_diagnosis[]')
            doctor_plan = request.POST.get('doctor_plan')            
            if not consultation_note:
                consultation_note = RemotePatientDiagnosisRecord.objects.create(patient=patient, visit=visit)
                consultation_note.data_recorder = data_recorder
            consultation_note.final_diagnosis.set(final_diagnosis)
            consultation_note.save()

            # Add success message
            messages.success(request, '')

            # Redirect based on the doctor's plan
            if doctor_plan == 'Prescription':
                return redirect(reverse('kahama_save_prescription', args=[patient_id, visit_id]))
            elif doctor_plan == 'Laboratory':
                return redirect(reverse('kahama_save_remotesconsultation_notes', args=[patient_id, visit_id]))
            elif doctor_plan == 'Referral':
                return redirect(reverse('kahama_save_remotereferral', args=[patient_id, visit_id]))
            elif doctor_plan == 'Counselling':
                return redirect(reverse('kahama_save_remote_counseling', args=[patient_id, visit_id]))
            elif doctor_plan == 'Procedure':
                return redirect(reverse('kahama_save_remoteprocedure', args=[patient_id, visit_id]))
            elif doctor_plan == 'Observation':
                return redirect(reverse('kahama_save_observation', args=[patient_id, visit_id]))
            elif doctor_plan == 'Discharge':
                return redirect(reverse('kahama_save_remote_discharges_notes', args=[patient_id, visit_id]))

        # Update doctor_plan in context if request is POST
        context = {
            'provisional_diagnoses': provisional_diagnoses,
            'final_diagnoses': final_diagnoses,
            'patient': patient,
            'visit': visit,
            'consultation_note': consultation_note,
            'provisional_diagnosis_ids': provisional_diagnosis_ids,
            'final_diagnosis_ids': final_diagnosis_ids,
            'doctor_plan_note': doctor_plan_note,
            'doctor_plan': doctor_plan,  # Include the value of doctor_plan
        }
        return render(request, 'kahama_template/add_patientprovisional_diagnosis.html', context)

    except Exception as e:
        messages.error(request, f'Error: {str(e)}')

        # Context for exception cases
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
        return render(request, 'kahama_template/add_patientprovisional_diagnosis.html', context)

    


@login_required
@csrf_exempt
def appointment_view(request):
    try:
        if request.method == 'POST':
            # Extract data from the request
            doctor_id = request.POST.get('doctor')
            patient_id = request.POST.get('patient_id')
            visit_id = request.POST.get('visit_id')
            date_of_consultation = request.POST.get('date_of_consultation')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            description = request.POST.get('description')

            # Get the currently logged-in staff member
            created_by = request.user.staff

            # Retrieve objects from database
            visit = get_object_or_404(RemotePatientVisits, id=visit_id)
            doctor = get_object_or_404(Staffs, id=doctor_id)
            patient = get_object_or_404(RemotePatient, id=patient_id)

            # Create a Consultation instance
            consultation = RemoteConsultation(
                doctor=doctor,
                visit=visit,
                patient=patient,
                appointment_date=date_of_consultation,
                start_time=start_time,
                end_time=end_time,
                description=description,
                created_by=created_by  # Set the created_by field
            )
            consultation.save()

            # Return JSON response indicating success
            return JsonResponse({'success': True, 'message': 'Appointment successfully created'})

        # Handle invalid requests
        return JsonResponse({'success': False, 'message': 'Invalid request'})

    except IntegrityError as e:
        # Handle integrity errors (e.g., duplicate key)
        return JsonResponse({'success': False, 'message': str(e)})

    except Exception as e:
        # Handle any other unexpected exceptions
        return JsonResponse({'success': False, 'message': str(e)})
    
  

 
@login_required    
def save_remote_discharges_notes(request, patient_id, visit_id):
    patient = get_object_or_404(RemotePatient, id=patient_id)
    visit = get_object_or_404(RemotePatientVisits, id=visit_id)
    consultation_notes = RemotePatientDiagnosisRecord.objects.filter(patient=patient_id, visit=visit_id)    
    remote_discharges_notes = RemoteDischargesNotes.objects.filter(patient=patient, visit=visit).first()  
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
            form = RemoteDischargesNotesForm(request.POST, instance=remote_discharges_notes)
            if form.is_valid():
                remote_discharges_notes = form.save(commit=False)
                remote_discharges_notes.patient = patient
                remote_discharges_notes.visit = visit
                remote_discharges_notes.data_recorder = data_recorder
                remote_discharges_notes.save()
                messages.success(request, '')
                return redirect(reverse('kahama_save_remotesconsultation_notes', args=[patient_id, visit_id]))  # Redirect to the next view
            else:
                messages.error(request, 'Please correct the errors in the form.')
        else:
            form = RemoteDischargesNotesForm(instance=remote_discharges_notes)        
        # Prepare context for rendering the template
        context['form'] = form
        return render(request, 'kahama_template/disrcharge_template.html', context)    
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return render(request, 'kahama_template/disrcharge_template.html', context)

@login_required    
def patient_statistics(request):
    current_year = datetime.now().year
    year_range = range(current_year, current_year - 10, -1)
    context = {
        'year_range': year_range,
        'current_year': current_year,
        # Other context variables...
    }
    return render(request, 'kahama_template/reports_comprehensive.html', context)


@login_required
def search_report(request):
    if request.method == 'POST' and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        # Get the report type and year from the request
        report_type = request.POST.get('report_type')
        year = request.POST.get('year')

        # Define a dictionary to map report types to their corresponding HTML templates
        report_templates = {
            'patient_type_reports': 'kahama_template/patient_type_report_table.html',
            'patient_company_wise_reports': 'kahama_template/company_wise_reports_table.html',
            'patient_lab_result_reports': 'kahama_template/laboratory_report_table.html',
            'patient_procedure_reports': 'kahama_template/procedure_report_table.html',
            'patient_referral_reports': 'kahama_template/referral_reports_table.html',
            'patient_pathology_reports': 'kahama_template/pathology_record_report_table.html',
            # Add more report types here as needed
        }

        # Check if the report type is valid
        if report_type in report_templates:
            # Render the corresponding HTML template based on the report type
            html_result = render_report(report_type, year)
            return JsonResponse({'html_result': html_result})
        else:
            # Return error response if the report type is invalid
            return JsonResponse({'error': 'Invalid report type'})


def render_report(report_type, year):
    if report_type == 'patient_type_reports':       
         # Define the list of all patient types
        all_patient_types = ['National Staff', 'International Staff', 'National Visitor', 'International Visitor', 'Unknown Status', 'Others']

        # Query the database to get patient counts grouped by patient type and month
        patients_by_type = (
            RemotePatient.objects.filter(created_at__year=year)
            .values('patient_type')
            .annotate(month=ExtractMonth('created_at'))
            .annotate(num_patients=Count('id'))
        )

        # Organize the data into a dictionary
        patient_type_reports = {}
        for patient_type in all_patient_types:
            # Initialize counts for each month
            patient_type_reports[patient_type] = [0] * 12

        for patient in patients_by_type:
            patient_type = patient['patient_type']
            month = patient['month']
            num_patients = patient['num_patients']

            if month is not None:
                month_index = month - 1  # ExtractMonth returns month as an integer
                patient_type_reports[patient_type][month_index] = num_patients

        # Prepare data for rendering in template
        context = {
            'patient_type_reports': patient_type_reports,
            'months': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        }
        return render_to_string('kahama_template/patient_type_report_table.html', context)
    
    elif report_type == 'patient_company_wise_reports':    
        # Get all distinct company names
        all_companies = RemoteCompany.objects.values_list('name', flat=True)

        # Query the database to get patient counts grouped by company and month
        patients_by_company = (
            RemotePatient.objects.filter(created_at__year=year)
            .values('company__name')
            .annotate(month=ExtractMonth('created_at'))
            .annotate(num_patients=Count('id'))
        )

        # Organize the data into a dictionary
        company_reports = {company: [0] * 12 for company in all_companies}
        for patient in patients_by_company:
            company_name = patient['company__name']
            month = patient['month']
            num_patients = patient['num_patients']

            if month is not None:
                month_index = month - 1  # ExtractMonth returns month as an integer
                company_reports[company_name][month_index] = num_patients

        # Prepare data for rendering in template
        context = {
            'company_reports': company_reports,
            'months': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        }
        return render_to_string('kahama_template/company_wise_reports_table.html', context)
    
    elif report_type == 'patient_lab_result_reports':      

        # Get all services with the laboratory category
        laboratory_services = RemoteService.objects.filter(category='Laboratory')

        # Query the database to get patient counts grouped by laboratory category and month
        laboratories_by_month = (
            RemoteLaboratoryOrder.objects.filter(created_at__year=year)
            .annotate(month=ExtractMonth('created_at'))
            .values('name__name', 'month')
            .annotate(num_patients=Count('id'))
        )

        # Organize the data into a dictionary
        laboratory_reports = {}
        for laboratory_service in laboratory_services:
            laboratory_name = laboratory_service.name
            laboratory_reports[laboratory_name] = [0] * 12  # Initialize counts for each month

        for laboratory in laboratories_by_month:
            laboratory_name = laboratory['name__name']
            month = laboratory['month']
            num_patients = laboratory['num_patients']

            if month is not None:
                month_index = int(month) - 1
                laboratory_reports[laboratory_name][month_index] = num_patients

        # Prepare data for rendering in template
        context = {
            'laboratory_reports': laboratory_reports,
            'months': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        }

        return render_to_string('kahama_template/laboratory_report_table.html', context)
    
    
    elif report_type == 'patient_procedure_reports':      

        # Get all services with the procedure category
        procedure_services = RemoteService.objects.filter(category='Procedure')
        # Query the database to get patient counts grouped by procedure category and month
        procedures_by_month = (
            RemoteProcedure.objects.filter(created_at__year=year)
            .annotate(month=ExtractMonth('created_at'))
            .values('name__name', 'month')
            .annotate(num_patients=Count('id'))
        )

        # Organize the data into a dictionary
        procedure_reports = {}
        for procedure_service in procedure_services:
            procedure_name = procedure_service.name
            procedure_reports[procedure_name] = [0] * 12  # Initialize counts for each month

        for procedure in procedures_by_month:
            procedure_name = procedure['name__name']
            month = procedure['month']
            num_patients = procedure['num_patients']

            if month is not None:
                month_index = int(month) - 1
                procedure_reports[procedure_name][month_index] = num_patients

        # Prepare data for rendering in template
        context = {
            'procedure_reports': procedure_reports,
            'months': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        }

        return render_to_string('kahama_template/procedure_report_table.html', context)
    
    elif report_type == 'patient_referral_reports':
        # Fetch data for patient referral report and render corresponding HTML template
        referrals = RemoteReferral.objects.filter(created_at__year=year)
        context = {'referrals': referrals}
        return render_to_string('kahama_template/referral_reports_table.html', context)
    
    elif report_type == 'patient_pathology_reports':
        # Get all distinct Pathodology Record names for the given year
        all_pathology_records = PathodologyRecord.objects.values_list('name', flat=True)
        # Query the database to get patient counts grouped by Pathodology Record and month for the given year
        patients_by_pathology_record = (
            PathodologyRecord.objects.filter(remoteconsultationnotes__created_at__year=year)
            .annotate(month=ExtractMonth('remoteconsultationnotes__created_at'))
            .values('name', 'month')
            .annotate(num_patients=Count('remoteconsultationnotes__id'))
        )

        # Organize the data into a dictionary
        pathology_record_reports = {record: [0] * 12 for record in all_pathology_records}
        for patient in patients_by_pathology_record:
            pathology_record_name = patient['name']
            month = patient['month']
            num_patients = patient['num_patients']

            if month is not None:
                month_index = month - 1  # ExtractMonth returns month as an integer
                pathology_record_reports[pathology_record_name][month_index] = num_patients

        # Prepare data for rendering in template
        context = {
            'pathology_record_reports': pathology_record_reports,
            'months': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        }
        return render_to_string('kahama_template/pathology_record_report_table.html',context)
    
 
 
@login_required    
def edit_lab_result(request, patient_id, visit_id, lab_id):
    # Retrieve patient and visit objects
    patient = get_object_or_404(RemotePatient, id=patient_id)
    visit = get_object_or_404(RemotePatientVisits, id=visit_id)            

    procedures = RemoteLaboratoryOrder.objects.filter(patient=patient, visit=visit, id=lab_id).first()
    
    # Prepare context for rendering the template
    context = {
        'patient': patient, 
        'visit': visit,
        'procedures': procedures,
    }
    
    # Handle form submission
    if request.method == 'POST':        
        form = RemoteLaboratoryOrderForm(request.POST, instance=procedures)
        
        # Check if a record already exists for the patient and visit
        if procedures:
            # If a record exists, update it
            if form.is_valid():
                try:
                    # Track the user who edited the record
                    procedures.data_recorder = request.user.staff   # Set the staff member who edited
                    form.save()  # Save the updated record
                    messages.success(request, 'Laboratory result updated successfully!')
                except ValidationError as e:
                    messages.error(request, f'Validation Error: {e}')
            else:
                messages.error(request, 'Please correct the errors in the form.')
        else:
            # If no record exists, create a new one
            form.instance.patient = patient          
            form.instance.visit = visit
            form.instance.data_recorder = request.user.staff   # Set the staff member who added the record
            if form.is_valid():
                try:
                    form.save()
                    messages.success(request, 'Laboratory result added successfully!')
                except ValidationError as e:
                    messages.error(request, f'Validation Error: {e}')
            else:
                messages.error(request, 'Please correct the errors in the form.')

        # Redirect to the appropriate page after saving
        return redirect(reverse('kahama_patient_lab_result_history_view', args=[patient.mrn]))
   
    else:
        # If it's a GET request, initialize the form with existing data (if any)
        form = RemoteLaboratoryOrderForm(instance=procedures)   
    
    # Add the form to the context
    context['form'] = form    
    return render(request, 'kahama_template/edit_lab_result.html', context)


@login_required    
def edit_procedure_result(request, patient_id, visit_id, procedure_id):
    # Retrieve patient and visit objects
    patient = get_object_or_404(RemotePatient, id=patient_id)
    visit = get_object_or_404(RemotePatientVisits, id=visit_id)            

    procedures = RemoteProcedure.objects.filter(patient=patient, visit=visit, id=procedure_id).first()
    
    # Prepare context for rendering the template
    context = {
        'patient': patient, 
        'visit': visit,
        'procedures': procedures,
    }
    
    # Handle form submission
    if request.method == 'POST':        
        form = RemoteProcedureForm(request.POST, instance=procedures)
        
        # Check if a record already exists for the patient and visit
        if procedures:
            # If a record exists, update it
            if form.is_valid():
                try:
                    # Track the user who edited the record
                    procedures.data_recorder = request.user.staff   # Set the staff member who edited
                    form.save()  # Save the updated record
                    messages.success(request, 'Procedure result updated successfully!')
                except ValidationError as e:
                    messages.error(request, f'Validation Error: {e}')
            else:
                messages.error(request, 'Please correct the errors in the form.')
        else:
            # If no record exists, create a new one
            form.instance.patient = patient          
            form.instance.visit = visit
            form.instance.data_recorder = request.user.staff   # Set the staff member who added the record
            if form.is_valid():
                try:
                    form.save()
                    messages.success(request, 'Procedure result added successfully!')
                except ValidationError as e:
                    messages.error(request, f'Validation Error: {e}')
            else:
                messages.error(request, 'Please correct the errors in the form.')

        # Redirect to the appropriate page after saving
        return redirect(reverse('kahama_patient_procedure_history_view_mrn', args=[patient.mrn]))
   
    else:
        # If it's a GET request, initialize the form with existing data (if any)
        form = RemoteProcedureForm(instance=procedures)   
    
    # Add the form to the context
    context['form'] = form    
    return render(request, 'kahama_template/edit_procedure_result.html', context)





