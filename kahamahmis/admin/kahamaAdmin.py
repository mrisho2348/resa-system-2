import calendar
from django.utils import timezone
import logging
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import  HttpResponse, JsonResponse
from kahamahmis.models import (
    KahamaChiefComplaint, KahamaCompany, KahamaConsultationNotes, KahamaDiagnosis, Country,  KahamaDiseaseRecode, KahamaHealthRecord, KahamaPatientVital,
    PathodologyRecord, KahamaMedicine, KahamaPatient, KahamaPatientVisits, 
    KahamaPrescription, KahamaProcedure, KahamaReagent, KahamaReferral, KahamaService,
    Staffs, KahamaObservationRecord,  KahamaCounseling, KahamaDischargesNotes,
    KahamaEquipment, KahamaLaboratoryRequest, KahamaAppointment
)
from clinic.models import ClinicCompany, CustomUser
from django.db.models import Max, Q, Count
from django.db.models.functions import ExtractMonth
from django.views.decorators.http import require_POST
from datetime import date, datetime
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash, logout
from weasyprint import HTML
import os
from django.template.loader import render_to_string

@login_required
def kahama_patient_list_view(request):
    patients = KahamaPatient.objects.select_related('company', 'nationality', 'data_recorder').all().order_by('-created_at')
    context = {'patients': patients}
    return render(request, 'divine_admin_template/kahama_patient_list.html', context)

@require_POST
@csrf_exempt
def delete_kahama_patient_view(request):
    patient_id = request.POST.get('patient_id')
    if not patient_id:
        return JsonResponse({'status': 'error', 'message': 'Missing patient ID'})

    try:
        patient = KahamaPatient.objects.get(id=patient_id)
        patient.delete()
        return JsonResponse({'status': 'success'})
    except KahamaPatient.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Patient not found'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})    

@login_required
def divine_dashboard(request):
    all_appointment = KahamaAppointment.objects.count()
    total_patients = KahamaPatient.objects.count()
    recently_added_patients = KahamaPatient.objects.order_by('-created_at')[:6]
    doctors = Staffs.objects.filter(role='doctor', work_place='kahama')
    doctors_count = doctors.count()
    nurses = Staffs.objects.filter(role='nurse', work_place='kahama').count()
    
    context = {
        'total_patients': total_patients,
        'recently_added_patients': recently_added_patients,
        'all_appointment': all_appointment,
        'doctors': doctors,
        'doctors_count': doctors_count,
        'nurses': nurses,
    }
    return render(request, "divine_admin_template/home_content.html", context)

def get_gender_yearly_data(request):
    if request.method == 'GET':
        selected_year = request.GET.get('year')
        
        # Query the database to get the total number of male and female patients for the selected year
        male_count = KahamaPatient.objects.filter(gender='Male', created_at__year=selected_year).count()
        female_count = KahamaPatient.objects.filter(gender='Female', created_at__year=selected_year).count()

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
            male_count = KahamaPatient.objects.filter(
                gender='Male',
                created_at__year=selected_year,
                created_at__month=month
            ).count()            
            female_count = KahamaPatient.objects.filter(
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

def get_patient_data_by_company(request):
    # Query patient data by company
    patient_data = {}

    companies = KahamaCompany.objects.all()
    for company in companies:
        patients_count = KahamaPatient.objects.filter(company=company).count()
        patient_data[company.name] = patients_count

    return JsonResponse(patient_data)  

def fetch_procedure_order_counts(request):
    """
    Fetch counts of procedure orders for the Kahama admin dashboard
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    # Count procedures without results (pending procedures)
    pending_procedure_count = KahamaProcedure.objects.filter(
        Q(result__isnull=True) | Q(result='')
    ).count()
    
    return JsonResponse({
        'unread_count': pending_procedure_count
    })

def fetch_laboratory_order_counts(request):
    """
    Fetch counts of laboratory orders for the Kahama admin dashboard
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    # Count lab requests without results (pending lab tests)
    pending_lab_count = KahamaLaboratoryRequest.objects.filter(
        Q(result__isnull=True) | Q(result='')
    ).count()
    
    return JsonResponse({
        'unread_count': pending_lab_count
    })

@login_required
def admin_profile(request):
    user = request.user
    try:
        staff = Staffs.objects.get(admin=user, role='admin')
        return render(request, 'divine_admin_template/profile.html', {'staff': staff})
    except Staffs.DoesNotExist:
        return render(request, 'divine_admin_template/profile.html', {'error': 'Admin not found.'})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was successfully updated! Please log in again.")
            logout(request)
            return redirect('kahamahmis:kahama_login')
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'divine_admin_template/change_password.html', {'form': form})            

@login_required
def expired_medicine_view(request):
    medicines = KahamaMedicine.objects.filter(
        is_clinic_stock=True,
        expiration_date__lt=timezone.now().date()
    )
    return render(request, 'divine_admin_template/expired_medicine.html', {'medicines': medicines})

@login_required
def instock_medicine_view(request):
    medicines = KahamaMedicine.objects.filter(
        is_clinic_stock=True,
        quantity__gt=0,
        expiration_date__gte=timezone.now().date()
    )
    return render(request, 'divine_admin_template/instock_medicine.html', {'medicines': medicines})

@login_required
def checklist_medicine_view(request):
    medicines = KahamaMedicine.objects.filter(is_clinic_stock=False)
    return render(request, 'divine_admin_template/checklist_medicine.html', {'medicines': medicines})

@login_required
def outofstock_medicine_view(request):
    medicines = KahamaMedicine.objects.filter(
        is_clinic_stock=True,
        quantity__lte=0
    )
    return render(request, 'divine_admin_template/outofstock_medicine.html', {'medicines': medicines})

@login_required
def manage_country(request):
    countries = Country.objects.all() 
    return render(request, "divine_admin_template/manage_country.html", {"countries": countries})

@login_required
def manage_company(request):
    companies = KahamaCompany.objects.all() 
    return render(request, "divine_admin_template/manage_company.html", {"companies": companies})

@login_required
def manage_disease(request):
    disease_records = KahamaDiseaseRecode.objects.all() 
    return render(request, "divine_admin_template/manage_disease.html", {"disease_records": disease_records})

@login_required
def manage_staff(request):     
    staffs = Staffs.objects.all()  
    return render(request, "divine_admin_template/manage_staff.html", {"staffs": staffs})  

@login_required
@require_POST
def update_staff_status(request):
    try:
        user_id = request.POST.get('user_id')
        is_active = request.POST.get('is_active')

        # Validate input
        if not user_id or is_active not in ['0', '1']:
            return JsonResponse({
                'success': False,
                'message': 'Invalid request data.'
            })

        staff = get_object_or_404(CustomUser, id=user_id)

        # Toggle status
        if is_active == '1':
            staff.is_active = False
            message_text = f'{staff.username} has been deactivated.'
        else:
            staff.is_active = True
            message_text = f'{staff.username} has been activated.'

        staff.save()

        return JsonResponse({
            'success': True,
            'message': message_text
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        })


@login_required
def reports_by_visit(request):
    patients = KahamaPatient.objects.all()
    patients_with_visit_counts = []
    for patient in patients:
        total_visits = KahamaPatientVisits.objects.filter(patient=patient).count()
        if total_visits > 0:
            patients_with_visit_counts.append({
                'patient': patient,
                'total_visits': total_visits
            })
    context = {'patients_with_visit_counts': patients_with_visit_counts}
    return render(request, 'divine_admin_template/reports_by_visit.html', context)

@login_required
def reports_patients_visit_summary(request):
    visits = KahamaPatientVisits.objects.all()
    context = {'visits': visits}
    return render(request, "divine_admin_template/reports_patients_visit_summary.html", context)

@login_required
def reports_patients(request):
    patients_report = KahamaPatient.objects.order_by('-created_at') 
    context = {'patients': patients_report}
    return render(request, "divine_admin_template/reports_patients.html", context)

@login_required
def individual_visit(request, patient_id):
    patient = get_object_or_404(KahamaPatient, id=patient_id)
    patient_visits = KahamaPatientVisits.objects.filter(patient=patient).order_by('-created_at')
    context = {'patient': patient, 'patient_visits': patient_visits}
    return render(request, 'divine_admin_template/reports_individual_visit.html', context)

@login_required
def manage_pathodology(request):
    pathodology_records = PathodologyRecord.objects.all()     
    return render(request, "divine_admin_template/manage_pathodology.html", {
        "pathodology_records": pathodology_records,
    })

@login_required
def patient_procedure_view(request):
    distinct_procedure_sets = (
        KahamaProcedure.objects
        .values('patient_id', 'visit_id')
        .annotate(latest_date=Max('created_at'))
        .order_by('-latest_date')
    )

    patient_procedures = []
    for entry in distinct_procedure_sets:
        patient_id = entry['patient_id']
        visit_id = entry['visit_id']
        latest_date = entry['latest_date']

        procedures = KahamaProcedure.objects.filter(
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
                'procedure_done_by': first_proc.doctor,
                'procedures': procedures
            })

    context = {'patient_procedures': patient_procedures}
    return render(request, 'divine_admin_template/manage_procedure.html', context)

@login_required
def manage_referral(request):
    referrals = KahamaReferral.objects.all()   
    return render(request, 'divine_admin_template/manage_referral.html', {'referrals': referrals})

@login_required
def appointment_list_view(request):
    appointments = KahamaAppointment.objects.all() 
    doctors = Staffs.objects.filter(role='doctor', work_place='kahama')   
    context = {        
        'appointments': appointments,
        'doctors': doctors        
    }
    return render(request, 'divine_admin_template/manage_appointment.html', context)

@csrf_exempt
@login_required
def add_disease(request):
    if request.method == 'POST':
        try:
            disease_id = request.POST.get('disease_id')
            disease_name = request.POST.get('Disease').strip()
            code = request.POST.get('Code').strip()

            if disease_id:
                disease = KahamaDiseaseRecode.objects.get(pk=disease_id)
                if KahamaDiseaseRecode.objects.exclude(pk=disease_id).filter(disease_name=disease_name).exists():
                    return JsonResponse({'success': False, 'message': 'Another disease with the same name already exists'})                    
                if KahamaDiseaseRecode.objects.exclude(pk=disease_id).filter(code=code).exists():
                    return JsonResponse({'success': False, 'message': 'Another disease with the same code already exists'})
                
                disease.data_recorder = request.user.staff 
                disease.disease_name = disease_name
                disease.code = code
                disease.save()
                return JsonResponse({'success': True, 'message': 'Disease updated successfully'})
            else:
                if KahamaDiseaseRecode.objects.filter(disease_name=disease_name).exists():
                    return JsonResponse({'success': False, 'message': 'Another disease with the same name already exists'})            
                if KahamaDiseaseRecode.objects.filter(code=code).exists():
                    return JsonResponse({'success': False, 'message': 'Another disease with the same code already exists'})

                KahamaDiseaseRecode.objects.create(
                    disease_name=disease_name, 
                    data_recorder=request.user.staff,
                    code=code
                )
                return JsonResponse({'success': True, 'message': 'Disease added successfully'})

        except IntegrityError:
            return JsonResponse({'success': False, 'message': 'Disease already exists'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
    
@require_POST
def delete_kahama_company(request):
    company_id = request.POST.get('company_id')
    try:
        KahamaCompany.objects.get(id=company_id).delete()
        return JsonResponse({'success': True})
    except KahamaCompany.DoesNotExist:
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

            if company_id:
                try:
                    company = KahamaCompany.objects.get(pk=company_id)
                    if KahamaCompany.objects.filter(name=name).exclude(pk=company_id).exists():
                        return JsonResponse({'success': False, 'message': 'Company name already exists.'})
                    company.name = name
                    company.save()
                    return JsonResponse({'success': True, 'message': 'Company updated successfully.'})
                except KahamaCompany.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Company not found.'})
            else:
                if KahamaCompany.objects.filter(name=name).exists():
                    return JsonResponse({'success': False, 'message': 'Company already exists.'})
                KahamaCompany.objects.create(name=name)
                return JsonResponse({'success': True, 'message': 'Company added successfully.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})
  
@csrf_exempt
@login_required
def add_pathodology_record(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('Name').strip()
            description = request.POST.get('Description')
            pathology_record_id = request.POST.get('pathology_record_id')
            
            if pathology_record_id:             
                if PathodologyRecord.objects.exclude(pk=pathology_record_id).filter(name=name).exists():
                    return JsonResponse({'success': False, 'message':  f'Another pathology record with the name "{name}" already exists'})
                pathology_record = PathodologyRecord.objects.get(pk=pathology_record_id)
                pathology_record.data_recorder = request.user.staff 
                pathology_record.name = name
                pathology_record.description = description
                pathology_record.save()
                return JsonResponse({'success': True, 'message': 'Pathology updated successfully'})
            else:
                if PathodologyRecord.objects.filter(name=name).exists():
                    return JsonResponse({'success': False, 'message':  f'A pathology record with the name "{name}" already exists'})
                PathodologyRecord.objects.create(
                    name=name,
                    data_recorder=request.user.staff,
                    description=description
                )
                return JsonResponse({'success': True, 'message': f'{name} added successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
def prescription_list(request):
    prescriptions = KahamaPrescription.objects.select_related(
        'visit', 'patient', 'medicine', 'frequency'
    ).order_by('-visit__created_at')

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

    visit_groups = sorted(
        grouped_visits.values(), key=lambda v: v['visit'].created_at, reverse=True
    )

    return render(request, 'divine_admin_template/manage_prescription_list.html', {
        'visit_groups': visit_groups,
    })

@login_required
def consultation_notes_view(request):
    patient_records = (
        KahamaPatient.objects.filter(consultation_notes__isnull=False)
        .distinct()
        .order_by('-consultation_notes__updated_at')
    )

    return render(request, 'divine_admin_template/manage_consultation_notes.html', {
        'patient_records': patient_records
    })


@login_required
def diagnosis_list(request):
    diagnoses = KahamaDiagnosis.objects.all().order_by('-created_at')    
    return render(request, 'divine_admin_template/manage_diagnosis_list.html', {'diagnoses': diagnoses}) 

@csrf_exempt
@require_POST
def delete_diagnosis(request):
    try:
        diagnosis_id = request.POST.get('diagnosis_id')
        diagnosis = get_object_or_404(KahamaDiagnosis, pk=diagnosis_id)
        diagnosis.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
@csrf_exempt
@require_POST
def save_diagnosis(request):
    try:
        diagnosis_name = request.POST.get('diagnosis_name', '').strip()
        diagnosis_code = request.POST.get('diagnosis_code', '').strip()
        diagnosis_id = request.POST.get('diagnosis_id', '')

        if diagnosis_id:
            try:
                diagnosis = KahamaDiagnosis.objects.get(pk=diagnosis_id)
            except KahamaDiagnosis.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Diagnosis not found.'})

            if KahamaDiagnosis.objects.exclude(pk=diagnosis_id).filter(diagnosis_name=diagnosis_name).exists():
                return JsonResponse({'success': False, 'message': 'Diagnosis with this name already exists.'})
            if KahamaDiagnosis.objects.exclude(pk=diagnosis_id).filter(diagnosis_code=diagnosis_code).exists():
                return JsonResponse({'success': False, 'message': 'Diagnosis with this code already exists.'})

            diagnosis.data_recorder = request.user.staff 
            diagnosis.diagnosis_name = diagnosis_name
            diagnosis.diagnosis_code = diagnosis_code
            diagnosis.save()
            return JsonResponse({'success': True, 'message': 'Diagnosis updated successfully.'})
        else:
            if KahamaDiagnosis.objects.filter(diagnosis_name=diagnosis_name).exists():
                return JsonResponse({'success': False, 'message': 'Diagnosis with this name already exists.'})
            if KahamaDiagnosis.objects.filter(diagnosis_code=diagnosis_code).exists():
                return JsonResponse({'success': False, 'message': 'Diagnosis with this code already exists.'})

            KahamaDiagnosis.objects.create(
                diagnosis_name=diagnosis_name,
                data_recorder=request.user.staff,
                diagnosis_code=diagnosis_code,
            )
            return JsonResponse({'success': True, 'message': 'Diagnosis added successfully.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
def kahamaservice_list(request):
    services = KahamaService.objects.all()
    return render(request, 'divine_admin_template/service_list.html', {'services': services})

@login_required
@csrf_exempt
@require_POST
def save_kahama_service(request):
    try:
        service_id = request.POST.get('service_id')
        name = request.POST.get('name').strip()
        description = request.POST.get('description')
        category = request.POST.get('category')
        data_recorder = request.user.staff 
        
        if service_id:
            service = KahamaService.objects.get(pk=service_id)
            if KahamaService.objects.exclude(pk=service_id).filter(name=name, data_recorder=data_recorder).exists():
                return JsonResponse({'success': False, 'message': f'A service with the name "{name}" already exists.'})
            service.data_recorder = data_recorder
            service.name = name
            service.description = description
            service.category = category
            service.save()
            return JsonResponse({'success': True, 'message': 'Updated successfully'})
        else:
            if KahamaService.objects.filter(name=name).exists():
                return JsonResponse({'success': False, 'message': f'A service with the name "{name}" already exists.'})
            KahamaService.objects.create(
                name=name, 
                description=description, 
                category=category,
                data_recorder=data_recorder
            )
            return JsonResponse({'success': True, 'message': 'Added successfully'})
    except KahamaService.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Service not found.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
   
@login_required
def counseling_list_view(request):
    counselings = KahamaCounseling.objects.all().order_by('-created_at')
    return render(request, 'divine_admin_template/manage_counselling.html', {'counselings': counselings})    

@login_required
def observation_record_list_view(request):
    observation_records = KahamaObservationRecord.objects.all().order_by('-created_at')
    return render(request, 'divine_admin_template/manage_observation_record.html', {'observation_records': observation_records})

@login_required
def discharge_notes_list_view(request):
    discharge_notes = KahamaDischargesNotes.objects.all().order_by('-discharge_date')
    return render(request, 'divine_admin_template/manage_discharge.html', {'discharge_notes': discharge_notes})

@csrf_exempt    
def delete_discharge_note(request):
    if request.method == 'POST':
        try:
            observation_id = request.POST.get('observation_id')
            observation = KahamaDischargesNotes.objects.get(id=observation_id)
            observation.delete()
            return JsonResponse({'success': True, 'message': f'Discharge record deleted successfully.'})
        except KahamaDischargesNotes.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid observation ID.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {e}'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})    

@login_required
def health_record_list(request):
    records = KahamaHealthRecord.objects.all()
    return render(request, 'divine_admin_template/healthrecord_list.html', {'records': records})


@login_required
def resa_report(request):
    return render(request,"divine_admin_template/resa_reports.html")    

@login_required    
def patient_statistics(request):
    current_year = datetime.now().year
    year_range = range(current_year, current_year - 10, -1)
    context = {
        'year_range': year_range,
        'current_year': current_year,
    }
    return render(request, 'divine_admin_template/reports_comprehensive.html', context)

@login_required
def search_report(request):
    if request.method == 'POST' and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        report_type = request.POST.get('report_type')
        year = request.POST.get('year')
        report_templates = {
            'patient_type_reports': 'divine_admin_template/patient_type_report_table.html',
            'patient_company_wise_reports': 'divine_admin_template/company_wise_reports_table.html',
            'patient_lab_result_reports': 'divine_admin_template/laboratory_report_table.html',
            'patient_procedure_reports': 'divine_admin_template/procedure_report_table.html',
            'patient_referral_reports': 'divine_admin_template/referral_reports_table.html',
            'patient_pathology_reports': 'divine_admin_template/pathology_record_report_table.html',
        }
        if report_type in report_templates:
            html_result = render_report(report_type, year)
            return JsonResponse({'html_result': html_result})
        else:
            return JsonResponse({'error': 'Invalid report type'})

def render_report(report_type, year):
    if report_type == 'patient_type_reports':       
        all_patient_types =  ['National Staff', 'International Staff', 'National Visitor', 'International Visitor', 'Unknown Status','Permanent','Temporary','Visitor', 'Others']
        patients_by_type = (
            KahamaPatient.objects.filter(created_at__year=year)
            .values('patient_type')
            .annotate(month=ExtractMonth('created_at'))
            .annotate(num_patients=Count('id'))
        )
        patient_type_reports = {}
        for patient_type in all_patient_types:
            patient_type_reports[patient_type] = [0] * 12
        for patient in patients_by_type:
            patient_type = patient['patient_type']
            month = patient['month']
            num_patients = patient['num_patients']
            if month is not None:
                month_index = month - 1
                patient_type_reports[patient_type][month_index] = num_patients
        context = {
            'patient_type_reports': patient_type_reports,
            'months': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        }
        return render_to_string('divine_admin_template/patient_type_report_table.html', context)
    elif report_type == 'patient_company_wise_reports':    
        all_companies = KahamaCompany.objects.values_list('name', flat=True)
        patients_by_company = (
            KahamaPatient.objects.filter(created_at__year=year)
            .values('company__name')
            .annotate(month=ExtractMonth('created_at'))
            .annotate(num_patients=Count('id'))
        )
        company_reports = {company: [0] * 12 for company in all_companies}
        for patient in patients_by_company:
            company_name = patient['company__name']
            month = patient['month']
            num_patients = patient['num_patients']
            if month is not None:
                month_index = month - 1
                company_reports[company_name][month_index] = num_patients
        context = {
            'company_reports': company_reports,
            'months': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        }
        return render_to_string('divine_admin_template/company_wise_reports_table.html', context)
    elif report_type == 'patient_lab_result_reports':      
        laboratory_services = KahamaService.objects.filter(category='Laboratory')
        laboratories_by_month = (
            KahamaLaboratoryRequest.objects.filter(created_at__year=year)
            .annotate(month=ExtractMonth('created_at'))
            .values('name__name', 'month')
            .annotate(num_patients=Count('id'))
        )
        laboratory_reports = {}
        for laboratory_service in laboratory_services:
            laboratory_name = laboratory_service.name
            laboratory_reports[laboratory_name] = [0] * 12
        for laboratory in laboratories_by_month:
            laboratory_name = laboratory['name__name']
            month = laboratory['month']
            num_patients = laboratory['num_patients']
            if month is not None:
                month_index = int(month) - 1
                laboratory_reports[laboratory_name][month_index] = num_patients
        context = {
            'laboratory_reports': laboratory_reports,
            'months': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        }
        return render_to_string('divine_admin_template/laboratory_report_table.html', context)
    elif report_type == 'patient_procedure_reports':      
        procedure_services = KahamaService.objects.filter(category='Procedure')
        procedures_by_month = (
            KahamaProcedure.objects.filter(created_at__year=year)
            .annotate(month=ExtractMonth('created_at'))
            .values('name__name', 'month')
            .annotate(num_patients=Count('id'))
        )
        procedure_reports = {}
        for procedure_service in procedure_services:
            procedure_name = procedure_service.name
            procedure_reports[procedure_name] = [0] * 12
        for procedure in procedures_by_month:
            procedure_name = procedure['name__name']
            month = procedure['month']
            num_patients = procedure['num_patients']
            if month is not None:
                month_index = int(month) - 1
                procedure_reports[procedure_name][month_index] = num_patients
        context = {
            'procedure_reports': procedure_reports,
            'months': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        }
        return render_to_string('divine_admin_template/procedure_report_table.html', context)
    elif report_type == 'patient_referral_reports':
        referrals = KahamaReferral.objects.filter(created_at__year=year)
        context = {'referrals': referrals}
        return render_to_string('divine_admin_template/referral_reports_table.html', context)
    elif report_type == 'patient_pathology_reports':
        all_pathology_records = PathodologyRecord.objects.values_list('name', flat=True)
        patients_by_pathology_record = (
            PathodologyRecord.objects.filter(kahamaconsultationnotes__created_at__year=year)
            .annotate(month=ExtractMonth('kahamaconsultationnotes__created_at'))
            .values('name', 'month')
            .annotate(num_patients=Count('kahamaconsultationnotes__id'))
        )
        pathology_record_reports = {record: [0] * 12 for record in all_pathology_records}
        for patient in patients_by_pathology_record:
            pathology_record_name = patient['name']
            month = patient['month']
            num_patients = patient['num_patients']
            if month is not None:
                month_index = int(month) - 1
                pathology_record_reports[pathology_record_name][month_index] = num_patients
        context = {
            'pathology_record_reports': pathology_record_reports,
            'months': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        }
        return render_to_string('divine_admin_template/pathology_record_report_table.html',context)

@login_required
@csrf_exempt
def save_health_record(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name').strip()
            health_record_id = request.POST.get('health_record_id')
            
            if health_record_id:
                health_record = KahamaHealthRecord.objects.get(pk=health_record_id)
                if KahamaHealthRecord.objects.exclude(pk=health_record_id).filter(name=name).exists():
                    return JsonResponse({'success': False, 'message': f'A record with the name "{name}" already exists.'})
                health_record.name = name
                health_record.data_recorder = request.user.staff 
                health_record.save()
            else:
                if KahamaHealthRecord.objects.filter(name=name).exists():
                    return JsonResponse({'success': False, 'message': f'A record with the name "{name}" already exists.'})
                KahamaHealthRecord.objects.create(
                    name=name, 
                    data_recorder=request.user.staff
                )
            return JsonResponse({'success': True, 'message': 'Successfully saved.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@csrf_exempt
@login_required
def delete_healthrecord(request):
    if request.method == 'POST':
        health_record_id = request.POST.get('health_record_id')
        try:
            health_record = get_object_or_404(KahamaHealthRecord, pk=health_record_id)
            health_record.delete()
            return JsonResponse({'success': True, 'message': f'Health record {health_record.name} deleted successfully.'})
        except KahamaHealthRecord.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid health record ID.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {e}'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

@login_required
def kahamamedicine_list(request):
    medicines = KahamaMedicine.objects.all()
    today = date.today()
    for medicine in medicines:
        if medicine.expiration_date:
            medicine.days_left = (medicine.expiration_date - today).days
        else:
            medicine.days_left = None
    return render(request, 'divine_admin_template/kahamamedicine_list.html', {'medicines': medicines, 'today': date.today()})

@login_required
@csrf_exempt
def add_kahama_medicine(request):
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
                try:
                    medicine = KahamaMedicine.objects.get(pk=drug_id)
                except KahamaMedicine.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Medicine not found for editing.'})

                if KahamaMedicine.objects.exclude(pk=drug_id).filter(drug_name=drug_name).exists():
                    return JsonResponse({'success': False, 'message': 'Another medicine with the same name already exists'})
                if KahamaMedicine.objects.exclude(pk=drug_id).filter(batch_number=batch_number).exists():
                    return JsonResponse({'success': False, 'message': 'Another medicine with the same batch number already exists'})

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
                if KahamaMedicine.objects.filter(drug_name=drug_name).exists():
                    return JsonResponse({'success': False, 'message': 'Medicine with the same name already exists'})
                if KahamaMedicine.objects.filter(batch_number=batch_number).exists():
                    return JsonResponse({'success': False, 'message': 'Medicine with the same batch number already exists'})

                medicine = KahamaMedicine(
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

@login_required
def medicine_count_api(request):
    today = timezone.now().date()
    expired_count = KahamaMedicine.objects.filter(is_clinic_stock=True, expiration_date__lt=today).count()
    instock_count = KahamaMedicine.objects.filter(is_clinic_stock=True, quantity__gt=0, expiration_date__gte=today).count()
    checklist_count = KahamaMedicine.objects.filter(is_clinic_stock=False).count()
    outofstock_count = KahamaMedicine.objects.filter(is_clinic_stock=True, quantity__lte=0).count()
    total_count = KahamaMedicine.objects.all().count()

    return JsonResponse({
        "expired": expired_count,
        "instock": instock_count,
        "checklist": checklist_count,
        "outofstock": outofstock_count,
        "all": total_count
    })

@csrf_exempt
@login_required
def delete_kahama_medicine(request):
    if request.method == 'POST':
        medicine_id = request.POST.get('medicine_id')
        try:
            medicine = get_object_or_404(KahamaMedicine, pk=medicine_id)
            medicine.delete()
            return JsonResponse({'success': True, 'message': 'Medicine deleted successfully.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

@login_required
def company_registration_view(request):
    try:
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

            if company:
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
                company.data_recorder = request.user.staff
                company.save()
                messages.success(request, 'Company updated successfully!')
            else:
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
                    data_recorder=request.user.staff
                )
                new_company.save()
                messages.success(request, 'Company added successfully!')
            return redirect('divine_add_clinic_company')
        else:
            return render(request, 'divine_admin_template/company_registration.html', {'company': company})
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return render(request, 'divine_admin_template/company_registration.html')

@login_required
def kahama_equipment_list(request):
    equipment_list = KahamaEquipment.objects.all()
    return render(request, 'divine_admin_template/kahama_equipment_list.html', {'equipment_list': equipment_list})

@login_required    
@csrf_exempt
def add_or_edit_kahama_equipment(request):
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

        try:
            if equipment_id:
                equipment = KahamaEquipment.objects.get(id=equipment_id)
                if KahamaEquipment.objects.exclude(id=equipment_id).filter(name=name).exists():
                    return JsonResponse({'success': False, 'message': 'Equipment with this name already exists.'})
                if KahamaEquipment.objects.exclude(id=equipment_id).filter(serial_number=serial_number).exists():
                    return JsonResponse({'success': False, 'message': 'Equipment with this serial number already exists.'})
                equipment.name = name
                equipment.description = description
                equipment.serial_number = serial_number
                equipment.manufacturer = manufacturer
                equipment.purchase_date = purchase_date
                equipment.warranty_expiry_date = warranty_expiry_date
                equipment.location = location
                equipment.status = status
                equipment.data_recorder = request.user.staff
                equipment.save()
                return JsonResponse({'success': True, 'message': 'Equipment updated successfully!'})
            else:
                if KahamaEquipment.objects.filter(name=name).exists():
                    return JsonResponse({'success': False, 'message': 'Equipment with this name already exists.'})
                if KahamaEquipment.objects.filter(serial_number=serial_number).exists():
                    return JsonResponse({'success': False, 'message': 'Equipment with this serial number already exists.'})
                KahamaEquipment.objects.create(
                    name=name,
                    description=description,
                    serial_number=serial_number,
                    manufacturer=manufacturer,
                    purchase_date=purchase_date,
                    warranty_expiry_date=warranty_expiry_date,
                    location=location,
                    status=status,
                    data_recorder=request.user.staff
                )
                return JsonResponse({'success': True, 'message': 'Equipment added successfully!'})
        except KahamaEquipment.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Equipment not found.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
@csrf_exempt
def delete_kahama_equipment(request):
    if request.method == 'POST':
        equipment_id = request.POST.get('id')
        try:
            equipment = KahamaEquipment.objects.get(id=equipment_id)
            equipment.delete()
            return JsonResponse({'status': 'true', 'message': 'Equipment deleted successfully!'})
        except KahamaEquipment.DoesNotExist:
            return JsonResponse({'status': 'false', 'message': 'Equipment not found.'})
        except Exception as e:
            return JsonResponse({'status': 'false', 'message': str(e)})
    return JsonResponse({'status': 'false', 'message': 'Invalid request method'})

@login_required
def kahama_reagent_list(request):
    reagent_list = KahamaReagent.objects.all()
    return render(request, 'divine_admin_template/kahama_reagent_list.html', {'reagent_list': reagent_list})

@login_required
def patient_laboratory_view(request):
    # Get distinct (patient, visit) combinations with latest result date
    distinct_lab_sets = (
        KahamaLaboratoryRequest.objects
        .values('patient_id', 'visit_id')
        .annotate(latest_date=Max('created_at'))
        .order_by('-latest_date')
    )

    patient_lab_data = []

    for entry in distinct_lab_sets:
        patient_id = entry['patient_id']
        visit_id = entry['visit_id']
        latest_date = entry['latest_date']

        lab_tests = KahamaLaboratoryRequest.objects.filter(
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

@login_required    
@csrf_exempt
def add_or_edit_kahama_reagent(request):
    if request.method == 'POST':
        data = request.POST
        reagent_id = data.get('reagent_id')
        name = data.get('name').strip()
        supplier = data.get('supplier', '')
        quantity = data.get('quantity')
        expiry_date = data.get('expiry_date')
        storage_conditions = data.get('storage_conditions', '')

        try:
            if reagent_id:
                reagent = KahamaReagent.objects.get(id=reagent_id)
                if KahamaReagent.objects.exclude(id=reagent_id).filter(name=name).exists():
                    return JsonResponse({'success': False, 'message': 'A reagent with the same name already exists.'})
                reagent.name = name
                reagent.supplier = supplier
                reagent.quantity = quantity
                reagent.expiry_date = expiry_date
                reagent.storage_conditions = storage_conditions
                reagent.data_recorder = request.user.staff
                reagent.save()
                return JsonResponse({'success': True, 'message': 'Reagent updated successfully!'})
            else:
                if KahamaReagent.objects.filter(name=name).exists():
                    return JsonResponse({'success': False, 'message': 'A reagent with the same name already exists.'})
                KahamaReagent.objects.create(
                    name=name,
                    supplier=supplier,
                    quantity=quantity,
                    expiry_date=expiry_date,
                    storage_conditions=storage_conditions,
                    data_recorder=request.user.staff
                )
                return JsonResponse({'success': True, 'message': 'Reagent added successfully!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
@csrf_exempt
def delete_kahama_reagent(request):
    if request.method == 'POST':
        reagent_id = request.POST.get('id')
        try:
            reagent = KahamaReagent.objects.get(id=reagent_id)
            reagent.delete()
            return JsonResponse({'status': 'true', 'message': 'Reagent deleted successfully'})
        except KahamaReagent.DoesNotExist:
            return JsonResponse({'status': 'false', 'message': 'Reagent does not exist'})
        except Exception as e:
            return JsonResponse({'status': 'false', 'message': str(e)})
    return JsonResponse({'status': 'false', 'message': 'Invalid request method'})

@login_required
@csrf_exempt
def delete_counseling_session(request):
    if request.method == 'POST':
        reagent_id = request.POST.get('id')
        try:
            reagent = KahamaCounseling.objects.get(id=reagent_id)
            reagent.delete()
            return JsonResponse({'status': 'true', 'message': 'Counsel record deleted successfully'})
        except KahamaCounseling.DoesNotExist:
            return JsonResponse({'status': 'false', 'message': 'Counsel record  does not exist'})
        except Exception as e:
            return JsonResponse({'status': 'false', 'message': str(e)})
    return JsonResponse({'status': 'false', 'message': 'Invalid request method'})

# ... (Include the rest of the report views from the original code, updating models to Kahama equivalents) ...

@csrf_exempt
@require_POST
def delete_consultation(request):
    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        try:
            appointment = KahamaAppointment.objects.get(id=appointment_id)
            appointment.delete()
            return JsonResponse({'status': 'success'})
        except KahamaAppointment.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Appointment not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
@login_required
def delete_pathology_record(request):
    if request.method == 'POST':
        try:
            pathology_record_id = request.POST.get('pathology_record_id')
            pathology_record = PathodologyRecord.objects.get(id=pathology_record_id)
            pathology_record_name = pathology_record.name
            pathology_record.delete()
            return JsonResponse({'success': True, 'message': f'Pathology record "{pathology_record_name}" deleted successfully.'})
        except PathodologyRecord.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Pathology record not found.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error deleting record: {str(e)}'})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@csrf_exempt    
def delete_observation(request):
    if request.method == 'POST':
        try:
            observation_id = request.POST.get('observation_id')
            observation = KahamaObservationRecord.objects.get(id=observation_id)
            observation.delete()
            return JsonResponse({'success': True, 'message': f'Observation record deleted successfully.'})
        except KahamaObservationRecord.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid observation ID.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {e}'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})



@csrf_exempt    
def delete_lab_result(request):
    if request.method == 'POST':
        try:
            lab_result_id = request.POST.get('lab_result_id')
            lab_result = KahamaLaboratoryRequest.objects.get(id=lab_result_id)
            lab_result.delete()
            return JsonResponse({'success': True, 'message': f'Lab result record deleted successfully.'})
        except KahamaLaboratoryRequest.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid lab result ID.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {e}'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

@csrf_exempt    
def delete_referral(request):
    if request.method == 'POST':
        try:
            referral_id = request.POST.get('referral_id')
            referral_record = KahamaReferral.objects.get(id=referral_id)
            referral_record.delete()
            return JsonResponse({'success': True, 'message': f'Referral record deleted successfully.'})
        except KahamaReferral.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid Referral ID.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {e}'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

@csrf_exempt
def delete_disease_record(request):
    if request.method == 'POST':
        disease_id = request.POST.get('disease_id')
        if disease_id:
            try:
                disease = KahamaDiseaseRecode.objects.get(id=disease_id)
                disease.delete()
                return JsonResponse({'status': 'success', 'message': 'Disease deleted successfully'})
            except KahamaDiseaseRecode.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Disease not found'}, status=404)
        return JsonResponse({'status': 'error', 'message': 'Invalid disease ID'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@login_required
@csrf_exempt
def delete_kahama_company(request):
    if request.method == 'POST':
        company_id = request.POST.get('company_id')
        if not company_id:
            return JsonResponse({'success': False, 'error': 'Company ID not provided'})
        try:
            company = get_object_or_404(KahamaCompany, pk=company_id)
            company.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@require_POST
def delete_service(request):
    try:
        service_id = request.POST.get('service_id')
        service = KahamaService.objects.get(id=service_id)
        service.delete()
        return JsonResponse({'success': True,'message': 'Service deleted successfully'})
    except KahamaService.DoesNotExist:
        return JsonResponse({'success': False,'message': 'Service not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@csrf_exempt      
@require_POST
def delete_procedure(request):
    if request.method == 'POST':
        procedure_id = request.POST.get('procedure_id')
        try:
            procedure = KahamaProcedure.objects.get(id=procedure_id)
            procedure.delete()
            return JsonResponse({'status': 'success', 'message': 'Procedure deleted successfully.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

@login_required
def download_referral_pdf(request, patient_id, visit_id):
    """View for downloading referrals as PDF"""
    visit = get_object_or_404(KahamaPatientVisits, id=visit_id)
    patient = get_object_or_404(KahamaPatient, id=patient_id)
    referral = get_object_or_404(KahamaReferral, patient=patient, visit=visit)
    
    context = {
        'referral': referral,
        'patient': patient,
        'visit': visit,
    }
    
    html_content = render_to_string('kahama_template/view_referral.html', context)
    temp_dir = os.path.join(os.path.expanduser("~"), "pdf_temp")
    os.makedirs(temp_dir, exist_ok=True)
    file_name = f'referral_{patient.full_name}_{visit.vst}.pdf'
    file_path = os.path.join(temp_dir, file_name)
    
    if os.path.exists(file_path):
        os.remove(file_path)
        
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(file_path)
    
    with open(file_path, 'rb') as f:
        pdf_data = f.read()
        
    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response     

@login_required
def download_consultation_summary_pdf(request, patient_id, visit_id):
    """View for downloading consultation summary as PDF"""
    # Fetch core patient and visit info
    patient = get_object_or_404(KahamaPatient, id=patient_id)
    visit = get_object_or_404(KahamaPatientVisits, id=visit_id)

    # Query all related models for that visit
    counseling = KahamaCounseling.objects.filter(patient=patient, visit=visit).last()
    prescriptions = KahamaPrescription.objects.filter(patient=patient, visit=visit)
    observations = KahamaObservationRecord.objects.filter(patient=patient, visit=visit).last()
    discharge_note = KahamaDischargesNotes.objects.filter(patient=patient, visit=visit).last()
    referral = KahamaReferral.objects.filter(patient=patient, visit=visit).last()
    complaints = KahamaChiefComplaint.objects.filter(patient=patient, visit=visit)
    vitals = KahamaPatientVital.objects.filter(patient=patient, visit=visit).last()

    # Add Consultation Notes
    consultation_note = KahamaConsultationNotes.objects.filter(patient=patient, visit=visit).last()   

    # Add Laboratory Orders
    lab_tests = KahamaLaboratoryRequest.objects.filter(patient=patient, visit=visit).select_related('name', 'data_recorder')

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
        'lab_tests': lab_tests,
    }

    # Render the HTML template
    html_content = render_to_string('kahama_template/pdf_consultation_summary.html', context)

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
def download_counseling_pdf(request, patient_id, visit_id):
    """View for downloading counseling notes as PDF"""
    visit = get_object_or_404(KahamaPatientVisits, id=visit_id)
    patient = get_object_or_404(KahamaPatient, id=patient_id)
    counseling = get_object_or_404(KahamaCounseling, patient=patient, visit=visit)
    
    context = {
        'counseling': counseling,
        'patient': patient,
        'visit': visit,
    }
    
    html_content = render_to_string('kahama_template/counseling_notes_details.html', context)
    temp_dir = os.path.join(os.path.expanduser("~"), "pdf_temp")
    os.makedirs(temp_dir, exist_ok=True)
    file_name = f'counseling_{patient.full_name}_{visit.vst}.pdf'
    file_path = os.path.join(temp_dir, file_name)
    
    if os.path.exists(file_path):
        os.remove(file_path)
        
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(file_path)
    
    with open(file_path, 'rb') as f:
        pdf_data = f.read()
        
    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response 

@login_required
def download_discharge_pdf(request, patient_id, visit_id):
    """View for downloading discharge notes as PDF"""
    visit = get_object_or_404(KahamaPatientVisits, id=visit_id)
    patient = get_object_or_404(KahamaPatient, id=patient_id)
    discharge_note = get_object_or_404(KahamaDischargesNotes, patient=patient, visit=visit)
    
    context = {
        'discharge_note': discharge_note,
        'patient': patient,
        'visit': visit,
    }
    
    html_content = render_to_string('kahama_template/discharge_note_detail.html', context)
    temp_dir = os.path.join(os.path.expanduser("~"), "pdf_temp")
    os.makedirs(temp_dir, exist_ok=True)
    file_name = f'discharge_{patient.full_name}_{visit.vst}.pdf'
    file_path = os.path.join(temp_dir, file_name)
    
    if os.path.exists(file_path):
        os.remove(file_path)
        
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(file_path)
    
    with open(file_path, 'rb') as f:
        pdf_data = f.read()
        
    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response     


@login_required
def download_lab_result_pdf(request, lab_id):
    """View for downloading lab results as PDF"""
    # Fetch the lab order or return 404 if not found
    lab = get_object_or_404(
        KahamaLaboratoryRequest.objects.select_related('patient', 'visit', 'data_recorder', 'name'),
        id=lab_id
    )

    # Prepare context for PDF rendering
    context = {
        'lab': lab,
    }

    # Render HTML from template
    html_content = render_to_string('kahama_template/pdf_lab_result.html', context)

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
    """View for downloading all lab results for a patient as PDF"""
    # Fetch patient and visit objects
    patient = get_object_or_404(KahamaPatient, mrn=patient_mrn)
    visit = get_object_or_404(KahamaPatientVisits, vst=visit_vst)

    # Fetch all laboratory orders for this patient and visit
    lab_tests = KahamaLaboratoryRequest.objects.filter(patient=patient, visit=visit).select_related(
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
    html_content = render_to_string('kahama_template/pdf_all_lab_results.html', context)

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
def download_observation_pdf(request, patient_id, visit_id):
    """View for downloading observation records as PDF"""
    # Fetch the required patient and visit
    visit = get_object_or_404(KahamaPatientVisits, id=visit_id)
    patient = get_object_or_404(KahamaPatient, id=patient_id)
    observation_record = get_object_or_404(KahamaObservationRecord, patient=patient, visit=visit)

    # Prepare context for the template
    context = {
        'observation_record': observation_record,
        'visit': visit,
    }

    # Render HTML template
    html_content = render_to_string('kahama_template/observation_notes_detail.html', context)

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


@login_required
def download_prescription_notes_pdf(request, patient_id, visit_id):
    """View for downloading prescription notes as PDF"""
    # Fetch patient and visit
    patient = get_object_or_404(KahamaPatient, id=patient_id)
    visit = get_object_or_404(KahamaPatientVisits, id=visit_id)

    # Get all prescriptions for this patient and visit
    prescriptions = KahamaPrescription.objects.filter(patient=patient, visit=visit)

    # Prepare context
    context = {
        'patient': patient,
        'visit': visit,
        'prescriptions': prescriptions,
    }

    # Render HTML content using a dedicated template
    html_content = render_to_string('kahama_template/prescription_notes.html', context)

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
    """View for downloading procedure results as PDF"""
    procedure = get_object_or_404(KahamaProcedure.objects.select_related('patient', 'visit', 'name'), id=procedure_id)
    
    context = {
        'procedure': procedure,
    }
    
    html_content = render_to_string('kahama_template/pdf_procedure_result.html', context)
    temp_dir = os.path.join(os.path.expanduser("~"), "pdf_temp")
    os.makedirs(temp_dir, exist_ok=True)
    file_name = f"procedure_result_{procedure.patient.full_name}.pdf"
    file_path = os.path.join(temp_dir, file_name)
    
    if os.path.exists(file_path):
        os.remove(file_path)
        
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(file_path)
    
    with open(file_path, 'rb') as f:
        pdf_data = f.read()
        
    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response    


@login_required
def download_all_procedures_pdf(request, patient_mrn, visit_vst):
    """View for downloading all procedures as PDF"""
    patient = get_object_or_404(KahamaPatient, mrn=patient_mrn)
    visit = get_object_or_404(KahamaPatientVisits, vst=visit_vst)
    procedures = KahamaProcedure.objects.filter(patient=patient, visit=visit).select_related('name')
    
    if not procedures.exists():
        return HttpResponse("No procedures found for this visit.", status=404)
        
    context = {
        'patient': patient,
        'visit': visit,
        'procedures': procedures
    }
    
    html_content = render_to_string('kahama_template/pdf_all_procedures.html', context)
    file_name = f"all_procedures_{patient.full_name}_{visit.vst}.pdf"
    temp_dir = os.path.join(os.path.expanduser("~"), "pdf_temp")
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file_name)
    
    if os.path.exists(file_path):
        os.remove(file_path)
        
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(file_path)
    
    with open(file_path, 'rb') as f:
        pdf_data = f.read()
        
    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response 

@login_required
def download_consultation_summary_pdf(request, patient_id, visit_id):
    """View for downloading consultation summary as PDF"""
    # Fetch core patient and visit info
    patient = get_object_or_404(KahamaPatient, id=patient_id)
    visit = get_object_or_404(KahamaPatientVisits, id=visit_id)

    # Query all related models for that visit
    counseling = KahamaCounseling.objects.filter(patient=patient, visit=visit).last()
    prescriptions = KahamaPrescription.objects.filter(patient=patient, visit=visit)
    observations = KahamaObservationRecord.objects.filter(patient=patient, visit=visit).last()
    discharge_note = KahamaDischargesNotes.objects.filter(patient=patient, visit=visit).last()
    referral = KahamaReferral.objects.filter(patient=patient, visit=visit).last()
    complaints = KahamaChiefComplaint.objects.filter(patient=patient, visit=visit)
    vitals = KahamaPatientVital.objects.filter(patient=patient, visit=visit).last()

    # Add Consultation Notes
    consultation_note = KahamaConsultationNotes.objects.filter(patient=patient, visit=visit).last()   

    # Add Laboratory Orders
    lab_tests = KahamaLaboratoryRequest.objects.filter(patient=patient, visit=visit).select_related('name', 'data_recorder')

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
        'lab_tests': lab_tests,
    }

    # Render the HTML template
    html_content = render_to_string('kahama_template/pdf_consultation_summary.html', context)

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