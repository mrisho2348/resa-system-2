# Standard library imports
import calendar
from datetime import datetime, date, timedelta
from decimal import Decimal
import os
from collections import defaultdict
# Django imports
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404, HttpResponse
from django.db import transaction, IntegrityError
from django.db.models import F, Sum, Q, ExpressionWrapper, DecimalField, Max, Count, DurationField
from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.utils import timezone
from django.utils.timezone import now
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.conf import settings
from weasyprint import HTML
import tempfile
from django.template.loader import render_to_string
# Local imports
from clinic.forms import StaffProfileForm
from clinic.models import Staffs, Patients
from .models import (
    Medicine, Employee, EmployeeDeduction, MedicineDosage, MedicineRoute, PatientVisits, 
    Prescription, PrescriptionFrequency, Reagent, SalaryChangeRecord, WalkInCustomer, WalkInPrescription, WalkInVisit
)
from io import BytesIO

# ==================== UTILITY FUNCTIONS ====================
def get_today_and_ten_days():
    """Return today's date and date 10 days from now"""
    today = timezone.now().date()
    ten_days_from_now = today + timedelta(days=10)
    return today, ten_days_from_now


def get_recent_visits_with_prescriptions(limit=10):
    """Get recent visits with prescriptions"""
    return (
        Prescription.objects
        .values(
            'visit__id',
            'visit__vst',
            'visit__created_at',
            'visit__patient__id',
            'visit__patient__first_name',
            'visit__patient__middle_name',
            'visit__patient__last_name',
        )
        .annotate(total_price=Sum('total_price'))
        .order_by('-visit__created_at')[:limit]
    )

def get_recent_walkin_visits_with_prescriptions(limit=10):
    """Get recent walk-in visits with prescriptions"""
    return (
        WalkInPrescription.objects
        .values(
            'visit__id',
            'visit__visit_number',
            'visit__visit_date',
            'visit__customer__id',
            'visit__customer__first_name',
            'visit__customer__middle_name',
            'visit__customer__last_name',
            'visit__customer__phone_number',
            'visit__customer__payment_form',
        )
        .annotate(total_price=Sum('total_price'))
        .order_by('-visit__visit_date')[:limit]
    )

def attach_walkin_prescriptions_to_visits(visits):
    """Attach prescriptions and status information to walk-in visit data"""
    for visit in visits:
        prescriptions = WalkInPrescription.objects.filter(
            visit__id=visit['visit__id']
        ).select_related('medicine', 'frequency')
        
        visit['prescriptions'] = prescriptions
        
        # Derive consistent statuses
        statuses = prescriptions.values_list('status', flat=True).distinct()
        issued = prescriptions.values_list('issued', flat=True).distinct()
        verified = prescriptions.values_list('verified', flat=True).distinct()
        
        visit['status'] = statuses[0] if len(statuses) == 1 else "mixed"
        visit['issued'] = issued[0] if len(issued) == 1 else "mixed"
        visit['verified'] = verified[0] if len(verified) == 1 else "mixed"
    
    return visits

def attach_prescriptions_to_visits(visits):
    """Attach prescriptions and status information to visit data"""
    for visit in visits:
        prescriptions = Prescription.objects.filter(
            visit__id=visit['visit__id']
        ).select_related('medicine')
        
        visit['prescriptions'] = prescriptions
        
        # Derive consistent statuses
        statuses = prescriptions.values_list('status', flat=True).distinct()
        issued = prescriptions.values_list('issued', flat=True).distinct()
        verified = prescriptions.values_list('verified', flat=True).distinct()
        
        visit['status'] = statuses[0] if len(statuses) == 1 else "status"
        visit['issued'] = issued[0] if len(issued) == 1 else "issued"
        visit['verified'] = verified[0] if len(verified) == 1 else "verified"
    
    return visits


def get_low_stock_medicines(threshold=20, limit=10):
    """Get medicines with stock below threshold percentage"""
    return Medicine.objects.annotate(
        remain_quantity_percentage=ExpressionWrapper(
            F('remain_quantity') * 100 / F('quantity'),
            output_field=DecimalField()
        )
    ).filter(remain_quantity_percentage__lt=threshold).order_by(
        'remain_quantity_percentage'
    )[:limit]

def get_expiring_soon_medicines(days=10, limit=10):
    """Get medicines expiring within the specified number of days"""
    today, ten_days_from_now = get_today_and_ten_days()
    return Medicine.objects.filter(
        expiration_date__range=[today, ten_days_from_now]
    ).annotate(
        days_until_expiry=ExpressionWrapper(
            F('expiration_date') - today,
            output_field=DurationField()
        ),
        remain_quantity_percentage=ExpressionWrapper(
            F('remain_quantity') * 100 / F('quantity'),
            output_field=DecimalField()
        )
    ).order_by('expiration_date')[:limit]




        
@csrf_exempt
def get_cash_price(request):
    """Get cash price for a medicine"""
    medicine_id = request.GET.get('medicine_id')
    
    if not medicine_id:
        return JsonResponse({'error': 'Medicine ID is required'}, status=400)
    
    try:
        medicine = Medicine.objects.get(pk=medicine_id)
        return JsonResponse({'cash_price': medicine.cash_cost})
    except Medicine.DoesNotExist:
        return JsonResponse({'error': 'Medicine not found'}, status=404)





@csrf_exempt
def restock_medicine(request):
    """Restock a medicine with new quantity, batch number, and expiry date"""
    if request.method == 'POST':
        try:
            medicine_id = request.POST.get('medicine_id')
            quantity_to_add = int(request.POST.get('quantity_to_add'))
            new_batch_number = request.POST.get('new_batch_number')
            new_expiry_date = request.POST.get('new_expiry_date')
            
            medicine = get_object_or_404(Medicine, id=medicine_id)
            
            # Update medicine quantity
            medicine.quantity += quantity_to_add
            medicine.remain_quantity += quantity_to_add
            
            # Update batch number if provided
            if new_batch_number:
                medicine.batch_number = new_batch_number
            
            # Update expiry date if provided
            if new_expiry_date:
                medicine.expiration_date = new_expiry_date
            
            # Recalculate total buying price if needed
            if medicine.buying_price:
                medicine.total_buying_price = float(medicine.buying_price) * medicine.quantity
            
            medicine.save()
            
            return JsonResponse({
                'status': 'success',
                'message': f'Successfully restocked {medicine.drug_name} with {quantity_to_add} units.'
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error restocking medicine: {str(e)}'
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })


@csrf_exempt
def verify_prescriptions(request):
    """Mark all prescriptions for a visit as verified"""
    if request.method == 'POST':
        visit_number = request.POST.get('visit_number')
        try:
            prescriptions = Prescription.objects.filter(visit__vst=visit_number)
            for prescription in prescriptions:
                prescription.verified = 'verified'
                prescription.save()
            return JsonResponse({'success': True, 'message': 'Prescriptions verified successfully.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)

@csrf_exempt
def issue_prescriptions(request):
    """Mark all prescriptions for a visit as issued"""
    if request.method == 'POST':
        visit_number = request.POST.get('visit_number')
        try:
            prescriptions = Prescription.objects.filter(visit__vst=visit_number)
            for prescription in prescriptions:
                prescription.issued = 'issued'
                prescription.save()
            return JsonResponse({'success': True, 'message': 'Prescriptions issued successfully.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)


@csrf_exempt
def unverify_prescriptions(request):
    """Mark all prescriptions for a visit as unverified"""
    if request.method == 'POST':
        visit_number = request.POST.get('visit_number')
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
    return JsonResponse({'error': 'Invalid request.'}, status=400)


@csrf_exempt
def unissue_prescriptions(request):
    """Mark all prescriptions for a visit as not issued"""
    if request.method == 'POST':
        visit_number = request.POST.get('visit_number')
        try:
            prescriptions = Prescription.objects.filter(visit__vst=visit_number)
            for prescription in prescriptions:
                prescription.issued = 'Not Issued'
                prescription.status = 'Unpaid'
                prescription.save()
            return JsonResponse({'message': 'Prescriptions unissued successfully.'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request.'}, status=400)


@csrf_exempt
@require_POST
def add_medicine(request):
    """Add or update a medicine"""
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
                return JsonResponse({
                    'success': False, 
                    'message': 'Expiration date must be in the future.'
                })

        # Check if required fields are provided
        if not (drug_name and quantity and buying_price):
            return JsonResponse({
                'success': False, 
                'message': 'Missing required fields'
            })

        # Convert quantity and buying_price to numbers
        try:
            quantity = int(quantity)
            buying_price = float(buying_price)
        except ValueError:
            return JsonResponse({
                'success': False, 
                'message': 'Invalid quantity or buying price'
            })
            
        # Check if this is an edit operation
        if medicine_id:
            if Medicine.objects.exclude(pk=medicine_id).filter(drug_name=drug_name).exists():
                return JsonResponse({
                    'success': False, 
                    'message': 'The medicine drug with the same name already exists.'
                })
            if Medicine.objects.exclude(pk=medicine_id).filter(batch_number=batch_number).exists():
                return JsonResponse({
                    'success': False, 
                    'message': 'The medicine drug with the same bath number already exists.'
                })
            
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
            return JsonResponse({
                'success': True, 
                'message': 'Medicine drug updated successfully'
            })
        else:
            # Check for uniqueness for new medicine
            if Medicine.objects.filter(drug_name=drug_name).exists():
                return JsonResponse({
                    'success': False, 
                    'message': 'The medicine drug with the same name already exists.'
                })
            if Medicine.objects.filter(batch_number=batch_number).exists():
                return JsonResponse({
                    'success': False, 
                    'message': 'The medicine drug with the same bath number already exists.'
                })

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
            return JsonResponse({
                'success': True, 
                'message': 'Medicine drug added successfully'
            })
    except ObjectDoesNotExist:
        return JsonResponse({'success': False, 'message': 'Medicine not found.'})
    except ValidationError as ve:
        return JsonResponse({'success': False, 'message': ve.message})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@csrf_exempt
@require_POST
def add_remoteprescription(request):
    """Add prescription remotely for both regular and walk-in patients"""
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
            total_prices = request.POST.getlist('total_price[]')
            entered_by = request.user.staff

            # Handle walk-in patients
            if not patient_id:
                # Create a temporary patient record for walk-in
                walkin_payment_method = request.POST.get('walkin_payment_method', 'Cash')
                walkin_customer_name = request.POST.get('walkin_customer_name', 'Walk-in Customer')
                
                # Create a minimal patient record
                patient = Patients.objects.create(
                    first_name=walkin_customer_name or 'Walk-in',
                    last_name='Customer',
                    payment_form=walkin_payment_method,
                    insurance_name=request.POST.get('insurance_name') if walkin_payment_method == 'Insurance' else '',
                    # Set other required fields with default values
                    gender='U',  # Unknown
                    age=0,
                    mrn=f"WALKIN-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    # Add other required fields as needed
                )
            else:
                # Retrieve the existing patient
                patient = Patients.objects.get(id=patient_id)

            # Retrieve visit if available
            visit = None
            if visit_id:
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
                    frequency_obj=PrescriptionFrequency.objects.get(id=frequencies[i]),
                    duration=durations[i],
                    quantity_used=quantity_used,
                    total_price=total_prices[i]
                )

            return JsonResponse({'status': 'success', 'message': 'Prescription saved.'})
    except ValueError as ve:
        return JsonResponse({'status': 'error', 'message': str(ve)})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred: ' + str(e)})
    
@csrf_exempt
@require_POST
def add_walkin_prescription(request):
    """Add prescription for walk-in customers with enhanced validation and visit management"""
    try:
        with transaction.atomic():
            # ---------------- Customer Data ----------------
            first_name = request.POST.get('walkin_first_name')
            middle_name = request.POST.get('walkin_middle_name', '')
            last_name = request.POST.get('walkin_last_name', '')
            gender = request.POST.get('walkin_gender', '')
            age = request.POST.get('walkin_age')
            phone_number = request.POST.get('walkin_phone_number', '')
            address = request.POST.get('walkin_address', '')
            payment_form = request.POST.get('walkin_payment_form', 'cash')

            # Validate required fields
            if not first_name:
                return JsonResponse({'status': 'error', 'message': 'Customer first name is required'})
            if not payment_form:
                return JsonResponse({'status': 'error', 'message': 'Payment method is required'})

            # Handle insurance details
            if payment_form == 'insurance':
                insurance_name = request.POST.get('insurance_name', '')
                insurance_number = request.POST.get('insurance_number', '')
                if not insurance_name or not insurance_number:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Insurance details are required for insurance payments'
                    })

            # Find or create customer
            customer_filter_params = {
                'first_name': first_name,
                'last_name': last_name,
            }
            if phone_number:
                customer_filter_params['phone_number'] = phone_number

            customer, created = WalkInCustomer.objects.get_or_create(
                **customer_filter_params,
                defaults={
                    'middle_name': middle_name,
                    'gender': gender,
                    'age': age,
                    'address': address,
                    'payment_form': payment_form,
                }
            )

            # Update existing customer
            if not created:
                if middle_name:
                    customer.middle_name = middle_name
                if gender:
                    customer.gender = gender
                if age:
                    customer.age = age
                if address:
                    customer.address = address
                if payment_form:
                    customer.payment_form = payment_form
                customer.save()

            # ---------------- Visit ----------------
            visit = WalkInVisit.objects.create(
                customer=customer,
                notes=f"Prescription visit - {timezone.now().strftime('%Y-%m-%d %H:%M')}"
            )

            # ---------------- Prescription Data ----------------
            medicines = request.POST.getlist('medicine[]')
            dosages = request.POST.getlist('dosage[]')
            frequencies = request.POST.getlist('frequency[]')
            durations = request.POST.getlist('duration[]')
            quantities = request.POST.getlist('quantity[]')
            routes = request.POST.getlist('route[]')
            total_prices = request.POST.getlist('total_price[]')

            if not all([medicines, dosages, frequencies, durations, quantities, routes]):
                return JsonResponse({'status': 'error', 'message': 'Incomplete prescription data'})

            if len(medicines) == 0:
                return JsonResponse({'status': 'error', 'message': 'No medicines in prescription'})

            # Staff who entered
            try:
                entered_by = request.user.staff
            except AttributeError:
                return JsonResponse({'status': 'error', 'message': 'Staff information not found'})

            # Pre-check all medicines
            for i in range(len(medicines)):
                try:
                    medicine = Medicine.objects.get(id=medicines[i])
                    quantity_used = int(quantities[i])

                    if medicine.expiration_date and medicine.expiration_date < timezone.now().date():
                        return JsonResponse({
                            'status': 'error',
                            'message': f'Cannot prescribe {medicine.drug_name}, expired on {medicine.expiration_date}.'
                        })

                    if medicine.remain_quantity is not None and quantity_used > medicine.remain_quantity:
                        return JsonResponse({
                            'status': 'error',
                            'message': f'Insufficient stock for {medicine.drug_name}. '
                                       f'Only {medicine.remain_quantity} available.'
                        })
                except Medicine.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': f'Medicine with ID {medicines[i]} not found'})

            # ---------------- Save Prescriptions ----------------
            for i in range(len(medicines)):
                medicine = Medicine.objects.get(id=medicines[i])
                quantity_used = int(quantities[i])

                prescription = WalkInPrescription(
                    visit=visit,
                    medicine=medicine,
                    entered_by=entered_by,
                    duration=int(durations[i]),
                    quantity_used=quantity_used,
                    total_price=Decimal(total_prices[i]),
                    status='unpaid',
                    verified='verified',
                    issued='issued',                  
                )

                # Frequency (FK)
                if frequencies[i]:
                    try:
                        prescription.frequency = PrescriptionFrequency.objects.get(id=frequencies[i])
                    except PrescriptionFrequency.DoesNotExist:
                        pass

                # Dosage (FK)
                if dosages[i]:
                    try:
                        prescription.dosage = MedicineDosage.objects.get(id=dosages[i].strip())
                    except MedicineDosage.DoesNotExist:
                        return JsonResponse({'status': 'error', 'message': f'Invalid dosage ID: {dosages[i]}'})

                # Route (FK)
                if routes[i]:
                    try:
                        prescription.route = MedicineRoute.objects.get(id=routes[i].strip())
                    except MedicineRoute.DoesNotExist:
                        return JsonResponse({'status': 'error', 'message': f'Invalid route ID: {routes[i]}'})


                # Validate & save
                try:
                    prescription.full_clean()
                except ValidationError as e:
                    return JsonResponse({'status': 'error', 'message': str(e)})

                prescription.save()

            return JsonResponse({
                'status': 'success',
                'message': f'Walk-in prescription saved successfully. Visit Number: {visit.visit_number}',
                'visit_id': visit.id
            })

    except Medicine.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'One or more medicines not found'})
    except ValueError as e:
        return JsonResponse({'status': 'error', 'message': f'Invalid data format: {str(e)}'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'An unexpected error occurred: {str(e)}'})

        

@login_required
def walkin_prescription_list(request):
    """View for walk-in prescription list grouped by visit, including visit status."""
    try:
        # Step 1: Fetch grouped visits with aggregated total price
        grouped_visits = (
            WalkInPrescription.objects
            .values(
                'visit__id',
                'visit__visit_number',
                'visit__visit_date',
                'visit__customer__id',
                'visit__customer__first_name',
                'visit__customer__middle_name',
                'visit__customer__last_name',
                'visit__customer__gender',
                'visit__customer__age',
                'visit__customer__pharmacy_number',
                'visit__customer__address',
                'visit__customer__phone_number',
                'visit__customer__payment_form',
            )
            .annotate(total_price=Sum('total_price'))
            .order_by('-visit__visit_date')
        )

        # Step 2: Fetch prescriptions for those visits
        visit_ids = [v['visit__id'] for v in grouped_visits]
        prescriptions = (
            WalkInPrescription.objects
            .filter(visit_id__in=visit_ids)
            .select_related('medicine', 'frequency', 'entered_by')
        )

        # Step 3: Group prescriptions by visit ID
        prescriptions_by_visit = defaultdict(list)
        for p in prescriptions:
            prescriptions_by_visit[p.visit_id].append(p)

        # Step 4: Attach prescriptions + visit status to each grouped visit
        for visit in grouped_visits:
            visit_id = visit['visit__id']
            related_prescriptions = prescriptions_by_visit.get(visit_id, [])
            visit['prescriptions'] = related_prescriptions

            # Get visit object to compute status
            try:
                visit_obj = WalkInVisit.objects.get(id=visit_id)
                visit['visit_status'] = WalkInPrescription.get_visit_status(visit_obj)
            except WalkInVisit.DoesNotExist:
                visit['visit_status'] = {
                    "verified": "visit_not_found",
                    "issued": "visit_not_found",
                    "status": "visit_not_found"
                }

        return render(request, 'pharmacist_template/manage_walkin_prescription_list.html', {
            'visit_total_prices': grouped_visits,
        })

    except Exception as e:
        return render(request, '404.html', {
            'error_message': f"An error occurred: {str(e)}"
        })

@login_required
def download_prescription_notes(request, visit_id):
    """
    Generate or download prescription notes PDF for a visit.
    Auto-generates prescription_notes_id if it doesn't exist.
    """
    # 1. Get the visit
    visit = get_object_or_404(WalkInVisit, id=visit_id)

    # 2. Generate prescription_notes_id if missing
    if not visit.prescription_notes_id:
        visit.generate_prescription_notes_id()  # This will save the ID in DB

    # 3. Get prescriptions for this visit
    prescriptions = WalkInPrescription.objects.filter(visit=visit)

    # 4. Prepare context for template
    context = {
        'visit': visit,
        'prescriptions': prescriptions,
         'pharmacist': request.user.staff if hasattr(request.user, 'staff') else None,
    }

    # 5. Render HTML template
    html_string = render_to_string('pharmacist_template/prescription_notes_pdf.html', context)

    # 6. Create PDF in memory
    buffer = BytesIO()
    HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(buffer)
    pdf_content = buffer.getvalue()
    buffer.close()

    # 7. Create HTTP response
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="prescription_notes_{visit.prescription_notes_id}.pdf"'

    return response

@login_required
def update_walkin_payment_status(request):
    """Update payment status for walk-in prescriptions and visit with inventory management"""
    if request.method == 'POST':
        try:
            visit_id = request.POST.get('visit_id')
            action = request.POST.get('action')  # 'pay' or 'unpay'
            
            if not visit_id or not action:
                return JsonResponse({'status': 'error', 'message': 'Missing parameters.'})
            
            # Map action → status
            status_map = {
                'pay': 'paid',
                'unpay': 'unpaid',
            }
            
            if action not in status_map:
                return JsonResponse({'status': 'error', 'message': 'Invalid action.'})
            
            new_status = status_map[action]
            
            # Get visit and prescriptions
            with transaction.atomic():
                visit = WalkInVisit.objects.select_for_update().get(id=visit_id)
                prescriptions = WalkInPrescription.objects.filter(visit=visit)
                
                # If trying to mark as paid, enforce validation and update inventory
                if new_status == 'paid':
                    # Check if all prescriptions are verified and issued
                    if not all(p.verified == 'verified' for p in prescriptions):
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Cannot mark as paid until all prescriptions are verified.'
                        })
                    
                    if not all(p.issued == 'issued' for p in prescriptions):
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Cannot mark as paid until all prescriptions are issued.'
                        })
                    
                    # Deduct medicine quantities from inventory
                    for prescription in prescriptions:
                        medicine = prescription.medicine
                        if medicine.remain_quantity < prescription.quantity_used:
                            return JsonResponse({
                                'status': 'error', 
                                'message': f'Insufficient inventory for {medicine.drug_name}. Only {medicine.quantity} available but {prescription.quantity_used} required.'
                            })
                        
                        # Deduct the quantity
                        medicine.remain_quantity -= prescription.quantity_used
                        medicine.save()
                
                # If unpaying, restore inventory (if previously paid)
                elif new_status == 'unpaid':
                    # Check if currently paid
                    if all(p.status == 'paid' for p in prescriptions):
                        # Restore medicine quantities to inventory
                        for prescription in prescriptions:
                            medicine = prescription.medicine
                            medicine.remain_quantity += prescription.quantity_used
                            medicine.save()
                
                # Update all prescriptions
                prescriptions.update(status=new_status)
                
                # Also update visit status (if your WalkInVisit has a field for this)
                if hasattr(visit, "status"):
                    visit.status = new_status
                    visit.save()
                
                message = f"Payment status updated to {new_status} for visit {visit.visit_number}."
                return JsonResponse({'status': 'success', 'message': message})
        
        except WalkInVisit.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Visit not found.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@login_required
def generate_walkin_receipt_pdf(request, visit_id):
    """Generate PDF receipt for a walk-in visit"""
    try:
        # --- 1. Get visit and prescriptions ---
        visit = WalkInVisit.objects.get(id=visit_id)
        prescriptions = WalkInPrescription.objects.filter(visit=visit)

        # --- 2. Check if visit is paid and needs receipt number ---
        has_paid = prescriptions.filter(status="paid").exists()
        if has_paid and not visit.receipt_number:
            visit.generate_receipt_number()  # auto-generate receipt

        # --- 3. Calculate totals ---
        total_price = sum(p.total_price for p in prescriptions if p.total_price)
        tax_rate = Decimal("0.10")  # 10% tax
        tax = total_price * tax_rate
        grand_total = total_price + tax

        context = {
            "visit": visit,
            "prescriptions": prescriptions,
            "total_price": total_price,
            "tax": tax,
            "grand_total": grand_total,
            'pharmacist': request.user.staff if hasattr(request.user, 'staff') else None,
        }

        # --- 4. Render HTML template ---
        html_string = render_to_string(
            "pharmacist_template/walkin_receipt_pdf.html", context
        )

        # --- 5. Generate PDF with WeasyPrint ---
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        result = html.write_pdf()

        # --- 6. Create response ---
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="receipt_{visit.visit_number}.pdf"'
        )
        response.write(result)
        return response

    except WalkInVisit.DoesNotExist:
        return HttpResponse("Visit not found", status=404)
    except Exception as e:
        return HttpResponse(f"Error generating PDF: {str(e)}", status=500)



@login_required
def walkin_prescription_stats(request):
    """Get statistics for walk-in prescriptions"""
    try:
        # Total prescriptions count
        total_prescriptions = WalkInPrescription.objects.count()
        
        # Verified prescriptions count
        verified_count = WalkInPrescription.objects.filter(verified='verified').count()
        
        # Issued prescriptions count
        issued_count = WalkInPrescription.objects.filter(issued='issued').count()
        
        # Paid prescriptions count
        paid_count = WalkInPrescription.objects.filter(status='Paid').count()
        
        # Total revenue
        total_revenue = WalkInPrescription.objects.aggregate(
            total=Sum('total_price')
        )['total'] or 0
        
        # Payment method distribution
        payment_methods = WalkInCustomer.objects.values('payment_form').annotate(
            count=Count('id'),
            total=Sum('walkinprescription__total_price')
        )
        
        return JsonResponse({
            'status': 'success',
            'data': {
                'total_prescriptions': total_prescriptions,
                'verified_count': verified_count,
                'issued_count': issued_count,
                'paid_count': paid_count,
                'total_revenue': float(total_revenue),
                'payment_methods': list(payment_methods)
            }
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@require_GET
def get_medicine_details(request):
    """
    Unified view to return all medicine details needed for prescription management
    """
    medicine_id = request.GET.get('medicine_id')
    
    if not medicine_id:
        return JsonResponse({'success': False, 'error': 'Medicine ID is required'})
    
    try:
        medicine = Medicine.objects.get(id=medicine_id)
        
        # Get payment method to determine the right price
        payment_method = request.GET.get('payment_method', 'cash')
        
        # Determine unit price based on payment method
        if payment_method == 'insurance':
            unit_price = medicine.insurance_cost
        elif payment_method == 'nhif':
            unit_price = medicine.nhif_cost
        else:  # cash, card, mobile_money, other
            unit_price = medicine.cash_cost
        
        response_data = {
            'success': True,
            'drug_name': medicine.drug_name,
            'formulation_unit': medicine.formulation_unit,
            'dividing_unit': medicine.dividing_unit,
            'is_dividable': medicine.is_dividable,
            'unit_price': float(unit_price) if unit_price else 0,
            'cash_cost': float(medicine.cash_cost) if medicine.cash_cost else 0,
            'insurance_cost': float(medicine.insurance_cost) if medicine.insurance_cost else 0,
            'nhif_cost': float(medicine.nhif_cost) if medicine.nhif_cost else 0,
            'remain_quantity': medicine.remain_quantity,
        }
        
        return JsonResponse(response_data)
        
    except Medicine.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Medicine not found'})


@login_required
def medicine_counts_api(request):
    """API endpoint for medicine counts"""
    today = now().date()
    ten_days_from_now = today + timedelta(days=10)
    
    out_of_stock_count = Medicine.objects.filter(remain_quantity=0).count()
    total_quantity = Medicine.objects.filter(remain_quantity__gt=0).aggregate(
        total=Sum('remain_quantity')
    )['total'] or 0
    expiring_soon_count = Medicine.objects.filter(
        expiration_date__range=[today, ten_days_from_now]
    ).count()
    expired_count = Medicine.objects.filter(expiration_date__lt=today).count()

    return JsonResponse({
        'out_of_stock': out_of_stock_count,
        'total_quantity': total_quantity,
        'expiring_soon': expiring_soon_count,
        'expired': expired_count,
    })



@login_required
def pharmacy_stock_data(request):
    """API endpoint for pharmacy stock data visualization"""
    # Get top 10 medicines by stock level
    medicines = Medicine.objects.order_by('-remain_quantity')[:10]
    
    data = {
        'labels': [med.drug_name for med in medicines],
        'stockLevels': [med.remain_quantity for med in medicines],
        'colors': [
            'rgba(52, 152, 219, 0.8)',  # Blue
            'rgba(46, 204, 113, 0.8)',  # Green
            'rgba(155, 89, 182, 0.8)',  # Purple
            'rgba(241, 196, 15, 0.8)',  # Yellow
            'rgba(230, 126, 34, 0.8)',  # Orange
            'rgba(231, 76, 60, 0.8)',   # Red
            'rgba(149, 165, 166, 0.8)', # Gray
            'rgba(26, 188, 156, 0.8)',  # Turquoise
            'rgba(52, 73, 94, 0.8)',    # Dark blue
            'rgba(243, 156, 18, 0.8)',  # Dark yellow
        ]
    }
    
    return JsonResponse(data)


@login_required
def pharmacy_prescription_status_data(request):
    """API endpoint for prescription status data visualization"""
    # Get prescription status counts
    verified_count = Prescription.objects.filter(verified='verified').count()
    not_verified_count = Prescription.objects.filter(verified='Not Verified').count()
    issued_count = Prescription.objects.filter(issued='issued').count()
    not_issued_count = Prescription.objects.filter(issued='Not Issued').count()
    
    data = {
        'labels': ['Verified', 'Not Verified', 'Issued', 'Not Issued'],
        'data': [verified_count, not_verified_count, issued_count, not_issued_count],
        'colors': [
            'rgba(46, 204, 113, 0.8)',  # Green for verified
            'rgba(231, 76, 60, 0.8)',   # Red for not verified
            'rgba(52, 152, 219, 0.8)',  # Blue for issued
            'rgba(241, 196, 15, 0.8)',  # Yellow for not issued
        ]
    }
    
    return JsonResponse(data)


# ==================== DASHBOARD & MAIN VIEWS ====================
@login_required
def pharmacist_dashboard(request):
    """Pharmacist dashboard view"""
    today, ten_days_from_now = get_today_and_ten_days()
    
    # Get recent visits with prescriptions
    recent_visits = get_recent_visits_with_prescriptions(limit=5)
    recent_visits = attach_prescriptions_to_visits(recent_visits)
    
    # Get recent walk-in visits with prescriptions
    recent_walkin_visits = get_recent_walkin_visits_with_prescriptions(limit=5)
    recent_walkin_visits = attach_walkin_prescriptions_to_visits(recent_walkin_visits)
    
    # Get low stock medicines
    low_stock_medicines = get_low_stock_medicines(threshold=20, limit=10)
    
    # Get expiring soon medicines
    expiring_soon_medicines = get_expiring_soon_medicines(days=10, limit=10)
    
    # Get expired medicines
    expired_medicines = Medicine.objects.filter(expiration_date__lt=today)
    
    # Add additional context for each medicine
    for medicine in low_stock_medicines:
        medicine.remain_quantity_percentage = round(
            (medicine.remain_quantity / medicine.quantity) * 100, 1
        )
        medicine.is_expired = medicine.expiration_date < today
        medicine.expiring_soon = today <= medicine.expiration_date <= ten_days_from_now
    
    for medicine in expiring_soon_medicines:
        medicine.remain_quantity_percentage = round(
            (medicine.remain_quantity / medicine.quantity) * 100, 1
        )
        medicine.is_expired = medicine.expiration_date < today
        medicine.expiring_soon = today <= medicine.expiration_date <= ten_days_from_now
        medicine.days_until_expiry = (medicine.expiration_date - today).days
    
    context = {
        'total_patients_count': Patients.objects.count(),
        'total_medicines_count': Medicine.objects.count(),
        'total_prescriptions_count': Prescription.objects.count() + WalkInPrescription.objects.count(),
        'out_of_stock_count': Medicine.objects.filter(remain_quantity=0).count(),
        'daily_dispensed_count': Prescription.objects.filter(
            updated_at__date=today, 
            issued='issued'
        ).count() + WalkInPrescription.objects.filter(
            updated_at__date=today, 
            issued='issued'
        ).count(),
        'expired_medicines_count': expired_medicines.count(),
        'expiring_soon_count': expiring_soon_medicines.count(),
        'total_quantity': Medicine.objects.aggregate(total=Sum('remain_quantity'))['total'] or 0,
        'recent_visits': recent_visits,
        'recent_walkin_visits': recent_walkin_visits,
        'low_stock_medicines': low_stock_medicines,
        'expiring_soon_medicines': expiring_soon_medicines,
        'expired_medicines': expired_medicines,
    }

    return render(request, "pharmacist_template/home_content.html", context)


@login_required
@require_GET
def pharmacist_dashboard_counts(request):
    """Return counts for medicines and prescriptions in a single response"""
    try:
        today = timezone.now().date()
        
        # Medicine counts
        medicines = Medicine.objects.all()
        total_medicines = medicines.count()
        out_of_stock_medicines = medicines.filter(remain_quantity=0).count()
        low_stock_medicines = medicines.filter(remain_quantity__lte=5).count()
        expiring_soon_medicines = medicines.filter(
            expiration_date__range=(today, today + timedelta(days=30))
        ).count()
        expired_medicines = medicines.filter(expiration_date__lt=today).count()
        
        # Prescription counts
        prescriptions = Prescription.objects.all()
        walkin_prescriptions = WalkInPrescription.objects.all()
        
        # All prescriptions (both regular and walk-in)
        all_prescriptions_count = prescriptions.count() + walkin_prescriptions.count()
        
        # Today's prescriptions
        today_prescriptions = prescriptions.filter(created_at__date=today).count()
        today_walkin_prescriptions = walkin_prescriptions.filter(created_at__date=today).count()
        today_total_prescriptions = today_prescriptions + today_walkin_prescriptions
        
        # Pending prescriptions (not verified)
        pending_prescriptions = prescriptions.filter(verified='not_verified').count()
        pending_walkin_prescriptions = walkin_prescriptions.filter(verified='not_verified').count()
        total_pending_prescriptions = pending_prescriptions + pending_walkin_prescriptions
        
        # Unissued prescriptions
        unissued_prescriptions = prescriptions.filter(issued='not_issued').count()
        unissued_walkin_prescriptions = walkin_prescriptions.filter(issued='not_issued').count()
        total_unissued_prescriptions = unissued_prescriptions + unissued_walkin_prescriptions
        
        data = {
            "medicines": {
                "total": total_medicines,
                "out_of_stock": out_of_stock_medicines,
                "low_stock": low_stock_medicines,
                "expiring_soon": expiring_soon_medicines,
                "expired": expired_medicines
            },
            "prescriptions": {
                "all": all_prescriptions_count,
                "today": today_total_prescriptions,
                "pending": total_pending_prescriptions,
                "unissued": total_unissued_prescriptions,
                "walkin": walkin_prescriptions.count()
            },
            "status": "success",
            "timestamp": timezone.now().isoformat()
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e),
            "medicines": {
                "total": 0,
                "out_of_stock": 0,
                "low_stock": 0,
                "expiring_soon": 0,
                "expired": 0
            },
            "prescriptions": {
                "all": 0,
                "today": 0,
                "pending": 0,
                "unissued": 0,
                "walkin": 0
            },
            "timestamp": timezone.now().isoformat()
        }, status=500)





@login_required
def today_dispensed(request):
    """View for medicines dispensed today"""
    today = timezone.now().date()
    dispensed_today = Prescription.objects.filter(
        updated_at__date=today, 
        issued='issued'
    ).select_related('patient', 'medicine')
    
    context = {
        'dispensed_today': dispensed_today,
        'page_title': 'Medicines Dispensed Today'
    }
    
    return render(request, "pharmacist_template/today_dispensed.html", context)


@login_required
def low_stock_medicines(request):
    """View for low stock medicines"""
    low_stock_medicines = get_low_stock_medicines(threshold=20)
    
    context = {
        'low_stock_medicines': low_stock_medicines,
        'page_title': 'Low Stock Medicines'
    }
    
    return render(request, "pharmacist_template/low_stock_medicines.html", context)


@login_required
def manage_patient(request):
    """View for managing patients"""
    patients = Patients.objects.all().order_by('-created_at')
    
    context = {
        'patients': patients,
        'page_title': 'Manage Patients'
    }
    
    return render(request, "pharmacist_template/manage_patient.html", context)


@login_required
def expired_medicines(request):
    """View for expired medicines"""
    today = timezone.now().date()
    expired_medicines = Medicine.objects.filter(expiration_date__lt=today)
    
    context = {
        'expired_medicines': expired_medicines,
        'page_title': 'Expired Medicines'
    }
    
    return render(request, "pharmacist_template/expired_medicines.html", context)


@login_required
def expiring_soon_medicines(request):
    """View for medicines expiring soon"""
    today = timezone.now().date()
    ten_days_from_now = today + timedelta(days=10)
    expiring_soon = Medicine.objects.filter(
        expiration_date__range=[today, ten_days_from_now]
    )
    
    context = {
        'expiring_soon_medicines': expiring_soon,
        'page_title': 'Medicines Expiring Soon'
    }
    
    return render(request, "pharmacist_template/expiring_soon_medicines.html", context)


@login_required
def pharmacist_profile(request):
    """View for pharmacist profile"""
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
    """View for changing password"""
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
    """View for editing staff profile"""
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
    """View for prescription list"""
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

    # Step 2: Attach related prescriptions to each grouped visit and get status
    visit_list = []
    for visit in grouped_visits:
        visit_id = visit['visit__id']
        visit_instance = PatientVisits.objects.get(id=visit_id)
        
        # Get the status using the model method
        status = Prescription.get_visit_status(visit_instance)
        
        # Get all prescriptions for this visit
        prescriptions = Prescription.objects.filter(visit_id=visit_id).select_related('medicine', 'frequency')
        
        # Create a new dictionary with all the data
        visit_data = {
            **visit,
            'prescriptions': prescriptions,
            'verified_status': status['verified'],
            'issued_status': status['issued'],
            'payment_status': status['status']
        }
        
        visit_list.append(visit_data)

    return render(request, 'pharmacist_template/manage_prescription_list.html', {
        'visit_total_prices': visit_list,
    })

@login_required
def todays_prescriptions(request):
    """View for prescription list"""
    today = now().date()
    # Step 1: Fetch prescriptions grouped by visit
    grouped_visits = (
        Prescription.objects.filter(visit__created_at__date=today)
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

    # Step 2: Attach related prescriptions to each grouped visit and get status
    visit_list = []
    for visit in grouped_visits:
        visit_id = visit['visit__id']
        visit_instance = PatientVisits.objects.get(id=visit_id)
        
        # Get the status using the model method
        status = Prescription.get_visit_status(visit_instance)
        
        # Get all prescriptions for this visit
        prescriptions = Prescription.objects.filter(visit_id=visit_id).select_related('medicine', 'frequency')
        
        # Create a new dictionary with all the data
        visit_data = {
            **visit,
            'prescriptions': prescriptions,
            'verified_status': status['verified'],
            'issued_status': status['issued'],
            'payment_status': status['status']
        }
        
        visit_list.append(visit_data)

    return render(request, 'pharmacist_template/todays_prescription_list.html', {
        'visit_total_prices': visit_list,
    })




@login_required
def medicine_list(request):
    """View for medicine list"""
    # Retrieve medicines and check for expired ones
    medicines = Medicine.objects.all()
    # Render the template with medicine data and notifications
    return render(request, 'pharmacist_template/manage_medicine.html', {'medicines': medicines})   





@login_required
def medicine_expired_list(request):
    """View for expired medicines list"""
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
    """View for in-stock medicines"""
    # Retrieve medicines with inventory levels above zero
    in_stock_medicines = Medicine.objects.filter(remain_quantity__gt=0)

    return render(request, 'pharmacist_template/manage_in_stock_medicines.html', {'in_stock_medicines': in_stock_medicines})  


@login_required
def out_of_stock_medicines_view(request):
    out_of_stock_medicines = Medicine.objects.filter(remain_quantity=0)

    # Annotate each inventory with how long it's been out of stock
    today = datetime.now(timezone.utc)
    medicines_with_status = []
    for inv in out_of_stock_medicines:
        days_out = (today - inv.updated_at).days if inv.updated_at else None
        status = "recent" if days_out is not None and days_out <= 7 else "older"
        medicines_with_status.append({
            "inventory": inv,
            "days_out": days_out,
            "status": status,
        })

    return render(
        request,
        "pharmacist_template/manage_out_of_stock_medicines.html",
        {"medicines_with_status": medicines_with_status}
    )
    

@login_required
def visit_list(request):
    """View for visit list"""
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
    """View for saving prescription"""
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
        range_31 = range(1,31)
        return render(request, 'pharmacist_template/prescription_template.html', {
            'patient': patient,
            'visit': visit,        
            'medicines': medicines,          
            'frequencies': frequencies,
            'range_31': range_31,
        })

    except Exception as e:
        return render(request, '404.html', {
            'error_message': f"Oop's sorry we can't find that page! ({str(e)})"
        })

@login_required
def add_non_registered_prescription(request):
    """View for adding prescription for non-registered patients"""
    try:
        frequencies = PrescriptionFrequency.objects.all()
        routes = MedicineRoute.objects.all()    
        medicines = Medicine.objects.all()
        range_31 = range(1,31)
        
        return render(request, 'pharmacist_template/non_registered_prescription.html', {
            'medicines': medicines,          
            'frequencies': frequencies,
            'routes': routes,
            'range_31': range_31,
        })

    except Exception as e:
        return render(request, '404.html', {
            'error_message': f"An error occurred: {str(e)}"
        })


@login_required
def employee_detail(request):
    """View for employee details"""
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