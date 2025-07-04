import calendar
from datetime import  date, datetime
import os
from django.urls import reverse
from django.utils import timezone
import logging
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib import messages
from django.core.exceptions import ValidationError
from clinic.forms import CounselingForm, DischargesNotesForm, LaboratoryOrderForm, ObservationRecordForm
from clinic.models import Consultation,  Medicine,PathodologyRecord, Patients, Procedure, Staffs
from django.views.decorators.http import require_POST
from .models import AmbulanceOrder, ClinicChiefComplaint, ConsultationNotes, ConsultationOrder, Counseling, Country,  Diagnosis, DischargesNotes, DiseaseRecode, Employee, EmployeeDeduction, ImagingRecord,  LaboratoryOrder, ObservationRecord, Order, PatientDiagnosisRecord, PatientVisits, PatientVital, Prescription, PrescriptionFrequency,  Referral, SalaryChangeRecord,Service, AmbulanceVehicleOrder
from django.template.loader import render_to_string
from weasyprint import HTML
from django.db.models import Max,Sum,Q,Count
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import logout
from django.utils.decorators import method_decorator
from kahamahmis.forms import StaffProfileForm
from django.views import View
import re
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
    


@login_required
def receptionist_dashboard(request):
    try:
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

    except Patients.DoesNotExist:
        messages.error(request, 'Error fetching patient data.')
    except Medicine.DoesNotExist:
        messages.error(request, 'Error fetching medicine data.')
    except LaboratoryOrder.DoesNotExist:
        messages.error(request, 'Error fetching laboratory order data.')
    except DiseaseRecode.DoesNotExist:
        messages.error(request, 'Error fetching disease record data.')
    except Service.DoesNotExist:
        messages.error(request, 'Error fetching service data.')
    except Staffs.DoesNotExist:
        messages.error(request, 'Error fetching staff data.')
    except Exception as e:
        messages.error(request, f'An unexpected error occurred: {e}')

    # Render the template with the context
    return render(request, "receptionist_template/home_content.html", context)


def get_patient_completion_status(request):
    # Imaging Records
    imaging_with_result = ImagingRecord.objects.exclude(Q(result__isnull=True) | Q(result='')).values('patient').distinct().count()
    imaging_pending = ImagingRecord.objects.filter(Q(result__isnull=True) | Q(result='')).values('patient').distinct().count()

    # Procedures
    procedure_with_result = Procedure.objects.exclude(Q(result__isnull=True) | Q(result='')).values('patient').distinct().count()
    procedure_pending = Procedure.objects.filter(Q(result__isnull=True) | Q(result='')).values('patient').distinct().count()

    # Lab Orders
    lab_with_result = LaboratoryOrder.objects.exclude(Q(result__isnull=True) | Q(result='')).values('patient').distinct().count()
    lab_pending = LaboratoryOrder.objects.filter(Q(result__isnull=True) | Q(result='')).values('patient').distinct().count()

    # Consultation Notes - Count how many patients have multiple plans
    consultation_group = (
        ConsultationNotes.objects
        .values('patient')
        .annotate(plan_count=Count('doctor_plan'))
    )
    consultation_completed = consultation_group.filter(plan_count=1).count()
    consultation_in_progress = consultation_group.filter(plan_count__gt=1).count()

    return JsonResponse({
        "imaging": {
            "completed": imaging_with_result,
            "pending": imaging_pending
        },
        "procedure": {
            "completed": procedure_with_result,
            "pending": procedure_pending
        },
        "laboratory": {
            "completed": lab_with_result,
            "pending": lab_pending
        },
        "consultation": {
            "completed": consultation_completed,
            "in_progress": consultation_in_progress
        }
    })    

def get_earnings_data(request):
    try:
        today = date.today()

        # Helper function to calculate earnings from multiple querysets
        def aggregate_earnings(querysets, field='cost'):
            totals = {'nhif': 0, 'cash': 0, 'other': 0}

            for qs in querysets:
                # NHIF Insurance Earnings
                totals['nhif'] += qs.filter(
                    patient__payment_form='Insurance',
                    patient__insurance_name__icontains='nhif'
                ).aggregate(total=Sum(field))['total'] or 0

                # Cash Payments
                totals['cash'] += qs.filter(
                    patient__payment_form='Cash'
                ).aggregate(total=Sum(field))['total'] or 0

                # Other Insurance (non-NHIF)
                totals['other'] += qs.filter(
                    patient__payment_form='Insurance'
                ).exclude(
                    patient__insurance_name__icontains='nhif'
                ).aggregate(total=Sum(field))['total'] or 0

            return totals

        # Helper function to compute total earnings
        def compute_total(totals_dict):
            return totals_dict['nhif'] + totals_dict['cash'] + totals_dict['other']

        # DAILY EARNINGS: group related hospital and prescription queries
        daily_hospital_querysets = [
            LaboratoryOrder.objects.filter(order_date=today),
            Procedure.objects.filter(order_date=today),
            ImagingRecord.objects.filter(order_date=today),
            ConsultationOrder.objects.filter(order_date=today),
        ]

        daily_prescription_querysets = [
            Prescription.objects.filter(created_at__date=today),
        ]

        # Process hospital and prescription earnings
        hospital_earnings = aggregate_earnings(daily_hospital_querysets)
        prescription_earnings = aggregate_earnings(daily_prescription_querysets, field='total_price')

        # Build JSON response
        response_data = {
            'daily': {
                'hospital': {
                    'nhif': hospital_earnings['nhif'],
                    'cash': hospital_earnings['cash'],
                    'other': hospital_earnings['other'],
                    'total': compute_total(hospital_earnings),
                },
                'prescription': {
                    'nhif': prescription_earnings['nhif'],
                    'cash': prescription_earnings['cash'],
                    'other': prescription_earnings['other'],
                    'total': compute_total(prescription_earnings),
                },
                'grand_total': compute_total(hospital_earnings) + compute_total(prescription_earnings),
            }
        }

        return JsonResponse(response_data)

    except Exception as e:
        logger.error(f"[get_earnings_data] Error: {str(e)}")
        return JsonResponse({'error': 'An error occurred while retrieving earnings data.'}, status=500)





@login_required
def receptionist_profile(request):
    user = request.user
    
    try:
        # Fetch the receptionist's details from the Staffs model
        staff = Staffs.objects.get(admin=user, role='receptionist')
        
        # Pass the receptionist details to the template
        return render(request, 'receptionist_template/profile.html', {'staff': staff})

    except Staffs.DoesNotExist:
        return render(request, 'receptionist_template/profile.html', {'error': 'Receptionist not found.'})

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

    return render(request, 'receptionist_template/change_password.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class EditStaffProfileView(View):
    template_name = 'receptionist_template/edit_profile.html'

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
            return redirect('receptionist_edit_staff_profile', pk=staff.id)

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
    
    return render(request, 'receptionist_template/employee_detail.html', context)


@login_required
def all_orders_view(request):
    grouped_orders = (
        Order.objects
        .values(
            'patient__id',
            'patient__first_name',
            'patient__middle_name',
            'patient__last_name',
            'patient__gender',
            'patient__dob',
            'patient__mrn',
            'patient__payment_form',
            'patient__insurance_name',
            'visit__id',
            'visit__vst',
            'visit__updated_at',
        )
        .annotate(
            total_cost=Sum('cost'),
            latest_order_date=Max('order_date'),
        )
        .order_by('-latest_order_date')
    )

    for group in grouped_orders:
        patient_id = group['patient__id']
        visit_id = group['visit__id']
        orders_qs = Order.objects.filter(patient_id=patient_id, visit_id=visit_id).order_by('order_date')
        group['orders'] = list(orders_qs)

        # Precompute statuses for template use
        unique_statuses = orders_qs.values_list('status', flat=True).distinct()
        group['statuses'] = list(unique_statuses)

        # Combine full name
        group['full_name'] = f"{group.get('patient__first_name', '')} {group.get('patient__middle_name', '')} {group.get('patient__last_name', '')}".strip()

    return render(request, 'receptionist_template/order_detail.html', {
        'grouped_orders': grouped_orders,
    })


@login_required
def generate_invoice_bill(request,  patient_id,visit_id):
    # Retrieve the patient and visit objects based on IDs
    patient = get_object_or_404(Patients, id=patient_id)
    visit = get_object_or_404(PatientVisits, id=visit_id)    
    orders = Order.objects.filter(patient=patient, visit=visit)
     
    context = {
        'orders': orders,
        'patient': patient,
        'visit': visit,
       
    }
    return render(request, 'receptionist_template/invoice_bill.html', context)

@csrf_exempt
def update_orderpayment_status(request):
    if request.method == 'POST':
        try:
            order_id = request.POST.get('order_id')
            patient_id = request.POST.get('patient_id')
            visit_id = request.POST.get('visit_id')
            payment_status = request.POST.get('payment_status')

            if not all([patient_id, visit_id, payment_status]):
                return JsonResponse({'error': 'Missing required data.'}, status=400)

            # Update all orders for this patient and visit
            orders = Order.objects.filter(patient_id=patient_id, visit_id=visit_id)
            for order in orders:
                order.status = payment_status
                order.save()

            return JsonResponse({'message': 'Order payment status updated successfully.'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)
    
    
@login_required
def manage_patients(request):
    patient_records=Patients.objects.all().order_by('created_at') 
    range_121 = range(0, 121)
    all_country = Country.objects.all()
    doctors=Staffs.objects.filter(role='doctor', work_place = 'resa')
    return render(request,"receptionist_template/manage_patients.html", {
        "patient_records":patient_records,
        "range_121":range_121,
        "doctors":doctors,
        "all_country":all_country,
        })



@login_required
def patient_vital_visit_list(request, patient_id,visit_id):
    # Retrieve the patient object
    import numpy as np
    patient = Patients.objects.get(pk=patient_id)
    visit = PatientVisits.objects.get(pk=visit_id)
    range_51 = range(51)
    range_301 = range(301)
    range_101 = range(101)
    range_15 = range(3, 16)
    integer_range = np.arange(start=0, stop=510, step=1)
    temps = integer_range / 10
    # Retrieve all vital information for the patient
    patient_vitals = PatientVital.objects.filter(patient=patient,visit=visit).order_by('-recorded_at')

    # Render the template with the patient's vital information
    context = {
        'range_51': range_51,
        'range_301': range_301,
        'range_101': range_101,
        'range_15': range_15,
        'temps': temps,
        'patient': patient, 
        'patient_vitals': patient_vitals,
        'visit': visit
    }
    
    return render(request, 'receptionist_template/manage_patient_vital_list.html', context)  


@csrf_exempt
@require_POST
def save_patient_vital(request):
    try:
        # Extract data from the request
        vital_id = request.POST.get('vital_id')
        visit_id = request.POST.get('visit_id')
        patient_id = request.POST.get('patient_id')
        respiratory_rate = request.POST.get('respiratory_rate')
        pulse_rate = request.POST.get('pulse_rate')
        blood_pressure = request.POST.get('blood_pressure')
        spo2 = request.POST.get('spo2')
        temperature = request.POST.get('temperature')
        weight = request.POST.get('Weight')
        gcs = request.POST.get('gcs')
        avpu = request.POST.get('avpu')

        # Retrieve the corresponding 
        patient = Patients.objects.get(id=patient_id)
        visit = PatientVisits.objects.get(id=visit_id)
        recorded_by = request.user.staff
              


        # Check if the usageHistoryId is provided for editing
        if vital_id:
            # Editing existing usage history
            vital = PatientVital.objects.get(pk=vital_id)
          
        else:
            # Creating new usage history
            vital = PatientVital()
         

        # Update or set values for other fields
        vital.recorded_by = recorded_by
        vital.respiratory_rate = respiratory_rate
        vital.visit = visit
        vital.pulse_rate = pulse_rate
        vital.blood_pressure = blood_pressure
        vital.spo2 = spo2
        vital.gcs = gcs
        vital.temperature = temperature
        vital.weight = weight
        vital.avpu = avpu
        vital.patient = patient

    
        vital.save()

        return JsonResponse({'status': 'success','message':'vital saved successfully'}, status=201)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    


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
        entered_by = request.user.staff
        # Retrieve the corresponding patient and visit
        patient = Patients.objects.get(id=patient_id)
        visit = PatientVisits.objects.get(id=visit_id)

        # Check inventory levels for each medicine
        for i in range(len(medicines)):
            medicine = Medicine.objects.get(id=medicines[i])
            quantity_used_str = quantities[i]  # Get the quantity as a string

            if quantity_used_str is None:
                return JsonResponse({'status': 'error', 'message': f'Invalid quantity for {medicine.name}. Quantity cannot be empty.'})

            try:
                quantity_used = int(quantity_used_str)
            except ValueError:
                return JsonResponse({'status': 'error', 'message': f'Invalid quantity for {medicine.name}. Quantity must be a valid number.'})

            if quantity_used < 0:
                return JsonResponse({'status': 'error', 'message': f'Invalid quantity for {medicine.name}. Quantity must be a non-negative number.'})

            # Retrieve the corresponding medicine inventory
            medicine_inventory = medicine.medicineinventory_set.first()

            if medicine_inventory and quantity_used > medicine_inventory.remain_quantity:
                return JsonResponse({'status': 'error', 'message': f'Insufficient stock for {medicine.name}. Only {medicine_inventory.remain_quantity} available.'})

        # Save prescriptions only if inventory check passes
        for i in range(len(medicines)):
            medicine = Medicine.objects.get(id=medicines[i])
            prescription = Prescription()
            prescription.patient = patient
            prescription.entered_by = entered_by
            prescription.medicine = medicine
            prescription.visit = visit
            prescription.dose = doses[i]
            prescription.frequency = frequencies[i]
            prescription.duration = durations[i]
            prescription.quantity_used = int(quantities[i])
            prescription.save()

        return JsonResponse({'status': 'success', 'message': 'Prescription saved.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    
@login_required
def manage_consultation(request):
    patients=Patients.objects.all() 
    pathology_records=PathodologyRecord.objects.all() 
    doctors=Staffs.objects.filter(role='doctor', work_place = 'resa')
    context = {
        'patients':patients,
        'pathology_records':pathology_records,
        'doctors':doctors,
    }
    return render(request,"receptionist_template/manage_consultation.html",context)




@login_required
def save_observation(request, patient_id, visit_id):
    try:    
        try:
            visit = PatientVisits.objects.get(id=visit_id, patient_id=patient_id)
        except PatientVisits.DoesNotExist:
            visit = None
       
        doctors=Staffs.objects.filter(role='doctor', work_place = 'resa')
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
       
        return render(request, 'receptionist_template/observation_template.html', {
            'visit': visit,
            'patient': patient,
            'doctors': doctors,          
            'remote_service': remote_service,
        
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
    
@login_required    
def save_remotereferral(request, patient_id, visit_id):
    try:
        # Retrieve visit history for the specified patient
        visits = PatientVisits.objects.get(id=visit_id)
        visit_history = PatientVisits.objects.filter(patient_id=patient_id)       
        
        prescriptions = Prescription.objects.filter(patient=patient_id, visit=visit_id)
        try:
            consultation_notes = ConsultationNotes.objects.filter(patient_id=patient_id, visit=visit_id).order_by('-created_at').first()
        except ConsultationNotes.DoesNotExist:
            consultation_notes = None
        try:
            vital = PatientVital.objects.get(patient=patient_id, visit=visit_id)
        except PatientVital.DoesNotExist:
            vital = None
        try:
            referral = Referral.objects.get(patient=patient_id, visit=visit_id)
        except Referral.DoesNotExist:
            referral = None
        pathology_records = PathodologyRecord.objects.all()  # Fetch all consultation notes from the database
        doctors = Staffs.objects.filter(role='doctor', work_place = 'resa')
        provisional_diagnoses = Diagnosis.objects.all()
        final_diagnoses = Diagnosis.objects.all()

        total_price = sum(prescription.total_price for prescription in prescriptions)
        range_31 = range(31)
        current_date = timezone.now().date()
        patient = Patients.objects.get(id=patient_id)
        remote_service = Service.objects.all()
        range_51 = range(51)
        range_301 = range(301)
        range_101 = range(101)
        range_15 = range(3, 16)
        medicines = Medicine.objects.filter(
            medicineinventory__remain_quantity__gt=0,  # Inventory level greater than zero
            expiration_date__gt=current_date  # Not expired
        ).distinct()

        return render(request, 'receptionist_template/save_remotereferral.html', {
            'visit_history': visit_history,
            'patient': patient,
            'visits': visits,
            'range_31': range_31,
            'medicines': medicines,
            'prescriptions': prescriptions,
            'total_price': total_price,
            'consultation_notes': consultation_notes,
            'pathology_records': pathology_records,
            'doctors': doctors,
            'provisional_diagnoses': provisional_diagnoses,
            'final_diagnoses': final_diagnoses,
            'vital': vital,
            'referral': referral,
            'remote_service': remote_service,
            'range_51': range_51,
            'range_301': range_301,
            'range_101': range_101,
            'range_15': range_15,
        })
    except Exception as e:
        # Handle other exceptions if necessary
        return render(request, '404.html', {'error_message': str(e)})    

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
            visit = PatientVisits.objects.get(id=visit_id, patient_id=patient_id)
        except PatientVisits.DoesNotExist:
            visit = None    

        patient = Patients.objects.get(id=patient_id)

        doctors = Staffs.objects.filter(role='doctor', work_place = 'resa')
        # Fetching services based on coverage and type
        if patient.payment_form == 'insurance':
            # If patient's payment form is insurance, fetch services with matching coverage
            remote_service = Service.objects.filter(
                Q(type_service='procedure') & Q(coverage=patient.payment_form)
            )
        else:
            # If payment form is cash, fetch all services of type procedure
            remote_service = Service.objects.filter(type_service='procedure')

        return render(request, 'receptionist_template/procedure_template.html', {
            'visit': visit,
            'patient': patient,      
            'doctors': doctors,        
            'remote_service': remote_service,          
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
        return render(request, 'receptionist_template/prescription_template.html', {           
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
       
        try:
            visit = PatientVisits.objects.get(id=visit_id, patient_id=patient_id)
        except PatientVisits.DoesNotExist:
            visit = None   
        doctors = Staffs.objects.filter(role='labTechnician',work_place="resa")
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

        return render(request, 'receptionist_template/laboratory_template.html', {
            'visit': visit,
            'patient': patient,
            'doctors': doctors,          
            'remote_service': remote_service,
       
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
        visits = PatientVisits.objects.get(id=visit_id)
        visit_history = PatientVisits.objects.filter(patient_id=patient_id)
        prescriptions = Prescription.objects.filter(patient=patient_id, visit=visit_id)
        try:
            consultation_notes = ConsultationNotes.objects.filter(patient_id=patient_id, visit=visit_id).order_by('-created_at').first()
        except ConsultationNotes.DoesNotExist:
            consultation_notes = None
         
        try:
            previous_vitals = PatientVital.objects.filter(patient=patient_id,visit=visit_id).order_by('-recorded_at')
        except PatientVital.DoesNotExist:
            previous_vitals = None   
             
        try:
            consultation_notes_previous  = ConsultationNotes.objects.filter(patient=patient_id).order_by('-created_at')
        except ConsultationNotes.DoesNotExist:
            consultation_notes_previous  = None   
             
        try:
            vital = PatientVital.objects.filter(patient=patient_id, visit=visit_id)
        except PatientVital.DoesNotExist:
            vital = None
            
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
        pathology_records = PathodologyRecord.objects.all()  # Fetch all consultation notes from the database
        doctors = Staffs.objects.filter(role='doctor', work_place = 'resa')
        provisional_diagnoses = Diagnosis.objects.all()
        final_diagnoses = Diagnosis.objects.all()
        total_price = sum(prescription.total_price for prescription in prescriptions)
     
        current_date = timezone.now().date()
        patient = Patients.objects.get(id=patient_id)
        return render(request, 'receptionist_template/manage_patient_health_record.html', {
            'visit_history': visit_history,
            'patient': patient,
            'visit': visits,          
            'total_procedure_cost': total_procedure_cost,
            'total_imaging_cost': total_imaging_cost,
            'lab_tests_cost': lab_tests_cost,
            'imaging_records': imaging_records,
            'prescriptions': prescriptions,
            'total_price': total_price,
            'consultation_notes': consultation_notes,
            'pathology_records': pathology_records,
            'doctors': doctors,
            'consultation_notes_previous': consultation_notes_previous,
            'provisional_diagnoses': provisional_diagnoses,
            'previous_vitals': previous_vitals,
            'final_diagnoses': final_diagnoses,
            'vital': vital,
            'lab_results': lab_results,
            'procedures': procedures,
      
        })
    except Exception as e:
        # Handle other exceptions if necessary
        return render(request, '404.html', {'error_message': str(e)})
    


logger = logging.getLogger(__name__)

@login_required
def single_staff_detail(request, staff_id):
    staff = get_object_or_404(Staffs, id=staff_id)
    # Fetch additional staff-related data  
    context = {
        'staff': staff,
     
    }

    return render(request, "receptionist_template/staff_details.html", context)

@login_required
def view_patient(request, patient_id):
    patient = get_object_or_404(Patients, id=patient_id)
    # Fetch additional staff-related data  
    context = {
        'patient': patient,
     
    }

    return render(request, "receptionist_template/patients_detail.html", context)



@login_required
@csrf_exempt
def appointment_view(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    try:
        # Extract POST data
        doctor_id = request.POST.get('doctor')
        patient_id = request.POST.get('patient_id')
        visit_id = request.POST.get('visit_id', None)  # Optional
        date_of_consultation = request.POST.get('date_of_consultation')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        description = request.POST.get('description')

        # Basic validation
        if not all([doctor_id, patient_id, date_of_consultation, start_time, end_time]):
            return JsonResponse({'status': 'error', 'message': 'Missing required fields.'}, status=400)

        # Fetch objects
        doctor = get_object_or_404(Staffs, id=doctor_id)
        patient = get_object_or_404(Patients, id=patient_id)
        created_by = request.user.staff

        # Optional visit object
        visit = None
        if visit_id:
            try:
                visit = PatientVisits.objects.get(id=visit_id)
            except PatientVisits.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Visit not found for provided ID.'}, status=404)

        # Create consultation
        consultation = Consultation.objects.create(
            doctor=doctor,
            patient=patient,
            visit=visit,  # Will be None if not provided
            appointment_date=date_of_consultation,
            start_time=start_time,
            end_time=end_time,
            description=description,
            created_by=created_by
        )

        return JsonResponse({'status': 'success', 'message': 'Appointment successfully created'})

    except IntegrityError as e:
        return JsonResponse({'status': 'error', 'message': 'Database integrity error: ' + str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': 'Unexpected error: ' + str(e)}, status=500)



@login_required
def ambulance_order_view(request):
    template_name = 'receptionist_template/ambulance_order_template.html'
    # Retrieve all ambulance records with the newest records appearing first
    ambulance_orders = AmbulanceOrder.objects.all().order_by('-id')
    return render(request, template_name, {'ambulance_orders': ambulance_orders})

@login_required
def save_ambulance_order(request, patient_id, visit_id, ambulance_id=None): 
    # Get the patient and visit objects based on IDs
    patient = get_object_or_404(Patients, id=patient_id)
    visit = get_object_or_404(PatientVisits, id=visit_id)
    range_31 = range(1,31)
    context = {
        'patient': patient,
        'visit': visit,
        'days': range_31
    }

    # Check if ambulance_id is provided, indicating an edit operation
    if ambulance_id:
        ambulance_order = get_object_or_404(AmbulanceOrder, id=ambulance_id)
        context['ambulance_order'] = ambulance_order

    if request.method == 'POST':
        try:
            # If ambulance_id is provided, it's an edit operation
            if ambulance_id:
                ambulance_order = get_object_or_404(AmbulanceOrder, id=ambulance_id)
            else:
                # Otherwise, it's a new record
                ambulance_order = AmbulanceOrder()

            # Set the data recorder as the current user
            data_recorder = request.user.staff
            
            # Assign values to the AmbulanceOrder fields
            ambulance_order.patient = patient
            ambulance_order.visit = visit
            ambulance_order.data_recorder = data_recorder
            ambulance_order.service = request.POST.get('service')
            ambulance_order.from_location = request.POST.get('from_location')
            ambulance_order.to_location = request.POST.get('to_location')
            ambulance_order.age = request.POST.get('age')
            ambulance_order.condition = request.POST.get('condition')
            ambulance_order.intubation = request.POST.get('intubation')
            ambulance_order.pregnancy = request.POST.get('pregnancy')
            ambulance_order.oxygen = request.POST.get('oxygen')
            ambulance_order.ambulance_type = request.POST.get('ambulance_type')
            ambulance_order.cost = request.POST.get('cost')
            ambulance_order.payment_mode = request.POST.get('payment_mode')
            ambulance_order.duration_hours = request.POST.get('duration_hours')
            ambulance_order.duration_days = request.POST.get('duration_days')

            # Save the AmbulanceOrder object
            ambulance_order.save()

            # Define success message
            if ambulance_id:
                message = 'Ambulance order updated successfully'
            else:
                message = 'Ambulance order saved successfully'
            # Redirect to another URL upon successful data saving
            return redirect(reverse('receptionist_ambulance_order_view'))        
        except Exception as e:
            # Render the template with error message in case of exception
            messages.error(request, f'Error adding/editing ambulance record: {str(e)}')
            return render(request, 'receptionist_template/add_ambulance_order.html', context)
    else:
        # Render the template with patient and visit data for GET request
        return render(request, 'receptionist_template/add_ambulance_order.html', context)
    
@login_required    
def ambulance_order_detail(request, order_id):
    # Retrieve the ambulance order object
    ambulance_order = get_object_or_404(AmbulanceOrder, id=order_id)    
    # Pass the ambulance order object to the template
    return render(request, 'receptionist_template/ambulance_order_detail.html', {'ambulance_order': ambulance_order})

@login_required
def vehicle_ambulance_view(request):
    orders = AmbulanceVehicleOrder.objects.all().order_by('-id')  # Retrieve all AmbulanceVehicleOrder ambulance records, newest first
    template_name = 'receptionist_template/vehicle_ambulance.html'
    return render(request, template_name, {'orders': orders})

@login_required
def patient_procedure_history_view(request, mrn):
    patient = get_object_or_404(Patients, mrn=mrn)
    
    # Retrieve all procedures for the specific patient
    procedures = Procedure.objects.filter(patient=patient)
    
    context = {
        'patient': patient,
        'procedures': procedures,
    }

    return render(request, 'receptionist_template/manage_patient_procedure.html', context)


@csrf_exempt  # Use csrf_exempt decorator for simplicity in this example. For a production scenario, consider using csrf protection.
def save_procedure(request):
    if request.method == 'POST':
        try:
            mrn = request.POST.get('mrn')
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

            # Save procedure record
            procedure_record = Procedure.objects.create(
                patient=Patients.objects.get(mrn=mrn),
                name=name,
                description=description,
                duration_time=duration,
                equipments_used=equipments_used,
                cost=cost
            )

            return JsonResponse({'success': True, 'message': f'Procedure record for {procedure_record.name} saved successfully.'})
        except Patients.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid patient ID.'})
        except IntegrityError:
            return JsonResponse({'success': False, 'message': 'Duplicate entry. Procedure record not saved.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {e}'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


@csrf_exempt  # Use csrf_exempt decorator for simplicity in this example. For a production scenario, consider using csrf protection.
def save_referral(request):
    if request.method == 'POST':
        try:
            mrn = request.POST.get('mrn')            
            source_location = request.POST.get('source_location')
            destination_location = request.POST.get('destination_location')
            reason = request.POST.get('reason')
            notes = request.POST.get('notes')       


            # Save procedure record
            referral_record = Referral.objects.create(
                patient=Patients.objects.get(mrn=mrn),
                source_location=source_location,
                destination_location=destination_location,
                reason=reason,
                notes=notes,
       
            )

            return JsonResponse({'success': True, 'message': f'Referral record for {referral_record} saved successfully.'})
        except Patients.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid patient ID.'})
        except IntegrityError:
            return JsonResponse({'success': False, 'message': 'Duplicate entry. Referral record not saved.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {e}'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

@csrf_exempt
def change_referral_status(request):
    if request.method == 'POST':
        try:
            referral_id = request.POST.get('referralId')
            new_status = request.POST.get('newStatus')
            print(new_status)
            # Update referral record with new status
            referral_record = Referral.objects.get(id=referral_id)
            referral_record.status = new_status
            referral_record.save()

            return JsonResponse({'success': True, 'message': f'Status for {referral_record} changed successfully.'})
        except Referral.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid Referral ID.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {e}'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

@login_required
def manage_referral(request):
    referrals = Referral.objects.all()
    patients = Patients.objects.all()
    return render(request, 'receptionist_template/manage_referral.html', {'referrals': referrals,'patients':patients})


@login_required
def generate_billing(request, procedure_id):
    procedure = get_object_or_404(Procedure, id=procedure_id)

    context = {
        'procedure': procedure,
    }

    return render(request, 'receptionist_template/billing_template.html', context)

@login_required
def appointment_list_view(request):
    appointments = Consultation.objects.all()   
    context = {         
        'appointments':appointments,
    }
    return render(request, 'receptionist_template/manage_appointment.html', context)



@csrf_exempt
def save_edited_patient(request):
    if request.method == 'POST':
        try:
            patient_id = request.POST.get('patient_id')
            edited_patient = Patients.objects.get(id=patient_id)

            # Normalize and extract name fields
            first_name = request.POST.get('edit_first_name', '').strip().capitalize()
            middle_name = request.POST.get('edit_middle_name', '').strip().capitalize()
            last_name = request.POST.get('edit_last_name', '').strip().capitalize()

            # Check for duplicate full name (excluding self)
            duplicate = Patients.objects.filter(
                first_name__iexact=first_name,
                middle_name__iexact=middle_name,
                last_name__iexact=last_name
            ).exclude(id=patient_id).exists()
            if duplicate:
                return JsonResponse({'success': False, 'message': 'Another patient with the same full name already exists.'})

            # Update patient name fields
            edited_patient.first_name = first_name
            edited_patient.middle_name = middle_name
            edited_patient.last_name = last_name

            # Other fields
            edited_patient.gender = request.POST.get('edit_gender')
            edited_patient.phone = request.POST.get('edit_phone')
            edited_patient.address = request.POST.get('edit_Address')
            edited_patient.nationality_id = request.POST.get('edit_nationality')
            edited_patient.payment_form = request.POST.get('edit_payment_type')

            # Optional emergency contacts
            edited_patient.emergency_contact_name = request.POST.get('edit_emergency_contact_name') or None
            edited_patient.emergency_contact_relation = request.POST.get('emergency_contact_relation') or None
            edited_patient.emergency_contact_phone = request.POST.get('edit_emergency_contact_phone') or None

            # Validate and update NIDA number if provided
            nida_number = request.POST.get('edit_nida_number', '').strip()
            if nida_number:
                if not re.fullmatch(r'\d{20}', nida_number):
                    return JsonResponse({'success': False, 'message': 'NIDA number must be exactly 20 digits.'})
                if Patients.objects.filter(nida_number=nida_number).exclude(id=patient_id).exists():
                    return JsonResponse({'success': False, 'message': 'NIDA number already exists.'})
                edited_patient.nida_number = nida_number
            else:
                edited_patient.nida_number = None

            # Handle DOB and age
            age = request.POST.get('edit_age')
            dob = request.POST.get('edit_dob')

            if dob:
                try:
                    dob_date = datetime.strptime(dob, '%Y-%m-%d').date()
                    current_date = date.today()
                    age = current_date.year - dob_date.year - ((current_date.month, current_date.day) < (dob_date.month, dob_date.day))
                except ValueError:
                    dob_date = None
                    age = None
            elif age:
                try:
                    age_int = int(age)
                    current_date = date.today()
                    dob_date = current_date.replace(year=current_date.year - age_int)
                except ValueError:
                    dob_date = None
                    age = None
            else:
                dob_date = None
                age = None

            edited_patient.dob = dob_date
            edited_patient.age = age

            # Insurance details if payment type is insurance
            if edited_patient.payment_form == 'Insurance':
                edited_patient.insurance_name = request.POST.get('insurance_name')
                edited_patient.insurance_number = request.POST.get('edit_insurance_number')
            else:
                edited_patient.insurance_name = None
                edited_patient.insurance_number = None

            # Validate and save
            edited_patient.full_clean()
            edited_patient.save()

            return JsonResponse({'success': True, 'message': 'Patient data updated successfully.'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)

    
    
@csrf_exempt
def add_patient(request):
    try:
        if request.method == 'POST':
            # Extract data
            first_name = request.POST.get('first_name')
            middle_name = request.POST.get('middle_name')
            last_name = request.POST.get('last_name')
            # Ensure uniqueness by checking full name (case-insensitive)
            existing_patient = Patients.objects.filter(
                first_name__iexact=first_name if first_name else '',
                middle_name__iexact=middle_name if middle_name else '',
                last_name__iexact=last_name if last_name else ''
            ).exists()

            if existing_patient:
                return JsonResponse({'success': False, 'message': 'Patient with the same full name already exists.'})
            first_name = first_name.capitalize() if first_name else None
            middle_name = middle_name.capitalize() if middle_name else None
            last_name = last_name.capitalize() if last_name else None  

            emergency_contact_name = request.POST.get('emergency_contact_name')
            emergency_contact_relation = request.POST.get('emergency_contact_relation')         
            emergency_contact_phone = request.POST.get('emergency_contact_phone')

            nationality_id = request.POST.get('nationality')           
            gender = request.POST.get('gender')
            phone = request.POST.get('phone')
            address = request.POST.get('Address')                       

            payment_type = request.POST.get('payment_type')
            insurance_name = request.POST.get('insurance_company')
            insurance_number = request.POST.get('insurance_number')
            nida_number = request.POST.get('nida_number')

            age = request.POST.get('age')
            dob = request.POST.get('dob')

            # Age or DOB conversion
            if dob:
                try:
                    dob_date = datetime.strptime(dob, '%Y-%m-%d').date()
                    current_date = datetime.today().date()
                    age = current_date.year - dob_date.year - ((current_date.month, current_date.day) < (dob_date.month, dob_date.day))
                except ValueError:
                    dob_date = None
                    age = None
            elif age:
                try:
                    age_int = int(age)
                    current_date = datetime.today().date()
                    dob_date = current_date.replace(year=current_date.year - age_int)
                except ValueError:
                    dob_date = None
                    age = None
            else:
                dob_date = None
                age = None

            # NIDA number validation
            if nida_number and not re.fullmatch(r'\d{20}', nida_number):
                return JsonResponse({'success': False, 'message': 'NIDA number must be exactly 20 digits.'})

            if nida_number and Patients.objects.filter(nida_number=nida_number).exists():
                return JsonResponse({'success': False, 'message': 'NIDA number already exists.'})

            # Check duplicate patient name
            existing_patient = Patients.objects.filter(
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name
            ).exists()

            if existing_patient:
                return JsonResponse({'success': False, 'message': 'Patient with the same name already exists.'})

            # Generate MRN
            mrn = generate_mrn()

            # Create patient instance
            patient_instance = Patients(
                mrn=mrn,
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,             
                dob=dob_date,
                age=age,
                gender=gender,
                phone=phone,
                address=address,
                emergency_contact_name=emergency_contact_name or None,
                emergency_contact_relation=emergency_contact_relation or None,                
                emergency_contact_phone=emergency_contact_phone or None,
                nationality_id=nationality_id,
                payment_form=payment_type,
                nida_number=nida_number or None,
            )

            # Optional insurance
            if payment_type == 'Insurance':
                patient_instance.insurance_name = insurance_name
                patient_instance.insurance_number = insurance_number

            # Run model validation
            patient_instance.full_clean()
            patient_instance.save()

            return JsonResponse({'success': True, 'message': 'Patient added successfully'})

    except Exception as e:
        logger.error(f"Error adding patient: {str(e)}")
        return JsonResponse({'success': False, 'message': f'Failed to add patient: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})
    

def generate_mrn():
    last_patient = Patients.objects.order_by('-id').first()
    last_mrn_number = int(last_patient.mrn.split('-')[-1]) if last_patient else 0
    new_mrn_number = last_mrn_number + 1
    return f"RES-{new_mrn_number:07d}"
      
      


def save_service_data(request):
    if request.method == 'POST':
        service_id = request.POST.get('service_id')
        covarage = request.POST.get('covarage')
        department = request.POST.get('department')
        type_service = request.POST.get('typeService')
        name = request.POST.get('serviceName')
        description = request.POST.get('description')
        cost = request.POST.get('cost')

        try:
            if service_id:
                # Editing existing service
                service = Service.objects.get(pk=service_id)
            else:
                # Creating a new service
                service = Service()

            service.covarage = covarage
            service.department = department
            service.type_service = type_service
            service.name = name
            service.description = description
            service.cost = cost
            service.save()

            return redirect('manage_service')
        except Exception as e:
            return HttpResponseBadRequest(f"Error: {str(e)}") 

    # If the request is not a POST request, handle it accordingly
    return HttpResponseBadRequest("Invalid request method.")   






@login_required
def patient_consultation_detail(request, patient_id, visit_id):
    try:        
        try:
            visit = PatientVisits.objects.get(id=visit_id, patient_id=patient_id)                  
        except PatientVisits.DoesNotExist:
            visit= None    
                
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
     
       
        doctors = Staffs.objects.filter(role='doctor', work_place = 'resa')
        return render(request, 'receptionist_template/patient_consultation_detail.html', {      
             'visit': visit,
            'patient': patient,       
            'doctors': doctors,     
          
            'remote_service': remote_service,
        
        })
    except Exception as e:
        # Handle other exceptions if necessary
        return render(request, '404.html', {'error_message': str(e)})    
    
    

@csrf_exempt
@require_POST
def add_prescription(request):
    try:
        # Extract data from the request
        prescription_id = request.POST.get('prescription_id')
        patient_id = request.POST.get('patient')
        medicine_id = request.POST.get('medicine')
        route = request.POST.get('route')
        medicine_used = int(request.POST.get('quantity'))
        frequency = request.POST.get('frequency')
        duration = request.POST.get('duration')
        dose = request.POST.get('dose')

        # Retrieve the corresponding patient and medicine
        patient = Patients.objects.get(id=patient_id)
        medicine = Medicine.objects.get(id=medicine_id)
        
        # Check if there is sufficient stock
        medicine_inventory = medicine.medicineinventory_set.first()
        if medicine_inventory and medicine_used > medicine_inventory.remain_quantity:
            return JsonResponse({'success': False, 'message': f'Insufficient stock. Only {medicine_inventory.remain_quantity} {medicine.name} available.'})

        # Check if the usageHistoryId is provided for editing
        if prescription_id:
            # Editing existing prescription
            prescription = Prescription.objects.get(pk=prescription_id)
            # Get the previous quantity used
            previous_quantity_used = prescription.quantity_used
            
            # Calculate the difference in quantity
            quantity_difference = medicine_used - previous_quantity_used
            
            # Update the stock level of the corresponding item
            if medicine_inventory:
                medicine_inventory.remain_quantity -= quantity_difference
                medicine_inventory.save()
            # Recalculate total price
            total_price = medicine_used * medicine.unit_price
            prescription.total_price = total_price
        else:
            # Creating new prescription
            prescription = Prescription()
            prs_no = generate_prescription_id()
            prescription.prs_no = prs_no

        # Update or set values for other fields
        prescription.patient = patient
        prescription.medicine = medicine
        prescription.route = route
        prescription.dose = dose
        prescription.frequency = frequency
        prescription.duration = duration
        prescription.quantity_used = medicine_used

        # Save the changes to both models
        prescription.save()

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})    
    
def generate_prescription_id():
    last_prescription = Prescription.objects.last()
    last_sample_number = int(last_prescription.prs_no.split('-')[-1]) if last_prescription else 0
    new_prescription_id = last_sample_number + 1
    return f"PRS-{new_prescription_id:07d}"



    
    


def add_patient_visit(request):
    if request.method == 'POST':
        try:
            # Extract data from POST request
            visit_id = request.POST.get('visit_id')          
            visitType = request.POST.get('visitType')           
            insuranceName = request.POST.get('insuranceName')
            insuranceNumber = request.POST.get('insuranceNumber')
            verificationCode = request.POST.get('verificationCode')
            visitReason = request.POST.get('visitReason')
            patient_id = request.POST.get('patient_id')          
            referral_number = request.POST.get('referral_number')    
            primary_service = request.POST.get('primary_service')  

            # Retrieve patient object
            patient = Patients.objects.get(pk=patient_id)

            # Update or create PatientVisit object
            if visit_id:
                visit = PatientVisits.objects.get(pk=visit_id)
            else:
                visit = PatientVisits(patient=patient, vst=generate_vst())

            # Update fields
            visit.visit_type = visitType         
            visit.primary_service = primary_service
            visit.insurance_name = insuranceName
            visit.insurance_number = insuranceNumber            
            visit.authorization_code = verificationCode
            visit.visit_reason = visitReason
            visit.referral_number = referral_number
            visit.save()

            # Redirect the user based on the type of service
            redirect_url = {        
                'Investigation': reverse('receptionist_save_laboratory', args=[patient_id, visit.id]),       
                'Procedure': reverse('receptionist_save_remoteprocedure', args=[patient_id, visit.id]),
                'Imaging': reverse('receptionist_save_observation', args=[patient_id, visit.id]),
                'Consultation': reverse('receptionist_patient_consultation_detail', args=[patient_id, visit.id]),
                'Ambulance': reverse('save_ambulance_order', args=[patient_id, visit.id]),
            }
            # If the primary service is not found in the redirect_url dictionary, default to receptionist_patient_visit_history_view
            return redirect(redirect_url.get(primary_service, reverse('receptionist_patient_visit_history_view', args=[patient_id])))

        except Patients.DoesNotExist:
            messages.error(request, 'Invalid patient ID.')
        except Exception as e:
            messages.error(request, f'Error adding/editing visit record: {str(e)}')

    # If the request method is not POST or an exception occurred, redirect to visit history view
    return redirect(reverse('receptionist_patient_visit_history_view', args=[patient_id]))

    

def generate_vst():
    # Retrieve the last patient's VST from the database
    last_patient_visit = PatientVisits.objects.last()

    # Extract the numeric part from the last VST, or start from 0 if there are no patients yet
    last_vst_number = int(last_patient_visit.vst.split('-')[-1]) if last_patient_visit else 0

    # Increment the numeric part for the new patient
    new_vst_number = last_vst_number + 1

    # Format the VST with leading zeros and concatenate with the prefix "PAT-"
    new_vst = f"VST-{new_vst_number:07d}"

    return new_vst 

@login_required
def patient_visit_history_view(request, patient_id):
    # Retrieve visit history for the specified patient
    visits = PatientVisits.objects.filter(patient_id=patient_id)
    patient = Patients.objects.get(id=patient_id)
    return render(request, 'receptionist_template/manage_patient_visit_history.html', {
        'visits': visits,
        'patient':patient,  
       
        })


@login_required
def prescription_list(request):
    # Step 1: Fetch prescriptions grouped by visit
    grouped_visits = (
        Prescription.objects
        .values(
            'visit__id',
            'visit__vst',
            'visit__created_at',
            'visit__patient__id',
            'visit__patient__first_name',
            'visit__patient__middle_name',
            'visit__patient__last_name',
            'visit__patient__gender',
            'visit__patient__dob',
            'visit__patient__mrn',
            'visit__patient__payment_form',
            'visit__patient__insurance_name',
        )
        .annotate(
            total_price=Sum('total_price')
        )
        .order_by('-visit__created_at')
    )

    # Step 2: Attach related prescriptions to each grouped visit
    for visit in grouped_visits:
        prescriptions = Prescription.objects.filter(visit__id=visit['visit__id']).select_related('medicine')
        visit['prescriptions'] = prescriptions

        # Optional: Derive consistent status, issued, verified if all match
        statuses = prescriptions.values_list('status', flat=True).distinct()
        issued = prescriptions.values_list('issued', flat=True).distinct()
        verified = prescriptions.values_list('verified', flat=True).distinct()

        visit['status'] = statuses[0] if len(statuses) == 1 else "Mixed"
        visit['issued'] = issued[0] if len(issued) == 1 else "Mixed"
        visit['verified'] = verified[0] if len(verified) == 1 else "Mixed"

    return render(request, 'receptionist_template/manage_prescription_list.html', {
        'visit_total_prices': grouped_visits,
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
    return render(request, "receptionist_template/prescription_detail.html", context)

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
    return render(request, "receptionist_template/prescription_bill.html", context)

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
    return render(request, "receptionist_template/prescription_notes.html", context)



 

@login_required
@csrf_exempt
@require_POST
def save_remotepatient_vital(request):
    try:
        # Extract data from the request
        vital_id = request.POST.get('vital_id')
        patient_id = request.POST.get('patient_id')
        visit_id = request.POST.get('visit_id')
        respiratory_rate = request.POST.get('respiratory_rate')
        pulse_rate = request.POST.get('pulse_rate')
        sbp = request.POST.get('sbp')
        dbp = request.POST.get('dbp')
        spo2 = request.POST.get('spo2')
        temperature = request.POST.get('temperature')
        gcs = request.POST.get('gcs')
        avpu = request.POST.get('avpu')
        weight = request.POST.get('weight')
        doctor = request.user.staff

        try:
            # Retrieve the patient
            patient = Patients.objects.get(id=patient_id)
        except Patients.DoesNotExist:
            return JsonResponse({'status': False, 'message': 'Patient does not exist'})

        try:
            # Retrieve the visit
            visit = PatientVisits.objects.get(id=visit_id)
        except PatientVisits.DoesNotExist:
            return JsonResponse({'status': False, 'message': 'Visit does not exist'})

        # Check for duplicate records
        blood_pressure = f"{sbp}/{dbp}"
        if not vital_id:
            duplicate_vitals = PatientVital.objects.filter(
                patient=patient,
                visit=visit,
                respiratory_rate=respiratory_rate,
                pulse_rate=pulse_rate,
                blood_pressure=blood_pressure,
                spo2=spo2,
                sbp=sbp,
                dbp=dbp,
                temperature=temperature,
                gcs=gcs,
                avpu=avpu,
                weight=weight,
            )
            if duplicate_vitals.exists():
                return JsonResponse({'status': False, 'message': 'A similar vital record already exists for this patient during this visit.'})

        if vital_id:
            try:
                # Editing existing vital
                vital = PatientVital.objects.get(pk=vital_id)
                vital.blood_pressure = blood_pressure if sbp and dbp else vital.blood_pressure  # Use existing SBP/DBP if not provided
                message = 'Patient vital updated successfully'
            except PatientVital.DoesNotExist:
                return JsonResponse({'status': False, 'message': 'Vital record does not exist'})
        else:
            # Creating new vital
            vital = PatientVital()
            vital.blood_pressure = blood_pressure
            message = 'Patient vital created successfully'

        # Update or set values for other fields
        vital.visit = visit
        vital.respiratory_rate = respiratory_rate
        vital.pulse_rate = pulse_rate
        vital.recorded_by = doctor
        vital.blood_pressure = blood_pressure
        vital.sbp = sbp
        vital.dbp = dbp
        vital.spo2 = spo2
        vital.gcs = gcs
        vital.temperature = temperature
        vital.avpu = avpu
        vital.weight = weight
        vital.patient = patient
        vital.save()

        return JsonResponse({'status': True, 'message': message})
    except Patients.DoesNotExist:
        return JsonResponse({'status': False, 'message': 'Patient does not exist'})
    except PatientVisits.DoesNotExist:
        return JsonResponse({'status': False, 'message': 'Visit does not exist'})
    except Exception as e:
        return JsonResponse({'status': False, 'message': str(e)})

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
    return render(request, 'receptionist_template/manage_all_patient_vital.html', context)    


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
def ambulance_order_create_or_update(request, order_id=None):
    try:
        duration_hours = range(1, 25)    
        ambulance_number = range(1, 10)    
        days = range(1, 121)    
        if request.method == 'POST':
            # Extract data from the request
            vehicle_type = request.POST.get('ambulance_type')
            activities = request.POST.get('activities')
            cost = request.POST.get('cost')
            ambulance_number = request.POST.get('ambulance_number')
            organization = request.POST.get('organization')
            contact_person = request.POST.get('contact_person')
            contact_phone = request.POST.get('contact_phone')
            location = request.POST.get('location')
            duration = request.POST.get('duration_hours')
            days = request.POST.get('duration_days')
            payment_mode = request.POST.get('payment_mode')
            order_date = request.POST.get('order_date')
            
            # Create or update AmbulanceVehicleOrder instance based on whether order_id is provided
            if order_id:
                order = AmbulanceVehicleOrder.objects.get(pk=order_id)
            else:
                order = AmbulanceVehicleOrder()

            # Assign values to the instance
            order.vehicle_type = vehicle_type
            order.activities = activities
            order.cost = cost
            order.ambulance_number = ambulance_number
            order.organization = organization
            order.contact_person = contact_person
            order.contact_phone = contact_phone
            order.location = location
            order.duration = duration
            order.days = days
            order.payment_mode = payment_mode
            order.order_date = order_date
            order.save()

            # Redirect to a success URL
            return redirect('receptionist_vehicle_ambulance_view')  # Replace 'success_url' with your actual success URL
        else:
            # If it's a GET request, render the form
            context = {
                'duration_hours':duration_hours,
                'days':days,
                'ambulance_numbers':ambulance_number,
            }
            if order_id:
                order = AmbulanceVehicleOrder.objects.get(pk=order_id)
                context['order'] = order
            return render(request, 'receptionist_template/add_ambulance_carorder.html', context)
    except Exception as e:
        messages.error(request, f'Error adding/editing  record: {str(e)}')
        return redirect('ambulance_order_create_or_update')  

@login_required    
def vehicle_detail(request, order_id):
    # Retrieve the ambulance vehicle order object using the provided order_id
    order = get_object_or_404(AmbulanceVehicleOrder, pk=order_id)    
    # Render the vehicle detail template with the order object
    return render(request, 'receptionist_template/vehicle_detail.html', {'order': order}) 


@csrf_exempt  # Use csrf_exempt decorator for simplicity in this example. For a production scenario, consider using csrf protection.
def delete_ambulancecardorder(request):
    if request.method == 'POST':
        try:
            order_id = request.POST.get('order_id')

            # Delete procedure record
            record = get_object_or_404(AmbulanceVehicleOrder, pk=order_id)
            record.delete()

            return JsonResponse({'success': True, 'message': f' record for {record} deleted successfully.'})
        except AmbulanceVehicleOrder.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid record ID.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {e}'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


@csrf_exempt  # Use csrf_exempt decorator for simplicity in this example. For a production scenario, consider using csrf protection.
def delete_ambulancedorder(request):
    if request.method == 'POST':
        try:
            order_id = request.POST.get('order_id')
            # Delete procedure record
            record = get_object_or_404(AmbulanceOrder, pk=order_id)
            record.delete()

            return JsonResponse({'success': True, 'message': f' record for {record} deleted successfully.'})
        except AmbulanceVehicleOrder.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid record ID.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {e}'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})




@login_required
def manage_service(request):
    services=Service.objects.all()   
    context = {
        'services':services,       
    }
    return render(request,"receptionist_template/manage_service.html",context)




@login_required
def patient_laboratory_view(request):
    # Get distinct (patient, visit) combinations with latest result date
    distinct_lab_sets = (
        LaboratoryOrder.objects
        .values('patient_id', 'visit_id')
        .annotate(latest_date=Max('created_at'))
        .order_by('-latest_date')
    )

    patient_lab_data = []

    for entry in distinct_lab_sets:
        patient_id = entry['patient_id']
        visit_id = entry['visit_id']
        latest_date = entry['latest_date']

        lab_tests = LaboratoryOrder.objects.filter(
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

    return render(request, 'receptionist_template/manage_lab_result.html', context)


@login_required
def patient_imaging_view(request):
    # Get distinct (patient, visit) combinations with the latest imaging record date
    distinct_imaging_sets = (
        ImagingRecord.objects
        .values('patient_id', 'visit_id')
        .annotate(latest_date=Max('created_at'))
        .order_by('-latest_date')
    )

    patient_imaging_data = []

    for entry in distinct_imaging_sets:
        patient_id = entry['patient_id']
        visit_id = entry['visit_id']
        latest_date = entry['latest_date']

        imaging_records = ImagingRecord.objects.filter(
            patient_id=patient_id,
            visit_id=visit_id
        ).select_related('patient', 'visit', 'data_recorder__admin', 'imaging')

        if imaging_records.exists():
            first_imaging = imaging_records.first()
            patient_imaging_data.append({
                'patient': first_imaging.patient,
                'visit': first_imaging.visit,
                'latest_date': latest_date,
                'imaging_done_by': first_imaging.data_recorder,
                'imaging_records': imaging_records
            })

    context = {
        'patient_imaging': patient_imaging_data,
    }

    return render(request, 'receptionist_template/manage_imaging_result.html', context)

@login_required
def patient_lab_result_history_view(request, mrn):
    patient = get_object_or_404(Patients, mrn=mrn)    
    # Retrieve all procedures for the specific patient
    lab_results = LaboratoryOrder.objects.filter(patient=patient)
    patient_lab_results =  Service.objects.filter(type_service='Laboratory')    
    context = {
        'patient': patient,
        'lab_results': lab_results,
        'patient_lab_results': patient_lab_results,
    }
    return render(request, 'receptionist_template/manage_patient_lab_result.html', context)

@login_required
def patient_lab_details_view(request, mrn, visit_number):
    # Fetch the patient with a prefetch query to reduce database hits
    patient = get_object_or_404(Patients.objects.prefetch_related('laboratoryorder_set'), mrn=mrn)
    visit = get_object_or_404(PatientVisits, vst=visit_number)
    
    # Retrieve lab results efficiently
    lab_results = list(patient.laboratoryorder_set.filter(visit__vst=visit_number))

    # Get the first data recorder if lab results exist
    lab_done_by = lab_results[0].data_recorder if lab_results else None

    context = {
        'patient': patient,
        'visit': visit,
        'lab_done_by': lab_done_by,
        'lab_results': lab_results,
    }

    return render(request, 'receptionist_template/lab_details.html', context)    

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
        return redirect(reverse('receptionist_patient_lab_result_history_view', args=[patient.mrn]))
   
    else:
        # If it's a GET request, initialize the form with existing data (if any)
        form = LaboratoryOrderForm(instance=procedures)   
    
    # Add the form to the context
    context['form'] = form    
    return render(request, 'receptionist_template/edit_lab_result.html', context)   

@login_required
def add_radiology(request, patient_id, visit_id):
    try:    
        try:
            visit = PatientVisits.objects.get(id=visit_id, patient_id=patient_id)
        except PatientVisits.DoesNotExist:
            visit = None
       
        doctors=Staffs.objects.filter(role='doctor', work_place = 'resa')
        patient = Patients.objects.get(id=patient_id)
        consultation_notes = PatientDiagnosisRecord.objects.filter(patient=patient_id, visit=visit_id)
        radiology_record = ImagingRecord.objects.filter(patient=patient_id, visit=visit_id)
        consultation_note = ConsultationNotes.objects.filter(patient=patient, visit=visit).first()
        provisional_record, _ = PatientDiagnosisRecord.objects.get_or_create(patient=patient, visit=visit)     
        final_provisional_diagnosis= provisional_record.final_diagnosis.values_list('id', flat=True)
        # Fetching services based on coverage and type
        if patient.payment_form == 'insurance':
            # If patient's payment form is insurance, fetch services with matching coverage
            remote_service = Service.objects.filter(
                Q(type_service='Imaging') & Q(coverage=patient.payment_form)
            )
        else:
            # If payment form is cash, fetch all services of type procedure
            remote_service = Service.objects.filter(type_service='Imaging')
       
        return render(request, 'receptionist_template/add_radiology.html', {
            'visit': visit,
            'patient': patient,
            'radiology_record': radiology_record,          
            'final_provisional_diagnosis': final_provisional_diagnosis,          
            'doctors': doctors,          
            'consultation_note': consultation_note,          
            'consultation_notes': consultation_notes,          
            'remote_service': remote_service,
        
        })
    except Exception as e:
        # Handle other exceptions if necessary
        return render(request, '404.html', {'error_message': str(e)})     

@login_required
@csrf_exempt
def add_imaging(request):
    if request.method == 'POST':
        try:
            # Assuming your form fields are named appropriately in your template
            patient_id = request.POST.get('patient_id')
            doctor = request.user.staff
            visit_id = request.POST.get('visit_id')
            doctor_id = request.POST.get('doctor_id')
            imaging_names = request.POST.getlist('imaging_name[]')
            descriptions = request.POST.getlist('description[]')            
            costs = request.POST.getlist('cost[]')
            order_date = request.POST.get('order_date')

            # Loop through the submitted data and create ImagingRecord objects
            for i in range(len(imaging_names)):
                imaging_record = ImagingRecord.objects.create(
                    patient_id=patient_id,
                    doctor_id=doctor_id,
                    visit_id=visit_id,
                    order_date=order_date,              
                    data_recorder=request.user.staff ,
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
def patient_procedure_view(request):
    # Get all distinct (patient, visit) pairs that have at least one procedure
    distinct_procedure_sets = (
        Procedure.objects
        .values('patient_id', 'visit_id')
        .annotate(latest_date=Max('created_at'))
        .order_by('-latest_date')
    )

    # Prepare data structure for template
    patient_procedures = []

    for entry in distinct_procedure_sets:
        patient_id = entry['patient_id']
        visit_id = entry['visit_id']
        latest_date = entry['latest_date']

        procedures = Procedure.objects.filter(
            patient_id=patient_id,
            visit_id=visit_id
        ).select_related('patient', 'visit', 'doctor__admin', 'name', 'data_recorder')

        if procedures.exists():
            first_proc = procedures.first()
            patient_procedures.append({
                'patient': first_proc.patient,
                'visit': first_proc.visit,
                'latest_date': latest_date,
                'doctor': first_proc.doctor,
                'procedure_done_by': first_proc.data_recorder,
                'procedures': procedures  # All procedures for that visit
            })

    context = {
        'patient_procedures': patient_procedures,
    }
    return render(request, 'receptionist_template/manage_procedure.html', context)


@login_required
def patient_procedure_detail_view(request, mrn, visit_number):
    """ View to display procedure details for a specific patient and visit. """
    
    # Fetch patient and visit in one go
    patient = get_object_or_404(Patients, mrn=mrn)
    visit = get_object_or_404(PatientVisits, vst=visit_number)
    
    # Retrieve procedures related to this patient and visit
    procedures = Procedure.objects.filter(patient=patient, visit=visit).select_related('doctor')

    # Get the doctor who performed the first procedure (if exists)
    procedure_done_by = procedures[0].doctor if procedures else None

    context = {
        'procedure_done_by': procedure_done_by,
        'patient': patient,
        'visit': visit,
        'procedure': procedures,
    }

    return render(request, 'receptionist_template/manage_procedure_detail_view.html', context)


@login_required
def manage_referral(request):
    referrals = Referral.objects.all()
    patients = Patients.objects.all()
    return render(request, 'receptionist_template/manage_referral.html', {'referrals': referrals,'patients':patients}) 

def view_referral(request, referral_id):
    referral = get_object_or_404(Referral, id=referral_id)
    context = {
        'referral': referral
    }
    return render(request, 'receptionist_template/view_referral.html', context)

def counseling_list_view(request):
    counselings = Counseling.objects.all().order_by('-created_at')
    return render(request, 'receptionist_template/manage_counselling.html', {'counselings': counselings})   

@login_required    
def save_counsel(request, patient_id, visit_id):
    # Retrieve patient and visit objects
    patient = get_object_or_404(Patients, id=patient_id)
    visit = get_object_or_404(PatientVisits, id=visit_id)              
    data_recorder = request.user.staff
    # Retrieve existing remote counseling record if it exists
    remote_counseling = Counseling.objects.get(patient=patient, visit=visit)
    consultation_notes = PatientDiagnosisRecord.objects.filter(patient=patient_id, visit=visit_id)  
    # Prepare context for rendering the template
    context = {
        'patient': patient, 
        'visit': visit,
        'remote_counseling': remote_counseling,
        'consultation_notes': consultation_notes,
    }
    
    # Handle form submission
    if request.method == 'POST':        
        form = CounselingForm(request.POST, instance=remote_counseling)
        
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
        return redirect(reverse('receptionist_save_remotesconsultation_notes', args=[patient_id, visit_id]))
   
    else:
        # If it's a GET request, initialize the form with existing data (if any)
        form = CounselingForm(instance=remote_counseling)   
    # Add the form to the context
    context['form'] = form    
    return render(request, 'receptionist_template/counsel_template.html', context)

def view_counseling_notes(request, patient_id, visit_id):
    visit = get_object_or_404(PatientVisits, id=visit_id)  
    patient = get_object_or_404(Patients, id=patient_id) 
    counseling_note = get_object_or_404(Counseling, patient=patient, visit=visit)
    
    context = {
        'patient': patient,
        'visit': visit,
        'counseling_note': counseling_note,
    }
    return render(request, 'receptionist_template/counseling_notes_details.html', context) 

def discharge_notes_list_view(request):
    discharge_notes = DischargesNotes.objects.all().order_by('-discharge_date')
    return render(request, 'receptionist_template/manage_discharge.html', {'discharge_notes': discharge_notes})           

@login_required    
def save_remote_discharges_notes(request, patient_id, visit_id):
    patient = get_object_or_404(Patients, id=patient_id)
    visit = get_object_or_404(PatientVisits, id=visit_id)
    consultation_notes = PatientDiagnosisRecord.objects.filter(patient=patient_id, visit=visit_id)    
    remote_discharges_notes = DischargesNotes.objects.filter(patient=patient, visit=visit).first()  
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
            form = DischargesNotesForm(request.POST, instance=remote_discharges_notes)
            if form.is_valid():
                remote_discharges_notes = form.save(commit=False)
                remote_discharges_notes.patient = patient
                remote_discharges_notes.visit = visit
                remote_discharges_notes.data_recorder = data_recorder
                remote_discharges_notes.save()
                messages.success(request, '')
                return redirect(reverse('receptionist_patient_visit_details_view', args=[patient_id, visit_id]))  # Redirect to the next view
            else:
                messages.error(request, 'Please correct the errors in the form.')
        else:
            form = DischargesNotesForm(instance=remote_discharges_notes)        
        # Prepare context for rendering the template
        context['form'] = form
        return render(request, 'receptionist_template/disrcharge_template.html', context)    
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return render(request, 'receptionist_template/disrcharge_template.html', context)

@login_required
def discharge_details_view(request, patient_id, visit_id):
    # Fetch the patient
    patient = get_object_or_404(Patients, id=patient_id)

    # Fetch the visit
    visit = get_object_or_404(PatientVisits, id=visit_id)
    consultation_notes = PatientDiagnosisRecord.objects.filter(patient=patient_id, visit=visit_id)  
    
    # Fetch the discharge note related to this visit
    discharge_note = get_object_or_404(DischargesNotes, patient=patient, visit=visit)

    context = {
        'patient': patient,
        'visit': visit,
        'consultation_notes': consultation_notes,
        'discharge_note': discharge_note,
    }

    return render(request, 'receptionist_template/discharge_details.html', context)        

def observation_record_list_view(request):
    observation_records = ObservationRecord.objects.all().order_by('-created_at')
    return render(request, 'receptionist_template/manage_observation_record.html', {'observation_records': observation_records})

@login_required
def save_observation(request, patient_id, visit_id):
    patient = get_object_or_404(Patients, id=patient_id)
    visit = get_object_or_404(PatientVisits, id=visit_id)
    data_recorder = request.user.staff
    record_exists = ObservationRecord.objects.filter(patient_id=patient_id, visit_id=visit_id).first()
    consultation_notes = PatientDiagnosisRecord.objects.filter(patient=patient_id, visit=visit_id)    
    context = {'patient': patient, 
               'visit': visit, 
               'consultation_notes': consultation_notes, 
               'record_exists': record_exists
               }
    if request.method == 'POST':
        form = ObservationRecordForm(request.POST)
        if form.is_valid():
            description = form.cleaned_data['observation_notes']
            try:
                if record_exists:
                    # If a record exists, update it
                    observation_record = ObservationRecord.objects.get(patient_id=patient_id, visit_id=visit_id)
                    observation_record.observation_notes = description
                    observation_record.data_recorder = data_recorder
                    observation_record.save()
                    messages.success(request, '')
                else:
                    # If no record exists, create a new one
                    ObservationRecord.objects.create(
                        patient=patient,
                        visit=visit,
                        data_recorder=data_recorder,
                        observation_notes=description,
                    )
                    messages.success(request, '')
                return redirect(reverse('receptionist_save_remotesconsultation_notes', args=[patient_id, visit_id]))
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            messages.error(request, 'Please fill out all required fields.')
    else:
        form = ObservationRecordForm(initial={'observation_notes': record_exists.observation_notes if record_exists else ''})

    context['form'] = form
    return render(request, 'receptionist_template/observation_template.html', context)

def view_observation_notes(request, patient_id, visit_id):
    visit = get_object_or_404(PatientVisits, id=visit_id)  
    patient = get_object_or_404(Patients, id=patient_id)  
    observation_record = get_object_or_404(ObservationRecord, patient=patient, visit=visit)      
    
    return render(request, 'receptionist_template/observation_notes_detail.html', {
        'observation_record': observation_record,
        'visit': visit,
    })


def download_observation_pdf(request, patient_id, visit_id):
    # Fetch the required patient and visit
    visit = get_object_or_404(PatientVisits, id=visit_id)
    patient = get_object_or_404(Patients, id=patient_id)
    observation_record = get_object_or_404(ObservationRecord, patient=patient, visit=visit)

    # Prepare context for the template
    context = {
        'observation_record': observation_record,
        'visit': visit,
    }

    # Render HTML template
    html_content = render_to_string('receptionist_template/observation_notes_detail.html', context)

    # Create a temporary directory and file path
    temp_dir = os.path.join(os.path.expanduser("~"), "pdf_temp")
    os.makedirs(temp_dir, exist_ok=True)
    file_name = f'observation_{patient.full_name}_{visit.vst}.pdf'
    file_path = os.path.join(temp_dir, file_name)

    # Delete old file if it exists
    if os.path.exists(file_path):
        os.remove(file_path)

    # Generate PDF
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(file_path)

    # Return file as response
    with open(file_path, 'rb') as f:
        pdf_data = f.read()

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response

def download_discharge_pdf(request, patient_id, visit_id):
    # Fetch patient, visit, and discharge note
    visit = get_object_or_404(PatientVisits, id=visit_id)
    patient = get_object_or_404(Patients, id=patient_id)
    discharge_note = get_object_or_404(DischargesNotes, patient=patient, visit=visit)

    # Prepare context
    context = {
        'discharge_note': discharge_note,
        'patient': patient,
        'visit': visit,
    }

    # Render HTML content using a dedicated template
    html_content = render_to_string('receptionist_template/discharge_note_detail.html', context)

    # Prepare file path
    temp_dir = os.path.join(os.path.expanduser("~"), "pdf_temp")
    os.makedirs(temp_dir, exist_ok=True)
    file_name = f'discharge_{patient.full_name}_{visit.vst}.pdf'
    file_path = os.path.join(temp_dir, file_name)

    # Remove old file if exists
    if os.path.exists(file_path):
        os.remove(file_path)

    # Generate PDF
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(file_path)

    # Return PDF response
    with open(file_path, 'rb') as f:
        pdf_data = f.read()

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response   

def download_counseling_pdf(request, patient_id, visit_id):
    # Fetch patient, visit, and counseling note
    visit = get_object_or_404(PatientVisits, id=visit_id)
    patient = get_object_or_404(Patients, id=patient_id)
    counseling = get_object_or_404(Counseling, patient=patient, visit=visit)

    # Prepare context
    context = {
        'counseling': counseling,
        'patient': patient,
        'visit': visit,
    }

    # Render HTML content from a dedicated counseling note template
    html_content = render_to_string('receptionist_template/counseling_notes_details.html', context)

    # Prepare PDF file path
    temp_dir = os.path.join(os.path.expanduser("~"), "pdf_temp")
    os.makedirs(temp_dir, exist_ok=True)
    file_name = f'counseling_{patient.full_name}_{visit.vst}.pdf'
    file_path = os.path.join(temp_dir, file_name)

    # Delete existing PDF if present
    if os.path.exists(file_path):
        os.remove(file_path)

    # Generate PDF using WeasyPrint
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(file_path)

    # Serve PDF as download
    with open(file_path, 'rb') as f:
        pdf_data = f.read()

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response    

def download_referral_pdf(request, patient_id, visit_id):
    # Fetch patient, visit, and referral
    visit = get_object_or_404(PatientVisits, id=visit_id)
    patient = get_object_or_404(Patients, id=patient_id)
    referral = get_object_or_404(Referral, patient=patient, visit=visit)

    # Prepare context
    context = {
        'referral': referral,
        'patient': patient,
        'visit': visit,
    }

    # Render HTML content from a dedicated referral note template
    html_content = render_to_string('receptionist_template/view_referral.html', context)

    # Prepare PDF file path
    temp_dir = os.path.join(os.path.expanduser("~"), "pdf_temp")
    os.makedirs(temp_dir, exist_ok=True)
    file_name = f'referral_{patient.full_name}_{visit.vst}.pdf'
    file_path = os.path.join(temp_dir, file_name)

    # Delete existing PDF if present
    if os.path.exists(file_path):
        os.remove(file_path)

    # Generate PDF using WeasyPrint
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(file_path)

    # Serve PDF as download
    with open(file_path, 'rb') as f:
        pdf_data = f.read()

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response


def download_prescription_notes_pdf(request, patient_id, visit_id):
    # Fetch patient and visit
    patient = get_object_or_404(Patients, id=patient_id)
    visit = get_object_or_404(PatientVisits, id=visit_id)

    # Get all prescriptions for this patient and visit
    prescriptions = Prescription.objects.filter(patient=patient, visit=visit)

    # Prepare context
    context = {
        'patient': patient,
        'visit': visit,
        'prescriptions': prescriptions,
    }

    # Render HTML content using a dedicated template
    html_content = render_to_string('receptionist_template/prescription_notes.html', context)

    # Prepare PDF file path
    temp_dir = os.path.join(os.path.expanduser("~"), "pdf_temp")
    os.makedirs(temp_dir, exist_ok=True)
    file_name = f'prescription_notes_{patient.full_name}_{visit.vst}.pdf'
    file_path = os.path.join(temp_dir, file_name)

    # Remove old file if exists
    if os.path.exists(file_path):
        os.remove(file_path)

    # Generate PDF using WeasyPrint
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(file_path)

    # Serve file as HTTP response
    with open(file_path, 'rb') as f:
        pdf_data = f.read()

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response

def download_prescription_bill_pdf(request, patient_id, visit_id):
    # Fetch patient and visit
    patient = get_object_or_404(Patients, id=patient_id)
    visit = get_object_or_404(PatientVisits, id=visit_id)

    # Get all prescriptions for this visit and patient
    prescriptions = Prescription.objects.filter(patient=patient, visit=visit)

    # Prepare context
    context = {
        'patient': patient,
        'visit': visit,
        'prescriptions': prescriptions,
    }

    # Render HTML content using template
    html_content = render_to_string('receptionist_template/prescription_bill.html', context)

    # Create temporary folder and define file path
    temp_dir = os.path.join(os.path.expanduser("~"), "pdf_temp")
    os.makedirs(temp_dir, exist_ok=True)
    file_name = f'prescription_bill_{patient.full_name}_{visit.vst}.pdf'
    file_path = os.path.join(temp_dir, file_name)

    # Remove old file if it exists
    if os.path.exists(file_path):
        os.remove(file_path)

    # Generate PDF using WeasyPrint
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(file_path)

    # Return PDF as downloadable response
    with open(file_path, 'rb') as f:
        pdf_data = f.read()

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response


@login_required
def download_procedure_result_pdf(request, procedure_id):
    # Fetch procedure or return 404
    procedure = get_object_or_404(Procedure.objects.select_related('patient', 'visit', 'name'), id=procedure_id)

    # Prepare context for template
    context = {
        'procedure': procedure,
    }

    # Render the HTML content using template
    html_content = render_to_string('receptionist_template/pdf_procedure_result.html', context)

    # Create temporary directory for storing the PDF
    temp_dir = os.path.join(os.path.expanduser("~"), "pdf_temp")
    os.makedirs(temp_dir, exist_ok=True)

    # Define safe file name and full path
    file_name = f"procedure_result_{procedure.patient.full_name}_{procedure.procedure_number}.pdf"
    file_path = os.path.join(temp_dir, file_name)

    # Remove file if it already exists
    if os.path.exists(file_path):
        os.remove(file_path)

    # Generate PDF using WeasyPrint
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(file_path)

    # Return the PDF as downloadable response
    with open(file_path, 'rb') as f:
        pdf_data = f.read()

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response    

@login_required
def download_all_procedures_pdf(request, patient_mrn, visit_vst):
    # Get patient and visit
    patient = get_object_or_404(Patients, mrn=patient_mrn)
    visit = get_object_or_404(PatientVisits, vst=visit_vst)

    # Fetch all related procedures
    procedures = Procedure.objects.filter(patient=patient, visit=visit).select_related('name', 'data_recorder')

    if not procedures.exists():
        return HttpResponse("No procedures found for this visit.", status=404)

    context = {
        'patient': patient,
        'visit': visit,
        'procedures': procedures
    }

    # Render the template
    html_content = render_to_string('receptionist_template/pdf_all_procedures.html', context)

    # Generate file
    file_name = f"all_procedures_{patient.full_name}_{visit.vst}.pdf"
    temp_dir = os.path.join(os.path.expanduser("~"), "pdf_temp")
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file_name)

    # Remove existing file
    if os.path.exists(file_path):
        os.remove(file_path)

    # Write PDF
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(file_path)

    # Return file
    with open(file_path, 'rb') as f:
        pdf_data = f.read()

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response    


@login_required
def download_lab_result_pdf(request, lab_id):
    # Fetch the lab order or return 404 if not found
    lab = get_object_or_404(
        LaboratoryOrder.objects.select_related('patient', 'visit', 'data_recorder', 'name'),
        id=lab_id
    )

    # Prepare context for PDF rendering
    context = {
        'lab': lab,
    }

    # Render HTML from template
    html_content = render_to_string('receptionist_template/pdf_lab_result.html', context)

    # Setup temporary directory
    temp_dir = os.path.join(os.path.expanduser("~"), "pdf_temp")
    os.makedirs(temp_dir, exist_ok=True)

    # Safe file name and path
    safe_name = lab.patient.full_name.replace(" ", "_")
    file_name = f"lab_result_{safe_name}_{lab.lab_number}.pdf"
    file_path = os.path.join(temp_dir, file_name)

    # Delete if file exists
    if os.path.exists(file_path):
        os.remove(file_path)

    # Generate PDF with WeasyPrint
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(file_path)

    # Serve the PDF as an HTTP response
    with open(file_path, 'rb') as f:
        pdf_data = f.read()

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response


@login_required
def download_all_lab_results_pdf(request, patient_mrn, visit_vst):
    # Fetch patient and visit objects
    patient = get_object_or_404(Patients, mrn=patient_mrn)
    visit = get_object_or_404(PatientVisits, vst=visit_vst)

    # Fetch all laboratory orders for this patient and visit
    lab_tests = LaboratoryOrder.objects.filter(patient=patient, visit=visit).select_related(
        'name', 'data_recorder'
    )

    if not lab_tests.exists():
        return HttpResponse("No lab results found for this visit.", status=404)

    # Prepare the template context
    context = {
        'patient': patient,
        'visit': visit,
        'lab_tests': lab_tests
    }

    # Render HTML template
    html_content = render_to_string('receptionist_template/pdf_all_lab_results.html', context)

    # Define a safe filename and temporary path
    temp_dir = os.path.join(os.path.expanduser("~"), "pdf_temp")
    os.makedirs(temp_dir, exist_ok=True)
    safe_name = patient.full_name.replace(" ", "_")
    file_name = f"all_lab_results_{safe_name}_{visit.vst}.pdf"
    file_path = os.path.join(temp_dir, file_name)

    # Remove existing file if it exists
    if os.path.exists(file_path):
        os.remove(file_path)

    # Generate the PDF file
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(file_path)

    # Serve the file as an HTTP response
    with open(file_path, 'rb') as f:
        pdf_data = f.read()

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response


@login_required
def download_imaging_result_pdf(request, imaging_id):
    # Fetch the imaging record or return 404
    imaging = get_object_or_404(
        ImagingRecord.objects.select_related('patient', 'visit', 'data_recorder', 'imaging'),
        id=imaging_id
    )

    # Prepare context for rendering
    context = {
        'imaging': imaging,
    }

    # Render HTML content from template
    html_content = render_to_string('receptionist_template/pdf_imaging_result.html', context)

    # Temporary directory
    temp_dir = os.path.join(os.path.expanduser("~"), "pdf_temp")
    os.makedirs(temp_dir, exist_ok=True)

    # Safe filename
    safe_name = imaging.patient.full_name.replace(" ", "_")
    file_name = f"imaging_result_{safe_name}_{imaging.id}.pdf"
    file_path = os.path.join(temp_dir, file_name)

    # Delete existing file if present
    if os.path.exists(file_path):
        os.remove(file_path)

    # Generate PDF using WeasyPrint
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(file_path)

    # Serve PDF
    with open(file_path, 'rb') as f:
        pdf_data = f.read()

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response


@login_required
def download_all_imaging_results_pdf(request, patient_mrn, visit_vst):
    # Fetch patient and visit instances
    patient = get_object_or_404(Patients, mrn=patient_mrn)
    visit = get_object_or_404(PatientVisits, vst=visit_vst)

    # Fetch all imaging records for this visit
    imaging_records = ImagingRecord.objects.filter(patient=patient, visit=visit).select_related(
        'imaging', 'data_recorder'
    )

    if not imaging_records.exists():
        return HttpResponse("No imaging records found for this visit.", status=404)

    # Prepare context for rendering
    context = {
        'patient': patient,
        'visit': visit,
        'imaging_records': imaging_records
    }

    # Render HTML content
    html_content = render_to_string('receptionist_template/pdf_all_imaging_results.html', context)

    # Prepare temporary directory and file path
    temp_dir = os.path.join(os.path.expanduser("~"), "pdf_temp")
    os.makedirs(temp_dir, exist_ok=True)
    safe_name = patient.full_name.replace(" ", "_")
    file_name = f"all_imaging_results_{safe_name}_{visit.vst}.pdf"
    file_path = os.path.join(temp_dir, file_name)

    # Delete existing file if any
    if os.path.exists(file_path):
        os.remove(file_path)

    # Generate PDF
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(file_path)

    # Serve PDF response
    with open(file_path, 'rb') as f:
        pdf_data = f.read()

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response


@login_required
def download_consultation_summary_pdf(request, patient_id, visit_id):
    # Fetch core patient and visit info
    patient = get_object_or_404(Patients, id=patient_id)
    visit = get_object_or_404(PatientVisits, id=visit_id)

    # Query all related models for that visit
    counseling = Counseling.objects.filter(patient=patient, visit=visit).last()
    prescriptions = Prescription.objects.filter(patient=patient, visit=visit)
    observations = ObservationRecord.objects.filter(patient=patient, visit=visit).last()
    discharge_note = DischargesNotes.objects.filter(patient=patient, visit=visit).last()
    referral = Referral.objects.filter(patient=patient, visit=visit).last()
    complaints = ClinicChiefComplaint.objects.filter(patient=patient, visit=visit)
    vitals = PatientVital.objects.filter(patient=patient, visit=visit).last()

    # NEW: Add Consultation Notes
    consultation_note = ConsultationNotes.objects.filter(patient=patient, visit=visit).last()

    # NEW: Add Imaging Records
    imaging_records = ImagingRecord.objects.filter(patient=patient, visit=visit).select_related('imaging', 'data_recorder')

    # NEW: Add Laboratory Orders
    lab_tests = LaboratoryOrder.objects.filter(patient=patient, visit=visit).select_related('name', 'data_recorder')

    # Prepare context
    context = {
        'patient': patient,
        'visit': visit,
        'counseling': counseling,
        'prescriptions': prescriptions,
        'observation_record': observations,
        'discharge_note': discharge_note,
        'referral': referral,
        'complaints': complaints,
        'vitals': vitals,
        'consultation_note': consultation_note,
        'imaging_records': imaging_records,
        'lab_tests': lab_tests,
    }

    # Render the HTML template
    html_content = render_to_string('receptionist_template/pdf_consultation_summary.html', context)

    # Save to a temp directory
    safe_name = patient.full_name.replace(" ", "_")
    file_name = f"consultation_summary_{safe_name}_{visit.vst}.pdf"
    temp_dir = os.path.join(os.path.expanduser("~"), "pdf_temp")
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file_name)

    if os.path.exists(file_path):
        os.remove(file_path)

    # Generate PDF
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(file_path)

    # Return the file as a response
    with open(file_path, 'rb') as f:
        pdf_data = f.read()

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response


@login_required
def download_invoice_bill_pdf(request, patient_id, visit_id):
    # Fetch patient and visit objects
    patient = get_object_or_404(Patients, id=patient_id)
    visit = get_object_or_404(PatientVisits, id=visit_id)

    # Get all orders for this patient and visit
    orders = Order.objects.filter(patient=patient, visit=visit)

    if not orders.exists():
        return HttpResponse("No orders found for this visit.", status=404)

    # Calculate total cost
    total_cost = orders.aggregate(total=Sum('cost'))['total'] or 0

    # Prepare context
    context = {
        'patient': patient,
        'visit': visit,
        'orders': orders,
        'total_cost': total_cost,
    }

    # Render HTML content
    html_content = render_to_string('receptionist_template/invoice_template.html', context)

    # Define PDF storage path
    temp_dir = os.path.join(os.path.expanduser("~"), "pdf_temp")
    os.makedirs(temp_dir, exist_ok=True)
    safe_name = patient.full_name.replace(" ", "_")
    file_name = f"invoice_bill_{safe_name}_{visit.vst}.pdf"
    file_path = os.path.join(temp_dir, file_name)

    # Remove old file if it exists
    if os.path.exists(file_path):
        os.remove(file_path)

    # Generate PDF with WeasyPrint
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(file_path)

    # Return file as download
    with open(file_path, 'rb') as f:
        pdf_data = f.read()

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response

@login_required
def consultation_notes_view(request):
    # Get all patients who have consultation notes
    patient_records = Patients.objects.filter(
        consultationnotes__isnull=False
    ).distinct().order_by('-consultationnotes__updated_at')

    return render(request, 'receptionist_template/manage_consultation_notes.html', {
        'patient_records': patient_records
    })





    


















