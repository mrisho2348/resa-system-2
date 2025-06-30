import calendar
from datetime import  datetime
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import now
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
from datetime import timedelta, date
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
            dividable = medicine.is_dividable
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
    today = now().date()
    ten_days_from_now = today + timedelta(days=10)

    context = {
        'total_patients_count': Patients.objects.count(),
        'total_medicines_count': Medicine.objects.count(),
        'total_prescriptions_count': Prescription.objects.count(),
        'out_of_stock_count': Medicine.objects.filter(remain_quantity=0).count(),
        'daily_dispensed_count': Prescription.objects.filter(updated_at__date=today).count(),
        'expired_medicines_count': Medicine.objects.filter(expiration_date__lt=today).count(),
        'expiring_soon_count': Medicine.objects.filter(expiration_date__range=[today, ten_days_from_now]).count(),
        'total_quantity': Medicine.objects.aggregate(total=Sum('remain_quantity'))['total'] or 0,
    }

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

    return render(request, 'pharmacist_template/manage_prescription_list.html', {
        'visit_total_prices': grouped_visits,
    })

@login_required
def todays_prescriptions(request):
    today = now().date()

    # Step 1: Filter prescriptions where the visit was created today
    grouped_visits = (
        Prescription.objects
        .filter(visit__created_at__date=today)
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
        .annotate(total_price=Sum('total_price'))
        .order_by('-visit__created_at')
    )

    # Step 2: Attach prescriptions and statuses
    for visit in grouped_visits:
        prescriptions = Prescription.objects.filter(visit__id=visit['visit__id']).select_related('medicine')
        visit['prescriptions'] = prescriptions

        statuses = prescriptions.values_list('status', flat=True).distinct()
        issued = prescriptions.values_list('issued', flat=True).distinct()
        verified = prescriptions.values_list('verified', flat=True).distinct()

        visit['status'] = statuses[0] if len(statuses) == 1 else "Mixed"
        visit['issued'] = issued[0] if len(issued) == 1 else "Mixed"
        visit['verified'] = verified[0] if len(verified) == 1 else "Mixed"

    return render(request, 'pharmacist_template/todays_prescription_list.html', {
        'visit_total_prices': grouped_visits,
    })  


@csrf_exempt
@login_required
def add_medicine(request):
    if request.method == 'POST':
        try:
            # Extract data from request
            medicine_id = request.POST.get('medicine_id')
            drug_name = request.POST.get('drug_name').strip()
            drug_type = request.POST.get('drug_type')
            dividing_unit = int(request.POST.get('dividing_unit') or 125)
            formulation_unit = request.POST.get('formulation_unit')
            manufacturer = request.POST.get('manufacturer').strip()
            quantity = request.POST.get('quantity')
            is_dividable = request.POST.get('is_dividable')
            batch_number = request.POST.get('batch_number').strip()
            expiration_date = request.POST.get('expiration_date')
            cash_cost = request.POST.get('cash_cost')
            insurance_cost = request.POST.get('insurance_cost')
            nhif_cost = request.POST.get('nhif_cost')
            buying_price = request.POST.get('buying_price')

            # Validate expiration_date
            if expiration_date:
                expiration_date_obj = datetime.strptime(expiration_date, '%Y-%m-%d').date()
                if expiration_date_obj <= datetime.now().date():
                    return JsonResponse({'success': False, 'message':  'Expiration date must be in the future.'})

             # Check if required fields are provided
            if not (drug_name and quantity and buying_price):
                return JsonResponse({'success': False, 'message': 'Missing required fields'})

            # Convert quantity and buying_price to integers .exclude(pk=disease_id)
            try:
                quantity = int(quantity)
                buying_price = float(buying_price)
            except ValueError:
                return JsonResponse({'success': False, 'message': 'Invalid quantity or buying price'})
            # Check if this is an edit operation
            if medicine_id:
                if Medicine.objects.exclude(pk=medicine_id).filter(drug_name=drug_name).exists():
                    return JsonResponse({'success': False, 'message':  'The medicine drug with the same name  already exists.'})
                if Medicine.objects.exclude(pk=medicine_id).filter(batch_number=batch_number).exists():
                    return JsonResponse({'success': False, 'message': 'The  medicine drug with the same bath number  already exists.'})
                
                
                medicine = Medicine.objects.get(pk=medicine_id)
                medicine.drug_name = drug_name
                medicine.drug_type = drug_type
                medicine.formulation_unit = formulation_unit
                medicine.manufacturer = manufacturer
                medicine.quantity = quantity
                medicine.dividing_unit = dividing_unit
                medicine.remain_quantity = quantity
                medicine.is_dividable = is_dividable
                medicine.batch_number = batch_number
                medicine.expiration_date = expiration_date
                medicine.cash_cost = cash_cost
                medicine.insurance_cost = insurance_cost
                medicine.nhif_cost = nhif_cost
                medicine.buying_price = buying_price
                medicine.save()
                return JsonResponse({'success': True, 'message': 'medicine drug is updated successfully'})
            else:
                # Check for uniqueness
                if Medicine.objects.filter(drug_name=drug_name).exists():
                    return JsonResponse({'success': False, 'message': 'The  medicine drug with the same name  already exists.'})
                if Medicine.objects.filter(batch_number=batch_number).exists():
                    return JsonResponse({'success': False, 'message':  'The  medicine drug with the same bath number  already exists.'})

                # Create a new Medicine instance
                medicine = Medicine(
                    drug_name=drug_name,
                    drug_type=drug_type,
                    formulation_unit=formulation_unit,
                    manufacturer=manufacturer,
                    quantity=quantity,
                    remain_quantity=quantity,
                    is_dividable=is_dividable,
                    dividing_unit=dividing_unit,
                    batch_number=batch_number,
                    expiration_date=expiration_date,
                    cash_cost=cash_cost,
                    insurance_cost=insurance_cost,
                    nhif_cost=nhif_cost,
                    buying_price=buying_price,
                )

            # Save the medicine instance
            medicine.save()
            return JsonResponse({'success': True, 'message': 'medicine drug is added successfully'})
        except ObjectDoesNotExist:
            return JsonResponse({'success': False, 'message':  'Medicine not found.'})
        except ValidationError as ve:
            return JsonResponse({'success': False, 'message':  ve.message})
        except Exception as e:
            return JsonResponse({'success': False, 'message':  str(e)})
    return JsonResponse({'success': False, 'message':  'Invalid request method'})



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


@login_required
def medicine_list(request):
    # Retrieve medicines and check for expired ones
    medicines = Medicine.objects.all()
    # Render the template with medicine data and notifications
    return render(request, 'pharmacist_template/manage_medicine.html', {'medicines': medicines})   

@login_required
def lab_reagent_expiring_soon(request):
    today = date.today()
    ten_days_from_now = today + timedelta(days=10)
    reagents = Reagent.objects.filter(expiration_date__range=[today, ten_days_from_now])

    # Annotate each with days left
    for reagent in reagents:
        if reagent.expiration_date:
            reagent.days_left = (reagent.expiration_date - today).days
        else:
            reagent.days_left = None

    return render(request, 'pharmacist_template/reagent_expiring_soon_list.html', {'reagents': reagents})

@login_required
def lab_reagent_out_of_stock(request):
    out_of_stock_reagents = Reagent.objects.filter(remaining_quantity__lte=0).order_by('name')
    context = {
        'reagents': out_of_stock_reagents,
        'title': 'Out of Stock Reagents',
    }
    return render(request, 'pharmacist_template/reagent_out_of_stock_list.html', context)

@login_required
def lab_reagent_expired(request):
    today = now().date()
    expired_reagents = Reagent.objects.filter(expiration_date__lt=today).order_by('expiration_date')
    context = {
        'reagents': expired_reagents,
        'title': 'Expired Reagents',
    }
    return render(request, 'pharmacist_template/reagent_expired_list.html', context)

def reagent_counts_api(request):
    today = now().date()
    soon_threshold = today + timedelta(days=10)

    expired_count = Reagent.objects.filter(expiration_date__lt=today).count()
    expiring_soon_count = Reagent.objects.filter(expiration_date__gte=today, expiration_date__lte=soon_threshold).count()
    out_of_stock_count = Reagent.objects.filter(remaining_quantity__lte=0).count()

    return JsonResponse({
        'expired': expired_count,
        'expiring_soon': expiring_soon_count,
        'out_of_stock': out_of_stock_count,
    })


@login_required
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
def visit_list(request):
    visits = PatientVisits.objects.select_related('patient').order_by('-created_at')

    # Get all prescriptions related to the visits
    all_prescriptions = Prescription.objects.filter(visit__in=visits)

    # Initialize maps
    prescription_map = {}       # True if prescriptions exist for visit
    paid_prescription_map = {}  # True if any prescription is paid
    verified_prescription_map = {}  # True if any prescription is verified
    issued_prescription_map = {}    # True if any prescription is issued

    for pres in all_prescriptions:
        visit_id = pres.visit.id
        prescription_map[visit_id] = True

        if pres.status == 'Paid':
            paid_prescription_map[visit_id] = True

        if pres.verified == 'verified':
            verified_prescription_map[visit_id] = True

        if pres.issued == 'issued':
            issued_prescription_map[visit_id] = True

    context = {
        'visits': visits,
        'prescription_map': prescription_map,
        'paid_prescription_map': paid_prescription_map,
        'verified_prescription_map': verified_prescription_map,
        'issued_prescription_map': issued_prescription_map,
    }

    return render(request, 'pharmacist_template/visit_list.html', context)


@login_required
def save_prescription(request, patient_id, visit_id):
    try:
        # Get patient and visit objects first
        try:
            patient = Patients.objects.get(id=patient_id)
        except Patients.DoesNotExist:
            return render(request, '404.html', {'error_message': "Patient not found."})

        try:
            visit = PatientVisits.objects.get(id=visit_id, patient_id=patient_id)
        except PatientVisits.DoesNotExist:
            return render(request, '404.html', {'error_message': "Visit not found."})
        # Retrieve related data
        frequencies = PrescriptionFrequency.objects.all()

        current_date = timezone.now().date()      

        medicines = Medicine.objects.filter(
            remain_quantity__gt=0,
            expiration_date__gt=current_date
        ).distinct()    

        return render(request, 'pharmacist_template/prescription_template.html', {
            'patient': patient,
            'visit': visit,        
            'medicines': medicines,          
            'frequencies': frequencies,
        })

    except Exception as e:
        return render(request, '404.html', {
            'error_message': f"Oop's sorry we can't find that page! ({str(e)})"
        })


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

                if quantity_used_str is None:
                    raise ValueError(f'Invalid quantity for {medicine.drug_name}. Quantity cannot be empty.')

                try:
                    quantity_used = int(quantity_used_str)
                except ValueError:
                    raise ValueError(f'Invalid quantity for {medicine.drug_name}. Quantity must be a valid number.')

                if quantity_used < 0:
                    raise ValueError(f'Invalid quantity for {medicine.drug_name}. Quantity must be a non-negative number.')

                # Retrieve the remaining quantity of the medicine
                remain_quantity = medicine.remain_quantity

                if remain_quantity is not None and quantity_used > remain_quantity:
                    raise ValueError(f'Insufficient stock for {medicine.drug_name}. Only {remain_quantity} available.')

                # Reduce the remain quantity of the medicine
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
                
   
@csrf_exempt
@login_required
def medicine_counts_api(request):
    today = now().date()
    in_10_days = today + timedelta(days=10)

    out_of_stock_count = Medicine.objects.filter(remain_quantity=0).count()
    total_quantity = Medicine.objects.filter(remain_quantity__gt=0).aggregate(total=Sum('remain_quantity'))['total'] or 0
    expiring_soon_count = Medicine.objects.filter(expiration_date__range=(today, in_10_days)).count()
    expired_count = Medicine.objects.filter(expiration_date__lt=today).count()

    return JsonResponse({
        'out_of_stock': out_of_stock_count,
        'total_quantity': total_quantity,
        'expiring_soon': expiring_soon_count,
        'expired': expired_count,
    })


@login_required
def reagent_list(request):
    reagent_list = Reagent.objects.all()
    today = date.today()
        # Annotate each with days left
    for reagent in reagent_list:
        if reagent.expiration_date:
            reagent.days_left = (reagent.expiration_date - today).days
        else:
            reagent.days_left = None

    return render(request, 'pharmacist_template/manage_reagent_list.html', {
        'reagent_list': reagent_list,
      
    })


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
