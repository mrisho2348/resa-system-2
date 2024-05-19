import calendar
from datetime import datetime
import json
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from clinic.forms import RemoteCounselingForm, RemoteDischargesNotesForm, RemoteObservationRecordForm, RemoteReferralForm, YearSelectionForm
from clinic.models import ChiefComplaint, Company, Diagnosis, FamilyMedicalHistory, HealthRecord, Medicine, Notification, PathodologyRecord, PatientHealthCondition, PatientLifestyleBehavior, PatientMedicationAllergy, PatientSurgery, PrescriptionFrequency, PrimaryPhysicalExamination, RemoteCompany, RemoteConsultation, RemoteConsultationNotes, RemoteCounseling, RemoteDischargesNotes, RemoteLaboratoryOrder, RemoteMedicine, RemoteObservationRecord, RemotePatient, RemotePatientDiagnosisRecord, RemotePatientVisits, RemotePatientVital, RemotePrescription, RemoteProcedure, RemoteReferral, RemoteService, SecondaryPhysicalExamination, Service, Staffs
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.db.models import OuterRef, Subquery
from django.db.models import Count
from django.db.models import Q
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from django.core.exceptions import ValidationError
from django.db.models.functions import ExtractMonth  # Add this import
from django.template.loader import render_to_string
import numpy as np

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
            
            # Create PatientLifestyleBehavior object
            lifestyle_behavior = PatientLifestyleBehavior.objects.create(
                patient=patient,
                smoking=smoking,
                alcohol_consumption=alcohol_consumption,
                weekly_exercise_frequency=weekly_exercise_frequency,
                healthy_diet=healthy_diet,
                stress_management=stress_management,
                sufficient_sleep=sufficient_sleep,
            )

            # Check if the patient has surgery history
            if surgery_history == 'yes':
                surgery_names = request.POST.getlist('surgery_name[]')
                surgery_dates = request.POST.getlist('date_of_surgery[]')
                for name, date in zip(surgery_names, surgery_dates):
                    surgery = PatientSurgery.objects.create(
                        patient=patient,
                        surgery_name=name,
                        surgery_date=date,
                    )

            # Check if the patient has chronic illness
            if chronic_illness == 'yes':
                health_conditions = request.POST.getlist('health_condition[]')
                health_condition_notes = request.POST.getlist('health_condition_notes[]')
                for condition, notes in zip(health_conditions, health_condition_notes):
                    patient_health_condition = PatientHealthCondition.objects.create(
                        patient=patient,
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
                        medicine_name_id=medicine_name_id.id,
                        reaction=reaction
                    )

            # Redirect to the appropriate URL upon successful data saving
            return redirect(reverse('kahamahmis:save_patient_visit_save', args=[patient_id]))

    except RemotePatient.DoesNotExist:
        # Handle the case where the patient ID is not valid
        messages.error(request, 'Patient not found.')
        return redirect(reverse('kahamahmis:save_patient_health_information', args=[patient_id])) 

    except Exception as e:
        # Handle other exceptions
        messages.error(request, f'Error adding patient health information: {str(e)}')

    # If the request method is not POST or if there's an error, render the form again
    return render(request, 'kahama_template/add_patient_health_condition_form.html', {'patient': patient,'all_medicines':all_medicines})

@login_required
def health_record_list(request):
    records = HealthRecord.objects.all()
    return render(request, 'kahama_template/healthrecord_list.html', {'records': records})

@csrf_exempt
def save_health_record(request):
    if request.method == 'POST':
        try:
            # Extract data from POST request
            name = request.POST.get('name')
            health_record_id = request.POST.get('health_record_id')  # Check if health record ID is provided
            
            if health_record_id:  # If health record ID is provided, it's an edit operation
                # Get the existing health record object
                health_record = HealthRecord.objects.get(pk=health_record_id)
                # Update the existing health record
                health_record.name = name
                health_record.save()
            else:  # If no health record ID is provided, it's an add operation
                # Create a new health record
                HealthRecord.objects.create(name=name)
            
            # Return success response
            return JsonResponse({'success': True,'message': 'Successfully saved.'}, status=200)
        except Exception as e:
            # Return error response if an exception occurs
            return JsonResponse({'success': False, 'message': str(e)})
    else:
        # Return error response for invalid requests
        return JsonResponse({'success': False, 'message': 'Invalid request'})
    
    
@csrf_exempt      
@require_POST
def delete_healthrecord(request, health_record_id):
    try:
        health_record = get_object_or_404(HealthRecord, pk=health_record_id)
        health_record.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})      
    
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
        if request.method == 'POST':
            # Extract data from the request
            patient_id = request.POST.get('patient_id')
            visit_id = request.POST.get('visit_id')
            health_record_id = request.POST.get('chief_complain_name')
            other_chief_complaint = request.POST.get('other_chief_complaint')
            duration = request.POST.get('chief_complain_duration')        

            # Create a new ChiefComplaint object
            chief_complaint = ChiefComplaint(
                duration=duration,
                patient_id=patient_id,
                visit_id=visit_id
            )

            # Set the appropriate fields based on the provided data
            if health_record_id == "other":
                if ChiefComplaint.objects.filter(visit_id=visit_id,other_complaint=other_chief_complaint).exists():
                    return JsonResponse({'error': 'A ChiefComplaint with the same health record already exists for this visit'}, status=400)
                chief_complaint.other_complaint = other_chief_complaint
            else:
                # Check if a ChiefComplaint with the same health_record_id already exists for the given visit_id
                if ChiefComplaint.objects.filter(health_record_id=health_record_id, visit_id=visit_id).exists():
                    return JsonResponse({'error': 'A ChiefComplaint with the same health record already exists for this visit'}, status=400)
               
                chief_complaint.health_record_id = health_record_id          

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
                'id': chief_complaint.id,
                'health_record': health_record_data,
                'duration': chief_complaint.duration,
            }

            if other_chief_complaint:
                response_data['other_complaint'] = other_chief_complaint

            return JsonResponse(response_data, status=200)

        # If request method is not POST, return an error response
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    except Exception as e:
        # Catch any exceptions and return an error response
        return JsonResponse({'error': str(e)}, status=500)

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
        chief_complaint = get_object_or_404(ChiefComplaint, id=chief_complaint_id)
        
        # Delete the ChiefComplaint
        chief_complaint.delete()
        
        # Return a success response
        return JsonResponse({'message': 'Chief complaint deleted successfully'})
    except Exception as e:
        # If an error occurs, return an error response
        return JsonResponse({'error': str(e)}, status=500)   
    
@csrf_exempt
def add_primary_physical_examination(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            primary_physical_id = data.get('primary_physical_id')  # Check if primary_physical_id is provided

            if primary_physical_id:  # If primary_physical_id is provided, update the existing record
                primary_examination = PrimaryPhysicalExamination.objects.get(id=primary_physical_id)
            else:  # Otherwise, create a new record
                # Check if a record already exists for the patient on the specified visit
                existing_record = PrimaryPhysicalExamination.objects.filter(patient_id=data.get('patient_id'), visit_id=data.get('visit_id')).first()
                if existing_record:
                    return JsonResponse({'success': False, 'error': 'A record already exists for this patient on the specified visit.'})
                
                primary_examination = PrimaryPhysicalExamination()

            # Extract data from the JSON
            primary_examination.patient_id = data.get('patient_id')
            primary_examination.visit_id = data.get('visit_id')
            primary_examination.patent_airway = data.get('airway')
            primary_examination.notpatient_explanation = data.get('explanation')
            primary_examination.breathing = data.get('breathing')
            primary_examination.normal_breathing = data.get('normalBreathing')
            primary_examination.abnormal_breathing = data.get('abnormalBreathing')
            primary_examination.circulating = data.get('circulating')
            primary_examination.normal_circulating = data.getlist('normalCirculating[]')
            primary_examination.abnormal_circulating = data.get('abnormalCirculating')
            primary_examination.gcs = data.get('gcs')
            primary_examination.rbg = data.get('rbg')
            primary_examination.pupil = data.get('pupil')
            primary_examination.pain_score = data.get('painScore')
            primary_examination.avpu = data.get('avpu')
            primary_examination.exposure = data.get('exposure')
            primary_examination.normal_exposure = data.get('temperatures')
            primary_examination.abnormal_exposure = data.get('abnormalities')

            # Save the PrimaryPhysicalExamination object
            primary_examination.save()

            # Return success response
            return JsonResponse({'success': True})

        except Exception as e:
            # Return error response
            return JsonResponse({'success': False, 'error': str(e)})

    else:
        # Return error response for unsupported request method
        return JsonResponse({'success': False, 'error': 'Unsupported request method'})
     
@login_required
def save_remotesconsultation_notes(request, patient_id, visit_id):
    doctor = request.user.staff
    patient = get_object_or_404(RemotePatient, pk=patient_id)
    visit = get_object_or_404(RemotePatientVisits, patient=patient_id, id=visit_id)
    
    try:
        health_conditions = PatientHealthCondition.objects.filter(patient_id=patient_id)
        surgery_info = PatientSurgery.objects.filter(patient_id=patient_id)
        family_history = FamilyMedicalHistory.objects.filter(patient_id=patient_id)
        allergies = PatientMedicationAllergy.objects.filter(patient_id=patient_id)
        behaviors = PatientLifestyleBehavior.objects.get(patient_id=patient_id)
        patient_vitals = RemotePatientVital.objects.filter(patient=patient_id, visit=visit)
        health_records = HealthRecord.objects.all()
        patient_surgeries = PatientSurgery.objects.filter(patient=patient_id)
    except Exception as e:
        patient_vitals = None  
        surgery_info = None  
        family_history = None  
        allergies = None  
        health_conditions = None  
        health_records = None  
        patient_surgeries = None  
        behaviors = None  
       
    provisional_diagnoses = Diagnosis.objects.all()
    consultation_note = RemoteConsultationNotes.objects.filter(patient=patient_id, visit=visit).first()
    provisional_record, created = RemotePatientDiagnosisRecord.objects.get_or_create(patient=patient, visit=visit)
    provisional_diagnosis_ids = provisional_record.provisional_diagnosis.values_list('id', flat=True)
    primary_examination = PrimaryPhysicalExamination.objects.filter(patient=patient_id, visit=visit).first()
    previous_counselings = RemoteCounseling.objects.filter(patient=patient_id, visit=visit)
    previous_discharges = RemoteDischargesNotes.objects.filter(patient=patient_id, visit=visit)
    previous_observations = RemoteObservationRecord.objects.filter(patient=patient_id, visit=visit)
    previous_lab_orders = RemoteLaboratoryOrder.objects.filter(patient=patient_id, visit=visit)
    previous_prescriptions = RemotePrescription.objects.filter(patient=patient_id, visit=visit)
    previous_referrals = RemoteReferral.objects.filter(patient=patient_id, visit=visit)
    previous_procedures = RemoteProcedure.objects.filter(patient=patient_id, visit=visit)
    secondary_examination = SecondaryPhysicalExamination.objects.filter(patient_id=patient_id, visit_id=visit_id).first()    
    pathology_records = PathodologyRecord.objects.all()   
    range_51 = range(51)
    range_301 = range(301)
    range_101 = range(101)
    range_15 = range(3, 16)
    temps = np.arange(start=0, stop=51, step=0.1)
    
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
        'health_conditions': health_conditions,
        'surgery_info': surgery_info,
        'provisional_diagnoses': provisional_diagnoses,
        'provisional_diagnosis_ids': provisional_diagnosis_ids,
        'family_history': family_history,
        'behaviors': behaviors,
        'allergies': allergies,
        'patient': patient,
        'visit': visit,
        'patient_vitals': patient_vitals,
        'patient_surgeries': patient_surgeries,
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
                provisional_record = RemotePatientDiagnosisRecord.objects.create(patient=patient, visit=visit)
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
                existing_record = PrimaryPhysicalExamination.objects.filter(patient_id=patient_id, visit_id=visit_id).first()
                if existing_record:
                    messages.error(request, f'A record already exists for this patient on the specified visit')
                    return render(request, 'kahama_template/add_consultation_notes.html', context)
                PrimaryPhysicalExamination.objects.create(
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
                existing_record = SecondaryPhysicalExamination.objects.filter(patient_id=patient_id, visit_id=visit_id).first()
                if existing_record:
                    messages.error(request, f'A record already exists for this patient on the specified visit')
                    return render(request, 'kahama_template/add_consultation_notes.html', context)
                # If record doesn't exist, create a new one
                SecondaryPhysicalExamination.objects.create(
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
                existing_record = RemoteConsultationNotes.objects.filter(patient_id=patient_id, visit_id=visit_id).first()
                if existing_record:
                    messages.error(request, f'A record already exists for this patient on the specified visit')
                    return render(request, 'kahama_template/add_consultation_notes.html', context)
                consultation_note = RemoteConsultationNotes()
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
            return redirect(reverse('kahamahmis:save_remotesconsultation_notes_next', args=[patient_id, visit_id]))
            # Add similar logic for other plans
            
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            # Return an appropriate response or render a template with an error message
            return render(request, 'kahama_template/add_consultation_notes.html', context)
    else:
        # If GET request, render the template for adding consultation notes
        return render(request, 'kahama_template/add_consultation_notes.html', context)
    

@login_required    
def save_counsel(request, patient_id, visit_id):
    # Retrieve patient and visit objects
    patient = get_object_or_404(RemotePatient, id=patient_id)
    visit = get_object_or_404(RemotePatientVisits, id=visit_id)              
    data_recorder = request.user.staff
    # Retrieve existing remote counseling record if it exists
    remote_counseling = RemoteCounseling.objects.filter(patient=patient, visit=visit).first()
    
    # Prepare context for rendering the template
    context = {
        'patient': patient, 
        'visit': visit,
        'remote_counseling': remote_counseling,
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
                    messages.success(request, 'Remote counseling updated successfully.')
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
                    messages.success(request, 'Remote counseling saved successfully.')
                except ValidationError as e:
                    messages.error(request, f'Validation Error: {e}')
            else:
                messages.error(request, 'Please correct the errors in the form.')

        # Redirect to the appropriate page after saving
        return redirect(reverse('kahamahmis:save_remotesconsultation_notes', args=[patient_id, visit_id]))
   
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
        context = {'patient': patient, 'visit': visit, 'referral': referral}  

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
                    messages.success(request, 'Remote referral updated successfully.')
                else:
                    # If no referral record exists, create a new one
                    form.instance.patient = patient
                    form.instance.visit = visit
                    form.instance.data_recorder = data_recorder
                    form.save()
                    messages.success(request, 'Remote referral saved successfully.')
                
                # Redirect to a success page or another view
                return redirect(reverse('kahamahmis:save_remotesconsultation_notes', args=[patient_id, visit_id]))
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
    previous_procedures = RemoteProcedure.objects.filter(patient_id=patient_id)
    context = {
        'patient': patient, 
        'visit': visit, 
        'procedures': procedures,
        'previous_procedures': previous_procedures,
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
                    existing_procedure.image = image  # Update image field
                    existing_procedure.save()
                    messages.success(request, 'Remote procedure updated successfully.')
                else:
                    RemoteProcedure.objects.create(
                        patient_id=patient_id,
                        visit_id=visit_id,
                        name_id=name,
                        description=description,
                        image=image,  # Add image field
                    )                    
            messages.success(request, 'Remote procedure saved successfully.')
            return redirect(reverse('kahamahmis:save_remotesconsultation_notes', args=[patient_id, visit_id]))  # Change 'success_page' to your success page URL name
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
    context = {'patient': patient, 'visit': visit, 'record_exists': record_exists}
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
                    messages.success(request, 'Remote observation record updated successfully.')
                else:
                    # If no record exists, create a new one
                    RemoteObservationRecord.objects.create(
                        patient=patient,
                        visit=visit,
                        data_recorder=data_recorder,
                        observation_notes=description,
                    )
                    messages.success(request, 'Remote observation record saved successfully.')
                return redirect(reverse('kahamahmis:save_remotesconsultation_notes', args=[patient_id, visit_id]))
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

    # Check if the laboratory order already exists for this patient on the specified visit
    laboratory_order = RemoteLaboratoryOrder.objects.filter(patient=patient, visit=visit).first()
    context = {'patient': patient, 'visit': visit, 'previous_results': previous_results, 'remote_service': remote_service} 

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
                    laboratory_order.save()
                    messages.success(request, 'Laboratory order updated successfully.')
                else:
                    # If no laboratory order exists, create a new one
                    RemoteLaboratoryOrder.objects.create(
                        data_recorder=data_recorder,
                        patient=patient,
                        visit=visit,
                        name_id=name,
                        result=description
                    )
                    messages.success(request, 'Laboratory order saved successfully.')
            # Redirect to a success page or another view
            return redirect(reverse('kahamahmis:save_remotesconsultation_notes', args=[patient_id, visit_id]))
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

    return render(request, 'kahama_template/laboratory_template.html', context)


def get_unit_price(request):
    if request.method == 'GET':
        medicine_id = request.GET.get('medicine_id')
        try:
            medicine = RemoteMedicine.objects.get(pk=medicine_id)
            unit_price = medicine.unit_cost
            return JsonResponse({'unit_price': unit_price})
        except RemoteMedicine.DoesNotExist:
            return JsonResponse({'error': 'Medicine not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)

    
def get_drug_division_status(request):
    if request.method == 'GET':
        medicine_id = request.GET.get('medicine_id')
        try:
            medicine = RemoteMedicine.objects.get(pk=medicine_id)
            dividable = medicine.dividable
            return JsonResponse({'dividable': dividable})
        except RemoteMedicine.DoesNotExist:
            return JsonResponse({'error': 'Medicine not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method or missing parameter'}, status=400) 
    
def get_medicine_formulation(request):
    if request.method == 'GET':
        medicine_id = request.GET.get('medicine_id')
        try:
            medicine = RemoteMedicine.objects.get(pk=medicine_id)
            formulation = medicine.formulation_unit
            return JsonResponse({'formulation': formulation})
        except RemoteMedicine.DoesNotExist:
            return JsonResponse({'error': 'Medicine not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method or missing parameter'}, status=400) 
    
def get_formulation_unit(request):
    if request.method == 'GET':
        medicine_id = request.GET.get('medicine_id')
        try:
            medicine = RemoteMedicine.objects.get(pk=medicine_id)
            formulation_unit = medicine.formulation_unit
            return JsonResponse({'formulation_unit': formulation_unit})
        except RemoteMedicine.DoesNotExist:
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
        patient = RemotePatient.objects.get(id=patient_id)
        visit = RemotePatientVisits.objects.get(id=visit_id)

        # Save prescriptions only if inventory check passes
        for i in range(len(medicines)):
            medicine = RemoteMedicine.objects.get(id=medicines[i])
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
            prescription = RemotePrescription.objects.create(
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
    
def medicine_dosage(request):
    if request.method == 'GET' and 'medicine_id' in request.GET:
        medicine_id = request.GET.get('medicine_id')

        try:
            medicine = RemoteMedicine.objects.get(id=medicine_id)
            dosage = medicine.dosage
            return JsonResponse({'dosage': dosage})
        except RemoteMedicine.DoesNotExist:
            return JsonResponse({'error': 'Medicine not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)  
    
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
    template_name = 'kahama_template/manage_lab_result.html'    
    # Query to retrieve the latest procedure record for each patient
    Labs = RemoteLaboratoryOrder.objects.filter(
        patient=OuterRef('id')
    ).order_by('-created_at')
    # Query to retrieve patients with their corresponding procedure (excluding patients without observations)
    patients_with_lab_result = RemotePatient.objects.annotate(
        lab_result_name=Subquery(Labs.values('name__name')[:1]),
    ).filter(lab_result_name__isnull=False)    
  
    data = patients_with_lab_result.values(
        'id', 'mrn', 'lab_result_name'
    )
    return render(request, template_name, {'data': data})   

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


# View to verify prescriptions
@csrf_exempt
def verify_prescriptions(request):
    if request.method == 'POST':
        visit_number = request.POST.get('visit_number')
        # Perform logic to mark prescriptions as verified for the given visit_number
        # Example:
        try:
            prescriptions = RemotePrescription.objects.filter(visit__vst=visit_number)
            for prescription in prescriptions:
                prescription.verified = 'verified'
                prescription.save()
            return JsonResponse({'message': 'Prescriptions verified successfully.'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request.'}, status=400)

# View to issue prescriptions
@csrf_exempt
def issue_prescriptions(request):
    if request.method == 'POST':
        visit_number = request.POST.get('visit_number')
        # Perform logic to mark prescriptions as issued for the given visit_number
        # Example:
        try:
            prescriptions = RemotePrescription.objects.filter(visit__vst=visit_number)
            for prescription in prescriptions:
                prescription.issued = 'issued'
                prescription.save()
            return JsonResponse({'message': 'RemotePrescriptions issued successfully.'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request.'}, status=400)

# View to update payment status
@csrf_exempt
def update_payment_status(request):
    if request.method == 'POST':
        visit_number = request.POST.get('visit_number')
        # Perform logic to update payment status for the given visit_number
        # Example:
        try:
            prescriptions = RemotePrescription.objects.filter(visit__vst=visit_number)
            for prescription in prescriptions:
                prescription.status = 'Paid'
                prescription.save()
            return JsonResponse({'message': 'Payment status updated successfully.'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request.'}, status=400)

    
# View to unverify prescriptions
@csrf_exempt
def unverify_prescriptions(request):
    if request.method == 'POST':
        visit_number = request.POST.get('visit_number')
        # Perform logic to mark prescriptions as unverified for the given visit_number
        # Example:
        try:
            prescriptions = RemotePrescription.objects.filter(visit__vst=visit_number)
            for prescription in prescriptions:
                prescription.verified = 'Not Verified'
                prescription.status = 'Unpaid'
                prescription.issued = 'Not Issued'
                prescription.save()
            return JsonResponse({'message': 'RemotePrescriptions unverified successfully.'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request.'}, status=400)

# View to unissue prescriptions
@csrf_exempt
def unissue_prescriptions(request):
    if request.method == 'POST':
        visit_number = request.POST.get('visit_number')
        # Perform logic to mark prescriptions as not issued for the given visit_number
        # Example:
        try:
            prescriptions = RemotePrescription.objects.filter(visit__vst=visit_number)
            for prescription in prescriptions:
                prescription.issued = 'Not Issued'
                prescription.status = 'Unpaid'
                prescription.save()
            return JsonResponse({'message': 'RemotePrescriptions unissued successfully.'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request.'}, status=400)

# View to unpay prescriptions
@csrf_exempt
def unpay_prescriptions(request):
    if request.method == 'POST':
        visit_number = request.POST.get('visit_number')
        # Perform logic to mark prescriptions as unpaid for the given visit_number
        # Example:
        try:
            prescriptions = RemotePrescription.objects.filter(visit__vst=visit_number)
            for prescription in prescriptions:
                prescription.status = 'Unpaid'
                prescription.save()
            return JsonResponse({'message': 'RemotePrescription unpaid successfully.'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request.'}, status=400)
    

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
                    service.nhif_cost = 0
                    service.insurance_cost = 0  
                      
                new_service.save()
                    
                return JsonResponse({'success': True, 'message': 'Service added successfully'})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid request method'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})    
    
    
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

        # Retrieve the doctor plan from the query string
        if request.method == 'POST':          
            final_diagnosis = request.POST.getlist('final_diagnosis[]')
            doctor_plan = request.POST.get('doctor_plan')
            print("Doctor Plan:", doctor_plan)  # Debugging
            if not consultation_note:
                consultation_note = RemotePatientDiagnosisRecord.objects.create(patient=patient, visit=visit)
                consultation_note.data_recorder = data_recorder
            consultation_note.final_diagnosis.set(final_diagnosis)
            consultation_note.save()

            # Add success message
            messages.success(request, 'Consultation notes saved successfully.')

            # Redirect based on the doctor's plan
            if doctor_plan == 'Prescription':
                return redirect(reverse('kahamahmis:save_prescription', args=[patient_id, visit_id]))
            elif doctor_plan == 'Laboratory':
                return redirect(reverse('kahamahmis:save_laboratory', args=[patient_id, visit_id]))
            elif doctor_plan == 'Referral':
                return redirect(reverse('kahamahmis:save_remotereferral', args=[patient_id, visit_id]))
            elif doctor_plan == 'Counselling':
                return redirect(reverse('kahamahmis:save_remote_counseling', args=[patient_id, visit_id]))
            elif doctor_plan == 'Procedure':
                return redirect(reverse('kahamahmis:save_remoteprocedure', args=[patient_id, visit_id]))
            elif doctor_plan == 'Observation':
                return redirect(reverse('kahamahmis:save_observation', args=[patient_id, visit_id]))
            elif doctor_plan == 'Discharge':
                return redirect(reverse('kahamahmis:save_remote_discharges_notes', args=[patient_id, visit_id]))

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
            # Create a Consultation instance
            visit = get_object_or_404(RemotePatientVisits, id=visit_id)
            doctor = get_object_or_404(Staffs, id=doctor_id)
            patient = get_object_or_404(RemotePatient, id=patient_id)
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
            return JsonResponse({'status': 'success', 'message': 'Appointment successfully created'})          

    
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'})

    except IntegrityError as e:      
        return JsonResponse({'status': 'error', 'message': str(e)})
    except Exception as e:    
        return JsonResponse({'status': 'error', 'message': str(e)})
    
  
@csrf_exempt      
@require_POST
def delete_remote_patient(request, patient_id):
    try:
        patient_remote = get_object_or_404(RemotePatient, pk=patient_id)
        patient_remote.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}) 
 
@login_required    
def save_remote_discharges_notes(request, patient_id, visit_id):
    patient = get_object_or_404(RemotePatient, id=patient_id)
    visit = get_object_or_404(RemotePatientVisits, id=visit_id)
    remote_discharges_notes = RemoteDischargesNotes.objects.filter(patient=patient, visit=visit).first()  
    context = {
            'patient': patient,
            'visit': visit,
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
                messages.success(request, 'Remote discharge notes saved successfully.')
                return redirect(reverse('kahamahmis:save_remotesconsultation_notes', args=[patient_id, visit_id]))  # Redirect to the next view
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
def patient_health_info_edit_record(request, patient_id):
    try:
        # Retrieve the patient object
        patient = get_object_or_404(RemotePatient, pk=patient_id)        
        medication_allergies = PatientMedicationAllergy.objects.filter(patient_id=patient_id)
        lifestyle_behavior_instance, created = PatientLifestyleBehavior.objects.get_or_create(patient=patient)
        # Retrieve existing health records for the patient
        family_medical_history = FamilyMedicalHistory.objects.filter(patient=patient)
        patient_health_records = PatientHealthCondition.objects.filter(patient_id=patient_id)
        surgery_history = PatientSurgery.objects.filter(patient_id=patient_id)
        
        if request.method == 'POST':            
            existing_allergies = patient.medication_allergies.all()
            for allergy in existing_allergies:
                allergy_id = str(allergy.id)
                medicine_name = request.POST.get('medicine_name_' + allergy_id)
                reaction = request.POST.get('reaction_' + allergy_id)
                
                # Update existing medication allergies if data is provided
                if medicine_name is not None:
                    allergy.medicine_name = medicine_name
                if reaction is not None:
                    allergy.reaction = reaction
                allergy.save()
                
                # Check if medication allergy should be deleted
                if 'delete_record_' + allergy_id in request.POST:
                    allergy.delete()
            
            # Handle addition of new medication allergies
            if 'new_medicine_name[]' in request.POST:
                new_medicine_names = request.POST.getlist('new_medicine_name[]')
                new_reactions = request.POST.getlist('new_reaction[]')
                
                # Create new medication allergy records
                for medicine_name, reaction in zip(new_medicine_names, new_reactions):
                    new_allergy = PatientMedicationAllergy(patient=patient, medicine_name=medicine_name, reaction=reaction)
                    new_allergy.save()
                
                messages.success(request, f'{len(new_medicine_names)} new medication allergies added successfully.')
            
            
               # Handle chronic illness option
            medication_allergy = request.POST.get('medication_allergy')
            if medication_allergy == 'no':
                # If the patient does not have chronic illness, delete all health records
                patient.medication_allergies.all().delete()
              
            smoking = request.POST.get('smoking')
            alcohol_consumption = request.POST.get('alcohol_consumption')
            weekly_exercise_frequency = request.POST.get('weekly_exercise_frequency')
            healthy_diet = request.POST.get('healthy_diet') == 'on'
            stress_management = request.POST.get('stress_management')
            sufficient_sleep = request.POST.get('sufficient_sleep')

            # Update or create the lifestyle behavior instance
            lifestyle_behavior_instance.smoking = smoking
            lifestyle_behavior_instance.alcohol_consumption = alcohol_consumption
            lifestyle_behavior_instance.weekly_exercise_frequency = weekly_exercise_frequency
            lifestyle_behavior_instance.healthy_diet = healthy_diet
            lifestyle_behavior_instance.stress_management = stress_management
            lifestyle_behavior_instance.sufficient_sleep = sufficient_sleep
            lifestyle_behavior_instance.save()    
            
            for record in family_medical_history:
                record_id = str(record.id)
                condition = request.POST.get('condition_' + record_id)
                relationship = request.POST.get('relationship_' + record_id)
                comments = request.POST.get('comments_' + record_id)
                
                # Update existing record
                record.condition = condition
                record.relationship = relationship
                record.comments = comments
                record.save()
                
                # Check if record should be deleted
                if 'delete_record_' + record_id in request.POST:
                    record.delete()
            
            # Handle addition of new records
            if 'new_condition[]' in request.POST:
                new_conditions = request.POST.getlist('new_condition[]')
                new_relationships = request.POST.getlist('new_relationship[]')
                new_comments = request.POST.getlist('new_comments[]')
                
                for condition, relationship, comments in zip(new_conditions, new_relationships, new_comments):
                    new_record = FamilyMedicalHistory(patient=patient, condition=condition, relationship=relationship, comments=comments)
                    new_record.save()
                
                messages.success(request, f'{len(new_conditions)} new family medical records added successfully.')
                
                
              # Handle chronic illness option
            family_medical_history = request.POST.get('family_medical_history')
            if family_medical_history == 'no':
                # If the patient does not have chronic illness, delete all health records
                patient.family_medical_history.all().delete()    
            
            existing_surgeries = patient.patientsurgery_set.all()
            for surgery in existing_surgeries:
                surgery_id = str(surgery.id)
                surgery_name = request.POST.get('surgery_name_' + surgery_id)            
                date_of_surgery = request.POST.get('date_of_surgery_' + surgery_id)
                
                # Update existing surgery records if data is provided
                if surgery_name is not None:
                    surgery.surgery_name = surgery_name             
                if date_of_surgery is not None:
                    surgery.surgery_date = date_of_surgery
                surgery.save()
                
                # Check if surgery record should be deleted
                if 'delete_record_' + surgery_id in request.POST:
                    surgery.delete()
            
            # Handle addition of new surgery history
            if 'new_surgery_name[]' in request.POST:
                new_surgery_names = request.POST.getlist('new_surgery_name[]')             
                new_dates_of_surgery = request.POST.getlist('new_date_of_surgery[]')
                
                # Create new surgery records
                for name, date in zip(new_surgery_names, new_dates_of_surgery):
                    new_surgery = PatientSurgery(patient=patient, surgery_name=name, surgery_date=date)
                    new_surgery.save()
                
                messages.success(request, f'{len(new_surgery_names)} new surgery records added successfully.')
            
            # Handle surgery history option
            surgery_history = request.POST.get('surgery_history')
            if surgery_history == 'no':
                # If the patient does not have surgery history, delete all surgery records
                patient.patientsurgery_set.all().delete()
                
            # Update existing health records and handle deletion
            for record in patient_health_records:
                record_id = str(record.id)
                health_condition = request.POST.get('health_condition_' + record_id)
                health_condition_notes = request.POST.get('health_condition_notes_' + record_id)
                
                # Update existing records if data is provided
                if health_condition is not None:
                    record.health_condition = health_condition
                if health_condition_notes is not None:
                    record.health_condition_notes = health_condition_notes
                record.save()
                
                # Check if record should be deleted
                if 'delete_record_' + record_id in request.POST:
                    record.delete()
            
            # Handle addition of new health records
            if 'new_health_condition[]' in request.POST:
                new_health_conditions = request.POST.getlist('new_health_condition[]')
                new_health_condition_notes = request.POST.getlist('new_health_condition_notes[]')
                
                # Create new health records
                for condition, notes in zip(new_health_conditions, new_health_condition_notes):
                    new_record = PatientHealthCondition(patient=patient, health_condition=condition, health_condition_notes=notes)
                    new_record.save()
                
                messages.success(request, f'{len(new_health_conditions)} new health records added successfully.')
            
            # Handle chronic illness option
            chronic_illness = request.POST.get('chronic_illness')
            if chronic_illness == 'no':
                # If the patient does not have chronic illness, delete all health records
                patient.health_conditions.all().delete()
                
            if 'save_and_return' in request.POST:
                return redirect('patients_list')
            elif 'save_and_continue_family_health' in request.POST:
                return redirect('kahamahmis:edit_patient_medication_allergy', patient_id=patient.id)
        
        # Prepare context for rendering the template
        context = {
            'patient': patient,
            'patient_health_records': patient_health_records
        }
        
        # Render the template with the prepared context
        return render(request, 'kahama_template/edit_patient_health_condition_form.html', context)
    
    except Exception as e:
        # Handle any exceptions and display error messages
        messages.error(request, f'Error editing patient health record: {str(e)}')
        context = {
            'patient': patient,
            'patient_health_records': patient_health_records,
            'family_medical_history': family_medical_history,
            'surgery_history': surgery_history,
            'medication_allergies': medication_allergies,
            'lifestyle_behavior_instance': lifestyle_behavior_instance,
        }
        
        return render(request, 'kahama_template/edit_patient_health_condition_form.html', context)
    
    

@login_required
def remotemedicine_list(request):
    medicines = RemoteMedicine.objects.all()
    return render(request, 'kahama_template/remotemedicine_list.html', {'medicines': medicines})

@csrf_exempt
def add_remote_medicine(request):
    if request.method == 'POST':
        try:
            # Retrieve data from POST request
            drug_id = request.POST.get('drug_id')  # Check if drug ID is provided
            drug_name = request.POST.get('drug_name')
            drug_type = request.POST.get('drug_type')
            formulation_unit = request.POST.get('formulation_unit')
            manufacturer = request.POST.get('manufacturer')           
            quantity = request.POST.get('quantity')
            dividable = request.POST.get('dividable')
            batch_number = request.POST.get('batch_number')
            expiration_date = request.POST.get('expiration_date')
            unit_cost = request.POST.get('unit_cost')
            buying_price = request.POST.get('buying_price')
            
            # Check if required fields are provided
            if not (drug_name and quantity and buying_price):
                return JsonResponse({'success': False, 'message': 'Missing required fields'})

            # Convert quantity and buying_price to integers
            try:
                quantity = int(quantity)
                buying_price = float(buying_price)
            except ValueError:
                return JsonResponse({'success': False, 'message': 'Invalid quantity or buying price'})

            # If drug ID is provided, it indicates editing existing data
            if drug_id:
                # Get the RemoteMedicine object to edit
                medicine = RemoteMedicine.objects.get(pk=drug_id)
                
                # Update fields with new values
                medicine.drug_name = drug_name
                medicine.drug_type = drug_type
                medicine.formulation_unit = formulation_unit
                medicine.manufacturer = manufacturer                
                medicine.quantity = quantity
                medicine.remain_quantity = quantity
                medicine.dividable = dividable
                medicine.batch_number = batch_number
                medicine.expiration_date = expiration_date
                medicine.unit_cost = unit_cost
                medicine.buying_price = buying_price                
                # Save the changes
                medicine.save()                
                # Return success response
                return JsonResponse({'success': True, 'message': 'Medicine updated successfully'})
            
            else:            
                 # Check if drug name already exists in the database
                if not drug_id and RemoteMedicine.objects.filter(drug_name=drug_name).exists():
                    return JsonResponse({'success': False, 'message': 'Medicine with this name already exists'})
                    # Create RemoteMedicine object for adding new data
                medicine = RemoteMedicine(
                    drug_name=drug_name,
                    drug_type=drug_type,
                    formulation_unit=formulation_unit,
                    manufacturer=manufacturer,            
                    quantity=quantity,
                    remain_quantity=quantity,
                    dividable=dividable,
                    batch_number=batch_number,
                    expiration_date=expiration_date,
                    unit_cost=unit_cost,
                    buying_price=buying_price
                )
                
                # Save the object
                medicine.save()
                
                # Return success response
                return JsonResponse({'success': True, 'message': 'Medicine added successfully'})
        
        except Exception as e:
            # Return error response if an exception occurs
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})

    # If request method is not POST, return error response
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@login_required
def company_registration_view(request, company_id=None):
    try:
        if request.method == 'POST':
            name = request.POST.get('name')
            registration_number = request.POST.get('registration_number')
            address = request.POST.get('address')
            city = request.POST.get('city')
            state = request.POST.get('state')
            country = request.POST.get('country')
            postal_code = request.POST.get('postal_code')
            phone_number = request.POST.get('phone_number')
            email = request.POST.get('email')
            website = request.POST.get('website')
            logo = request.FILES.get('logo') if 'logo' in request.FILES else None

            if company_id:  # Editing existing record
                company = get_object_or_404(Company, pk=company_id)
                company.name = name
                company.registration_number = registration_number
                company.address = address
                company.city = city
                company.state = state
                company.country = country
                company.postal_code = postal_code
                company.phone_number = phone_number
                company.email = email
                company.website = website
                if logo:
                    company.logo = logo
                company.save()
                messages.success(request, 'Company details updated successfully.')
            else:  # Adding new record
                new_company = Company(
                    name=name,
                    registration_number=registration_number,
                    address=address,
                    city=city,
                    state=state,
                    country=country,
                    postal_code=postal_code,
                    phone_number=phone_number,
                    email=email,
                    website=website,
                    logo=logo
                )
                new_company.save()
                messages.success(request, 'Company added successfully.')

            return redirect('registration_success')  # Redirect to success page

        else:
            if company_id:  # Editing existing record
                company = get_object_or_404(Company, pk=company_id)
            else:  # Adding new record
                company = None
            return render(request, 'kahama_template/company_registration.html', {'company': company})
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return render(request, 'kahama_template/company_registration.html')
        
    