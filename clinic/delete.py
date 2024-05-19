

from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render,get_object_or_404


from .models import Category, Consultation, ConsultationFee, ConsultationNotes, Diagnosis, DiagnosticTest, DiseaseRecode, Equipment, EquipmentMaintenance, HealthIssue, HealthRecord, InsuranceCompany, InventoryItem, MedicationPayment, Medicine, MedicineInventory, PathodologyRecord, PathologyDiagnosticTest, PatientDisease, PatientVisits, PatientVital, Patients, Prescription, Procedure, QualityControl, Reagent, ReagentUsage, Referral, RemoteCompany, RemotePatient, RemoteService, Sample, Service, Staffs, Supplier, UsageHistory
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import F



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

def delete_patient(request, patient_id):
    # Retrieve the staff object or return a 404 if not found
    patient = get_object_or_404(Patients, id=patient_id)

    if request.method == 'POST':
        # Perform the deletion
        patient.delete()
        # Redirect to a success page or a list view
        messages.success(request, 'patient deleted successfully.')
        return redirect('clinic:manage_patient')  # Replace 'manage_patient' with your actual list view name

    return render(request, 'delete/delete_patient_confirm.html', {'patient': patient})

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
    
@csrf_exempt
@require_POST
def delete_patient(request, patient_id):
    # Get the medicine object or return 404 if not found
    patient = get_object_or_404(Patients, id=patient_id)

    try:
        # Delete the medicine
        patient.delete()
        message = f"Medicine '{patient.name}' deleted successfully."
        return JsonResponse({'success': True, 'message': message})
    except Exception as e:
        # Handle any exception or error during deletion
        return JsonResponse({'success': False, 'message': str(e)})
    
def delete_insurance(request, insurance_id):
    insurance = get_object_or_404(InsuranceCompany, pk=insurance_id)

    if request.method == 'POST':
        try:
            # Delete the InsuranceCompany object
            insurance.delete()

            messages.success(request, 'Insurance details deleted successfully!')
            return redirect('clinic:manage_insurance')  # Replace 'your_redirect_url' with the appropriate URL name

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
            return redirect('clinic:manage_disease')  # Replace with the appropriate URL name

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
            return redirect('clinic:manage_company')  # Replace 'your_redirect_url' with the appropriate URL name
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
            return redirect('clinic:manage_pathodology')  # Replace 'your_redirect_url' with the appropriate URL name

        except Exception as e:
            messages.error(request, f'An error occurred: {e}')

    return render(request, 'delete/pathodology_delete_confirmation.html', {'pathodology': pathodology})


    
@require_POST
def delete_medicine_inventory(request, inventory_id):
    # Get the MedicineInventory object
    inventory = get_object_or_404(MedicineInventory, pk=inventory_id)

    # Perform deletion
    inventory.delete()

    # Redirect to the medicine inventory page
    return redirect('clinic:medicine_inventory') 

@require_POST
def delete_patient_disease(request, patient_disease_id):
    # Get the PatientDisease object
    patient_disease = get_object_or_404(PatientDisease, pk=patient_disease_id)

    # Perform deletion
    patient_disease.delete()

    # Redirect to the PatientDisease page
    return redirect('clinic:patient_diseases_view') 

@require_POST
def delete_diagnostic_test(request, test_id):
    # Get the MedicineInventory object
    test = get_object_or_404(DiagnosticTest, pk=test_id)

    # Perform deletion
    test.delete()

    # Redirect to the medicine inventory page
    return redirect('clinic:diagnostic_tests')
 
@require_POST
def delete_sample(request, sample_id):
    # Get the MedicineInventory object
    sample = get_object_or_404(Sample, pk=sample_id)

    # Perform deletion
    sample.delete()

    # Redirect to the medicine inventory page
    return redirect('clinic:sample_list') 

@require_POST
def pathology_diagnostic_test_delete(request, test_id):
    # Get the PathologyDiagnosticTest object
    pathology_diagnostic_test = get_object_or_404(PathologyDiagnosticTest, pk=test_id)

    # Perform deletion
    pathology_diagnostic_test.delete()

    # Redirect to the PathologyDiagnosticTest  page
    return redirect('clinic:pathology_diagnostic_test_list')
 
@require_POST
def delete_consultation(request, appointment_id):
    # Get the Consultation object
    consultation = get_object_or_404(Consultation, pk=appointment_id)

    # Perform deletion
    consultation.delete()

    # Redirect to the Consultation  page
    return redirect('clinic:appointment_list')
 
@require_POST
def delete_consultation_fee(request, fee_id):
    # Get the ConsultationFee object
    consultation_fee = get_object_or_404(ConsultationFee, pk=fee_id)

    # Perform deletion
    consultation_fee.delete()

    # Redirect to the ConsultationFee  page
    return redirect('clinic:consultation_fee_list') 

@require_POST
def delete_service(request):
    try:
        # Get the frequency ID from the POST data
        service_id = request.POST.get('service_id')
        # Delete the frequency from the database
        service = Service.objects.get(id=service_id)
        service.delete()
        return JsonResponse({'status': 'success', 'message': 'service deleted successfully'})
    except Service.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'service not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

   
@require_POST
def delete_medication_payment(request, payment_id):
    try:
        # Get the MedicationPayment object
        medication_payment = get_object_or_404(MedicationPayment, pk=payment_id)

        # Store the quantity being deleted for later adjustment
        deleted_quantity = medication_payment.quantity

        with transaction.atomic():
            # Perform deletion
            medication_payment.delete()

            # Adjust MedicineInventory
            MedicineInventory.objects.filter(medicine=medication_payment.medicine).update(
                remain_quantity=F('remain_quantity') + deleted_quantity
            )

        # Redirect to the MedicationPayment
        return redirect('clinic:patient_medicationpayment_history_view_mrn', mrn=medication_payment.patient.mrn)

    except MedicationPayment.DoesNotExist:
        return HttpResponseBadRequest("MedicationPayment not found.")
    

@csrf_exempt      
@require_POST
def delete_category(request, category_id):
    try:
        category = get_object_or_404(Category, pk=category_id)
        category.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}) 
       
@csrf_exempt      
@require_POST
def delete_supplier(request, supplier_id):
    try:
        supplier = get_object_or_404(Supplier, pk=supplier_id)
        supplier.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})  
    

      
@csrf_exempt      
@require_POST
def delete_inventory(request, item_id):
    try:
        item = get_object_or_404(InventoryItem, pk=item_id)
        item.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
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
def delete_equipment(request, equipment_id):
    try:
        equipment = get_object_or_404(Equipment, pk=equipment_id)
        equipment.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}) 
    
    
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
            MedicineInventory.objects.filter(medicine=prescription.medicine).update(
                remain_quantity=F('remain_quantity') + deleted_quantity
            )

        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}) 
    

@csrf_exempt      
@require_POST    
def delete_remotecompany(request, company_id):
    # Your delete logic here
    try:
        company = RemoteCompany.objects.get(id=company_id)
        company.delete()
        return JsonResponse({'success': True})
    except RemoteCompany.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Company does not exist'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})    
    
@csrf_exempt      
@require_POST
def delete_maintenance(request, maintenance_id):
    try:
        maintenance = get_object_or_404(EquipmentMaintenance, pk=maintenance_id)
        maintenance.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}) 
    
@csrf_exempt      
@require_POST
def delete_reagent(request, reagent_id):
    try:
        reagent = get_object_or_404(Reagent, pk=reagent_id)
        reagent.delete()
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
def delete_diagnosis(request, diagnosis_id):
    try:
        diagnosis = get_object_or_404(Diagnosis, pk=diagnosis_id)
        diagnosis.delete()
        return JsonResponse({'status': 'success'})
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
@require_POST
def delete_qualitycontrol(request, control_id):
    try:
        control = get_object_or_404(QualityControl, pk=control_id)
        control.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}) 
    
@csrf_exempt      
@require_POST
def delete_health_issue(request, health_issue_id):
    try:
        health_issue = get_object_or_404(HealthIssue, pk=health_issue_id)
        health_issue.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}) 
       
@csrf_exempt      
@require_POST
def delete_usage_history(request, usage_id):
    try:
        with transaction.atomic():
            usage = get_object_or_404(UsageHistory, pk=usage_id)
            quantity_used = usage.quantity_used
            inventory_item = usage.inventory_item
            inventory_item.remain_quantity += quantity_used
            inventory_item.save()
            usage.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    
@csrf_exempt      
@require_POST
def delete_reagent_used(request, reagentusage_id):
    try:
        with transaction.atomic():
            usage = get_object_or_404(ReagentUsage, pk=reagentusage_id)
            quantity_used = usage.quantity_used
            inventory_item = usage.reagent
            inventory_item.remaining_quantity += quantity_used
            inventory_item.save()
            usage.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})    
    
    
    