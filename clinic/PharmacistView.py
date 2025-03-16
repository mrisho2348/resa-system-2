import calendar
from datetime import  datetime
from django.urls import reverse
from django.utils import timezone
from django.db.models import F
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404, JsonResponse
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist,ValidationError
from clinic.forms import ImagingRecordForm, LaboratoryOrderForm, ProcedureForm
from clinic.models import Consultation,  Medicine,PathodologyRecord, Patients, Procedure, Staffs
from django.views.decorators.http import require_POST
from .models import ClinicChiefComplaint, ClinicPrimaryPhysicalExamination, ClinicSecondaryPhysicalExamination, ConsultationNotes, ConsultationOrder, Counseling, Country, Diagnosis, Diagnosis, DischargesNotes, DiseaseRecode, Employee, EmployeeDeduction, HealthRecord, ImagingRecord,LaboratoryOrder, ObservationRecord,  Order, PatientDiagnosisRecord, PatientVisits, PatientVital, Prescription, PrescriptionFrequency, Reagent, Referral, SalaryChangeRecord,Service
from django.db.models import Sum
from django.db.models import Q
from django.db import transaction
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import logout
from django.utils.decorators import method_decorator
from kahamahmis.forms import StaffProfileForm
from django.views import View
# Create your views here.

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
def pharmacist_dashboard(request):
    # Count total records for different models
    total_patients_count = Patients.objects.count()
    total_medicines_count = Medicine.objects.count()
    total_lab_orders_count = LaboratoryOrder.objects.count()
    total_disease_records_count = DiseaseRecode.objects.count()
    total_services_count = Service.objects.count()

    # Fetch the most recently added patients (limit to 6)
    recently_added_patients = Patients.objects.order_by('-created_at')[:6]

    # Count staff by roles
    total_doctors_count = Staffs.objects.filter(role='doctor', work_place="resa").count()
    total_nurses_count = Staffs.objects.filter(role='nurse', work_place="resa").count()
    total_physiotherapists_count = Staffs.objects.filter(role='physiotherapist', work_place="resa").count()
    total_lab_technicians_count = Staffs.objects.filter(role='labTechnician', work_place="resa").count()
    total_pharmacists_count = Staffs.objects.filter(role='pharmacist', work_place="resa").count()
    total_receptionists_count = Staffs.objects.filter(role='receptionist', work_place="resa").count()

    # Prepare the context dictionary
    context = {
        'total_patients_count': total_patients_count,
        'total_medicines_count': total_medicines_count,
        'total_lab_orders_count': total_lab_orders_count,
        'total_disease_records_count': total_disease_records_count,
        'total_services_count': total_services_count,
        'recently_added_patients': recently_added_patients,
        'total_doctors_count': total_doctors_count,
        'total_nurses_count': total_nurses_count,
        'total_physiotherapists_count': total_physiotherapists_count,
        'total_lab_technicians_count': total_lab_technicians_count,
        'total_pharmacists_count': total_pharmacists_count,
        'total_receptionists_count': total_receptionists_count,
        # 'gender_based_monthly_counts': gender_based_monthly_counts,  # Uncomment and implement if needed
    }

    # Render the template with the context
    return render(request, "pharmacist_template/home_content.html", context)

@login_required
def pharmacist_profile(request):
    user = request.user
    
    try:
        # Fetch the pharmacist's details from the Staffs model
        staff = Staffs.objects.get(admin=user, role='pharmacist')
        
        # Pass the pharmacist details to the template
        return render(request, 'pharmacist_template/profile.html', {'staff': staff})

    except Staffs.DoesNotExist:
        return render(request, 'pharmacist_template/profile.html', {'error': 'Pharmacist not found.'})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Prevent user logout before redirecting
            messages.success(request, "Your password was successfully updated! Please log in again.")
            logout(request)  # Log out the user
            
            # Redirect based on workplace
            if request.user.staff.work_place == 'kahama':
                return redirect('kahamahmis:kahama')  # Redirect to Kahama login page
            else:
                return redirect('login')  # Redirect to default login page (Resa)

        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'pharmacist_template/change_password.html', {'form': form})        

@method_decorator(login_required, name='dispatch')
class EditStaffProfileView(View):
    template_name = 'pharmacist_template/edit_profile.html'

    def get(self, request, pk):
        staff = get_object_or_404(Staffs, id=pk, admin=request.user)
        form = StaffProfileForm(instance=staff)
        return render(request, self.template_name, {'form': form, 'staff': staff})

    def post(self, request, pk):
        staff = get_object_or_404(Staffs, id=pk, admin=request.user)
        form = StaffProfileForm(request.POST, request.FILES, instance=staff)

        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('pharmacist_edit_staff_profile', pk=staff.id)

        return render(request, self.template_name, {'form': form, 'staff': staff})      


def get_gender_yearly_data(request):
    if request.method == 'GET':
        selected_year = request.GET.get('year')
        
        # Query the database to get the total number of male and female patients for the selected year
        male_count = Patients.objects.filter(gender='Male', created_at__year=selected_year).count()
        female_count = Patients.objects.filter(gender='Female', created_at__year=selected_year).count()

        # Create a dictionary with the total male and female counts
        yearly_gender_data = {
            'Male': male_count,
            'Female': female_count
        }

        return JsonResponse(yearly_gender_data)
    else:
        # Return an error response if the request method is not GET or if it's not an AJAX request
        return JsonResponse({'error': 'Invalid request'})
    
def get_gender_monthly_data(request):
    if request.method == 'GET':
        selected_year = request.GET.get('year')       
        # Initialize a dictionary to store gender-wise monthly data
        gender_monthly_data = {}

        # Loop through each month and calculate gender-wise counts
        for month in range(1, 13):
            # Get the number of males and females for the current month and year
            male_count = Patients.objects.filter(
                gender='Male',
                created_at__year=selected_year,
                created_at__month=month
            ).count()            
            female_count = Patients.objects.filter(
                gender='Female',
                created_at__year=selected_year,
                created_at__month=month
            ).count()

            # Store the counts in the dictionary
            month_name = calendar.month_name[month]
            gender_monthly_data[month_name] = {'Male': male_count, 'Female': female_count}

        return JsonResponse(gender_monthly_data)
    else:
        return JsonResponse({'error': 'Invalid request'})

@login_required
def all_orders_view(request):
    # Retrieve all orders from the database
    orders = Order.objects.all().order_by('-order_date')    
    # Render the template with the list of orders
    return render(request, 'pharmacist_template/order_detail.html', {'orders': orders})

@login_required
def generate_invoice_bill(request,  order_id):
    # Retrieve the patient and visit objects based on IDs
    
    order = Order.objects.get(id=order_id)
     
    context = {
        'order': order,
       
    }
    return render(request, 'pharmacist_template/invoice_bill.html', context)


    
@login_required
def manage_patients(request):
    patient_records=Patients.objects.all().order_by('-created_at') 
    range_121 = range(1, 121)
    all_country = Country.objects.all()
    doctors=Staffs.objects.filter(role='doctor', work_place="resa")
    return render(request,"pharmacist_template/manage_patients.html", {
        "patient_records":patient_records,
        "range_121":range_121,
        "doctors":doctors,
        "all_country":all_country,
        })




def patient_vital_visit_list(request, patient_id,visit_id):
    # Retrieve the patient object
    patient = Patients.objects.get(pk=patient_id)
    visit = PatientVisits.objects.get(pk=visit_id)
   
    # Retrieve all vital information for the patient
    patient_vitals = PatientVital.objects.filter(patient=patient,visit=visit).order_by('-recorded_at')

    # Render the template with the patient's vital information
    context = {       
        'patient': patient, 
        'patient_vitals': patient_vitals,
        'visit': visit
    }
    
    return render(request, 'pharmacist_template/manage_patient_vital_list.html', context)  



@csrf_exempt
@require_POST
def add_remoteprescription(request):
    try:
        with transaction.atomic():
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

                if not quantity_used_str:
                    raise ValueError(f'Invalid quantity for {medicine.drug_name}. Quantity cannot be empty.')

                try:
                    quantity_used = int(quantity_used_str)
                except ValueError:
                    raise ValueError(f'Invalid quantity for {medicine.drug_name}. Quantity must be a valid whole number.')

                if float(quantity_used_str) != quantity_used:
                    raise ValueError(f'Invalid quantity for {medicine.drug_name}. Quantity must be a whole number.')

                if quantity_used < 0:
                    raise ValueError(f'Invalid quantity for {medicine.drug_name}. Quantity must be a non-negative number.')

                # Retrieve the remaining quantity of the medicine
                remain_quantity = medicine.remain_quantity

                if remain_quantity is not None and quantity_used > remain_quantity:
                    raise ValueError(f'Insufficient stock for {medicine.drug_name}. Only {remain_quantity} available.')

                # Reduce the remaining quantity of the medicine
                if remain_quantity is not None:
                    medicine.remain_quantity -= quantity_used
                    medicine.save()

                # Save prescription
                Prescription.objects.create(
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
    except ValueError as ve:
        return JsonResponse({'status': 'error', 'message': str(ve)})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred: ' + str(e)})
    
    
@login_required
def manage_consultation(request):
    patients=Patients.objects.all() 
    pathology_records=PathodologyRecord.objects.all() 
    doctors=Staffs.objects.filter(role='doctor', work_place="resa")
    context = {
        'patients':patients,
        'pathology_records':pathology_records,
        'doctors':doctors,
    }
    return render(request,"pharmacist_template/manage_consultation.html",context)




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

        doctors=Staffs.objects.filter(role='doctor', work_place="resa")
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
        return render(request, 'pharmacist_template/observation_template.html', {
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
    
    
@csrf_exempt
def add_imaging(request):
    if request.method == 'POST':
        try:
            # Assuming your form fields are named appropriately in your template
            patient_id = request.POST.get('patient_id')
            doctor_id = request.POST.get('doctor_id')
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
                    data_recorder=data_recorder,
                    doctor_id=doctor_id,
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
                doctor_id = request.POST.get('doctor_id')
                visit_id = request.POST.get('visit_id')
                orderDate = request.POST.get('order_date')
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

        doctors = Staffs.objects.filter(role='doctor', work_place="resa")
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

        return render(request, 'pharmacist_template/procedure_template.html', {
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
        return render(request, 'pharmacist_template/prescription_template.html', {           
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

        doctors = Staffs.objects.filter(role='labTechnician')
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
        return render(request, 'pharmacist_template/laboratory_template.html', {
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
            doctor_id = request.POST.get('doctor_id')
            data_recorder = request.user.staff
            visit_id = request.POST.get('visit_id')
            investigation_names = request.POST.getlist('investigation_name[]')
            descriptions = request.POST.getlist('description[]')            
            costs = request.POST.getlist('cost[]')
            order_date = request.POST.get('order_date')

            # Loop through the submitted data and create LaboratoryOrder objects
            for i in range(len(investigation_names)):
                investigation_record = LaboratoryOrder.objects.create(
                    patient_id=patient_id,
                    doctor_id=doctor_id,
                    visit_id=visit_id,
                    order_date=order_date,
                    data_recorder=data_recorder,
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


@login_required
def patient_health_record(request, patient_id, visit_id):
    try:
        # Retrieve visit history for the specified patient       
        visit = PatientVisits.objects.get(patient_id=patient_id,id=visit_id)
        prescriptions = Prescription.objects.filter(patient=patient_id, visit=visit_id)
        try:
            consultation_notes = PatientDiagnosisRecord.objects.filter(patient_id=patient_id, visit=visit_id).order_by('-created_at').first()
        except PatientDiagnosisRecord.DoesNotExist:
            consultation_notes = None
         
        try:
            vitals = PatientVital.objects.filter(patient=patient_id,visit=visit_id).order_by('-recorded_at')
        except PatientVital.DoesNotExist:
            vitals = None  
   
        try:
            procedures = Procedure.objects.filter(patient=patient_id, visit=visit_id)            
        except Procedure.DoesNotExist:
            procedures = None
          
        try:
            lab_results = LaboratoryOrder.objects.filter(patient=patient_id, visit=visit_id)
        except LaboratoryOrder.DoesNotExist:
            lab_results = None  

        try:
            imaging_records = ImagingRecord.objects.filter(patient_id=patient_id, visit_id=visit_id)
        except ImagingRecord.DoesNotExist:
            imaging_records = None
        
        total_procedure_cost = procedures.aggregate(Sum('cost'))['cost__sum']
        total_imaging_cost = imaging_records.aggregate(Sum('cost'))['cost__sum']
        lab_tests_cost = lab_results.aggregate(Sum('cost'))['cost__sum']     
        total_price = sum(prescription.total_price for prescription in prescriptions)
  
        patient = Patients.objects.get(id=patient_id)
        return render(request, 'pharmacist_template/manage_patient_health_record.html', {        
            'patient': patient,
            'visit': visit,           
            'total_procedure_cost': total_procedure_cost,
            'total_imaging_cost': total_imaging_cost,
            'lab_tests_cost': lab_tests_cost,
            'imaging_records': imaging_records,
            'prescriptions': prescriptions,
            'total_price': total_price,
            'consultation_notes': consultation_notes,        
            'vitals': vitals,
            'lab_results': lab_results,
            'procedures': procedures,
      
        })
    except Exception as e:
        # Handle other exceptions if necessary
        return render(request, '404.html', {'error_message': str(e)})
    
    


@login_required
def manage_service(request):
    services=Service.objects.all()
    context = {
        'services':services
    }
    return render(request,"pharmacist_template/manage_service.html",context)

@login_required
def single_staff_detail(request, staff_id):
    staff = get_object_or_404(Staffs, id=staff_id)
    # Fetch additional staff-related data  
    context = {
        'staff': staff,
     
    }

    return render(request, "pharmacist_template/staff_details.html", context)

@login_required
def view_patient(request, patient_id):
    patient = get_object_or_404(Patients, id=patient_id)
    # Fetch additional staff-related data  
    context = {
        'patient': patient,
     
    }

    return render(request, "pharmacist_template/patients_detail.html", context)



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
            visit = get_object_or_404(PatientVisits, id=visit_id)
            doctor = get_object_or_404(Staffs, id=doctor_id)
            patient = get_object_or_404(Patients, id=patient_id)
            consultation = Consultation(
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




@login_required
def patient_procedure_view(request):
    template_name = 'pharmacist_template/manage_procedure.html'
    
    # Retrieve all procedure data ordered by created_at field in descending order
    procedures = Procedure.objects.order_by('-created_at')

    return render(request, template_name, {'data': procedures})



@login_required
def patient_procedure_history_view(request, mrn):
    patient = get_object_or_404(Patients, mrn=mrn)
    
    # Retrieve all procedures for the specific patient
    procedures = Procedure.objects.filter(patient=patient)
    
    context = {
        'patient': patient,
        'procedures': procedures,
    }

    return render(request, 'pharmacist_template/manage_patient_procedure.html', context)



@login_required
def manage_referral(request):
    referrals = Referral.objects.all()   
    return render(request, 'pharmacist_template/manage_referral.html', {'referrals': referrals})

@login_required
def generate_billing(request, procedure_id):
    procedure = get_object_or_404(Procedure, id=procedure_id)

    context = {
        'procedure': procedure,
    }

    return render(request, 'pharmacist_template/billing_template.html', context)

@login_required
def appointment_list_view(request):
    appointments = Consultation.objects.all()   
    context = {    
        'appointments':appointments,
    }
    return render(request, 'pharmacist_template/manage_appointment.html', context)





@login_required
def patient_consultation_detail(request, patient_id, visit_id):
    try:        
      
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
        
       
        doctors = Staffs.objects.filter(role='doctor', work_place="resa")
        return render(request, 'pharmacist_template/patient_consultation_detail.html', {       
    
            'visit_history': visit_history,
            'patient': patient,       
            'doctors': doctors,      
        
            'remote_service': remote_service,
        
        })
    except Exception as e:
        # Handle other exceptions if necessary
        return render(request, '404.html', {'error_message': str(e)})    
    
 
@login_required
def patient_visit_history_view(request, patient_id):
    # Retrieve visit history for the specified patient
    visits = PatientVisits.objects.filter(patient_id=patient_id)   
    patient = Patients.objects.get(id=patient_id)
    return render(request, 'pharmacist_template/manage_patient_visit_history.html', {
        'visits': visits,
        'patient':patient,        
        })


@login_required
def prescription_list(request):     
    # Retrieve all prescriptions with related patient and visit
    prescriptions = Prescription.objects.select_related('patient', 'visit')
    # Group prescriptions by visit and calculate total price for each visit
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
      
    return render(request, 'pharmacist_template/manage_prescription_list.html', {
       
        'visit_total_prices': visit_total_prices,
    })
    

@login_required
def prescription_detail(request, visit_number, patient_id):
    patient = Patients.objects.get(id=patient_id)
    prescriptions = Prescription.objects.filter(visit__vst=visit_number, patient_id=patient_id)
    
    # Get the prescriber information for the first prescription (assuming all prescriptions have the same prescriber)
    prescriber = None
    if prescriptions.exists():
        prescriber = prescriptions.first().entered_by
    
    # Retrieve verification status, issued status, and payment status
    verification_status = None
    issued_status = None
    payment_status = None
    if prescriptions.exists():
        verification_status = prescriptions.first().verified
        issued_status = prescriptions.first().issued
        payment_status = prescriptions.first().status
    
    context = {
        'patient': patient,
        'prescriptions': prescriptions,
        'visit_number': visit_number,
        'prescriber': prescriber,
        'verification_status': verification_status,
        'issued_status': issued_status,
        'payment_status': payment_status,
    }
    return render(request, "pharmacist_template/prescription_detail.html", context)

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
    return render(request, "pharmacist_template/prescription_bill.html", context)

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
    return render(request, "pharmacist_template/prescription_notes.html", context)

@csrf_exempt
@login_required
def add_medicine(request):
    if request.method == 'POST':
        try:
            # Extract data from request
            medicine_id = request.POST.get('medicine_id')
            drug_name = request.POST.get('drug_name')
            drug_type = request.POST.get('drug_type')
            formulation_unit = request.POST.get('formulation_unit')
            manufacturer = request.POST.get('manufacturer')
            quantity = request.POST.get('quantity')
            dividable = request.POST.get('dividable')
            batch_number = request.POST.get('batch_number')
            expiration_date = request.POST.get('expiration_date')
            cash_cost = request.POST.get('cash_cost')
            insurance_cost = request.POST.get('insurance_cost')
            nhif_cost = request.POST.get('nhif_cost')
            buying_price = request.POST.get('buying_price')

            # Validate expiration_date
            if expiration_date:
                expiration_date_obj = datetime.strptime(expiration_date, '%Y-%m-%d').date()
                if expiration_date_obj <= datetime.now().date():
                    return JsonResponse({'status': 'fail', 'error': 'Expiration date must be in the future.'})

             # Check if required fields are provided
            if not (drug_name and quantity and buying_price):
                return JsonResponse({'status': 'fail', 'error': 'Missing required fields'})

            # Convert quantity and buying_price to integers .exclude(pk=disease_id)
            try:
                quantity = int(quantity)
                buying_price = float(buying_price)
            except ValueError:
                return JsonResponse({'status': 'fail', 'error': 'Invalid quantity or buying price'})
            # Check if this is an edit operation
            if medicine_id:
                if Medicine.objects.exclude(pk=medicine_id).filter(drug_name=drug_name).exists():
                    return JsonResponse({'status': 'fail', 'error': 'The medicine drug with the same name  already exists.'})
                if Medicine.objects.exclude(pk=medicine_id).filter(batch_number=batch_number).exists():
                    return JsonResponse({'status': 'fail', 'error': 'The  medicine drug with the same bath number  already exists.'})
                
                medicine = Medicine.objects.get(pk=medicine_id)
                medicine.drug_name = drug_name
                medicine.drug_type = drug_type
                medicine.formulation_unit = formulation_unit
                medicine.manufacturer = manufacturer
                medicine.quantity = quantity
                medicine.remain_quantity = quantity
                medicine.dividable = dividable
                medicine.batch_number = batch_number
                medicine.expiration_date = expiration_date
                medicine.cash_cost = cash_cost
                medicine.insurance_cost = insurance_cost
                medicine.nhif_cost = nhif_cost
                medicine.buying_price = buying_price
            else:
                # Check for uniqueness
                if Medicine.objects.filter(drug_name=drug_name).exists():
                    return JsonResponse({'status': 'fail', 'error': 'The  medicine drug with the same name  already exists.'})
                if Medicine.objects.filter(batch_number=batch_number).exists():
                    return JsonResponse({'status': 'fail', 'error': 'The  medicine drug with the same bath number  already exists.'})

                # Create a new Medicine instance
                medicine = Medicine(
                    drug_name=drug_name,
                    drug_type=drug_type,
                    formulation_unit=formulation_unit,
                    manufacturer=manufacturer,
                    quantity=quantity,
                    remain_quantity=quantity,
                    dividable=dividable,
                    batch_number=batch_number,
                    expiration_date=expiration_date,
                    cash_cost=cash_cost,
                    insurance_cost=insurance_cost,
                    nhif_cost=nhif_cost,
                    buying_price=buying_price,
                )

            # Save the medicine instance
            medicine.save()
            return JsonResponse({'status': 'success'})
        except ObjectDoesNotExist:
            return JsonResponse({'status': 'fail', 'error': 'Medicine not found.'})
        except ValidationError as ve:
            return JsonResponse({'status': 'fail', 'error': ve.message})
        except Exception as e:
            return JsonResponse({'status': 'fail', 'error': str(e)})
    return JsonResponse({'status': 'fail', 'error': 'Invalid request method'})



@login_required    
def patient_vital_list(request, patient_id):
    # Retrieve the patient object
    patient = Patients.objects.get(pk=patient_id)    
    # Retrieve all vital information for the patient
    patient_vitals = PatientVital.objects.filter(patient=patient).order_by('-recorded_at')

    # Render the template with the patient's vital information
    context = {      
        'patient_vitals': patient_vitals
    }
    
    return render(request, 'pharmacist_template/manage_patient_vital_list.html', context)    

@login_required
def patient_vital_all_list(request): 
    # Retrieve all vital information for the patient
    patient_vitals = PatientVital.objects.all().order_by('-recorded_at')
    
    context = {        
        'patient_vitals': patient_vitals
    }
    # Render the template with the patient's vital information
    return render(request, 'pharmacist_template/manage_all_patient_vital.html', context)    


# View to verify prescriptions
# View to verify prescriptions
@csrf_exempt
def verify_prescriptions(request):
    if request.method == 'POST':
        visit_number = request.POST.get('visit_number')
        # Perform logic to mark prescriptions as verified for the given visit_number
        # Example:
        try:
            prescriptions = Prescription.objects.filter(visit__vst=visit_number)
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
            prescriptions = Prescription.objects.filter(visit__vst=visit_number)
            for prescription in prescriptions:
                prescription.issued = 'issued'
                prescription.save()
            return JsonResponse({'message': 'Prescriptions issued successfully.'})
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
            prescriptions = Prescription.objects.filter(visit__vst=visit_number)
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
            prescriptions = Prescription.objects.filter(visit__vst=visit_number)
            for prescription in prescriptions:
                prescription.verified = 'Not Verified'
                prescription.status = 'Unpaid'
                prescription.issued = 'Not Issued'
                prescription.save()
            return JsonResponse({'message': 'Prescriptions unverified successfully.'})
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
            prescriptions = Prescription.objects.filter(visit__vst=visit_number)
            for prescription in prescriptions:
                prescription.issued = 'Not Issued'
                prescription.status = 'Unpaid'
                prescription.save()
            return JsonResponse({'message': 'Prescriptions unissued successfully.'})
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
            prescriptions = Prescription.objects.filter(visit__vst=visit_number)
            for prescription in prescriptions:
                prescription.status = 'Unpaid'
                prescription.save()
            return JsonResponse({'message': 'Prescriptions unpaid successfully.'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request.'}, status=400)
    

   
@login_required
def new_procedure_order(request):
    template_name = 'pharmacist_template/new_procedure_order.html'
    data_recorder = request.user.staff
    # Query to retrieve the latest procedure record for each patient
    procedures = Procedure.objects.filter(data_recorder=data_recorder.id).order_by('-order_date')    
    unread_orders = Order.objects.filter(order_type__in=[procedure.name.name for procedure in procedures])     
    orders = unread_orders 
    unread_orders.update(is_read=True)         
    return render(request, template_name, {'orders': orders})

@login_required
def new_consultation_order(request):   
    # Retrieve the current logged-in doctor
    data_recorder = request.user.staff    
    # Retrieve all ConsultationOrder instances for the current doctor
    consultation_orders = ConsultationOrder.objects.filter(data_recorder=data_recorder).order_by('-order_date')
    
    # Retrieve all unread orders for the ConsultationOrder instances
    unread_orders = Order.objects.filter(order_type__in=[consultation.consultation.name for consultation in consultation_orders])    
    # Mark the retrieved unread orders as read
    orders = unread_orders     
    unread_orders.update(is_read=True)    
    # Render the template with the fetched unread orders
    return render(request, 'pharmacist_template/new_consultation_order.html', {'orders': unread_orders})


@login_required
def new_radiology_order(request):
    data_recorder = request.user.staff
    pathodology_records=ImagingRecord.objects.filter(data_recorder=data_recorder.id).order_by('-order_date')   
    unread_orders = Order.objects.filter(order_type__in=[pathology.imaging.name for pathology in pathodology_records])     
    orders = unread_orders   
    unread_orders.update(is_read=True)     
    return render(request,"pharmacist_template/new_radiology_order.html",{
        "orders":unread_orders,       
        }) 
@login_required
def new_lab_order(request):
    data_recorder = request.user.staff
    lab_records=LaboratoryOrder.objects.filter(data_recorder=data_recorder.id).order_by('-order_date')   
    unread_orders = Order.objects.filter(order_type__in=[lab_record.name.name for lab_record in lab_records])     
    orders = unread_orders   
    unread_orders.update(is_read=True)     
    return render(request,"pharmacist_template/new_lab_order.html",{
        "orders":unread_orders,       
        }) 
    
@login_required
def manage_disease(request):
    disease_records=DiseaseRecode.objects.all() 
    return render(request,"pharmacist_template/manage_disease.html",{"disease_records":disease_records})    


    
    
@login_required
def medicine_list(request):
    # Retrieve medicines and check for expired ones
    medicines = Medicine.objects.all()
    # Render the template with medicine data and notifications
    return render(request, 'pharmacist_template/manage_medicine.html', {'medicines': medicines})   




def medicine_expired_list(request):
    # Get all medicines
    all_medicines = Medicine.objects.all()

    # Filter medicines with less than or equal to 10 days remaining for expiration
    medicines = []
    for medicine in all_medicines:
        days_remaining = (medicine.expiration_date - timezone.now().date()).days
        if days_remaining <= 10:
            medicines.append({
                'name': medicine.drug_name,
                'expiration_date': medicine.expiration_date,
                'days_remaining': days_remaining,
            })

    return render(request, 'pharmacist_template/manage_medicine_expired.html', {'medicines': medicines}) 

@login_required
def in_stock_medicines_view(request):
    # Retrieve medicines with inventory levels above zero
    in_stock_medicines = Medicine.objects.filter(remain_quantity__gt=0)

    return render(request, 'pharmacist_template/manage_in_stock_medicines.html', {'in_stock_medicines': in_stock_medicines})  

@login_required
def out_of_stock_medicines_view(request):
    try:
        # Query the database for out-of-stock medicines
        out_of_stock_medicines = Medicine.objects.filter(remain_quantity=0)
        
        # Render the template with the out-of-stock medicines data
        return render(request, 'pharmacist_template/manage_out_of_stock_medicines.html', {'out_of_stock_medicines': out_of_stock_medicines})
    
    except Exception as e:
        # Handle any errors and return an error response
        return render(request, '404.html', {'error_message': str(e)}) 
    

   
@login_required
def expiring_soon_medicines_count(request):
    today = timezone.now().date()
    ten_days_from_now = today + timezone.timedelta(days=10)
    count = Medicine.objects.filter(expiration_date__lt=ten_days_from_now, expiration_date__gte=today).count()
    return JsonResponse({'count': count})

@login_required
def total_quantity(request):
    total_quantity = Medicine.objects.filter(remain_quantity__gt=0).count()
    return JsonResponse({'total_quantity': total_quantity})  

@login_required
def health_record_list(request):
    records = HealthRecord.objects.all()
    return render(request, 'pharmacist_template/healthrecord_list.html', {'records': records})

@login_required 
def reagent_list(request):
    reagent_list = Reagent.objects.all()
    return render(request, 'pharmacist_template/manage_reagent_list.html', {'reagent_list': reagent_list})    

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
        return redirect(reverse('pharmacist_new_procedure_order'))
   
    else:
        # If it's a GET request, initialize the form with existing data (if any)
        form = ProcedureForm(instance=procedures)   
    # Add the form to the context
    context['form'] = form    
    return render(request, 'pharmacist_template/edit_procedure_result.html', context)

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
        return redirect(reverse('pharmacist_new_radiology_order'))
   
    else:
        # If it's a GET request, initialize the form with existing data (if any)
        form = ImagingRecordForm(instance=procedures)   
    # Add the form to the context
    context['form'] = form    
    return render(request, 'pharmacist_template/edit_radiology_result.html', context)

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
        return redirect(reverse('pharmacist_new_lab_order'))
   
    else:
        # If it's a GET request, initialize the form with existing data (if any)
        form = LaboratoryOrderForm(instance=procedures)   
    # Add the form to the context
    context['form'] = form    
    return render(request, 'pharmacist_template/edit_lab_result.html', context)

@login_required
def total_lab_orders_today(request):
    today = timezone.now()
    start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = today.replace(hour=23, minute=59, second=59, microsecond=999999)
    staff = request.user.staff  # Assuming the logged-in staff is the user
    total_lab_orders = LaboratoryOrder.objects.filter(created_at__range=(start_of_day, end_of_day), doctor=staff).count()
    return JsonResponse({'total_quantity': total_lab_orders or 0})

@login_required
def total_patients_today(request):
    today = timezone.now()
    start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = today.replace(hour=23, minute=59, second=59, microsecond=999999)
    total_patients = Patients.objects.filter(created_at__range=(start_of_day, end_of_day)).count()
    return JsonResponse({'total_patients': total_patients})

def out_of_stock_medicines(request):
    try:
        # Query the database for the count of out-of-stock medicines
        out_of_stock_count = Medicine.objects.filter(remain_quantity=0).count()
        
        # Return the count in JSON format
        return JsonResponse({'count': out_of_stock_count})
    
    except Exception as e:
        # Handle any errors and return an error response
        return JsonResponse({'error': str(e)}, status=500)     
    
@login_required
def patient_detail(request, patient_id):
    # Retrieve the patient object using the patient_id
    patient = get_object_or_404(Patients, id=patient_id)    
    # Context to be passed to the template
    context = {
        'patient': patient,
    }    
    # Render the patient_detail template with the context
    return render(request, 'pharmacist_template/patient_detail.html', context)  

@login_required
def employee_detail(request):
    try:
        # Get the logged-in staff member
        staff_member = request.user.staff        
        # Get the employee record for the logged-in staff member
        employee = get_object_or_404(Employee, name=staff_member)       
        # Fetch the related employee deductions and salary change records
        employee_deductions = EmployeeDeduction.objects.filter(employee=employee)
        salary_change_records = SalaryChangeRecord.objects.filter(employee=employee)

        # Context data to pass to the template
        context = {
            'staff_member': staff_member,
            'employee': employee,
            'employee_deductions': employee_deductions,
            'salary_change_records': salary_change_records,
        }
    except Staffs.DoesNotExist:
        context = {
            'error': "Staff member not found."
        }
    except Employee.DoesNotExist:
        context = {
            'error': "Employee record not found."
        }
    except Exception as e:
        context = {
            'error': str(e)
        }
    
    return render(request, 'pharmacist_template/employee_detail.html', context)

@login_required
def patient_visit_details_view(request, patient_id, visit_id):
    try:        
        visit = PatientVisits.objects.get(id=visit_id)
        prescriptions = Prescription.objects.filter(patient=patient_id, visit=visit_id)
        chief_complaints = ClinicChiefComplaint.objects.filter(patient_id=patient_id, visit_id=visit_id)
        primary_physical_examination = ClinicPrimaryPhysicalExamination.objects.filter(patient_id=patient_id, visit_id=visit_id).first()
        secondary_physical_examination = ClinicSecondaryPhysicalExamination.objects.filter(patient=patient_id, visit=visit_id).first()
        consultation_notes = ConsultationNotes.objects.filter(patient_id=patient_id, visit=visit_id).order_by('-created_at').first()
        vitals = PatientVital.objects.filter(patient=patient_id, visit=visit_id).order_by('-recorded_at')
        referral_records  = Referral.objects.filter(patient=patient_id, visit=visit_id).order_by('-created_at')
        counseling_records = Counseling.objects.filter(patient=patient_id, visit=visit_id).order_by('-created_at')        
        procedures = Procedure.objects.filter(patient=patient_id, visit=visit_id)
        imaging_records = ImagingRecord.objects.filter(patient=patient_id, visit=visit_id)
        discharge_notes = DischargesNotes.objects.filter(patient=patient_id, visit=visit_id)
        observation_records = ObservationRecord.objects.filter(patient=patient_id, visit=visit_id)
        lab_tests = LaboratoryOrder.objects.filter(patient=patient_id, visit=visit_id)
        procedure = Procedure.objects.filter(patient=patient_id, visit=visit_id).first()    
        diagnosis_record = PatientDiagnosisRecord.objects.filter(patient_id=patient_id, visit_id=visit_id).first()
        patient = get_object_or_404(Patients, id=patient_id)

        context = {
            'primary_physical_examination': primary_physical_examination,
            'secondary_physical_examination': secondary_physical_examination,
            'visit': visit,
            'counseling_records': counseling_records,
            'observation_records': observation_records,
            'patient': patient,
            'referral_records ': referral_records ,
            'chief_complaints': chief_complaints,              
            'prescriptions': prescriptions,           
            'consultation_notes': consultation_notes,     
            'diagnosis_record': diagnosis_record,            
            'vitals': vitals,     
            'lab_tests': lab_tests,
            'procedures': procedures,
            'procedure': procedure,
            'imaging_records': imaging_records,
            'discharge_notes': discharge_notes,
        }

        return render(request, 'pharmacist_template/manage_patient_visit_detail_record.html', context)
    except Patients.DoesNotExist:
        raise Http404("Patient does not exist")
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)})    