

from django.http import  JsonResponse
from django.shortcuts import  get_object_or_404
from clinic.models import  ConsultationNotes, Diagnosis, DiseaseRecode,  FamilyMedicalHistory,    Medicine,  PathodologyRecord,  PatientHealthCondition, PatientMedicationAllergy, PatientSurgery, PatientVisits, PatientVital, Patients, Prescription, Procedure,  RemoteCompany, RemoteConsultation, RemoteLaboratoryOrder, RemoteMedicine, RemoteObservationRecord, RemotePatient, RemoteProcedure, RemoteReferral, RemoteService,Service, Staffs

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import F
from django.contrib.auth.decorators import login_required



@csrf_exempt
@require_POST
def delete_medicine(request, medicine_id):
    # Get the medicine object or return 404 if not found
    medicine = get_object_or_404(Medicine, id=medicine_id)

    try:
        # Delete the medicine
        medicine.delete()
        message = f"Medicine '{medicine.name}' deleted successfully."
        return JsonResponse({'success': True, 'message': message})
    except Exception as e:
        # Handle any exception or error during deletion
        return JsonResponse({'success': False, 'message': str(e)})




@csrf_exempt  # Use csrf_exempt decorator for simplicity in this example. For a production scenario, consider using csrf protection.
def delete_observation(request):
    if request.method == 'POST':
        try:
            observation_id = request.POST.get('observation_id')
            # Delete procedure record
            observation = RemoteObservationRecord.objects.get(id=observation_id)
            observation.delete()
            return JsonResponse({'success': True, 'message': f'observation record for {observation.imaging} deleted successfully.'})
        except RemoteObservationRecord.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid observation ID.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {e}'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

@csrf_exempt  # Use csrf_exempt decorator for simplicity in this example. For a production scenario, consider using csrf protection.
def delete_lab_result(request):
    if request.method == 'POST':
        try:
            lab_result_id = request.POST.get('lab_result_id')
            # Delete procedure record
            lab_result = RemoteLaboratoryOrder.objects.get(id=lab_result_id)
            lab_result.delete()
            return JsonResponse({'success': True, 'message': f'lab result record for {lab_result.name} deleted successfully.'})
        except RemoteLaboratoryOrder.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid lab result ID.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {e}'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

@csrf_exempt  # Use csrf_exempt decorator for simplicity in this example. For a production scenario, consider using csrf protection.
def delete_referral(request):
    if request.method == 'POST':
        try:
            referral_id = request.POST.get('referral_id')

            # Delete procedure record
            referral_record = RemoteReferral.objects.get(id=referral_id)
            referral_record.delete()

            return JsonResponse({'success': True, 'message': f'Referral record for {referral_record} deleted successfully.'})
        except Procedure.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid Referral ID.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {e}'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


@csrf_exempt  # Use this if CSRF middleware is not handled in your JavaScript (not recommended for production)
def delete_disease_record(request):
    if request.method == 'POST':
        disease_id = request.POST.get('disease_id')  # Extract the ID from POST data
        if disease_id:
            try:
                disease = DiseaseRecode.objects.get(id=disease_id)
                disease.delete()
                return JsonResponse({'status': 'success', 'message': 'Disease deleted successfully'})
            except DiseaseRecode.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Disease not found'}, status=404)
        return JsonResponse({'status': 'error', 'message': 'Invalid disease ID'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@login_required
@csrf_exempt
def delete_remotecompany(request):
    if request.method == 'POST':
        company_id = request.POST.get('company_id')
        if not company_id:
            return JsonResponse({'success': False, 'error': 'Company ID not provided'})
        
        try:
            company = get_object_or_404(RemoteCompany, pk=company_id)  # Replace `Company` with your actual model
            company.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})



@require_POST
def delete_service(request):
    try:
        # Get the frequency ID from the POST data
        service_id = request.POST.get('service_id')
        # Delete the frequency from the database
        service = RemoteService.objects.get(id=service_id)
        service.delete()
        return JsonResponse({'success': True,'message': 'service deleted successfully'})
    except Service.DoesNotExist:
        return JsonResponse({'success': False,'message': 'service not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@csrf_exempt      
@require_POST
def delete_patient_visit(request, patient_visit_id):
    try:
        patient_visit = get_object_or_404(PatientVisits, pk=patient_visit_id)
        patient_visit.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}) 
    
@csrf_exempt      
@require_POST
def delete_prescription(request, prescription_id):
    try:
        prescription = get_object_or_404(Prescription, pk=prescription_id)
        deleted_quantity = prescription.quantity_used
        
        with transaction.atomic():
            # Perform deletion
            prescription.delete()

            # Adjust MedicineInventory
            Medicine.objects.filter(medicine=prescription.medicine).update(
                remain_quantity=F('remain_quantity') + deleted_quantity
            )

        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}) 
    


    
@csrf_exempt      
@require_POST
def delete_patient_vital(request, vital_id):
    try:
        vital = get_object_or_404(PatientVital, pk=vital_id)
        vital.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}) 
    
@csrf_exempt
@require_POST
def delete_diagnosis(request):
    try:
        # Extract and trim the diagnosis_id from the POST data
        diagnosis_id = request.POST.get('diagnosis_id', '').strip()

        # Check if diagnosis_id is provided
        if not diagnosis_id:
            return JsonResponse({'status': 'error', 'message': 'Diagnosis ID is required'})

        # Get the diagnosis object or return a 404 error
        diagnosis = get_object_or_404(Diagnosis, pk=diagnosis_id)

        # Delete the diagnosis
        diagnosis.delete()

        # Return success response
        return JsonResponse({'status': 'success', 'message': 'Diagnosis deleted successfully'})
    except Diagnosis.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Diagnosis not found'})
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
    
@csrf_exempt      
@require_POST
def delete_ConsultationNotes(request, consultation_id):
    try:
        consultation = get_object_or_404(ConsultationNotes, pk=consultation_id)
        consultation.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}) 
    

    

@csrf_exempt    
def delete_procedure(request):
    if request.method == 'POST':
        # Retrieve the procedure ID from the POST data
        procedure_id = request.POST.get('procedure_id')
        print(procedure_id)
        try:
            # Query and delete the procedure object from the database
            procedure = RemoteProcedure.objects.get(id=procedure_id)
            procedure.delete()
            # Return a success response
            return JsonResponse({'status': 'success', 'message': 'Procedure deleted successfully.'})
        except Exception as e:
            # Return an error response if deletion fails
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        # Return an error response for requests other than POST
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})     
    
# View for deleting a result
@csrf_exempt
def delete_result(request):
    if request.method == 'POST':
        try:
            result_id = request.POST.get('result_id')    
            result = RemoteLaboratoryOrder.objects.get(id=result_id)
            result.delete()     
            deleted_result_id = result_id
            # Return a JSON response indicating success
            return JsonResponse({'success': True, 'result_id': deleted_result_id})
        except Exception as e:
            # Return a JSON response indicating failure
            return JsonResponse({'success': False, 'message': f'Error deleting result: {str(e)}'})
    else:
        # Return a JSON response indicating failure
        return JsonResponse({'success': False, 'message': 'Invalid request method'})    
     

    
@csrf_exempt
@login_required
def delete_pathology_record(request):
    if request.method == 'POST':
        try:
            pathology_record_id = request.POST.get('pathology_record_id')
            pathology_record = PathodologyRecord.objects.get(id=pathology_record_id)
            pathology_record_name = pathology_record.name  # Capture the name before deletion
            pathology_record.delete()
            # Return a JSON response indicating success and include the name of the deleted record
            return JsonResponse({'success': True, 'message': f'Pathology record "{pathology_record_name}" deleted successfully.'})
        except PathodologyRecord.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Pathology record not found.'})
        except Exception as e:
            # Return a JSON response indicating failure
            return JsonResponse({'success': False, 'message': f'Error deleting result: {str(e)}'})
    else:
        # Return a JSON response indicating failure
        return JsonResponse({'success': False, 'message': 'Invalid request method'})

      
@csrf_exempt
def delete_drug(request):
    if request.method == 'POST':
        try:
            medicine_id = request.POST.get('medicine_id')    
            result = RemoteMedicine.objects.get(id=medicine_id)
            result.delete()     
            deleted_medicine_id = medicine_id
            # Return a JSON response indicating success
            return JsonResponse({'success': True, 'medicine_id': deleted_medicine_id})
        except Exception as e:
            # Return a JSON response indicating failure
            return JsonResponse({'success': False, 'message': f'Error deleting result: {str(e)}'})
    else:
        # Return a JSON response indicating failure
        return JsonResponse({'success': False, 'message': 'Invalid request method'})    

@csrf_exempt    
def delete_health_record(request):
    if request.method == 'POST':
        record_id = request.POST.get('record_id')
        # Delete the record from the database
        try:
            record = PatientHealthCondition.objects.get(id=record_id)
            record.delete()
            return JsonResponse({'message': 'Record deleted successfully'})
        except PatientHealthCondition.DoesNotExist:
            return JsonResponse({'error': 'Record not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt    
def delete_medication_allergy_record(request):
    if request.method == 'POST':
        record_id = request.POST.get('record_id')
        # Delete the record from the database
        try:
            record = PatientMedicationAllergy.objects.get(id=record_id)
            record.delete()
            return JsonResponse({'message': 'Record deleted successfully'})
        except PatientMedicationAllergy.DoesNotExist:
            return JsonResponse({'error': 'Record not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400) 

@csrf_exempt    
def delete_surgery_history_record(request):
    if request.method == 'POST':
        record_id = request.POST.get('record_id')
        # Delete the record from the database
        try:
            record = PatientSurgery.objects.get(id=record_id)
            record.delete()
            return JsonResponse({'message': 'Record deleted successfully'})
        except PatientSurgery.DoesNotExist:
            return JsonResponse({'error': 'Record not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)    

@csrf_exempt
def delete_family_medical_history_record(request):
    if request.method == 'POST':
        record_id = request.POST.get('record_id')
        # Delete the record from the database
        try:
            record = FamilyMedicalHistory.objects.get(id=record_id)
            record.delete()
            return JsonResponse({'message': 'Record deleted successfully'})
        except FamilyMedicalHistory.DoesNotExist:
            return JsonResponse({'error': 'Record not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)             