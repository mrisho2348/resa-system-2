from django.http import  JsonResponse
from django.shortcuts import redirect, render,get_object_or_404
from .models import Category, Company, Consultation, ConsultationNotes, Diagnosis, DiseaseRecode, Equipment, EquipmentMaintenance,  InsuranceCompany, InventoryItem,  Medicine,  PathodologyRecord,  PatientVisits, PatientVital, Patients, Prescription, Procedure, QualityControl, Reagent, ReagentUsage, Referral, RemoteCompany, RemoteService,  Service, Staffs, Supplier, UsageHistory
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import F
from django.contrib.auth.decorators import login_required


def delete_staff(request, staff_id):
    # Retrieve the staff object or return a 404 if not found
    staff = get_object_or_404(Staffs, id=staff_id)

    if request.method == 'POST':
        # Perform the deletion
        staff.delete()
        # Redirect to a success page or a list view
        messages.success(request, 'staff deleted successfully.')
        return redirect('clinic:manage_staff')  # Replace 'staff_list' with your actual list view name

    return render(request, 'delete/delete_staff_confirm.html', {'staff': staff})


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
    
    
def delete_insurance(request, insurance_id):
    insurance = get_object_or_404(InsuranceCompany, pk=insurance_id)

    if request.method == 'POST':
        try:
            # Delete the InsuranceCompany object
            insurance.delete()

            messages.success(request, 'Insurance details deleted successfully!')
            return redirect('admin_manage_insurance')  # Replace 'your_redirect_url' with the appropriate URL name

        except Exception as e:
            messages.error(request, f'An error occurred: {e}')

    return render(request, 'delete/delete_insurance_confirmation.html', {'insurance': insurance})



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


def delete_disease_record(request, disease_id):
    record = get_object_or_404(DiseaseRecode, pk=disease_id)

    if request.method == 'POST':
        try:
            # Delete the DiseaseRecode object
            record.delete()
            messages.success(request, 'Disease record deleted successfully!')
            return redirect('admin_manage_disease')  # Replace with the appropriate URL name

        except Exception as e:
            messages.error(request, f'An error occurred: {e}')

    return render(request, 'delete/delete_disease_record_confirmation.html', {'record': record})

def delete_company(request, company_id):
    company = get_object_or_404(RemoteCompany, pk=company_id)

    if request.method == 'POST':
        try:
            # Delete the Company object
            company.delete()

            messages.success(request, 'Company deleted successfully!')
            return redirect('admin_manage_company')  # Replace 'your_redirect_url' with the appropriate URL name
        except Exception as e:
            messages.error(request, f'An error occurred: {e}')

    return render(request, 'delete/company_delete_confirmation_template.html', {'company': company})


def delete_pathodology(request, pathodology_id):
    pathodology = get_object_or_404(PathodologyRecord, pk=pathodology_id)

    if request.method == 'POST':
        try:
            # Delete the PathodologyRecord object
            pathodology.delete()

            messages.success(request, 'Pathodology record deleted successfully!')
            return redirect('admin_manage_pathology')  # Replace 'your_redirect_url' with the appropriate URL name

        except Exception as e:
            messages.error(request, f'An error occurred: {e}')

    return render(request, 'delete/pathodology_delete_confirmation.html', {'pathodology': pathodology})


@require_POST
def delete_consultation(request, appointment_id):
    # Get the Consultation object
    consultation = get_object_or_404(Consultation, pk=appointment_id)

    # Perform deletion
    consultation.delete()

    # Redirect to the Consultation  page
    return redirect('clinic:appointment_list')
 

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
def delete_category(request):
    try:
        category_id = request.POST.get('category_id')
        category = get_object_or_404(Category, pk=category_id)
        category.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
       
@csrf_exempt
@require_POST
def delete_supplier(request):
    supplier_id = request.POST.get('supplier_id')
    if not supplier_id:
        return JsonResponse({'status': 'error', 'message': 'Missing supplier ID'})
    
    try:
        supplier = get_object_or_404(Supplier, pk=supplier_id)
        supplier.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    

      
@csrf_exempt
@require_POST
def delete_inventory_item(request):
    try:
        # Retrieve the inventory ID from the POST data
        inventory_id = request.POST.get('inventory_id')
        
        if not inventory_id:
            return JsonResponse({'status': 'error', 'message': 'Missing inventory ID'})
        
        # Retrieve the inventory object or return a 404 error if not found
        inventory_item = get_object_or_404(InventoryItem, pk=inventory_id)
        
        # Delete the inventory item
        inventory_item.delete()
        
        # Return a success response
        return JsonResponse({'status': 'success'})
    except Exception as e:
        # Return an error response with the exception message
        return JsonResponse({'status': 'error', 'message': str(e)})
    

@csrf_exempt      
@require_POST
def delete_remote_service(request, service_id):
    try:
        service = get_object_or_404(RemoteService, pk=service_id)
        service.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}) 
        
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
@require_POST
def delete_remotecompany(request):
    try:
        # Get company_id from POST data
        company_id = request.POST.get('company_id')

        # Check if company_id is provided
        if not company_id:
            return JsonResponse({'success': False, 'error': 'Company ID is required'})

        # Try to get the company and delete it
        company = Company.objects.get(id=company_id)
        company.delete()

        # Return success response
        return JsonResponse({'success': True})

    except Company.DoesNotExist:
        # Return error response if company does not exist
        return JsonResponse({'success': False, 'error': 'Company does not exist'})
    except Exception as e:
        # Return error response for any other exceptions
        return JsonResponse({'success': False, 'error': str(e)}) 
    
    
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
def delete_maintenance(request):
    try:
        maintenance_id = request.POST.get('maintenance_id')
        maintenance = get_object_or_404(EquipmentMaintenance, pk=maintenance_id)
        maintenance.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    
@csrf_exempt
@login_required
def delete_insurance_company(request):
    try:
        if request.method == 'POST':
            company_id = request.POST.get('company_id')
            company = InsuranceCompany.objects.get(id=company_id)
            company.delete()
            return JsonResponse({'success': True, 'message': 'Successfully deleted'})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid request method'})
    except InsuranceCompany.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Insurance company not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})    
    
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
def delete_diagnosis(request, diagnosis_id):
    try:
        diagnosis = get_object_or_404(Diagnosis, pk=diagnosis_id)
        diagnosis.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}) 
    
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
    
    
@csrf_exempt
@require_POST
def delete_quality_control(request):
    try:
        # Retrieve the control ID from the POST data
        control_id = request.POST.get('control_id')
        
        if not control_id:
            return JsonResponse({'status': 'error', 'message': 'Missing control ID'})
        
        # Retrieve the quality control object or return a 404 error if not found
        control = get_object_or_404(QualityControl, pk=control_id)
        
        # Delete the quality control
        control.delete()
        
        # Return a success response
        return JsonResponse({'status': 'success'})
    except Exception as e:
        # Return an error response with the exception message
        return JsonResponse({'status': 'error', 'message': str(e)})
    

       
@csrf_exempt
@require_POST
def delete_usage_history(request):
    history_id = request.POST.get('history_id')
    if not history_id:
        return JsonResponse({'status': 'error', 'message': 'Missing history ID'})
    
    try:
        usage_history = get_object_or_404(UsageHistory, pk=history_id)
        usage_history.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    
@csrf_exempt
@require_POST
def delete_reagent_used(request):
    try:
        # Retrieve the reagent usage ID from the POST data
        reagentusage_id = request.POST.get('reagent_usage_id')
        
        if not reagentusage_id:
            return JsonResponse({'status': 'error', 'message': 'Missing reagent usage ID'})
        
        # Ensure database operations are atomic
        with transaction.atomic():
            # Retrieve the reagent usage object or return a 404 error if not found
            usage = get_object_or_404(ReagentUsage, pk=reagentusage_id)
            
            # Update the inventory item
            quantity_used = usage.quantity_used
            inventory_item = usage.reagent
            inventory_item.remaining_quantity += quantity_used
            inventory_item.save()
            
            # Delete the usage record
            usage.delete()
        
        # Return a success response
        return JsonResponse({'status': 'success'})
    except Exception as e:
        # Return an error response with the exception message
        return JsonResponse({'status': 'error', 'message': str(e)})
    
    
    