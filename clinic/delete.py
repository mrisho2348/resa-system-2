from django.http import  JsonResponse
from django.shortcuts import  get_object_or_404
from .models import    ConsultationNotes, Diagnosis,  Equipment,      Medicine,  PathodologyRecord,  PatientVisits, PatientVital, Patients, Prescription, Procedure,  Reagent,  Referral,    Service

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import F
from django.contrib.auth.decorators import login_required


@csrf_exempt
@require_POST
def delete_medicine(request):
    medicine_id = request.POST.get('medicine_id')

    if not medicine_id:
        return JsonResponse({'success': False, 'message': 'Medicine ID is required.'})

    medicine = get_object_or_404(Medicine, id=medicine_id)

    try:
        medicine_name = medicine.drug_name  # Store the name before deletion
        medicine.delete()
        message = f"Medicine '{medicine_name}' deleted successfully."
        return JsonResponse({'success': True, 'message': message})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
    
@csrf_exempt
@require_POST
def delete_patient(request):
    try:
        # Retrieve the patient ID from the POST data
        patient_id = request.POST.get('patient_id')
        
        if not patient_id:
            return JsonResponse({'status': 'error', 'message': 'Missing patient ID'})
        
        # Retrieve the patient object or return a 404 error if not found
        patient = get_object_or_404(Patients, pk=patient_id)
        
        # Delete the patient
        patient.delete()
        
        # Return a success response
        return JsonResponse({'status': 'success'})
    except Exception as e:
        # Return an error response with the exception message
        return JsonResponse({'status': 'error', 'message': str(e)})


@csrf_exempt  # Use csrf_exempt decorator for simplicity in this example. For a production scenario, consider using csrf protection.
def delete_procedure(request):
    if request.method == 'POST':
        try:
            procedure_id = request.POST.get('procedure_id')

            # Delete procedure record
            procedure_record = Procedure.objects.get(id=procedure_id)
            procedure_record.delete()

            return JsonResponse({'success': True, 'message': f'Procedure record for {procedure_record.name} deleted successfully.'})
        except Procedure.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid procedure ID.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {e}'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

@csrf_exempt  # Use csrf_exempt decorator for simplicity in this example. For a production scenario, consider using csrf protection.
def delete_referral(request):
    if request.method == 'POST':
        try:
            referral_id = request.POST.get('referral_id')

            # Delete procedure record
            referral_record = Referral.objects.get(id=referral_id)
            referral_record.delete()

            return JsonResponse({'success': True, 'message': f'Referral record for {referral_record} deleted successfully.'})
        except Procedure.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid Referral ID.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {e}'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})



@require_POST
def delete_service(request):
    try:
        # Get the frequency ID from the POST data
        service_id = request.POST.get('service_id')
        # Delete the frequency from the database
        service = Service.objects.get(id=service_id)
        service.delete()
        return JsonResponse({'success': True,'message': 'service deleted successfully'})
    except Service.DoesNotExist:
        return JsonResponse({'success': False,'message': 'service not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

 
        
@csrf_exempt
@require_POST
def delete_equipment(request):
    try:
        # Retrieve the equipment ID from the POST data
        equipment_id = request.POST.get('equipment_id')

        if not equipment_id:
            return JsonResponse({'success': False, 'message': 'Missing equipment ID'})
        
        # Retrieve the equipment object or return a 404 error if not found
        equipment = get_object_or_404(Equipment, pk=equipment_id)
        
        # Delete the equipment
        equipment.delete()
        
        # Return a success response
        return JsonResponse({'success': True, 'message': 'Equipment deleted successfully'})
    except Exception as e:
        # Return an error response with the exception message
        return JsonResponse({'success': False, 'message': str(e)})
    
    
@csrf_exempt      
@require_POST
def delete_patient_visit(request):
    try:
        patient_visit_id = request.POST.get('patient_visit_id')
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
@require_POST
def delete_reagent(request):
    try:
        # Retrieve the reagent ID from the POST data
        reagent_id = request.POST.get('reagent_id')
        
        if not reagent_id:
            return JsonResponse({'status': 'error', 'message': 'Missing reagent ID'})
        
        # Retrieve the reagent object or return a 404 error if not found
        reagent = get_object_or_404(Reagent, pk=reagent_id)
        
        # Delete the reagent
        reagent.delete()
        
        # Return a success response
        return JsonResponse({'status': 'success'})
    except Exception as e:
        # Return an error response with the exception message
        return JsonResponse({'status': 'error', 'message': str(e)})
    
    
@csrf_exempt
@require_POST
def delete_patient_vital(request):
    try:
        # Retrieve the vital ID from the POST data
        vital_id = request.POST.get('vital_id')
        
        if not vital_id:
            return JsonResponse({'success': False, 'message': 'Missing vital ID'})
        
        # Retrieve the vital object or return a 404 error if not found
        vital = get_object_or_404(PatientVital, pk=vital_id)
        
        # Delete the vital
        vital.delete()
        
        # Return a success response
        return JsonResponse({'success': True})
    except Exception as e:
        # Return an error response with the exception message
        return JsonResponse({'success': False, 'message': str(e)})    
    

    
@csrf_exempt
@require_POST
def delete_diagnosis(request):
    try:
        diagnosis_id = request.POST.get('diagnosis_id')
        diagnosis = get_object_or_404(Diagnosis, pk=diagnosis_id)
        diagnosis.delete()
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
    

    

    
    
    