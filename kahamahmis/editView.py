from datetime import datetime
import logging
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from clinic.models import Consultation, ConsultationFee, DiagnosticTest, DiseaseRecode, InsuranceCompany, MedicationPayment, MedicineInventory, PathodologyRecord, PathologyDiagnosticTest, PatientDisease, Patients, Medicine, Procedure, Referral, RemoteCompany, RemoteConsultation, RemoteLaboratoryOrder, RemoteObservationRecord, RemotePatient, RemoteProcedure, RemoteReferral, Sample, Staffs
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import F
from django.contrib.auth.decorators import login_required
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

            # Update the InsuranceCompany object
            insurance.name = name
            insurance.phone = phone
            insurance.short_name = short_name
            insurance.email = email
            insurance.address = address

            # Save the changes
            insurance.save()

            messages.success(request, 'Insurance details updated successfully!')
            return redirect('manage_insurance')  # Replace 'your_redirect_url' with the appropriate URL name

        except Exception as e:
            messages.error(request, f'An error occurred: {e}')

    return render(request, 'update/edit_insurance.html', {'insurance': insurance})


@csrf_exempt  # Use csrf_exempt decorator for simplicity in this example. For a production scenario, consider using csrf protection.
def edit_procedure(request):
    if request.method == 'POST':
        try:
            procedure_id = request.POST.get('procedure_id')
            name_id = request.POST.get('name')         
            description = request.POST.get('description')          
            cost = request.POST.get('cost')
            # Update procedure record
            procedure_record = RemoteProcedure.objects.get(id=procedure_id)
            procedure_record.name_id = name_id          
            procedure_record.description = description  
            procedure_record.cost = cost     
            procedure_record.save()
            return JsonResponse({'success': True, 'message': f'Procedure record for {procedure_record.name} updated successfully.'})
        except Procedure.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid procedure ID.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {e}'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

@csrf_exempt  # Use csrf_exempt decorator for simplicity in this example. For a production scenario, consider using csrf protection.
def edit_observation(request):
    if request.method == 'POST':
        try:
            observation_id = request.POST.get('observation_id')
            imaging_id = request.POST.get('imaging')
            description = request.POST.get('description')
            result = request.POST.get('result')
            cost = request.POST.get('cost')
            image = request.FILES.get('new_image')
            # Update procedure record
            observation_record = RemoteObservationRecord.objects.get(id=observation_id)
            observation_record.imaging_id = imaging_id
            observation_record.description = description
            observation_record.result = result
            observation_record.cost = cost
            if image:
                observation_record.image = image
            observation_record.save()         
            return JsonResponse({'success': True, 'message': f'observation record for {observation_record.imaging} updated successfully.'})
        except RemoteObservationRecord.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid observation ID.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {e}'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


@csrf_exempt  # Use csrf_exempt decorator for simplicity in this example. For a production scenario, consider using csrf protection.
def edit_lab_result(request):
    if request.method == 'POST':
        try:
            lab_result_id = request.POST.get('lab_result_id')
            name_id = request.POST.get('lab_service')
            description = request.POST.get('description')
            result = request.POST.get('result')
            cost = request.POST.get('cost')        
            # Update procedure record
            lab_record = RemoteLaboratoryOrder.objects.get(id=lab_result_id)
            lab_record.name_id = name_id
            lab_record.description = description
            lab_record.result = result
            lab_record.cost = cost         
            lab_record.save()         
            return JsonResponse({'success': True, 'message': f'lab record record for {lab_record.name} updated successfully.'})
        except RemoteLaboratoryOrder.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid lab record ID.'})
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
            referral_record = RemoteReferral.objects.get(id=referral_id)
            referral_record.patient = RemotePatient.objects.get(mrn=mrn)        
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
        unit_price = request.POST.get('unit_price')

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
            medicine.unit_price = unit_price

            # Save the changes
            medicine.save()

        # Log a success message
        messages.success(request, 'Medicine details updated successfully!')
        return redirect('medicine_list') 
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
            return redirect('kahamahmis:manage_disease')  # Replace 'your_redirect_url' with the appropriate URL name

        except Exception as e:
            messages.error(request, f'An error occurred: {e}')

    return render(request, 'kahamaUpdate/edit_disease.html', {'disease': disease})

@login_required
def edit_company(request, company_id):
    company = get_object_or_404(RemoteCompany, pk=company_id)

    if request.method == 'POST':
        try:
            # Retrieve data from the form
            name = request.POST.get('Name')
            industry = request.POST.get('industry')
            sector = request.POST.get('sector')
            headquarters = request.POST.get('headquarters')
            Founded = request.POST.get('Founded')
            Notes = request.POST.get('Notes')

            # Update the Company object
            company.name = name
            company.industry = industry
            company.sector = sector
            company.headquarters = headquarters
            company.Founded = Founded
            company.Notes = Notes

            # Save the changes
            company.save()

            messages.success(request, 'Company details updated successfully!')
            return redirect('manage_company')  # Replace 'your_redirect_url' with the appropriate URL name
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
            return redirect('kahamahmis:manage_pathodology')  # Replace 'your_redirect_url' with the appropriate URL name

        except Exception as e:
            print(f"ERROR: {str(e)}")
            messages.error(request, f'An error occurred: {e}')

    return render(request, 'kahamaUpdate/edit_pathodology.html', {
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
        return redirect('medicine_inventory')  # Adjust the URL as needed

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
        return redirect('medicine_inventory')  # Adjust the URL as needed

    except (ValueError, TypeError):
        # Handle invalid data types, redirect or display an error message
        return redirect('medicine_inventory')
    
    


    



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
            consultation = get_object_or_404(RemoteConsultation, id=appointment_id)
            # Update Consultation instance with new data
            consultation.doctor = Staffs.objects.get(id=doctor_id)
            consultation.patient = Patients.objects.get(id=patient_id)
            consultation.appointment_date = appointment_date
            consultation.start_time = start_time
            consultation.end_time = end_time
            consultation.description = description          

            # Save the updated Consultation instance
            consultation.save()

            # Return a JsonResponse to indicate success
            return redirect("kahamahmis:appointment_list")
        except Exception as e:
            # Return a JsonResponse with an error message
            return HttpResponseBadRequest(f"Error: {str(e)}") 

    # If the request is not a POST request, you might want to handle it accordingly (e.g., render a form)
    return HttpResponseBadRequest("Invalid request method")


