import calendar
from datetime import  datetime
from django.utils import timezone
import logging
from kahamahmis.forms import StaffProfileForm
import numpy as np
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.http import Http404, HttpResponse 
from django.shortcuts import render
from django.urls import reverse
from django.db.models import F
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from clinic.models import ChiefComplaint, FamilyMedicalHistory, Country, CustomUser,InsuranceCompany, PatientHealthCondition, PatientLifestyleBehavior, PatientMedicationAllergy, PatientSurgery, PrescriptionFrequency, PrimaryPhysicalExamination, Referral,  RemoteCompany, RemoteConsultation, RemoteConsultationNotes, RemoteCounseling, RemoteDischargesNotes, RemoteLaboratoryOrder, RemoteMedicine, RemoteObservationRecord, RemotePatient, RemotePatientDiagnosisRecord, RemotePatientVisits, RemotePatientVital, RemotePrescription, RemoteProcedure, RemoteReferral, RemoteService, SecondaryPhysicalExamination,Staffs
from django.template.loader import render_to_string
import pdfkit
from django.db.models import Max
from django.views.decorators.http import require_POST
from django.db.models import OuterRef, Subquery
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import logout


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
            messages.success(request, '')
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

    return render(request, "kahama_template/staff_details.html", context)



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
def patient_procedure_view(request):
    # Retrieve distinct patient and visit combinations from RemoteProcedure
    patient_procedures = (
        RemoteProcedure.objects.values('patient__mrn', 'visit__vst',
                                       'doctor__admin__first_name',
                                          'doctor__middle_name',
                                          'doctor__role',
                                          'doctor__admin__first_name',
                                       ) 
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
    return render(request, 'kahama_template/manage_procedure.html', context)

@login_required
def patient_procedure_detail_view(request, mrn, visit_number):
    """ View to display procedure details for a specific patient and visit. """
    
    # Fetch patient and visit in one go
    patient = get_object_or_404(RemotePatient, mrn=mrn)
    visit = get_object_or_404(RemotePatientVisits, vst=visit_number)
    
    # Retrieve procedures related to this patient and visit
    procedures = RemoteProcedure.objects.filter(patient=patient, visit=visit).select_related('doctor')

    # Get the doctor who performed the first procedure (if exists)
    procedure_done_by = procedures[0].doctor if procedures else None

    context = {
        'procedure_done_by': procedure_done_by,
        'patient': patient,
        'visit': visit,
        'procedure': procedures,
    }

    return render(request, 'kahama_template/manage_procedure_detail_view.html', context)


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



@csrf_exempt
def change_referral_status(request):
    if request.method == 'POST':
        try:
            referral_id = request.POST.get('referralId')
            new_status = request.POST.get('newStatus')
            
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

def view_referral(request, referral_id):
    referral = get_object_or_404(RemoteReferral, id=referral_id)
    context = {
        'referral': referral
    }
    return render(request, 'kahama_template/view_referral.html', context)

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

        return render(request, 'kahama_template/manage_patient_visit_detail_record.html', context)
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

    return render(request, 'kahama_template/manage_prescription_list.html', {
        'visit_data': visit_data_list,
    })


@login_required
def prescription_notes(request, visit_id, patient_id):
    patient = get_object_or_404(RemotePatient, id=patient_id)
    visit = get_object_or_404(RemotePatientVisits, id=visit_id)

    # Fetch prescriptions and optimize queries
    prescriptions = RemotePrescription.objects.filter(visit_id=visit_id, visit__patient_id=patient_id).select_related('medicine', 'entered_by')

    prescriber = prescriptions.first().entered_by if prescriptions.exists() else None

    # Process prescriptions to extract only the unit (e.g., 'mg' from '300mg')
    for prescription in prescriptions:
        if prescription.medicine and prescription.medicine.formulation_unit:
            prescription.medicine.unit_only = ''.join(filter(str.isalpha, prescription.medicine.formulation_unit))

    context = {
        'patient': patient,
        'visit': visit,
        'prescriptions': prescriptions,
        'prescriber': prescriber,
        'visit_number': visit.vst,
    }
    
    return render(request, "kahama_template/prescription_notes.html", context)


@login_required
def patient_vital_all_list(request):
    # Retrieve distinct patient and visit combinations
    patient_vitals = (
        RemotePatientVital.objects.values('patient__mrn', 'visit__vst')
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
def patient_vital_detail(request, patient_mrn, visit_number):
    # Get the patient instance
    patient = get_object_or_404(RemotePatient, mrn=patient_mrn)

    # Get the visit instance
    visit = get_object_or_404(RemotePatientVisits, vst=visit_number)

    # Get vitals related to the patient and visit
    vitals = RemotePatientVital.objects.filter(patient=patient, visit=visit).select_related('doctor')

    # Ensure we retrieve the doctor correctly
    vital_done_by = vitals.first().doctor if vitals.exists() and vitals.first().doctor else None

    context = {
        'vitals': vitals,
        'patient': patient,
        'patient_mrn': patient_mrn,
        'vital_done_by': vital_done_by,
        'visit': visit,
    }

    return render(request, 'kahama_template/manage_patient_vital_list.html', context)



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
                avpu=avpu,
            )
            if duplicate_vitals.exists():
                return JsonResponse({'status': False, 'message': 'A similar vital record already exists for this patient during this visit.'})

        if vital_id:
            try:
                # Editing existing vital
                vital = RemotePatientVital.objects.get(pk=vital_id)
                vital.blood_pressure = blood_pressure if sbp and dbp else vital.blood_pressure  # Use existing SBP/DBP if not provided
                message = ''
            except RemotePatientVital.DoesNotExist:
                return JsonResponse({'status': False, 'message': 'Vital record does not exist'})
        else:
            # Creating new vital
            vital = RemotePatientVital()
            vital.blood_pressure = blood_pressure
            message = ''

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
            # Define a helper function to decode safely
            def safe_decode(value):
                if value is None:
                    return ''
                return value.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')

            # Retrieve form data using safe_decode
            respiratory_rate = safe_decode(request.POST.get('respiratory_rate'))
            pulse_rate = safe_decode(request.POST.get('pulse_rate'))
            sbp = safe_decode(request.POST.get('sbp'))
            dbp = safe_decode(request.POST.get('dbp'))
            blood_pressure = f"{sbp}/{dbp}"
            spo2 = safe_decode(request.POST.get('spo2'))
            temperature = safe_decode(request.POST.get('temperature'))
            gcs = safe_decode(request.POST.get('gcs'))
            avpu = safe_decode(request.POST.get('avpu'))

            if existing_vital:  # If a record exists, update it
                existing_vital.respiratory_rate = respiratory_rate
                existing_vital.doctor = doctor
                existing_vital.pulse_rate = pulse_rate
                existing_vital.sbp = sbp
                existing_vital.dbp = dbp
                existing_vital.spo2 = spo2
                existing_vital.blood_pressure = blood_pressure
                existing_vital.temperature = temperature
                existing_vital.gcs = gcs
                existing_vital.avpu = avpu
                existing_vital.save()
                messages.success(request, '')
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
                messages.success(request, '')

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
                data_recorder=request.user.staff ,
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
def save_patient_visit_save(request, patient_id, visit_id=None):
    # Retrieve the patient object or handle the error if it does not exist
    patient = get_object_or_404(RemotePatient, pk=patient_id)
    data_recorder=request.user.staff 
    if request.method == 'POST':
        try:
            # Retrieve form data
            visit_type = request.POST.get('visit_type')
            primary_service = request.POST.get('primary_service')

            # Check if we are editing an existing visit or adding a new one
            if visit_id:
                # Editing an existing visit
                visit = get_object_or_404(RemotePatientVisits, pk=visit_id)
                visit.data_recorder = data_recorder
                visit.visit_type = visit_type
                visit.primary_service = primary_service
                visit.save()
                messages.success(request, '')
            else:
                # Adding a new visit
                visit = RemotePatientVisits.objects.create(
                    patient=patient,
                    data_recorder=data_recorder,
                    visit_type=visit_type,
                    primary_service=primary_service
                )
                messages.success(request, '')

            return redirect(reverse('kahama_save_remotepatient_vitals', args=[patient_id, visit.id]))

        except Exception as e:
            # Handle the exception, log it or render an error message
            messages.error(request, f'Error adding/updating patient visit records: {str(e)}')
            return render(request, 'kahama_template/add_patient_visit.html', {'patient': patient, 'visit': None})

    else:
        if visit_id:
            # Editing an existing visit
            visit = get_object_or_404(RemotePatientVisits, pk=visit_id)
        else:
            # Adding a new visit, ensure no pre-population
            visit = None

        return render(request, 'kahama_template/add_patient_visit.html', {'patient': patient, 'visit': visit})


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
            patient.data_recorder=request.user.staff          
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
                
                messages.success(request, '')
                
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
def generatePDF(request, patient_id, visit_id):
    pass


def counseling_list_view(request):
    counselings = RemoteCounseling.objects.all().order_by('-created_at')
    return render(request, 'kahama_template/manage_counselling.html', {'counselings': counselings})    

def view_counseling_notes(request, patient_id, visit_id):
    visit = get_object_or_404(RemotePatientVisits, id=visit_id)  
    patient = get_object_or_404(RemotePatient, id=patient_id) 
    counseling_note = get_object_or_404(RemoteCounseling, patient=patient, visit=visit)
    
    context = {
        'patient': patient,
        'visit': visit,
        'counseling_note': counseling_note,
    }
    return render(request, 'kahama_template/counseling_notes_details.html', context) 

def download_counseling_notes(request, patient_id, visit_id):
    visit = get_object_or_404(RemotePatientVisits, id=visit_id)  
    patient = get_object_or_404(RemotePatient, id=patient_id) 
    counseling_note = get_object_or_404(RemoteCounseling, patient=patient, visit=visit)

    # Render HTML template with data
    html_content = render_to_string(
        'kahama_template/counseling_notes_details.html', 
        {'counseling_note': counseling_note},
        request=request  # Ensures full URL generation
    )

    # PDF Options
    options = {
        'enable-local-file-access': '',  # Allows static files and images
        'page-size': 'A4',
        'encoding': "UTF-8",
        'quiet': '',
    }

    # PDF Generation
    try:
        config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")  # Windows path
        pdf = pdfkit.from_string(html_content, False, options=options, configuration=config)

        # Return PDF response
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Counseling_Notes_{patient}.pdf"'
        return response

    except OSError as e:
        return HttpResponse(f"PDF generation error: {e}", content_type="text/plain")

def observation_record_list_view(request):
    observation_records = RemoteObservationRecord.objects.all().order_by('-created_at')
    return render(request, 'kahama_template/manage_observation_record.html', {'observation_records': observation_records})

def view_observation_notes(request, patient_id, visit_id):
    visit = get_object_or_404(RemotePatientVisits, id=visit_id)  
    patient = get_object_or_404(RemotePatient, id=patient_id)  
    observation_record = get_object_or_404(RemoteObservationRecord, patient=patient, visit=visit)      
    
    return render(request, 'kahama_template/observation_notes_detail.html', {
        'observation_record': observation_record,
        'visit': visit,
    })


def discharge_notes_list_view(request):
    discharge_notes = RemoteDischargesNotes.objects.all().order_by('-discharge_date')
    return render(request, 'kahama_template/manage_discharge.html', {'discharge_notes': discharge_notes})


def get_all_medicine_data(request):
    """
    Returns all medicine data in JSON format for preloading on the frontend.
    """
    try:
        # Query all RemoteMedicine objects
        medicines = RemoteMedicine.objects.all()

        # Prepare data to be returned as JSON
        medicine_data = {
            medicine.id: {
                "drug_name": medicine.drug_name,
                "drug_type": medicine.drug_type,
                "formulation_unit": medicine.formulation_unit,
                "manufacturer": medicine.manufacturer,
                "remain_quantity": medicine.remain_quantity,
                "quantity": medicine.quantity,
                "dividable": medicine.dividable,
                "batch_number": medicine.batch_number,
                "expiration_date": medicine.expiration_date.strftime("%Y-%m-%d"),  # Convert date to string
                "unit_cost": float(medicine.unit_cost) if medicine.unit_cost else None,
                "buying_price": float(medicine.buying_price) if medicine.buying_price else None,
                "total_buying_price": float(medicine.total_buying_price) if medicine.total_buying_price else None,
            }
            for medicine in medicines
        }

        # Return data as JSON response
        return JsonResponse(medicine_data, safe=False, status=200)

    except Exception as e:
        # Handle errors and return error response
        return JsonResponse({"error": str(e)}, status=500)
    
def get_all_frequency_data(request):
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
        

@method_decorator(login_required, name='dispatch')
class EditStaffProfileView(View):
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
    user = request.user
    
    try:
        # Fetch the doctor's details from the Staffs model
        staff = Staffs.objects.get(admin=user, role='doctor')
        
        # Pass the doctor details to the template
        return render(request, 'kahama_template/profile.html', {'staff': staff})

    except Staffs.DoesNotExist:
        return render(request, 'kahama_template/profile.html', {'error': 'Doctor not found.'})

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
            if request.user.staffs.work_place == 'kahama':
                return redirect('kahamahmis:kahama')  # Redirect to Kahama login page
            else:
                return redirect('login')  # Redirect to default login page (Resa)

        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'kahama_template/change_password.html', {'form': form})           