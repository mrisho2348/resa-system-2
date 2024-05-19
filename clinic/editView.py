from datetime import datetime
import logging
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404


from .models import Consultation, ConsultationFee, DiagnosticTest, DiseaseRecode, InsuranceCompany, MedicationPayment, MedicineInventory, PathodologyRecord, PathologyDiagnosticTest, PatientDisease, Patients, Medicine, Procedure, Referral, RemoteCompany, Sample, Staffs
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
# Define a logger
logger = logging.getLogger(__name__)

@login_required
def edit_insurance(request, insurance_id):
    insurance = get_object_or_404(InsuranceCompany, pk=insurance_id)

    if request.method == 'POST':
        try:
            # Retrieve data from the form
            name = request.POST.get('Name')
            phone = request.POST.get('Phone')
            short_name = request.POST.get('Short_name')
            email = request.POST.get('Email')
            address = request.POST.get('Address')
            website = request.POST.get('website')

            # Update the InsuranceCompany object
            insurance.name = name
            insurance.phone = phone
            insurance.short_name = short_name
            insurance.email = email
            insurance.address = address
            insurance.website = website

            # Save the changes
            insurance.save()

            messages.success(request, 'Insurance details updated successfully!')
            return redirect('clinic:manage_insurance')  # Replace 'your_redirect_url' with the appropriate URL name

        except Exception as e:
            messages.error(request, f'An error occurred: {e}')

    return render(request, 'update/edit_insurance.html', {'insurance': insurance})





@csrf_exempt  # Use csrf_exempt decorator for simplicity in this example. For a production scenario, consider using csrf protection.
def edit_procedure(request):
    if request.method == 'POST':
        try:
            procedure_id = request.POST.get('procedure_id')
            name = request.POST.get('name')
            start_time_str = request.POST.get('start_time')
            end_time_str = request.POST.get('end_time')
            description = request.POST.get('description')
            equipments_used = request.POST.get('equipments_used')
            cost = request.POST.get('cost')

            # Validate start and end times
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()

            if start_time >= end_time:
                return JsonResponse({'success': False, 'message': 'Start time must be greater than end time.'})

            # Calculate duration in hours
            duration = (datetime.combine(datetime.today(), end_time) - datetime.combine(datetime.today(), start_time)).seconds / 3600

            # Update procedure record
            procedure_record = Procedure.objects.get(id=procedure_id)
            procedure_record.name = name          
            procedure_record.description = description
            procedure_record.equipments_used = equipments_used
            procedure_record.cost = cost
            procedure_record.duration_time = duration
            procedure_record.save()

            return JsonResponse({'success': True, 'message': f'Procedure record for {procedure_record.name} updated successfully.'})
        except Procedure.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid procedure ID.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {e}'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


@csrf_exempt  # Use csrf_exempt decorator for simplicity in this example. For a production scenario, consider using csrf protection.
def edit_referral(request):
    if request.method == 'POST':
        try:
            mrn = request.POST.get('mrn')            
            referral_id = request.POST.get('referral_id')            
            source_location = request.POST.get('source_location')
            destination_location = request.POST.get('destination_location')
            reason = request.POST.get('reason')
            notes = request.POST.get('notes')           

            # Update procedure record
            referral_record = Referral.objects.get(id=referral_id)
            referral_record.patient = Patients.objects.get(mrn=mrn)        
            referral_record.source_location = source_location
            referral_record.destination_location = destination_location
            referral_record.reason = reason           
            referral_record.notes = notes           
            referral_record.save()

            return JsonResponse({'success': True, 'message': f'Referral record for {referral_record} updated successfully.'})
        except Referral.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid Referral ID.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {e}'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

@login_required
def edit_patient(request, patient_id):
    patient = get_object_or_404(Patients, pk=patient_id)

    if request.method == 'POST':
        try:
            # Retrieve data from the form
            fullname = request.POST.get('fullname')
            email = request.POST.get('email')
            dob = request.POST.get('dob')
            gender = request.POST.get('gender')
            phone = request.POST.get('phone')
            address = request.POST.get('Address')
            nationality = request.POST.get('profession')            
            marital_status = request.POST.get('maritalStatus')
            patient_type = request.POST.get('patient_type')
            payment_form = request.POST.get('payment_type')
            insurance_name = request.POST.get('insurance_name')
            insurance_number = request.POST.get('insurance_number')
      

            # Update the Patient object
            patient.fullname = fullname
            patient.email = email
            patient.dob = dob
            patient.gender = gender
            patient.phone = phone
            patient.address = address
            patient.nationality = nationality            
            patient.marital_status = marital_status
            patient.patient_type = patient_type
            patient.payment_form = payment_form

            # If payment type is insurance, update insurance details
            if payment_form == 'insurance':
                patient.insurance_name = insurance_name
                patient.insurance_number = insurance_number
          
            else:
                # Clear insurance details if payment form is cash
                patient.insurance_name = None
                patient.insurance_number = None
                patient.authorization_code = None

            # Save the changes
            patient.save()

            messages.success(request, 'Patient details updated successfully!')
            return redirect('clinic:manage_patient')  # Replace 'manage_patient' with the appropriate URL name

        except Exception as e:
            messages.error(request, f'An error occurred: {e}')

    return render(request, 'update/edit_patient.html', {'patient': patient})



def edit_medicine(request, medicine_id):
    try:
        # Check if the request method is POST
        if request.method != 'POST':
            return JsonResponse({'message': 'Invalid request method'}, status=400)

        # Get the medicine instance to be edited
        medicine = get_object_or_404(Medicine, id=medicine_id)

        # Extract the data from the request
        name = request.POST.get('name')
        medicine_type = request.POST.get('medicine_type')
        side_effect = request.POST.get('side_effect')
        dosage = request.POST.get('dosage')
        storage_condition = request.POST.get('storage_condition')
        manufacturer = request.POST.get('manufacturer')
        description = request.POST.get('description')
        expiration_date = request.POST.get('expiration_date')
        cash_cost = request.POST.get('cash_cost')
        buying_price = request.POST.get('buying_price')
        nhif_cost = request.POST.get('nhif_cost')

        # Perform the update within a transaction
        with transaction.atomic():
            # Update the medicine instance
            medicine.name = name
            medicine.medicine_type = medicine_type
            medicine.side_effect = side_effect
            medicine.dosage = dosage
            medicine.storage_condition = storage_condition
            medicine.manufacturer = manufacturer
            medicine.description = description
            medicine.expiration_date = expiration_date
            medicine.cash_cost = cash_cost
            medicine.buying_price = buying_price
            medicine.nhif_cost = nhif_cost

            # Save the changes
            medicine.save()

        # Log a success message
        messages.success(request, 'Medicine details updated successfully!')
        return redirect('clinic:medicine_list') 
    except Exception as e:
        # Log an error message
        logger.error(f'Error updating medicine details. Medicine ID: {medicine_id}, Error: {str(e)}')
        # Handle exceptions and return an error response
        return JsonResponse({'message': 'Error updating medicine details', 'error': str(e)}, status=500)
    

@login_required
def edit_disease_record(request, disease_id):
    disease = get_object_or_404(DiseaseRecode, pk=disease_id)

    if request.method == 'POST':
        try:
            # Retrieve data from the form
            name = request.POST.get('Name')
            code = request.POST.get('code')

            # Update the DiseaseRecode object
            disease.disease_name = name
            disease.code = code

            # Save the changes
            disease.save()

            messages.success(request, 'Disease details updated successfully!')
            return redirect('clinic:manage_disease')  # Replace 'your_redirect_url' with the appropriate URL name

        except Exception as e:
            messages.error(request, f'An error occurred: {e}')

    return render(request, 'update/edit_disease.html', {'disease': disease})

@login_required
def edit_company(request, company_id):
    company = get_object_or_404(RemoteCompany, pk=company_id)

    if request.method == 'POST':
        try:
            # Retrieve data from the form
            name = request.POST.get('Name')
            code = request.POST.get('code')
            category = request.POST.get('category')

            # Update the Company object
            company.name = name
            company.code = code
            company.category = category

            # Save the changes
            company.save()

            messages.success(request, 'Company details updated successfully!')
            return redirect('clinic:manage_company')  # Replace 'your_redirect_url' with the appropriate URL name
        except Exception as e:
            messages.error(request, f'An error occurred: {e}')

    return render(request, 'update/edit_company.html', {'company': company})

@login_required
def edit_pathodology(request, pathodology_id):
    pathodology = get_object_or_404(PathodologyRecord, pk=pathodology_id)
    disease_records=DiseaseRecode.objects.all() 

    if request.method == 'POST':
        try:
            # Retrieve data from the form
            name = request.POST.get('Name')
            description = request.POST.get('Description')
            related_diseases = request.POST.getlist('RelatedDiseases')

            # Update the PathodologyRecord object
            pathodology.name = name
            pathodology.description = description

            # Assuming related_diseases is a comma-separated list of disease IDs
            # Convert the string to a list of integers
            for disease_id in related_diseases:
                disease = DiseaseRecode.objects.get(pk=disease_id)
                pathodology.related_diseases.add(disease)

          

            # Save the changes
            pathodology.save()

            messages.success(request, 'Pathodology details updated successfully!')
            return redirect('clinic:manage_pathodology')  # Replace 'your_redirect_url' with the appropriate URL name

        except Exception as e:
            print(f"ERROR: {str(e)}")
            messages.error(request, f'An error occurred: {e}')

    return render(request, 'update/edit_pathodology.html', {
        'pathodology': pathodology,
        'all_diseases': disease_records,
        })


@require_POST
def edit_inventory(request, inventory_id):
    # Retrieve the MedicineInventory object
    inventory = get_object_or_404(MedicineInventory, pk=inventory_id)

    # Retrieve form data from request.POST
    medicine_id = request.POST.get('medicine_id')
    quantity = request.POST.get('quantity')
    purchase_date = request.POST.get('purchase_date')

    # Validate form data (add more validation as needed)
    if not medicine_id or not quantity or not purchase_date:
        # Handle validation error, redirect or display an error message
        return redirect('clinic:medicine_inventory')  # Adjust the URL as needed

    try:
        # Convert the quantity to an integer
        quantity = int(quantity)

        # Convert the purchase date to a datetime object
        purchase_date = datetime.strptime(purchase_date, '%Y-%m-%d').date()

        # Update the existing MedicineInventory record
        inventory.medicine_id = medicine_id
        inventory.quantity = quantity
        inventory.purchase_date = purchase_date
        inventory.save()

        # Recalculate total payment based on updated quantity and medicine unit price
        total_payment = inventory.quantity * inventory.medicine.unit_price
        inventory.total_payment = total_payment
        inventory.save(update_fields=['total_payment'])

        # Redirect to a success page or the medicine inventory page
        return redirect('clinic:medicine_inventory')  # Adjust the URL as needed

    except (ValueError, TypeError):
        # Handle invalid data types, redirect or display an error message
        return redirect('clinic:medicine_inventory')
    
    

@csrf_exempt
@require_POST
def edit_medication_payment(request, payment_id):
    try:
        # Retrieve the MedicationPayment object
        medication_payment = get_object_or_404(MedicationPayment, pk=payment_id)

        # Store the previous quantity for later adjustment
        previous_quantity_sold = medication_payment.quantity

        # Update MedicationPayment object based on the form data
        medicine_used = int(request.POST.get('edit_quantity'))
        amount = float(request.POST.get('edit_amount'))
        medicine_id = int(request.POST.get('medicine_id'))

        # Validate form data
        if medicine_used <= 0 or amount < 0 or not Medicine.objects.filter(pk=medicine_id).exists():
            return HttpResponseBadRequest("Invalid form data.")
        
        medicine = Medicine.objects.get(id=medicine_id)
        
        # Check that there is enough stock of this medicine in the pharmacy
        # Check if there is sufficient stock
        medicine_inventory = medicine.medicineinventory_set.first()
        if medicine_inventory and medicine_used > medicine_inventory.remain_quantity:
            return JsonResponse({'success': False, 'message': f'Insufficient stock. Only {medicine_inventory.remain_quantity} {medicine.name} available.'})
        with transaction.atomic():
            # Update MedicationPayment object
            medication_payment.quantity = medicine_used
            medication_payment.amount = amount
            medication_payment.medicine = medicine_id
            medication_payment.save()

            # Adjust MedicineInventory
            MedicineInventory.objects.filter(medicine=medication_payment.medicine).update(
                remain_quantity=F('remain_quantity') + (previous_quantity_sold - medicine_used)
            )

        # Redirect to the medication history page or another appropriate page
        return redirect('clinic:patient_medicationpayment_history_view_mrn', mrn=medication_payment.patient.mrn)

    except (ValueError, TypeError, MedicationPayment.DoesNotExist):
        return HttpResponseBadRequest("Invalid data types or MedicationPayment not found.")
    

def edit_diagnostic_test(request, test_id):
    if request.method == 'POST':
        try:
            # Retrieve form data from POST request
            patient_id = request.POST.get('patient')
            test_type = request.POST.get('test_type')
            test_date = request.POST.get('test_date')
            result = request.POST.get('result')          
            disease_or_pathology = request.POST.get('disease_or_pathology') 
            pathology_id = None
            diseases_ids = None
            health_issues_ids = None
            if disease_or_pathology == 'pathology':
                pathology_id = request.POST.get('Disease_Pathology_otherhealthissues')
                
            if disease_or_pathology == 'disease':
                diseases_ids = request.POST.get('Disease_Pathology_otherhealthissues')
                
            if disease_or_pathology == 'health_issue':
                health_issues_ids = request.POST.get('Disease_Pathology_otherhealthissues')
            # Retrieve the existing DiagnosticTest object
            diagnostic_test = get_object_or_404(DiagnosticTest, id=test_id)

            # Update the DiagnosticTest object with the new data
            patient = Patients.objects.get(id=patient_id)
            diagnostic_test.patient = patient
            diagnostic_test.test_type = test_type
            diagnostic_test.test_date = test_date
            diagnostic_test.result = result
            diagnostic_test.pathology_record = pathology_id

            # Save the changes to the DiagnosticTest object
            diagnostic_test.save()

            # Update diseases and health issues in the many-to-many fields
            if diseases_ids is not None:
                diagnostic_test.diseases.set(diseases_ids)
                
            if health_issues_ids is not None:
               diagnostic_test.health_issues.set(health_issues_ids)

            # Redirect to the diagnostic tests page or another appropriate URL
            return redirect('clinic:diagnostic_tests')  # Adjust the URL as needed

        except Exception as e:
            print(f"ERROR: {str(e)}")
            return HttpResponseBadRequest(f"Error: {str(e)}")

    return HttpResponseBadRequest("Invalid request method")    


def edit_sample(request, sample_id): 

    if request.method == 'POST':
        try:
            # Retrieve form data from POST request
            lab_test = request.POST.get('edit_lab_test')
            collection_date = request.POST.get('edit_collection_date')
            processing_date = request.POST.get('edit_processing_date')
            analysis_date = request.POST.get('edit_analysis_date')
            status = request.POST.get('edit_status')
                        # Convert date strings to datetime objects if provided
            collection_date = datetime.strptime(collection_date, '%Y-%m-%d') if collection_date else None
            processing_date = datetime.strptime(processing_date, '%Y-%m-%d') if processing_date else None
            analysis_date = datetime.strptime(analysis_date, '%Y-%m-%d') if analysis_date else None
            
            sample = get_object_or_404(Sample, id=sample_id)
            # Update the existing Sample object
            sample.lab_test = DiagnosticTest.objects.get(id=lab_test)
            sample.collection_date = collection_date
            sample.processing_date = processing_date
            sample.analysis_date = analysis_date
            sample.status = status

            sample.save()

            # Redirect to a success page or another appropriate URL
            return redirect('clinic:sample_list')  # Adjust the URL as needed

        except Exception as e:
            print(f"ERROR: {str(e)}")
            return HttpResponseBadRequest(f"Error: {str(e)}") 

    return HttpResponseBadRequest("Invalid request method")  

def edit_patient_disease_save(request, patient_disease_id): 

    if request.method == 'POST':
        try:
            # Retrieve form data from POST request
            patient_id = request.POST.get('patient_id')
            disease_record_id = request.POST.get('diseaseRecord')
            diagnosis_date = request.POST.get('diagnosisDate')
            severity = request.POST.get('severity')
            treatment_plan = request.POST.get('treatmentPlan')
            patient_disease = get_object_or_404(PatientDisease, id=patient_disease_id)
            patient_disease.patient = Patients.objects.get(id=patient_id)
            patient_disease.disease_record = DiseaseRecode.objects.get(id=disease_record_id)
            patient_disease.diagnosis_date = diagnosis_date
            patient_disease.severity = severity
            patient_disease.treatment_plan = treatment_plan

            patient_disease.save()

            # Redirect to a success page or another appropriate URL
            return redirect('clinic:patient_diseases_view')  # Adjust the URL as needed

        except Exception as e:
            print(f"ERROR: {str(e)}")
            return HttpResponseBadRequest(f"Error: {str(e)}") 

    return HttpResponseBadRequest("Invalid request method")  


def pathology_diagnostic_test_edit_save(request, test_id):
    if request.method == 'POST':
        try:
            pathology_diagnostic_test = get_object_or_404(PathologyDiagnosticTest, pk=test_id)

            # Retrieve data from the form
            pathology_record_id = request.POST.get('pathologyRecord')
            diagnostic_test_id = request.POST.get('diagnosticTest')
            test_result = request.POST.get('testResult')
            testing_date = request.POST.get('testingDate')
            conducted_by = request.POST.get('conductedBy')

            # Update PathologyDiagnosticTest object
            pathology_diagnostic_test.pathology_record = PathodologyRecord.objects.get(id=pathology_record_id)
            pathology_diagnostic_test.diagnostic_test =  DiagnosticTest.objects.get(id=diagnostic_test_id)
            pathology_diagnostic_test.test_result = test_result
            pathology_diagnostic_test.testing_date = testing_date
            pathology_diagnostic_test.conducted_by = conducted_by

            # Save the changes
            pathology_diagnostic_test.save()

            return redirect("clinic:pathology_diagnostic_test_list")
        except Exception as e:
            return HttpResponseBadRequest(f"Error: {str(e)}") 

    return HttpResponseBadRequest("Invalid request method") 


def update_consultation_data(request, appointment_id):
    # Get the Consultation instance
    if request.method == 'POST':
        try:
            # Extract form data from the request
            doctor_id = request.POST.get('doctor')
            patient_id = request.POST.get('patient')
            appointment_date = request.POST.get('appointmentDate')
            start_time = request.POST.get('startTime')
            end_time = request.POST.get('endTime')
            description = request.POST.get('description')
            pathodology_record_id = request.POST.get('pathodologyRecord')
            consultation = get_object_or_404(Consultation, id=appointment_id)
            # Update Consultation instance with new data
            consultation.doctor = Staffs.objects.get(id=doctor_id)
            consultation.patient = Patients.objects.get(id=patient_id)
            consultation.appointment_date = appointment_date
            consultation.start_time = start_time
            consultation.end_time = end_time
            consultation.description = description
            consultation.pathodology_record = PathodologyRecord.objects.get(id=pathodology_record_id)

            # Save the updated Consultation instance
            consultation.save()

            # Return a JsonResponse to indicate success
            return redirect("clinic:appointment_list")
        except Exception as e:
            # Return a JsonResponse with an error message
            return HttpResponseBadRequest(f"Error: {str(e)}") 

    # If the request is not a POST request, you might want to handle it accordingly (e.g., render a form)
    return HttpResponseBadRequest("Invalid request method")


require_POST
@csrf_exempt  # For simplicity, you can use CSRF exemption. In a real-world scenario, handle CSRF properly.
def update_consultation_fee(request):
    try:
        with transaction.atomic():
            consultation_fee_id = request.POST.get('consultation_fee_id')
            fee = get_object_or_404(ConsultationFee, id=consultation_fee_id)

            # Extract form data from the request
            doctor_id = request.POST.get('doctor')
            patient_id = request.POST.get('patient')
            fee_amount = request.POST.get('feeAmount')
            consultation_id = request.POST.get('consultation')

            # Update ConsultationFee instance with new data
            fee.doctor=Staffs.objects.get(id=doctor_id)
            fee.patient = Patients.objects.get(id=patient_id)
            fee.fee_amount = fee_amount
            fee.consultation= Consultation.objects.get(id=consultation_id)

            # Save the updated ConsultationFee instance
            fee.save()

        return redirect("clinic:consultation_fee_list")
    except Exception as e:
        # Return a JsonResponse with an error message
        return HttpResponseBadRequest(f"Error: {str(e)}") 