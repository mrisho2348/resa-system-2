import calendar
from datetime import  datetime
from django.utils import timezone
import logging
import numpy as np
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django.db.models import F
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from clinic.forms import  RemoteCounselingForm, RemoteDischargesNotesForm, RemoteObservationRecordForm, RemoteReferralForm
from clinic.models import ChiefComplaint, Diagnosis,   FamilyMedicalHistory, ContactDetails, Country, CustomUser, DiseaseRecode, ImagingRecord, InsuranceCompany, Medicine, PathodologyRecord, PatientHealthCondition, PatientLifestyleBehavior, PatientMedicationAllergy, PatientSurgery, Patients, PrescriptionFrequency, PrimaryPhysicalExamination, Referral,  RemoteCompany, RemoteConsultation, RemoteConsultationNotes, RemoteCounseling, RemoteDischargesNotes, RemoteLaboratoryOrder, RemoteMedicine, RemoteObservationRecord, RemotePatient, RemotePatientDiagnosisRecord, RemotePatientVisits, RemotePatientVital, RemotePrescription, RemoteProcedure, RemoteReferral, RemoteService, SecondaryPhysicalExamination,Staffs

from django.db.models import Sum
from django.views.decorators.http import require_POST
from django.db.models import OuterRef, Subquery





@login_required
def kahama_dashboard(request):
    all_appointment = RemoteConsultation.objects.count()
    total_patients = RemotePatient.objects.count()
    recently_added_patients = RemotePatient.objects.order_by('-created_at')[:6]
    doctors = Staffs.objects.filter(role='doctor', work_place = 'kahama')
    doctors_count = Staffs.objects.filter(role='doctor', work_place = 'kahama').count()
    nurses = Staffs.objects.filter(role='nurse', work_place = 'kahama').count()
    context = {
        'total_patients': total_patients,
        'recently_added_patients': recently_added_patients,
        'all_appointment': all_appointment,
        'doctors': doctors,
        'doctors_count': doctors_count,
        'nurses': nurses,
        # 'gender_based_monthly_counts': gender_based_monthly_counts,
    }
    return render(request,"kahama_template/home_content.html",context)


def get_gender_yearly_data(request):
    if request.method == 'GET':
        selected_year = request.GET.get('year')

        # Query the database to get the total number of male and female patients for the selected year
        male_count = RemotePatient.objects.filter(gender='Male', created_at__year=selected_year).count()
        female_count = RemotePatient.objects.filter(gender='Female', created_at__year=selected_year).count()

        # Create a dictionary with the total male and female counts
        yearly_gender_data = {
            'Male': male_count,
            'Female': female_count
        }

        return JsonResponse(yearly_gender_data)
    else:
        # Return an error response if the request method is not GET or if it's not an AJAX request
        return JsonResponse({'error': 'Invalid request'})
    
def get_patient_data_by_company(request):
    # Query patient data by company
    patient_data = {}

    companies = RemoteCompany.objects.all()
    for company in companies:
        patients_count = RemotePatient.objects.filter(company=company).count()
        patient_data[company.name] = patients_count

    return JsonResponse(patient_data)    

def get_gender_monthly_data(request):
    if request.method == 'GET':
        selected_year = request.GET.get('year')
        
        # Initialize a dictionary to store gender-wise monthly data
        gender_monthly_data = {}

        # Loop through each month and calculate gender-wise counts
        for month in range(1, 13):
            # Get the number of males and females for the current month and year
            male_count = RemotePatient.objects.filter(
                gender='Male',
                created_at__year=selected_year,
                created_at__month=month
            ).count()

            female_count = RemotePatient.objects.filter(
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
    patient_records=Patients.objects.all() 
    return render(request,"kahama_template/manage_patients.html", {"patient_records":patient_records})

@login_required
def manage_country(request):
    countries=Country.objects.all() 
    return render(request,"kahama_template/manage_country.html", {"countries":countries})


@login_required
def manage_consultation(request):
    patients=Patients.objects.all() 
    pathology_records=PathodologyRecord.objects.all() 
    doctors=Staffs.objects.filter(role='doctor', work_place = 'kahama')
    context = {
        'patients':patients,
        'pathology_records':pathology_records,
        'doctors':doctors,
    }
    return render(request,"kahama_template/manage_consultation.html",context)

@login_required
def manage_company(request):
    companies=RemoteCompany.objects.all() 
    return render(request,"kahama_template/manage_company.html",{"companies":companies})

@login_required
def manage_disease(request):
    disease_records=DiseaseRecode.objects.all() 
    return render(request,"kahama_template/manage_disease.html",{"disease_records":disease_records})

@login_required
def manage_staff(request):     
    staffs=Staffs.objects.all()  
    return render(request,"kahama_template/manage_staff.html",{"staffs":staffs})  

@login_required
def manage_insurance(request):
    insurance_companies=InsuranceCompany.objects.all() 
    return render(request,"kahama_template/manage_insurance.html",{"insurance_companies":insurance_companies})

@login_required
def resa_report(request):
    return render(request,"kahama_template/resa_reports.html")



def manage_adjustment(request):
    return render(request,"kahama_template/manage_adjustment.html")

@login_required
def reports_adjustments(request):
    return render(request,"kahama_template/reports_adjustments.html")


@login_required
def reports_by_visit(request):
    # Retrieve all patients
    patients = RemotePatient.objects.all()

    # Create a list to store each patient along with their total visit count
    patients_with_visit_counts = []

    # Iterate through each patient and calculate their total visit count
    for patient in patients:
        total_visits = RemotePatientVisits.objects.filter(patient=patient).count()
        if total_visits > 0:
            patients_with_visit_counts.append({
                'patient': patient,
                'total_visits': total_visits
            })

    context = {
        'patients_with_visit_counts': patients_with_visit_counts
    }
    return render(request, 'kahama_template/reports_by_visit.html', context)

@login_required
def reports_comprehensive(request):
    return render(request,"kahama_template/reports_comprehensive.html")

@login_required
def reports_patients_visit_summary(request):
    visits = RemotePatientVisits.objects.all()
    context = {'visits':visits}
    return render(request,"kahama_template/reports_patients_visit_summary.html",context)

@login_required
def reports_patients(request):
    patients_report = RemotePatient.objects.order_by('-created_at') 
    context = {'patients':patients_report}
    return render(request,"kahama_template/reports_patients.html",context)



@login_required
def reports_service(request):
    return render(request,"kahama_template/reports_service.html")

@login_required
def reports_stock_ledger(request):
    return render(request,"kahama_template/reports_stock_ledger.html")

def reports_stock_level(request):
    return render(request,"kahama_template/reports_stock_level.html")

@login_required
def reports_orders(request):
    return render(request,"kahama_template/reports_orders.html")

@login_required
def individual_visit(request, patient_id):
    # Retrieve the RemotePatient instance
    patient = get_object_or_404(RemotePatient, id=patient_id)
    
    # Retrieve all visits of the patient and order them by created_at
    patient_visits = RemotePatientVisits.objects.filter(patient=patient).order_by('-created_at')

    context = {'patient': patient, 'patient_visits': patient_visits}
    return render(request, 'kahama_template/reports_individual_visit.html', context)
    

@login_required
def product_summary(request):
    return render(request,"kahama_template/product_summary.html")

@login_required
def manage_pathodology(request):
    pathodology_records=PathodologyRecord.objects.all()     
    return render(request,"kahama_template/manage_pathodology.html",{
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
            gender = request.POST.get('gender')
            dob = request.POST.get('dob')
            phone = request.POST.get('phone')
            profession = request.POST.get('profession')            
            marital_status = request.POST.get('maritalStatus')
            email = request.POST.get('email')
            password = request.POST.get('password')            
            user_role = request.POST.get('userRole')

            # Create a new CustomUser instance (if not exists) and link it to Staffs
            user = CustomUser.objects.create_user(username=email, password=password, email=email, first_name=first_name, last_name=lastname, user_type=2)

            # Create a new Staffs instance and link it to the user
            
            user.staff.middle_name = middle_name
            user.staff.date_of_birth = dob
            user.staff.gender = gender            
            user.staff.phone_number = phone            
            user.staff.marital_status = marital_status
            user.staff.profession = profession
            user.staff.role = user_role
        
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
            elif is_active == '0':
                staff.is_active = True
            else:
                messages.error(request, 'Invalid request')
                return redirect('manage_staff')  # Make sure 'manage_staffs' is the name of your staff list URL

            staff.save()
            messages.success(request, 'Status updated successfully')
        else:
            messages.error(request, 'Invalid request method')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')

    # Redirect back to the staff list page
    return redirect('manage_staff')  # Make sure 'manage_staffs' is the name of your staff list URL



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
                return redirect("manage_staff")

            # Retrieve the staff instance from the database
            try:
                staff = Staffs.objects.get(id=staff_id)
            except ObjectDoesNotExist:
                messages.error(request, "Staff not found")
                return redirect("manage_staff")

            # Extract the form data
            first_name = request.POST.get('firstName')
            middle_name = request.POST.get('middleName')
            lastname = request.POST.get('lastname')            
            gender = request.POST.get('gender')
            dob = request.POST.get('date_of_birth')
            phone = request.POST.get('phone')
            profession = request.POST.get('profession')            
            marital_status = request.POST.get('maritalStatus')
            email = request.POST.get('email')                        
            user_role = request.POST.get('userRole')    
          

            # Save the staff details
   
            staff.admin.first_name = first_name
            staff.admin.last_name = lastname
            staff.admin.email = email
            staff.middle_name = middle_name
            staff.role = user_role
            staff.profession = profession
            staff.marital_status = marital_status
            staff.date_of_birth = dob
            staff.phone_number = phone
            staff.gender = gender      
            staff.save()

       
            messages.success(request, "Staff details updated successfully.")
            return redirect("manage_staff")
        except Exception as e:
            messages.error(request, f"Error updating staff details: {str(e)}")

    return redirect("edit_staff",staff_id=staff_id)



@login_required
def single_staff_detail(request, staff_id):
    staff = get_object_or_404(Staffs, id=staff_id)
    # Fetch additional staff-related data  
    context = {
        'staff': staff,
     
    }

    return render(request, "kahama_template/staff_details.html", context)

@login_required
def view_patient(request, patient_id):
    patient = get_object_or_404(Patients, id=patient_id)
    # Fetch additional staff-related data  
    context = {
        'patient': patient,
     
    }

    return render(request, "kahama_template/patients_detail.html", context)





def confirm_meeting(request, appointment_id):
    try:
        # Retrieve the appointment
        appointment = get_object_or_404(RemoteConsultation, id=appointment_id)

        if request.method == 'POST':
            # Get the selected status from the form
            selected_status = int(request.POST.get('status'))

            # Check if the appointment is not already confirmed
            if not appointment.status:
                # Perform the confirmation action (e.g., set status to selected status)
                appointment.status = selected_status
                appointment.save()

                # Add a success message
                messages.success(request, f"Meeting with {appointment.patient.first_name} confirmed.")
            else:
                messages.warning(request, f"Meeting with {appointment.patient.first_name} is already confirmed.")
        else:
            messages.warning(request, "Invalid request method for confirming meeting.")

    except IntegrityError as e:
        # Handle IntegrityError (e.g., database constraint violation)
        messages.error(request, f"Error confirming meeting: {str(e)}")
    return redirect('kahama_appointment_list')  # Adjust the URL name based on your actual URL structure

def edit_meeting(request, appointment_id):
    try:
        if request.method == 'POST':
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')

            appointment = get_object_or_404(RemoteConsultation, id=appointment_id)

            # Perform the edit action (e.g., update start time and end time)
            appointment.start_time = start_time
            appointment.end_time = end_time
            appointment.save()

            messages.success(request, f"Meeting time for {appointment.patient.first_name} edited successfully.")
    except Exception as e:
        messages.error(request, f"Error editing meeting time: {str(e)}")

    return redirect('kahama_appointment_list')



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
                'name': medicine.name,
                'expiration_date': medicine.expiration_date,
                'days_remaining': days_remaining,
            })

    return render(request, 'kahama_template/manage_medicine_expired.html', {'medicines': medicines})

@login_required
def patient_procedure_view(request):
    template_name = 'kahama_template/manage_procedure.html'    
    # Query to retrieve the latest procedure record for each patient
    procedures = RemoteProcedure.objects.filter(
        patient=OuterRef('id')
    ).order_by('-created_at')
    # Query to retrieve patients with their corresponding procedure (excluding patients without procedures)
    patients_with_procedures = RemotePatient.objects.annotate(
        procedure_name=Subquery(procedures.values('name__name')[:1]),
    ).filter(procedure_name__isnull=False)    
  
    data = patients_with_procedures.values(
        'id', 'mrn', 'procedure_name'

    )
    return render(request, template_name, {'data': data})


@login_required
def patient_procedure_history_view(request, mrn):
    patient = get_object_or_404(RemotePatient, mrn=mrn)
    
    # Retrieve all procedures for the specific patient
    procedures = RemoteProcedure.objects.filter(patient=patient)
    patient_procedures =  RemoteService.objects.filter(category='Procedure')
    
    context = {
        'patient': patient,
        'procedures': procedures,
        'patient_procedures': patient_procedures,
    }

    return render(request, 'kahama_template/manage_patient_procedure.html', context)





@csrf_exempt  # Use csrf_exempt decorator for simplicity in this example. For a production scenario, consider using csrf protection.
def save_referral(request):
    if request.method == 'POST':
        try:
                      
            source_location = request.POST.get('source_location')
            destination_location = request.POST.get('destination_location')
            visit_id = request.POST.get('visit_id')
            patient_id = request.POST.get('patient_id')
            consultation_id = request.POST.get('consultation_id')
            reason = request.POST.get('reason')
            notes = request.POST.get('notes')       


            # Save procedure record
            referral_record = RemoteReferral.objects.create(
                patient=RemotePatient.objects.get(id=patient_id),
                visit=RemotePatientVisits.objects.get(id=visit_id),
                consultation=RemoteConsultationNotes.objects.get(id=consultation_id),
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
            referral_record = RemoteReferral.objects.get(id=referral_id)
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
    referrals = RemoteReferral.objects.all()
    patients = RemotePatient.objects.all()
    return render(request, 'kahama_template/manage_referral.html', {'referrals': referrals,'patients':patients})

@login_required
def generate_billing(request, procedure_id):
    procedure = get_object_or_404(RemoteProcedure, id=procedure_id) 
    context = {
        'procedure': procedure,
       
    }

    return render(request, 'kahama_template/billing_template.html', context)

@login_required
def appointment_list_view(request):
    appointments = RemoteConsultation.objects.all() 
    doctors = Staffs.objects.filter(role='doctor', work_place = 'kahama')
    patients = RemotePatient.objects.all()
    context = {        
        'appointments':appointments,
        'doctors':doctors,
        'patients':patients,
    }
    return render(request, 'kahama_template/manage_appointment.html', context)



@csrf_exempt
@login_required
def add_disease(request):
    if request.method == 'POST':
        try:
            # Extract data from the request
            disease_id = request.POST.get('disease_id')
            disease_name = request.POST.get('Disease').strip()
            code = request.POST.get('Code').strip()

            # If disease ID is provided, it's an edit operation
            if disease_id:
                # Check if the disease with the given ID exists
                disease = DiseaseRecode.objects.get(pk=disease_id)
                if disease:
                    # Check if updating the disease name and code will cause a duplicate entry error
                    if DiseaseRecode.objects.exclude(pk=disease_id).filter(disease_name=disease_name).exists():
                        return JsonResponse({'success': False, 'message': 'Another disease with the same name already exists'})                    
                    if DiseaseRecode.objects.exclude(pk=disease_id).filter(code=code).exists():
                        return JsonResponse({'success': False, 'message': 'Another disease with the same code already exists'})
                    
                    # Update disease data
                    disease.disease_name = disease_name
                    disease.code = code
                    disease.save()
                    return JsonResponse({'success': True, 'message': 'Disease updated successfully'})
                else:
                    return JsonResponse({'success': False, 'message': 'Disease does not exist'})

            # Check if the disease already exists
            if DiseaseRecode.objects.filter(disease_name=disease_name).exists():
                return JsonResponse({'success': False, 'message': 'Another disease with the same name already exists'})            
            if DiseaseRecode.objects.filter(code=code).exists():
                return JsonResponse({'success': False, 'message': 'Another disease with the same code already exists'})

            # Save data to the model for new disease
            DiseaseRecode.objects.create(disease_name=disease_name, code=code)
            return JsonResponse({'success': True, 'message': 'Disease added successfully'})

        except IntegrityError:
            # Handle the specific IntegrityError raised when a duplicate entry occurs
            return JsonResponse({'success': False, 'message': 'Disease already exists'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
    
 
@csrf_exempt
@login_required    
def add_insurance_company(request):
    if request.method == 'POST':
        try:
            # Extract data from the request
            company_id = request.POST.get('company_id')
            name = request.POST.get('Name').strip()
            phone = request.POST.get('Phone').strip()
            short_name = request.POST.get('Short_name').strip()
            email = request.POST.get('Email').strip()
            address = request.POST.get('Address').strip()
            website = request.POST.get('website').strip()

            # Check if company_id is provided
            if company_id:
                # Get the existing insurance company object
                insurance_company = InsuranceCompany.objects.get(pk=company_id)
                if insurance_company:
                    # Check if the new name conflicts with existing names
                    if InsuranceCompany.objects.exclude(pk=company_id).filter(name=name).exists():
                        return JsonResponse({'success': False, 'message': 'Another insurance company with the same name already exists'})
                    
                    # Update the insurance company details
                    insurance_company.name = name
                    insurance_company.phone = phone
                    insurance_company.short_name = short_name
                    insurance_company.email = email
                    insurance_company.address = address
                    insurance_company.website = website
                    insurance_company.save()
                    return JsonResponse({'success': True, 'message': 'Insurance company updated successfully'})
                else:
                    return JsonResponse({'success': False, 'message': 'Insurance company does not exist'})
            else:
                # Check if an insurance company with the same name already exists
                if InsuranceCompany.objects.filter(name=name).exists():
                    return JsonResponse({'success': False, 'message': 'Insurance company already exists'})
                
                # Save data to the model for new insurance company
                InsuranceCompany.objects.create(
                    name=name,
                    phone=phone,
                    short_name=short_name,
                    email=email,
                    address=address,
                    website=website,
                )
                
                return JsonResponse({'success': True, 'message': 'Insurance company added successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})

 
@csrf_exempt
@login_required
def add_company(request):
    if request.method == 'POST':
        try:
            # Get data from the request
            company_id = request.POST.get('company_id')
            name = request.POST.get('Name').strip()
            industry = request.POST.get('industry', '')
            sector = request.POST.get('sector', '')
            headquarters = request.POST.get('headquarters', '')
            Founded = request.POST.get('Founded', '')
            Notes = request.POST.get('Notes', '')

            # Check if company_id is provided
            if company_id:
                # Fetch the existing company object
                company = RemoteCompany.objects.get(pk=company_id)

                # Check if the new name already exists and it's not the same as the current name
                if RemoteCompany.objects.filter(name=name).exclude(pk=company_id).exists():
                    return JsonResponse({'success': False, 'message': 'Company with the provided name already exists'})

                # Update company data
                company.name = name
                company.industry = industry
                company.sector = sector
                company.headquarters = headquarters
                company.Founded = Founded
                company.Notes = Notes
                company.save()

                return JsonResponse({'success': True, 'message': 'Company updated successfully'})
            else:
                # Check if a company with the given name already exists
                if RemoteCompany.objects.filter(name=name).exists():
                    return JsonResponse({'success': False, 'message': 'Company already exists'})

                # Save new company data
                RemoteCompany.objects.create(
                    name=name,
                    industry=industry,
                    sector=sector,
                    headquarters=headquarters,
                    Founded=Founded,
                    Notes=Notes,
                )

                return JsonResponse({'success': True, 'message': 'Company added successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
    
  
 
@csrf_exempt
@login_required
def add_pathodology_record(request):
    if request.method == 'POST':
        try:
            # Extract data from the request
            name = request.POST.get('Name').strip()
            description = request.POST.get('Description')
            pathology_record_id = request.POST.get('pathology_record_id')
            
            # If pathology record ID is provided, it's an edit operation
            if pathology_record_id:             
                
                # Check if the provided name already exists in the database excluding the current record
                if PathodologyRecord.objects.exclude(pk=pathology_record_id).filter(name=name).exists():
                    return JsonResponse({'success': False, 'message':  f'Another pathology record with the name "{name}" already exists'})
                 # Get the existing pathology record object
                pathology_record = PathodologyRecord.objects.get(pk=pathology_record_id)
                # Update the existing pathology record
                pathology_record.name = name
                pathology_record.description = description
                pathology_record.save()
                return JsonResponse({'success': True, 'message': 'Patholody updated successfully'})
            else:  # If no pathology record ID is provided, it's an add operation
                # Check if the provided name already exists in the database
                if PathodologyRecord.objects.filter(name=name).exists():
                    return JsonResponse({'success': False, 'message':  f'A pathology record with the name "{name}" already exists'})

                # Save data to the model for a new pathology record
                pathodology_record = PathodologyRecord.objects.create(
                    name=name,
                    description=description
                )
                return JsonResponse({'success': True, 'message': f'{name} added successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})

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
def out_of_stock_medicines_view(request):
    try:
        # Query the database for out-of-stock medicines
        out_of_stock_medicines = Medicine.objects.filter(remain_quantity=0)
        
        # Render the template with the out-of-stock medicines data
        return render(request, 'kahama_template/manage_out_of_stock_medicines.html', {'out_of_stock_medicines': out_of_stock_medicines})
    
    except Exception as e:
        # Handle any errors and return an error response
        return render(request, '404.html', {'error_message': str(e)}) 


    
@login_required    
def in_stock_medicines_view(request):
    # Retrieve medicines with inventory levels above zero
    in_stock_medicines = Medicine.objects.filter(remain_quantity__gt=0)

    return render(request, 'kahama_template/manage_in_stock_medicines.html', {'in_stock_medicines': in_stock_medicines})  



@login_required
def patient_visit_history_view(request, patient_id):
    # Retrieve visit history for the specified patient
    visit_history = RemotePatientVisits.objects.filter(patient_id=patient_id)
    current_date = timezone.now().date()
    doctors = Staffs.objects.filter(role='doctor', work_place = 'kahama')
    patient = RemotePatient.objects.get(id=patient_id)   
    return render(request, 'kahama_template/manage_patient_visit_history.html', {
        'visit_history': visit_history,
        'patient':patient,        
        'doctors': doctors,
        })

@login_required    
def patient_health_record_view(request, patient_id, visit_id):
    try:
        # Retrieve visit history for the specified patient
        visits = RemotePatientVisits.objects.get(id=visit_id)
        visit_history = RemotePatientVisits.objects.filter(patient_id=patient_id)
        prescriptions = RemotePrescription.objects.filter(patient=patient_id, visit=visit_id)
        try:
            consultation_notes = RemoteConsultationNotes.objects.filter(patient_id=patient_id, visit=visit_id).order_by('-created_at').first()
        except RemoteConsultationNotes.DoesNotExist:
            consultation_notes = None
         
        try:
            previous_vitals = RemotePatientVital.objects.filter(patient=patient_id,visit=visit_id).order_by('-recorded_at')
        except RemotePatientVital.DoesNotExist:
            previous_vitals = None   
             
        try:
            consultation_notes_previous  = RemoteConsultationNotes.objects.filter(patient=patient_id).order_by('-created_at')
        except RemoteConsultationNotes.DoesNotExist:
            consultation_notes_previous  = None   
             
        try:
            vital = RemotePatientVital.objects.filter(patient=patient_id, visit=visit_id)
        except RemotePatientVital.DoesNotExist:
            vital = None
            
        try:
            procedures = RemoteProcedure.objects.filter(patient=patient_id, visit=visit_id)            
        except RemoteProcedure.DoesNotExist:
            procedures = None
          
       
     
        pathology_records = PathodologyRecord.objects.all()  # Fetch all consultation notes from the database
        doctors = Staffs.objects.filter(role='doctor', work_place = 'kahama')
        provisional_diagnoses = Diagnosis.objects.all()
        final_diagnoses = Diagnosis.objects.all()

        total_price = sum(prescription.total_price for prescription in prescriptions)
        range_31 = range(31)
        current_date = timezone.now().date()
        patient = RemotePatient.objects.get(id=patient_id)

        medicines = Medicine.objects.filter(
            medicineinventory__remain_quantity__gt=0,  # Inventory level greater than zero
            expiration_date__gt=current_date  # Not expired
        ).distinct()

        return render(request, 'kahama_template/manage_patient_health_record.html', {
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
            'consultation_notes_previous': consultation_notes_previous,
            'provisional_diagnoses': provisional_diagnoses,
            'previous_vitals': previous_vitals,
            'final_diagnoses': final_diagnoses,
            'vital': vital,          
            'procedures': procedures,
      
        })
    except Exception as e:
        # Handle other exceptions if necessary
        return render(request, '404.html', {'error_message': str(e)})
    
    
@login_required
def patient_visit_details_view(request, patient_id, visit_id):
    try:        
        visit = RemotePatientVisits.objects.get(id=visit_id)
        prescriptions = RemotePrescription.objects.filter(patient=patient_id, visit=visit_id)
        chief_complaints = ChiefComplaint.objects.filter(patient_id=patient_id, visit_id=visit_id)
        primary_physical_examination = PrimaryPhysicalExamination.objects.filter(patient_id=patient_id, visit_id=visit_id).first()
        secondary_physical_examination = SecondaryPhysicalExamination.objects.filter(patient=patient_id, visit=visit_id).first()
        consultation_notes = RemoteConsultationNotes.objects.filter(patient_id=patient_id, visit=visit_id).order_by('-created_at').first()
        vitals = RemotePatientVital.objects.filter(patient=patient_id, visit=visit_id).order_by('-recorded_at')
        referral_records  = RemoteReferral.objects.filter(patient=patient_id, visit=visit_id).order_by('-created_at')
        counseling_records = RemoteCounseling.objects.filter(patient=patient_id, visit=visit_id).order_by('-created_at')        
        procedures = RemoteProcedure.objects.filter(patient=patient_id, visit=visit_id)        
        discharge_notes = RemoteDischargesNotes.objects.filter(patient=patient_id, visit=visit_id)
        observation_records = RemoteObservationRecord.objects.filter(patient=patient_id, visit=visit_id)
        lab_tests = RemoteLaboratoryOrder.objects.filter(patient=patient_id, visit=visit_id)         
        diagnosis_record = RemotePatientDiagnosisRecord.objects.filter(patient_id=patient_id, visit_id=visit_id).first()
        patient = get_object_or_404(RemotePatient, id=patient_id)

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
            'discharge_notes': discharge_notes,
        }

        return render(request, 'kahama_template/manage_patient_visit_detail_record.html', context)
    except Patients.DoesNotExist:
        raise Http404("Patient does not exist")
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)})    
    

    

@login_required
def prescription_list(request):  
    # Retrieve all prescriptions with related patient and visit
    prescriptions = RemotePrescription.objects.select_related('patient', 'visit')
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
    verified=F('verified'), 
    issued=F('issued'),   
    status=F('status'),      
)
   
    # Calculate total price of all prescriptions
    total_price = sum(prescription.total_price for prescription in prescriptions)     
    return render(request, 'kahama_template/manage_prescription_list.html', { 
        'total_price': total_price,
        'visit_total_prices': visit_total_prices,
    })
    
    
@login_required
def prescription_detail(request, visit_number, patient_id):
    patient = RemotePatient.objects.get(id=patient_id)
    prescriptions = RemotePrescription.objects.filter(visit__vst=visit_number, patient_id=patient_id)    
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
    return render(request, "kahama_template/prescription_detail.html", context)

@login_required
def prescription_billing(request, visit_number, patient_id):
    patient = RemotePatient.objects.get(id=patient_id)
    visit = RemotePatientVisits.objects.get(vst=visit_number)
    prescriptions = RemotePrescription.objects.filter(visit__vst=visit_number, visit__patient__id=patient_id)
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
    return render(request, "kahama_template/prescription_bill.html", context)

@login_required
def prescription_notes(request, visit_number, patient_id):
    patient = RemotePatient.objects.get(id=patient_id)
    visit = RemotePatientVisits.objects.get(vst=visit_number)
    prescriptions = RemotePrescription.objects.filter(visit__vst=visit_number, visit__patient__id=patient_id)
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
    return render(request, "kahama_template/prescription_notes.html", context)



@login_required    
def patient_vital_list(request, patient_id,visit_id):
    # Retrieve the patient object
    patient = RemotePatient.objects.get(pk=patient_id)
    visit = RemotePatientVisits.objects.get(pk=visit_id)  
    patient_vitals = RemotePatientVital.objects.filter(patient=patient).order_by('-recorded_at')
    # Render the template with the patient's vital information
    context = {      
        'patient': patient, 
        'visit': visit, 
        'patient_vitals': patient_vitals
    }
    
    return render(request, 'kahama_template/manage_patient_vital_list.html', context)  

@login_required  
def patient_vital_all_list(request):
    # Retrieve the patient object
    patients = Patients.objects.all()  
    patient_vitals = RemotePatientVital.objects.all().order_by('-recorded_at')
    
    context = {      
        'patients': patients, 
        'patient_vitals': patient_vitals
    }
    # Render the template with the patient's vital information
    return render(request, 'kahama_template/manage_all_patient_vital.html', context)    


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
        doctor = request.user.staff

        try:
            # Retrieve the patient
            patient = RemotePatient.objects.get(id=patient_id)
        except RemotePatient.DoesNotExist:
            return JsonResponse({'status': False, 'message': 'Patient does not exist'})

        try:
            # Retrieve the visit
            visit = RemotePatientVisits.objects.get(id=visit_id)
        except RemotePatientVisits.DoesNotExist:
            return JsonResponse({'status': False, 'message': 'Visit does not exist'})

        # Check for duplicate records
        blood_pressure = f"{sbp}/{dbp}"
        if not vital_id:
            duplicate_vitals = RemotePatientVital.objects.filter(
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
            )
            if duplicate_vitals.exists():
                return JsonResponse({'status': False, 'message': 'A similar vital record already exists for this patient during this visit.'})

        if vital_id:
            try:
                # Editing existing vital
                vital = RemotePatientVital.objects.get(pk=vital_id)
                vital.blood_pressure = blood_pressure if sbp and dbp else vital.blood_pressure  # Use existing SBP/DBP if not provided
                message = 'Patient vital updated successfully'
            except RemotePatientVital.DoesNotExist:
                return JsonResponse({'status': False, 'message': 'Vital record does not exist'})
        else:
            # Creating new vital
            vital = RemotePatientVital()
            vital.blood_pressure = blood_pressure
            message = 'Patient vital created successfully'

        # Update or set values for other fields
        vital.visit = visit
        vital.respiratory_rate = respiratory_rate
        vital.pulse_rate = pulse_rate
        vital.doctor = doctor
        vital.blood_pressure = blood_pressure
        vital.sbp = sbp
        vital.dbp = dbp
        vital.spo2 = spo2
        vital.gcs = gcs
        vital.temperature = temperature
        vital.avpu = avpu
        vital.patient = patient
        vital.save()

        return JsonResponse({'status': True, 'message': message})
    except RemotePatient.DoesNotExist:
        return JsonResponse({'status': False, 'message': 'Patient does not exist'})
    except RemotePatientVisits.DoesNotExist:
        return JsonResponse({'status': False, 'message': 'Visit does not exist'})
    except Exception as e:
        return JsonResponse({'status': False, 'message': str(e)})
    
    
@login_required
def save_remotepatient_vitals(request, patient_id, visit_id):
    patient = RemotePatient.objects.get(pk=patient_id)
    visit = RemotePatientVisits.objects.get(patient=patient_id, id=visit_id)
    range_51 = range(51)
    integer_range = np.arange(start=0, stop=510, step=1)
    temps = integer_range / 10
    range_301 = range(301)
    range_101 = range(101)
    range_15 = range(3, 16)
    context = {
        'patient': patient,
        'range_51': range_51,
        'range_301': range_301,
        'range_101': range_101,
        'range_15': range_15,
        'temps': temps,
        'visit': visit,
    }
    try:
        # Retrieve the current logged-in user (presumably a doctor)
        doctor = request.user.staff
        
        # Check if a vital record already exists for this patient and visit
        existing_vital = RemotePatientVital.objects.filter(patient=patient, visit=visit).last()
        
        if existing_vital:
            # Include existing vital in the context if it exists
            context['existing_vital'] = existing_vital

        if request.method == 'POST':
            # Retrieve form data
            respiratory_rate = request.POST.get('respiratory_rate')
            pulse_rate = request.POST.get('pulse_rate')
            sbp = request.POST.get('sbp')
            dbp = request.POST.get('dbp')
            blood_pressure = f"{sbp}/{dbp}"
            spo2 = request.POST.get('spo2')
            temperature = request.POST.get('temperature')
            gcs = request.POST.get('gcs')
            avpu = request.POST.get('avpu')

            if existing_vital:  # If a record exists, update it
                existing_vital.respiratory_rate = respiratory_rate
                existing_vital.pulse_rate = pulse_rate
                existing_vital.sbp = sbp
                existing_vital.dbp = dbp
                existing_vital.spo2 = spo2
                existing_vital.blood_pressure = blood_pressure
                existing_vital.temperature = temperature
                existing_vital.gcs = gcs
                existing_vital.avpu = avpu
                existing_vital.save()
                messages.success(request, 'Remote patient vital information updated successfully.')
            else:  # If no record exists, create a new one
                RemotePatientVital.objects.create(
                    patient=patient,
                    visit=visit,
                    doctor=doctor,
                    respiratory_rate=respiratory_rate,
                    pulse_rate=pulse_rate,
                    sbp=sbp,
                    dbp=dbp,
                    blood_pressure=blood_pressure,
                    spo2=spo2,
                    temperature=temperature,
                    gcs=gcs,
                    avpu=avpu
                )
                messages.success(request, 'Remote patient vital information saved successfully.')

            # Redirect to a success page or any other page as needed
            return redirect(reverse('kahama_save_remotesconsultation_notes', args=[patient_id, visit_id]))
        else:
            return render(request, 'kahama_template/add_remotepatient_vital.html', context)

    except Exception as e:
        # Handle any other exceptions
        messages.error(request, f'Error adding/editing remote patient vital information: {str(e)}')
        return render(request, 'kahama_template/add_remotepatient_vital.html', context)
    


    
@login_required        
def consultation_notes_view(request):
    consultation_notes = RemoteConsultationNotes.objects.all() 
    return render(request, 'kahama_template/manage_consultation_notes.html', {
        'consultation_notes': consultation_notes,       
        })    

@login_required
def save_prescription(request, patient_id, visit_id):
    try:
        # Retrieve visit history for the specified patient
        visit = RemotePatientVisits.objects.get(id=visit_id)         
        frequencies = PrescriptionFrequency.objects.all()         
        prescriptions = RemotePrescription.objects.filter(patient=patient_id, visit_id=visit_id)        
        consultation_notes = RemotePatientDiagnosisRecord.objects.filter(patient=patient_id, visit=visit_id)  
        current_date = timezone.now().date()
        patient = RemotePatient.objects.get(id=patient_id)    
        total_price = sum(prescription.total_price for prescription in prescriptions)  
        medicines = RemoteMedicine.objects.filter(
            remain_quantity__gt=0,  # Inventory level greater than zero
            expiration_date__gt=current_date  # Not expired
        ).distinct()
        range_31 = range(1,31)
        return render(request, 'kahama_template/prescription_template.html', {           
            'patient': patient,
            'visit': visit,       
            'consultation_notes': consultation_notes,       
            'medicines': medicines,
            'total_price': total_price,
            'range_31': range_31,
            'frequencies': frequencies,
            'prescriptions': prescriptions,
         
        })
    except Exception as e:
        # Handle other exceptions if necessary
        return render(request, '404.html', {'error_message': str(e)})    

@login_required
def save_nextprescription(request, patient_id, visit_id):
    try:
        # Retrieve visit history for the specified patient
        visit = RemotePatientVisits.objects.get(id=visit_id)         
        frequencies = PrescriptionFrequency.objects.all()         
        prescriptions = RemotePrescription.objects.filter(patient=patient_id, visit_id=visit_id)        
        consultation_notes = RemotePatientDiagnosisRecord.objects.filter(patient=patient_id, visit=visit_id)  
        current_date = timezone.now().date()
        patient = RemotePatient.objects.get(id=patient_id)    
        total_price = sum(prescription.total_price for prescription in prescriptions)  
        medicines = RemoteMedicine.objects.filter(
            remain_quantity__gt=0,  # Inventory level greater than zero
            expiration_date__gt=current_date  # Not expired
        ).distinct()
        range_31 = range(1,31)
        return render(request, 'kahama_template/nextprescription_template.html', {           
            'patient': patient,
            'visit': visit,       
            'consultation_notes': consultation_notes,       
            'medicines': medicines,
            'total_price': total_price,
            'range_31': range_31,
            'frequencies': frequencies,
            'prescriptions': prescriptions,
         
        })
    except Exception as e:
        # Handle other exceptions if necessary
        return render(request, '404.html', {'error_message': str(e)})    
    

@login_required
def save_nextlaboratory(request, patient_id, visit_id):
    patient = get_object_or_404(RemotePatient, id=patient_id)
    visit = get_object_or_404(RemotePatientVisits, id=visit_id)
    remote_service = RemoteService.objects.filter(category='Laboratory')
    data_recorder = request.user.staff
    previous_results = RemoteLaboratoryOrder.objects.filter(patient=patient)
    consultation_notes = RemotePatientDiagnosisRecord.objects.filter(patient=patient_id, visit=visit_id)  
    # Check if the laboratory order already exists for this patient on the specified visit
    laboratory_order = RemoteLaboratoryOrder.objects.filter(patient=patient, visit=visit).first()
    context = {
                'patient': patient,
               'visit': visit, 
               'previous_results': previous_results,
               'remote_service': remote_service,
               'consultation_notes': consultation_notes,
               } 

    if request.method == 'POST':
        # Retrieve the list of investigation names, descriptions, and results from the form data
        investigation_names = request.POST.getlist('investigation_name[]')
        descriptions = request.POST.getlist('description[]')

        try:
            for name, description in zip(investigation_names, descriptions):
                # If the laboratory order already exists, update it
                if laboratory_order:
                    laboratory_order.data_recorder = data_recorder         
                    laboratory_order.name_id = name         
                    laboratory_order.result = description
                    laboratory_order.save()
                    messages.success(request, 'Laboratory order updated successfully.')
                else:
                    # If no laboratory order exists, create a new one
                    RemoteLaboratoryOrder.objects.create(
                        data_recorder=data_recorder,
                        patient=patient,
                        visit=visit,
                        name_id=name,
                        result=description
                    )
                    messages.success(request, 'Laboratory order saved successfully.')
            # Redirect to a success page or another view
            return redirect(reverse('kahama_save_remotesconsultation_notes', args=[patient_id, visit_id]))
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

    return render(request, 'kahama_template/nextlaboratory_template.html', context)
    

    
@login_required
def save_nextremotereferral(request, patient_id, visit_id):
    try:
        # Retrieve patient and visit objects
        patient = get_object_or_404(RemotePatient, id=patient_id)
        visit = get_object_or_404(RemotePatientVisits, id=visit_id)        
        data_recorder = request.user.staff
        referral = RemoteReferral.objects.filter(patient=patient, visit=visit).first()   
        context = {'patient': patient, 'visit': visit, 'referral': referral}  

        if request.method == 'POST':
            # Process the form data if it's a POST request
            form = RemoteReferralForm(request.POST, instance=referral)
            
            if form.is_valid():
                # If a referral record exists, update it
                if referral:
                    referral = form.save(commit=False)
                    referral.patient = patient
                    referral.visit = visit
                    referral.data_recorder = data_recorder
                    referral.save()
                    messages.success(request, 'Remote referral updated successfully.')
                else:
                    # If no referral record exists, create a new one
                    form.instance.patient = patient
                    form.instance.visit = visit
                    form.instance.data_recorder = data_recorder
                    form.save()
                    messages.success(request, 'Remote referral saved successfully.')
                
                # Redirect to a success page or another view
                return redirect(reverse('kahama_save_remotesconsultation_notes', args=[patient_id, visit_id]))
            else:
                messages.error(request, 'Please correct the errors in the form.')
        else:
            # If it's a GET request, initialize the form with existing data (if any)
            form = RemoteReferralForm(instance=referral)
        
        context['form'] = form
        return render(request, 'kahama_template/nextsave_remotereferral.html', context)
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return render(request, 'kahama_template/nextsave_remotereferral.html', context)
    
    

@login_required    
def save_nextcounsel(request, patient_id, visit_id):
    # Retrieve patient and visit objects
    patient = get_object_or_404(RemotePatient, id=patient_id)
    visit = get_object_or_404(RemotePatientVisits, id=visit_id)   
    consultation_notes = RemotePatientDiagnosisRecord.objects.filter(patient=patient_id, visit=visit_id)             
    data_recorder = request.user.staff
    # Retrieve existing remote counseling record if it exists
    remote_counseling = RemoteCounseling.objects.filter(patient=patient, visit=visit).first()
    
    # Prepare context for rendering the template
    context = {
        'patient': patient, 
        'visit': visit,
        'consultation_notes': consultation_notes,
        'remote_counseling': remote_counseling,
    }
    
    # Handle form submission
    if request.method == 'POST':        
        form = RemoteCounselingForm(request.POST, instance=remote_counseling)
        
        # Check if a record already exists for the patient and visit
        if remote_counseling:
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
            form.instance.data_recorder = data_recorder
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
        return redirect(reverse('kahama_save_remotesconsultation_notes', args=[patient_id, visit_id]))
   
    else:
        # If it's a GET request, initialize the form with existing data (if any)
        form = RemoteCounselingForm(instance=remote_counseling)   
    # Add the form to the context
    context['form'] = form    
    return render(request, 'kahama_template/nextcounsel_template.html', context)


    
@login_required    
def save_nextremoteprocedure(request, patient_id, visit_id):
    patient = get_object_or_404(RemotePatient, id=patient_id)
    visit = get_object_or_404(RemotePatientVisits, id=visit_id)
    procedures = RemoteService.objects.filter(category='Procedure')
    previous_procedures = RemoteProcedure.objects.filter(patient_id=patient_id)
    context = {
        'patient': patient, 
        'visit': visit, 
        'procedures': procedures,
        'previous_procedures': previous_procedures,
        }   
    try:
        if request.method == 'POST':
            # Get the list of procedure names and descriptions from the form
            names = request.POST.getlist('name[]')
            descriptions = request.POST.getlist('description[]')            
            # Validate if all required fields are present
            if not all(names) or not all(descriptions):
                messages.error(request, 'Please fill out all required fields.')
                return render(request, 'kahama_template/nextprocedure_template.html', context)            
            # Loop through the submitted data to add or update each procedure
            for name, description in zip(names, descriptions):
                # Check if a RemoteProcedure record already exists for this patient on the specified visit
                existing_procedure = RemoteProcedure.objects.filter(patient_id=patient_id, visit_id=visit_id, name_id=name).first()
                
                if existing_procedure:
                    # If a procedure exists, update it
                    existing_procedure.description = description                  
                    existing_procedure.save()
                    messages.success(request, 'Remote procedure updated successfully.')
                else:
                    RemoteProcedure.objects.create(
                        patient_id=patient_id,
                        visit_id=visit_id,
                        name_id=name,
                        description=description,
                    )                    
            messages.success(request, 'Remote procedure saved successfully.')
            return redirect(reverse('kahama_save_remotesconsultation_notes', args=[patient_id, visit_id]))  # Change 'success_page' to your success page URL name
        else:
            # If request method is not POST, render the corresponding template
            return render(request, 'kahama_template/nextprocedure_template.html', context)
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')        
        return render(request, 'kahama_template/nextprocedure_template.html', context)   
    

    
@login_required
def save_nextobservation(request, patient_id, visit_id):
    patient = get_object_or_404(RemotePatient, id=patient_id)
    visit = get_object_or_404(RemotePatientVisits, id=visit_id)
    data_recorder = request.user.staff
    record_exists = RemoteObservationRecord.objects.filter(patient_id=patient_id, visit_id=visit_id).first()
    context = {'patient': patient, 'visit': visit, 'record_exists': record_exists}
    if request.method == 'POST':
        form = RemoteObservationRecordForm(request.POST)
        if form.is_valid():
            description = form.cleaned_data['observation_notes']
            try:
                if record_exists:
                    # If a record exists, update it
                    observation_record = RemoteObservationRecord.objects.get(patient_id=patient_id, visit_id=visit_id)
                    observation_record.observation_notes = description
                    observation_record.data_recorder = data_recorder
                    observation_record.save()
                    messages.success(request, 'Remote observation record updated successfully.')
                else:
                    # If no record exists, create a new one
                    RemoteObservationRecord.objects.create(
                        patient=patient,
                        visit=visit,
                        data_recorder=data_recorder,
                        observation_notes=description,
                    )
                    messages.success(request, 'Remote observation record saved successfully.')
                return redirect(reverse('kahama_save_remotesconsultation_notes', args=[patient_id, visit_id]))
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            messages.error(request, 'Please fill out all required fields.')
    else:
        form = RemoteObservationRecordForm(initial={'observation_notes': record_exists.observation_notes if record_exists else ''})

    context['form'] = form
    return render(request, 'kahama_template/nextobservation_template.html', context)

@login_required    
def save_nextremote_discharges_notes(request, patient_id, visit_id):
    patient = get_object_or_404(RemotePatient, id=patient_id)
    visit = get_object_or_404(RemotePatientVisits, id=visit_id)
    remote_discharges_notes = RemoteDischargesNotes.objects.filter(patient=patient, visit=visit).first()  
    context = {
            'patient': patient,
            'visit': visit,
            'remote_discharges_notes': remote_discharges_notes,         
        }
        
    try:      
        # Check if the request user is staff
        data_recorder = request.user.staff      
        # Handle form submission
        if request.method == 'POST':
            form = RemoteDischargesNotesForm(request.POST, instance=remote_discharges_notes)
            if form.is_valid():
                remote_discharges_notes = form.save(commit=False)
                remote_discharges_notes.patient = patient
                remote_discharges_notes.visit = visit
                remote_discharges_notes.data_recorder = data_recorder
                remote_discharges_notes.save()
                messages.success(request, 'Remote discharge notes saved successfully.')
                return redirect(reverse('kahama_save_remotesconsultation_notes', args=[patient_id, visit_id]))  # Redirect to the next view
            else:
                messages.error(request, 'Please correct the errors in the form.')
        else:
            form = RemoteDischargesNotesForm(instance=remote_discharges_notes)        
        # Prepare context for rendering the template
        context['form'] = form
        return render(request, 'kahama_template/next_discharge_template.html', context)    
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return render(request, 'kahama_template/next_discharge_template.html', context)
    


def diagnosis_list(request):
    diagnoses = Diagnosis.objects.all().order_by('-created_at')    
    return render(request, 'kahama_template/manage_diagnosis_list.html', {'diagnoses': diagnoses}) 


@login_required
@csrf_exempt
@require_POST
def save_diagnosis(request):
    try:
        # Extract and trim data from the request
        diagnosis_name = request.POST.get('diagnosis_name', '').strip()
        diagnosis_code = request.POST.get('diagnosis_code', '').strip()
        diagnosis_id = request.POST.get('diagnosis_id', '')

        if diagnosis_id:
            # Editing existing diagnosis
            try:
                diagnosis = Diagnosis.objects.get(pk=diagnosis_id)
            except Diagnosis.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Diagnosis not found.'})

            # Check for uniqueness excluding the current diagnosis
            if Diagnosis.objects.exclude(pk=diagnosis_id).filter(diagnosis_name=diagnosis_name).exists():
                return JsonResponse({'success': False, 'message': 'Diagnosis with this name already exists.'})
            
            if Diagnosis.objects.exclude(pk=diagnosis_id).filter(diagnosis_code=diagnosis_code).exists():
                return JsonResponse({'success': False, 'message': 'Diagnosis with this code already exists.'})

            # Update fields
            diagnosis.diagnosis_name = diagnosis_name
            diagnosis.diagnosis_code = diagnosis_code
            diagnosis.save()
            return JsonResponse({'success': True, 'message': 'Diagnosis updated successfully.'})
        else:
            # Adding new diagnosis
            # Check for uniqueness
            if Diagnosis.objects.filter(diagnosis_name=diagnosis_name).exists():
                return JsonResponse({'success': False, 'message': 'Diagnosis with this name already exists.'})
            if Diagnosis.objects.filter(diagnosis_code=diagnosis_code).exists():
                return JsonResponse({'success': False, 'message': 'Diagnosis with this code already exists.'})

            # Create new diagnosis
            diagnosis = Diagnosis.objects.create(diagnosis_name=diagnosis_name, diagnosis_code=diagnosis_code)
            return JsonResponse({'success': True, 'message': 'Diagnosis added successfully.'})

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

  
    
    
@login_required    
def patient_info_form(request):  
    if request.method == 'POST':
        try:
            # Retrieve data from the form submission
            first_name = request.POST.get('first_name')
            middle_name = request.POST.get('middle_name')
            last_name = request.POST.get('last_name')
            # Capitalize the received values
            first_name = first_name.capitalize() if first_name else None
            middle_name = middle_name.capitalize() if middle_name else None
            last_name = last_name.capitalize() if last_name else None
            gender = request.POST.get('gender')
            occupation = request.POST.get('occupation')
            other_occupation = request.POST.get('other_occupation')
            phone = request.POST.get('phone')           
            osha_certificate = request.POST.get('osha_certificate')
            date_of_osha_certification = request.POST.get('date_of_osha_certification')
            insurance = request.POST.get('insurance')
            insurance_company = request.POST.get('insurance_company')
            other_insurance = request.POST.get('other_insurance')
            insurance_number = request.POST.get('insurance_number')
            emergency_contact_name = request.POST.get('emergency_contact_name')
            emergency_contact_relation = request.POST.get('emergency_contact_relation')
            other_relation = request.POST.get('other_relation')
            emergency_contact_phone = request.POST.get('emergency_contact_phone')
            marital_status = request.POST.get('marital_status')
            nationality_id = request.POST.get('nationality')
            patient_type = request.POST.get('patient_type')
            other_patient_type = request.POST.get('other_patient_type')
            company_id = request.POST.get('company')
            age = request.POST.get('age')
            dob = request.POST.get('dob')
            # Check if age or dob is provided
            if dob:
                # Calculate age from dob
                try:
                    dob_date = datetime.strptime(dob, '%Y-%m-%d').date()  # Use datetime class from datetime module
                    current_date = datetime.today().date()  # Use datetime class from datetime module
                    age = current_date.year - dob_date.year - ((current_date.month, current_date.day) < (dob_date.month, dob_date.day))
                except ValueError:
                    age = None
                    
            elif age:
                # Calculate dob from age
                try:
                    age_int = int(age)
                    current_date = datetime.today().date()  # Use datetime class from datetime module
                    dob = current_date.replace(year=current_date.year - age_int)
                except ValueError:
                    dob = None           
             # Check if a patient with the same name already exists
            # Convert empty fields to None
            date_of_osha_certification = date_of_osha_certification or None
            dob = dob or None
            age = age or None

            # Check if a patient with the same information already exists
            existing_patient = RemotePatient.objects.filter(
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,                          
            ).exists()

            if existing_patient:                
                messages.error(request, f'A patient with the same information already exists.')
                return redirect(reverse('kahama_patient_info_form'))
            
            # Create or update patient record
            patient = RemotePatient(
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                gender=gender,
                occupation=occupation,
                other_occupation=other_occupation,
                phone=phone,
                osha_certificate=osha_certificate,
                date_of_osha_certification=date_of_osha_certification,
                insurance=insurance,
                insurance_company=insurance_company,
                other_insurance_company=other_insurance,
                insurance_number=insurance_number,
                emergency_contact_name=emergency_contact_name,
                emergency_contact_relation=emergency_contact_relation,
                other_emergency_contact_relation=other_relation,
                emergency_contact_phone=emergency_contact_phone,
                marital_status=marital_status,
                nationality_id=nationality_id,
                patient_type=patient_type,
                other_patient_type=other_patient_type,
                company_id=company_id,
                age=age,
                dob=dob
            )
            patient.save()
            return redirect(reverse('kahama_save_patient_health_information', args=[patient.id]))

        except Exception as e:
            # Handle the exception, you can log it or render an error message
            messages.error(request, f'Error adding Patient record : {str(e)}')
            return redirect(reverse('kahama_patient_info_form'))

    # If the request method is not POST, render the form template
    range_121 = range(0, 121)
    all_country = Country.objects.all()
    all_company = RemoteCompany.objects.all()
    
    # Populate context with initial values
    context = {
        'range_121': range_121,
        'all_country': all_country,
        'all_company': all_company, 
    }
    
    return render(request, 'kahama_template/add_remotePatients.html', context)



@login_required
def patients_list(request):
    patients =RemotePatient.objects.order_by('-created_at')    
    doctors = Staffs.objects.filter(role='doctor', work_place = 'kahama')
    return render(request, 'kahama_template/manage_remotepatients_list.html',
                  {
                      'patients': patients,
                      'doctors': doctors,
                      })

@login_required
def save_patient_visit_save(request, patient_id):
    try:
        # Attempt to retrieve the patient object
        patient = RemotePatient.objects.get(pk=patient_id) 
    except RemotePatient.DoesNotExist:
        # If the patient does not exist, handle the error appropriately
        messages.error(request, 'Patient does not exist.')
        return redirect(reverse('kahama_patient_info_form', args=[patient_id]))

    # Initialize latest_visit as None
    latest_visit = None

    try:
        # Attempt to retrieve the latest patient visit
        latest_visit = RemotePatientVisits.objects.filter(patient=patient).order_by("-created_at").first()
    except ObjectDoesNotExist:
        # If the visit does not exist, handle the error or notify the user
        messages.warning(request, 'No visit records found for this patient.')

    if request.method == 'POST':
        try:
            # Retrieve form data
            visit_type = request.POST.get('visit_type')
            primary_service = request.POST.get('primary_service')

            # Create or update the patient visit object
            if latest_visit:
                latest_visit.visit_type = visit_type
                latest_visit.primary_service = primary_service
                latest_visit.save()
                messages.success(request, 'Patient visit records updated successfully.')
            else:
                patient_visit = RemotePatientVisits.objects.create(
                    patient=patient,
                    visit_type=visit_type,
                    primary_service=primary_service
                )
                messages.success(request, 'Patient visit records added successfully.')

            return redirect(reverse('kahama_save_remotepatient_vitals', args=[patient_id, latest_visit.id if latest_visit else patient_visit.id]))

        except Exception as e:
            # Handle the exception, you can log it or render an error message
            messages.error(request, f'Error adding/updating patient visit records: {str(e)}')
            # Optionally, you can render an error message in the template
            return render(request, 'kahama_template/add_patient_visit.html', {'patient': patient, 'latest_visit': latest_visit})

    # If the request method is not POST, render the form template
    return render(request, 'kahama_template/add_patient_visit.html', {'patient': patient, 'latest_visit': latest_visit})


@login_required
def patient_info_form_edit(request, patient_id):    
    try:
        patient = RemotePatient.objects.get(pk=patient_id)    
    except RemotePatient.DoesNotExist:
        # Handle the case where the patient does not exist
        # For example, you can redirect to an error page or return an appropriate response
        return HttpResponse("Patient not found", status=404)
    
    if request.method == 'POST':
        try:
            # Extract data from POST request
            first_name = request.POST.get('first_name')
            middle_name = request.POST.get('middle_name')
            last_name = request.POST.get('last_name')
            first_name = first_name.capitalize() if first_name else None
            middle_name = middle_name.capitalize() if middle_name else None
            last_name = last_name.capitalize() if last_name else None
            gender = request.POST.get('gender')
            occupation = request.POST.get('occupation')
            other_occupation = request.POST.get('other_occupation')
            phone = request.POST.get('phone')           
            osha_certificate = request.POST.get('osha_certificate')
            date_of_osha_certification = request.POST.get('date_of_osha_certification')
            insurance = request.POST.get('insurance')
            insurance_company = request.POST.get('insurance_company')
            other_insurance = request.POST.get('other_insurance')
            insurance_number = request.POST.get('insurance_number')
            emergency_contact_name = request.POST.get('emergency_contact_name')
            emergency_contact_relation = request.POST.get('emergency_contact_relation')
            other_relation = request.POST.get('other_relation')
            emergency_contact_phone = request.POST.get('emergency_contact_phone')
            marital_status = request.POST.get('marital_status')
            nationality_id = request.POST.get('nationality')
            patient_type = request.POST.get('patient_type')
            other_patient_type = request.POST.get('other_patient_type')
            company_id = request.POST.get('company')
            age = request.POST.get('age')
            dob = request.POST.get('dob')          
            if dob:
                # Calculate age from dob
                try:
                    dob_date = datetime.strptime(dob, '%Y-%m-%d').date()  # Use datetime class from datetime module
                    current_date = datetime.today().date()  # Use datetime class from datetime module
                    age = current_date.year - dob_date.year - ((current_date.month, current_date.day) < (dob_date.month, dob_date.day))
                except ValueError:
                    age = None
                    
            elif age:
                # Calculate dob from age
                try:
                    age_int = int(age)
                    current_date = datetime.today().date()  # Use datetime class from datetime module
                    dob = current_date.replace(year=current_date.year - age_int)
                except ValueError:
                    dob = None           
             # Check if a patient with the same name already exists

            if date_of_osha_certification == '':
                date_of_osha_certification = None

            # Update patient object
            patient.first_name = first_name
            patient.middle_name = middle_name
            patient.last_name = last_name
            patient.gender = gender
            patient.age = age
            patient.dob = dob            
            patient.nationality_id = Country.objects.get(id=nationality_id)
            patient.phone = phone
            patient.osha_certificate = osha_certificate
            patient.date_of_osha_certification = date_of_osha_certification
            patient.insurance = insurance
            patient.insurance_company = insurance_company if insurance == 'Insured' else None
            patient.other_insurance_company = other_insurance if insurance_company == 'Other' else None
            patient.insurance_number = insurance_number if insurance == 'Insured' else None
            patient.emergency_contact_name = emergency_contact_name
            patient.emergency_contact_relation = emergency_contact_relation
            patient.other_emergency_contact_relation = other_relation  if emergency_contact_relation == 'Other' else None
            patient.emergency_contact_phone = emergency_contact_phone
            patient.marital_status = marital_status
            patient.occupation = occupation
            patient.other_occupation = other_occupation  if occupation == 'Other' else None
            patient.patient_type = patient_type           
            patient.other_patient_type = other_patient_type  if patient_type == 'Other' else None           
            patient.company_id = RemoteCompany.objects.get(id=company_id)
            patient.save()

            if 'save_back' in request.POST:
                # Redirect to the patients list view
                return redirect('kahama_patients_list')
            elif 'save_continue_health' in request.POST:
                # Redirect to continue editing health information
                return redirect(reverse('kahama_health_info_edit', args=[patient_id]))

        except Exception as e:
            # Handle any errors that may occur during form processing
            messages.error(request, f'Error editing Patient record: {str(e)}')
            return redirect(reverse('kahama_patient_info_form_edit', args=[patient_id]))

    # Render the template with patient data if available
    all_country = Country.objects.all()
    all_company = RemoteCompany.objects.all()
    range_121 = range(1, 121)
    return render(request, 'kahama_template/edit_remotepatient.html', {
        'patient': patient,
        'all_country': all_country,
        'all_company': all_company,
        'range_121': range_121,
    })

@login_required
def health_info_edit(request, patient_id):
    try:
        # Retrieve the patient object
        patient = get_object_or_404(RemotePatient, pk=patient_id)
        try:
            all_medicines = RemoteMedicine.objects.all()
        except RemoteMedicine.DoesNotExist:
            # Handle the case where no medicines are found
            all_medicines = []
       # Retrieve existing health records for the patient
        try:
            patient_health_records = PatientHealthCondition.objects.filter(patient_id=patient_id)
        except PatientHealthCondition.DoesNotExist:
            patient_health_records = None
        
        try:
            medication_allergies = PatientMedicationAllergy.objects.filter(patient_id=patient_id)
        except PatientMedicationAllergy.DoesNotExist:
            medication_allergies = None
        
        try:
            surgery_history = PatientSurgery.objects.filter(patient_id=patient_id)
        except PatientSurgery.DoesNotExist:
            surgery_history = None
        
        try:
            lifestyle_behavior = PatientLifestyleBehavior.objects.get(patient_id=patient_id)
        except PatientLifestyleBehavior.DoesNotExist:
            lifestyle_behavior = None
        
        try:
            family_medical_history = FamilyMedicalHistory.objects.filter(patient=patient)
        except FamilyMedicalHistory.DoesNotExist:
            family_medical_history = None
        
        context = {
            'patient': patient,
            'patient_health_records': patient_health_records,
            'medication_allergies': medication_allergies,
            'lifestyle_behavior': lifestyle_behavior,
            'family_medical_history': family_medical_history,
            'surgery_history': surgery_history,
            'all_medicines': all_medicines,
        }
        
        if request.method == 'POST':
            
            if lifestyle_behavior:
                lifestyle_behavior.smoking = request.POST.get('smoking')
                lifestyle_behavior.alcohol_consumption = request.POST.get('alcohol_consumption')
                lifestyle_behavior.weekly_exercise_frequency = request.POST.get('weekly_exercise_frequency')
                lifestyle_behavior.healthy_diet = request.POST.get('healthy_diet')
                lifestyle_behavior.stress_management = request.POST.get('stress_management')
                lifestyle_behavior.sufficient_sleep = request.POST.get('sufficient_sleep')
                lifestyle_behavior.save()
            else:
              # Create a new instance of PatientLifestyleBehavior
                    lifestyle_behavior = PatientLifestyleBehavior(
                        patient_id=patient_id,
                        smoking=request.POST.get('smoking'),
                        alcohol_consumption=request.POST.get('alcohol_consumption'),
                        weekly_exercise_frequency=request.POST.get('weekly_exercise_frequency'),
                        healthy_diet=request.POST.get('healthy_diet'),
                        stress_management=request.POST.get('stress_management'),
                        sufficient_sleep=request.POST.get('sufficient_sleep')
                    )
                    lifestyle_behavior.save()
            # Update or add family medical history records
            for record in family_medical_history:
                record_id = str(record.id)
                condition = request.POST.get('condition_' + record_id)
                relationship = request.POST.get('relationship_' + record_id)
                comments = request.POST.get('comments_' + record_id)
                
                # Update existing record
                record.condition = condition
                record.relationship = relationship
                record.comments = comments
                record.save()
                
            if 'new_condition[]' in request.POST:
                new_conditions = request.POST.getlist('new_condition[]')
                new_relationships = request.POST.getlist('new_relationship[]')
                new_comments = request.POST.getlist('new_comments[]')
                
                # Create new family medical history records
                for condition, relationship, comments in zip(new_conditions, new_relationships, new_comments):
                    new_record = FamilyMedicalHistory(patient=patient, condition=condition, relationship=relationship, comments=comments)
                    new_record.save()
                
            # Handle chronic illness option for family medical history
            if request.POST.get('family_medical_history') == 'no':
                patient.remote_family_medical_history.all().delete()
                
            # Update or add medication allergies
            for allergy in medication_allergies:
                allergy_id = str(allergy.id)
                medicine_name = request.POST.get('medicine_name_' + allergy_id)
                reaction = request.POST.get('reaction_' + allergy_id)
                
                # Update existing record
                if medicine_name is not None:
                    medicine_name_id = RemoteMedicine.objects.get(id=medicine_name) 
                    allergy.medicine_name_id = medicine_name_id.id
                if reaction is not None:
                    allergy.reaction = reaction
                allergy.save()
                
            if 'new_medicine_name[]' in request.POST:
                new_medicine_names = request.POST.getlist('new_medicine_name[]')
                new_reactions = request.POST.getlist('new_reaction[]')
                
                # Create new medication allergy records
                for medicine_name, reaction in zip(new_medicine_names, new_reactions):
                    medicine_name_id = RemoteMedicine.objects.get(id=medicine_name)  
                    new_allergy = PatientMedicationAllergy(patient=patient, medicine_name_id=medicine_name_id.id, reaction=reaction)
                    new_allergy.save()
                
            # Handle chronic illness option for medication allergies
            if request.POST.get('medication_allergy') == 'no':
                patient.remote_medication_allergies.all().delete()
                
            # Update or add surgery history records
            for surgery in surgery_history:
                surgery_id = str(surgery.id)
                surgery_name = request.POST.get('surgery_name_' + surgery_id)
                date_of_surgery = request.POST.get('date_of_surgery_' + surgery_id)
                
                # Update existing record
                if surgery_name is not None:
                    surgery.surgery_name = surgery_name
                if date_of_surgery is not None:
                    surgery.surgery_date = date_of_surgery
                surgery.save()
                
            if 'new_surgery_name[]' in request.POST:
                new_surgery_names = request.POST.getlist('new_surgery_name[]')
                new_dates_of_surgery = request.POST.getlist('new_date_of_surgery[]')
                
                # Create new surgery history records
                for name, date in zip(new_surgery_names, new_dates_of_surgery):
                    new_surgery = PatientSurgery(patient=patient, surgery_name=name, surgery_date=date)
                    new_surgery.save()
                
            # Handle chronic illness option for surgery history
            if request.POST.get('surgery_history') == 'no':
                patient.remote_patient_surgery.all().delete()
                
            # Update or add health records
            for record in patient_health_records:
                record_id = str(record.id)
                health_condition = request.POST.get('health_condition_' + record_id)
                health_condition_notes = request.POST.get('health_condition_notes_' + record_id)
                
                # Update existing record
                if health_condition is not None:
                    record.health_condition = health_condition
                if health_condition_notes is not None:
                    record.health_condition_notes = health_condition_notes
                record.save()
                
            if 'new_health_condition[]' in request.POST:
                new_health_conditions = request.POST.getlist('new_health_condition[]')
                new_health_condition_notes = request.POST.getlist('new_health_condition_notes[]')
                
                # Create new health records
                for condition, notes in zip(new_health_conditions, new_health_condition_notes):
                    new_record = PatientHealthCondition(patient=patient, health_condition=condition, health_condition_notes=notes)
                    new_record.save()
                
                messages.success(request, f'{len(new_health_conditions)} new health records added successfully.')
                
            # Handle chronic illness option for patient health conditions
            if request.POST.get('chronic_illness') == 'no':
                patient.remote_health_conditions.all().delete()
                
            # Redirect to appropriate view after successful update
            if 'save_and_return' in request.POST:
                return redirect('kahama_patients_list')
            elif 'save_and_continue_family_health' in request.POST:
                return redirect(reverse('kahama_save_patient_visit_save', args=[patient_id]))
        
        # Render the template with the prepared context
        return render(request, 'kahama_template/edit_patient_health_condition_form.html', context)
    
    except Exception as e:
        # Handle any exceptions and display error messages
        messages.error(request, f'Error editing patient health record: {str(e)}')
        
        # If an exception occurs, still render the template with available context
        return render(request, 'kahama_template/edit_patient_health_condition_form.html', context)




@login_required
def remoteservice_list(request):
    # Retrieve all services from the database
    services = RemoteService.objects.all()
    return render(request, 'kahama_template/service_list.html', {'services': services})


@login_required
@csrf_exempt
@require_POST
def save_remote_service(request):
    try:
        # Extract data from the request
        service_id = request.POST.get('service_id')
        name = request.POST.get('name').strip()
        description = request.POST.get('description')
        category = request.POST.get('category')

        if service_id:
            # Editing existing remote service
            service = RemoteService.objects.get(pk=service_id)
            
            # Check for duplicate name excluding the current record
            if RemoteService.objects.exclude(pk=service_id).filter(name=name).exists():
                return JsonResponse({'success': False, 'message': f'A service with the name "{name}" already exists.'})
            
            # Update the existing service
            service.name = name
            service.description = description
            service.category = category
            service.save()
            
            return JsonResponse({'success': True, 'message': 'Updated successfully'})
        else:
            # Creating new remote service
            # Check for duplicate name
            if RemoteService.objects.filter(name=name).exists():
                return JsonResponse({'success': False, 'message': f'A service with the name "{name}" already exists.'})
            
            # Create a new service
            service = RemoteService(name=name, description=description, category=category)
            service.save()
            
            return JsonResponse({'success': True, 'message': 'Added successfully'})
    except RemoteService.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Service not found.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
   

    
@require_POST
def add_remote_consultation(request):
    if request.method == 'POST':
        try:
            # Retrieve data from the POST request
            doctor_id = request.POST.get('doctor')
            patient_id = request.POST.get('patient_id')
            description = request.POST.get('description')
            date_of_consultation = request.POST.get('date_of_consultation')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')

            # Ensure date_of_consultation is greater than the current date
            if timezone.now().date() >= timezone.datetime.strptime(date_of_consultation, "%Y-%m-%d").date():
                return JsonResponse({'status': 'error', 'message': 'Consultation date must be greater than the current date'})

            patient = RemotePatient.objects.get(id=patient_id)
            doctor = Staffs.objects.get(id=doctor_id)

            # Validate the time inputs
            if not validate_time(start_time, end_time):
                return JsonResponse({'status': 'error', 'message': 'End time must be greater than start time'})

            # Create a new consultation object in the database
            consultation = RemoteConsultation(
                doctor=doctor,
                patient=patient,
                description=description,
                appointment_date=date_of_consultation,
                start_time=start_time,
                end_time=end_time
            )
            consultation.save()

            # Return a JSON response indicating success
            return JsonResponse({'status': 'success', 'message': 'Consultation added successfully'})
        except Exception as e:
            # If an exception occurs, return a JSON response with an error message
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        # If the request method is not POST, return a JSON response with an error message
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def validate_time(start_time, end_time):
    # Validate that end time is greater than start time
    return start_time < end_time

@login_required
def generatePDF(request, patient_id, visit_id):
    pass


@require_POST
def save_consultation_data(request):
    try:
        # Retrieve data from the form
        doctor_id = request.POST.get('doctor')
        patient_id = request.POST.get('patient')
        appointment_date = request.POST.get('appointmentDate')
        start_time = request.POST.get('startTime')
        end_time = request.POST.get('endTime')
        description = request.POST.get('description')        
        pathodology_record_id = request.POST.get('pathodologyRecord')        
        # Create or update Consultation object
        consultation, created = RemoteConsultation.objects.update_or_create(
            doctor=Staffs.objects.get(id=doctor_id),
            patient=RemotePatient.objects.get(id=patient_id),
            appointment_date=appointment_date,
            start_time=start_time,
            end_time=end_time,
            description=description,
            pathodology_record= PathodologyRecord.objects.get(id=pathodology_record_id),
            
        )
        return redirect('kahama_appointment_list')
    except Exception as e:
        return HttpResponseBadRequest(f"Error: {str(e)}")
    
def counseling_list_view(request):
    counselings = RemoteCounseling.objects.all().order_by('-created_at')
    return render(request, 'kahama_template/manage_counselling.html', {'counselings': counselings})    

def observation_record_list_view(request):
    observation_records = RemoteObservationRecord.objects.all().order_by('-created_at')
    return render(request, 'kahama_template/manage_observation_record.html', {'observation_records': observation_records})

def discharge_notes_list_view(request):
    discharge_notes = RemoteDischargesNotes.objects.all().order_by('-discharge_date')
    return render(request, 'kahama_template/manage_discharge.html', {'discharge_notes': discharge_notes})