import calendar
from datetime import  datetime
import json
from django.utils import timezone
import logging
from kahamahmis.forms import RemoteLaboratoryOrderForm, RemoteProcedureForm
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
from clinic.models import ChiefComplaint, ClinicCompany, Diagnosis,   FamilyMedicalHistory, Country, CustomUser, DiseaseRecode, HealthRecord,  InsuranceCompany, Medicine, PathodologyRecord, PatientHealthCondition, PatientLifestyleBehavior, PatientMedicationAllergy, PatientSurgery, PrescriptionFrequency, PrimaryPhysicalExamination, Referral,  RemoteCompany, RemoteConsultation, RemoteConsultationNotes, RemoteCounseling, RemoteDischargesNotes, RemoteEquipment, RemoteLaboratoryOrder, RemoteMedicine, RemoteObservationRecord, RemotePatient, RemotePatientDiagnosisRecord, RemotePatientVisits, RemotePatientVital, RemotePrescription, RemoteProcedure, RemoteReagent, RemoteReferral, RemoteService, SecondaryPhysicalExamination, Service,Staffs
from django.template.loader import render_to_string
from django.db.models import Sum, Max, Count,Q
from django.views.decorators.http import require_POST
from django.db.models import OuterRef, Subquery
from django.db.models.functions import ExtractMonth ,TruncDay
from calendar import monthrange
from datetime import date, timedelta



@login_required
def divine_dashboard(request):
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
    return render(request,"divine_admin_template/home_content.html",context)


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
def manage_country(request):
    countries=Country.objects.all() 
    return render(request,"divine_admin_template/manage_country.html", {"countries":countries})



@login_required
def manage_company(request):
    companies=RemoteCompany.objects.all() 
    return render(request,"divine_admin_template/manage_company.html",{"companies":companies})

@login_required
def manage_disease(request):
    disease_records=DiseaseRecode.objects.all() 
    return render(request,"divine_admin_template/manage_disease.html",{"disease_records":disease_records})

@login_required
def manage_staff(request):     
    staffs=Staffs.objects.all()  
    return render(request,"divine_admin_template/manage_staff.html",{"staffs":staffs})  

@login_required
def manage_insurance(request):
    insurance_companies=InsuranceCompany.objects.all() 
    return render(request,"divine_admin_template/manage_insurance.html",{"insurance_companies":insurance_companies})

@login_required
def resa_report(request):
    return render(request,"divine_admin_template/resa_reports.html")



def manage_adjustment(request):
    return render(request,"divine_admin_template/manage_adjustment.html")

@login_required
def reports_adjustments(request):
    return render(request,"divine_admin_template/reports_adjustments.html")


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
    return render(request, 'divine_admin_template/reports_by_visit.html', context)

@login_required
def reports_comprehensive(request):
    return render(request,"divine_admin_template/reports_comprehensive.html")

@login_required
def reports_patients_visit_summary(request):
    visits = RemotePatientVisits.objects.all()
    context = {'visits':visits}
    return render(request,"divine_admin_template/reports_patients_visit_summary.html",context)

@login_required
def reports_patients(request):
    patients_report = RemotePatient.objects.order_by('-created_at') 
    context = {'patients':patients_report}
    return render(request,"divine_admin_template/reports_patients.html",context)



@login_required
def reports_service(request):
    return render(request,"divine_admin_template/reports_service.html")

@login_required
def reports_stock_ledger(request):
    return render(request,"divine_admin_template/reports_stock_ledger.html")

def reports_stock_level(request):
    return render(request,"divine_admin_template/reports_stock_level.html")

@login_required
def reports_orders(request):
    return render(request,"divine_admin_template/reports_orders.html")

@login_required
def individual_visit(request, patient_id):
    # Retrieve the RemotePatient instance
    patient = get_object_or_404(RemotePatient, id=patient_id)
    
    # Retrieve all visits of the patient and order them by created_at
    patient_visits = RemotePatientVisits.objects.filter(patient=patient).order_by('-created_at')

    context = {'patient': patient, 'patient_visits': patient_visits}
    return render(request, 'divine_admin_template/reports_individual_visit.html', context)
    

@login_required
def product_summary(request):
    return render(request,"divine_admin_template/product_summary.html")

@login_required
def manage_pathodology(request):
    pathodology_records=PathodologyRecord.objects.all()     
    return render(request,"divine_admin_template/manage_pathodology.html",{
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
    

@login_required
def edit_staff(request, staff_id):
    # Check if the staff with the given ID exists, or return a 404 page
    staff = get_object_or_404(Staffs, id=staff_id)  
    # If staff exists, proceed with the rest of the view
    request.session['staff_id'] = staff_id
    return render(request, "divine_admin_template/edit_staff.html", {"id": staff_id, "username": staff.admin.username, "staff": staff})   


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

       
            messages.success(request, "")
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

    return render(request, "divine_admin_template/staff_details.html", context)



@login_required
def patient_procedure_view(request):
    # Retrieve distinct patient and visit combinations from RemoteProcedure
    patient_procedures = (
        RemoteProcedure.objects.values('patient__mrn', 'visit__vst',
                                       'doctor__admin__first_name',
                                          'doctor__middle_name',
                                          'doctor__role',
                                          'doctor__admin__first_name',
                                       )  # Group by patient MRN and visit number
        .annotate(
            latest_date=Max('created_at'),  # Get the latest procedure date for each patient and visit
            procedure_name=Subquery(
                RemoteProcedure.objects.filter(
                    patient__mrn=OuterRef('patient__mrn'),  # Match patient MRN
                    visit__vst=OuterRef('visit__vst')       # Match visit number
                )
                .order_by('-created_at')  # Order by most recent procedure
                .values('name__name')[:1]  # Retrieve the latest procedure name
            )
        )
        .order_by('-latest_date')  # Order by the latest procedure date
    )

    context = {
        'patient_procedures': patient_procedures,
    }
    return render(request, 'divine_admin_template/manage_procedure.html', context)

@login_required
def patient_procedure_detail_view(request, mrn, visit_number):
    # Retrieve the patient based on MRN
    patient = get_object_or_404(RemotePatient, mrn=mrn)

    # Retrieve the visit based on visit_number for the specific patient
    visit = get_object_or_404(RemotePatientVisits, vst=visit_number)

    # Retrieve the corresponding procedure for the patient and visit
    procedure =RemoteProcedure.objects.filter(patient=patient, visit = visit)

    context = {
        'patient': patient,
        'visit': visit,
        'procedure': procedure,
    }

    return render(request, 'divine_admin_template/manage_procedure_detail_view.html', context)


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

    return render(request, 'divine_admin_template/manage_patient_procedure.html', context)




@login_required
def manage_referral(request):
    referrals = RemoteReferral.objects.all()
    patients = RemotePatient.objects.all()
    return render(request, 'divine_admin_template/manage_referral.html', {'referrals': referrals,'patients':patients})



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
    return render(request, 'divine_admin_template/manage_appointment.html', context)



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
                    disease.data_recorder=request.user.staff 
                    disease.disease_name = disease_name
                    disease.code = code
                    disease.save()
                    return JsonResponse({'success': True, 'message': 'Disease divine_admin_templated successfully'})
                else:
                    return JsonResponse({'success': False, 'message': 'Disease does not exist'})

            # Check if the disease already exists
            if DiseaseRecode.objects.filter(disease_name=disease_name).exists():
                return JsonResponse({'success': False, 'message': 'Another disease with the same name already exists'})            
            if DiseaseRecode.objects.filter(code=code).exists():
                return JsonResponse({'success': False, 'message': 'Another disease with the same code already exists'})

            # Save data to the model for new disease
            DiseaseRecode.objects.create(disease_name=disease_name, data_recorder=request.user.staff , code=code)
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
                    insurance_company.data_recorder=request.user.staff 
                    insurance_company.phone = phone
                    insurance_company.short_name = short_name
                    insurance_company.email = email
                    insurance_company.address = address
                    insurance_company.website = website
                    insurance_company.save()
                    return JsonResponse({'success': True, 'message': 'Insurance company divine_admin_templated successfully'})
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
                    data_recorder=request.user.staff ,
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
                company.data_recorder=request.user.staff 
                company.Founded = Founded
                company.Notes = Notes
                company.save()

                return JsonResponse({'success': True, 'message': 'Company divine_admin_templated successfully'})
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
                    data_recorder=request.user.staff ,
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
                pathology_record.data_recorder=request.user.staff 
                pathology_record.name = name
                pathology_record.description = description
                pathology_record.save()
                return JsonResponse({'success': True, 'message': 'Patholody divine_admin_templated successfully'})
            else:  # If no pathology record ID is provided, it's an add operation
                # Check if the provided name already exists in the database
                if PathodologyRecord.objects.filter(name=name).exists():
                    return JsonResponse({'success': False, 'message':  f'A pathology record with the name "{name}" already exists'})

                # Save data to the model for a new pathology record
                pathodology_record = PathodologyRecord.objects.create(
                    name=name,
                    data_recorder=request.user.staff ,
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
        return render(request, 'divine_admin_template/manage_out_of_stock_medicines.html', {'out_of_stock_medicines': out_of_stock_medicines})
    
    except Exception as e:
        # Handle any errors and return an error response
        return render(request, '404.html', {'error_message': str(e)}) 


    
@login_required    
def in_stock_medicines_view(request):
    # Retrieve medicines with inventory levels above zero
    in_stock_medicines = Medicine.objects.filter(remain_quantity__gt=0)

    return render(request, 'divine_admin_template/manage_in_stock_medicines.html', {'in_stock_medicines': in_stock_medicines})  



@login_required
def patient_visit_history_view(request, patient_id):
    # Retrieve visit history for the specified patient
    visit_history = RemotePatientVisits.objects.filter(patient_id=patient_id)
    current_date = timezone.now().date()
    doctors = Staffs.objects.filter(role='doctor', work_place = 'kahama')
    patient = RemotePatient.objects.get(id=patient_id)   
    return render(request, 'divine_admin_template/manage_patient_visit_history.html', {
        'visit_history': visit_history,
        'patient':patient,        
        'doctors': doctors,
        })


   
    
@login_required
def patient_visit_details_view(request, patient_id, visit_id):
    try:        
        visit = RemotePatientVisits.objects.get(id=visit_id)
        prescriptions = RemotePrescription.objects.filter(patient=patient_id, visit=visit_id)
        chief_complaints = ChiefComplaint.objects.filter(patient_id=patient_id, visit_id=visit_id)
        primary_physical_examination = PrimaryPhysicalExamination.objects.filter(patient_id=patient_id, visit_id=visit_id).first()
        secondary_physical_examination = SecondaryPhysicalExamination.objects.filter(patient=patient_id, visit=visit_id).first()
        consultation_notes = RemoteConsultationNotes.objects.get(patient_id=patient_id, visit=visit_id)  
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

        return render(request, 'divine_admin_template/manage_patient_visit_detail_record.html', context)
    except RemotePatient.DoesNotExist:
        raise Http404("Patient does not exist")
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)})    
    

    

@login_required
def prescription_list(request):
    # Retrieve all prescriptions with related patient and visit
    prescriptions = RemotePrescription.objects.select_related('visit__patient').all()

    # Initialize a dictionary to store visit-wise data
    visit_data = {}

    # Iterate through prescriptions to group by visit
    for prescription in prescriptions:
        visit_id = prescription.visit_id

        # Check if visit_id already exists in visit_data
        if visit_id in visit_data:
            visit_data[visit_id]['prescriptions'].append({
                'medicine_name': prescription.medicine.drug_name,
                'frequency_name': prescription.frequency.name,
                'duration': prescription.duration,
                'quantity': prescription.quantity_used,
                'dose': prescription.dose,
            })
        else:
            # Add new entry for the visit_id
            visit_data[visit_id] = {
                'visit_id': visit_id,
                'visit_number': prescription.visit.vst,  # Include visit number
                'patient_name': f"{prescription.visit.patient.first_name} {prescription.visit.patient.last_name}",
                'created_at': prescription.visit.created_at,
                'patient_id': prescription.visit.patient_id,
                'middle_name': prescription.visit.patient.middle_name,
                'prescriptions': [{
                    'medicine_name': prescription.medicine.drug_name,
                    'frequency_name': prescription.frequency.name,
                    'duration': prescription.duration,
                    'quantity': prescription.quantity_used,
                    'dose': prescription.dose,
                }],
            }

    # Convert dictionary values to list for template rendering
    visit_data_list = list(visit_data.values())

    return render(request, 'divine_admin_template/manage_prescription_list.html', {
        'visit_data': visit_data_list,
    })


@login_required
def prescription_notes(request, visit_id, patient_id):
    patient = RemotePatient.objects.get(id=patient_id)
    visit = RemotePatientVisits.objects.get(id=visit_id)
    prescriptions = RemotePrescription.objects.filter(visit__id=visit_id, visit__patient__id=patient_id)
    prescriber = None
    if prescriptions.exists():
        prescriber = prescriptions.first().entered_by
    context = {
        'patient': patient,
        'prescriptions': prescriptions,
        'prescriber': prescriber,
        'visit_number': visit.vst,
        'visit': visit,
    }
    return render(request, "divine_admin_template/prescription_notes.html", context)




@login_required
def patient_vital_all_list(request):
    # Retrieve distinct patient and visit combinations
    patient_vitals = (
        RemotePatientVital.objects.values('patient__mrn', 'visit__vst',
                                          'doctor__admin__first_name',
                                          'doctor__middle_name',
                                          'doctor__role',
                                          'doctor__admin__first_name')
        .annotate(
            latest_date=Max('recorded_at')  # Get the latest record date for each patient and visit
        )
        .order_by('-latest_date')
    )
    
    context = {      
        'patient_vitals': patient_vitals,
    }
    return render(request, 'divine_admin_template/manage_all_patient_vital.html', context) 

@login_required
def patient_vital_detail(request, patient_mrn, visit_number):
    # Fetch all vitals for the specific patient and visit
    patient = RemotePatient.objects.get(mrn=patient_mrn)
    vitals = RemotePatientVital.objects.filter(patient__mrn=patient_mrn, visit__vst=visit_number)
    
    context = {
        'vitals': vitals,
        'patient': patient,
        'patient_mrn': patient_mrn,
        'visit_number': visit_number,
    }
    return render(request, 'divine_admin_template/manage_patient_vital_list.html', context)


    
@login_required
def save_remotepatient_vitals(request, patient_id, visit_id):
    try:
        # Retrieve the patient and visit objects
        patient = RemotePatient.objects.get(pk=patient_id)
        visit = RemotePatientVisits.objects.get(patient=patient, id=visit_id)

        # Prepare ranges for context
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

        # Retrieve the existing vital record, if any, for this patient and visit
        existing_vital = RemotePatientVital.objects.filter(patient=patient, visit=visit).last()

        if existing_vital:
            # Include existing vital in the context if it exists
            context['existing_vital'] = existing_vital

        # Render the template with the patient, visit, and any existing vital data
        return render(request, 'divine_admin_template/add_remotepatient_vital.html', context)

    except Exception as e:
        # Handle any other exceptions and display an error message
        messages.error(request, f'Error retrieving patient vital information: {str(e)}')
        return render(request, 'divine_admin_template/add_remotepatient_vital.html', context)

    
@login_required        
def consultation_notes_view(request):
    consultation_notes = RemoteConsultationNotes.objects.all() 
    return render(request, 'divine_admin_template/manage_consultation_notes.html', {
        'consultation_notes': consultation_notes,       
        })    


def diagnosis_list(request):
    diagnoses = Diagnosis.objects.all().order_by('-created_at')    
    return render(request, 'divine_admin_template/manage_diagnosis_list.html', {'diagnoses': diagnoses}) 


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
            diagnosis.data_recorder  = request.user.staff 
            diagnosis.diagnosis_name = diagnosis_name
            diagnosis.diagnosis_code = diagnosis_code
            diagnosis.save()
            return JsonResponse({'success': True, 'message': 'Diagnosis divine_admin_templated successfully.'})
        else:
            # Adding new diagnosis
            # Check for uniqueness
            if Diagnosis.objects.filter(diagnosis_name=diagnosis_name).exists():
                return JsonResponse({'success': False, 'message': 'Diagnosis with this name already exists.'})
            if Diagnosis.objects.filter(diagnosis_code=diagnosis_code).exists():
                return JsonResponse({'success': False, 'message': 'Diagnosis with this code already exists.'})

            # Create new diagnosis
            diagnosis = Diagnosis.objects.create(diagnosis_name=diagnosis_name,
                                                 data_recorder=request.user.staff ,
                                                 diagnosis_code=diagnosis_code,
                                                 )
            return JsonResponse({'success': True, 'message': 'Diagnosis added successfully.'})

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})



@login_required
def patients_list(request):
    patients =RemotePatient.objects.order_by('-created_at')    
    doctors = Staffs.objects.filter(role='doctor', work_place = 'kahama')
    return render(request, 'divine_admin_template/manage_remotepatients_list.html',
                  {
                      'patients': patients,
                      'doctors': doctors,
                      })

@login_required
def save_patient_visit_save(request, patient_id, visit_id=None):
    # Retrieve the patient object or handle the error if it does not exist
    patient = get_object_or_404(RemotePatient, pk=patient_id)

    # Retrieve the visit object if editing an existing visit
    if visit_id:
        visit = get_object_or_404(RemotePatientVisits, pk=visit_id)
    else:
        visit = None

    # Render the template with patient and visit data (no POST request handling)
    return render(request, 'divine_admin_template/add_patient_visit.html', {
        'patient': patient,
        'visit': visit,
    })



@login_required
def patient_info_form_edit(request, patient_id):    
    try:
        # Retrieve the patient object
        patient = RemotePatient.objects.get(pk=patient_id)    
    except RemotePatient.DoesNotExist:
        # Handle the case where the patient does not exist
        return HttpResponse("Patient not found", status=404)

    # Retrieve necessary data for the form (no POST request handling)
    all_country = Country.objects.all()
    all_company = RemoteCompany.objects.all()
    range_121 = range(1, 121)

    # Render the template with the patient data and additional required data
    return render(request, 'divine_admin_template/edit_remotepatient.html', {
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
        
        # Render the template with the prepared context
        return render(request, 'divine_admin_template/edit_patient_health_condition_form.html', context)
    
    except Exception as e:
        # Handle any exceptions and display error messages
        messages.error(request, f'Error retrieving patient health records: {str(e)}')
        
        # If an exception occurs, still render the template with available context
        return render(request, 'divine_admin_template/edit_patient_health_condition_form.html', context)



@login_required
def remoteservice_list(request):
    # Retrieve all services from the database
    services = RemoteService.objects.all()
    return render(request, 'divine_admin_template/service_list.html', {'services': services})


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
        data_recorder=request.user.staff 
        if service_id:
            # Editing existing remote service
            service = RemoteService.objects.get(pk=service_id)
            
            # Check for duplicate name excluding the current record
            if RemoteService.objects.exclude(pk=service_id).filter(name=name, data_recorder=data_recorder).exists():
                return JsonResponse({'success': False, 'message': f'A service with the name "{name}" already exists.'})
            
            # Update the existing service
            service.data_recorder=data_recorder
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
   

@login_required
def generatePDF(request, patient_id, visit_id):
    pass


def counseling_list_view(request):
    counselings = RemoteCounseling.objects.all().order_by('-created_at')
    return render(request, 'divine_admin_template/manage_counselling.html', {'counselings': counselings})    

def observation_record_list_view(request):
    observation_records = RemoteObservationRecord.objects.all().order_by('-created_at')
    return render(request, 'divine_admin_template/manage_observation_record.html', {'observation_records': observation_records})

def discharge_notes_list_view(request):
    discharge_notes = RemoteDischargesNotes.objects.all().order_by('-discharge_date')
    return render(request, 'divine_admin_template/manage_discharge.html', {'discharge_notes': discharge_notes})




@login_required
def health_record_list(request):
    records = HealthRecord.objects.all()
    return render(request, 'divine_admin_template/healthrecord_list.html', {'records': records})

@login_required
@csrf_exempt
def save_health_record(request):
    if request.method == 'POST':
        try:
            # Extract data from POST request
            name = request.POST.get('name').strip()
            health_record_id = request.POST.get('health_record_id')
            
            if health_record_id:  # If health record ID is provided, it's an edit operation
                # Get the existing health record object
                health_record = HealthRecord.objects.get(pk=health_record_id)
                
                # Check if the provided name already exists in the database
                if HealthRecord.objects.exclude(pk=health_record_id).filter(name=name).exists():
                    return JsonResponse({'success': False, 'message': f'A record with the name "{name}" already exists.'})
                
                # Update the existing health record
                health_record.name = name
                health_record.data_recorder=request.user.staff 
                health_record.save()
            else:  # If no health record ID is provided, it's an add operation
                # Check if the provided name already exists in the database
                if HealthRecord.objects.filter(name=name).exists():
                    return JsonResponse({'success': False, 'message': f'A record with the name "{name}" already exists.'})
                
                # Create a new health record
                HealthRecord.objects.create(name=name, 
                                            data_recorder=request.user.staff )
            
            # Return success response
            return JsonResponse({'success': True, 'message': 'Successfully saved.'})
        except Exception as e:
            # Return error response if an exception occurs
            return JsonResponse({'success': False, 'message': str(e)})
    else:
        # Return error response for invalid requests
        return JsonResponse({'success': False, 'message': 'Invalid request'})


        
    
@csrf_exempt  # Use csrf_exempt decorator for simplicity in this example. For a production scenario, consider using csrf protection.
def delete_healthrecord(request):
    if request.method == 'POST':
        try:
            health_record_id = request.POST.get('health_record_id')

            # Delete procedure record
            health_record = get_object_or_404(HealthRecord, pk=health_record_id)
            health_record.delete()

            return JsonResponse({'success': True, 'message': f'health_record record for {health_record.name} deleted successfully.'})
        except HealthRecord.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid health_record ID.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {e}'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})
    

  
@login_required
def fetch_existing_data(request):
    try:
        # Extract patient_id and visit_id from the request parameters
        patient_id = request.GET.get('patient_id')
        visit_id = request.GET.get('visit_id')

        # Query the database to fetch existing chief complaints based on patient_id and visit_id
        existing_data = ChiefComplaint.objects.filter(patient_id=patient_id, visit_id=visit_id).values()
        
        # Create a list to hold the modified data with unified information
        modified_data = []

        # Iterate through each entry in the existing data
        for entry in existing_data:
            # Determine the information to display based on whether the health record is null or not
            display_info = None
            if entry['health_record_id'] is not None:
                try:
                    health_record = HealthRecord.objects.get(pk=entry['health_record_id'])
                    display_info = health_record.name
                except ObjectDoesNotExist:
                    # Handle the case where the HealthRecord object does not exist
                    display_info = "Unknown Health Record"
            else:
                # Use the "other complaint" field if health record is null
                display_info = entry['other_complaint'] if entry['other_complaint'] else "Unknown"
        
            # Create a modified entry with unified information under the 'health_record' key
            modified_entry = {
                'id': entry['id'],
                'patient_id': entry['patient_id'],
                'visit_id': entry['visit_id'],
                'health_record': display_info,
                'health_record_id': health_record.id,
                'duration': entry['duration'],
                'created_at': entry['created_at'],
                'updated_at': entry['updated_at']
            }

            # Add the modified entry to the list
            modified_data.append(modified_entry)

        # Return the modified data as a JSON response
        return JsonResponse(modified_data, safe=False)
    
    except Exception as e:
        # If an error occurs, return an error response with status code 500
        return JsonResponse({'error': str(e)}, status=500)
    

@csrf_exempt
def delete_chief_complaint(request, chief_complaint_id):
    try:
        # Fetch the ChiefComplaint object to delete
        chief_complaint = get_object_or_404(ChiefComplaint, id=chief_complaint_id)
        
        # Delete the ChiefComplaint
        chief_complaint.delete()
        
        # Return a success response
        return JsonResponse({'message': 'Chief complaint deleted successfully'})
    except Exception as e:
        # If an error occurs, return an error response
        return JsonResponse({'error': str(e)}, status=500)   
    

     
@login_required
def save_remotesconsultation_notes(request, patient_id, visit_id):
    doctor = request.user.staff
    patient = get_object_or_404(RemotePatient, pk=patient_id)
    visit = get_object_or_404(RemotePatientVisits, patient=patient_id, id=visit_id)
    
    # Initialize context variables
    context = {
        'secondary_examination': None,
        'previous_counselings': None,
        'previous_discharges': None,
        'previous_observations': None,
        'previous_lab_orders': None,
        'previous_prescriptions': None,
        'previous_referrals': None,
        'previous_procedures': None,
        'primary_examination': None,
        'provisional_record': None,
        'health_records': None,
        'pathology_records': None,
        'health_conditions': None,
        'surgery_info': None,
        'provisional_diagnoses': None,
        'final_provisional_diagnosis': None,
        'provisional_diagnosis_ids': None,
        'family_history': None,
        'behaviors': None,
        'allergies': None,
        'patient': patient,
        'visit': visit,
        'patient_vitals': None,
        'patient_surgeries': None,
        'consultation_note': None,
    }

    try:
        # Query for various records associated with the patient and visit
        health_conditions = PatientHealthCondition.objects.filter(patient_id=patient_id)
        surgery_info = PatientSurgery.objects.filter(patient_id=patient_id)
        family_history = FamilyMedicalHistory.objects.filter(patient_id=patient_id)
        allergies = PatientMedicationAllergy.objects.filter(patient_id=patient_id)
        behaviors = PatientLifestyleBehavior.objects.get(patient_id=patient_id)
        patient_vitals = RemotePatientVital.objects.filter(patient=patient_id, visit=visit)
        health_records = HealthRecord.objects.all()
        patient_surgeries = PatientSurgery.objects.filter(patient=patient_id)

        # Other related data retrievals
        provisional_diagnoses = Diagnosis.objects.all()
        consultation_note = RemoteConsultationNotes.objects.filter(patient=patient_id, visit=visit).first()
        provisional_record, created = RemotePatientDiagnosisRecord.objects.get_or_create(patient=patient, visit=visit)
        provisional_diagnosis_ids = provisional_record.provisional_diagnosis.values_list('id', flat=True)
        final_provisional_diagnosis = provisional_record.final_diagnosis.values_list('id', flat=True)
        primary_examination = PrimaryPhysicalExamination.objects.filter(patient=patient_id, visit=visit).first()
        previous_counselings = RemoteCounseling.objects.filter(patient=patient_id, visit=visit)
        previous_discharges = RemoteDischargesNotes.objects.filter(patient=patient_id, visit=visit)
        previous_observations = RemoteObservationRecord.objects.filter(patient=patient_id, visit=visit)
        previous_lab_orders = RemoteLaboratoryOrder.objects.filter(patient=patient_id, visit=visit)
        previous_prescriptions = RemotePrescription.objects.filter(patient=patient_id, visit=visit)
        previous_referrals = RemoteReferral.objects.filter(patient=patient_id, visit=visit)
        previous_procedures = RemoteProcedure.objects.filter(patient=patient_id, visit=visit)
        secondary_examination = SecondaryPhysicalExamination.objects.filter(patient_id=patient_id, visit_id=visit_id).first()
        pathology_records = PathodologyRecord.objects.all()

        # Update context with the retrieved data
        context.update({
            'secondary_examination': secondary_examination,
            'previous_counselings': previous_counselings,
            'previous_discharges': previous_discharges,
            'previous_observations': previous_observations,
            'previous_lab_orders': previous_lab_orders,
            'previous_prescriptions': previous_prescriptions,
            'previous_referrals': previous_referrals,
            'previous_procedures': previous_procedures,
            'primary_examination': primary_examination,
            'provisional_record': provisional_record,
            'health_records': health_records,
            'pathology_records': pathology_records,
            'health_conditions': health_conditions,
            'surgery_info': surgery_info,
            'provisional_diagnoses': provisional_diagnoses,
            'final_provisional_diagnosis': final_provisional_diagnosis,
            'provisional_diagnosis_ids': provisional_diagnosis_ids,
            'family_history': family_history,
            'behaviors': behaviors,
            'allergies': allergies,
            'patient_vitals': patient_vitals,
            'patient_surgeries': patient_surgeries,
            'consultation_note': consultation_note,
        })
        
    except Exception as e:
        # Handle any exception that might occur and show an error message
        messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'divine_admin_template/add_consultation_notes.html', context)


    

@login_required    
def save_counsel(request, patient_id, visit_id):
    # Retrieve patient and visit objects
    patient = get_object_or_404(RemotePatient, id=patient_id)
    visit = get_object_or_404(RemotePatientVisits, id=visit_id)              
    data_recorder = request.user.staff
    # Retrieve existing remote counseling record if it exists
    remote_counseling = RemoteCounseling.objects.filter(patient=patient, visit=visit).first()
    consultation_notes = RemotePatientDiagnosisRecord.objects.filter(patient=patient_id, visit=visit_id)  
    # Prepare context for rendering the template
    context = {
        'patient': patient, 
        'visit': visit,
        'remote_counseling': remote_counseling,
        'consultation_notes': consultation_notes,
    }
    
    # Handle form submission
    if request.method == 'POST':        
        form = RemoteCounselingForm(request.POST, instance=remote_counseling)
        
        # Check if a record already exists for the patient and visit
        if remote_counseling:
            # If a record exists, divine_admin_template it
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
        return redirect(reverse('divine_save_remotesconsultation_notes', args=[patient_id, visit_id]))
   
    else:
        # If it's a GET request, initialize the form with existing data (if any)
        form = RemoteCounselingForm(instance=remote_counseling)   
    # Add the form to the context
    context['form'] = form    
    return render(request, 'divine_admin_template/counsel_template.html', context)

@login_required
def save_remotereferral(request, patient_id, visit_id):
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
                # If a referral record exists, divine_admin_template it
                if referral:
                    referral = form.save(commit=False)
                    referral.patient = patient
                    referral.visit = visit
                    referral.data_recorder = data_recorder
                    referral.save()
                    messages.success(request, '')
                else:
                    # If no referral record exists, create a new one
                    form.instance.patient = patient
                    form.instance.visit = visit
                    form.instance.data_recorder = data_recorder
                    form.save()
                    messages.success(request, '')
                
                # Redirect to a success page or another view
                return redirect(reverse('divine_patient_visit_details_view', args=[patient_id, visit_id]))
            else:
                messages.error(request, 'Please correct the errors in the form.')
        else:
            # If it's a GET request, initialize the form with existing data (if any)
            form = RemoteReferralForm(instance=referral)
        
        context['form'] = form
        return render(request, 'divine_admin_template/save_remotereferral.html', context)
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return render(request, 'divine_admin_template/save_remotereferral.html', context)
        

    


@login_required
def save_observation(request, patient_id, visit_id):
    patient = get_object_or_404(RemotePatient, id=patient_id)
    visit = get_object_or_404(RemotePatientVisits, id=visit_id)
    data_recorder = request.user.staff
    record_exists = RemoteObservationRecord.objects.filter(patient_id=patient_id, visit_id=visit_id).first()
    consultation_notes = RemotePatientDiagnosisRecord.objects.filter(patient=patient_id, visit=visit_id)    
    context = {'patient': patient, 
               'visit': visit, 
               'consultation_notes': consultation_notes, 
               'record_exists': record_exists
               }
    if request.method == 'POST':
        form = RemoteObservationRecordForm(request.POST)
        if form.is_valid():
            description = form.cleaned_data['observation_notes']
            try:
                if record_exists:
                    # If a record exists, divine_admin_template it
                    observation_record = RemoteObservationRecord.objects.get(patient_id=patient_id, visit_id=visit_id)
                    observation_record.observation_notes = description
                    observation_record.data_recorder = data_recorder
                    observation_record.save()
                    messages.success(request, '')
                else:
                    # If no record exists, create a new one
                    RemoteObservationRecord.objects.create(
                        patient=patient,
                        visit=visit,
                        data_recorder=data_recorder,
                        observation_notes=description,
                    )
                    messages.success(request, '')
                return redirect(reverse('divine_save_remotesconsultation_notes', args=[patient_id, visit_id]))
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            messages.error(request, 'Please fill out all required fields.')
    else:
        form = RemoteObservationRecordForm(initial={'observation_notes': record_exists.observation_notes if record_exists else ''})

    context['form'] = form
    return render(request, 'divine_admin_template/observation_template.html', context)


    
@login_required
def patient_observation_view(request):
    template_name = 'divine_admin_template/manage_observation.html'    
    # Query to retrieve the latest procedure record for each patient
    observations = RemoteObservationRecord.objects.filter(
        patient=OuterRef('id')
    ).order_by('-created_at')
    # Query to retrieve patients with their corresponding procedure (excluding patients without observations)
    patients_with_observations = RemotePatient.objects.annotate(
        observation_name=Subquery(observations.values('imaging__name')[:1]),      
    ).filter(observation_name__isnull=False)    
  
    data = patients_with_observations.values(
        'id', 'mrn', 'observation_description',
       
    )
    return render(request, template_name, {'data': data})

@login_required
def patient_observation_history_view(request, mrn):
    patient = get_object_or_404(RemotePatient, mrn=mrn)    
    # Retrieve all procedures for the specific patient
    observations = RemoteObservationRecord.objects.filter(patient=patient)
    patient_observations =  Service.objects.filter(type_service='Imaging')    
    context = {
        'patient': patient,
        'observations': observations,
        'patient_observations': patient_observations,
    }
    return render(request, 'divine_admin_template/manage_patient_observation.html', context)


@login_required
def patient_laboratory_view(request):
    template_name = 'divine_admin_template/manage_lab_result.html'

    # Retrieve distinct patient and visit combinations from RemoteLaboratoryOrder
    patient_lab_results = (
        RemoteLaboratoryOrder.objects.values('patient__mrn', 
                                            'data_recorder__admin__first_name',
                                          'data_recorder__middle_name',
                                          'data_recorder__role',
                                          'data_recorder__admin__first_name',
                                             'visit__vst',
                                             )  
        .annotate(
            latest_result_date=Max('created_at')  # Annotate with the latest lab result date for each combination
        )
        .order_by('-latest_result_date')  # Order results by the latest date in descending order
    )

    context = {
        'data': patient_lab_results,  # Pass the results as 'data' for template rendering
    }

    return render(request, template_name, context)



@login_required
def patient_lab_details_view(request, mrn, visit_number):
    # Fetch the patient and corresponding lab results
    patient = get_object_or_404(RemotePatient, mrn=mrn)
    lab_results = RemoteLaboratoryOrder.objects.filter(patient=patient, visit__vst=visit_number)

    context = {
        'patient': patient,
        'visit_number': visit_number,
        'lab_results': lab_results,
    }
    return render(request, 'divine_admin_template/lab_details.html', context)

@login_required
def patient_lab_result_history_view(request, mrn):
    patient = get_object_or_404(RemotePatient, mrn=mrn)    
    # Retrieve all procedures for the specific patient
    lab_results = RemoteLaboratoryOrder.objects.filter(patient=patient)
    patient_lab_results =  Service.objects.filter(type_service='Laboratory')    
    context = {
        'patient': patient,
        'lab_results': lab_results,
        'patient_lab_results': patient_lab_results,
    }
    return render(request, 'divine_admin_template/manage_patient_lab_result.html', context)



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
                service.data_recorder = request.user.staff 
                
                # Add nhif_cost and insurance_cost only if coverage is insurance
                if coverage == 'Insurance':
                    service.nhif_cost = nhif_cost
                    service.insurance_cost = insurance_cost
                else:
                    # If coverage is not insurance, set nhif_cost and insurance_cost to 0
                    service.nhif_cost = 0
                    service.insurance_cost = 0
                
                service.save()
                return JsonResponse({'success': True, 'message': 'Service divine_admin_templated successfully'})
            else:
                # Check if the service name already exists
                if Service.objects.filter(name=name).exists():
                    return JsonResponse({'success': False, 'message': 'Service with this name already exists'})
                
                # Add new service
                new_service = Service.objects.create(name=name, 
                                                     description=description,
                                                     type_service=type_service,
                                                     data_recorder = request.user.staff , 
                                                      coverage=coverage, cash_cost=cash_cost
                                                      )
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
    

  
@csrf_exempt      
@require_POST
def delete_remote_patient(request, patient_id):
    try:
        patient_remote = get_object_or_404(RemotePatient, pk=patient_id)
        patient_remote.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}) 
 
@login_required    
def save_remote_discharges_notes(request, patient_id, visit_id):
    patient = get_object_or_404(RemotePatient, id=patient_id)
    visit = get_object_or_404(RemotePatientVisits, id=visit_id)
    consultation_notes = RemotePatientDiagnosisRecord.objects.filter(patient=patient_id, visit=visit_id)    
    remote_discharges_notes = RemoteDischargesNotes.objects.filter(patient=patient, visit=visit).first()  
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
            form = RemoteDischargesNotesForm(request.POST, instance=remote_discharges_notes)
            if form.is_valid():
                remote_discharges_notes = form.save(commit=False)
                remote_discharges_notes.patient = patient
                remote_discharges_notes.visit = visit
                remote_discharges_notes.data_recorder = data_recorder
                remote_discharges_notes.save()
                messages.success(request, '')
                return redirect(reverse('divine_patient_visit_details_view', args=[patient_id, visit_id]))  # Redirect to the next view
            else:
                messages.error(request, 'Please correct the errors in the form.')
        else:
            form = RemoteDischargesNotesForm(instance=remote_discharges_notes)        
        # Prepare context for rendering the template
        context['form'] = form
        return render(request, 'divine_admin_template/disrcharge_template.html', context)    
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return render(request, 'divine_admin_template/disrcharge_template.html', context)

@login_required    
def patient_statistics(request):
    current_year = datetime.now().year
    year_range = range(current_year, current_year - 10, -1)
    context = {
        'year_range': year_range,
        'current_year': current_year,
        # Other context variables...
    }
    return render(request, 'divine_admin_template/reports_comprehensive.html', context)


@login_required
def search_report(request):
    # Check if the request is POST and is an AJAX request
    if request.method == 'POST' and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        try:
            # Get the report type, year, and optionally month from the POST data
            report_type = request.POST.get('report_type')
            year = request.POST.get('year')
       

            # Define a dictionary to map report types to their corresponding HTML templates
            report_templates = {
                'patient_type_reports': 'divine_admin_template/patient_type_report_table.html',
                'patient_company_wise_reports': 'divine_admin_template/company_wise_reports_table.html',
                'patient_lab_result_reports': 'divine_admin_template/laboratory_report_table.html',
                'patient_procedure_reports': 'divine_admin_template/procedure_report_table.html',
                'patient_referral_reports': 'divine_admin_template/referral_reports_table.html',
                'patient_pathology_reports': 'divine_admin_template/pathology_record_report_table.html',
                # Add more report types here as needed
            }

            # Check if the report type is valid
            if report_type in report_templates:
                # Call the appropriate function to render the report based on the report type, year, and month
                html_result = render_report(report_type, year, report_templates[report_type])

                # Return the rendered HTML as a JSON response
                return JsonResponse({'html_result': html_result})

            else:
                # Return an error response if the report type is invalid
                return JsonResponse({'error': 'Invalid report type'})

        except Exception as e:
            # Handle any errors that may occur during processing
            return JsonResponse({'error': f'An error occurred: {str(e)}'})

    # Return an error response if the request is not POST or is not an AJAX request
    return JsonResponse({'error': 'Invalid request type'})




def get_monthly_data(queryset, key_field, name_field):
    """
    Helper function to process and format monthly data from a queryset.
    """
    monthly_data = {}
    for item in queryset:
        name = item[name_field]
        month = item['month']
        count = item[key_field]

        if month is not None:
            month_index = month - 1
            if name not in monthly_data:
                monthly_data[name] = [0] * 12
            monthly_data[name][month_index] = count

    return monthly_data


def render_report(report_type, year, template):
    """
    Generates a yearly report based on the report type, year, and template.

    Args:
        report_type (str): The type of report to generate.
        year (int): The year for the report data.
        template (str): The template file to use for rendering.

    Returns:
        str: Rendered HTML content for the report.
    """
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
              'August', 'September', 'October', 'November', 'December']

    if report_type == 'patient_type_reports':
        all_patient_types = ['National Staff', 'International Staff', 'National Visitor',
                             'International Visitor', 'Unknown Status', 'Others']

        patients_by_type = (
            RemotePatient.objects.filter(created_at__year=year)
            .values('patient_type')
            .annotate(month=ExtractMonth('created_at'), num_patients=Count('id'))
        )

        patient_type_reports = {ptype: [0] * 12 for ptype in all_patient_types}
        patient_type_reports.update(get_monthly_data(patients_by_type, 'num_patients', 'patient_type'))

        context = {'patient_type_reports': patient_type_reports, 'months': months}
        return render_to_string(template, context)

    elif report_type == 'patient_company_wise_reports':
        all_companies = RemoteCompany.objects.values_list('name', flat=True)

        patients_by_company = (
            RemotePatient.objects.filter(created_at__year=year)
            .values('company__name')
            .annotate(month=ExtractMonth('created_at'), num_patients=Count('id'))
        )

        company_reports = {company: [0] * 12 for company in all_companies}
        company_reports.update(get_monthly_data(patients_by_company, 'num_patients', 'company__name'))

        context = {'company_reports': company_reports, 'months': months}
        return render_to_string(template, context)

    elif report_type == 'patient_lab_result_reports':
        laboratory_services = RemoteService.objects.filter(category='Laboratory').values_list('name', flat=True)

        labs_by_month = (
            RemoteLaboratoryOrder.objects.filter(created_at__year=year)
            .values('name__name')
            .annotate(month=ExtractMonth('created_at'), num_patients=Count('id'))
        )

        laboratory_reports = {service: [0] * 12 for service in laboratory_services}
        laboratory_reports.update(get_monthly_data(labs_by_month, 'num_patients', 'name__name'))

        context = {'laboratory_reports': laboratory_reports, 'months': months}
        return render_to_string(template, context)

    elif report_type == 'patient_procedure_reports':
        procedure_services = RemoteService.objects.filter(category='Procedure').values_list('name', flat=True)

        procedures_by_month = (
            RemoteProcedure.objects.filter(created_at__year=year)
            .values('name__name')
            .annotate(month=ExtractMonth('created_at'), num_patients=Count('id'))
        )

        procedure_reports = {service: [0] * 12 for service in procedure_services}
        procedure_reports.update(get_monthly_data(procedures_by_month, 'num_patients', 'name__name'))

        context = {'procedure_reports': procedure_reports, 'months': months}
        return render_to_string(template, context)

    elif report_type == 'patient_referral_reports':
        referrals = RemoteReferral.objects.filter(created_at__year=year)
        context = {'referrals': referrals}
        return render_to_string(template, context)

    elif report_type == 'patient_pathology_reports':
        all_pathology_records = PathodologyRecord.objects.values_list('name', flat=True)

        pathologies_by_month = (
            PathodologyRecord.objects.filter(remoteconsultationnotes__created_at__year=year)
            .values('name')
            .annotate(month=ExtractMonth('remoteconsultationnotes__created_at'), num_patients=Count('remoteconsultationnotes__id'))
        )

        pathology_reports = {record: [0] * 12 for record in all_pathology_records}
        pathology_reports.update(get_monthly_data(pathologies_by_month, 'num_patients', 'name'))

        context = {'pathology_record_reports': pathology_reports, 'months': months}
        return render_to_string(template, context)

    else:
        raise ValueError(f"Unknown report type: {report_type}")




 

@login_required
def remotemedicine_list(request):
    medicines = RemoteMedicine.objects.all()
    return render(request, 'divine_admin_template/remotemedicine_list.html', {'medicines': medicines})

@login_required
@csrf_exempt
def add_remote_medicine(request):
    if request.method == 'POST':
        try:
            # Retrieve data from POST request
            drug_id = request.POST.get('drug_id')
            drug_name = request.POST.get('drug_name').strip()
            drug_type = request.POST.get('drug_type').strip()
            formulation_unit = request.POST.get('formulation_unit').strip()
            manufacturer = request.POST.get('manufacturer').strip()
            quantity = request.POST.get('quantity').strip()
            dividable = request.POST.get('dividable')
            batch_number = request.POST.get('batch_number').strip()
            expiration_date = request.POST.get('expiration_date')
            unit_cost = request.POST.get('unit_cost').strip()
            buying_price = request.POST.get('buying_price').strip()
            
            # Check if required fields are provided
            if not (drug_name and quantity and buying_price):
                return JsonResponse({'success': False, 'message': 'Missing required fields'})

            # Convert quantity and buying_price to integers or floats
            try:
                quantity = int(quantity)
                buying_price = float(buying_price)
            except ValueError:
                return JsonResponse({'success': False, 'message': 'Invalid quantity or buying price'})

            # If drug ID is provided, it indicates editing existing data
            if drug_id:
                # Check if another medicine with the same name or batch number already exists
                if RemoteMedicine.objects.exclude(pk=drug_id).filter(drug_name=drug_name).exists():
                    return JsonResponse({'success': False, 'message': 'Another medicine with the same name already exists'})
                if RemoteMedicine.objects.exclude(pk=drug_id).filter(batch_number=batch_number).exists():
                    return JsonResponse({'success': False, 'message': 'Another medicine with the same batch number already exists'})
                
                # Get the RemoteMedicine object to edit
                medicine = RemoteMedicine.objects.get(pk=drug_id)
                
                # Update fields with new values
                medicine.drug_name = drug_name
                medicine.drug_type = drug_type
                medicine.formulation_unit = formulation_unit
                medicine.manufacturer = manufacturer
                medicine.quantity = quantity
                medicine.remain_quantity = quantity
                medicine.dividable = dividable
                medicine.batch_number = batch_number
                medicine.expiration_date = expiration_date
                medicine.unit_cost = unit_cost
                medicine.buying_price = buying_price
                medicine.data_recorder = request.user.staff 
                
                # Save the changes
                medicine.save()                
                # Return success response
                return JsonResponse({'success': True, 'message': 'Medicine divine_admin_templated successfully'})
            
            else:            
                # Check if another medicine with the same name or batch number already exists
                if RemoteMedicine.objects.filter(drug_name=drug_name).exists():
                    return JsonResponse({'success': False, 'message': 'Medicine with the same name already exists'})
                if RemoteMedicine.objects.filter(batch_number=batch_number).exists():
                    return JsonResponse({'success': False, 'message': 'Medicine with the same batch number already exists'})
                
                # Create RemoteMedicine object for adding new data
                medicine = RemoteMedicine(
                    drug_name=drug_name,
                    drug_type=drug_type,
                    formulation_unit=formulation_unit,
                    manufacturer=manufacturer,
                    quantity=quantity,
                    remain_quantity=quantity,
                    dividable=dividable,
                    batch_number=batch_number,
                    expiration_date=expiration_date,
                    unit_cost=unit_cost,
                    buying_price=buying_price,
                    data_recorder = request.user.staff 
                )
                
                # Save the object
                medicine.save()                
                # Return success response
                return JsonResponse({'success': True, 'message': 'Medicine added successfully'})
        
        except Exception as e:
            # Return error response if an exception occurs
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
    # If request method is not POST, return error response
    return JsonResponse({'success': False, 'message': 'Invalid request method'})



@login_required
def company_registration_view(request):
    try:
        # There should only be one company record, retrieve it if it exists
        company = ClinicCompany.objects.first()

        if request.method == 'POST':
            name = request.POST.get('name').strip()
            registration_number = request.POST.get('registration_number')
            address = request.POST.get('address').strip()
            city = request.POST.get('city').strip()
            state = request.POST.get('state').strip()
            country = request.POST.get('country').strip()
            postal_code = request.POST.get('postal_code').strip()
            phone_number = request.POST.get('phone_number').strip()
            email = request.POST.get('email').strip()
            website = request.POST.get('website').strip()
            logo = request.FILES.get('logo') if 'logo' in request.FILES else None

            if company:  # Editing existing record
                company.name = name
                company.registration_number = registration_number
                company.address = address
                company.city = city
                company.state = state
                company.country = country
                company.postal_code = postal_code
                company.phone_number = phone_number
                company.email = email
                company.website = website
                if logo:
                    company.logo = logo
                company.data_recorder = request.user.staff   # Track who edited the record
                company.save()
                messages.success(request, 'Company divine_admin_templated successfully!')
            else:  # Adding new record
                new_company = ClinicCompany(
                    name=name,
                    registration_number=registration_number,
                    address=address,
                    city=city,
                    state=state,
                    country=country,
                    postal_code=postal_code,
                    phone_number=phone_number,
                    email=email,
                    website=website,
                    logo=logo,
                    data_recorder=request.user.staff   # Track who added the record
                )
                new_company.save()
                messages.success(request, 'Company added successfully!')

            return redirect('divine_add_clinic_company')  # Redirect to success page

        else:
            return render(request, 'divine_admin_template/company_registration.html', {'company': company})
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return render(request, 'divine_admin_template/company_registration.html')

    
    
@login_required    
def edit_lab_result(request, patient_id, visit_id, lab_id):
    # Retrieve patient and visit objects
    patient = get_object_or_404(RemotePatient, id=patient_id)
    visit = get_object_or_404(RemotePatientVisits, id=visit_id)            

    procedures = RemoteLaboratoryOrder.objects.filter(patient=patient, visit=visit, id=lab_id).first()
    
    # Prepare context for rendering the template
    context = {
        'patient': patient, 
        'visit': visit,
        'procedures': procedures,
    }
    
    # Handle form submission
    if request.method == 'POST':        
        form = RemoteLaboratoryOrderForm(request.POST, instance=procedures)
        
        # Check if a record already exists for the patient and visit
        if procedures:
            # If a record exists, divine_admin_template it
            if form.is_valid():
                try:
                    # Track the user who edited the record
                    procedures.data_recorder = request.user.staff   # Set the staff member who edited
                    form.save()  # Save the divine_admin_templated record
                    messages.success(request, 'Laboratory result divine_admin_templated successfully!')
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
        return redirect(reverse('divine_patient_lab_result_history_view', args=[patient.mrn]))
   
    else:
        # If it's a GET request, initialize the form with existing data (if any)
        form = RemoteLaboratoryOrderForm(instance=procedures)   
    
    # Add the form to the context
    context['form'] = form    
    return render(request, 'divine_admin_template/edit_lab_result.html', context)


@login_required    
def edit_procedure_result(request, patient_id, visit_id, procedure_id):
    # Retrieve patient and visit objects
    patient = get_object_or_404(RemotePatient, id=patient_id)
    visit = get_object_or_404(RemotePatientVisits, id=visit_id)            

    procedures = RemoteProcedure.objects.filter(patient=patient, visit=visit, id=procedure_id).first()
    
    # Prepare context for rendering the template
    context = {
        'patient': patient, 
        'visit': visit,
        'procedures': procedures,
    }
    
    # Handle form submission
    if request.method == 'POST':        
        form = RemoteProcedureForm(request.POST, instance=procedures)
        
        # Check if a record already exists for the patient and visit
        if procedures:
            # If a record exists, divine_admin_template it
            if form.is_valid():
                try:
                    # Track the user who edited the record
                    procedures.data_recorder = request.user.staff   # Set the staff member who edited
                    form.save()  # Save the divine_admin_templated record
                    messages.success(request, 'Procedure result divine_admin_templated successfully!')
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
                    messages.success(request, 'Procedure result added successfully!')
                except ValidationError as e:
                    messages.error(request, f'Validation Error: {e}')
            else:
                messages.error(request, 'Please correct the errors in the form.')

        # Redirect to the appropriate page after saving
        return redirect(reverse('divine_patient_procedure_history_view_mrn', args=[patient.mrn]))
   
    else:
        # If it's a GET request, initialize the form with existing data (if any)
        form = RemoteProcedureForm(instance=procedures)   
    
    # Add the form to the context
    context['form'] = form    
    return render(request, 'divine_admin_template/edit_procedure_result.html', context)


@login_required
def remote_equipment_list(request):
    equipment_list = RemoteEquipment.objects.all()
    return render(request, 'divine_admin_template/remote_equipment_list.html', {'equipment_list': equipment_list})


@login_required    
@csrf_exempt
def add_or_edit_remote_equipment(request):
    if request.method == 'POST':
        data = request.POST
        equipment_id = data.get('equipment_id')
        name = data.get('name').strip()
        description = data.get('description', '')
        serial_number = data.get('serial_number').strip()
        manufacturer = data.get('manufacturer', '')
        purchase_date = data.get('purchase_date')
        warranty_expiry_date = data.get('warranty_expiry_date', None)
        location = data.get('location', '')
        status = data.get('status', 'Operational')

        # Check for uniqueness
        try:
            if equipment_id:
                # Edit existing record
                equipment = RemoteEquipment.objects.get(id=equipment_id)
                if RemoteEquipment.objects.exclude(id=equipment_id).filter(name=name).exists():
                    return JsonResponse({'success': False, 'message': 'Equipment with this name already exists.'})
                if RemoteEquipment.objects.exclude(id=equipment_id).filter(serial_number=serial_number).exists():
                    return JsonResponse({'success': False, 'message': 'Equipment with this serial number already exists.'})

                equipment.name = name
                equipment.description = description
                equipment.serial_number = serial_number
                equipment.manufacturer = manufacturer
                equipment.purchase_date = purchase_date
                equipment.warranty_expiry_date = warranty_expiry_date
                equipment.location = location
                equipment.status = status
                equipment.data_recorder = request.user.staff   # Track who divine_admin_templated the record
                equipment.save()
                return JsonResponse({'success': True, 'message': 'Equipment divine_admin_templated successfully!'})
            else:
                # Add new record
                if RemoteEquipment.objects.filter(name=name).exists():
                    return JsonResponse({'success': False, 'message': 'Equipment with this name already exists.'})
                if RemoteEquipment.objects.filter(serial_number=serial_number).exists():
                    return JsonResponse({'success': False, 'message': 'Equipment with this serial number already exists.'})

                RemoteEquipment.objects.create(
                    name=name,
                    description=description,
                    serial_number=serial_number,
                    manufacturer=manufacturer,
                    purchase_date=purchase_date,
                    warranty_expiry_date=warranty_expiry_date,
                    location=location,
                    status=status,
                    data_recorder=request.user.staff   # Track who added the record
                )
                return JsonResponse({'success': True, 'message': 'Equipment added successfully!'})
        except RemoteEquipment.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Equipment not found.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})



@login_required
@csrf_exempt
def delete_remote_equipment(request):
    if request.method == 'POST':
        equipment_id = request.POST.get('id')
        
        try:
            equipment = RemoteEquipment.objects.get(id=equipment_id)
            equipment.delete()
            return JsonResponse({'status': 'true', 'message': 'Equipment deleted successfully!'})
        except RemoteEquipment.DoesNotExist:
            return JsonResponse({'status': 'false', 'message': 'Equipment not found.'})
        except Exception as e:
            return JsonResponse({'status': 'false', 'message': str(e)})
    
    return JsonResponse({'status': 'false', 'message': 'Invalid request method'})



@login_required
def reagent_list(request):
    reagent_list = RemoteReagent.objects.all()
    return render(request, 'divine_admin_template/remotereagent_list.html', {'reagent_list': reagent_list})

@login_required    
@csrf_exempt
def add_or_edit_reagent(request):
    if request.method == 'POST':
        data = request.POST  # Using request.POST for form data
        reagent_id = data.get('reagent_id')
        name = data.get('name').strip()
        supplier = data.get('supplier', '')
        quantity = data.get('quantity')
        expiry_date = data.get('expiry_date')
        storage_conditions = data.get('storage_conditions', '')

        try:
            # Check for uniqueness before creating or updating
            if reagent_id:
                # Edit existing record
                existing_reagent = RemoteReagent.objects.exclude(id=reagent_id).filter(name=name)
                if existing_reagent.exists():
                    return JsonResponse({'status': 'false', 'message': 'A reagent with the same name already exists.'})
                reagent = RemoteReagent.objects.get(id=reagent_id)
                reagent.name = name
                reagent.supplier = supplier
                reagent.quantity = quantity
                reagent.expiry_date = expiry_date
                reagent.storage_conditions = storage_conditions
                reagent.data_recorder = request.user.staff   # Track who divine_admin_templated the record
                reagent.save()
                return JsonResponse({'success': True, 'message': 'Reagent divine_admin_templated successfully!'})
            else:
                # Add new record
                existing_reagent = RemoteReagent.objects.filter(name=name)
                if existing_reagent.exists():
                    return JsonResponse({'success': False, 'message': 'A reagent with the same name already exists.'})
                RemoteReagent.objects.create(
                    name=name,
                    supplier=supplier,
                    quantity=quantity,
                    expiry_date=expiry_date,
                    storage_conditions=storage_conditions,
                    data_recorder=request.user.staff   # Track who added the record
                )
                return JsonResponse({'success': True, 'message': 'Reagent added successfully!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@login_required
@csrf_exempt
def delete_reagent(request):
    if request.method == 'POST':
        reagent_id = request.POST.get('id')

        try:
            # Check if the reagent exists
            reagent = RemoteReagent.objects.get(id=reagent_id)
            reagent.delete()
            return JsonResponse({'status': 'true', 'message': 'Reagent deleted successfully'})
        except RemoteReagent.DoesNotExist:
            return JsonResponse({'status': 'false', 'message': 'Reagent does not exist'})
        except Exception as e:
            return JsonResponse({'status': 'false', 'message': str(e)})

    return JsonResponse({'status': 'false', 'message': 'Invalid request method'})

        
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
            messages.success(request, '')
        else:
            messages.error(request, 'Invalid request method')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')

    # Redirect back to the staff list page
    return redirect('manage_staff')  # Make sure 'manage_staffs' is the name of your staff list URL        

