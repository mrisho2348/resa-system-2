import calendar
import os
import json
from kahamahmis.kahamaReports import render_comprehensive_report, render_daily_comprehensive_report
import numpy as np
from datetime import datetime, date
from django.utils.timezone import now
# Django imports
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.views import View
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.template.loader import render_to_string
from django.db.models import Count, Max, OuterRef, Subquery
from django.db.models.functions import ExtractMonth
from django.db import IntegrityError
from django.contrib.auth.forms import PasswordChangeForm
from django.db import models

# Third-party imports
from weasyprint import HTML
import pdfkit

# Local imports
from clinic.forms import StaffProfileForm, YearMonthSelectionForm
from clinic.models import CustomUser
from kahamahmis.models import (
    KahamaPatient, KahamaPatientVisits, KahamaAppointment, Staffs, KahamaCompany, 
    KahamaService, KahamaLaboratoryRequest, KahamaProcedure, KahamaReferral, 
    PathodologyRecord, KahamaPatientVital, KahamaHealthRecord, 
    KahamaPatientHealthCondition, KahamaPatientSurgery, KahamaFamilyMedicalHistory, 
    KahamaPatientMedicationAllergy, KahamaPatientLifestyleBehavior,
    KahamaConsultationNotes, KahamaDischargesNotes, KahamaPatientDiagnosisRecord, 
    KahamaDiagnosis, KahamaCounseling, KahamaPrescription, KahamaObservationRecord, 
    KahamaChiefComplaint, KahamaMedicine, PrescriptionFrequency, Country
)
from kahamahmis.forms import (
    KahamaCounselingForm, KahamaDischargesNotesForm, KahamaLaboratoryRequestForm, KahamaObservationRecordForm, 
    KahamaProcedureForm, KahamaReferralForm
)


# ==================== PROFILE MANAGEMENT VIEWS ====================

@method_decorator(login_required, name='dispatch')
class EditStaffProfileView(View):
    """View for editing staff profiles"""
    template_name = 'kahama_template/edit_profile.html'

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
            return redirect('kahama_edit_staff_profile', pk=staff.id)

        return render(request, self.template_name, {'form': form, 'staff': staff})


@login_required
def doctor_profile(request):
    """View for displaying doctor profile"""
    user = request.user
    
    try:
        # Fetch the doctor's details from the Staffs model
        staff = Staffs.objects.get(admin=user, role='doctor')
        return render(request, 'kahama_template/profile.html', {'staff': staff})

    except Staffs.DoesNotExist:
        return render(request, 'kahama_template/profile.html', {'error': 'Doctor not found.'})


@login_required
def change_password(request):
    """View for changing user password"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Prevent user logout before redirecting
            messages.success(request, "Your password was successfully updated! Please log in again.")
            logout(request)  # Log out the user
            
            # Redirect based on workplace
            if request.user.staffs.work_place == 'kahama':
                return redirect('kahamahmis:kahama')  # Redirect to Kahama login page
            else:
                return redirect('login')  # Redirect to default login page (Resa)

        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'kahama_template/change_password.html', {'form': form})


# ==================== DASHBOARD & REPORT VIEWS ====================

@login_required
def kahama_dashboard(request):
    """Main dashboard view with statistics"""
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
    return render(request, "kahama_template/home_content.html", context)


@login_required
def search_report(request):
    if request.method == 'POST' and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        report_type = request.POST.get('report_type')
        year = request.POST.get('year')
        report_templates = {
            'patient_type_reports': 'kahama_template/patient_type_report_table.html',
            'patient_company_wise_reports': 'kahama_template/company_wise_reports_table.html',
            'patient_lab_result_reports': 'kahama_template/laboratory_report_table.html',
            'patient_procedure_reports': 'kahama_template/procedure_report_table.html',
            'patient_referral_reports': 'kahama_template/referral_reports_table.html',
            'patient_pathology_reports': 'kahama_template/pathology_record_report_table.html',
        }
        if report_type in report_templates:
            html_result = render_report(report_type, year)
            return JsonResponse({'html_result': html_result})
        else:
            return JsonResponse({'error': 'Invalid report type'})

def render_report(report_type, year):
    if report_type == 'patient_type_reports':       
        all_patient_types = ['National Staff', 'International Staff', 'National Visitor', 'International Visitor', 'Unknown Status','Permanent','Temporary','Visitor', 'Others']
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
        return render_to_string('kahama_template/patient_type_report_table.html', context)
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
        return render_to_string('kahama_template/company_wise_reports_table.html', context)
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
        return render_to_string('kahama_template/laboratory_report_table.html', context)
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
        return render_to_string('kahama_template/procedure_report_table.html', context)
    elif report_type == 'patient_referral_reports':
        referrals = KahamaReferral.objects.filter(created_at__year=year)
        context = {'referrals': referrals}
        return render_to_string('kahama_template/referral_reports_table.html', context)
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
        return render_to_string('kahama_template/pathology_record_report_table.html',context)

def generate_year_month_report(request):
    if request.method == 'POST':
        form = YearMonthSelectionForm(request.POST)

        if form.is_valid():
            year = int(form.cleaned_data['year'])
            month = int(form.cleaned_data['month']) if form.cleaned_data['month'] else 0

            try:
                if month == 0:
                    # Year-only selection (Yearly report)
                    response = render_comprehensive_report(year)
                    messages.success(request, f"Yearly report for {year} generated successfully.")
                else:
                    # Year and Month selection (Monthly report)
                    response = render_daily_comprehensive_report(year, month)
                    messages.success(request, f"Monthly report for {year}-{month:02d} generated successfully.")

                return response

            except Exception as e:
                messages.error(request, f"Error generating report: {str(e)}")
                return redirect('kahama_doctor_generate_year_month_report')

        else:
            messages.error(request, "Form validation failed. Please correct the errors below.")
            return render(request, 'kahama_template/generate_year_month_report.html', {'form': form})

    else:
        form = YearMonthSelectionForm()

    return render(request, 'kahama_template/generate_year_month_report.html', {'form': form})

@login_required
def get_gender_yearly_data(request):
    """AJAX view to get gender data by year"""
    if request.method == 'GET':
        selected_year = request.GET.get('year')
        male_count = KahamaPatient.objects.filter(gender='Male', created_at__year=selected_year).count()
        female_count = KahamaPatient.objects.filter(gender='Female', created_at__year=selected_year).count()
        
        yearly_gender_data = {
            'Male': male_count,
            'Female': female_count
        }
        
        return JsonResponse(yearly_gender_data)
    else:
        return JsonResponse({'error': 'Invalid request'})


@login_required
def get_patient_data_by_company(request):
    """AJAX view to get patient data by company"""
    patient_data = {}
    companies = KahamaCompany.objects.all()
    
    for company in companies:
        patients_count = KahamaPatient.objects.filter(company=company).count()
        patient_data[company.name] = patients_count
        
    return JsonResponse(patient_data)


@login_required
def get_gender_monthly_data(request):
    """AJAX view to get monthly gender data"""
    if request.method == 'GET':
        selected_year = request.GET.get('year')
        gender_monthly_data = {}
        
        for month in range(1, 13):
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
            
            month_name = calendar.month_name[month]
            gender_monthly_data[month_name] = {'Male': male_count, 'Female': female_count}
            
        return JsonResponse(gender_monthly_data)
    else:
        return JsonResponse({'error': 'Invalid request'})


# ==================== APPOINTMENT MANAGEMENT VIEWS ====================

@csrf_exempt
def appointment_view(request):
    """View for creating appointments"""
    try:
        if request.method == 'POST':
            doctor_id = request.POST.get('doctor')
            patient_id = request.POST.get('patient_id')
            visit_id = request.POST.get('visit_id')
            date_of_consultation = request.POST.get('date_of_consultation')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            description = request.POST.get('description')
            created_by = request.user.staff
            
            visit = get_object_or_404(KahamaPatientVisits, id=visit_id)
            doctor = get_object_or_404(Staffs, id=doctor_id)
            patient = get_object_or_404(KahamaPatient, id=patient_id)
            
            consultation = KahamaAppointment(
                doctor=doctor,
                visit=visit,
                patient=patient,
                appointment_date=date_of_consultation,
                start_time=start_time,
                end_time=end_time,
                description=description,
                created_by=created_by
            )
            consultation.save()
            
            return JsonResponse({'success': True, 'message': 'Appointment successfully created'})
        
        return JsonResponse({'success': False, 'message': 'Invalid request'})
    
    except IntegrityError as e:
        return JsonResponse({'success': False, 'message': str(e)})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
def appointment_list_view(request):
    """View for listing appointments"""
    appointments = KahamaAppointment.objects.all() 
    doctors = Staffs.objects.filter(role='doctor', work_place='kahama')
    patients = KahamaPatient.objects.all()
    
    context = {        
        'appointments': appointments,
        'doctors': doctors,
        'patients': patients,
    }
    
    return render(request, 'kahama_template/manage_appointment.html', context)


@login_required
def add_appointment(request):
    if request.method == 'POST':
        try:
            patient_id = request.POST.get('patient')
            doctor_id = request.POST.get('doctor')
            appointment_date = request.POST.get('appointment_date')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            description = request.POST.get('description')
            status = request.POST.get('status', 0)

            # Validate required fields
            if not all([patient_id, doctor_id, appointment_date, start_time, end_time]):
                return JsonResponse({'success': False, 'message': 'Please fill all required fields'})

            # Convert date + time
            appointment_date_obj = datetime.strptime(appointment_date, "%Y-%m-%d").date()
            start_time_obj = datetime.strptime(start_time, "%H:%M").time()
            end_time_obj = datetime.strptime(end_time, "%H:%M").time()

            # Validate date (must not be in past)
            if appointment_date_obj < now().date():
                return JsonResponse({'success': False, 'message': 'Appointment date cannot be in the past'})

            # Validate time (start < end)
            if start_time_obj >= end_time_obj:
                return JsonResponse({'success': False, 'message': 'Start time must be earlier than end time'})

            # Save appointment
            appointment = KahamaAppointment.objects.create(
                patient_id=patient_id,
                doctor_id=doctor_id,
                appointment_date=appointment_date,
                start_time=start_time,
                end_time=end_time,
                description=description,
                status=status,
                created_by=request.user.staff,
                data_recorder=request.user.staff
            )

            return JsonResponse({'success': True, 'message': 'Appointment created successfully'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error creating appointment: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@login_required
def confirm_meeting(request, appointment_id):
    """View for confirming appointments"""
    try:
        appointment = get_object_or_404(KahamaAppointment, id=appointment_id)
        
        if request.method == 'POST':
            selected_status = int(request.POST.get('status'))
            
            if not appointment.status:
                appointment.status = selected_status
                appointment.save()
                messages.success(request, f"Meeting with {appointment.patient.first_name} confirmed.")
            else:
                messages.warning(request, f"Meeting with {appointment.patient.first_name} is already confirmed.")
        else:
            messages.warning(request, "Invalid request method for confirming meeting.")
            
    except IntegrityError as e:
        messages.error(request, f"Error confirming meeting: {str(e)}")
        
    return redirect('kahama_doctor_appointment_list')


@login_required
def edit_meeting(request, appointment_id):
    """View for editing appointments"""
    try:
        if request.method == 'POST':
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            
            appointment = get_object_or_404(KahamaAppointment, id=appointment_id)
            appointment.start_time = start_time
            appointment.end_time = end_time
            appointment.save()
            
            messages.success(request, f"Meeting time for {appointment.patient.first_name} edited successfully.")
            
    except Exception as e:
        messages.error(request, f"Error editing meeting time: {str(e)}")
        
    return redirect('kahama_doctor_appointment_list') 


# ==================== CONSULTATION & MEDICAL RECORD VIEWS ====================

@login_required
def save_remotesconsultation_notes(request, patient_id, visit_id):
    """View for saving consultation notes"""
    doctor = request.user.staff
    patient = get_object_or_404(KahamaPatient, pk=patient_id)
    visit = get_object_or_404(KahamaPatientVisits, patient=patient, id=visit_id)
    patient_visits = KahamaPatientVisits.objects.filter(patient=patient)

    # Fetch patient health-related data
    try:
        context_data = {
            'patient_vitals': KahamaPatientVital.objects.filter(patient=patient, visit=visit),
            'health_records': KahamaHealthRecord.objects.all(),
            'health_conditions': KahamaPatientHealthCondition.objects.filter(patient=patient),
            'surgery_info': KahamaPatientSurgery.objects.filter(patient=patient),
            'family_history': KahamaFamilyMedicalHistory.objects.filter(patient=patient),
            'allergies': KahamaPatientMedicationAllergy.objects.filter(patient=patient),
            'behaviors': KahamaPatientLifestyleBehavior.objects.filter(patient=patient).first(),
        }
        
    except Exception:
        context_data = {
            'patient_vitals': None, 'health_records': None,
            'health_conditions': None, 'surgery_info': None,
            'family_history': None, 'allergies': None, 'behaviors': None,
        }
    
    consultation_note = KahamaConsultationNotes.objects.filter(patient=patient, visit=visit).first()
    previous_referrals = KahamaReferral.objects.filter(patient=patient, visit=visit)
    previous_discharges = KahamaDischargesNotes.objects.filter(patient=patient, visit=visit)

    provisional_record, _ = KahamaPatientDiagnosisRecord.objects.get_or_create(patient=patient, visit=visit)
    provisional_diagnosis_ids = provisional_record.provisional_diagnosis.values_list('id', flat=True)
    final_diagnosis_ids = provisional_record.final_diagnosis.values_list('id', flat=True)

    pathology_records = PathodologyRecord.objects.all()

    context = {
        'patient': patient,
        'visit': visit,
        'consultation_note': consultation_note,
        'previous_referrals': previous_referrals,
        'previous_discharges': previous_discharges,
        'patient_visits': patient_visits,
        'pathology_records': pathology_records,
        'provisional_diagnoses': KahamaDiagnosis.objects.all(),
        'provisional_diagnosis_ids': provisional_diagnosis_ids,
        'final_provisional_diagnosis': final_diagnosis_ids,
        'range_51': range(51),
        'range_101': range(101),
        'range_301': range(301),
        'range_15': range(3, 16),
        'temps': np.arange(0, 510, 1) / 10,
    }
    context.update(context_data)

    if request.method == 'POST':
        try:
            history = request.POST.get('history_of_presenting_illness')
            doctor_plan = request.POST.get('doctor_plan')
            plan_note = request.POST.get('doctor_plan_note')
            ros = request.POST.get('review_of_systems')
            exam_notes = request.POST.get('physical_examination')         
         
            provisional_ids = request.POST.getlist('provisional_diagnosis[]')
            pathology_ids = request.POST.getlist('pathology[]')

            # Update provisional diagnosis
            if not provisional_ids:
                provisional_record.data_recorder = doctor
            provisional_record.provisional_diagnosis.set(provisional_ids)
            provisional_record.save()

            if consultation_note:
                # Update existing note
                consultation_note.history_of_presenting_illness = history
                consultation_note.doctor_plan = doctor_plan
                consultation_note.doctor_plan_note = plan_note
                consultation_note.review_of_systems = ros
                consultation_note.physical_examination = exam_notes
       
                consultation_note.pathology.set(pathology_ids)
                consultation_note.save()
            else:
                if KahamaConsultationNotes.objects.filter(patient=patient, visit=visit).exists():
                    messages.error(request, 'A consultation note already exists for this visit.')
                    return render(request, 'kahama_template/add_consultation_notes.html', context)

                consultation_note = KahamaConsultationNotes.objects.create(
                    doctor=doctor,
                    patient=patient,
                    visit=visit,
                    history_of_presenting_illness=history,
                    doctor_plan=doctor_plan,
                    doctor_plan_note=plan_note,
                    review_of_systems=ros,
                    physical_examination=exam_notes,
                 
                )
                consultation_note.pathology.set(pathology_ids)
                consultation_note.save()

            messages.success(request, 'Consultation record saved successfully.')

            if doctor_plan == "Laboratory":
                return redirect(reverse('kahama_doctor_laboratory_save', args=[patient_id, visit_id]))
            else:
                return redirect(reverse('kahama_doctor_consultation_save_next', args=[patient_id, visit_id]))

        except Exception as e:
            messages.error(request, f'Error saving consultation note: {str(e)}')

    return render(request, 'kahama_template/add_consultation_notes.html', context)


@login_required
def save_remotesconsultation_notes_next(request, patient_id, visit_id):
    """View for saving additional consultation notes"""
    try:
        # Retrieve the patient and visit objects
        patient = get_object_or_404(KahamaPatient, pk=patient_id)
        visit = get_object_or_404(KahamaPatientVisits, patient=patient_id, id=visit_id)
        doctor_plan_note = KahamaConsultationNotes.objects.filter(patient=patient_id, visit=visit).first()
        data_recorder = request.user.staff

        # Retrieve the consultation note object if it exists, otherwise create a new one
        consultation_note, created = KahamaPatientDiagnosisRecord.objects.get_or_create(patient=patient, visit=visit)

        # Retrieve all provisional and final diagnoses
        provisional_diagnoses = KahamaDiagnosis.objects.all()
        final_diagnoses = KahamaDiagnosis.objects.all()

        # Get the IDs of the provisional and final diagnoses associated with the consultation note
        provisional_diagnosis_ids = consultation_note.provisional_diagnosis.values_list('id', flat=True)
        final_diagnosis_ids = consultation_note.final_diagnosis.values_list('id', flat=True)

        # Initialize doctor_plan to None to avoid UnboundLocalError
        doctor_plan = None

        # Retrieve the doctor plan from the query string
        if request.method == 'POST':
            final_diagnosis = request.POST.getlist('final_diagnosis[]')
            doctor_plan = request.POST.get('doctor_plan')            
            
            if not consultation_note:
                consultation_note = KahamaPatientDiagnosisRecord.objects.create(patient=patient, visit=visit)
                consultation_note.data_recorder = data_recorder
                
            consultation_note.final_diagnosis.set(final_diagnosis)
            consultation_note.save()

            # Add success message
            messages.success(request, '')

            # Redirect based on the doctor's plan
            if doctor_plan == 'Prescription':
                return redirect(reverse('kahama_doctor_prescription_save', args=[patient_id, visit_id]))
            elif doctor_plan == 'Laboratory':
                return redirect(reverse('kahama_doctor_consultation_save', args=[patient_id, visit_id]))
            elif doctor_plan == 'Referral':
                return redirect(reverse('kahama_doctor_referral_save', args=[patient_id, visit_id]))
            elif doctor_plan == 'Counselling':
                return redirect(reverse('kahama_doctor_counseling_save', args=[patient_id, visit_id]))
            elif doctor_plan == 'Procedure':
                return redirect(reverse('kahama_doctor_procedure_save', args=[patient_id, visit_id]))
            elif doctor_plan == 'Observation':
                return redirect(reverse('kahama_doctor_save_observation', args=[patient_id, visit_id]))
            elif doctor_plan == 'Discharge':
                return redirect(reverse('kahama_doctor_discharge_save', args=[patient_id, visit_id]))

        # Update doctor_plan in context if request is POST
        context = {
            'provisional_diagnoses': provisional_diagnoses,
            'final_diagnoses': final_diagnoses,
            'patient': patient,
            'visit': visit,
            'consultation_note': consultation_note,
            'provisional_diagnosis_ids': provisional_diagnosis_ids,
            'final_diagnosis_ids': final_diagnosis_ids,
            'doctor_plan_note': doctor_plan_note,
            'doctor_plan': doctor_plan,  # Include the value of doctor_plan
        }
        return render(request, 'kahama_template/add_patientprovisional_diagnosis.html', context)

    except Exception as e:
        messages.error(request, f'Error: {str(e)}')

        # Context for exception cases
        context = {
            'provisional_diagnoses': provisional_diagnoses,
            'final_diagnoses': final_diagnoses,
            'patient': patient,
            'visit': visit,
            'consultation_note': consultation_note,
            'provisional_diagnosis_ids': provisional_diagnosis_ids,
            'final_diagnosis_ids': final_diagnosis_ids,
            'doctor_plan_note': doctor_plan_note,
        }
        return render(request, 'kahama_template/add_patientprovisional_diagnosis.html', context)


@login_required
def consultation_notes_view(request):
    """View for displaying consultation notes"""
    # Get all patients who have consultation notes
    patient_records = KahamaPatient.objects.filter(
        consultation_notes__isnull=False
    ).distinct().order_by('-consultation_notes__updated_at')

    return render(request, 'kahama_template/manage_consultation_notes.html', {
        'patient_records': patient_records
    })


# ==================== PDF EXPORT VIEWS ====================

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


# ==================== COUNSELING VIEWS ====================

@login_required    
def save_counsel(request, patient_id, visit_id):
    """View for saving counseling records"""
    patient = get_object_or_404(KahamaPatient, id=patient_id)
    visit = get_object_or_404(KahamaPatientVisits, id=visit_id)              
    data_recorder = request.user.staff

    # Use .filter().first() to avoid DoesNotExist error
    remote_counseling = KahamaCounseling.objects.filter(patient=patient, visit=visit).first()
    consultation_notes = KahamaPatientDiagnosisRecord.objects.filter(patient=patient_id, visit=visit_id)  

    if request.method == 'POST':        
        form = KahamaCounselingForm(request.POST, instance=remote_counseling)

        if form.is_valid():
            counseling = form.save(commit=False)
            if not remote_counseling:
                counseling.patient = patient
                counseling.data_recorder = data_recorder
                counseling.visit = visit
            try:
                counseling.save()
                messages.success(request, 'Counseling record saved successfully.')
            except ValidationError as e:
                messages.error(request, f'Validation Error: {e}')
        else:
            messages.error(request, 'Please correct the errors in the form.')

        return redirect(reverse('kahama_doctor_consultation_save', args=[patient_id, visit_id]))
    else:
        form = KahamaCounselingForm(instance=remote_counseling)   

    context = {
        'patient': patient, 
        'visit': visit,
        'remote_counseling': remote_counseling,
        'consultation_notes': consultation_notes,
        'form': form,
    }

    return render(request, 'kahama_template/counsel_template.html', context)



@login_required
def counseling_list_view(request):
    """View for listing counseling records"""
    counselings = KahamaCounseling.objects.all().order_by('-created_at')
    return render(request, 'kahama_template/manage_counselling.html', {'counselings': counselings})


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


# ==================== DISCHARGE NOTES VIEWS ====================

@login_required    
def save_remote_discharges_notes(request, patient_id, visit_id):
    """View for saving discharge notes"""
    patient = get_object_or_404(KahamaPatient, id=patient_id)
    visit = get_object_or_404(KahamaPatientVisits, id=visit_id)
    consultation_notes = KahamaPatientDiagnosisRecord.objects.filter(patient=patient_id, visit=visit_id)    
    remote_discharges_notes = KahamaDischargesNotes.objects.filter(patient=patient, visit=visit).first()  
    
    context = {
        'patient': patient,
        'visit': visit,
        'consultation_notes': consultation_notes,
        'remote_discharges_notes': remote_discharges_notes,         
    }
    
    try:      
        data_recorder = request.user.staff      
        
        if request.method == 'POST':
            form = KahamaDischargesNotesForm(request.POST, instance=remote_discharges_notes)
            
            if form.is_valid():
                remote_discharges_notes = form.save(commit=False)
                remote_discharges_notes.patient = patient
                remote_discharges_notes.visit = visit
                remote_discharges_notes.data_recorder = data_recorder
                remote_discharges_notes.save()
                
                messages.success(request, '')
                return redirect(reverse('kahama_doctor_consultation_save', args=[patient_id, visit_id]))
            else:
                messages.error(request, 'Please correct the errors in the form.')
        else:
            form = KahamaDischargesNotesForm(instance=remote_discharges_notes)        
        
        context['form'] = form
        return render(request, 'kahama_template/discharge_template.html', context)    
        
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return render(request, 'kahama_template/discharge_template.html', context)


@login_required
def discharge_notes_list_view(request):
    """View for listing discharge notes"""
    discharge_notes = KahamaDischargesNotes.objects.all().order_by('-discharge_date')
    return render(request, 'kahama_template/manage_discharge.html', {'discharge_notes': discharge_notes})


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


# ==================== LABORATORY VIEWS ====================

@login_required    
def save_laboratory(request, patient_id, visit_id):
    """View for saving laboratory requests"""
    patient = get_object_or_404(KahamaPatient, id=patient_id)
    visit = get_object_or_404(KahamaPatientVisits, id=visit_id)
    remote_service = KahamaService.objects.filter(category='Laboratory')
    data_recorder = request.user.staff
    previous_results = KahamaLaboratoryRequest.objects.filter(patient=patient)
    consultation_notes = KahamaPatientDiagnosisRecord.objects.filter(patient=patient_id, visit=visit_id)  
    
    # Check if the laboratory order already exists for this patient on the specified visit
    laboratory_order = KahamaLaboratoryRequest.objects.filter(patient=patient, visit=visit).first()
    
    context = {
        'patient': patient,
        'visit': visit, 
        'previous_results': previous_results, 
        'consultation_notes': consultation_notes, 
        'remote_service': remote_service
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
                    laboratory_order.data_recorder = data_recorder
                    laboratory_order.save()
                    messages.success(request, '')
                else:
                    # If no laboratory order exists, create a new one
                    KahamaLaboratoryRequest.objects.create(
                        data_recorder=data_recorder,
                        patient=patient,
                        visit=visit,
                        name_id=name,
                        result=description
                    )
                    messages.success(request, '')
                    
            # Redirect to a success page or another view
            return redirect(reverse('kahama_doctor_consultation_save_next', args=[patient_id, visit_id])) 
            
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

    return render(request, 'kahama_template/laboratory_template.html', context)


@login_required
def patient_laboratory_view(request):
    """View for displaying patient laboratory results"""
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

    return render(request, 'kahama_template/manage_lab_result.html', context)


@login_required
def patient_lab_details_view(request, mrn, visit_number):
    """View for displaying detailed lab results for a patient"""
    # Fetch the patient with a prefetch query to reduce database hits
    patient = get_object_or_404(KahamaPatient.objects.prefetch_related('remotelaboratoryorder_set'), mrn=mrn)
    visit = get_object_or_404(KahamaPatientVisits, vst=visit_number)
    
    # Retrieve lab results efficiently
    lab_results = list(patient.remotelaboratoryorder_set.filter(visit__vst=visit_number))

    # Get the first data recorder if lab results exist
    lab_done_by = lab_results[0].data_recorder if lab_results else None

    context = {
        'patient': patient,
        'visit': visit,
        'lab_done_by': lab_done_by,
        'lab_results': lab_results,
    }

    return render(request, 'kahama_template/lab_details.html', context)

@login_required
def patient_lab_result_history_view(request, mrn):
    patient = get_object_or_404(KahamaPatient, mrn=mrn)    
    # Retrieve all procedures for the specific patient
    lab_results = KahamaLaboratoryRequest.objects.filter(patient=patient)
    patient_lab_results =  KahamaService.objects.filter(category='Laboratory')    
    context = {
        'patient': patient,
        'lab_results': lab_results,
        'patient_lab_results': patient_lab_results,
    }
    return render(request, 'kahama_template/manage_patient_lab_result.html', context)

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
def edit_lab_result(request, patient_id, visit_id, lab_id):
    """View for editing lab results"""
    # Retrieve patient and visit objects
    patient = get_object_or_404(KahamaPatient, id=patient_id)
    visit = get_object_or_404(KahamaPatientVisits, id=visit_id)            

    procedures = KahamaLaboratoryRequest.objects.filter(patient=patient, visit=visit, id=lab_id).first()
    
    # Prepare context for rendering the template
    context = {
        'patient': patient, 
        'visit': visit,
        'procedures': procedures,
    }
    
    # Handle form submission
    if request.method == 'POST':        
        form = KahamaLaboratoryRequestForm(request.POST, instance=procedures)
        
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
        return redirect(reverse('kahama_doctor_patient_lab_result_history_view', args=[patient.mrn]))
   
    else:
        # If it's a GET request, initialize the form with existing data (if any)
        form = KahamaLaboratoryRequestForm(instance=procedures)   
    
    # Add the form to the context
    context['form'] = form    
    return render(request, 'kahama_template/edit_lab_result.html', context)


# ==================== OBSERVATION VIEWS ====================

@login_required
def patient_observation_view(request):
    """View for displaying patient observations"""
    template_name = 'kahama_template/manage_observation.html'    
    
    # Query to retrieve the latest procedure record for each patient
    observations = KahamaObservationRecord.objects.filter(
        patient=OuterRef('id')
    ).order_by('-created_at')
    
    # Query to retrieve patients with their corresponding procedure (excluding patients without observations)
    patients_with_observations = KahamaPatient.objects.annotate(
        observation_name=Subquery(observations.values('imaging__name')[:1]),      
    ).filter(observation_name__isnull=False)    
  
    data = patients_with_observations.values(
        'id', 'mrn', 'observation_description',
    )
    
    return render(request, template_name, {'data': data})


@login_required
def observation_record_list_view(request):
    """View for listing observation records"""
    observation_records = KahamaObservationRecord.objects.all().order_by('-created_at')
    return render(request, 'kahama_template/manade_observation_record.html', {'observation_records': observation_records})

@login_required
def save_observation(request, patient_id, visit_id):
    patient = get_object_or_404(KahamaPatient, id=patient_id)
    visit = get_object_or_404(KahamaPatientVisits, id=visit_id)
    data_recorder = request.user.staff
    record_exists = KahamaObservationRecord.objects.filter(patient_id=patient_id, visit_id=visit_id).first()
    consultation_notes = KahamaPatientDiagnosisRecord.objects.filter(patient=patient_id, visit=visit_id)    
    context = {'patient': patient, 
               'visit': visit, 
               'consultation_notes': consultation_notes, 
               'record_exists': record_exists
               }
    if request.method == 'POST':
        form = KahamaObservationRecordForm(request.POST)
        if form.is_valid():
            description = form.cleaned_data['observation_notes']
            try:
                if record_exists:
                    # If a record exists, update it
                    observation_record = KahamaObservationRecord.objects.get(patient_id=patient_id, visit_id=visit_id)
                    observation_record.observation_notes = description
                    observation_record.data_recorder = data_recorder
                    observation_record.save()
                    messages.success(request, '')
                else:
                    # If no record exists, create a new one
                    KahamaObservationRecord.objects.create(
                        patient=patient,
                        visit=visit,
                        data_recorder=data_recorder,
                        observation_notes=description,
                    )
                    messages.success(request, '')
                return redirect(reverse('kahama_doctor_consultation_save', args=[patient_id, visit_id]))
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            messages.error(request, 'Please fill out all required fields.')
    else:
        form = KahamaObservationRecordForm(initial={'observation_notes': record_exists.observation_notes if record_exists else ''})

    context['form'] = form
    return render(request, 'kahama_template/observation_template.html', context)

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


# ==================== PATIENT MANAGEMENT VIEWS ====================

@login_required
def patient_info_form(request):
    """View for creating new patient information"""
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
            ftw_certificate = request.POST.get('ftw_certificate')
            date_of_ftw_certification = request.POST.get('date_of_ftw_certification')
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
                    dob_date = datetime.strptime(dob, '%Y-%m-%d').date()
                    current_date = datetime.today().date()
                    age = current_date.year - dob_date.year - ((current_date.month, current_date.day) < (dob_date.month, dob_date.day))
                except ValueError:
                    age = None
            elif age:
                # Calculate dob from age
                try:
                    age_int = int(age)
                    current_date = datetime.today().date()
                    dob = current_date.replace(year=current_date.year - age_int)
                except ValueError:
                    dob = None
           
            # Convert empty fields to None
            date_of_osha_certification = date_of_osha_certification or None
            date_of_ftw_certification = date_of_ftw_certification or None
            dob = dob or None
            age = age or None
            
            # Check if a patient with the same information already exists
            existing_patient = KahamaPatient.objects.filter(
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,                          
            ).exists()
            
            if existing_patient:                
                messages.error(request, f'A patient with the same information already exists.')
                return redirect(reverse('kahama_doctor_patient_add'))
                
            # Create or update patient record
            patient = KahamaPatient(
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                gender=gender,
                data_recorder=request.user.staff,
                occupation=occupation,
                other_occupation=other_occupation,
                phone=phone,
                osha_certificate=osha_certificate,
                date_of_osha_certification=date_of_osha_certification,
                ftw_certificate=ftw_certificate,
                date_of_ftw_certification=date_of_ftw_certification,
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
            
            return redirect(reverse('kahama_doctor_patient_health_info', args=[patient.id]))
            
        except Exception as e:
            messages.error(request, f'Error adding Patient record : {str(e)}')
            return redirect(reverse('kahama_doctor_patient_add'))
            
    range_121 = range(0, 121)
    all_country = Country.objects.all()
    all_company = KahamaCompany.objects.all()
    
    context = {
        'range_121': range_121,
        'all_country': all_country,
        'all_company': all_company, 
    }
    
    return render(request, 'kahama_template/add_remotePatients.html', context)


@login_required
def patients_list(request):
    """View for listing all patients"""
    patients = KahamaPatient.objects.order_by('-created_at')    
    doctors = Staffs.objects.filter(role='doctor', work_place='kahama')
    
    return render(request, 'kahama_template/manage_remotepatients_list.html', {
        'patients': patients,
        'doctors': doctors,
    })


@login_required
def patient_info_form_edit(request, patient_id):    
    """View for editing patient information"""
    try:
        patient = KahamaPatient.objects.get(pk=patient_id)    
    except KahamaPatient.DoesNotExist:
        return HttpResponse("Patient not found", status=404)
        
    if request.method == 'POST':
        try:
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
            ftw_certificate = request.POST.get('ftw_certificate')
            date_of_ftw_certification = request.POST.get('date_of_ftw_certification')
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
                try:
                    dob_date = datetime.strptime(dob, '%Y-%m-%d').date()
                    current_date = datetime.today().date()
                    age = current_date.year - dob_date.year - ((current_date.month, current_date.day) < (dob_date.month, dob_date.day))
                except ValueError:
                    age = None
            elif age:
                try:
                    age_int = int(age)
                    current_date = datetime.today().date()
                    dob = current_date.replace(year=current_date.year - age_int)
                except ValueError:
                    dob = None
           
            if date_of_osha_certification == '':
                date_of_osha_certification = None
            if date_of_ftw_certification == '':
                date_of_osha_certification = None
                
            patient.first_name = first_name
            patient.middle_name = middle_name
            patient.last_name = last_name
            patient.gender = gender
            patient.age = age
            patient.dob = dob            
            patient.data_recorder = request.user.staff          
            patient.nationality_id = Country.objects.get(id=nationality_id)
            patient.phone = phone
            patient.osha_certificate = osha_certificate
            patient.date_of_osha_certification = date_of_osha_certification
            patient.ftw_certificate = ftw_certificate
            patient.date_of_ftw_certification = date_of_ftw_certification
            patient.insurance = insurance
            patient.insurance_company = insurance_company if insurance == 'Insured' else None
            patient.other_insurance_company = other_insurance if insurance_company == 'Other' else None
            patient.insurance_number = insurance_number if insurance == 'Insured' else None
            patient.emergency_contact_name = emergency_contact_name
            patient.emergency_contact_relation = emergency_contact_relation
            patient.other_emergency_contact_relation = other_relation if emergency_contact_relation == 'Other' else None
            patient.emergency_contact_phone = emergency_contact_phone
            patient.marital_status = marital_status
            patient.occupation = occupation
            patient.other_occupation = other_occupation if occupation == 'Other' else None
            patient.patient_type = patient_type           
            patient.other_patient_type = other_patient_type if patient_type == 'Other' else None           
            patient.company_id = KahamaCompany.objects.get(id=company_id)
            patient.save()
            
            if 'save_back' in request.POST:
                return redirect('kahama_doctor_patients_list')
            elif 'save_continue_health' in request.POST:
                return redirect(reverse('kahama_doctor_patient_health_edit', args=[patient_id]))
                
        except Exception as e:
            messages.error(request, f'Error editing Patient record: {str(e)}')
            return redirect(reverse('kahama_doctor_patient_edit', args=[patient_id]))
            
    all_country = Country.objects.all()
    all_company = KahamaCompany.objects.all()
    range_121 = range(1, 121)
    
    return render(request, 'kahama_template/edit_remotepatient.html', {
        'patient': patient,
        'all_country': all_country,
        'all_company': all_company,
        'range_121': range_121,
    })


# ==================== HEALTH RECORD MANAGEMENT VIEWS ====================

@require_POST
@csrf_exempt
def delete_health_record(request):
    """AJAX view to delete health records"""
    try:
        record_id = request.POST.get('record_id')
        
        if not record_id:
            return JsonResponse({'status': 'error', 'message': 'Record ID not provided'}, status=400)
            
        record = get_object_or_404(KahamaPatientHealthCondition, id=record_id)
        record.delete()
        
        return JsonResponse({'status': 'success', 'message': 'Record deleted'})
        
    except KahamaPatientHealthCondition.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Health record not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Unexpected error: {str(e)}'}, status=500)


@require_POST
@csrf_exempt
def delete_family_medical_history_record(request):
    """AJAX view to delete family medical history records"""
    try:
        record_id = request.POST.get('record_id')
        
        if not record_id:
            return JsonResponse({'status': 'error', 'message': 'Record ID not provided'}, status=400)
            
        record = get_object_or_404(KahamaFamilyMedicalHistory, id=record_id)
        record.delete()
        
        return JsonResponse({'status': 'success', 'message': 'Family medical history record deleted successfully'})
        
    except KahamaFamilyMedicalHistory.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Record not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Unexpected error: {str(e)}'}, status=500)


@require_POST
@csrf_exempt
def delete_medication_allergy_record(request):
    """AJAX view to delete medication allergy records"""
    try:
        record_id = request.POST.get('record_id')
        
        if not record_id:
            return JsonResponse({'status': 'error', 'message': 'Record ID not provided'}, status=400)
            
        record = get_object_or_404(KahamaPatientMedicationAllergy, id=record_id)
        record.delete()
        
        return JsonResponse({'status': 'success', 'message': 'Record deleted successfully'})
        
    except KahamaPatientMedicationAllergy.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Allergy record not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Unexpected error: {str(e)}'}, status=500)


@require_POST
@csrf_exempt
def delete_surgery_history_record(request):
    """AJAX view to delete surgery history records"""
    try:
        record_id = request.POST.get('record_id')
        
        if not record_id:
            return JsonResponse({'status': 'error', 'message': 'Record ID not provided'}, status=400)
            
        record = get_object_or_404(KahamaPatientSurgery, id=record_id)
        record.delete()
        
        return JsonResponse({'status': 'success', 'message': 'Surgery record deleted successfully'})
        
    except KahamaPatientSurgery.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Surgery record not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Unexpected error: {str(e)}'}, status=500)


@login_required
def health_info_edit(request, patient_id):
    """View for editing patient health information"""
    try:
        patient = get_object_or_404(KahamaPatient, pk=patient_id)
        
        try:
            all_medicines = KahamaMedicine.objects.all()
        except KahamaMedicine.DoesNotExist:
            all_medicines = []
            
        try:
            patient_health_records = KahamaPatientHealthCondition.objects.filter(patient_id=patient_id)
        except KahamaPatientHealthCondition.DoesNotExist:
            patient_health_records = None
            
        try:
            medication_allergies = KahamaPatientMedicationAllergy.objects.filter(patient_id=patient_id)
        except KahamaPatientMedicationAllergy.DoesNotExist:
            medication_allergies = None
            
        try:
            surgery_history = KahamaPatientSurgery.objects.filter(patient_id=patient_id)
        except KahamaPatientSurgery.DoesNotExist:
            surgery_history = None
            
        try:
            lifestyle_behavior = KahamaPatientLifestyleBehavior.objects.get(patient_id=patient_id)
        except KahamaPatientLifestyleBehavior.DoesNotExist:
            lifestyle_behavior = None
            
        try:
            family_medical_history = KahamaFamilyMedicalHistory.objects.filter(patient=patient)
        except KahamaFamilyMedicalHistory.DoesNotExist:
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
                lifestyle_behavior = KahamaPatientLifestyleBehavior(
                    patient_id=patient_id,
                    smoking=request.POST.get('smoking'),
                    alcohol_consumption=request.POST.get('alcohol_consumption'),
                    weekly_exercise_frequency=request.POST.get('weekly_exercise_frequency'),
                    healthy_diet=request.POST.get('healthy_diet'),
                    stress_management=request.POST.get('stress_management'),
                    sufficient_sleep=request.POST.get('sufficient_sleep')
                )
                lifestyle_behavior.save()
                
            for record in family_medical_history:
                record_id = str(record.id)
                condition = request.POST.get('condition_' + record_id)
                relationship = request.POST.get('relationship_' + record_id)
                comments = request.POST.get('comments_' + record_id)
                
                record.condition = condition
                record.relationship = relationship
                record.comments = comments
                record.save()
                
            if 'new_condition[]' in request.POST:
                new_conditions = request.POST.getlist('new_condition[]')
                new_relationships = request.POST.getlist('new_relationship[]')
                new_comments = request.POST.getlist('new_comments[]')
                
                for condition, relationship, comments in zip(new_conditions, new_relationships, new_comments):
                    new_record = KahamaFamilyMedicalHistory(patient=patient, condition=condition, relationship=relationship, comments=comments)
                    new_record.save()
                    
            if request.POST.get('family_medical_history') == 'no':
                patient.family_medical_history.all().delete()
                
            for allergy in medication_allergies:
                allergy_id = str(allergy.id)
                medicine_name = request.POST.get('medicine_name_' + allergy_id)
                reaction = request.POST.get('reaction_' + allergy_id)
                
                if medicine_name is not None:
                    medicine_name_id = KahamaMedicine.objects.get(id=medicine_name) 
                    allergy.medicine_id = medicine_name_id.id
                    
                if reaction is not None:
                    allergy.reaction = reaction
                    
                allergy.save()
                
            if 'new_medicine_name[]' in request.POST:
                new_medicine_names = request.POST.getlist('new_medicine_name[]')
                new_reactions = request.POST.getlist('new_reaction[]')
                
                for medicine_name, reaction in zip(new_medicine_names, new_reactions):
                    medicine_name_id = KahamaMedicine.objects.get(id=medicine_name)  
                    new_allergy = KahamaPatientMedicationAllergy(patient=patient, medicine_id=medicine_name_id.id, reaction=reaction)
                    new_allergy.save()
                    
            if request.POST.get('medication_allergy') == 'no':
                patient.medication_allergies.all().delete()
                
            for surgery in surgery_history:
                surgery_id = str(surgery.id)
                surgery_name = request.POST.get('surgery_name_' + surgery_id)
                date_of_surgery = request.POST.get('date_of_surgery_' + surgery_id)
                
                if surgery_name is not None:
                    surgery.surgery_name = surgery_name
                    
                if date_of_surgery is not None:
                    surgery.surgery_date = date_of_surgery
                    
                surgery.save()
                
            if 'new_surgery_name[]' in request.POST:
                new_surgery_names = request.POST.getlist('new_surgery_name[]')
                new_dates_of_surgery = request.POST.getlist('new_date_of_surgery[]')
                
                for name, date in zip(new_surgery_names, new_dates_of_surgery):
                    new_surgery = KahamaPatientSurgery(patient=patient, surgery_name=name, surgery_date=date)
                    new_surgery.save()
                    
            if request.POST.get('surgery_history') == 'no':
                patient.surgeries.all().delete()
                
            for record in patient_health_records:
                record_id = str(record.id)
                health_condition = request.POST.get('health_condition_' + record_id)
                health_condition_notes = request.POST.get('health_condition_notes_' + record_id)
                
                if health_condition is not None:
                    record.health_condition = health_condition
                    
                if health_condition_notes is not None:
                    record.health_condition_notes = health_condition_notes
                    
                record.save()
                
            if 'new_health_condition[]' in request.POST:
                new_health_conditions = request.POST.getlist('new_health_condition[]')
                new_health_condition_notes = request.POST.getlist('new_health_condition_notes[]')
                
                for condition, notes in zip(new_health_conditions, new_health_condition_notes):
                    new_record = KahamaPatientHealthCondition(patient=patient, health_condition=condition, health_condition_notes=notes)
                    new_record.save()
                    
                messages.success(request, '')
                
            if request.POST.get('chronic_illness') == 'no':
                patient.health_conditions.all().delete()
                
            if 'save_and_return' in request.POST:
                return redirect('kahama_doctor_patients_list')
            elif 'save_and_continue_family_health' in request.POST:
                return redirect(reverse('kahama_doctor_visit_save', args=[patient_id]))
                
        return render(request, 'kahama_template/edit_patient_health_condition_form.html', context)
        
    except Exception as e:
        messages.error(request, f'Error editing patient health record: {str(e)}')
        return render(request, 'kahama_template/edit_patient_health_condition_form.html', context)


@login_required
def save_patient_health_information(request, patient_id):
    """View for saving patient health information"""
    try:
        # Retrieve the patient object using the patient_id from URL parameters
        patient = get_object_or_404(KahamaPatient, pk=patient_id)
        
        try:
            all_medicines = KahamaMedicine.objects.all()
        except KahamaMedicine.DoesNotExist:
            # Handle the case where no medicines are found
            all_medicines = []
            
        if request.method == 'POST':
            # Check if the patient has allergies to medication
            medication_allergy = request.POST.get('medication_allergy')
            family_medical_history = request.POST.get('family_medical_history')
            surgery_history = request.POST.get('surgery_history')
            chronic_illness = request.POST.get('chronic_illness')
                        
            smoking = request.POST.get('smoking')
            alcohol_consumption = request.POST.get('alcohol_consumption')
            weekly_exercise_frequency = request.POST.get('weekly_exercise_frequency')
            healthy_diet = request.POST.get('healthy_diet')
            stress_management = request.POST.get('stress_management')
            sufficient_sleep = request.POST.get('sufficient_sleep')
            data_recorder = request.user.staff 
            
            # Create PatientLifestyleBehavior object
            lifestyle_behavior = KahamaPatientLifestyleBehavior.objects.create(
                patient=patient,
                smoking=smoking,
                alcohol_consumption=alcohol_consumption,
                weekly_exercise_frequency=weekly_exercise_frequency,
                healthy_diet=healthy_diet,
                stress_management=stress_management,
                sufficient_sleep=sufficient_sleep,
                data_recorder=data_recorder,
            )

            # Check if the patient has surgery history
            if surgery_history == 'yes':
                surgery_names = request.POST.getlist('surgery_name[]')
                surgery_dates = request.POST.getlist('date_of_surgery[]')
                
                for name, date in zip(surgery_names, surgery_dates):
                    surgery = KahamaPatientSurgery.objects.create(
                        patient=patient,
                        surgery_name=name,
                        data_recorder=data_recorder,
                        surgery_date=date,
                    )

            # Check if the patient has chronic illness
            if chronic_illness == 'yes':
                health_conditions = request.POST.getlist('health_condition[]')
                health_condition_notes = request.POST.getlist('health_condition_notes[]')
                
                for condition, notes in zip(health_conditions, health_condition_notes):
                    patient_health_condition = KahamaPatientHealthCondition.objects.create(
                        patient=patient,
                        data_recorder=data_recorder,
                        health_condition=condition,
                        health_condition_notes=notes
                    )

            # Check if the patient has family medical history
            if family_medical_history == 'yes':
                conditions = request.POST.getlist('condition[]')
                relationships = request.POST.getlist('relationship[]')
                comments = request.POST.getlist('comments[]')
                
                for condition, relationship, comment in zip(conditions, relationships, comments):
                    family_medical_history = KahamaFamilyMedicalHistory.objects.create(
                        patient=patient,
                        data_recorder=data_recorder,
                        condition=condition,
                        relationship=relationship,
                        comments=comment
                    )

            # Check if the patient has medication allergies
            if medication_allergy == 'yes':
                medicine_names = request.POST.getlist('medicine_name[]')
                reactions = request.POST.getlist('reaction[]')
                
                for medicine_name, reaction in zip(medicine_names, reactions):
                    medicine_name_id = KahamaMedicine.objects.get(id=medicine_name)           
                    medication_allergy = KahamaPatientMedicationAllergy.objects.create(
                        patient=patient,
                        data_recorder=data_recorder,
                        medicine_id=medicine_name_id.id,
                        reaction=reaction
                    )

            # Redirect to the appropriate URL upon successful data saving
            return redirect(reverse('kahama_doctor_visit_save', args=[patient_id]))

    except KahamaPatient.DoesNotExist:
        # Handle the case where the patient ID is not valid
        messages.error(request, 'Patient not found.')
        return redirect(reverse('kahama_doctor_patient_health_info', args=[patient_id])) 

    except Exception as e:
        # Handle other exceptions
        messages.error(request, f'Error adding patient health information: {str(e)}')

    # If the request method is not POST or if there's an error, render the form again
    return render(request, 'kahama_template/add_patient_health_condition_form.html', {'patient': patient, 'all_medicines': all_medicines})


# ==================== PRESCRIPTION VIEWS ====================

@login_required
def save_prescription(request, patient_id, visit_id):
    """View for saving prescriptions"""
    try:
        # Retrieve visit history for the specified patient
        visit = KahamaPatientVisits.objects.get(id=visit_id)         
        frequencies = PrescriptionFrequency.objects.all()         
        prescriptions = KahamaPrescription.objects.filter(patient=patient_id, visit_id=visit_id)        
        consultation_notes = KahamaPatientDiagnosisRecord.objects.filter(patient=patient_id, visit=visit_id)  
        current_date = timezone.now().date()
        patient = KahamaPatient.objects.get(id=patient_id)   
        
        
        medicines = KahamaMedicine.objects.filter(
            remain_quantity__gt=0,  # Inventory level greater than zero
            expiration_date__gt=current_date  # Not expired
        ).distinct()
        
        range_31 = range(1,31)
        
        return render(request, 'kahama_template/prescription_template.html', {           
            'patient': patient,
            'visit': visit,       
            'consultation_notes': consultation_notes,       
            'medicines': medicines,        
            'range_31': range_31,
            'frequencies': frequencies,
            'prescriptions': prescriptions,
        })
        
    except Exception as e:
        # Handle other exceptions if necessary
        return render(request, '404.html', {'error_message': str(e)}) 


@login_required
def prescription_list(request):
    """View for listing prescriptions"""
    # Step 1: Fetch all prescriptions with related fields
    prescriptions = KahamaPrescription.objects.select_related(
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

    return render(request, 'kahama_template/manage_prescription_list.html', {
        'visit_groups': visit_groups,
    }) 


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


@csrf_exempt
@require_POST
def add_remoteprescription(request):
    """AJAX view for adding prescriptions"""
    try:
        patient_id = request.POST.get('patient_id')
        visit_id = request.POST.get('visit_id')
        medicines = request.POST.getlist('medicine[]')
        doses = request.POST.getlist('dose[]')
        frequencies = request.POST.getlist('frequency[]')
        durations = request.POST.getlist('duration[]')
        quantities = request.POST.getlist('quantity[]')
        entered_by = request.user.staff

        patient = KahamaPatient.objects.get(id=patient_id)
        visit = KahamaPatientVisits.objects.get(id=visit_id)

        for i in range(len(medicines)):
            medicine = KahamaMedicine.objects.get(id=medicines[i])
            quantity_used_str = quantities[i]

            if quantity_used_str is None:
                return JsonResponse({'status': 'error', 'message': f'Invalid quantity for {medicine.drug_name}. Quantity cannot be empty.'})

            try:
                quantity_used = int(quantity_used_str)
            except ValueError:
                return JsonResponse({'status': 'error', 'message': f'Invalid quantity for {medicine.drug_name}. Quantity must be a valid number.'})

            if quantity_used < 0:
                return JsonResponse({'status': 'error', 'message': f'Invalid quantity for {medicine.drug_name}. Quantity must be a non-negative number.'})

            if medicine.is_clinic_stock:
                remain_quantity = medicine.remain_quantity

                if remain_quantity is not None and quantity_used > remain_quantity:
                    return JsonResponse({'status': 'error', 'message': f'Insufficient stock for {medicine.drug_name}. Only {remain_quantity} available.'})

                if remain_quantity is not None:
                    medicine.remain_quantity -= quantity_used
                    medicine.save()

            KahamaPrescription.objects.create(
                patient=patient,
                medicine=medicine,
                entered_by=entered_by,
                visit=visit,
                dose=doses[i],
                frequency=PrescriptionFrequency.objects.get(id=frequencies[i]),
                duration=durations[i],
                quantity_used=quantity_used,
            )

        return JsonResponse({'status': 'success', 'message': 'Prescription saved.'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@login_required
def get_all_medicine_data(request):
    """AJAX view to get all medicine data"""
    try:
        today = date.today()
        medicines = KahamaMedicine.objects.all()

        medicine_data = {}
        
        for medicine in medicines:
            if medicine.is_clinic_stock:
                if medicine.remain_quantity and medicine.remain_quantity > 0 and \
                   medicine.expiration_date and medicine.expiration_date >= today:
                    medicine_data[medicine.id] = {
                        "drug_name": medicine.drug_name,
                        "drug_type": medicine.drug_type,
                        "formulation_unit": medicine.formulation_unit,
                        "manufacturer": medicine.manufacturer,
                        "remain_quantity": medicine.remain_quantity,
                        "quantity": medicine.quantity,
                        "dividable": medicine.is_dividable,
                        "batch_number": medicine.batch_number,
                        "expiration_date": medicine.expiration_date.strftime("%Y-%m-%d")
                    }
            else:
                medicine_data[medicine.id] = {
                    "drug_name": medicine.drug_name,
                    "drug_type": medicine.drug_type,
                    "formulation_unit": medicine.formulation_unit,
                    "manufacturer": medicine.manufacturer,
                    "remain_quantity": medicine.remain_quantity,
                    "quantity": medicine.quantity,
                    "dividable": medicine.is_dividable,
                    "batch_number": medicine.batch_number,
                    "expiration_date": medicine.expiration_date.strftime("%Y-%m-%d") if medicine.expiration_date else None
                }

        return JsonResponse(medicine_data, safe=False, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    
@login_required
def get_all_frequency_data(request):
    """AJAX view to get all frequency data"""
    """
    Returns all frequency data in JSON format for preloading on the frontend.
    """
    try:
        # Query all PrescriptionFrequency objects
        frequencies = PrescriptionFrequency.objects.all()

        # Prepare data to be returned as JSON
        frequency_data = {
            frequency.id: {
                "name": frequency.name,
                "interval": frequency.interval,
                "description": frequency.description,
            }
            for frequency in frequencies
        }

        # Return data as JSON response
        return JsonResponse(frequency_data, safe=False, status=200)

    except Exception as e:
        # Handle errors and return error response
        return JsonResponse({"error": str(e)}, status=500)


# ==================== PROCEDURE VIEWS ====================

@login_required    
def save_remoteprocedure(request, patient_id, visit_id):
    """View for saving procedures"""
    patient = get_object_or_404(KahamaPatient, id=patient_id)
    visit = get_object_or_404(KahamaPatientVisits, id=visit_id)
    procedures = KahamaService.objects.filter(category='Procedure')
    consultation_notes = KahamaPatientDiagnosisRecord.objects.filter(
        patient=patient_id, visit=visit_id
    )
    previous_procedures = KahamaProcedure.objects.filter(patient_id=patient_id)

    context = {
        'patient': patient,
        'visit': visit,
        'procedures': procedures,
        'previous_procedures': previous_procedures,
        'consultation_notes': consultation_notes,
    }

    try:
        if request.method == 'POST':
            # Use getlist to capture multiple values
            names = request.POST.getlist('name[]')
            descriptions = request.POST.getlist('description[]')
            images = request.FILES.getlist('image[]')

            print("DEBUG - names:", names)
            print("DEBUG - descriptions:", descriptions)
            print("DEBUG - images:", images)

            # Safety check
            if not names or not descriptions:
                messages.error(request, 'Please fill out all required fields.')
                return render(request, 'kahama_template/procedure_template.html', context)

            # Pad missing images so zip_longest works
            from itertools import zip_longest
            for name, description, image in zip_longest(names, descriptions, images, fillvalue=None):
                if not name or not description:
                    continue

                print(f"Processing: name={name}, desc={description}, img={image}")

                existing_procedure = KahamaProcedure.objects.filter(
                    patient_id=patient_id,
                    visit_id=visit_id,
                    name_id=name
                ).first()

                if existing_procedure:
                    existing_procedure.description = description
                    existing_procedure.doctor = request.user.staff
                    if image:
                        existing_procedure.image = image
                    existing_procedure.save()
                    messages.success(request, f"Updated procedure {name}")
                else:
                    KahamaProcedure.objects.create(
                        patient_id=patient_id,
                        visit_id=visit_id,
                        doctor=request.user.staff,
                        name_id=name,
                        description=description,
                        image=image if image else None,
                    )
                    messages.success(request, f"Added procedure {name}")

            return redirect(reverse('kahama_doctor_consultation_save', args=[patient_id, visit_id]))

        return render(request, 'kahama_template/procedure_template.html', context)

    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return render(request, 'kahama_template/procedure_template.html', context)


@login_required    
def edit_procedure_result(request, patient_id, visit_id, procedure_id):
    """View for editing procedure results"""
    patient = get_object_or_404(KahamaPatient, id=patient_id)
    visit = get_object_or_404(KahamaPatientVisits, id=visit_id)            
    procedures = KahamaProcedure.objects.get(patient=patient, visit=visit, id=procedure_id)
    
    context = {
        'patient': patient, 
        'visit': visit,
        'procedures': procedures,
    }
    
    if request.method == 'POST':        
        form = KahamaProcedureForm(request.POST, instance=procedures)
        
        if procedures:
            if form.is_valid():
                try:
                    procedures.data_recorder = request.user.staff
                    form.save()
                    messages.success(request, 'Procedure result updated successfully!')
                except ValidationError as e:
                    messages.error(request, f'Validation Error: {e}')
            else:
                messages.error(request, 'Please correct the errors in the form.')
        else:
            form.instance.patient = patient          
            form.instance.visit = visit
            form.instance.data_recorder = request.user.staff
            
            if form.is_valid():
                try:
                    form.save()
                    messages.success(request, 'Procedure result added successfully!')
                except ValidationError as e:
                    messages.error(request, f'Validation Error: {e}')
            else:
                messages.error(request, 'Please correct the errors in the form.')
                
        return redirect(reverse('kahama_doctor_procedure_history', args=[patient.mrn]))
        
    else:
        form = KahamaProcedureForm(instance=procedures)   
        
    context['form'] = form    
    return render(request, 'kahama_template/edit_procedure_result.html', context)


@login_required
def patient_procedure_view(request):
    """View for displaying patient procedures"""
    from django.db.models import Max
    
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
            
    context = {
        'patient_procedures': patient_procedures,
    }
    
    return render(request, 'kahama_template/manage_procedure.html', context)


@login_required
def patient_procedure_history_view(request, mrn):
    """View for displaying patient procedure history"""
    patient = get_object_or_404(KahamaPatient, mrn=mrn)
    procedures = KahamaProcedure.objects.filter(patient=patient)
    patient_procedures = KahamaService.objects.filter(category='Procedure')
    
    context = {
        'patient': patient,
        'procedures': procedures,
        'patient_procedures': patient_procedures,
    }
    
    return render(request, 'kahama_template/manage_patient_procedure.html', context)


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


# ==================== REFERRAL VIEWS ====================

@login_required
def save_remotereferral(request, patient_id, visit_id):
    """View for saving referrals"""
    try:
        patient = get_object_or_404(KahamaPatient, id=patient_id)
        visit = get_object_or_404(KahamaPatientVisits, id=visit_id)        
        data_recorder = request.user.staff
        referral = KahamaReferral.objects.filter(patient=patient, visit=visit).first()   
        consultation_notes = KahamaPatientDiagnosisRecord.objects.filter(patient=patient_id, visit=visit_id)  
        
        context = {
            'patient': patient,
            'visit': visit, 
            'referral': referral,
            'consultation_notes': consultation_notes,
        }  
        
        if request.method == 'POST':
            form = KahamaReferralForm(request.POST, instance=referral)
            
            if form.is_valid():
                if referral:
                    referral = form.save(commit=False)
                    referral.patient = patient
                    referral.visit = visit
                    referral.data_recorder = data_recorder
                    referral.save()
                    messages.success(request, '')
                else:
                    form.instance.patient = patient
                    form.instance.visit = visit
                    form.instance.data_recorder = data_recorder
                    form.save()
                    messages.success(request, '')
                    
                return redirect(reverse('kahama_doctor_consultation_save', args=[patient_id, visit_id]))
            else:
                messages.error(request, 'Please correct the errors in the form.')
        else:
            form = KahamaReferralForm(instance=referral)
            
        context['form'] = form
        return render(request, 'kahama_template/save_remotereferral.html', context)
        
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return render(request, 'kahama_template/save_remotereferral.html', context)


@csrf_exempt
def change_referral_status(request):
    """AJAX view for changing referral status"""
    if request.method == 'POST':
        try:
            referral_id = request.POST.get('referralId')
            new_status = request.POST.get('newStatus')
            referral_record = KahamaReferral.objects.get(id=referral_id)
            referral_record.status = new_status
            referral_record.save()
            
            return JsonResponse({'success': True, 'message': f'Status for {referral_record} changed successfully.'})
        except KahamaReferral.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid Referral ID.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {e}'})
            
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


@login_required
def manage_referral(request):
    """View for managing referrals"""
    referrals = KahamaReferral.objects.all()
    patients = KahamaPatient.objects.all()
    
    return render(request, 'kahama_template/manage_referral.html', {'referrals': referrals, 'patients': patients})


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


# ==================== REPORT VIEWS ====================

@login_required    
def reports_comprehensive(request):
    current_year = datetime.now().year
    year_range = range(current_year, current_year - 10, -1)
    context = {
        'year_range': year_range,
        'current_year': current_year,
    }
    return render(request, 'kahama_template/reports_comprehensive.html', context)


@login_required
def reports_patients_visit_summary(request):
    """View for patient visit summary reports"""
    visits = KahamaPatientVisits.objects.all()
    context = {'visits': visits}
    
    return render(request, "kahama_template/reports_patients_visit_summary.html", context)


@login_required
def reports_patients(request):
    """View for patient reports"""
    patients_report = KahamaPatient.objects.order_by('-created_at') 
    context = {'patients': patients_report}
    
    return render(request, "kahama_template/reports_patients.html", context)


@login_required
def reports_service(request):
    """View for service reports"""
    return render(request, "kahama_template/reports_service.html")


@login_required
def reports_stock_level(request):
    """View for stock level reports"""
    return render(request, "kahama_template/reports_stock_level.html")

@login_required
def resa_report(request):
    # Get current date for filtering
    today = timezone.now().date()
    
    # Patient statistics
    total_patients = KahamaPatient.objects.count()
    
    # Visit statistics
    total_visits = KahamaPatientVisits.objects.count()
    visits_today = KahamaPatientVisits.objects.filter(created_at__date=today).count()
    
    # Procedure statistics
    total_procedures = KahamaProcedure.objects.count()
    procedures_today = KahamaProcedure.objects.filter(created_at__date=today).count()
    
    # Inventory statistics
    stock_items = KahamaMedicine.objects.filter(is_clinic_stock=True).count()
    low_stock_items = KahamaMedicine.objects.filter(
        is_clinic_stock=True, 
        remain_quantity__lte=models.F('minimum_stock_level')
    ).count()
    
    # Get recent adjustments (assuming you have a model for stock adjustments)
    # If you don't have one, you might need to create it or remove this
    recent_adjustments = 0  # Placeholder - replace with actual query if you have adjustment model
    
    # Order statistics
    service_orders = 0  # Placeholder - replace with actual query if you have service orders model
    medication_orders = 0  # Placeholder - replace with actual query if you have medication orders model
    
    # Lab statistics
    lab_orders = KahamaLaboratoryRequest.objects.count()
    lab_tests = KahamaLaboratoryRequest.objects.count()  # Same as lab_orders unless you have a different model
    
    # Staff statistics
    doctor_count = Staffs.objects.filter(role='doctor').count()
    
    # Comprehensive reports - assuming this is a count of some comprehensive report model
    # If you don't have one, you can use a placeholder or calculate differently
    comprehensive_reports = total_visits  # Using visits as a placeholder
    
    context = {
        'total_patients': total_patients,
        'total_visits': total_visits,
        'total_procedures': total_procedures,
        'current_date': timezone.now(),
        'visits_today': visits_today,
        'comprehensive_reports': comprehensive_reports,
        'stock_items': stock_items,
        'low_stock_items': low_stock_items,
        'recent_adjustments': recent_adjustments,
        'service_orders': service_orders,
        'medication_orders': medication_orders,
        'lab_orders': lab_orders,
        'procedures_today': procedures_today,
        'lab_tests': lab_tests,
        'doctor_count': doctor_count,
    }

    return render(request, "kahama_template/resa_reports.html", context) 

@login_required
def individual_visit(request, patient_id):
    """View for individual visit reports"""
    # Retrieve the KahamaPatient instance
    patient = get_object_or_404(KahamaPatient, id=patient_id)
    
    # Retrieve all visits of the patient and order them by created_at
    patient_visits = KahamaPatientVisits.objects.filter(patient=patient).order_by('-created_at')

    context = {'patient': patient, 'patient_visits': patient_visits}
    return render(request, 'kahama_template/reports_individual_visit.html', context)


# ==================== CHIEF COMPLAINT VIEWS ====================

@csrf_exempt
def save_chief_complaint(request):
    """AJAX view for saving chief complaints"""
    try:
        # Ensure the request method is POST
        if request.method == 'POST':
            # Extract data from the POST request
            patient_id = request.POST.get('patient_id')
            visit_id = request.POST.get('visit_id')
            health_record_id = request.POST.get('chief_complain_name')
            other_chief_complaint = request.POST.get('other_complaint')          
            
            if request.POST.get('chief_complain_duration'):
                duration = request.POST.get('chief_complain_duration')  
            else:
                duration = request.POST.get('other_complain_duration')       

            # Create a new ChiefComplaint object
            chief_complaint = KahamaChiefComplaint(
                duration=duration,
                patient_id=patient_id,
                visit_id=visit_id
            )

            # Set the appropriate fields based on the provided data
            if health_record_id == "other":
                # Check if a ChiefComplaint with the same other_complaint already exists for the given visit_id
                if KahamaChiefComplaint.objects.filter(visit_id=visit_id, other_complaint=other_chief_complaint).exists():
                    return JsonResponse({'status': False, 'message': 'A Other ChiefComplaint with the same name already exists for this patient'})
                chief_complaint.other_complaint = other_chief_complaint
            else:
                # Check if a ChiefComplaint with the same health_record_id already exists for the given visit_id
                if KahamaChiefComplaint.objects.filter(health_record_id=health_record_id, visit_id=visit_id).exists():
                    return JsonResponse({'status': False, 'message': 'A ChiefComplaint with the same name  already exists for this patient'})
                chief_complaint.health_record_id = health_record_id          

            chief_complaint.data_recorder = request.user.staff  
            # Save the ChiefComplaint object
            chief_complaint.save()

            # Initialize health_record_data to None
            health_record_data = None

            # Serialize the KahamaHealthRecord object if applicable
            if health_record_id and health_record_id != "other":
                health_record = KahamaHealthRecord.objects.get(pk=health_record_id)
                # Extract the name of the health record
                health_record_data = {'name': health_record.name}
            
            # Return the saved data as a JSON response
            response_data = {
                'status': True,
                'id': chief_complaint.id,
                'health_record': health_record_data,
                'duration': chief_complaint.duration,
            }

            # Include other_complaint in the response data if present
            if other_chief_complaint:
                response_data['other_complaint'] = other_chief_complaint

            return JsonResponse(response_data)

        # If request method is not POST, return an error response
        return JsonResponse({'status': False, 'message': 'Invalid request method'})
        
    except Exception as e:
        # Catch any exceptions and return an error response
        return JsonResponse({'status': False, 'message': str(e)})


@login_required
def update_chief_complaint(request, chief_complaint_id):
    """AJAX view for updating chief complaints"""
    if request.method == 'POST':
        try:
            # Fetch the complaint record
            chief_complaint = get_object_or_404(KahamaChiefComplaint, id=chief_complaint_id)
            
            # Parse the JSON data from the request body
            data = json.loads(request.body)            
            chief_complain_duration = data.get('chief_complain_duration')
            other_complaint = data.get('other_complaint')           

            if chief_complain_duration:
                chief_complaint.duration = chief_complain_duration
                
            if other_complaint:
                chief_complaint.other_complaint = other_complaint

            # Save the updated record
            chief_complaint.save()

            # Return a success response
            return JsonResponse({'status': True, 'message': 'Chief complaint updated successfully.'})
        
        except KahamaChiefComplaint.DoesNotExist:
            # Handle the case where the chief complaint record does not exist
            return JsonResponse({'status': False, 'message': 'Chief complaint not found.'})
        
        except ValueError as e:
            # Handle invalid data errors
            return JsonResponse({'status': False, 'message': f'Invalid data: {str(e)}'})
        
        except Exception as e:
            # Handle any other unexpected errors
            return JsonResponse({'status': False, 'message': f'An unexpected error occurred: {str(e)}'})

    # If not a POST request, return a method not allowed response
    return JsonResponse({'status': False, 'message': 'Invalid request method.'})


@login_required
def fetch_existing_data(request):
    """AJAX view for fetching existing chief complaint data"""
    try:
        patient_id = request.GET.get('patient_id')
        visit_id = request.GET.get('visit_id')

        existing_data = KahamaChiefComplaint.objects.filter(
            patient_id=patient_id, visit_id=visit_id
        ).values()

        modified_data = []

        admin = CustomUser.objects.get(id=request.user.id)
        staff = Staffs.objects.get(admin=admin)

        for entry in existing_data:
            display_info = None
            health_record_id = None  # Default to None

            if entry['health_record_id'] is not None:
                try:
                    health_record = KahamaHealthRecord.objects.get(pk=entry['health_record_id'])
                    display_info = health_record.name
                    health_record_id = health_record.id
                except ObjectDoesNotExist:
                    display_info = "Unknown Health Record"
                    health_record_id = entry['health_record_id']  # keep the original ID if needed
            else:
                display_info = entry['other_complaint'] if entry['other_complaint'] else "Unknown"

            modified_entry = {
                'id': entry['id'],
                'patient_id': entry['patient_id'],
                'visit_id': entry['visit_id'],
                'data_recorder_id': entry['data_recorder_id'],
                'staff_id': staff.id,
                'health_record': display_info,
                'health_record_id': health_record_id,  # Safe now
                'duration': entry['duration'],
                'created_at': entry['created_at'],
                'updated_at': entry['updated_at'],
            }
            modified_data.append(modified_entry)

        return JsonResponse(modified_data, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



@csrf_exempt
def delete_chief_complaint(request, chief_complaint_id):
    """AJAX view for deleting chief complaints"""
    try:
        if request.method == 'POST' and request.POST.get('_method') == 'DELETE':
            # Fetch the ChiefComplaint object to delete
            chief_complaint = get_object_or_404(KahamaChiefComplaint, id=chief_complaint_id)
            
            # Delete the ChiefComplaint
            chief_complaint.delete()
            
            # Return a success response
            return JsonResponse({'message': 'Chief complaint deleted successfully'})
            
        return JsonResponse({'error': 'Invalid request method'}, status=405)
        
    except Exception as e:
        # Return detailed error message for client-side display
        return JsonResponse({'error': f"Error: {str(e)}"}, status=500)


# ==================== PATIENT VISIT VIEWS ====================

@login_required
def save_patient_visit_save(request, patient_id, visit_id=None):
    """View for saving patient visits"""
    # Retrieve the patient object or handle the error if it does not exist
    patient = get_object_or_404(KahamaPatient, pk=patient_id)
    data_recorder = request.user.staff 
    
    if request.method == 'POST':
        try:
            # Retrieve form data
            visit_type = request.POST.get('visit_type')
            primary_service = request.POST.get('primary_service')

            # Check if we are editing an existing visit or adding a new one
            if visit_id:
                # Editing an existing visit
                visit = get_object_or_404(KahamaPatientVisits, pk=visit_id)
                visit.data_recorder = data_recorder
                visit.visit_type = visit_type
                visit.primary_service = primary_service
                visit.save()
                messages.success(request, '')
            else:
                # Adding a new visit
                visit = KahamaPatientVisits.objects.create(
                    patient=patient,
                    data_recorder=data_recorder,
                    visit_type=visit_type,
                    primary_service=primary_service
                )
                messages.success(request, '')

            return redirect(reverse('kahama_doctor_vitals_save', args=[patient_id, visit.id]))

        except Exception as e:
            # Handle the exception, log it or render an error message
            messages.error(request, f'Error adding/updating patient visit records: {str(e)}')
            return render(request, 'kahama_template/add_patient_visit.html', {'patient': patient, 'visit': None})

    else:
        if visit_id:
            # Editing an existing visit
            visit = get_object_or_404(KahamaPatientVisits, pk=visit_id)
        else:
            # Adding a new visit, ensure no pre-population
            visit = None

        return render(request, 'kahama_template/add_patient_visit.html', {'patient': patient, 'visit': visit})


@login_required
def reports_by_visit(request):
    """View for reports by visit"""
    # Retrieve all patients
    patients = KahamaPatient.objects.all()

    # Create a list to store each patient along with their total visit count
    patients_with_visit_counts = []

    # Iterate through each patient and calculate their total visit count
    for patient in patients:
        total_visits = KahamaPatientVisits.objects.filter(patient=patient).count()
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
def patient_visit_history_view(request, patient_id):
    """View for patient visit history"""
    # Retrieve visit history for the specified patient
    visit_history = KahamaPatientVisits.objects.filter(patient_id=patient_id)
    current_date = timezone.now().date()
    doctors = Staffs.objects.filter(role='doctor', work_place='kahama')
    patient = KahamaPatient.objects.get(id=patient_id)   
    
    return render(request, 'kahama_template/manage_patient_visit_history.html', {
        'visit_history': visit_history,
        'patient': patient,        
        'doctors': doctors,
    })


# ==================== PATIENT VITAL VIEWS ====================

@login_required
def patient_vital_all_list(request):
    """View for listing all patient vitals"""
    # Retrieve distinct patient and visit combinations
    patient_vitals = (
        KahamaPatientVital.objects.values('patient__mrn', 'visit__vst')
        .annotate(
            latest_date=Max('recorded_at')  # Get the latest record date for each patient and visit
        )
        .order_by('-latest_date')
    )
    
    context = {      
        'patient_vitals': patient_vitals,
    }
    
    return render(request, 'kahama_template/manage_all_patient_vital.html', context)


@login_required
@csrf_exempt
@require_POST
def save_remotepatient_vital(request):
    """AJAX view for saving patient vitals"""
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
        height = request.POST.get('height')
        weight = request.POST.get('weight')

        doctor = request.user.staff

        # Validate patient
        try:
            patient = KahamaPatient.objects.get(id=patient_id)
        except KahamaPatient.DoesNotExist:
            return JsonResponse({'status': False, 'message': 'Patient does not exist'})

        # Validate visit
        try:
            visit = KahamaPatientVisits.objects.get(id=visit_id)
        except KahamaPatientVisits.DoesNotExist:
            return JsonResponse({'status': False, 'message': 'Visit does not exist'})

        # Prepare blood pressure string
        blood_pressure = f"{sbp}/{dbp}" if sbp and dbp else None

        # Check for duplicates only if creating a new vital
        if not vital_id:
            duplicate_vitals = KahamaPatientVital.objects.filter(
                patient=patient,
                doctor=doctor,
                visit=visit,
                respiratory_rate=respiratory_rate,
                pulse_rate=pulse_rate,
                blood_pressure=blood_pressure,
                spo2=spo2,
                sbp=sbp,
                dbp=dbp,
                temperature=temperature,
                gcs=gcs,
                height=height,
                weight=weight,
            )
            if duplicate_vitals.exists():
                return JsonResponse({
                    'status': False,
                    'message': 'A similar vital record already exists for this patient during this visit.'
                })

        if vital_id:
            try:
                # Editing existing vital
                vital = KahamaPatientVital.objects.get(pk=vital_id)
                message = 'Vital record updated successfully'
            except KahamaPatientVital.DoesNotExist:
                return JsonResponse({'status': False, 'message': 'Vital record does not exist'})
        else:
            # Creating new vital
            vital = KahamaPatientVital()
            message = 'Vital record created successfully'

        # Update fields
        vital.visit = visit
        vital.patient = patient
        vital.doctor = doctor
        vital.respiratory_rate = respiratory_rate
        vital.pulse_rate = pulse_rate
        vital.blood_pressure = blood_pressure
        vital.sbp = sbp
        vital.dbp = dbp
        vital.spo2 = spo2
        vital.temperature = temperature
        vital.gcs = gcs
        vital.height = height
        vital.weight = weight

        vital.save()

        return JsonResponse({'status': True, 'message': message})

    except Exception as e:
        return JsonResponse({'status': False, 'message': str(e)})


@login_required
def save_remotepatient_vitals(request, patient_id, visit_id):
    """View for saving patient vitals"""
    import numpy as np

    patient = KahamaPatient.objects.get(pk=patient_id)
    visit = KahamaPatientVisits.objects.get(patient=patient_id, id=visit_id)

    # Ranges for dropdowns
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
        doctor = request.user.staff

        # Check if a vital record already exists
        existing_vital = KahamaPatientVital.objects.filter(patient=patient, visit=visit).last()
        if existing_vital:
            context['existing_vital'] = existing_vital

        if request.method == 'POST':

            # Helper to sanitize input
            def safe_decode(value):
                if value is None:
                    return ''
                return value.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')

            # Retrieve form data
            respiratory_rate = safe_decode(request.POST.get('respiratory_rate'))
            pulse_rate = safe_decode(request.POST.get('pulse_rate'))
            sbp = safe_decode(request.POST.get('sbp'))
            dbp = safe_decode(request.POST.get('dbp'))
            blood_pressure = f"{sbp}/{dbp}" if sbp and dbp else ''
            spo2 = safe_decode(request.POST.get('spo2'))
            temperature = safe_decode(request.POST.get('temperature'))
            gcs = safe_decode(request.POST.get('gcs'))
            height = safe_decode(request.POST.get('height'))
            weight = safe_decode(request.POST.get('weight'))

            if existing_vital:  # Update
                existing_vital.respiratory_rate = respiratory_rate
                existing_vital.doctor = doctor
                existing_vital.pulse_rate = pulse_rate
                existing_vital.sbp = sbp
                existing_vital.dbp = dbp
                existing_vital.spo2 = spo2
                existing_vital.blood_pressure = blood_pressure
                existing_vital.temperature = temperature
                existing_vital.gcs = gcs
                existing_vital.height = height
                existing_vital.weight = weight
                existing_vital.save()
                messages.success(request, 'Vitals updated successfully.')
            else:  # Create
                KahamaPatientVital.objects.create(
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
                    height=height,
                    weight=weight,
                )
                messages.success(request, 'Vitals recorded successfully.')

            return redirect(reverse('kahama_doctor_consultation_save', args=[patient_id, visit_id]))

        else:
            return render(request, 'kahama_template/add_remotepatient_vital.html', context)

    except Exception as e:
        messages.error(request, f'Error adding/editing remote patient vital information: {str(e)}')
        return render(request, 'kahama_template/add_remotepatient_vital.html', context)
