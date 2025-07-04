import calendar
from django.utils import timezone
import logging
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from clinic.models import  ChiefComplaint, ClinicCompany, Diagnosis,    Country, CustomUser, DiseaseRecode, HealthRecord,   PathodologyRecord,      RemoteCompany, RemoteConsultation, RemoteConsultationNotes,  RemoteCounseling, RemoteDischargesNotes, RemoteEquipment, RemoteImagingRecord, RemoteLaboratoryOrder, RemoteMedicine, RemoteObservationRecord, RemotePatient,  RemotePatientVisits, RemotePatientVital,  RemotePrescription, RemoteProcedure, RemoteReagent, RemoteReferral, RemoteService,  Staffs
from django.template.loader import render_to_string
from django.db.models import Max, Count,OuterRef, Subquery
from django.views.decorators.http import require_POST
from django.db.models.functions import ExtractMonth
from datetime import date, datetime
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash,logout
from weasyprint import HTML
import os

def remote_patient_list_view(request):
    patients = RemotePatient.objects.select_related('company', 'nationality', 'data_recorder').all().order_by('-created_at')
    context = {
        'patients': patients
    }
    return render(request, 'divine_admin_template/remote_patient_list.html', context)

@require_POST
@csrf_exempt  # Optional: remove if using {% csrf_token %} properly
def delete_remote_patient_view(request):
    patient_id = request.POST.get('patient_id')

    if not patient_id:
        return JsonResponse({'status': 'error', 'message': 'Missing patient ID'})

    try:
        patient = RemotePatient.objects.get(id=patient_id)
        patient.delete()
        return JsonResponse({'status': 'success'})
    except RemotePatient.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Patient not found'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})    

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

@login_required
def admin_profile(request):
    # Get the logged-in user
    user = request.user
    
    try:
        # Fetch the admin's details from the Staffs model
        staff = Staffs.objects.get(admin=user, role='admin')
        
        # Pass the admin details to the template
        return render(request, 'divine_admin_template/profile.html', {'staff': staff})

    except Staffs.DoesNotExist:
        # In case no admin data is found, return an error message
        return render(request, 'divine_admin_template/profile.html', {'error': 'Admin not found.'})

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

    return render(request, 'divine_admin_template/change_password.html', {'form': form})            

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
    

def expired_medicine_view(request):
    medicines = RemoteMedicine.objects.filter(
        is_clinic_stock=True,
        expiration_date__lt=timezone.now().date()
    )
    return render(request, 'divine_admin_template/expired_medicine.html', {'medicines': medicines})


def instock_medicine_view(request):
    medicines = RemoteMedicine.objects.filter(
        is_clinic_stock=True,
        quantity__gt=0,
        expiration_date__gte=timezone.now().date()
    )
    return render(request, 'divine_admin_template/instock_medicine.html', {'medicines': medicines})


def checklist_medicine_view(request):
    medicines = RemoteMedicine.objects.filter(is_clinic_stock=False)
    return render(request, 'divine_admin_template/checklist_medicine.html', {'medicines': medicines})


def outofstock_medicine_view(request):
    medicines = RemoteMedicine.objects.filter(
        is_clinic_stock=True,
        quantity__lte=0
    )
    return render(request, 'divine_admin_template/outofstock_medicine.html', {'medicines': medicines})


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





@login_required
def patient_procedure_view(request):
    # Get all distinct (patient, visit) pairs that have at least one procedure
    distinct_procedure_sets = (
        RemoteProcedure.objects
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

        procedures = RemoteProcedure.objects.filter(
            patient_id=patient_id,
            visit_id=visit_id
        ).select_related('patient', 'visit', 'doctor__admin', 'name')

        if procedures.exists():
            first_proc = procedures.first()
            patient_procedures.append({
                'patient': first_proc.patient,
                'visit': first_proc.visit,
                'latest_date': latest_date,
                'doctor': first_proc.doctor,
                'procedure_done_by':first_proc.doctor,
                'procedures': procedures  # All procedures for that visit
            })

    context = {
        'patient_procedures': patient_procedures,
    }
    return render(request, 'divine_admin_template/manage_procedure.html', context)


@login_required
def manage_referral(request):
    referrals = RemoteReferral.objects.all()   
    return render(request, 'divine_admin_template/manage_referral.html', {'referrals': referrals})



@login_required
def appointment_list_view(request):
    appointments = RemoteConsultation.objects.all() 
    doctors = Staffs.objects.filter(role='doctor', work_place = 'kahama')   
    context = {        
        'appointments':appointments,
        'doctors':doctors        
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
    
 

 
# views.py
@require_POST
def delete_remotecompany(request):
    company_id = request.POST.get('company_id')
    try:
        RemoteCompany.objects.get(id=company_id).delete()
        return JsonResponse({'success': True})
    except RemoteCompany.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Company not found'})

@csrf_exempt
@login_required
def add_company(request):
    if request.method == 'POST':
        try:
            company_id = request.POST.get('company_id')
            name = request.POST.get('name', '').strip()

            if not name:
                return JsonResponse({'success': False, 'message': 'Company name is required.'})

            # Editing an existing company
            if company_id:
                try:
                    company = RemoteCompany.objects.get(pk=company_id)

                    # Ensure no duplicate names
                    if RemoteCompany.objects.filter(name=name).exclude(pk=company_id).exists():
                        return JsonResponse({'success': False, 'message': 'Company name already exists.'})

                    company.name = name
                    company.save()

                    return JsonResponse({'success': True, 'message': 'Company updated successfully.'})
                except RemoteCompany.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Company not found.'})

            # Adding a new company
            else:
                if RemoteCompany.objects.filter(name=name).exists():
                    return JsonResponse({'success': False, 'message': 'Company already exists.'})

                RemoteCompany.objects.create(name=name)
                return JsonResponse({'success': True, 'message': 'Company added successfully.'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

    
  
 
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







@login_required
def prescription_list(request):
    # Step 1: Fetch all prescriptions with related fields
    prescriptions = RemotePrescription.objects.select_related(
        'visit', 'patient', 'medicine', 'frequency'
    ).order_by('-visit__created_at')

    # Step 2: Group prescriptions by visit
    grouped_visits = {}
    for prescription in prescriptions:
        visit_id = prescription.visit.id

        if visit_id not in grouped_visits:
            grouped_visits[visit_id] = {
                'visit': prescription.visit,
                'patient': prescription.patient,
                'prescriptions': [],
            }

        grouped_visits[visit_id]['prescriptions'].append(prescription)

    # Step 3: Sort visits by creation date
    visit_groups = sorted(
        grouped_visits.values(), key=lambda v: v['visit'].created_at, reverse=True
    )

    return render(request, 'divine_admin_template/manage_prescription_list.html', {
        'visit_groups': visit_groups,
    })



@login_required
def consultation_notes_view(request):
    # Get all patients who have consultation notes
    patient_records = RemotePatient.objects.filter(
        remoteconsultationnotes__isnull=False
    ).distinct().order_by('-remoteconsultationnotes__updated_at')

    return render(request, 'divine_admin_template/manage_consultation_notes.html', {
        'patient_records': patient_records
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
def patient_laboratory_view(request):
    # Get distinct (patient, visit) combinations with latest result date
    distinct_lab_sets = (
        RemoteLaboratoryOrder.objects
        .values('patient_id', 'visit_id')
        .annotate(latest_date=Max('created_at'))
        .order_by('-latest_date')
    )

    patient_lab_data = []

    for entry in distinct_lab_sets:
        patient_id = entry['patient_id']
        visit_id = entry['visit_id']
        latest_date = entry['latest_date']

        lab_tests = RemoteLaboratoryOrder.objects.filter(
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

    return render(request, 'divine_admin_template/manage_lab_result.html', context)

 
@csrf_exempt
def delete_consultation(request):
    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        try:
            appointment = RemoteConsultation.objects.get(id=appointment_id)
            appointment.delete()
            return JsonResponse({'status': 'success'})
        except RemoteConsultation.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Appointment not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

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
    today = date.today()
        # Annotate each with days left
    for medicine in medicines:
        if medicine.expiration_date:
            medicine.days_left = (medicine.expiration_date - today).days
        else:
            medicine.days_left = None
    return render(request, 'divine_admin_template/remotemedicine_list.html', {'medicines': medicines,'today': date.today()})


@login_required
@csrf_exempt
def add_remote_medicine(request):
    if request.method == 'POST':
        try:
            post = request.POST
            drug_id = post.get('medicine_id')
            drug_name = post.get('drug_name', '').strip()
            drug_type = post.get('drug_type', '').strip()
            formulation_unit = post.get('formulation_unit', '').strip()
            is_dividable = post.get('is_dividable') == 'true'
            dividing_unit = post.get('dividing_unit')
            is_clinic_stock = post.get('is_clinic_stock') == 'true'
            manufacturer = post.get('manufacturer', '').strip()
            quantity = post.get('quantity')
            minimum_stock_level = post.get('minimum_stock_level')
            batch_number = post.get('batch_number', '').strip()
            expiration_date = post.get('expiration_date')

            # Basic validation
            if not drug_name or not drug_type or not formulation_unit:
                return JsonResponse({'success': False, 'message': 'Drug name, type and formulation unit are required.'})

            if is_clinic_stock:
                required_fields = [manufacturer, quantity, minimum_stock_level, batch_number, expiration_date]
                if not all(required_fields):
                    return JsonResponse({'success': False, 'message': 'All clinic stock fields are required.'})
                try:
                    quantity = int(quantity)
                    minimum_stock_level = int(minimum_stock_level)
                except ValueError:
                    return JsonResponse({'success': False, 'message': 'Quantity and minimum stock level must be numeric.'})

            if drug_id:
                # Editing existing
                try:
                    medicine = RemoteMedicine.objects.get(pk=drug_id)
                except RemoteMedicine.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Medicine not found for editing.'})

                # Prevent duplicates on name or batch number
                if RemoteMedicine.objects.exclude(pk=drug_id).filter(drug_name=drug_name).exists():
                    return JsonResponse({'success': False, 'message': 'Another medicine with the same name already exists'})
                if RemoteMedicine.objects.exclude(pk=drug_id).filter(batch_number=batch_number).exists():
                    return JsonResponse({'success': False, 'message': 'Another medicine with the same batch number already exists'})

                # Update fields
                medicine.drug_name = drug_name
                medicine.drug_type = drug_type
                medicine.formulation_unit = formulation_unit
                medicine.is_dividable = is_dividable
                medicine.dividing_unit = dividing_unit if is_dividable else None
                medicine.is_clinic_stock = is_clinic_stock

                if is_clinic_stock:
                    medicine.manufacturer = manufacturer
                    medicine.quantity = quantity
                    medicine.remain_quantity = quantity
                    medicine.minimum_stock_level = minimum_stock_level
                    medicine.batch_number = batch_number
                    medicine.expiration_date = expiration_date

                medicine.data_recorder = request.user.staff
                medicine.save()
                return JsonResponse({'success': True, 'message': 'Medicine updated successfully'})
            else:
                # Check for duplicates
                if RemoteMedicine.objects.filter(drug_name=drug_name).exists():
                    return JsonResponse({'success': False, 'message': 'Medicine with the same name already exists'})
                if RemoteMedicine.objects.filter(batch_number=batch_number).exists():
                    return JsonResponse({'success': False, 'message': 'Medicine with the same batch number already exists'})

                # Create new entry
                medicine = RemoteMedicine(
                    drug_name=drug_name,
                    drug_type=drug_type,
                    formulation_unit=formulation_unit,
                    is_dividable=is_dividable,
                    dividing_unit=dividing_unit if is_dividable else None,
                    is_clinic_stock=is_clinic_stock,
                    manufacturer=manufacturer if is_clinic_stock else '',
                    quantity=quantity if is_clinic_stock else 0,
                    remain_quantity=quantity if is_clinic_stock else 0,
                    minimum_stock_level=minimum_stock_level if is_clinic_stock else 0,
                    batch_number=batch_number if is_clinic_stock else '',
                    expiration_date=expiration_date if is_clinic_stock else None,
                    data_recorder=request.user.staff
                )
                medicine.save()
                return JsonResponse({'success': True, 'message': 'Medicine added successfully'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})


def medicine_count_api(request):
    today = timezone.now().date()

    expired_count = RemoteMedicine.objects.filter(is_clinic_stock=True, expiration_date__lt=today).count()
    instock_count = RemoteMedicine.objects.filter(is_clinic_stock=True, quantity__gt=0, expiration_date__gte=today).count()
    checklist_count = RemoteMedicine.objects.filter(is_clinic_stock=False).count()
    outofstock_count = RemoteMedicine.objects.filter(is_clinic_stock=True, quantity__lte=0).count()
    total_count = RemoteMedicine.objects.all().count()

    return JsonResponse({
        "expired": expired_count,
        "instock": instock_count,
        "checklist": checklist_count,
        "outofstock": outofstock_count,
        "all": total_count
    })

@csrf_exempt
@login_required
def delete_remote_medicine(request):
  if request.method == 'POST':
    medicine_id = request.POST.get('medicine_id')
    try:
      medicine = get_object_or_404(RemoteMedicine, pk=medicine_id)
      medicine.delete()
      return JsonResponse({'success': True, 'message': 'Medicine deleted successfully.'})
    except Exception as e:
      return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
  return JsonResponse({'success': False, 'message': 'Invalid request method.'})



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

 
@login_required
def download_consultation_summary_pdf(request, patient_id, visit_id):
    # Fetch core patient and visit info
    patient = get_object_or_404(RemotePatient, id=patient_id)
    visit = get_object_or_404(RemotePatientVisits, id=visit_id)

    # Query all related models for that visit
    counseling = RemoteCounseling.objects.filter(patient=patient, visit=visit).last()
    prescriptions = RemotePrescription.objects.filter(patient=patient, visit=visit)
    observations = RemoteObservationRecord.objects.filter(patient=patient, visit=visit).last()
    discharge_note = RemoteDischargesNotes.objects.filter(patient=patient, visit=visit).last()
    referral = RemoteReferral.objects.filter(patient=patient, visit=visit).last()
    complaints = ChiefComplaint.objects.filter(patient=patient, visit=visit)
    vitals = RemotePatientVital.objects.filter(patient=patient, visit=visit).last()

    # NEW: Add Consultation Notes
    consultation_note = RemoteConsultationNotes.objects.filter(patient=patient, visit=visit).last()

    # NEW: Add Imaging Records
    imaging_records = RemoteImagingRecord.objects.filter(patient=patient, visit=visit).select_related('imaging', 'data_recorder')

    # NEW: Add Laboratory Orders
    lab_tests = RemoteLaboratoryOrder.objects.filter(patient=patient, visit=visit).select_related('name', 'data_recorder')

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
    html_content = render_to_string('divine_admin_template/pdf_consultation_summary.html', context)

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


def download_observation_pdf(request, patient_id, visit_id):
    # Fetch the required patient and visit
    visit = get_object_or_404(RemotePatientVisits, id=visit_id)
    patient = get_object_or_404(RemotePatient, id=patient_id)
    observation_record = get_object_or_404(RemoteObservationRecord, patient=patient, visit=visit)

    # Prepare context for the template
    context = {
        'observation_record': observation_record,
        'visit': visit,
    }

    # Render HTML template
    html_content = render_to_string('divine_admin_template/observation_notes_detail.html', context)

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
    visit = get_object_or_404(RemotePatientVisits, id=visit_id)
    patient = get_object_or_404(RemotePatient, id=patient_id)
    discharge_note = get_object_or_404(RemoteDischargesNotes, patient=patient, visit=visit)

    # Prepare context
    context = {
        'discharge_note': discharge_note,
        'patient': patient,
        'visit': visit,
    }

    # Render HTML content using a dedicated template
    html_content = render_to_string('divine_admin_template/discharge_note_detail.html', context)

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
    visit = get_object_or_404(RemotePatientVisits, id=visit_id)
    patient = get_object_or_404(RemotePatient, id=patient_id)
    counseling = get_object_or_404(RemoteCounseling, patient=patient, visit=visit)

    # Prepare context
    context = {
        'counseling': counseling,
        'patient': patient,
        'visit': visit,
    }

    # Render HTML content from a dedicated counseling note template
    html_content = render_to_string('divine_admin_template/counseling_notes_details.html', context)

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
    visit = get_object_or_404(RemotePatientVisits, id=visit_id)
    patient = get_object_or_404(RemotePatient, id=patient_id)
    referral = get_object_or_404(RemoteReferral, patient=patient, visit=visit)

    # Prepare context
    context = {
        'referral': referral,
        'patient': patient,
        'visit': visit,
    }

    # Render HTML content from a dedicated referral note template
    html_content = render_to_string('divine_admin_template/view_referral.html', context)

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
    patient = get_object_or_404(RemotePatient, id=patient_id)
    visit = get_object_or_404(RemotePatientVisits, id=visit_id)

    # Get all prescriptions for this patient and visit
    prescriptions = RemotePrescription.objects.filter(patient=patient, visit=visit)

    # Prepare context
    context = {
        'patient': patient,
        'visit': visit,
        'prescriptions': prescriptions,
    }

    # Render HTML content using a dedicated template
    html_content = render_to_string('divine_admin_template/prescription_notes.html', context)

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


@login_required
def download_procedure_result_pdf(request, procedure_id):
    # Fetch procedure or return 404
    procedure = get_object_or_404(RemoteProcedure.objects.select_related('patient', 'visit', 'name'), id=procedure_id)

    # Prepare context for template
    context = {
        'procedure': procedure,
    }

    # Render the HTML content using template
    html_content = render_to_string('divine_admin_template/pdf_procedure_result.html', context)

    # Create temporary directory for storing the PDF
    temp_dir = os.path.join(os.path.expanduser("~"), "pdf_temp")
    os.makedirs(temp_dir, exist_ok=True)

    # Define safe file name and full path
    file_name = f"procedure_result_{procedure.patient.full_name}.pdf"
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
    patient = get_object_or_404(RemotePatient, mrn=patient_mrn)
    visit = get_object_or_404(RemotePatientVisits, vst=visit_vst)

    # Fetch all related procedures
    procedures = RemoteProcedure.objects.filter(patient=patient, visit=visit).select_related('name')

    if not procedures.exists():
        return HttpResponse("No procedures found for this visit.", status=404)

    context = {
        'patient': patient,
        'visit': visit,
        'procedures': procedures
    }

    # Render the template
    html_content = render_to_string('divine_admin_template/pdf_all_procedures.html', context)

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
        RemoteLaboratoryOrder.objects.select_related('patient', 'visit', 'data_recorder', 'name'),
        id=lab_id
    )

    # Prepare context for PDF rendering
    context = {
        'lab': lab,
    }

    # Render HTML from template
    html_content = render_to_string('divine_admin_template/pdf_lab_result.html', context)

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
    patient = get_object_or_404(RemotePatient, mrn=patient_mrn)
    visit = get_object_or_404(RemotePatientVisits, vst=visit_vst)

    # Fetch all laboratory orders for this patient and visit
    lab_tests = RemoteLaboratoryOrder.objects.filter(patient=patient, visit=visit).select_related(
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
    html_content = render_to_string('divine_admin_template/pdf_all_lab_results.html', context)

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
        RemoteImagingRecord.objects.select_related('patient', 'visit', 'data_recorder', 'imaging'),
        id=imaging_id
    )

    # Prepare context for rendering
    context = {
        'imaging': imaging,
    }

    # Render HTML content from template
    html_content = render_to_string('divine_admin_template/pdf_imaging_result.html', context)

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
    patient = get_object_or_404(RemotePatient, mrn=patient_mrn)
    visit = get_object_or_404(RemotePatientVisits, vst=visit_vst)

    # Fetch all imaging records for this visit
    imaging_records = RemoteImagingRecord.objects.filter(patient=patient, visit=visit).select_related(
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
    html_content = render_to_string('divine_admin_template/pdf_all_imaging_results.html', context)

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
def patient_imaging_view(request):
    # Get distinct (patient, visit) combinations with the latest imaging record date
    distinct_imaging_sets = (
        RemoteImagingRecord.objects
        .values('patient_id', 'visit_id')
        .annotate(latest_date=Max('created_at'))
        .order_by('-latest_date')
    )

    patient_imaging_data = []

    for entry in distinct_imaging_sets:
        patient_id = entry['patient_id']
        visit_id = entry['visit_id']
        latest_date = entry['latest_date']

        imaging_records = RemoteImagingRecord.objects.filter(
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

    return render(request, 'divine_admin_template/manage_imaging_result.html', context)