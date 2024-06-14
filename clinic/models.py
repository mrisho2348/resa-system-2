from decimal import Decimal
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.db.models.signals import post_save,pre_save,post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.fields import CKEditor5Field
from uuid import uuid4
# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, user_type=1, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, user_type=user_type, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 1)  # Set the default user_type for superusers
        return self.create_user(username, email, password, **extra_fields)
    
        
class CustomUser(AbstractUser):
    user_type_data = (
        (1, "AdminHOD"),
        (2, "Staffs"),
    )
    user_type = models.CharField(default=1, choices=user_type_data, max_length=15)
    is_active = models.BooleanField(default=True)

    # Provide unique related_name values
    groups = models.ManyToManyField(
        "auth.Group",
        verbose_name="Groups",
        blank=True,
        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
        related_name="customuser_groups",  # Add a unique related_name for groups
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        verbose_name="User permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        related_name="customuser_user_permissions",  # Add a unique related_name for user_permissions
        related_query_name="user",
    )

    objects = CustomUserManager()

    def __str__(self):
        return self.username

class AdminHOD(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='admin_hod')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    # Existing fields...
MARITAL_STATUS_CHOICES = [
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
    ]

ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('doctor', 'Doctor'),
        ('nurse', 'Nurse'),
        ('physiotherapist', 'Physiotherapist'),
        ('labTechnician', 'Lab Technician'),
        ('pharmacist', 'Pharmacist'),
        ('receptionist', 'Receptionist'),
    ]
PROFESSION_CHOICES = [
        ('doctor', 'Doctor'),
        ('nurse', 'Nurse'),
        ('pharmacist', 'Pharmacist'),
        ('developer', 'Developer'),
        ('designer', 'Designer'),
        ('manager', 'Manager'),
        ('radiologist', 'Radiologist'),
        ('lab_technician', 'Lab Technician'),
        ('receptionist', 'Receptionist'),
        ('physiotherapist', 'Physiotherapist'),
        ('accountant', 'Accountant'),
        ('security_guard', 'Security Guard'),
        ('chef', 'Chef'),
        ('cleaner', 'Cleaner'),
    ]

# Existing fields...
work_place_choices = [
        ('resa', 'Resa'),
        ('kahama', 'Kahama'),
        # Add more choices as needed
    ]

GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('non-binary', 'Non-Binary'),
        ('prefer-not-to-say', 'Prefer Not to Say'),
    ]
class Staffs(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='staff')   
    middle_name = models.TextField(blank=True)    
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True)
    date_of_birth = models.DateField(blank=True, default='2000-01-01')
    phone_number = models.CharField(max_length=14, blank=True)
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES, blank=True)   
    profession = models.CharField(max_length=20, choices=PROFESSION_CHOICES, blank=True)
    role = models.CharField(max_length=20,choices=ROLE_CHOICES,  blank=True)    
    work_place = models.CharField(max_length=50, choices=work_place_choices, blank=True)
    joining_date = models.DateField(blank=True, null=True)  # New field added here
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)  # Profile picture field added here
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    def __str__(self):
        return f"{self.admin.first_name} {self.middle_name} {self.admin.last_name}"

class InsuranceCompany(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    short_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.TextField()
    website = models.URLField(default='http://example.com')  # Add the new field with a default value
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()    
    def __str__(self):
        return self.name
   
PROCEDURE = 'Procedure'
LABORATORY = 'Laboratory'
IMAGING = 'Imaging'
DRUGS = 'Drugs'
TEST = 'Test'
CONSULTATION = 'Consultation'
EDUCATION = 'Education'
EXAMINATION = 'Examination'
VACCINATION = 'Vaccination'
MEDICATION = 'Medication'
THERAPY = 'Therapy'
REHABILITATION = 'Rehabilitation'
RENTAL = 'Rental'
PLAN = 'Plan'

TYPE_CHOICES = [
        (PROCEDURE, 'Procedure'),
        (LABORATORY, 'Laboratory'),
        (IMAGING, 'Imaging'),
        (DRUGS, 'Drugs'),
        (TEST, 'Test'),
        (CONSULTATION, 'Consultation'),
        (EDUCATION, 'Education'),
        (EXAMINATION, 'Examination'),
        (VACCINATION, 'Vaccination'),
        (MEDICATION, 'Medication'),
        (THERAPY, 'Therapy'),
        (REHABILITATION, 'Rehabilitation'),
        (RENTAL, 'Rental'),
        (PLAN, 'Plan'),
    ]
CASH = 'Cash'
INSURANCE = 'Insurance'

COVERAGE_CHOICES = [
    (CASH, 'Cash'),
    (INSURANCE, 'Insurance'),
]
    
class Service(models.Model):
    name = models.CharField(max_length=255)
    type_service = models.CharField(max_length=200, choices=TYPE_CHOICES, blank=True, null=True)  
    coverage = models.CharField(max_length=200, choices=COVERAGE_CHOICES, blank=True, null=True)         
    description = models.TextField(blank=True, null=True)
    cash_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    insurance_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    nhif_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # New field for cost
    department = models.CharField(max_length=200, blank=True, null=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        return self.name
    

class MedicineUnitMeasure(models.Model):
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=20,default="")  
    application_user = models.CharField(max_length=100,default="")  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    
    def __str__(self):
        return self.name      

class InventoryItem(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)    
    supplier = models.ForeignKey('Supplier', on_delete=models.SET_NULL, null=True, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    location_in_storage = models.CharField(max_length=100, blank=True)
    min_stock_level = models.PositiveIntegerField(null=True, blank=True)
    images_attachments = models.ImageField(upload_to='inventory/images/', null=True, blank=True)
    condition = models.CharField(max_length=50, blank=True)
    remain_quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()  
    def __str__(self):
        return self.name  
   
class UsageHistory(models.Model):
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    usage_date = models.DateField()
    quantity_used = models.PositiveIntegerField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    
    def __str__(self):
        return f"{self.usage_date} - {self.quantity_used} units"    
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        return self.name    
        
class Supplier(models.Model):
    name = models.CharField(max_length=255, unique=True)  
    address = models.CharField(max_length=100,default="")
    contact_information = models.CharField(max_length=100,default="")
    email = models.EmailField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        return self.name    
        
class PathodologyRecord(models.Model):
    name = models.CharField(max_length=255, unique=True)    
    description = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    def __str__(self):
        return self.name
    
    
class DiseaseRecode(models.Model):
    disease_name = models.CharField(max_length=255, unique=True)  
    code = models.CharField(max_length=25,unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    def __str__(self):
        return self.disease_name
  
class ContactDetails(models.Model):    
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    subscribe_newsletter = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    def __str__(self):
        return self.name
    



class Patients(models.Model):
    # Auto-incremented primary key (ID)
    # The unique constraint for MRN is maintained separately
    mrn = models.CharField(max_length=20, unique=True, editable=False)
    first_name = models.CharField(max_length=100, default="")
    middle_name = models.CharField(max_length=100,default="")
    last_name = models.CharField(max_length=100, default="")
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    age = models.IntegerField(blank=True, null=True)
    dob = models.DateField(null=True, blank=True) 
    phone = models.CharField(max_length=15)
    address = models.TextField()
    nationality = models.ForeignKey('Country', on_delete=models.CASCADE) 
     # New payment-related fields
    PAYMENT_CHOICES = [
        ('Cash', 'Cash'),
        ('Insurance', 'Insurance'),
    ]
    payment_form = models.CharField(max_length=255, choices=PAYMENT_CHOICES)
    insurance_name = models.CharField(max_length=255,default="")
    insurance_number = models.CharField(max_length=255, blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100, default="")
    emergency_contact_relation = models.CharField(max_length=100,default="")    
    emergency_contact_phone = models.CharField(max_length=20,default="0657315955")
    marital_status = models.CharField(max_length=255)
    patient_type = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def save(self, *args, **kwargs):
        # Generate MRN only if it's not provided
        if not self.mrn:
            self.mrn = generate_mrn()

        super().save(*args, **kwargs)

    def __str__(self):
    # Concatenate first name, middle name (if exists), and last name
        full_name = self.first_name
        if self.middle_name:
            full_name += ' ' + self.middle_name
        full_name += ' ' + self.last_name
        return full_name

    
def generate_mrn():
    # Retrieve the last patient's MRN from the database
    last_patient = Patients.objects.last()

    # Extract the numeric part from the last MRN, or start from 0 if there are no patients yet
    last_mrn_number = int(last_patient.mrn.split('-')[-1]) if last_patient else 0

    # Increment the numeric part for the new patient
    new_mrn_number = last_mrn_number + 1

    # Format the MRN with leading zeros and concatenate with the prefix "PAT-"
    new_mrn = f"RES-{new_mrn_number:07d}"

    return new_mrn

 
class Country(models.Model):
        name = models.CharField(max_length=100,unique=True)
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)
        objects = models.Manager()        
    
        def __str__(self):
            return f"{self.name}"    
    

class PatientVital(models.Model):
    patient = models.ForeignKey('Patients', on_delete=models.CASCADE)
    visit = models.ForeignKey('PatientVisits', on_delete=models.CASCADE,blank=True, null=True) 
    recorded_by = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True) 
    recorded_at = models.DateTimeField(auto_now_add=True)
    respiratory_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Respiratory rate in breaths per minute")
    pulse_rate = models.PositiveIntegerField(null=True, blank=True, help_text="Pulse rate in beats per minute")
    blood_pressure = models.CharField(max_length=20, null=True, blank=True, help_text="Blood pressure measurement")
    spo2 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="SPO2 measurement in percentage")
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Temperature measurement in Celsius")
    gcs = models.PositiveIntegerField(null=True, blank=True, help_text="Glasgow Coma Scale measurement")
    avpu = models.CharField(max_length=20, null=True, blank=True, help_text="AVPU scale measurement")
    weight = models.CharField(max_length=20, null=True, blank=True, help_text="weight")
    unique_identifier = models.CharField(max_length=20, unique=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        return f"Vital information for {self.patient} recorded at {self.recorded_at}"

    def save(self, *args, **kwargs):
        # Generate a unique identifier based on the patient's format
        if not self.unique_identifier:
            self.unique_identifier = self.generate_unique_identifier()
        super().save(*args, **kwargs)

    def generate_unique_identifier(self):
        last_patient_vital = PatientVital.objects.last()
        last_number = int(last_patient_vital.unique_identifier.split('-')[-1]) if last_patient_vital else 0
        new_number = last_number + 1
        return f"VTN-{new_number:07d}"
    

class PatientVisits(models.Model):
    VISIT_TYPES = (
        ('Normal', _('Normal')),
        ('Emergency', _('Emergency')),
        ('Referral', _('Referral')),
        ('Follow up', _('Follow up')),
    )

    patient = models.ForeignKey('Patients', on_delete=models.CASCADE)
    vst = models.CharField(max_length=20, unique=True, editable=False)
    visit_type = models.CharField( max_length=15, choices=VISIT_TYPES)
    visit_reason = models.TextField(blank=True, null=True)
    referral_number = models.CharField(max_length=50, blank=True, null=True)
    primary_service = models.CharField(max_length=50)
    insurance_number = models.CharField(max_length=50, blank=True, null=True)
    insurance_name = models.CharField(max_length=50, blank=True, null=True)
    payment_scheme = models.CharField(max_length=50, blank=True, null=True)
    authorization_code = models.CharField(max_length=50, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Visit')
        verbose_name_plural = _('Visits')
        
    def save(self, *args, **kwargs):
        # Generate MRN only if it's not provided
        if not self.vst:
            self.vst = generate_vst()

        super().save(*args, **kwargs)   

    def __str__(self):
        return f'{self.patient} - {self.get_visit_type_display()}'
    
def generate_vst():
    # Retrieve the last patient's VST from the database
    last_patient_visit = PatientVisits.objects.last()

    # Extract the numeric part from the last VST, or start from 0 if there are no patients yet
    last_vst_number = int(last_patient_visit.vst.split('-')[-1]) if last_patient_visit else 0

    # Increment the numeric part for the new patient
    new_vst_number = last_vst_number + 1

    # Format the VST with leading zeros and concatenate with the prefix "PAT-"
    new_vst = f"VST-{new_vst_number:07d}"

    return new_vst  

class ConsultationNotes(models.Model):
    doctor = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE)
    visit = models.ForeignKey(PatientVisits, on_delete=models.CASCADE,blank=True, null=True) 
    chief_complaints = models.TextField(null=True, blank=True)
    history_of_presenting_illness = models.TextField(null=True, blank=True)
    consultation_number = models.CharField(max_length=20, unique=True)
    physical_examination = models.TextField(null=True, blank=True)
    allergy_to_medications = models.CharField(max_length=255, null=True, blank=True)
    provisional_diagnosis = models.ManyToManyField('Diagnosis', related_name='provisional_diagnosis_notes', blank=True)
    final_diagnosis = models.ManyToManyField('Diagnosis', related_name='final_diagnosis_notes', blank=True)
    pathology = models.ManyToManyField(PathodologyRecord, blank=True)
    doctor_plan = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        return f"Consultation for {self.patient} by Dr. {self.doctor}"
    
    def save(self, *args, **kwargs):
        if not self.consultation_number:
            self.consultation_number = generate_consultation_number()
        super().save(*args, **kwargs)   
    
def generate_consultation_number():
    last_consultation_notes = ConsultationNotes.objects.last()
    last_sample_number = int(last_consultation_notes.consultation_number.split('-')[-1]) if last_consultation_notes else 0
    new_consultation_number = last_sample_number + 1
    return f"CTN-{new_consultation_number:07d}"    
   
class ImagingRecord(models.Model):
    patient = models.ForeignKey('Patients', on_delete=models.CASCADE)
    visit = models.ForeignKey('PatientVisits', on_delete=models.CASCADE)
    doctor = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True) 
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True,related_name='data_recorder') 
    imaging= models.ForeignKey(Service, on_delete=models.CASCADE,blank=True, null=True) 
    order_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    result = models.TextField(null=True, blank=True)   
    image = models.ImageField(upload_to='imaging_records/', null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        return f"Imaging Record for {self.patient} - {self.imaging} ({self.data_recorder})"
    
class ConsultationOrder(models.Model):
    patient = models.ForeignKey('Patients', on_delete=models.CASCADE)
    visit = models.ForeignKey('PatientVisits', on_delete=models.CASCADE)
    doctor = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True) 
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True,related_name='consultation_data_recorder') 
    consultation= models.ForeignKey(Service, on_delete=models.CASCADE,blank=True, null=True) 
    order_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)   
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    def __str__(self):
        return f"Consultation Order for {self.patient} - {self.data_recorder} ({self.order_date})"

class Procedure(models.Model):
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE)
    visit = models.ForeignKey(PatientVisits, on_delete=models.CASCADE,blank=True, null=True) 
    doctor = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True) 
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True,related_name='procedure_data_recorder') 
    name = models.ForeignKey(Service, on_delete=models.CASCADE,blank=True, null=True) 
    description = models.TextField(blank=True, null=True)  
    order_date = models.DateField(null=True, blank=True)     
    result = CKEditor5Field(config_name='extends',blank=True, null=True)   
    equipments_used = models.CharField(max_length=255)
    procedure_number = models.CharField(max_length=20, unique=True)  # Unique procedure number
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        return f"Procedure: {self.name} for {self.patient}"
    
    def save(self, *args, **kwargs):  
        
        # Generate and set the appointment number if it's not already set
        if not self.procedure_number:
            last_procedure = Procedure.objects.order_by('-id').first()  # Get the last appointment
            if last_procedure:
                last_number = int(last_procedure.procedure_number.split('-')[-1])
            else:
                last_number = 0
            new_number = last_number + 1
            self.procedure_number = f"PR-{new_number:07}"  # Format the appointment number
        super().save(*args, **kwargs)  # Call the original save method
        
class LaboratoryOrder(models.Model):
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE)
    visit = models.ForeignKey(PatientVisits, on_delete=models.CASCADE,blank=True, null=True) 
    doctor = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True) 
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True,related_name='lab_data_recorder') 
    name = models.ForeignKey(Service, on_delete=models.CASCADE,blank=True, null=True) 
    description = models.TextField(blank=True, null=True)  
    order_date = models.DateField(null=True, blank=True)  
    result = CKEditor5Field(config_name='extends',blank=True, null=True)    
    lab_number = models.CharField(max_length=20, unique=True)  # Unique procedure number
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        return f"LaboratoryOrder: {self.name} for {self.patient}"
    
    def save(self, *args, **kwargs):  
        
        # Generate and set the appointment number if it's not already set
        if not self.lab_number:
            last_lab_number = LaboratoryOrder.objects.order_by('-id').first()  # Get the last appointment
            if last_lab_number:
                last_number = int(last_lab_number.lab_number.split('-')[-1])
            else:
                last_number = 0
            new_number = last_number + 1
            self.lab_number = f"LAB-{new_number:07}"  # Format the appointment number
        super().save(*args, **kwargs)  # Call the original save method
   

class HospitalVehicle(models.Model):
    number = models.CharField(max_length=50)
    plate_number = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    vehicle_type = models.CharField(max_length=100)  # New field for vehicle type
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        return self.number   
    
class AmbulanceRoute(models.Model):
    from_location = models.CharField(max_length=100)
    to_location = models.CharField(max_length=100)
    distance = models.FloatField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    profit = models.DecimalField(max_digits=10, decimal_places=2)
    advanced_ambulance_cost = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.FloatField(editable=False)  # Make total field read-only
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def save(self, *args, **kwargs):
        # Convert cost and profit to Decimal objects
        cost = Decimal(str(self.cost))
        profit = Decimal(str(self.profit))

        # Calculate total using Decimal arithmetic
        self.total = cost + profit

        super(AmbulanceRoute, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.from_location} to {self.to_location}"       
    
    
class AmbulanceActivity(models.Model):
    name = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    profit = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    
    def save(self, *args, **kwargs):
        # Convert cost and profit to Decimal objects
        cost = Decimal(str(self.cost))
        profit = Decimal(str(self.profit))

        # Calculate total using Decimal arithmetic
        self.total = cost + profit

        super(AmbulanceActivity, self).save(*args, **kwargs)

    def __str__(self):
        return self.name    
        
class AmbulanceOrder(models.Model):
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE)
    visit = models.ForeignKey(PatientVisits, on_delete=models.CASCADE, blank=True, null=True) 
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True,related_name='ambulance_data_recorder') 
    service = models.CharField(max_length=100)
    from_location = models.CharField(max_length=100)
    to_location = models.CharField(max_length=100)
    order_date = models.DateField(null=True, blank=True)  
    age = models.CharField(max_length=50)
    condition = models.CharField(max_length=100)
    intubation = models.CharField(max_length=100)
    pregnancy = models.CharField(max_length=100)
    oxygen = models.CharField(max_length=100)
    ambulance_type = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=100)
    duration_hours = models.IntegerField()
    duration_days = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ambulance_number = models.CharField(max_length=20, unique=True)  # Unique ambulance number
    objects = models.Manager()
    
    def __str__(self):
        return f"Ambulance Order for {self.patient} - Service: {self.service}"
    
    def save(self, *args, **kwargs):
        if not self.ambulance_number:
            last_ambulance = AmbulanceOrder.objects.order_by('-id').first()
            if last_ambulance:
                last_number = int(last_ambulance.ambulance_number.split('-')[-1])
            else:
                last_number = 0
            new_number = last_number + 1
            self.ambulance_number = f"AMB-{new_number:07}"  # Format the ambulance number
        super().save(*args, **kwargs)
           
class AmbulanceVehicleOrder(models.Model):
    vehicle_type = models.CharField(max_length=100,blank=True, null=True)
    activities = models.CharField(max_length=255,blank=True, null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    ambulance_number = models.CharField(max_length=100,blank=True, null=True)
    organization = models.CharField(max_length=255,blank=True, null=True)
    contact_person = models.CharField(max_length=100,blank=True, null=True)
    contact_phone = models.CharField(max_length=20,blank=True, null=True)
    location = models.CharField(max_length=100,blank=True, null=True)
    duration = models.IntegerField()
    days = models.IntegerField()
    payment_mode = models.CharField(max_length=100,blank=True, null=True)
    order_date = models.DateField(null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 
    objects = models.Manager()

    def __str__(self):
        return f"{self.vehicle_type} - {self.organization}"
 


class PrescriptionFrequency(models.Model):
    name = models.CharField(max_length=100)
    interval = models.CharField(max_length=50)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    def __str__(self):
        return f"{self.name}-{self.interval}"

class Order(models.Model):

    ORDER_STATUS = [
        ('Paid', 'Paid'),
        ('Unpaid', 'Unpaid'),
    ]

    ORDER_NUMBER_PREFIX = 'ORD'  # Prefix for the order number

    order_date = models.DateField(default=timezone.now, null=True, blank=True)
    order_type =  models.TextField(blank=True, null=True)
    type_of_order =  models.TextField(blank=True, null=True)
    patient = models.ForeignKey('Patients', on_delete=models.CASCADE)
    visit = models.ForeignKey(PatientVisits, on_delete=models.CASCADE,blank=True, null=True)
    added_by = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True)
    doctor = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True,related_name='doctor')
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    is_read = models.BooleanField(default=False)
    status = models.CharField(max_length=100, choices=ORDER_STATUS, default='Unpaid')
    order_number = models.CharField(max_length=12, unique=True)

    def __str__(self):
        return f"{self.order_type} Order for {self.patient}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            last_order = Order.objects.order_by('-id').first()
            if last_order:
                last_number = int(last_order.order_number.split('-')[-1])  # Extract the numeric part
            else:
                last_number = 0
            new_number = last_number + 1
            self.order_number = f"{self.ORDER_NUMBER_PREFIX}-{new_number:07}"  # Format the order number
        super().save(*args, **kwargs)
    
class Consultation(models.Model):
    doctor = models.ForeignKey(Staffs, on_delete=models.CASCADE, related_name='doctor_consultations')
    created_by = models.ForeignKey(Staffs, on_delete=models.CASCADE, blank=True, null=True, related_name='created_consultations')
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE)
    visit = models.ForeignKey(PatientVisits, on_delete=models.CASCADE, blank=True, null=True)
    appointment_date = models.DateField()
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    STATUS_CHOICES = [
        (0, 'Pending'),
        (1, 'Completed'),
        (2, 'Canceled'),
        (3, 'Rescheduled'),
        (4, 'No-show'),
        (5, 'In Progress'),
        (6, 'Confirmed'),
        (7, 'Arrived'),
    ]
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()    
    appointment_number = models.CharField(max_length=20, unique=True) # Unique appointment number
    
    def __str__(self):
        return f"Appointment with {self.doctor.admin.first_name} {self.doctor.middle_name} {self.doctor.admin.last_name} for {self.patient.fullname} on {self.appointment_date} from {self.start_time} to {self.end_time}"
    
    def save(self, *args, **kwargs):       
        
        # Generate and set the appointment number if it's not already set
        if not self.appointment_number:
            last_appointment = Consultation.objects.order_by('-id').first()  # Get the last appointment
            if last_appointment:
                last_number = int(last_appointment.appointment_number.split('-')[-1])
            else:
                last_number = 0
            new_number = last_number + 1
            self.appointment_number = f"APT-{new_number:07}"  # Format the appointment number
        super().save(*args, **kwargs)  # Call the original save method
        

class ConsultationNotification(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Consultation Notification'
        verbose_name_plural = 'Consultation Notifications'

    def __str__(self):
        return f'Notification for Consultation ID: {self.consultation.id} - Doctor: {self.doctor.username}'        
class Notification(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)    
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    
class Referral(models.Model):
    # Patient who is being referred
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE)
    visit = models.ForeignKey(PatientVisits, on_delete=models.CASCADE,blank=True, null=True) 
    doctor = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True) 
    # Information about the referral
    source_location  = models.CharField(max_length=255, help_text='Source location of the patient',default="resa medical hospital")
    destination_location = models.CharField(max_length=255, help_text='Destination location for MedEvac')
    reason = models.TextField()
    # Additional details
    referral_date = models.DateField(auto_now_add=True, help_text='Date when the referral was made')
    # Status of the referral (e.g., pending, accepted, rejected)
    REFERRAL_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    status = models.CharField(max_length=20, choices=REFERRAL_STATUS_CHOICES, default='pending')
    # Additional fields as needed
    notes = models.TextField(blank=True, null=True, help_text='Additional notes about the referral')
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        return f"Referral for {self.patient} to {self.destination_location} at {self.source_location} on {self.referral_date}"   
    
    def get_status_class(self):
        if self.status == 'pending':
            return 'text-warning'
        elif self.status == 'accepted':
            return 'text-success'
        elif self.status == 'rejected':
            return 'text-danger'
        return ''

    def get_status_color(self):
        if self.status == 'pending':
            return 'warning'
        elif self.status == 'accepted':
            return 'success'
        elif self.status == 'rejected':
            return 'danger'
        return '' 
  
class Counseling(models.Model):
    topic = models.CharField(max_length=100)
    description = models.TextField()
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE)
    visit = models.ForeignKey(PatientVisits, on_delete=models.CASCADE,blank=True, null=True) 
    counselor = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.topic    

class NotificationMedicine(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)    
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    def __str__(self):
        return f"{self.user.username} - {self.message}"   

MEDICINE_TYPES = [
    ('Tablet', 'Tablet'),
    ('Capsule', 'Capsule'),
    ('Syrup', 'Syrup'),
    ('Injection', 'Injection'),
    ('Ointment', 'Ointment'),
    ('Drops', 'Drops'),
    ('Inhaler', 'Inhaler'),
    ('Patch', 'Patch'),
    ('Liquid', 'Liquid'),
    ('Cream', 'Cream'),
    ('Gel', 'Gel'),
    ('Suppository', 'Suppository'),
    ('Powder', 'Powder'),
    ('Lotion', 'Lotion'),
    ('Suspension', 'Suspension'),
    ('Lozenge', 'Lozenge'),
    # Add more medicine types as needed
]

class Medicine(models.Model):
    drug_name = models.CharField(max_length=100)
    drug_type = models.CharField(max_length=20, blank=True, null=True) 
    formulation_unit = models.CharField(max_length=50)    
    manufacturer = models.CharField(max_length=100)
    remain_quantity = models.PositiveIntegerField(blank=True, null=True)
    quantity = models.PositiveIntegerField(blank=True, null=True)
    dividable = models.CharField(max_length=20, blank=True, null=True)   
    batch_number = models.CharField(max_length=20,unique=True,default=12345)   
    expiration_date = models.DateField()
    cash_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    insurance_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    nhif_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    buying_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_buying_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    def save(self, *args, **kwargs):
        # Calculate total buying price before saving
        if self.buying_price is not None and self.quantity is not None:
            self.total_buying_price = float(self.buying_price) * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return self.drug_name  
    
class RemoteMedicine(models.Model):
    drug_name = models.CharField(max_length=100)
    drug_type = models.CharField(max_length=20, blank=True, null=True) 
    formulation_unit = models.CharField(max_length=50)    
    manufacturer = models.CharField(max_length=100)
    remain_quantity = models.PositiveIntegerField(blank=True, null=True)
    quantity = models.PositiveIntegerField(blank=True, null=True)
    dividable = models.CharField(max_length=20, blank=True, null=True)   
    batch_number = models.CharField(max_length=20, blank=True, null=True)   
    expiration_date = models.DateField()
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    buying_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_buying_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    def save(self, *args, **kwargs):
        # Calculate total buying price before saving
        if self.buying_price is not None and self.quantity is not None:
            self.total_buying_price = float(self.buying_price) * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return self.drug_name    
    


class MedicineInventory(models.Model):
    medicine = models.ForeignKey('Medicine', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    remain_quantity = models.PositiveIntegerField(default=0)
    purchase_date = models.DateField()
    total_payment = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        return f"{self.medicine.name} - Quantity: {self.quantity}"

    @classmethod
    def update_or_create_inventory(cls, medicine_id, quantity, purchase_date):
        existing_record = cls.objects.filter(medicine_id=medicine_id).first()

        if existing_record:
            # Update the existing record's quantity
            existing_record.quantity += quantity
            existing_record.remain_quantity += quantity
            existing_record.save()
        else:
            # Create a new record
            cls.objects.create(
                medicine_id=medicine_id,
                quantity=quantity,
                remain_quantity=quantity, 
                purchase_date=purchase_date
            )
    
class Prescription(models.Model):
    VERIFICATION_CHOICES = (
        ('verified', 'Verified'),
        ('Not Verified', 'Not Verified'),
    )

    ISSUE_CHOICES = (
        ('issued', 'Issued'),
        ('Not Issued', 'Not Issued'),
    )

    patient = models.ForeignKey('Patients', on_delete=models.CASCADE)
    entered_by = models.ForeignKey('Staffs', on_delete=models.CASCADE,blank=True, null=True)
    medicine = models.ForeignKey('Medicine', on_delete=models.CASCADE)  # Link with Medicine model
    frequency = models.ForeignKey(PrescriptionFrequency, on_delete=models.CASCADE, blank=True, null=True)
    visit = models.ForeignKey(PatientVisits, on_delete=models.CASCADE,blank=True, null=True) # Link with Medicine model
    dose = models.CharField(max_length=50)
    frequency = models.CharField(max_length=50)
    duration = models.CharField(max_length=50)
    quantity_used = models.PositiveIntegerField()   
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    verified = models.CharField(max_length=20, choices=VERIFICATION_CHOICES, default='Not Verified')
    issued = models.CharField(max_length=20, choices=ISSUE_CHOICES, default='Not Issued')
    status = models.CharField(max_length=20, choices=[('Paid', 'Paid'), ('Unpaid', 'Unpaid')], default='Unpaid')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)    
    def __str__(self):
        return f"{self.patient.first_name} - {self.medicine.name}"  # Accessing drug's name   
    
class Equipment(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)  # Description of the equipment
    manufacturer = models.CharField(max_length=100, blank=True)  # Manufacturer of the equipment
    serial_number = models.CharField(max_length=50, blank=True)  # Serial number of the equipment
    acquisition_date = models.DateField(null=True, blank=True)  # Date when the equipment was acquired
    warranty_expiry_date = models.DateField(null=True, blank=True)  # Expiry date of the warranty
    location = models.CharField(max_length=100, blank=True)  # Location where the equipment is stored
    is_active = models.BooleanField(default=True)  # Flag indicating if the equipment is currently active
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    
    def __str__(self):
        return self.name
    
class EquipmentMaintenance(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    maintenance_date = models.DateField()
    technician = models.CharField(max_length=100)  # Technician who performed the maintenance
    description = models.TextField(blank=True)  # Description of the maintenance performed
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Cost of maintenance
    notes = models.TextField(blank=True)  # Additional notes or comments
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        return f"{self.equipment.name} - Maintenance on {self.maintenance_date}" 
    
class Reagent(models.Model):
    name = models.CharField(max_length=100)
    expiration_date = models.DateField(blank=True, null=True)
    manufacturer = models.CharField(max_length=100)
    lot_number = models.CharField(max_length=50)
    storage_conditions = models.TextField(blank=True)
    quantity_in_stock = models.PositiveIntegerField()
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    remaining_quantity = models.PositiveIntegerField()  # New field for remaining quantity
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        return self.name   
    
class ReagentUsage(models.Model):
    lab_technician = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    reagent = models.ForeignKey(Reagent, on_delete=models.CASCADE)
    usage_date = models.DateField()
    quantity_used = models.PositiveIntegerField()
    # Add other reagent usage-related information
    observation = models.TextField()  # Additional field for observations or notes
    technician_notes = models.TextField()  # Additional field for technician notes 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()  
    
class QualityControl(models.Model):
    lab_technician = models.ForeignKey('Staffs', on_delete=models.CASCADE)
    control_date = models.DateField()
    # Add other quality control-related information
    control_type = models.CharField(max_length=50)  # Type of quality control performed
    result = CKEditor5Field(config_name='extends',blank=True, null=True)   
    remarks = models.TextField(blank=True)  # Additional remarks or comments

    # Add more fields as needed         
        
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 1:  # HOD
            AdminHOD.objects.create(admin=instance)
        elif instance.user_type == 2:  # Staff
            Staffs.objects.create(admin=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == 1:
        instance.admin_hod.save()
    elif instance.user_type == 2:
        instance.staff.save()



class Company(models.Model):
    name =  models.CharField(max_length=255, unique=True)
    industry = models.CharField(max_length=50, default="")
    sector = models.CharField(max_length=50, default="")
    headquarters = models.CharField(max_length=100, default="")
    Founded = models.CharField(max_length=10, default="")
    Notes = models.TextField(max_length=100, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        return self.name

# kahama

   

class RemoteCompany(models.Model):
    name =  models.CharField(max_length=255, unique=True)
    industry = models.CharField(max_length=50, default="")
    sector = models.CharField(max_length=50, default="")
    headquarters = models.CharField(max_length=100, default="")
    Founded = models.CharField(max_length=10, default="")
    Notes = models.TextField(max_length=100, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        return self.name

class PatientMedicationAllergy(models.Model):
    patient = models.ForeignKey('RemotePatient', on_delete=models.CASCADE, related_name='remote_medication_allergies')
    medicine_name =models.ForeignKey(RemoteMedicine, on_delete=models.CASCADE, related_name='remote_medicine')
    reaction = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.medicine_name} - {self.reaction}"    
    
class PatientSurgery(models.Model):
    patient = models.ForeignKey('RemotePatient', on_delete=models.CASCADE,related_name='remote_patient_surgery')
    surgery_name = models.CharField(max_length=100,blank=True, null=True)
    surgery_date = models.TextField(blank=True, null=True)   
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    def __str__(self):
        return f"{self.surgery_name} - {self.surgery_date}"  
 
class HealthRecord(models.Model):    
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    # Add more fields for health record information as needed

    def __str__(self):
        return f"{self.name}"  
    
class PatientLifestyleBehavior(models.Model):
    patient = models.OneToOneField('RemotePatient', on_delete=models.CASCADE)
    weekly_exercise_frequency =models.CharField(max_length=10, blank=True, null=True)   
    smoking = models.CharField(max_length=10, blank=True, null=True)
    alcohol_consumption = models.CharField(max_length=10, blank=True, null=True)    
    healthy_diet = models.CharField(max_length=10, blank=True, null=True)
    stress_management = models.CharField(max_length=10, blank=True, null=True)
    sufficient_sleep = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.patient}"

class MedicineRoute(models.Model):
    name = models.CharField(max_length=100)
    explanation = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    
    def __str__(self):
        return self.name  
    

def generate_for_remote_mrn():
    # Retrieve the last patient's MRN from the database
    last_patient = RemotePatient.objects.last()

    # Extract the numeric part from the last MRN, or start from 0 if there are no patients yet
    last_mrn_number = int(last_patient.mrn.split('-')[-1]) if last_patient else 0

    # Increment the numeric part for the new patient
    new_mrn_number = last_mrn_number + 1

    # Format the MRN with leading zeros and concatenate with the prefix "PAT-"
    new_mrn = f"PAT-{new_mrn_number:05d}"

    return new_mrn
    


class RemotePatient(models.Model):
    mrn = models.CharField(max_length=20, unique=True, editable=False, verbose_name='MRN')
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, default="")
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    age = models.IntegerField(blank=True, null=True)
    dob = models.DateField(null=True, blank=True)
    nationality = models.ForeignKey(Country, on_delete=models.CASCADE) 
    phone = models.CharField(max_length=20)
    osha_certificate = models.BooleanField(default=False)
    date_of_osha_certification = models.DateField(null=True, blank=True)
    insurance = models.CharField(max_length=20, choices=[('Uninsured', 'Uninsured'), ('Insured', 'Insured'), ('Unknown', 'Unknown')])
    insurance_company = models.CharField(max_length=100, blank=True, null=True)
    other_insurance_company = models.CharField(max_length=100, blank=True, null=True)
    insurance_number = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_relation = models.CharField(max_length=100, blank=True, null=True)
    other_emergency_contact_relation = models.CharField(max_length=100,blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20)
    marital_status = models.CharField(max_length=20, choices=[('Single', 'Single'), ('Married', 'Married'), ('Divorced', 'Divorced'), ('Widowed', 'Widowed')],default="Single")
    occupation = models.CharField(max_length=100, blank=True, null=True)
    other_occupation = models.CharField(max_length=100, blank=True, null=True)
    patient_type = models.CharField(max_length=100, blank=True, null=True)
    other_patient_type = models.CharField(max_length=100, blank=True, null=True)
    company = models.ForeignKey(RemoteCompany, on_delete=models.CASCADE)    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    objects = models.Manager()
    
    def save(self, *args, **kwargs):
        # Generate MRN only if it's not provided
        if not self.mrn:
            self.mrn = generate_for_remote_mrn()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.middle_name} {self.company}"   

    
class PatientHealthCondition(models.Model):
    patient = models.ForeignKey(RemotePatient, on_delete=models.CASCADE, related_name='remote_health_conditions', verbose_name='Patient')    
    health_condition = models.CharField(max_length=200, blank=True, null=True, verbose_name='Health Condition')
    health_condition_notes = models.CharField(max_length=200, blank=True, null=True, verbose_name='Health Condition Notes')  
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    objects = models.Manager()  

class FamilyMedicalHistory(models.Model):
    patient = models.ForeignKey(RemotePatient, on_delete=models.CASCADE, related_name='remote_family_medical_history', verbose_name='Patient')
    condition = models.CharField(max_length=100, verbose_name='Condition')
    relationship = models.CharField(max_length=100, blank=True, null=True, verbose_name='Relationship')
    comments = models.CharField(max_length=100, blank=True, null=True, verbose_name='Comments')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    objects = models.Manager()

    def __str__(self):
        return f"{self.patient} - {self.condition}"
            
class RemoteService(models.Model):
    name = models.CharField(max_length=225,unique=True)  
    description = models.TextField(default="")
    category = models.CharField(max_length=50, null=True, blank=True,)   
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()        
    
    def __str__(self):
        return f"{self.name}-{self.category}"
    

class RemotePatientVital(models.Model):
    patient = models.ForeignKey('RemotePatient', on_delete=models.CASCADE)
    visit = models.ForeignKey('RemotePatientVisits', on_delete=models.CASCADE)  
    doctor = models.ForeignKey('Staffs', on_delete=models.CASCADE, blank=True, null=True)
    recorded_at = models.DateTimeField(auto_now_add=True)
    respiratory_rate = models.PositiveIntegerField(null=True, blank=True, help_text="Respiratory rate in breaths per minute")
    pulse_rate = models.PositiveIntegerField(null=True, blank=True, help_text="Pulse rate in beats per minute")
    sbp = models.PositiveIntegerField(null=True, blank=True, help_text="Systolic Blood Pressure (mmHg)")
    dbp = models.PositiveIntegerField(null=True, blank=True, help_text="Diastolic Blood Pressure (mmHg)")
    blood_pressure = models.CharField(max_length=7, null=True, blank=True, help_text="Blood pressure measurement in format 'SBP/DBP'")
    spo2 = models.PositiveIntegerField(null=True, blank=True, help_text="SPO2 measurement in percentage")
    temperature = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, help_text="Temperature measurement in Celsius", default=37.5)
    gcs = models.PositiveIntegerField(null=True, blank=True, help_text="Glasgow Coma Scale measurement")
    avpu = models.CharField(max_length=20, null=True, blank=True, help_text="AVPU scale measurement") 
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    def __str__(self):
        return f"Vital information for {self.patient} recorded at {self.recorded_at}"



        

class Diagnosis(models.Model):
    diagnosis_name= models.CharField(max_length=255,unique=True)
    diagnosis_code= models.CharField(max_length=20,unique=True,default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    
    def __str__(self):
        return f"{self.diagnosis_name}-{self.diagnosis_code}"

class RemotePatientDiagnosisRecord(models.Model):
    visit = models.ForeignKey('RemotePatientVisits', on_delete=models.CASCADE) 
    patient = models.ForeignKey(RemotePatient, on_delete=models.CASCADE) 
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True)
    provisional_diagnosis = models.ManyToManyField(Diagnosis, related_name='provisional_diagnosis_records')
    final_diagnosis = models.ManyToManyField(Diagnosis, related_name='final_diagnosis_records')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    
class RemoteConsultationNotes(models.Model):
    doctor = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    patient = models.ForeignKey(RemotePatient, on_delete=models.CASCADE)
    visit = models.ForeignKey('RemotePatientVisits', on_delete=models.CASCADE)  
    history_of_presenting_illness = models.TextField(null=True, blank=True)
    type_of_illness = models.CharField(max_length=200, null=True, blank=True)  
    nature_of_current_illness = models.CharField(max_length=200, null=True, blank=True)  
    consultation_number = models.CharField(max_length=20, unique=True)  
    pathology = models.ManyToManyField(PathodologyRecord, blank=True)
    doctor_plan = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        return f"Consultation for {self.patient} by Dr. {self.doctor}"
    
    def save(self, *args, **kwargs):
        if not self.consultation_number:
            self.consultation_number = generate_remoteconsultation_number()
        super().save(*args, **kwargs)   
    
def generate_remoteconsultation_number():
    last_consultation_notes = RemoteConsultationNotes.objects.last()
    last_sample_number = int(last_consultation_notes.consultation_number.split('-')[-1]) if last_consultation_notes else 0
    new_consultation_number = last_sample_number + 1
    return f"CTN-{new_consultation_number:07d}"       
  
class RemotePatientVisits(models.Model):
    VISIT_TYPES = (
        ('Normal', _('Normal')),
        ('Emergency', _('Emergency')),
        ('Referral', _('Referral')),
        ('Follow up', _('Follow up')),
    )

    patient = models.ForeignKey('RemotePatient', on_delete=models.CASCADE)
    vst = models.CharField(max_length=20, unique=True, editable=False)
    visit_type = models.CharField( max_length=15, choices=VISIT_TYPES)     
    primary_service = models.CharField(max_length=50) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Visit')
        verbose_name_plural = _('Visits')
        
    def save(self, *args, **kwargs):
        # Generate MRN only if it's not provided
        if not self.vst:
            self.vst = remotegenerate_vst()

        super().save(*args, **kwargs)   

    def __str__(self):
        return f'{self.patient} - {self.get_visit_type_display()}'
    
def remotegenerate_vst():
    # Retrieve the last patient's VST from the database
    last_patient_visit = RemotePatientVisits.objects.last()

    # Extract the numeric part from the last VST, or start from 0 if there are no patients yet
    last_vst_number = int(last_patient_visit.vst.split('-')[-1]) if last_patient_visit else 0

    # Increment the numeric part for the new patient
    new_vst_number = last_vst_number + 1

    # Format the VST with leading zeros and concatenate with the prefix "PAT-"
    new_vst = f"VST-{new_vst_number:07d}"

    return new_vst    
        


class RemoteObservationRecord(models.Model):
    patient = models.ForeignKey('RemotePatient', on_delete=models.CASCADE)
    visit = models.ForeignKey('RemotePatientVisits', on_delete=models.CASCADE)    
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True,related_name='remote_data_recorder') 
    observation_notes = CKEditor5Field(config_name='extends',blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    def __str__(self):
        return f"Record for {self.patient} - ({self.data_recorder})"
    
class RemoteConsultationOrder(models.Model):
    patient = models.ForeignKey('RemotePatient', on_delete=models.CASCADE)
    visit = models.ForeignKey('RemotePatientVisits', on_delete=models.CASCADE)
    doctor = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True) 
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True,related_name='remote_consultation_data_recorder') 
    consultation= models.ForeignKey(RemoteService, on_delete=models.CASCADE,blank=True, null=True) 
    order_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)   
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    def __str__(self):
        return f"Consultation Order for {self.patient} - {self.data_recorder} ({self.order_date})"


        
class RemoteLaboratoryOrder(models.Model):
    patient = models.ForeignKey(RemotePatient, on_delete=models.CASCADE)
    visit = models.ForeignKey(RemotePatientVisits, on_delete=models.CASCADE,blank=True, null=True)
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True,related_name='remote_lab_data_recorder') 
    name = models.ForeignKey(RemoteService, on_delete=models.CASCADE,blank=True, null=True) 
    result = CKEditor5Field(config_name='extends',blank=True, null=True)   
    lab_number = models.CharField(max_length=20, unique=True)  # Unique procedure number
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    def __str__(self):
        return f"LaboratoryOrder: {self.name} for {self.patient}"    
    def save(self, *args, **kwargs):
        # Generate and set the appointment number if it's not already set
        if not self.lab_number:
            last_lab_number = RemoteLaboratoryOrder.objects.order_by('-id').first()  # Get the last appointment
            if last_lab_number:
                last_number = int(last_lab_number.lab_number.split('-')[-1])
            else:
                last_number = 0
            new_number = last_number + 1
            self.lab_number = f"LAB-{new_number:07}"  # Format the appointment number
        super().save(*args, **kwargs)  # Call the original save method
   

class RemoteHospitalVehicle(models.Model):
    number = models.CharField(max_length=50)
    plate_number = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    vehicle_type = models.CharField(max_length=100)  # New field for vehicle type
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        return self.number   
    
class RemoteAmbulanceRoute(models.Model):
    from_location = models.CharField(max_length=100)
    to_location = models.CharField(max_length=100)
    distance = models.FloatField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    profit = models.DecimalField(max_digits=10, decimal_places=2)
    advanced_ambulance_cost = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.FloatField(editable=False)  # Make total field read-only
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def save(self, *args, **kwargs):
        # Convert cost and profit to Decimal objects
        cost = Decimal(str(self.cost))
        profit = Decimal(str(self.profit))

        # Calculate total using Decimal arithmetic
        self.total = cost + profit

        super(RemoteAmbulanceRoute, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.from_location} to {self.to_location}"       
    
    
class RemoteAmbulanceActivity(models.Model):
    name = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    profit = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    
    def save(self, *args, **kwargs):
        # Convert cost and profit to Decimal objects
        cost = Decimal(str(self.cost))
        profit = Decimal(str(self.profit))

        # Calculate total using Decimal arithmetic
        self.total = cost + profit

        super(RemoteAmbulanceActivity, self).save(*args, **kwargs)

    def __str__(self):
        return self.name    
        
class RemoteAmbulanceOrder(models.Model):
    patient = models.ForeignKey(RemotePatient, on_delete=models.CASCADE)
    visit = models.ForeignKey(RemotePatientVisits, on_delete=models.CASCADE, blank=True, null=True) 
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True,related_name='remote_ambulance_data_recorder') 
    service = models.CharField(max_length=100)
    from_location = models.CharField(max_length=100)
    to_location = models.CharField(max_length=100)
    order_date = models.DateField(null=True, blank=True)  
    age = models.CharField(max_length=50)
    condition = models.CharField(max_length=100)
    intubation = models.CharField(max_length=100)
    pregnancy = models.CharField(max_length=100)
    oxygen = models.CharField(max_length=100)
    ambulance_type = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=100)
    duration_hours = models.IntegerField()
    duration_days = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ambulance_number = models.CharField(max_length=20, unique=True)  # Unique ambulance number
    objects = models.Manager()
    
    def __str__(self):
        return f"Ambulance Order for {self.patient} - Service: {self.service}"
    
    def save(self, *args, **kwargs):
        if not self.ambulance_number:
            last_ambulance = RemoteAmbulanceOrder.objects.order_by('-id').first()
            if last_ambulance:
                last_number = int(last_ambulance.ambulance_number.split('-')[-1])
            else:
                last_number = 0
            new_number = last_number + 1
            self.ambulance_number = f"AMB-{new_number:07}"  # Format the ambulance number
        super().save(*args, **kwargs)
           
class RemoteAmbulanceVehicleOrder(models.Model):
    vehicle_type = models.CharField(max_length=100,blank=True, null=True)
    activities = models.CharField(max_length=255,blank=True, null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    ambulance_number = models.CharField(max_length=100,blank=True, null=True)
    organization = models.CharField(max_length=255,blank=True, null=True)
    contact_person = models.CharField(max_length=100,blank=True, null=True)
    contact_phone = models.CharField(max_length=20,blank=True, null=True)
    location = models.CharField(max_length=100,blank=True, null=True)
    duration = models.IntegerField()
    days = models.IntegerField()
    payment_mode = models.CharField(max_length=100,blank=True, null=True)
    order_date = models.DateField(null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 
    objects = models.Manager()

    def __str__(self):
        return f"{self.vehicle_type} - {self.organization}"
               
class RemoteProcedure(models.Model):
    patient = models.ForeignKey(RemotePatient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Staffs, on_delete=models.CASCADE, blank=True, null=True)
    visit = models.ForeignKey(RemotePatientVisits, on_delete=models.CASCADE)   
    name = models.ForeignKey(RemoteService, on_delete=models.CASCADE, blank=True, null=True) 
    description = models.TextField()   
    result = CKEditor5Field(config_name='extends',blank=True, null=True)  
    image = models.ImageField(upload_to='procedure_images/', blank=True, null=True)  # New field for uploading images
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        return f"Procedure: {self.name} for {self.patient}"
    

class RemoteOrder(models.Model):

    ORDER_STATUS = [
        ('Paid', 'Paid'),
        ('Unpaid', 'Unpaid'),
    ]

    ORDER_NUMBER_PREFIX = 'ORD'  # Prefix for the order number

    order_date = models.DateField(default=timezone.now, null=True, blank=True)
    order_type =  models.TextField(blank=True, null=True)
    patient = models.ForeignKey('RemotePatient', on_delete=models.CASCADE)
    visit = models.ForeignKey(RemotePatientVisits, on_delete=models.CASCADE,blank=True, null=True)
    added_by = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True)
    doctor = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True,related_name='remote_doctor')
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    is_read = models.BooleanField(default=False)
    status = models.CharField(max_length=100, choices=ORDER_STATUS, default='Unpaid')
    order_number = models.CharField(max_length=12, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 
    objects = models.Manager()
    
    def __str__(self):
        return f"{self.order_type} Order for {self.patient}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            last_order = RemoteOrder.objects.order_by('-id').first()
            if last_order:
                last_number = int(last_order.order_number.split('-')[-1])  # Extract the numeric part
            else:
                last_number = 0
            new_number = last_number + 1
            self.order_number = f"{self.ORDER_NUMBER_PREFIX}-{new_number:07}"  # Format the order number
        super().save(*args, **kwargs)
    

     
class RemoteConsultation(models.Model):
    doctor = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    patient = models.ForeignKey(RemotePatient, on_delete=models.CASCADE)
    visit = models.ForeignKey(RemotePatientVisits, on_delete=models.CASCADE,blank=True, null=True)
    created_by = models.ForeignKey(Staffs, on_delete=models.CASCADE, blank=True, null=True, related_name='remote_created_consultations')
    appointment_date = models.DateField()
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    STATUS_CHOICES = [
        (0, 'Pending'),
        (1, 'Completed'),
        (2, 'Canceled'),
        (3, 'Rescheduled'),
        (4, 'No-show'),
        (5, 'In Progress'),
        (6, 'Confirmed'),
        (7, 'Arrived'),
    ]
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)   
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()    
    
    def __str__(self):
        return f"Appointment with {self.doctor.admin.first_name} {self.doctor.middle_name} {self.doctor.admin.last_name} for {self.patient.fullname} on {self.appointment_date} from {self.start_time} to {self.end_time}"
    
    def save(self, *args, **kwargs):
        # Set a default pathodology record if none is provided
        if not self.pathodology_record:
            default_pathodology = PathodologyRecord.objects.get_or_create(name="Default Pathodology")[0]
            self.pathodology_record = default_pathodology

        super().save(*args, **kwargs)


class RemoteCounseling(models.Model):    
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True) 
    counselling_notes = CKEditor5Field(config_name='extends',blank=True, null=True)
    patient = models.ForeignKey(RemotePatient, on_delete=models.CASCADE)
    visit = models.ForeignKey(RemotePatientVisits, on_delete=models.CASCADE,blank=True, null=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()   
    def __str__(self):
        return self.patient   
class RemoteDischargesNotes(models.Model):    
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True) 
    discharge_condition  = models.CharField(max_length=255)
    discharge_notes = CKEditor5Field(config_name='extends',blank=True, null=True)
    patient = models.ForeignKey(RemotePatient, on_delete=models.CASCADE)
    visit = models.ForeignKey(RemotePatientVisits, on_delete=models.CASCADE,blank=True, null=True) 
    discharge_date = models.DateTimeField(auto_now_add=True)    
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()   
    def __str__(self):
        return self.patient   
   
NATURE_OF_REFERRAL_CHOICES = (
    ('Med Evac', 'Med Evac'),
    ('Referred', 'Referral'),
)

TRANSPORT_MODEL_CHOICES = (
    ('Ground Ambulance', 'Ground Ambulance'),
    ('Air Ambulance', 'Air Ambulance'),
    ('Private Vehicle', 'Private Vehicle'),
    ('Self Transport', 'Self Transport'),
    ('Company Walking', 'Company Walking'),
    ('Walking', 'Walking'),
    ('Motorcycle', 'Motorcycle'),
    ('Others', 'Others'),
    ('Unknown', 'Unknown'),
)     
class RemoteReferral(models.Model):
    # Patient who is being referred
    patient = models.ForeignKey(RemotePatient, on_delete=models.CASCADE)   
    visit = models.ForeignKey(RemotePatientVisits, on_delete=models.CASCADE,blank=True, null=True)
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True) 
    source_location  = models.CharField(max_length=255, help_text='Source location of the patient',default="resa medical hospital")
    destination_location = models.CharField(max_length=255, help_text='Destination location for MedEvac')
    rfn = models.CharField(max_length=20, unique=True, editable=False)  
    notes=   CKEditor5Field(config_name='extends',blank=True, null=True) 
    nature_of_referral = models.CharField(max_length=20, choices=NATURE_OF_REFERRAL_CHOICES, default='Referred')
    transport_model = models.CharField(max_length=50, choices=TRANSPORT_MODEL_CHOICES, default='Ground Ambulance')
    
    # Status of the referral (e.g., pending, accepted, rejected)
    REFERRAL_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    status = models.CharField(max_length=20, choices=REFERRAL_STATUS_CHOICES, default='pending')    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    
    def save(self, *args, **kwargs):
        if not self.rfn:
            last_referral_no = RemoteReferral.objects.order_by('-id').first()
            if last_referral_no:
                last_rfn = int(last_referral_no.rfn.split('-')[-1])
                new_rfn = f"RFN-{last_rfn + 1:07d}"
            else:
                new_rfn = "RFN-0000001"
            self.rfn = new_rfn
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Referral for {self.patient} to {self.destination_location} at {self.source_location} on {self.created_at}"   
    
    def get_status_class(self):
        if self.status == 'pending':
            return 'text-warning'
        elif self.status == 'accepted':
            return 'text-success'
        elif self.status == 'rejected':
            return 'text-danger'
        return ''

    def get_status_color(self):
        if self.status == 'pending':
            return 'warning'
        elif self.status == 'accepted':
            return 'success'
        elif self.status == 'rejected':
            return 'danger'
        return ''




class ChiefComplaint(models.Model):    
    patient = models.ForeignKey(RemotePatient, on_delete=models.CASCADE)
    visit = models.ForeignKey(RemotePatientVisits, on_delete=models.CASCADE,blank=True, null=True)
    health_record = models.ForeignKey(HealthRecord, on_delete=models.CASCADE,blank=True, null=True)
    other_complaint = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    # Other fields for Chief Complaint
    def __str__(self):
        return f"{self.health_record.name} - {self.duration}"    
    
class PrimaryPhysicalExamination(models.Model):
    patient = models.ForeignKey(RemotePatient, on_delete=models.CASCADE)
    visit = models.ForeignKey(RemotePatientVisits, on_delete=models.CASCADE,blank=True, null=True)
    airway = models.CharField(max_length=200,blank=True, null=True)
    patent_airway = models.CharField(max_length=200,blank=True, null=True)
    notpatient_explanation = models.TextField(blank=True, null=True)
    breathing = models.CharField(max_length=200,blank=True, null=True)
    normal_breathing = models.TextField(blank=True, null=True)
    abnormal_breathing = models.CharField(max_length=200,blank=True, null=True)
    circulating = models.CharField(max_length=200,blank=True, null=True)
    normal_circulating = models.TextField(blank=True, null=True)
    abnormal_circulating = models.CharField(max_length=200,blank=True, null=True)    
    gcs = models.CharField(max_length=200,blank=True, null=True)
    rbg = models.CharField(max_length=200,blank=True, null=True)
    pupil = models.CharField(max_length=200,blank=True, null=True)
    pain_score = models.CharField(max_length=200,blank=True, null=True)
    avpu = models.CharField(max_length=200,blank=True, null=True)
    exposure = models.CharField(max_length=200,blank=True, null=True)
    normal_exposure = models.CharField(max_length=200,blank=True, null=True)
    abnormal_exposure = models.CharField(max_length=200,blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        return f"Physical Examination - {self.pk}"
    
class SecondaryPhysicalExamination(models.Model):
    patient = models.ForeignKey(RemotePatient, on_delete=models.CASCADE)
    visit = models.ForeignKey(RemotePatientVisits, on_delete=models.CASCADE,blank=True, null=True)
    heent = models.CharField(max_length=50, blank=True, null=True)
    cns = models.CharField(max_length=50, blank=True, null=True)
    normal_cns = models.CharField(max_length=50, blank=True, null=True)
    abnormal_cns = models.CharField(max_length=50, blank=True, null=True)
    cvs = models.CharField(max_length=50, blank=True, null=True)
    normal_cvs = models.CharField(max_length=50, blank=True, null=True)
    abnormal_cvs = models.CharField(max_length=50, blank=True, null=True)
    rs = models.CharField(max_length=50, blank=True, null=True)
    normal_rs = models.CharField(max_length=50, blank=True, null=True)
    abnormal_rs = models.CharField(max_length=50, blank=True, null=True)
    pa = models.CharField(max_length=50, blank=True, null=True)
    normal_pa = models.CharField(max_length=50, blank=True, null=True)
    abnormal_pa = models.CharField(max_length=50, blank=True, null=True)
    gu = models.CharField(max_length=100, blank=True, null=True)
    normal_gu = models.CharField(max_length=100, blank=True, null=True)
    abnormal_gu = models.CharField(max_length=100, blank=True, null=True)
    mss = models.CharField(max_length=100, blank=True, null=True)    
    normal_mss = models.CharField(max_length=100, blank=True, null=True)    
    abnormal_mss = models.CharField(max_length=100, blank=True, null=True)    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    
    def __str__(self):
        return self.pk

  
class RemoteReagent(models.Model):
    name = models.CharField(max_length=255, unique=True)
    supplier = models.CharField(max_length=255, blank=True, null=True)
    quantity = models.PositiveIntegerField()
    expiry_date = models.DateField()
    storage_conditions = models.TextField(blank=True, null=True)
    date_received = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name  
    
class RemoteEquipment(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    serial_number = models.CharField(max_length=255, unique=True)
    manufacturer = models.CharField(max_length=255, blank=True, null=True)
    purchase_date = models.DateField()
    warranty_expiry_date = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50, choices=[('Operational', 'Operational'), ('Under Maintenance', 'Under Maintenance'), ('Out of Service', 'Out of Service')], default='Operational')
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name      
    
class RemotePrescription(models.Model):
    VERIFICATION_CHOICES = (
        ('verified', 'Verified'),
        ('not_verified', 'Not Verified'),
    )

    ISSUE_CHOICES = (
        ('issued', 'Issued'),
        ('not_issued', 'Not Issued'),
    )

    patient = models.ForeignKey('RemotePatient', on_delete=models.CASCADE)
    entered_by = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True)
    medicine = models.ForeignKey(RemoteMedicine, on_delete=models.CASCADE)  # Link with Medicine model
    visit = models.ForeignKey(RemotePatientVisits, on_delete=models.CASCADE)  # Link with Medicine model
    prs_no = models.CharField(max_length=20, unique=True, editable=False)    
    dose = models.CharField(max_length=50)
    frequency = models.ForeignKey(PrescriptionFrequency, on_delete=models.CASCADE, blank=True, null=True)
    duration = models.CharField(max_length=50)
    quantity_used = models.PositiveIntegerField()   
    verified = models.CharField(max_length=20, choices=VERIFICATION_CHOICES, default='not_verified')
    issued = models.CharField(max_length=20, choices=ISSUE_CHOICES, default='not_issued')
    status = models.CharField(max_length=20, choices=[('paid', 'Paid'), ('unpaid', 'Unpaid')], default='unpaid')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Generate a unique identifier based on count of existing records
        if not self.prs_no:
            self.prs_no = generate_remoteprescription_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.patient.fullname} - {self.drug.name}"  # Accessing drug's name   
    
def generate_remoteprescription_id():
    last_prescription = RemotePrescription.objects.last()
    last_sample_number = int(last_prescription.prs_no.split('-')[-1]) if last_prescription else 0
    new_prescription_id = last_sample_number + 1
    return f"PRS-{new_prescription_id:07d}"   
    
    
# financial part

class Payroll(models.Model):
    STATUS_CHOICES = [
        ('processed', 'Processed'),
        ('pending', 'Pending'),
        ('canceled', 'Canceled'),
    ]

    payroll_date = models.DateField()
    total_salary = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    payment_method = models.ForeignKey('PaymentMethod', on_delete=models.SET_NULL, null=True, blank=True)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    def __str__(self):
        return f"Payroll for {self.payroll_date}"
  

class BankAccount(models.Model):   
    bank_name = models.CharField(max_length=100, unique=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        return f"Bank:  {self.bank_name}"    

class SalaryPayment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('pending', 'Pending'),
        ('failed', 'Failed'),
    ]

    employee = models.ForeignKey('Employee', on_delete=models.CASCADE)
    payroll = models.ForeignKey('Payroll', on_delete=models.CASCADE)    
    payment_date = models.DateField()
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES)
    payment_details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    def __str__(self):
        return f"Salary payment  for {self.employee} on {self.payment_date}" 
    
    class Meta:
        verbose_name = " Salary Payment"   

class Employee(models.Model):
    name =  models.OneToOneField(Staffs, on_delete=models.CASCADE,blank=True, null=True) 
    employee_id = models.CharField(max_length=20, unique=True)    
    department = models.CharField(max_length=100)
    FULL_TIME = 'Full-time'
    PART_TIME = 'Part-time'
    CONTRACT = 'Contract'

    EMPLOYMENT_CHOICES = [
        (FULL_TIME, 'Full-time'),
        (PART_TIME, 'Part-time'),
        (CONTRACT, 'Contract'),
    ]

    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    bank_account = models.ForeignKey('BankAccount', on_delete=models.SET_NULL, blank=True, null=True)
    bank_account_number = models.CharField(max_length=30)  # Associated bank account number   
    account_holder_name = models.CharField(max_length=100, blank=True, null=True)
    # Organization-specific identification numbers
    tin_number = models.CharField(max_length=20, blank=True, null=True)  # TRA TIN number
    nssf_membership_number = models.CharField(max_length=20, blank=True, null=True)  # NSSF membership number
    nhif_number = models.CharField(max_length=20, blank=True, null=True)  # NHIF number
    wcf_number = models.CharField(max_length=20, blank=True, null=True)  # WCF number

    # Deduction status for each organization
    tra_deduction_status = models.BooleanField(default=False)  # TRA deduction status
    nssf_deduction_status = models.BooleanField(default=False)  # NSSF deduction status
    wcf_deduction_status = models.BooleanField(default=False)  # WCF deduction status
    heslb_deduction_status = models.BooleanField(default=False)  # HESLB deduction status
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    
    def save(self, *args, **kwargs):
        # Generate MRN only if it's not provided
        if not self.employee_id:
            self.employee_id = generate_employee_id()
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.name.admin.first_name} {self.name.middle_name} {self.name.admin.last_name}"
    
def generate_employee_id():
    # Retrieve the last patient's MRN from the database
    last_employee = Employee.objects.last()

    # Extract the numeric part from the last MRN, or start from 0 if there are no patients yet
    last_employee_number = int(last_employee.employee_id.split('-')[-1]) if last_employee else 0

    # Increment the numeric part for the new patient
    new_employee_number = last_employee_number + 1

    # Format the MRN with leading zeros and concatenate with the prefix "PAT-"
    new_number= f"RES-{new_employee_number:05d}"

    return new_number    
    
class DeductionOrganization(models.Model):
    name = models.CharField(max_length=100)
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    def __str__(self):
        return self.name
    
class EmployeeDeduction(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    payroll = models.ForeignKey(Payroll, on_delete=models.CASCADE)
    organization = models.ForeignKey(DeductionOrganization, on_delete=models.CASCADE)
    deducted_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    # Add any additional fields as needed

    def __str__(self):
        return f"Deduction for {self.employee.name} in {self.payroll} for {self.organization}"
    
    
class SalaryChangeRecord(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    payroll = models.ForeignKey(Payroll, on_delete=models.CASCADE)
    previous_salary = models.DecimalField(max_digits=10, decimal_places=2)
    new_salary = models.DecimalField(max_digits=10, decimal_places=2)
    change_date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 
    objects = models.Manager()
    def __str__(self):
        return f"Salary change for {self.employee} on {self.change_date}"        
    
class PaymentMethod(models.Model):
    name = models.CharField(max_length=100,unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 
    objects = models.Manager()
    def __str__(self):
        return self.name    
    
class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100,unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 
    objects = models.Manager()
    def __str__(self):
        return self.name

    
class Expense(models.Model):
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
    additional_details = models.TextField(blank=True)
    receipt = models.FileField(upload_to='expense_receipts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 
    objects = models.Manager()
    def __str__(self):
        return f"Expense of {self.amount} on {self.date}"

class Investment(models.Model):
    investment_type = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True)

    # Add any additional fields as needed
    
    def __str__(self):
        return f"{self.investment_type} - {self.amount} - {self.date}"
    
class Grant(models.Model):
    grant_name = models.CharField(max_length=100)
    funding_amount = models.DecimalField(max_digits=10, decimal_places=2)
    donor_name = models.CharField(max_length=100)
    grant_date = models.DateField()
    description = models.TextField(blank=True)

    # Add any additional fields as needed

    def __str__(self):
        return f"{self.grant_name} - {self.funding_amount} - {self.grant_date}"

class GovernmentProgram(models.Model):
    program_name = models.CharField(max_length=100)
    funding_amount = models.DecimalField(max_digits=10, decimal_places=2)
    eligibility_criteria = models.TextField()
    description = models.TextField(blank=True)

    # Add any additional fields as needed

    def __str__(self):
        return self.program_name    
    
class Invoice(models.Model):
    STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('pending', 'Pending'),
        ('overdue', 'Overdue'),
    ]

    number = models.CharField(max_length=50, unique=True)  # Ensure uniqueness
    date = models.DateField()
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    client = models.ForeignKey('Clients', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 
    objects = models.Manager()
    def save(self, *args, **kwargs):
        if not self.number:  # If the invoice number is not set
            last_invoice = Invoice.objects.order_by('-id').first()  # Get the last invoice
            if last_invoice:
                last_id = int(last_invoice.number[3:])  # Extract the numeric part of the last invoice number
                new_id = last_id + 1  # Increment the numeric part
            else:
                new_id = 1  # If no invoices exist yet, start from 1
            self.number = f'INV{new_id:03}'  # Format the new invoice number
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Invoice {self.number} for {self.client} - {self.status}"

class Payment(models.Model):
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, blank=True, null=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 
    objects = models.Manager()
    def __str__(self):
        return f"Payment of {self.amount} made on {self.date}"



class Clients(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=200, blank=True)
    contact_person = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 
    objects = models.Manager()
    # Add more fields for client details as needed

    def __str__(self):
        return self.name
    
    