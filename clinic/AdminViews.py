import calendar
from datetime import  datetime
from django.utils import timezone
import logging
from django.shortcuts import get_object_or_404, redirect, render
from django.http import   HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django.db.models import F
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.mail import send_mail
from clinic.models import Consultation,  CustomUser, DiseaseRecode, InsuranceCompany, Medicine, MedicineInventory, Notification, PathodologyRecord, Patients, Procedure, Staffs

from django.views.decorators.http import require_POST
from django.db.models import OuterRef, Subquery
from .models import AmbulanceActivity, AmbulanceOrder, AmbulanceRoute, AmbulanceVehicleOrder, Category, Company,  ConsultationNotes, ConsultationOrder,  Diagnosis,  Diagnosis, Equipment, EquipmentMaintenance,  HospitalVehicle, ImagingRecord, InventoryItem, LaboratoryOrder,  MedicineRoute, MedicineUnitMeasure, Order, PatientVisits, PatientVital, Prescription, PrescriptionFrequency, Procedure, Patients, QualityControl, Reagent, ReagentUsage, Referral,  Service, Supplier, UsageHistory
from django.db.models import Sum
from django.core.exceptions import ObjectDoesNotExist, ValidationError


@login_required
def dashboard(request):
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
    return render(request, "hod_template/home_content.html", context)

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
def manage_patient(request):
    patient_records=Patients.objects.all().order_by('-created_at')   
    return render(request,"hod_template/manage_patients.html", {
        "patient_records":patient_records,     
        })
    



@login_required
def manage_company(request):
    companies=Company.objects.all() 
    return render(request,"hod_template/manage_company.html",{"companies":companies})

@login_required
def manage_disease(request):
    disease_records=DiseaseRecode.objects.all() 
    return render(request,"hod_template/manage_disease.html",{"disease_records":disease_records})

@login_required
def manage_staff(request):     
    staffs=Staffs.objects.all()  
    return render(request,"hod_template/manage_staff.html",{"staffs":staffs})  

@login_required
def manage_insurance(request):
    insurance_companies=InsuranceCompany.objects.all() 
    return render(request,"hod_template/manage_insurance.html",{"insurance_companies":insurance_companies})

@login_required
def resa_report(request):
    return render(request,"hod_template/resa_reports.html")

@login_required
def manage_service(request):
    services=Service.objects.all()
    insurance_companies=InsuranceCompany.objects.all()
    context = {
        'services':services,
        'insurance_companies':insurance_companies,
    }
    return render(request,"hod_template/manage_service.html",context)


@login_required
def reports_adjustments(request):
    return render(request,"hod_template/reports_adjustments.html")

@login_required
def reports_by_visit(request):
    return render(request,"hod_template/reports_by_visit.html")

@login_required
def reports_comprehensive(request):
    return render(request,"hod_template/reports_comprehensive.html")

@login_required
def reports_patients_visit_summary(request):
    return render(request,"hod_template/reports_patients_visit_summary.html")

@login_required
def reports_patients(request):
    return render(request,"hod_template/reports_patients.html")

@login_required
def reports_service(request):
    return render(request,"hod_template/reports_service.html")

@login_required
def reports_stock_ledger(request):
    return render(request,"hod_template/reports_stock_ledger.html")

def reports_stock_level(request):
    return render(request,"hod_template/reports_stock_level.html")

@login_required
def reports_orders(request):
    return render(request,"hod_template/reports_orders.html")

@login_required
def individual_visit(request):
    return render(request,"hod_template/reports_individual_visit.html")

@login_required
def product_summary(request):
    return render(request,"hod_template/product_summary.html")

@login_required
def manage_pathodology(request):
    pathodology_records=PathodologyRecord.objects.all()    
    return render(request,"hod_template/manage_pathodology.html",{
        "pathodology_records":pathodology_records,        
        })


logger = logging.getLogger(__name__)

@csrf_exempt
@login_required
def save_staff_view(request):
    if request.method == 'POST':
        try:
            # Retrieve form data from the POST request
            first_name = request.POST.get('firstName')
            middle_name = request.POST.get('middleName')
            lastname = request.POST.get('lastname') 
            first_name = first_name.capitalize() if first_name else None
            middle_name = middle_name.capitalize() if middle_name else None
            last_name = lastname.capitalize() if lastname else None           
            gender = request.POST.get('gender')
            dob = request.POST.get('dob')
            phone = request.POST.get('phone')
            profession = request.POST.get('profession')            
            marital_status = request.POST.get('maritalStatus')
            email = request.POST.get('email')
            password = request.POST.get('password')            
            user_role = request.POST.get('userRole')
            Workingplace = request.POST.get('Workingplace')
            joiningDate = request.POST.get('joiningDate')

            # Create a new CustomUser instance (if not exists) and link it to Staffs
            user = CustomUser.objects.create_user(username=email, password=password, email=email, first_name=first_name, last_name=last_name, user_type=2)

            # Create a new Staffs instance and link it to the user
            
            user.staff.middle_name = middle_name
            user.staff.date_of_birth = dob
            user.staff.gender = gender            
            user.staff.phone_number = phone            
            user.staff.marital_status = marital_status
            user.staff.profession = profession
            user.staff.role = user_role
            user.staff.work_place = Workingplace
            user.staff.joining_date = joiningDate
        
            # Save the staff record
            user.save()

            # For demonstration purposes, you can log the saved data
            logger.info(f'Data saved successfully: {user.staff.__dict__}')

            # Return a success response to the user
            return JsonResponse({'message': 'Data saved successfully'}, status=200)
        except Exception as e:
            # Handle exceptions and log the error
            logger.error(f'Error saving data: {str(e)}')
            return JsonResponse({'error': str(e)}, status=400)

    # Return an error response if the request is not POST
    return JsonResponse({'error': 'Invalid request method'}, status=405)
 
@login_required
def update_staff_status(request):
    try:
        if request.method == 'POST':
            # Get the user_id and is_active values from POST data
            user_id = request.POST.get('user_id')
            is_active = request.POST.get('is_active')

            # Retrieve the staff object or return a 404 response if not found
            staff = get_object_or_404(CustomUser, id=user_id)

            # Toggle the is_active status based on the received value
            if is_active == '1':
                staff.is_active = False
                messages.success(request, f'{staff.username} has been deactivated.')
            elif is_active == '0':
                staff.is_active = True
                messages.success(request, f'{staff.username} has been activated.')

                # Send activation email to the user
                login_url = request.build_absolute_uri(reverse('clinic:login'))
                email_content = (
                    f"Dear {staff.first_name} {staff.last_name},\n\n"
                    f"MRISHO HAMISI is pleased to inform you that your account has been activated successfully. "
                    f"You can now log in to your account using the following link:\n\n"
                    f"{login_url}\n\n"
                    f"Your login details are as follows:\n"
                    f"Email: {staff.email}\n"
                    f"Password: {staff.password}\n\n"  # Note: This assumes that the password is stored in plaintext, which is not recommended
                    f"If you have any questions or need further assistance, please do not hesitate to contact the administrator.\n\n"
                    f"Best regards,\n"
                    f"RESA Team"
                )
                send_mail(
                    'Account Activation Notice',
                    email_content,
                    'admin@example.com',
                    [staff.email],
                    fail_silently=False,
                )
            else:
                messages.error(request, 'Invalid request')
                return redirect('admin_manage_staff')  

            staff.save()
        else:
            messages.error(request, 'Invalid request method')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')

    # Redirect back to the staff list page
    return redirect('admin_manage_staff') 


@login_required
def update_vehicle_status(request):
    try:
        if request.method == 'POST':
            # Get the user_id and is_active values from POST data
            vehicle_id = request.POST.get('vehicle_id')
            is_active = request.POST.get('is_active')

            # Retrieve the staff object or return a 404 response if not found
            vehicle = get_object_or_404(HospitalVehicle, id=vehicle_id)

            # Toggle the is_active status based on the received value
            if is_active == '1':
                vehicle.is_active = False
            elif is_active == '0':
                vehicle.is_active = True
            else:
                messages.error(request, 'Invalid request')
                return redirect('clinic:hospital_vehicle_list')  # Make sure 'hospital_vehicle_lists' is the name of your staff list URL

            vehicle.save()
            messages.success(request, 'Status updated successfully')
        else:
            messages.error(request, 'Invalid request method')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
    # Redirect back to the staff list page
    return redirect('clinic:hospital_vehicle_list')  # Make sure 'hospital_vehicle_lists' is the name of your staff list URL

@login_required
def update_equipment_status(request):
    try:
        if request.method == 'POST':
            # Get the user_id and is_active values from POST data
            equipment_id = request.POST.get('equipment_id')
            is_active = request.POST.get('is_active')

            # Retrieve the staff object or return a 404 response if not found
            equipment = get_object_or_404(Equipment, id=equipment_id)

            # Toggle the is_active status based on the received value
            if is_active == '1':
                equipment.is_active = False
            elif is_active == '0':
                equipment.is_active = True
            else:
                messages.error(request, 'Invalid request')
                return redirect('admin_equipment_list')  

            equipment.save()
            messages.success(request, 'equipment updated successfully')
        else:
            messages.error(request, 'Invalid request method')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')

    # Redirect back to the staff list page
    return redirect('admin_equipment_list') 

@login_required
def edit_staff(request, staff_id):
    # Check if the staff with the given ID exists, or return a 404 page
    staff = get_object_or_404(Staffs, id=staff_id)  
    # If staff exists, proceed with the rest of the view
    request.session['staff_id'] = staff_id
    return render(request, "update/edit_staff.html", {"id": staff_id, "username": staff.admin.username, "staff": staff})   


@login_required
def edit_staff_save(request):
    if request.method == "POST":
        try:
            # Retrieve the staff ID from the session
            staff_id = request.session.get('staff_id')
            if staff_id is None:
                messages.error(request, "Staff ID not found")
                return redirect("admin_manage_staff")

            # Retrieve the staff instance from the database
            try:
                staff = Staffs.objects.get(id=staff_id)
            except ObjectDoesNotExist:
                messages.error(request, "Staff not found")
                return redirect("admin_manage_staff")

            # Extract the form data
            first_name = request.POST.get('firstName')
            middle_name = request.POST.get('middleName')
            last_name = request.POST.get('lastname') 
            first_name = first_name.capitalize() if first_name else None
            middle_name = middle_name.capitalize() if middle_name else None
            last_name = last_name.capitalize() if last_name else None                  
            gender = request.POST.get('gender')
            dob = request.POST.get('date_of_birth')
            phone = request.POST.get('phone')
            profession = request.POST.get('profession')            
            marital_status = request.POST.get('maritalStatus')
            email = request.POST.get('email')                        
            user_role = request.POST.get('userRole')    
            joiningDate = request.POST.get('joiningDate')    
            Workingplace = request.POST.get('Workingplace')    
          

            # Save the staff details
   
            staff.admin.first_name = first_name
            staff.admin.last_name = last_name
            staff.admin.email = email
            staff.middle_name = middle_name
            staff.joining_date = joiningDate
            staff.work_place = Workingplace
            staff.role = user_role
            staff.profession = profession
            staff.marital_status = marital_status
            staff.date_of_birth = dob
            staff.phone_number = phone
            staff.gender = gender      
            staff.save()

            # Assuming the URL name for the next editing form is "qualification_form"
            messages.success(request, "Staff details updated successfully.")
            return redirect("admin_manage_staff")
        except Exception as e:
            messages.error(request, f"Error updating staff details: {str(e)}")

    return redirect("clinic:edit_staff",staff_id=staff_id)



@login_required
def single_staff_detail(request, staff_id):
    staff = get_object_or_404(Staffs, id=staff_id)
    # Fetch additional staff-related data  
    context = {
        'staff': staff,
     
    }

    return render(request, "hod_template/staff_details.html", context)

@login_required
def view_patient(request, patient_id):
    patient = get_object_or_404(Patients, id=patient_id)
    # Fetch additional staff-related data  
    context = {
        'patient': patient,
     
    }

    return render(request, "hod_template/patients_detail.html", context)



@login_required
def medicine_list(request):
    # Retrieve medicines and check for expired ones
    medicines = Medicine.objects.all()
    # Render the template with medicine data and notifications
    return render(request, 'hod_template/manage_medicine.html', {'medicines': medicines})


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



def medicine_expired_list(request):
    # Get all medicines
    all_medicines = Medicine.objects.all()

    # Filter medicines with less than or equal to 10 days remaining for expiration
    medicines = []
    for medicine in all_medicines:
        days_remaining = (medicine.expiration_date - timezone.now().date()).days
        if days_remaining <= 10:
            medicines.append({
                'name': medicine.name,
                'expiration_date': medicine.expiration_date,
                'days_remaining': days_remaining,
            })

    return render(request, 'hod_template/manage_medicine_expired.html', {'medicines': medicines})

@login_required
def patient_procedure_view(request):
    template_name = 'hod_template/manage_procedure.html'
    
    # Query to retrieve the latest procedure record for each patient
    procedures = Procedure.objects.filter(
        patient=OuterRef('id')
    ).order_by('-created_at')[:1]

    # Query to retrieve patients with their corresponding procedure (excluding patients without procedures)
    patients_with_procedures = Patients.objects.annotate(
        procedure_name=Subquery(procedures.values('name')[:1]),
        procedure_description=Subquery(procedures.values('description')[:1]),
        procedure_duration=Subquery(procedures.values('duration_time')[:1]),
        procedure_equipments=Subquery(procedures.values('equipments_used')[:1]),
        procedure_cost=Subquery(procedures.values('cost')[:1])
    ).filter(procedure_name__isnull=False)
    
    patients = Patients.objects.all()
    # Retrieve the data
    data = patients_with_procedures.values(
        'id', 'mrn', 'procedure_name', 'procedure_description',
        'procedure_duration', 'procedure_equipments', 'procedure_cost'
    )

    return render(request, template_name, {'data': data,'patients':patients})



@login_required
def patient_procedure_history_view(request, mrn):
    patient = get_object_or_404(Patients, mrn=mrn)    
    # Retrieve all procedures for the specific patient
    procedures = Procedure.objects.filter(patient=patient)    
    context = {
        'patient': patient,
        'procedures': procedures,
    }

    return render(request, 'hod_template/manage_patient_procedure.html', context)


@login_required
def manage_referral(request):
    referrals = Referral.objects.all()
    return render(request, 'hod_template/manage_referral.html', {'referrals': referrals})


@login_required
def generate_billing(request, procedure_id):
    procedure = get_object_or_404(Procedure, id=procedure_id)
    context = {
        'procedure': procedure,
    }

    return render(request, 'hod_template/billing_template.html', context)

@login_required
def appointment_list_view(request):
    appointments = Consultation.objects.all()
    unread_notification_count = Notification.objects.filter(is_read=False).count()
    patients=Patients.objects.all() 
    pathology_records=PathodologyRecord.objects.all() 
    doctors=Staffs.objects.filter(role='doctor',work_place = 'resa')
    context = {
        'patients':patients,
        'pathology_records':pathology_records,
        'doctors':doctors,
        'unread_notification_count':unread_notification_count,
        'appointments':appointments,
    }
    return render(request, 'hod_template/manage_appointment.html', context)



@csrf_exempt
@login_required
def add_disease(request):
    try:
        if request.method == 'POST':
            disease_name = request.POST.get('Disease')
            code = request.POST.get('Code')

            # Check if the disease already exists
            if DiseaseRecode.objects.filter(disease_name=disease_name).exists():
                return JsonResponse({'success': False, 'message': 'Disease already exists'})

            # Save data to the model
            DiseaseRecode.objects.create(disease_name=disease_name, code=code)

            return JsonResponse({'success': True,'message':'disease added successfully'})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid request method'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
 
@csrf_exempt
@login_required
def add_insurance_company(request):
    try:
        if request.method == 'POST':
            company_id = request.POST.get('company_id')
            name = request.POST.get('Name')
            phone = request.POST.get('Phone')
            short_name = request.POST.get('Short_name')
            email = request.POST.get('Email')
            address = request.POST.get('Address')
            website = request.POST.get('website')

            if company_id:
                # Edit existing company
                company = InsuranceCompany.objects.get(id=company_id)

                # Check for duplicates
                if InsuranceCompany.objects.filter(name=name).exclude(id=company_id).exists():
                    return JsonResponse({'success': False, 'message': 'Another company with this name already exists'})
                if InsuranceCompany.objects.filter(email=email).exclude(id=company_id).exists():
                    return JsonResponse({'success': False, 'message': 'Another company with this email already exists'})

                company.name = name
                company.phone = phone
                company.short_name = short_name
                company.email = email
                company.address = address
                company.website = website
                company.save()
                message = 'Successfully edited'
            else:
                # Check for duplicates
                if InsuranceCompany.objects.filter(name=name).exists():
                    return JsonResponse({'success': False, 'message': 'Company with this name already exists'})
                if InsuranceCompany.objects.filter(email=email).exists():
                    return JsonResponse({'success': False, 'message': 'Company with this email already exists'})

                # Create new company
                InsuranceCompany.objects.create(
                    name=name,
                    phone=phone,
                    short_name=short_name,
                    email=email,
                    address=address,
                    website=website,
                )
                message = 'Successfully added'

            return JsonResponse({'success': True, 'message': message})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid request method'})
    except InsuranceCompany.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Insurance company not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@csrf_exempt
@login_required
def add_pathodology_record(request):
    try:
        if request.method == 'POST':
            name = request.POST.get('Name')
            description = request.POST.get('Description')
            related_diseases_ids = request.POST.getlist('RelatedDiseases')

            # Save data to the model
            pathodology_record = PathodologyRecord.objects.create(
                name=name,
                description=description
            )

            # Add related diseases
            for disease_id in related_diseases_ids:
                disease = DiseaseRecode.objects.get(pk=disease_id)
                pathodology_record.related_diseases.add(disease)

            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid request method'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    

@login_required    
def save_service_data(request):
    if request.method == 'POST':
        service_id = request.POST.get('service_id')
        coverage = request.POST.get('covarage')        
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

            service.coverage = coverage           
            service.type_service = type_service
            service.name = name
            service.description = description
            service.cost = cost
            service.save()

            return redirect('clinic:manage_service')
        except Exception as e:
            return HttpResponseBadRequest(f"Error: {str(e)}") 

    # If the request is not a POST request, handle it accordingly
    return HttpResponseBadRequest("Invalid request method.")   

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'hod_template/manage_category_list.html', {'categories': categories})



@require_POST
def add_category(request):
    try:
        category_id = request.POST.get('category_id')
        name = request.POST.get('name')
        
        if not name:
            return JsonResponse({'success': False, 'message': 'Name field is required'})

        if category_id:
            try:
                # Editing an existing category
                category = Category.objects.get(pk=category_id)
                
                # Check for duplicates excluding the current category
                if Category.objects.filter(name=name).exclude(pk=category_id).exists():
                    return JsonResponse({'success': False, 'message': 'Category with this name already exists'})

                category.name = name
                category.save()
                message = 'Category successfully updated'
            except Category.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Category not found'})
        else:
            # Adding a new category
            if Category.objects.filter(name=name).exists():
                return JsonResponse({'success': False, 'message': 'Category with this name already exists'})
                
            category = Category(name=name)
            category.save()
            message = 'Category successfully added'

        return JsonResponse({'success': True, 'message': message})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required    
def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, 'hod_template/manage_supplier_list.html', {'suppliers': suppliers})

@login_required 
def inventory_list(request):
    inventory_items = InventoryItem.objects.all()  
    suppliers = Supplier.objects.all()
    categories = Category.objects.all()
    return render(request, 'hod_template/manage_inventory_list.html', {
        'inventory_items': inventory_items,
        'suppliers': suppliers,
        'categories': categories 
        }) 


@csrf_exempt
@require_POST
def add_supplier(request):
    try:
        supplier_id = request.POST.get('supplier_id')
        name = request.POST.get('name')
        address = request.POST.get('address', '')
        contact_information = request.POST.get('contact_information', '')
        email = request.POST.get('email', '')       
        if supplier_id:
            if Supplier.objects.filter(name=name).exclude(pk=supplier_id).exists():
                return JsonResponse({'success': False, 'message': 'Supplier with this name already exists.'})
            # Editing an existing supplier
            supplier = Supplier.objects.get(pk=supplier_id)
            supplier.name = name
            supplier.address = address
            supplier.contact_information = contact_information
            supplier.email = email
            supplier.save()
            message = 'Supplier updated successfully.'
        else:
            if Supplier.objects.filter(name=name).exists():
                return JsonResponse({'success': False, 'message': 'Supplier with this name already exists.'})
            supplier = Supplier(
                name=name,
                address=address,
                contact_information=contact_information,
                email=email,
            )
            supplier.save()
            message = 'Supplier added successfully.'

        return JsonResponse({'success': True, 'message': message})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
    

@require_POST
def add_inventory_item(request):
    try:
        inventory_id = request.POST.get('inventory_id')
        name = request.POST.get('name')
        supplier = request.POST.get('supplier')
        category = request.POST.get('category')
        quantity = int(request.POST.get('quantity'))
        description = request.POST.get('description')
        purchase_date = request.POST.get('purchase_date')
        purchase_price = request.POST.get('purchase_price')
        expiry_date = request.POST.get('expiry_date')
        min_stock_level = request.POST.get('min_stock_level')
        condition = request.POST.get('condition')
        location_in_storage = request.POST.get('location_in_storage')
        # Add more fields as needed

        if inventory_id:
            # Editing existing inventory item
            inventory_item = InventoryItem.objects.get(pk=inventory_id)
            inventory_item.name = name
            inventory_item.quantity = quantity
            inventory_item.remain_quantity = quantity
            inventory_item.category =  Category.objects.get(id=category)
            inventory_item.description = description
            inventory_item.supplier =  Supplier.objects.get(id=supplier)
            inventory_item.purchase_date = purchase_date
            inventory_item.purchase_price = purchase_price
            inventory_item.location_in_storage = location_in_storage
            inventory_item.min_stock_level = min_stock_level
            inventory_item.expiry_date = expiry_date
            inventory_item.condition = condition
            inventory_item.save()
        else:
            # Adding new inventory item
            inventory_item = InventoryItem(
                name=name,
                quantity=quantity,
                remain_quantity=quantity,
                category = Category.objects.get(id=category),
                description = description,
                supplier = Supplier.objects.get(id=supplier),
                purchase_date = purchase_date,
                purchase_price = purchase_price,
                location_in_storage = location_in_storage,
                min_stock_level = min_stock_level,
                expiry_date = expiry_date,
                condition = condition,
               
            )
            inventory_item.save()

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})      
    

@login_required
def usage_history_list(request):
    usage_history_list = UsageHistory.objects.filter(quantity_used__gt=0)
    inventory_item = InventoryItem.objects.all()
    return render(request, 'hod_template/manage_usage_history_list.html', {
        'usage_history_list': usage_history_list,
        'inventory_item': inventory_item,
        })    

@require_POST
def save_usage_history(request):
    try:
        # Extract data from the request
        usage_history_id = request.POST.get('usageHistoryId')
        usage_date = request.POST.get('usageDate')
        quantity_used = int(request.POST.get('quantityUsed'))
        notes = request.POST.get('notes')
        item_id = request.POST.get('item')

        # Retrieve the corresponding InventoryItem
        item = InventoryItem.objects.get(id=item_id)
        if quantity_used > item.remain_quantity:
            return JsonResponse({'status': 'error', 'message': 'Quantity used exceeds available stock quantity'})


        # Check if the usageHistoryId is provided for editing
        if usage_history_id:
            # Editing existing usage history
            usage_history = UsageHistory.objects.get(pk=usage_history_id)
            # Get the previous quantity used
            previous_quantity_used = usage_history.quantity_used
            # Calculate the difference in quantity
            quantity_difference = quantity_used - previous_quantity_used
            # Update the stock level of the corresponding item
            item.remain_quantity -= quantity_difference
        else:
            # Creating new usage history
            usage_history = UsageHistory()
         

        # Update or set values for other fields
        usage_history.usage_date = usage_date
        usage_history.quantity_used = quantity_used
        usage_history.notes = notes
        usage_history.inventory_item = item

        # Save the changes to both models
        item.save()
        usage_history.save()

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@csrf_exempt
def get_item_quantity(request):
    if request.method == 'POST':
        item_id = request.POST.get('itemId')  # Use request.POST.get() instead of request.GET.get()
        print(item_id)      
        try:
            item = InventoryItem.objects.get(id=item_id)
            quantity = item.quantity
            print(quantity)
            return JsonResponse({'quantity': quantity})
        except InventoryItem.DoesNotExist:
            return JsonResponse({'error': 'Item not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
@login_required
def out_of_stock_items(request):
    out_of_stock_items = InventoryItem.objects.filter(remain_quantity=0)
    return render(request, 'hod_template/manage_out_of_stock_items.html', {'out_of_stock_items': out_of_stock_items}) 

@login_required
def in_stock_items(request):
    in_stock_items = InventoryItem.objects.filter(remain_quantity__gt=0)
    return render(request, 'hod_template/manage_in_stock_items.html', {'in_stock_items': in_stock_items})   

def get_out_of_stock_count(request):
    count = InventoryItem.objects.filter(remain_quantity=0).count()
    
    return JsonResponse({'count': count})

def get_out_of_stock_count_reagent(request):
    count = Reagent.objects.filter(remaining_quantity=0).count()
    
    return JsonResponse({'count': count})

def get_items_below_min_stock(request):
    items_below_min_stock = InventoryItem.objects.filter(remain_quantity__lt=F('min_stock_level')).count()
    return JsonResponse({'count': items_below_min_stock})

@csrf_exempt
def increase_inventory_stock(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        quantity_to_add = int(request.POST.get('quantityToAdd'))
        try:
            item = InventoryItem.objects.get(id=item_id)
            item.quantity += quantity_to_add
            item.remain_quantity += quantity_to_add
            item.save()
            return JsonResponse({'status': 'success', 'message': f'Stock level increased by {quantity_to_add} for item {item.name}'})
        except InventoryItem.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Item not found'}, status=404)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
    
@csrf_exempt
def increase_reagent_stock(request):
    if request.method == 'POST':
        reagent_id = request.POST.get('reagent_id')
        quantity_to_add = int(request.POST.get('quantityToAdd'))
        try:
            reagent = Reagent.objects.get(id=reagent_id)
            reagent.quantity_in_stock += quantity_to_add
            reagent.remaining_quantity += quantity_to_add
            reagent.save()
            return JsonResponse({'status': 'success', 'message': f'Stock level increased by {quantity_to_add} for item {reagent.name}'})
        except InventoryItem.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Item not found'}, status=404)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@csrf_exempt    
def use_inventory_item(request):
    if request.method == 'POST':
        item_id = request.POST.get('itemId')
        notes = request.POST.get('notes')
        quantity_used = int(request.POST.get('quantityUsed'))
        usage_date = request.POST.get('usageDate')

        try:
            item = InventoryItem.objects.get(id=item_id)
            if quantity_used > item.remain_quantity:
                return JsonResponse({'status': 'error', 'message': 'Quantity used exceeds available stock quantity'})

            # Create a new usage history entry
            UsageHistory.objects.create(
                inventory_item=item,
                quantity_used=quantity_used,
                notes=notes,
                usage_date=usage_date
            )

            item.remain_quantity -= quantity_used
            item.save()

            message = f'Stock level decreased by {quantity_used} for item {item.name}'
            return JsonResponse({'status': 'success', 'message': message})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'})
    
def out_of_stock_medicines(request):
    try:
        # Query the database for the count of out-of-stock medicines
        out_of_stock_count = MedicineInventory.objects.filter(remain_quantity=0).count()
        
        # Return the count in JSON format
        return JsonResponse({'count': out_of_stock_count})
    
    except Exception as e:
        # Handle any errors and return an error response
        return JsonResponse({'error': str(e)}, status=500)    

@login_required    
def out_of_stock_medicines_view(request):
    try:
        # Query the database for out-of-stock medicines
        out_of_stock_medicines = Medicine.objects.filter(remain_quantity=0)
        
        # Render the template with the out-of-stock medicines data
        return render(request, 'hod_template/manage_out_of_stock_medicines.html', {'out_of_stock_medicines': out_of_stock_medicines})    
    except Exception as e:
        # Handle any errors and return an error response
        return render(request, '404.html', {'error_message': str(e)}) 

@login_required    
def out_of_stock_reagent_view(request):
    try:
        # Query the database for out-of-stock medicines
        out_of_stock_reagent = Reagent.objects.filter(remaining_quantity=0)
        
        # Render the template with the out-of-stock medicines data
        return render(request, 'hod_template/manage_out_of_stock_reagent.html', {'out_of_stock_reagent': out_of_stock_reagent})
    
    except Exception as e:
        # Handle any errors and return an error response
        return render(request, '404.html', {'error_message': str(e)}) 
    
@login_required    
def in_stock_medicines_view(request):
    # Retrieve medicines with inventory levels above zero
    in_stock_medicines = Medicine.objects.filter(remain_quantity__gt=0)

    return render(request, 'hod_template/manage_in_stock_medicines.html', {'in_stock_medicines': in_stock_medicines})  

@login_required
def in_stock_reagent_view(request):
    # Retrieve medicines with inventory levels above zero
    in_stock_reagent = Reagent.objects.filter(remaining_quantity__gt=0)

    return render(request, 'hod_template/manage_in_stock_reagent.html', {'in_stock_reagent': in_stock_reagent})  

@login_required
def equipment_list(request):
    equipment_list = Equipment.objects.all()
    return render(request, 'hod_template/manage_equipment_list.html', {'equipment_list': equipment_list})  

 
@csrf_exempt     
@require_POST
def add_equipment(request):
    try:
        equipment_id = request.POST.get('equipment_id')
        Manufacturer = request.POST.get('Manufacturer')
        SerialNumber = request.POST.get('SerialNumber')
        AcquisitionDate = request.POST.get('AcquisitionDate')
        warrantyExpiryDate = request.POST.get('warrantyExpiryDate')
        Location = request.POST.get('Location')
        description = request.POST.get('description')
        Name = request.POST.get('Name')
      
        # Add more fields as needed

        if equipment_id:
            # Editing existing inventory item
            equipment = Equipment.objects.get(pk=equipment_id)
            equipment.manufacturer = Manufacturer
            equipment.serial_number = SerialNumber
            equipment.acquisition_date = AcquisitionDate
            equipment.warranty_expiry_date =  warrantyExpiryDate
            equipment.description = description
            equipment.location = Location
            equipment.name = Name        
            equipment.save()
        else:
            # Adding new inventory item
            equipment = Equipment(
                name=Name,
                manufacturer=Manufacturer,
                serial_number=SerialNumber,
                acquisition_date = AcquisitionDate,
                description = description,
                warranty_expiry_date = warrantyExpiryDate,
                location = Location,             
               
            )
            equipment.save()

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})  
    
@login_required    
def equipment_maintenance_list(request):
    maintenance_list = EquipmentMaintenance.objects.all()
    equipments = Equipment.objects.all()
    return render(request, 'hod_template/manage_equipment_maintenance_list.html',
                  {
                      'maintenance_list': maintenance_list,
                      'equipments': equipments,
                   })    

@csrf_exempt     
@require_POST
def add_maintainance(request):
    try:
        maintenance_id = request.POST.get('maintenance_id')
        equipment = request.POST.get('equipment')
        maintenance_date = request.POST.get('maintenance_date')
        technician = request.POST.get('technician')
        description = request.POST.get('description')
        cost = request.POST.get('cost')
        notes = request.POST.get('notes')
      
      
        # Add more fields as needed

        if maintenance_id:
            # Editing existing inventory item
            maintainance = EquipmentMaintenance.objects.get(pk=maintenance_id)
            maintainance.equipment = Equipment.objects.get(id=equipment)
            maintainance.maintenance_date = maintenance_date
            maintainance.technician = technician
            maintainance.description =  description
            maintainance.cost = cost
            maintainance.notes = notes                    
            maintainance.save()
        else:
            # Adding new inventory item
            maintainance = EquipmentMaintenance(
                equipment= Equipment.objects.get(id=equipment),
                maintenance_date=maintenance_date,
                technician=technician,
                description = description,
                cost = cost,
                notes = notes,
                          
               
            )
            maintainance.save()

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})  

@login_required 
def reagent_list(request):
    reagent_list = Reagent.objects.all()
    return render(request, 'hod_template/manage_reagent_list.html', {'reagent_list': reagent_list})    

@csrf_exempt     
@require_POST
def add_reagent(request):
    try:
        reagent_id = request.POST.get('reagent_id')
        name = request.POST.get('name')
        expiration_date = request.POST.get('expiration_date')
        manufacturer = request.POST.get('manufacturer')
        lot_number = request.POST.get('lot_number')
        storage_conditions = request.POST.get('storage_conditions')
        quantity_in_stock = int(request.POST.get('quantity_in_stock'))
        price_per_unit = float(request.POST.get('price_per_unit'))
      
      
        # Add more fields as needed

        if reagent_id:
            # Editing existing inventory item
            reagent = Reagent.objects.get(pk=reagent_id)
            reagent.name = name
            reagent.expiration_date = expiration_date
            reagent.manufacturer = manufacturer
            reagent.lot_number =  lot_number
            reagent.storage_conditions = storage_conditions
            reagent.quantity_in_stock = quantity_in_stock                    
            reagent.price_per_unit = price_per_unit                    
            reagent.remaining_quantity = quantity_in_stock                    
            reagent.save()
        else:
            # Adding new inventory item
            reagent = Reagent(
                name=name,
                expiration_date=expiration_date,
                manufacturer=manufacturer,
                lot_number = lot_number,
                storage_conditions = storage_conditions,
                quantity_in_stock = quantity_in_stock,
                price_per_unit = price_per_unit,
                remaining_quantity = quantity_in_stock,
                          
               
            )
            reagent.save()

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})  

@login_required
def reagent_usage_list(request):
    reagent_usage_list = ReagentUsage.objects.all()
    technicians = Staffs.objects.all()
    reagents = Reagent.objects.all()
    return render(request, 'hod_template/manage_reagent_usage_list.html',
                  {
                      'reagent_usage_list': reagent_usage_list,
                      'technicians': technicians,
                      'reagents': reagents,
                   }
                  )

@csrf_exempt
@require_POST
def add_reagent_used(request):
    try:
        # Extract data from the request
        usage_id = request.POST.get('usage_id')
        labTechnician = request.POST.get('labTechnician')
        reagent_id = request.POST.get('reagent')
        usage_date = request.POST.get('usage_date')
        quantity_used = int(request.POST.get('quantity_used'))
        observation = request.POST.get('observation')
        technician_notes = request.POST.get('technician_notes')

        # Retrieve the corresponding InventoryItem
        labTechnician = Staffs.objects.get(id=labTechnician)
        reagent = Reagent.objects.get(id=reagent_id)
        
        if quantity_used > reagent.remaining_quantity:
            return JsonResponse({'status': 'error', 'message': 'Quantity used exceeds available stock quantity'})


        # Check if the usageHistoryId is provided for editing
        if usage_id:
            # Editing existing usage history
            usage_history = ReagentUsage.objects.get(pk=usage_id)
            # Get the previous quantity used
            previous_quantity_used = usage_history.quantity_used
            # Calculate the difference in quantity
            quantity_difference = quantity_used - previous_quantity_used
            # Update the stock level of the corresponding item
            reagent.remaining_quantity -= quantity_difference
        else:
            # Creating new usage history
            usage_history = ReagentUsage()
         

        # Update or set values for other fields
        usage_history.lab_technician = labTechnician
        usage_history.usage_date = usage_date
        usage_history.quantity_used = quantity_used
        usage_history.technician_notes = technician_notes
        usage_history.reagent = reagent
        usage_history.observation = observation

        # Save the changes to both models
        reagent.save()
        usage_history.save()

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@login_required    
def quality_control_list(request):
    # Retrieve all QualityControl objects
    quality_controls = QualityControl.objects.all()
    technicians = Staffs.objects.filter(role='labTechnician', work_place="resa")
    # Pass the queryset to the template for rendering
    return render(request, 'hod_template/manage_quality_control_list.html', 
                  {
                      'quality_controls': quality_controls,
                      'technicians': technicians,
                      }
                  ) 

@csrf_exempt
@require_POST
def add_quality_control(request):
    try:
        qualitycontrol_id = request.POST.get('qualitycontrol_id')
        lab_technician_id = request.POST.get('lab_technician')
        control_date = request.POST.get('control_date')
        control_type = request.POST.get('control_type')
        result = request.POST.get('result')
        remarks = request.POST.get('remarks')

        # Fetch the lab technician instance
        lab_technician = Staffs.objects.get(id=lab_technician_id)
        
        if qualitycontrol_id:
            # Editing existing quality control item
            quality_control = QualityControl.objects.get(pk=qualitycontrol_id)
            quality_control.lab_technician = lab_technician
            quality_control.control_date = control_date
            quality_control.control_type = control_type
            quality_control.result = result
            quality_control.remarks = remarks
            quality_control.save()
            message = 'Quality control record updated successfully.'
        else:
            # Adding new quality control item
            quality_control = QualityControl(
                lab_technician=lab_technician,
                control_date=control_date,
                control_type=control_type,
                result=result,
                remarks=remarks
            )
            quality_control.save()
            message = 'Quality control record added successfully.'

        return JsonResponse({'success': True, 'message': message})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})



@login_required
def patient_visit_history_view(request, patient_id):
    # Retrieve visit history for the specified patient
    visit_history = PatientVisits.objects.filter(patient_id=patient_id)
    patient = Patients.objects.get(id=patient_id)
    
    for visit in visit_history:
        # Calculate total cost for Prescription
        prescription_cost = Prescription.objects.filter(visit=visit).aggregate(total_cost=Sum('total_price'))['total_cost'] or 0        
        # Calculate total cost for AmbulanceVehicleOrder
        ambulance_cost = AmbulanceOrder.objects.filter(visit=visit).aggregate(total_cost=Sum('cost'))['total_cost'] or 0        
        # Calculate total cost for ImagingRecord
        imaging_cost = ImagingRecord.objects.filter(visit=visit).aggregate(total_cost=Sum('cost'))['total_cost'] or 0        
        # Calculate total cost for ConsultationOrder
        consultation_cost = ConsultationOrder.objects.filter(visit=visit).aggregate(total_cost=Sum('cost'))['total_cost'] or 0        
        # Calculate total cost for Procedure
        procedure_cost = Procedure.objects.filter(visit=visit).aggregate(total_cost=Sum('cost'))['total_cost'] or 0        
        # Calculate total cost for LaboratoryOrder
        lab_cost = LaboratoryOrder.objects.filter(visit=visit).aggregate(total_cost=Sum('cost'))['total_cost'] or 0        
        # Calculate total cost for all models combined
        total_cost = prescription_cost + ambulance_cost + imaging_cost + consultation_cost + procedure_cost + lab_cost        
        # Assign the total cost to the visit object
        visit.total_cost = total_cost    
    return render(request, 'hod_template/manage_patient_visit_history.html', {
        'visit_history': visit_history,
        'patient': patient,     
    })

@login_required    
def patient_health_record_view(request, patient_id, visit_id):
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
        doctors = Staffs.objects.filter(role='doctor',work_place = 'resa')
        provisional_diagnoses = Diagnosis.objects.all()
        final_diagnoses = Diagnosis.objects.all()

        total_price = sum(prescription.total_price for prescription in prescriptions)
        range_31 = range(31)
        current_date = timezone.now().date()
        patient = Patients.objects.get(id=patient_id)

        medicines = Medicine.objects.filter(
            medicineinventory__remain_quantity__gt=0,  # Inventory level greater than zero
            expiration_date__gt=current_date  # Not expired
        ).distinct()

        return render(request, 'hod_template/manage_patient_health_record.html', {
            'visit_history': visit_history,
            'patient': patient,
            'visit': visits,
            'range_31': range_31,
            'medicines': medicines,
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

@login_required
def prescription_list(request):
    # Retrieve all patients
    patients = Patients.objects.all()
    # Retrieve current date
    current_date = timezone.now().date()    
    # Retrieve all prescriptions with related patient and visit
    prescriptions = Prescription.objects.select_related('patient', 'visit')
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
    
    # Retrieve medicines with inventory levels not equal to zero or greater than zero, and not expired
    medicines = Medicine.objects.filter(
        medicineinventory__remain_quantity__gt=0,  # Inventory level greater than zero
        expiration_date__gt=current_date  # Not expired
    ).distinct() 
    
    # Calculate total price of all prescriptions
    total_price = sum(prescription.total_price for prescription in prescriptions) 
    
    return render(request, 'hod_template/manage_prescription_list.html', { 
        'medicines': medicines,
        'patients': patients,
        'total_price': total_price,
        'visit_total_prices': visit_total_prices,
    })
    

@login_required    
def all_orders_view(request):
    # Retrieve all orders from the database
    orders = Order.objects.all().order_by('-order_date')
    
    # Calculate total cost for each order date group
    order_dates_with_total_cost = []
    for order_date in orders.values('order_date').distinct():
        total_cost = orders.filter(order_date=order_date['order_date'],status='Paid').aggregate(total_cost=Sum('cost'))['total_cost']
        order_dates_with_total_cost.append((order_date['order_date'], total_cost))

    # Render the template with the list of orders and total cost for each group
    return render(request, 'hod_template/order_detail.html', {'orders': orders, 'order_dates_with_total_cost': order_dates_with_total_cost})

@login_required
def orders_by_date(request, date):
    # Query orders based on the provided date
    orders = Order.objects.filter(order_date=date)
    # Pass orders and date to the template
    context = {
        'orders': orders,
        'date': date,
    }
    return render(request, 'hod_template/orders_by_date.html', context)

@login_required
def prescription_frequency_list(request):
    frequencies = PrescriptionFrequency.objects.all()
    return render(request, 'hod_template/prescription_frequency_list.html', {'frequencies': frequencies})

@require_POST
def delete_frequency(request):
    try:
        # Get the frequency ID from the POST data
        frequency_id = request.POST.get('frequency_id')
        # Delete the frequency from the database
        frequency = PrescriptionFrequency.objects.get(pk=frequency_id)
        frequency.delete()

        return JsonResponse({'status': 'success', 'message': 'Frequency deleted successfully'})
    except PrescriptionFrequency.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Frequency not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    
def add_frequency(request):
    if request.method == 'POST':
        try:
            frequency_id = request.POST.get('frequency_id')
            name = request.POST.get('name')
            interval = request.POST.get('interval')
            description = request.POST.get('description')
            
            if frequency_id:
                # Editing existing frequency
                frequency = PrescriptionFrequency.objects.get(pk=frequency_id)
                frequency.name = name
                frequency.interval = interval
                frequency.description = description
                frequency.save()
                return JsonResponse({'status': 'success', 'message': 'Prescription frequency updated successfully'})
            else:
                # Adding new frequency
                frequency = PrescriptionFrequency.objects.create(name=name, interval=interval, description=description)
                return JsonResponse({'status': 'success', 'message': 'Prescription frequency added successfully', 'id': frequency.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required    
def generate_invoice_bill(request,  order_id):
    # Retrieve the patient and visit objects based on IDs    
    order = Order.objects.get(id=order_id)     
    context = {
        'order': order,
       
    }
    return render(request, 'hod_template/invoice_bill.html', context)   
    
@login_required
def prescription_detail(request, visit_number, patient_id):
    patient = Patients.objects.get(id=patient_id)
    prescriptions = Prescription.objects.filter(visit__vst=visit_number, visit__patient__id=patient_id)
    prescriber = None
    if prescriptions.exists():
        prescriber = prescriptions.first().entered_by
    context = {
        'patient': patient, 
        'prescriptions': prescriptions,
        'prescriber': prescriber,
        'visit_number': visit_number,
        }
    return render(request, "hod_template/prescription_detail.html", context)    

@login_required    
def patient_vital_list(request, patient_id, visit_id):
    # Retrieve the patient object
    patient = Patients.objects.get(pk=patient_id)
    visit = PatientVisits.objects.get(pk=visit_id)   
    # Retrieve all vital information for the patient
    patient_vitals = PatientVital.objects.filter(patient=patient,visit=visit).order_by('-recorded_at')

    # Render the template with the patient's vital information
    context = {    
        'patient': patient, 
        'patient_vitals': patient_vitals,
        'visit': visit,
    }    
    return render(request, 'hod_template/manage_patient_vital_list.html', context)   

@login_required 
def patient_vital_all_list(request):
    # Retrieve the patient object
    patients = Patients.objects.all() 
    patient_vitals = PatientVital.objects.all().order_by('-recorded_at')
    
    context = {        
        'patients': patients, 
        'patient_vitals': patient_vitals
    }
    # Render the template with the patient's vital information
    return render(request, 'hod_template/manage_all_patient_vital.html', context)    




@login_required    
def diagnosis_list(request):
    diagnoses = Diagnosis.objects.all().order_by('-created_at')    
    return render(request, 'hod_template/manage_diagnosis_list.html', {'diagnoses': diagnoses}) 


@csrf_exempt
@require_POST
def save_diagnosis(request):
    try:
        # Extract data from the request
        diagnosis_name = request.POST.get('diagnosis_name')
        diagnosis_code = request.POST.get('diagnosis_code')
        diagnosis_id = request.POST.get('diagnosis_id')

        # Check if the Diagnosis ID is provided for editing
        if diagnosis_id:
            # Editing existing diagnosis
            diagnosis = Diagnosis.objects.get(pk=diagnosis_id)
            diagnosis.diagnosis_name = diagnosis_name
            diagnosis.diagnosis_code = diagnosis_code
        else:
            # Creating a new diagnosis
            diagnosis = Diagnosis.objects.create(diagnosis_name=diagnosis_name,diagnosis_code=diagnosis_code)

        diagnosis.save()

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required 
def ambulance_order_view(request):
    template_name = 'hod_template/ambulance_order_template.html'
    # Retrieve all ambulance records with the newest records appearing first
    ambulance_orders = AmbulanceOrder.objects.all().order_by('-id')
    return render(request, template_name, {'ambulance_orders': ambulance_orders})
    
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
            return redirect(reverse('clinic:ambulance_order_view'))        
        except Exception as e:
            # Render the template with error message in case of exception
            messages.error(request, f'Error adding/editing ambulance record: {str(e)}')
            return render(request, 'hod_template/add_ambulance_order.html', context)
    else:
        # Render the template with patient and visit data for GET request
        return render(request, 'hod_template/add_ambulance_order.html', context)
    
@login_required    
def vehicle_detail(request, order_id):
    # Retrieve the ambulance vehicle order object using the provided order_id
    order = get_object_or_404(AmbulanceVehicleOrder, pk=order_id)    
    # Render the vehicle detail template with the order object
    return render(request, 'receptionist_template/vehicle_detail.html', {'order': order})     

@login_required     
def ambulance_order_detail(request, order_id):
    # Retrieve the ambulance order object
    ambulance_order = get_object_or_404(AmbulanceOrder, id=order_id)    
    # Pass the ambulance order object to the template
    return render(request, 'hod_template/ambulance_order_detail.html', {'ambulance_order': ambulance_order})

@login_required
def vehicle_ambulance_view(request):
    orders = AmbulanceVehicleOrder.objects.all().order_by('-id')  # Retrieve all AmbulanceVehicleOrder ambulance records, newest first
    template_name = 'hod_template/vehicle_ambulance.html'
    return render(request, template_name, {'orders': orders})


@login_required
def hospital_vehicle_list(request):
    vehicles = HospitalVehicle.objects.all()
    return render(request, 'hod_template/hospital_vehicle_list.html', {'vehicles': vehicles})

def add_vehicle(request):
    if request.method == 'POST':
        try:
            vehicle_id = request.POST.get('vehicle_id')
            if vehicle_id:
                # Editing existing vehicle
                vehicle = HospitalVehicle.objects.get(pk=vehicle_id)
                vehicle.number = request.POST.get('number')
                vehicle.plate_number = request.POST.get('plate_number')
                vehicle.vehicle_type = request.POST.get('vehicle_type')
                vehicle.save()
                return JsonResponse({'status': 'success', 'message': 'Hospital vehicle updated successfully'})
            else:
                # Adding new vehicle
                number = request.POST.get('number')
                plate_number = request.POST.get('plate_number')
                vehicle_type = request.POST.get('vehicle_type')
                new_vehicle = HospitalVehicle.objects.create(number=number, plate_number=plate_number, vehicle_type=vehicle_type)
                return JsonResponse({'status': 'success', 'message': 'Hospital vehicle added successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


@require_POST
def delete_vehicle(request):
    try:
        # Get the frequency ID from the POST data
        vehicle_id = request.POST.get('vehicle_id')
        # Delete the frequency from the database
        vehicle = HospitalVehicle.objects.get(pk=vehicle_id)
        vehicle.delete()
        return JsonResponse({'status': 'success', 'message': 'vehicle deleted successfully'})
    except HospitalVehicle.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'vehicle not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
@require_POST
def delete_ambulance_route(request):
    try:
        # Get the frequency ID from the POST data
        route_id = request.POST.get('route_id')
        # Delete the frequency from the database
        route = AmbulanceRoute.objects.get(id=route_id)
        route.delete()
        return JsonResponse({'status': 'success', 'message': 'route deleted successfully'})
    except AmbulanceRoute.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'route not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
@require_POST
def delete_ambulance_activity(request):
    try:
        # Get the frequency ID from the POST data
        activity_id = request.POST.get('activity_id')
        # Delete the frequency from the database
        activity = AmbulanceActivity.objects.get(id=activity_id)
        activity.delete()
        return JsonResponse({'status': 'success', 'message': 'activity deleted successfully'})
    except AmbulanceActivity.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'activity not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def ambulance_route_list(request):
    ambulance_routes = AmbulanceRoute.objects.all()
    return render(request, 'hod_template/ambulance_route_list.html', {'ambulance_routes': ambulance_routes})    

def add_or_edit_ambulance_route(request):
    if request.method == 'POST':
        try:
            # Retrieve data from POST request
            from_location = request.POST.get('from_location')
            to_location = request.POST.get('to_location')
            distance = request.POST.get('distance')
            cost = request.POST.get('cost')
            profit = request.POST.get('profit')
            advanced_ambulance_cost = request.POST.get('advanced_ambulance_cost')

            # Check if an AmbulanceRoute ID is provided for editing
            ambulance_route_id = request.POST.get('route_id')
            if ambulance_route_id:
                # Edit existing AmbulanceRoute
                ambulance_route = get_object_or_404(AmbulanceRoute, pk=ambulance_route_id)
                ambulance_route.from_location = from_location
                ambulance_route.to_location = to_location
                ambulance_route.distance = distance
                ambulance_route.cost = cost
                ambulance_route.profit = profit
                ambulance_route.advanced_ambulance_cost = advanced_ambulance_cost
                ambulance_route.save()
                return JsonResponse({'status': 'success', 'message': 'Ambulance route updated successfully'})
            else:
                # Create new AmbulanceRoute
                ambulance_route = AmbulanceRoute.objects.create(
                    from_location=from_location,
                    to_location=to_location,
                    distance=distance,
                    cost=cost,
                    profit=profit,
                    advanced_ambulance_cost=advanced_ambulance_cost
                )
                return JsonResponse({'status': 'success', 'message': 'Ambulance route added successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

  
def add_ambulance_activity(request):
    if request.method == 'POST':
        try:
            # Retrieve data from POST request
            activity_id = request.POST.get('activity_id')  # For editing existing activity
            name = request.POST.get('name')
            cost = request.POST.get('cost')
            profit = request.POST.get('profit')            
            # Perform data validation
            if not all([name, cost, profit]):
                return JsonResponse({'status': 'error', 'message': 'All fields are required'}, status=400)          

            if activity_id:
                # Editing existing activity
                activity = AmbulanceActivity.objects.get(id=activity_id)
                activity.name = name
                activity.cost = cost
                activity.profit = profit               
                activity.save()
                return JsonResponse({'status': 'success', 'message': 'Ambulance activity updated successfully'})
            else:
                # Adding new activity
                AmbulanceActivity.objects.create(name=name, cost=cost, profit=profit)
                return JsonResponse({'status': 'success', 'message': 'Ambulance activity added successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)   

@login_required    
def ambulance_activity_list(request):
    ambulance_activities = AmbulanceActivity.objects.all()
    return render(request, 'hod_template/ambulance_activity_list.html', {'ambulance_activities': ambulance_activities}) 

@login_required
def new_consultation_order(request):  
    consultation_orders = ConsultationOrder.objects.all().order_by('-order_date')     
    # Retrieve all unread orders for the ConsultationOrder instances
    unread_orders = Order.objects.filter(order_type__in=[consultation.consultation.name for consultation in consultation_orders], is_read=True)    
    # Mark the retrieved unread orders as read
    orders = unread_orders    
    unread_orders.update(is_read=True)    
    # Render the template with the fetched unread orders
    return render(request, 'hod_template/new_consultation_order.html', {'orders': orders})





@login_required
def new_radiology_order(request):    
    pathodology_records=ImagingRecord.objects.all().order_by('-order_date')   
    unread_orders = Order.objects.filter(order_type__in=[pathology.imaging.name for pathology in pathodology_records], is_read=True)     
    orders = unread_orders   
    unread_orders.update(is_read=True)     
    return render(request,"hod_template/new_radiology_order.html",{
        "orders":unread_orders,       
        }) 
    


@login_required
def new_procedure_order(request):
    template_name = 'hod_template/new_procedure_order.html'
    procedures = Procedure.objects.all().order_by('-order_date')    
    unread_orders = Order.objects.filter(order_type__in=[procedure.name.name for procedure in procedures], is_read=True) 
    print(procedures)
    orders = unread_orders 
    unread_orders.update(is_read=True)         
    return render(request, template_name, {'orders': orders})  
  

def fetch_order_counts_view(request):
    consultation_orders = ConsultationOrder.objects.all() 
    current_date = timezone.now().date()  
    # Retrieve the counts of unread and read orders for the current doctor
    unread_count = Order.objects.filter(order_type__in=[consultation.consultation.name for consultation in consultation_orders], order_date=current_date).count()
    read_count = Order.objects.filter(order_type__in=[consultation.consultation.name for consultation in consultation_orders], is_read=True).count()    
    # Return the counts as JSON response
    return JsonResponse({'unread_count': unread_count, 'read_count': read_count})

def fetch_radiology_order_counts_view(request):  
    pathodology_records=ImagingRecord.objects.all()
    current_date = timezone.now().date()   
    # Retrieve the counts of unread and read orders for the current doctor
    unread_count = Order.objects.filter(order_type__in=[pathology.imaging.name for pathology in pathodology_records],order_date=current_date) .count()
    read_count = Order.objects.filter(order_type__in=[pathology.imaging.name for pathology in pathodology_records], is_read=True) .count()    
    # Return the counts as JSON response
    return JsonResponse({'unread_count': unread_count, 'read_count': read_count})

def fetch_procedure_order_counts_view(request):  
    procedures = Procedure.objects.all()
    current_date = timezone.now().date() 
    # Retrieve the counts of unread and read orders for the current doctor
    unread_count = Order.objects.filter(order_type__in=[procedure.name.name for procedure in procedures], order_date=current_date).count()
    
    read_count = Order.objects.filter(order_type__in=[procedure.name.name for procedure in procedures], is_read=True).count()    
    # Return the counts as JSON response
    return JsonResponse({'unread_count': unread_count, 'read_count': read_count})

def fetch_prescription_counts_view(request):
    # Get the current date
    current_date = timezone.now().date()
    # Query the Prescription model for prescriptions created on the current date
    prescription_count = Prescription.objects.filter(created_at__date=current_date).count()
    # Construct the response data
    response_data = {
        'total_prescriptions': prescription_count
    }
    # Return the response as JSON
    return JsonResponse(response_data)


def add_service(request):
    try:
        if request.method == 'POST':
            # Get form data
            name = request.POST.get('name')
            description = request.POST.get('description')
            type_service = request.POST.get('type_service')
            coverage = request.POST.get('coverage')
            cash_cost = request.POST.get('cash_cost')
            nhif_cost = request.POST.get('nhif_cost')
            insurance_cost = request.POST.get('insurance_cost')
            
            # Check if service ID is provided (for editing existing service)
            service_id = request.POST.get('service_id')
            
            if service_id:
                service = Service.objects.get(pk=service_id)
                # Update existing service
                service.name = name
                service.description = description
                service.type_service = type_service
                service.coverage = coverage
                service.cash_cost = cash_cost
                
                # Add nhif_cost and insurance_cost only if coverage is insurance
                if coverage == 'Insurance':
                    service.nhif_cost = nhif_cost
                    service.insurance_cost = insurance_cost
                else:
                    # If coverage is not insurance, set nhif_cost and insurance_cost to 0
                    service.nhif_cost = 0
                    service.insurance_cost = 0
                
                service.save()
                return JsonResponse({'success': True, 'message': 'Service updated successfully'})
            else:
                # Check if the service name already exists
                if Service.objects.filter(name=name).exists():
                    return JsonResponse({'success': False, 'message': 'Service with this name already exists'})
                
                # Add new service
                new_service = Service.objects.create(name=name, description=description, type_service=type_service, 
                                                      coverage=coverage, cash_cost=cash_cost)
                # Add nhif_cost and insurance_cost only if coverage is insurance
                if coverage == 'Insurance':
                    new_service.nhif_cost = nhif_cost
                    new_service.insurance_cost = insurance_cost
                
                else:
                    service.nhif_cost = 0
                    service.insurance_cost = 0  
                      
                new_service.save()
                    
                return JsonResponse({'success': True, 'message': 'Service added successfully'})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid request method'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required    
def medicine_routes(request):
    routes = MedicineRoute.objects.all()
    return render(request, 'hod_template/medicine_routes.html', {'routes': routes}) 

def add_medicine_route(request):
    try:
        if request.method == 'POST':
            # Get form data
            name = request.POST.get('names')
            explanation = request.POST.get('explanation')
            medicine_route_id = request.POST.get('route_id')  # Check for the ID
            
            # If ID is provided, check if it's an existing medicine route
            if medicine_route_id:
                try:
                    medicine_route = MedicineRoute.objects.get(pk=medicine_route_id)
                    # Update existing medicine route
                    medicine_route.name = name
                    medicine_route.explanation = explanation
                    medicine_route.save()
                    return JsonResponse({'success': True, 'message': 'Medicine route updated successfully'})
                except MedicineRoute.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Medicine route does not exist'})
            else:
                # Check if the name already exists
                if MedicineRoute.objects.filter(name=name).exists():
                    return JsonResponse({'success': False, 'message': 'Medicine route with this name already exists'})
                
                # Create new MedicineRoute
                MedicineRoute.objects.create(name=name, explanation=explanation)
                return JsonResponse({'success': True, 'message': 'Medicine route added successfully'})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid request method'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
    
def delete_medicine_route(request):
    try:
        if request.method == 'POST':
            route_id = request.POST.get('route_id')
            
            if route_id:
                try:
                    route = MedicineRoute.objects.get(pk=route_id)
                    route.delete()
                    return JsonResponse({'success': True, 'message': 'Medicine route deleted successfully'})
                except MedicineRoute.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Medicine route does not exist'})
            else:
                return JsonResponse({'success': False, 'message': 'Invalid route ID'})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid request method'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})    

@login_required    
def medicine_unit_measures(request):
    measures = MedicineUnitMeasure.objects.all()
    return render(request, 'hod_template/medicine_unit_measures.html', {'measures': measures}) 

def add_medicine_unit_measure(request):
    try:
        if request.method == 'POST':
            # Get form data
            name = request.POST.get('name')
            short_name = request.POST.get('short_name')
            application_user = request.POST.get('application_user')

            # Check if the medicine unit measure ID is provided (for editing existing record)
            unit_measure_id = request.POST.get('unit_measure_id')
            if unit_measure_id:
                # Get the existing medicine unit measure instance
                unit_measure = get_object_or_404(MedicineUnitMeasure, pk=unit_measure_id)
                # Update the existing instance
                unit_measure.name = name
                unit_measure.short_name = short_name
                unit_measure.application_user = application_user
                unit_measure.save()
                return JsonResponse({'success': True, 'message': 'Medicine unit measure updated successfully'})

            # Check if the name already exists
            if MedicineUnitMeasure.objects.filter(name=name).exists():
                return JsonResponse({'success': False, 'message': 'Medicine unit measure with this name already exists'})

            # Create new MedicineUnitMeasure
            MedicineUnitMeasure.objects.create(name=name, short_name=short_name, application_user=application_user)
            return JsonResponse({'success': True, 'message': 'Medicine unit measure added successfully'})

        else:
            return JsonResponse({'success': False, 'message': 'Invalid request method'})

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})   
   
def delete_medicine_unit_measure(request):
    try:
        if request.method == 'POST':
            unit_measure_id = request.POST.get('unit_measure_id')
            
            if unit_measure_id:
                try:
                    unit_measure = MedicineUnitMeasure.objects.get(pk=unit_measure_id)
                    unit_measure.delete()
                    return JsonResponse({'success': True, 'message': 'Medicine unit_measure deleted successfully'})
                except MedicineUnitMeasure.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Medicine unit_measure does not exist'})
            else:
                return JsonResponse({'success': False, 'message': 'Invalid unit_measure ID'})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid request method'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})  
