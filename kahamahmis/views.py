import calendar
from datetime import date, datetime
import json
from django.utils import timezone
import logging
import pdfkit
import numpy as np
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import logout,login
from django.http import Http404, HttpResponse, HttpResponseBadRequest,HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import F
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.generic.edit import FormView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import send_mail
from clinic.emailBackEnd import EmailBackend
from django.core.exceptions import ObjectDoesNotExist
from clinic.forms import ImportStaffForm, RemoteCounselingForm, RemoteDischargesNotesForm, RemoteObservationRecordForm, RemoteReferralForm
from clinic.models import ChiefComplaint, Counseling, FamilyMedicalHistory, ImagingRecord, LaboratoryOrder,  Consultation, ContactDetails, Country, CustomUser, DiseaseRecode, InsuranceCompany, Medicine, MedicineInventory, Notification, NotificationMedicine, PathodologyRecord, PatientHealthCondition, PatientLifestyleBehavior, PatientMedicationAllergy, PatientSurgery, Patients, PrescriptionFrequency, PrimaryPhysicalExamination, Procedure, RemoteCompany, RemoteConsultation, RemoteConsultationNotes, RemoteCounseling, RemoteDischargesNotes, RemoteLaboratoryOrder, RemoteMedicine, RemoteObservationRecord, RemotePatient, RemotePatientDiagnosisRecord, RemotePatientVisits, RemotePatientVital, RemotePrescription, RemoteProcedure, RemoteReferral, RemoteService, SecondaryPhysicalExamination, ServiceRequest,Staffs
from clinic.resources import StaffResources
from tablib import Dataset
from django.db.models import Sum
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.contrib.contenttypes.models import ContentType
from django.db.models import OuterRef, Subquery
from clinic.models import Category, ConsultationFee, ConsultationNotes, Diagnosis, DiagnosticTest, Diagnosis, Equipment, EquipmentMaintenance, HealthIssue, InventoryItem, MedicationPayment, PathologyDiagnosticTest, PatientDisease, PatientVisits, PatientVital, Prescription, Procedure, Patients, QualityControl, Reagent, ReagentUsage, Referral,  Sample, Service, Supplier, UsageHistory




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
    
    

def contact(request):
    return render(request,"contact.html")
def blog_single(request):
    return render(request,"blog-single.html")
def page_404(request):
    return render(request,"404.html")


def ShowLoginKahama(request):  
  return render(request,'kahama_template/login.html')

def DoLoginKahama(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not allowed</h2>")
    else:
        user = EmailBackend.authenticate(request, request.POST.get("email"), request.POST.get("password"))
        if user is not None:
            if not user.is_active:
                messages.error(request, "Your account is not active. Please contact the administrator for support.")
                return HttpResponseRedirect(reverse("kahamahmis:kahama"))

            login(request, user)
            if user.user_type == "1":
                return HttpResponseRedirect(reverse("kahamahmis:dashboard"))
            elif user.user_type == "2":
                staff = Staffs.objects.get(admin=user)
                role = staff.role.lower()  # Convert role to lowercase for consistency
                if staff.work_place == 'kahama':
                    if role == "doctor":
                      return HttpResponseRedirect(reverse("kahamahmis:dashboard"))                    
                else :
                    messages.error(request, "You are not a staff for this hospital or clinic. Please contact the administrator for support.")
                    return HttpResponseRedirect(reverse("kahamahmis:kahama"))            
            else:
                return HttpResponseRedirect(reverse("kahamahmis:kahama"))
        else:
            messages.error(request, "Invalid Login Details")
            return HttpResponseRedirect(reverse("kahamahmis:kahama"))
    
    
def GetUserDetails(request):
  user = request.user
  if user.is_authenticated:
    return HttpResponse("User : "+user.email+" usertype : " + user.usertype)
  else:
    return HttpResponse("Please login first")   
  
  
def logout_user(request):
  logout(request)
  return HttpResponseRedirect(reverse("home"))
    
class ContactFormView(SuccessMessageMixin, FormView):
    template_name = 'contact_form.html'
    form_class = None  # No Django form is used
    success_url = '/success/'  # Set the URL where users should be redirected on success
    success_message = "Your message was submitted successfully. We'll get back to you soon."

    def form_valid(self, form):
        try:
            # Process the form data
            your_name = self.request.POST.get('your_name')
            your_email = self.request.POST.get('your_email')
            your_subject = self.request.POST.get('your_subject', '')
            your_message = self.request.POST.get('your_message')

            # Save to the model (optional)
            ContactDetails.objects.create(
                your_name=your_name,
                your_email=your_email,
                your_subject=your_subject,
                your_message=your_message
            )

            # Send email to the administrator
            send_mail(
                f'New Contact Form Submission: {your_subject}',
                f'Name: {your_name}\nEmail: {your_email}\nMessage: {your_message}',
                'from@example.com',  # Sender's email address
                ['mrishohamisi2348@gmail.com'],  # Administrator's email address
                fail_silently=False,
            )

            messages.success(self.request, self.get_success_message())
            return self.form_valid_redirection(self.form_valid_redirect())
        except Exception as e:
            messages.error(self.request, f"An error occurred: {str(e)}")
            return self.form_invalid(self.get_form())

    def form_invalid(self, form):
        # Handle the case where the form is invalid
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid_redirection(self, redirect_to):
        return self.render_to_response({'redirect_to': redirect_to})

    def form_valid_redirect(self):
        return self.get_success_url()    


def portfolio_details(request):
    return render(request,"portfolio-details.html")

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

@login_required
def manage_service(request):
    services=Service.objects.all()
    context = {
        'services':services
    }
    return render(request,"kahama_template/manage_service.html",context)

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
                return redirect('equipment_list')  # Make sure 'manage_staffs' is the name of your staff list URL

            equipment.save()
            messages.success(request, 'equipment updated successfully')
        else:
            messages.error(request, 'Invalid request method')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')

    # Redirect back to the staff list page
    return redirect('equipment_list')  # Make sure 'manage_staffs' is the name of your staff list URL

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



@login_required    
def notification_view(request):
    notifications = Notification.objects.filter(is_read=False)
    
    # Mark notifications as read when the user accesses them
    for notification in notifications:
        notification.is_read = True
        notification.save()
    
    context = {'notifications': notifications}
    return render(request, 'kahama_template/manage_notification.html', context)

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
    return redirect('kahamahmis:appointment_list')  # Adjust the URL name based on your actual URL structure

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

    return redirect('kahamahmis:appointment_list')

@login_required
def medicine_list(request):
    # Retrieve medicines and check for expired ones
    medicines = Medicine.objects.all()
    expired_medicines = medicines.filter(expiration_date__lt=timezone.now())

    # Create notifications for expired medicines
    for medicine in expired_medicines:
        message = f"The medicine '{medicine.name}' has expired."
        NotificationMedicine.objects.create(user=request.user, message=message)
    # Get unread notifications
    unread_notifications = NotificationMedicine.objects.filter(user=request.user, is_read=False)
    # Render the template with medicine data and notifications
    return render(request, 'kahama_template/manage_medicine.html', {'medicines': medicines, 'unread_notifications': unread_notifications})

@csrf_exempt
@login_required
def add_medicine(request):
    if request.method == 'POST':
        try:
            # Retrieve data from the form
            name = request.POST['name']
            medicine_type = request.POST['medicine_type']
            side_effect = request.POST.get('side_effect', '')
            dosage = request.POST['dosage']
            storage_condition = request.POST['storage_condition']
            manufacturer = request.POST['manufacturer']
            description = request.POST.get('description', '')
            expiration_date = request.POST['expiration_date']
            unit_price = request.POST['unit_price']

            # Validate expiration date
            if expiration_date <= str(date.today()):                
                return JsonResponse({'error': 'The expiration date cannot be in the past'}, status=500)

            # Save the data to the Medicine model
            medicine = Medicine.objects.create(
                name=name,
                medicine_type=medicine_type,
                side_effect=side_effect,
                dosage=dosage,
                storage_condition=storage_condition,
                manufacturer=manufacturer,
                description=description,
                expiration_date=expiration_date,
                unit_price=unit_price
            )

           
            return JsonResponse({'message': 'Medicine added successfully'}, status=200)

        except Exception as e:            
            logger.error(f"Error adding Medicine: {str(e)}")
            return JsonResponse({'error': 'Failed to add Medicine'}, status=500)

    return JsonResponse({'error': 'Failed to add Medicine'}, status=500)

@require_POST
def add_inventory(request):
    if request.method == 'POST':
        try:
            # Retrieve data from the POST request
            medicine_id = request.POST.get('medicine_id')
            quantity = request.POST.get('quantity')
            purchase_date = request.POST.get('purchase_date')

            # Perform basic validation
            if not medicine_id or not quantity or not purchase_date:
                # Handle validation error, redirect or display an error message
                return redirect('error_page')  # Adjust the URL as needed

            # Convert the quantity to an integer
            quantity = int(quantity)

            # Convert the purchase date to a datetime object
            purchase_date = datetime.strptime(purchase_date, '%Y-%m-%d').date()

            # Call the helper method to update or create the inventory
            MedicineInventory.update_or_create_inventory(medicine_id, quantity, purchase_date)

            # Perform additional processing if needed

            # Redirect to a success page or the medicine details page
            return redirect('medicine_inventory')  # Adjust the URL as needed

        except (ValueError, TypeError):
            # Handle invalid data types, redirect or display an error message
            return redirect('medicine_list')  # Adjust the URL as needed

    else:
        # Handle non-POST requests, redirect or display an error message
        return redirect('medicine_list')  # Adjust the URL as needed

@login_required    
def medicine_inventory_list(request):
    # Retrieve all medicine inventories
    medicine_inventories = MedicineInventory.objects.all()

    # Retrieve medicines with quantity below 100
    low_quantity_medicines = MedicineInventory.objects.filter(quantity__lt=100)
    current_date = timezone.now().date()
    non_expired_medicines = Medicine.objects.filter(expiration_date__gte=current_date)
    total_payment = sum(inventory.total_payment for inventory in medicine_inventories)

    # Pass the context variables to the template
    context = {
        'medicine_inventories': medicine_inventories,
        'low_quantity_medicines': low_quantity_medicines,
        'non_expired_medicines': non_expired_medicines,
        'total_payment': total_payment,
    }

    return render(request, 'kahama_template/manage_medical_inventory.html', context)

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
    unread_notification_count = Notification.objects.filter(is_read=False).count()
    patients=RemotePatient.objects.all() 
    pathology_records=PathodologyRecord.objects.all() 
    doctors=Staffs.objects.filter(role='doctor', work_place = 'kahama')
    context = {
        'patients':patients,
        'pathology_records':pathology_records,
        'doctors':doctors,
        'unread_notification_count':unread_notification_count,
        'appointments':appointments,
    }
    return render(request, 'kahama_template/manage_appointment.html', context)

@login_required
def import_staff(request):
    if request.method == 'POST':
        form = ImportStaffForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                staff_resource = StaffResources()
                new_staffs = request.FILES['staff_file']
                
                # Use tablib to load the imported data
                dataset = Dataset()
                imported_data = dataset.load(new_staffs.read(), format='xlsx')  # Assuming you are using xlsx, adjust accordingly

                for data in imported_data:
                   
                    user = CustomUser.objects.create_user(username=data[2],
                                                          password=data[2], 
                                                          email=data[2], 
                                                          first_name=data[0],
                                                          last_name=data[1],
                                                          user_type=2)
                    user.staff.middle_name =data[3],
                    user.staff.date_of_birth = data[5]
                    user.staff.gender = data[4],           
                    user.staff.phone_number = data[8]            
                    user.staff.marital_status = data[6]
                    user.staff.profession = data[7]
                    user.staff.role =data[9]
                    user.save()

                messages.success(request, 'Staff data imported successfully!')
            except Exception as e:
                messages.error(request, f'An error occurred: {e}')

    else:
        form = ImportStaffForm()

    return render(request, 'kahama_template/import_staff.html', {'form': form})

@csrf_exempt
@login_required
def add_disease(request):
    try:
        if request.method == 'POST':
            disease_name = request.POST.get('Disease')
            code = request.POST.get('Code')

            # Save data to the model
            DiseaseRecode.objects.create(disease_name=disease_name, code=code)

            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid request method'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
 
@csrf_exempt
@login_required    
def add_insurance_company(request):
    try:
        if request.method == 'POST':
            name = request.POST.get('Name')
            phone = request.POST.get('Phone')
            short_name = request.POST.get('Short_name')
            email = request.POST.get('Email')
            address = request.POST.get('Address')

            # Save data to the model
            InsuranceCompany.objects.create(
                name=name,
                phone=phone,
                short_name=short_name,
                email=email,
                address=address
            )

            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid request method'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})    
 
@csrf_exempt
@login_required      
def add_company(request):
    try:
        if request.method == 'POST':
            name = request.POST.get('Name')
            industry = request.POST.get('industry')
            sector = request.POST.get('sector')
            headquarters = request.POST.get('headquarters')
            Founded = request.POST.get('Founded')
            Notes = request.POST.get('Notes')

            # Save data to the model
            RemoteCompany.objects.create(
                name=name,
                industry=industry,
                sector=sector,
                headquarters=headquarters,
                Founded=Founded,
                Notes=Notes,
            )

            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid request method'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    
    
@csrf_exempt
def edit_remote_company(request, company_id):
    if request.method == 'POST':
        try:
            company = RemoteCompany.objects.get(id=company_id)
            # Update company fields
            company.name = request.POST.get('name')
            company.industry = request.POST.get('industry')
            company.sector = request.POST.get('sector')
            company.headquarters = request.POST.get('headquarters')
            company.Founded = request.POST.get('Founded')
            company.Notes = request.POST.get('Notes')
            company.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'error': 'Method not allowed'})    
 
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
def pathology_diagnostic_test_list(request):
    Pathology_diagnostic_tests = PathologyDiagnosticTest.objects.all()
    pathology_records=PathodologyRecord.objects.all() 
    diagnostic_tests = DiagnosticTest.objects.all()
    return render(request, 'kahama_template/manage_pathology_diagnostic_test_list.html', {
        'Pathology_diagnostic_tests': Pathology_diagnostic_tests,
        'pathology_records': pathology_records,
        'diagnostic_tests': diagnostic_tests,
        }) 





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
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'kahama_template/manage_category_list.html', {'categories': categories})


@require_POST
def add_category(request):
    try:
        category_id = request.POST.get('category_id')
        name = request.POST.get('name')
        # Add more fields as needed

        if category_id:
            # Editing an existing category
            category = Category.objects.get(pk=category_id)
            category.name = name
         
            category.save()
        else:
            # Adding a new category
            category = Category(name=name)
            category.save()

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


 
@login_required 
def inventory_list(request):
    inventory_items = InventoryItem.objects.all()  
    suppliers = Supplier.objects.all()
    categories = Category.objects.all()
    return render(request, 'kahama_template/manage_inventory_list.html', {
        'inventory_items': inventory_items,
        'suppliers': suppliers,
        'categories': categories 
        }) 



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
    return render(request, 'kahama_template/manage_usage_history_list.html', {
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
    return render(request, 'kahama_template/manage_out_of_stock_items.html', {'out_of_stock_items': out_of_stock_items}) 

@login_required
def in_stock_items(request):
    in_stock_items = InventoryItem.objects.filter(remain_quantity__gt=0)
    return render(request, 'kahama_template/manage_in_stock_items.html', {'in_stock_items': in_stock_items})   


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
        out_of_stock_medicines = MedicineInventory.objects.filter(remain_quantity=0)
        
        # Render the template with the out-of-stock medicines data
        return render(request, 'kahama_template/manage_out_of_stock_medicines.html', {'out_of_stock_medicines': out_of_stock_medicines})
    
    except Exception as e:
        # Handle any errors and return an error response
        return render(request, '404.html', {'error_message': str(e)}) 

@login_required    
def out_of_stock_reagent_view(request):
    try:
        # Query the database for out-of-stock medicines
        out_of_stock_reagent = Reagent.objects.filter(remaining_quantity=0)
        
        # Render the template with the out-of-stock medicines data
        return render(request, 'kahama_template/manage_out_of_stock_reagent.html', {'out_of_stock_reagent': out_of_stock_reagent})
    
    except Exception as e:
        # Handle any errors and return an error response
        return render(request, '404.html', {'error_message': str(e)}) 
    
@login_required    
def in_stock_medicines_view(request):
    # Retrieve medicines with inventory levels above zero
    in_stock_medicines = MedicineInventory.objects.filter(remain_quantity__gt=0)

    return render(request, 'kahama_template/manage_in_stock_medicines.html', {'in_stock_medicines': in_stock_medicines})  

@login_required
def in_stock_reagent_view(request):
    # Retrieve medicines with inventory levels above zero
    in_stock_reagent = Reagent.objects.filter(remaining_quantity__gt=0)

    return render(request, 'kahama_template/manage_in_stock_reagent.html', {'in_stock_reagent': in_stock_reagent})  

@login_required
def equipment_list(request):
    equipment_list = Equipment.objects.all()
    return render(request, 'kahama_template/manage_equipment_list.html', {'equipment_list': equipment_list})  

 
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
    return render(request, 'kahama_template/manage_equipment_maintenance_list.html',
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
    return render(request, 'kahama_template/manage_reagent_list.html', {'reagent_list': reagent_list})    

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
    return render(request, 'kahama_template/manage_reagent_usage_list.html',
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
def health_issue_list(request):
    health_issues = HealthIssue.objects.all()
    return render(request, 'kahama_template/manage_health_issues.html', {'health_issues': health_issues})       

@csrf_exempt     
@require_POST
def add_health_issue(request):
    try:
        health_id = request.POST.get('health_id')
        name = request.POST.get('name')
        description = request.POST.get('description')
        is_disease = request.POST.get('is_disease')
        severity = request.POST.get('severity')
        treatment_plan = request.POST.get('treatment_plan')
        onset_date = request.POST.get('onset_date')
        resolution_date = request.POST.get('resolution_date')

        if health_id:
            # Editing existing HealthIssue item
            health_issue = HealthIssue.objects.get(pk=health_id)
            health_issue.name = name
            health_issue.description = description
            health_issue.is_disease = bool(is_disease)
            health_issue.onset_date =  onset_date            
            health_issue.severity = severity
            health_issue.treatment_plan = treatment_plan
            health_issue.resolution_date = resolution_date
                            
            health_issue.save()
        else:
            # Adding new HealthIssue item
            health_issue = HealthIssue(
            name=name,
            description=description,
            is_disease=bool(is_disease),
            severity=severity,
            onset_date=onset_date,
            treatment_plan=treatment_plan,
            resolution_date=resolution_date
                          
               
            )
            health_issue.save()

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    
 
def fetch_model_data(request):
    selected_option = request.GET.get('selected_option')
    data = []

    if selected_option == 'disease':
        data = list(DiseaseRecode.objects.values_list('id', 'disease_name'))
    elif selected_option == 'pathology':
        data = list(PathodologyRecord.objects.values_list('id', 'name'))
    elif selected_option == 'health_issue':
        data = list(HealthIssue.objects.values_list('id', 'name'))

    return JsonResponse({'data': data})    

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
        # Retrieve visit history for the specified patient
        visits = RemotePatientVisits.objects.get(id=visit_id)
        visit_history = RemotePatientVisits.objects.filter(patient_id=patient_id)
        prescriptions = RemotePrescription.objects.filter(patient=patient_id, visit=visit_id)
        chief_complaints = ChiefComplaint.objects.filter(patient_id=patient_id, visit_id=visit_id)
        primary_physical_examination = PrimaryPhysicalExamination.objects.filter(patient_id=patient_id, visit_id=visit_id).first()
        secondary_physical_examination = SecondaryPhysicalExamination.objects.filter(patient=patient_id, visit=visit_id).first()
        consultation_notes = RemoteConsultationNotes.objects.filter(patient_id=patient_id, visit=visit_id).order_by('-created_at').first()
        previous_vitals = RemotePatientVital.objects.filter(patient=patient_id,visit=visit_id).order_by('-recorded_at')
        consultation_notes_previous = RemoteConsultationNotes.objects.filter(patient=patient_id).order_by('-created_at')
        referrals = RemoteReferral.objects.filter(patient=patient_id).order_by('-created_at')
        counselling = RemoteCounseling.objects.filter(patient=patient_id).order_by('-created_at')
        vital = RemotePatientVital.objects.filter(patient=patient_id, visit=visit_id)
        procedures = RemoteProcedure.objects.filter(patient=patient_id, visit=visit_id)
        observations = RemoteObservationRecord.objects.filter(patient=patient_id, visit=visit_id)
        lab_tests = RemoteLaboratoryOrder.objects.filter(patient=patient_id, visit=visit_id)
        procedure = RemoteProcedure.objects.filter(patient=patient_id, visit=visit_id).first()
        pathology_records = PathodologyRecord.objects.all()
        doctors = Staffs.objects.filter(role='doctor', work_place = 'kahama')
        diagnosis_record = RemotePatientDiagnosisRecord.objects.get(patient_id=patient_id, visit_id=visit_id)
        total_price = sum(prescription.total_price for prescription in prescriptions)
        patient = RemotePatient.objects.get(id=patient_id)

        return render(request, 'kahama_template/manage_patient_visit_detail_record.html', {
            'primary_physical_examination': primary_physical_examination,
            'secondary_physical_examination': secondary_physical_examination,
            'visit_history': visit_history,
            'counselling': counselling,
            'observations': observations,
            'patient': patient,
            'referrals': referrals,
            'chief_complaints': chief_complaints,
            'visits': visits,          
            'prescriptions': prescriptions,
            'total_price': total_price,
            'consultation_notes': consultation_notes,
            'pathology_records': pathology_records,
            'doctors': doctors,
            'diagnosis_record': diagnosis_record,            
            'previous_vitals': previous_vitals,
            'consultation_notes_previous': consultation_notes_previous,
            'vital': vital,
            'lab_tests': lab_tests,
            'procedures': procedures,
            'procedure': procedure,
        })
    except RemotePatientVisits.DoesNotExist:
        raise Http404("Visit does not exist")
    except RemotePrescription.DoesNotExist:
        prescriptions = None
    except ChiefComplaint.DoesNotExist:
        chief_complients = None
    except PrimaryPhysicalExamination.DoesNotExist:
        primary_physical_examination = None
    except SecondaryPhysicalExamination.DoesNotExist:
        secondary_physical_examination = None
    except RemoteConsultationNotes.DoesNotExist:
        consultation_notes = None
    except RemotePatientVital.DoesNotExist:
        previous_vitals = None
    except RemoteReferral.DoesNotExist:
        referrals = None
    except RemoteCounseling.DoesNotExist:
        counselling = None
    except RemoteProcedure.DoesNotExist:
        procedures = None
    except RemoteObservationRecord.DoesNotExist:
        observations = None
    except RemoteLaboratoryOrder.DoesNotExist:
        lab_tests = None
    except PathodologyRecord.DoesNotExist:
        pathology_records = None
    except Staffs.DoesNotExist:
        doctors = None
    except Diagnosis.DoesNotExist:
        provisional_diagnoses = None
        final_diagnoses = None
    except RemotePatient.DoesNotExist:
        raise Http404("Patient does not exist")
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)})
    

@login_required
def prescription_list(request):
    # Retrieve all patients
    patients = RemotePatient.objects.all()
    # Retrieve current date
    current_date = timezone.now().date()    
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
    # Retrieve medicines with inventory levels not equal to zero or greater than zero, and not expired
    medicines = Medicine.objects.filter(
        medicineinventory__remain_quantity__gt=0,  # Inventory level greater than zero
        expiration_date__gt=current_date  # Not expired
    ).distinct()     
    # Calculate total price of all prescriptions
    total_price = sum(prescription.total_price for prescription in prescriptions)     
    return render(request, 'kahama_template/manage_prescription_list.html', { 
        'medicines': medicines,
        'patients': patients,
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
        # Retrieve the corresponding InventoryItem
        patient = RemotePatient.objects.get(id=patient_id)
        visit = RemotePatientVisits.objects.get(id=visit_id)            


        # Check if the usageHistoryId is provided for editing
        if vital_id:
            # Editing existing usage history
            vital = RemotePatientVital.objects.get(pk=vital_id)
            vital.blood_pressure= request.POST.get('blood_pressure') 
          
        else:
            # Creating new usage history
            vital = RemotePatientVital()   
            blood_pressure = f"{sbp}/{dbp}"
            vital.blood_pressure = blood_pressure     

        # Update or set values for other fields
        vital.visit = visit
        vital.respiratory_rate = respiratory_rate
        vital.pulse_rate = pulse_rate        
        vital.doctor = doctor
        vital.sbp = sbp
        vital.dbp = dbp
        vital.spo2 = spo2
        vital.gcs = gcs
        vital.temperature = temperature
        vital.avpu = avpu
        vital.patient = patient    
        vital.save()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    
@login_required
def save_remotepatient_vitals(request, patient_id, visit_id):
    patient = RemotePatient.objects.get(pk=patient_id)
    visit = RemotePatientVisits.objects.get(patient=patient_id, id=visit_id)
    range_51 = range(51)
    temps = np.arange(start=0, stop=51, step=0.1)
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
        existing_vital = RemotePatientVital.objects.filter(patient=patient, visit=visit).first()
        
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
            return redirect(reverse('kahamahmis:save_remotesconsultation_notes', args=[patient_id, visit_id]))
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

    # Check if the laboratory order already exists for this patient on the specified visit
    laboratory_order = RemoteLaboratoryOrder.objects.filter(patient=patient, visit=visit).first()
    context = {'patient': patient, 'visit': visit, 'previous_results': previous_results, 'remote_service': remote_service} 

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
            return redirect(reverse('kahamahmis:save_remotesconsultation_notes', args=[patient_id, visit_id]))
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
                return redirect(reverse('kahamahmis:save_remotesconsultation_notes', args=[patient_id, visit_id]))
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
    data_recorder = request.user.staff
    # Retrieve existing remote counseling record if it exists
    remote_counseling = RemoteCounseling.objects.filter(patient=patient, visit=visit).first()
    
    # Prepare context for rendering the template
    context = {
        'patient': patient, 
        'visit': visit,
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
        return redirect(reverse('kahamahmis:save_remotesconsultation_notes', args=[patient_id, visit_id]))
   
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
            return redirect(reverse('kahamahmis:save_remotesconsultation_notes', args=[patient_id, visit_id]))  # Change 'success_page' to your success page URL name
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
                return redirect(reverse('kahamahmis:save_remotesconsultation_notes', args=[patient_id, visit_id]))
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
                return redirect(reverse('kahamahmis:save_remotesconsultation_notes', args=[patient_id, visit_id]))  # Redirect to the next view
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


@csrf_exempt
@require_POST
def save_diagnosis(request):
    try:
        # Extract data from the request
        diagnosis_name = request.POST.get('diagnosis_name')
        diagnosis_id = request.POST.get('diagnosis_id')

        # Check if the Diagnosis ID is provided for editing
        if diagnosis_id:
            # Editing existing diagnosis
            diagnosis = Diagnosis.objects.get(pk=diagnosis_id)
            diagnosis.diagnosis_name = diagnosis_name
        else:
            # Creating a new diagnosis
            diagnosis = Diagnosis.objects.create(diagnosis_name=diagnosis_name)

        diagnosis.save()

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    
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
                return redirect(reverse('kahamahmis:patient_info_form'))
            
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
            return redirect(reverse('kahamahmis:save_patient_health_information', args=[patient.id]))

        except Exception as e:
            # Handle the exception, you can log it or render an error message
            messages.error(request, f'Error adding Patient record : {str(e)}')
            return redirect(reverse('kahamahmis:patient_info_form'))

    # If the request method is not POST, render the form template
    range_121 = range(1, 121)
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
        return redirect(reverse('kahamahmis:patient_info_form', args=[patient_id]))

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

            return redirect(reverse('kahamahmis:save_remotepatient_vitals', args=[patient_id, latest_visit.id if latest_visit else patient_visit.id]))

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

            # Convert empty strings to None for date fields
            if dob == '':
                dob = None

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
                return redirect('kahamahmis:patients_list')
            elif 'save_continue_health' in request.POST:
                # Redirect to continue editing health information
                return redirect(reverse('kahamahmis:health_info_edit', args=[patient_id]))

        except Exception as e:
            # Handle any errors that may occur during form processing
            messages.error(request, f'Error editing Patient record: {str(e)}')
            return redirect(reverse('kahamahmis:patient_info_form_edit', args=[patient_id]))

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
                return redirect('kahamahmis:patients_list')
            elif 'save_and_continue_family_health' in request.POST:
                return redirect(reverse('kahamahmis:save_patient_visit_save', args=[patient_id]))
        
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




@csrf_exempt
@require_POST
def save_remote_service(request):
    try:
        # Extract data from the request
        service_id = request.POST.get('service_id')
        name = request.POST.get('name')
        price = request.POST.get('price')        
        description = request.POST.get('description')
        category = request.POST.get('category')



        # Check if the notes ID is provided for editing
        if service_id:
            # Editing existing consultation notes
            service = RemoteService.objects.get(pk=service_id)
        else:
            # Creating new consultation notes
            service = RemoteService()

        # Update or set values for consultation notes fields
        service.name = name
        service.price = price
        service.description = description
        service.category = category
        
        service.save()   
            
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
   

    
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

        return redirect('kahamahmis:appointment_list')
    except Exception as e:
        return HttpResponseBadRequest(f"Error: {str(e)}")
    
def counseling_list_view(request):
    counselings = Counseling.objects.all().order_by('-created_at')
    return render(request, 'kahama_template/manage_counselling.html', {'counselings': counselings})    

def observation_record_list_view(request):
    observation_records = RemoteObservationRecord.objects.all().order_by('-created_at')
    return render(request, 'kahama_template/manage_observation_record.html', {'observation_records': observation_records})

def discharge_notes_list_view(request):
    discharge_notes = RemoteDischargesNotes.objects.all().order_by('-discharge_date')
    return render(request, 'kahama_template/manage_discharge.html', {'discharge_notes': discharge_notes})