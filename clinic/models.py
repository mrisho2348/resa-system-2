# Standard library imports
from decimal import Decimal
from uuid import uuid4
import re
from django.contrib.auth import get_user_model
# Django core imports
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

# Third-party imports
from django_ckeditor_5.fields import CKEditor5Field

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
        ('1', "AdminHOD"),
        ('2', "Staffs"),
    )
    user_type = models.CharField(max_length=2, default='1', choices=user_type_data)
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
        ('pemba', 'Pemba'),
        # Add more choices as needed
    ]

GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
      
    ]


class Staffs(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='staff')   
    middle_name = models.TextField(blank=True)    
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True)
    from datetime import date
    date_of_birth = models.DateField(blank=True, default=date(2000, 1, 1))
    phone_number = models.CharField(max_length=14, blank=True)
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES, blank=True)   
    profession = models.CharField(max_length=20, choices=PROFESSION_CHOICES, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True)    
    work_place = models.CharField(max_length=50, choices=work_place_choices, blank=True)
    joining_date = models.DateField(blank=True, null=True)  # Joining date field
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)  # Profile picture field
    
    # ✅ New fields added below
    mct_number = models.CharField(max_length=50, blank=True, null=True, help_text="Medical Council of Tanzania (MCT) Number")
    signature = models.ImageField(upload_to='signatures/', blank=True, null=True, help_text="Upload digital signature")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)    

    objects = models.Manager()
    def clean(self):
        """Ensure unique staff full name (first_name + middle_name + last_name)."""
        if Staffs.objects.filter(
            admin__first_name=self.admin.first_name,
            middle_name=self.middle_name,
            admin__last_name=self.admin.last_name
        ).exclude(id=self.id).exists():
            raise ValidationError("A staff member with this full name already exists.")
    def get_full_name(self):
        return f"{self.admin.first_name} {self.middle_name} {self.admin.last_name}"

    def __str__(self):
        return f"{self.admin.first_name} {self.middle_name} {self.admin.last_name}"


   
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
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True,related_name='services') 
    name = models.CharField(max_length=255)
    type_service = models.CharField(max_length=200, choices=TYPE_CHOICES, blank=True, null=True)  
    coverage = models.CharField(max_length=200, choices=COVERAGE_CHOICES, blank=True, null=True)         
    description = models.TextField(blank=True, null=True)
    cash_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    insurance_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    nhif_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # New field for cost
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        return self.name
    

class MedicineUnitMeasure(models.Model):
    """
    Defines the units of measure used in formulations (e.g., mg, ml, tablet).
    """
    data_recorder = models.ForeignKey(
        Staffs, on_delete=models.CASCADE, blank=True, null=True,
        related_name='medicine_unit_measures'
    ) 
    name = models.CharField(max_length=100, help_text="Full name of the unit (e.g., Milligram, Milliliter)")
    short_name = models.CharField(max_length=20, default="", help_text="Short code (e.g., mg, ml, tab)")    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    
    def __str__(self):
        return self.short_name or self.name
     

 
        
class PathodologyRecord(models.Model):
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True,related_name='pathology_records') 
    name = models.CharField(max_length=255, unique=True)    
    description = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    def __str__(self):
        return self.name
    
    
class DiseaseRecode(models.Model):
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True,related_name='disease_records') 
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
    data_recorder = models.ForeignKey(
        'Staffs', on_delete=models.CASCADE, blank=True, null=True, related_name='patients'
    )
    mrn = models.CharField(max_length=20, unique=True, editable=False)

    first_name = models.CharField(max_length=100, default="")
    middle_name = models.CharField(max_length=100, default="", blank=True)
    last_name = models.CharField(max_length=100, default="")

    gender = models.CharField(
        max_length=10,
        choices=[('Male', 'Male'), ('Female', 'Female')],
    )
    age = models.IntegerField(blank=True, null=True)
    dob = models.DateField(null=True, blank=True)

    phone = models.CharField(max_length=15)
    address = models.TextField()

    nationality = models.ForeignKey('Country', on_delete=models.CASCADE)

    PAYMENT_CHOICES = [
        ('Cash', 'Cash'),
        ('Insurance', 'Insurance'),
    ]
    payment_form = models.CharField(max_length=255, choices=PAYMENT_CHOICES)
    insurance_name = models.CharField(max_length=255, blank=True, null=True)
    insurance_number = models.CharField(max_length=255, blank=True, null=True)

    # Optional emergency contact fields
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_relation = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)

    # NIDA number: optional but must be 20 digits and unique if provided
    nida_number = models.CharField(max_length=20, blank=True, null=True, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.mrn:
            self.mrn = generate_mrn()
        self.full_clean()  # ensure validation is triggered
        super().save(*args, **kwargs)

    def clean(self):
        # Validate NIDA number format if provided
        if self.nida_number:
            if not re.fullmatch(r'\d{20}', self.nida_number):
                raise ValidationError({'nida_number': "NIDA number must be exactly 20 digits."})
    def __str__(self):
        # Gracefully handle missing name fields
        name_parts = [self.first_name or '', self.middle_name or '', self.last_name or '']
        name = ' '.join(part for part in name_parts if part).strip()
        return name if name else f"Patient {self.pk}"
        return self.full_name

    @property
    def full_name(self):
        name_parts = [self.first_name]
        if self.middle_name:
            name_parts.append(self.middle_name)
        name_parts.append(self.last_name)
        return ' '.join(name_parts)


def generate_mrn():
    """
    Generate a unique MRN in the format RES-0000001.
    """
    last_patient = Patients.objects.order_by('-id').first()
    if last_patient and last_patient.mrn.startswith("RES-"):
        try:
            last_number = int(last_patient.mrn.split('-')[-1])
        except ValueError:
            last_number = 0
    else:
        last_number = 0

    new_number = last_number + 1
    return f"RES-{new_number:07d}"


 
class Country(models.Model):
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True,related_name='countries') 
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
    respiratory_rate = models.PositiveIntegerField(null=True, blank=True, help_text="Respiratory rate in breaths per minute")
    pulse_rate = models.PositiveIntegerField(null=True, blank=True, help_text="Pulse rate in beats per minute")
    blood_pressure = models.CharField(max_length=20, null=True, blank=True, help_text="Blood pressure measurement")
    sbp = models.PositiveIntegerField(null=True, blank=True, help_text="Systolic Blood Pressure (mmHg)")
    dbp = models.PositiveIntegerField(null=True, blank=True, help_text="Diastolic Blood Pressure (mmHg)")
    spo2 = models.PositiveIntegerField(null=True, blank=True, help_text="SPO2 measurement in percentage")
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
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True,related_name='patient_visits') 
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
    visit = models.ForeignKey(PatientVisits, on_delete=models.CASCADE, null=True, blank=True)  

    history_of_presenting_illness = models.TextField(null=True, blank=True)
    review_of_systems = models.TextField(null=True, blank=True)  # ✅ Added
    physical_examination = models.TextField(null=True, blank=True)  # ✅ Added
    doctor_plan = models.TextField()
    doctor_plan_note = models.TextField(null=True, blank=True)  # ✅ Added

    allergy_summary = models.TextField(null=True, blank=True)  # ✅ Added
    known_comorbidities_summary = models.TextField(null=True, blank=True)  # ✅ Added

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    def __str__(self):
        return f"Consultation for {self.patient} by Dr. {self.doctor}"
   
    

   
class ImagingRecord(models.Model):
    patient = models.ForeignKey('Patients', on_delete=models.CASCADE)
    visit = models.ForeignKey('PatientVisits', on_delete=models.CASCADE)
    doctor = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True) 
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True,related_name='imaging_records') 
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
    """
    Represents a laboratory test order for a patient during a visit.
    """
    patient = models.ForeignKey(
        Patients, on_delete=models.CASCADE,
        help_text="The patient for whom the laboratory order is created."
    )
    visit = models.ForeignKey(
        PatientVisits, on_delete=models.CASCADE, blank=True, null=True,
        help_text="The visit associated with this laboratory order."
    )
    doctor = models.ForeignKey(
        Staffs, on_delete=models.CASCADE, blank=True, null=True,
        help_text="The doctor who ordered the laboratory test."
    )
    data_recorder = models.ForeignKey(
        Staffs, on_delete=models.CASCADE, blank=True, null=True, related_name='lab_data_recorder',
        help_text="The staff member who recorded this laboratory order."
    )
    lab_test = models.ForeignKey(
        Service, on_delete=models.CASCADE, blank=True, null=True,
        help_text="The laboratory test being ordered."
    )
    description = models.TextField(
        blank=True, null=True,
        help_text="Additional notes or description for the laboratory order."
    )
    order_date = models.DateField(
        null=True, blank=True,
        help_text="The date the laboratory order was placed."
    )
    result = CKEditor5Field(
        config_name='extends', blank=True, null=True,
        help_text="The result of the laboratory test."
    )
    lab_number = models.CharField(
        max_length=20, unique=True,
        help_text="A unique identifier for this laboratory order."
    )
    cost = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="The cost of the laboratory test."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the laboratory order was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the laboratory order was last updated."
    )
    objects = models.Manager()

    class Meta:
        verbose_name = "Laboratory Order"
        verbose_name_plural = "Laboratory Orders"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"LaboratoryOrder: {self.lab_test} for {self.patient}"  # lab_test is the test name

    def clean(self) -> None:
        """
        Validate business logic for LaboratoryOrder.
        """
        if self.cost is not None and self.cost < 0:
            raise ValidationError({"cost": "Cost cannot be negative."})

    def save(self, *args, **kwargs) -> None:
        """
        Override save to auto-generate a unique lab_number if not set.
        Format: LAB-0000001
        """
        if not self.lab_number:
            last_lab_order = LaboratoryOrder.objects.order_by('-id').first()
            if last_lab_order and last_lab_order.lab_number.startswith('LAB-'):
                try:
                    last_number = int(last_lab_order.lab_number.split('-')[-1])
                except ValueError:
                    last_number = 0
            else:
                last_number = 0
            new_number = last_number + 1
            self.lab_number = f"LAB-{new_number:07d}"
        self.full_clean()  # Ensure validation is triggered
        super().save(*args, **kwargs)

class HospitalVehicle(models.Model):
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True,related_name='hospital_vehicles') 
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
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True,related_name='ambulance_routes') 
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
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True,related_name='ambulance_activities') 
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
    """
    Represents an ambulance service order for patient transportation.
    """
    patient = models.ForeignKey(
        Patients, on_delete=models.CASCADE,
        help_text="The patient requiring ambulance service."
    )
    visit = models.ForeignKey(
        PatientVisits, on_delete=models.CASCADE, blank=True, null=True,
        help_text="The visit associated with this ambulance order."
    )
    data_recorder = models.ForeignKey(
        Staffs, on_delete=models.CASCADE, blank=True, null=True, related_name='ambulance_data_recorder',
        help_text="The staff member who recorded this ambulance order."
    )
    
    # Service details
    service = models.CharField(max_length=100, help_text="Type of ambulance service required.")
    from_location = models.CharField(max_length=100, help_text="Pickup location for the ambulance.")
    to_location = models.CharField(max_length=100, help_text="Destination location for the ambulance.")
    order_date = models.DateField(null=True, blank=True, help_text="The date the ambulance order was placed.")
    
    # Patient condition details
    age = models.CharField(max_length=50, help_text="Patient's age at time of ambulance request.")
    condition = models.CharField(max_length=100, help_text="Patient's medical condition requiring ambulance.")
    intubation = models.CharField(max_length=100, help_text="Intubation status of the patient.")
    pregnancy = models.CharField(max_length=100, help_text="Pregnancy status if applicable.")
    oxygen = models.CharField(max_length=100, help_text="Oxygen requirement status.")
    
    # Ambulance specifications
    ambulance_type = models.CharField(max_length=100, help_text="Type of ambulance required (basic, advanced, etc.).")
    duration_hours = models.IntegerField(help_text="Duration of ambulance service in hours.")
    duration_days = models.IntegerField(help_text="Duration of ambulance service in days.")
    
    # Financial details
    cost = models.DecimalField(max_digits=10, decimal_places=2, help_text="Cost of the ambulance service.")
    payment_mode = models.CharField(max_length=100, help_text="Method of payment for the ambulance service.")
    
    # Unique identifier
    ambulance_number = models.CharField(max_length=20, unique=True, help_text="Unique identifier for this ambulance order.")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the ambulance order was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp when the ambulance order was last updated.")
    
    objects = models.Manager()

    class Meta:
        verbose_name = "Ambulance Order"
        verbose_name_plural = "Ambulance Orders"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Ambulance Order for {self.patient} - Service: {self.service}"

    def clean(self) -> None:
        """
        Validate business logic for AmbulanceOrder.
        """
        # Ensure cost is non-negative
        if self.cost is not None and self.cost < 0:
            raise ValidationError({"cost": "Cost cannot be negative."})

        # Safely cast duration values to int (they might come in as str from forms)
        try:
            hours = int(self.duration_hours)
            days = int(self.duration_days)
        except (ValueError, TypeError):
            raise ValidationError("Duration hours and days must be integers.")

        if hours < 0 or days < 0:
            raise ValidationError("Duration cannot be negative.")

    def save(self, *args, **kwargs) -> None:
        """
        Override save to auto-generate a unique ambulance_number if not set.
        Format: AMB-0000001
        """
        if not self.ambulance_number:
            last_ambulance = AmbulanceOrder.objects.order_by('-id').first()
            if last_ambulance and last_ambulance.ambulance_number.startswith('AMB-'):
                try:
                    last_number = int(last_ambulance.ambulance_number.split('-')[-1])
                except ValueError:
                    last_number = 0
            else:
                last_number = 0
            new_number = last_number + 1
            self.ambulance_number = f"AMB-{new_number:07d}"

        self.full_clean()  # Triggers validation
        super().save(*args, **kwargs)
        
class AmbulanceVehicleOrder(models.Model):
    """
    Represents an ambulance vehicle order for external organizations or events.
    """
    data_recorder = models.ForeignKey(
        Staffs, on_delete=models.CASCADE, blank=True, null=True, related_name='ambulance_vehicle_orders',
        help_text="The staff member who recorded this vehicle order."
    )
    
    # Vehicle and service details
    vehicle_type = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="Type of ambulance vehicle required."
    )
    activities = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="Activities or events the ambulance will be used for."
    )
    ambulance_number = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="Assigned ambulance vehicle number."
    )
    
    # Organization details
    organization = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="Name of the organization requesting the ambulance."
    )
    contact_person = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="Contact person at the requesting organization."
    )
    contact_phone = models.CharField(
        max_length=20, blank=True, null=True,
        help_text="Contact phone number for the organization."
    )
    location = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="Location where the ambulance service is needed."
    )
    
    # Service duration
    duration = models.IntegerField(
        help_text="Duration of service in hours."
    )
    days = models.IntegerField(
        help_text="Duration of service in days."
    )
    
    # Financial details
    cost = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Cost of the ambulance vehicle service."
    )
    payment_mode = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="Method of payment for the service."
    )
    order_date = models.DateField(
        null=True, blank=True,
        help_text="The date the vehicle order was placed."
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the vehicle order was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the vehicle order was last updated."
    )
    
    objects = models.Manager()

    class Meta:
        verbose_name = "Ambulance Vehicle Order"
        verbose_name_plural = "Ambulance Vehicle Orders"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.vehicle_type} - {self.organization}"

    def clean(self) -> None:
        """
        Validate business logic for AmbulanceVehicleOrder.
        """
        if self.cost is not None and self.cost < 0:
            raise ValidationError({"cost": "Cost cannot be negative."})
        
        if self.duration < 0 or self.days < 0:
            raise ValidationError("Duration cannot be negative.")

class PrescriptionFrequency(models.Model):
    """
    Represents the frequency and interval for medication prescriptions.
    """
    data_recorder = models.ForeignKey(
        Staffs, on_delete=models.CASCADE, blank=True, null=True, related_name='prescription_frequencies',
        help_text="The staff member who recorded this prescription frequency."
    )
    name = models.CharField(
        max_length=100,
        help_text="Name of the prescription frequency (e.g., 'Twice daily')."
    )
    interval = models.CharField(
        max_length=50,
        help_text="Time interval between doses (e.g., '12 hours')."
    )
    description = models.TextField(
        help_text="Detailed description of the prescription frequency."
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the prescription frequency was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the prescription frequency was last updated."
    )
    
    objects = models.Manager()

    class Meta:
        verbose_name = "Prescription Frequency"
        verbose_name_plural = "Prescription Frequencies"
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name}-{self.interval}"

    def clean(self) -> None:
        """
        Validate business logic for PrescriptionFrequency.
        """
        if not self.name.strip():
            raise ValidationError({"name": "Name cannot be empty."})
        
        if not self.interval.strip():
            raise ValidationError({"interval": "Interval cannot be empty."})

class Order(models.Model):
    """
    Represents a general order for various services in the clinic.
    """
    ORDER_STATUS = [
        ('Paid', 'Paid'),
        ('Unpaid', 'Unpaid'),
    ]

    ORDER_NUMBER_PREFIX = 'ORD'  # Prefix for the order number

    # Order details
    order_date = models.DateField(
        default=timezone.now, null=True, blank=True,
        help_text="The date when the order was placed."
    )
    order_type = models.TextField(
        blank=True, null=True,
        help_text="Type of service or item being ordered."
    )
    type_of_order = models.TextField(
        blank=True, null=True,
        help_text="Category of the order (e.g., Laboratory, Consultation, etc.)."
    )
    
    # Relationships
    patient = models.ForeignKey(
        'Patients', on_delete=models.CASCADE,
        help_text="The patient for whom the order is placed."
    )
    visit = models.ForeignKey(
        PatientVisits, on_delete=models.CASCADE, blank=True, null=True,
        help_text="The visit associated with this order."
    )
    added_by = models.ForeignKey(
        Staffs, on_delete=models.CASCADE, blank=True, null=True,
        help_text="The staff member who created this order."
    )
    doctor = models.ForeignKey(
        Staffs, on_delete=models.CASCADE, blank=True, null=True, related_name='doctor',
        help_text="The doctor who ordered this service."
    )
    
    # Financial details
    cost = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="The cost of the order."
    )
    status = models.CharField(
        max_length=100, choices=ORDER_STATUS, default='Unpaid',
        help_text="Payment status of the order."
    )
    
    # Order tracking
    order_number = models.CharField(
        max_length=12, unique=True,
        help_text="Unique identifier for this order."
    )
    is_read = models.BooleanField(
        default=False,
        help_text="Whether the order has been read/processed."
    )

        # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the prescription frequency was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the prescription frequency was last updated."
    )
    
    objects = models.Manager()
    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ["-order_date"]

    def __str__(self) -> str:
        return f"{self.order_type} Order for {self.patient}"

    def clean(self) -> None:
        """
        Validate business logic for Order.
        """
        if self.cost is not None and self.cost < 0:
            raise ValidationError({"cost": "Cost cannot be negative."})

    def save(self, *args, **kwargs) -> None:
        """
        Override save to auto-generate a unique order_number if not set.
        Format: ORD-0000001
        """
        if not self.order_number:
            last_order = Order.objects.order_by('-id').first()
            if last_order:
                last_number = int(last_order.order_number.split('-')[-1])
            else:
                last_number = 0
            new_number = last_number + 1
            self.order_number = f"{self.ORDER_NUMBER_PREFIX}-{new_number:07}"
        self.full_clean()  # Ensure validation is triggered
        super().save(*args, **kwargs)

class Consultation(models.Model):
    """
    Represents a medical consultation appointment between a doctor and patient.
    """
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
    
    # Relationships
    doctor = models.ForeignKey(
        Staffs, on_delete=models.CASCADE, related_name='doctor_consultations',
        help_text="The doctor conducting the consultation."
    )
    created_by = models.ForeignKey(
        Staffs, on_delete=models.CASCADE, blank=True, null=True, related_name='created_consultations',
        help_text="The staff member who created this appointment."
    )
    patient = models.ForeignKey(
        Patients, on_delete=models.CASCADE,
        help_text="The patient attending the consultation."
    )
    visit = models.ForeignKey(
        PatientVisits, on_delete=models.CASCADE, blank=True, null=True,
        help_text="The visit associated with this consultation."
    )
    
    # Appointment details
    appointment_date = models.DateField(
        help_text="The scheduled date for the consultation."
    )
    start_time = models.TimeField(
        blank=True, null=True,
        help_text="The scheduled start time for the consultation."
    )
    end_time = models.TimeField(
        blank=True, null=True,
        help_text="The scheduled end time for the consultation."
    )
    description = models.TextField(
        blank=True, null=True,
        help_text="Additional notes or description for the consultation."
    )
    
    # Status and tracking
    status = models.IntegerField(
        choices=STATUS_CHOICES, default=0,
        help_text="Current status of the consultation appointment."
    )
    appointment_number = models.CharField(
        max_length=20, unique=True,
        help_text="Unique identifier for this appointment."
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the appointment was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the appointment was last updated."
    )
    
    objects = models.Manager()

    class Meta:
        verbose_name = "Consultation"
        verbose_name_plural = "Consultations"
        ordering = ["-appointment_date", "-created_at"]

    def __str__(self) -> str:
        return f"Appointment with {self.doctor.admin.first_name} {self.doctor.middle_name} {self.doctor.admin.last_name} for {self.patient.full_name} on {self.appointment_date} from {self.start_time} to {self.end_time}"

    def clean(self) -> None:
        """
        Validate business logic for Consultation.
        """
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError("Start time must be before end time.")
        
        if self.appointment_date < timezone.now().date():
            raise ValidationError("Appointment date cannot be in the past.")

    def save(self, *args, **kwargs) -> None:
        """
        Override save to auto-generate a unique appointment_number if not set.
        Format: APT-0000001
        """
        if not self.appointment_number:
            last_appointment = Consultation.objects.order_by('-id').first()
            if last_appointment:
                last_number = int(last_appointment.appointment_number.split('-')[-1])
            else:
                last_number = 0
            new_number = last_number + 1
            self.appointment_number = f"APT-{new_number:07}"
        self.full_clean()  # Ensure validation is triggered
        super().save(*args, **kwargs)


class Counseling(models.Model):
    """
    Represents counseling sessions and notes for patients.
    """
    data_recorder = models.ForeignKey(
        Staffs, on_delete=models.CASCADE, blank=True, null=True,
        help_text="The staff member who recorded this counseling session."
    )
    
    # Patient and visit information
    patient = models.ForeignKey(
        Patients, on_delete=models.CASCADE,
        help_text="The patient receiving counseling."
    )
    visit = models.ForeignKey(
        PatientVisits, on_delete=models.CASCADE, blank=True, null=True,
        help_text="The visit associated with this counseling session."
    )
    
    # Counseling details
    counselling_notes = CKEditor5Field(
        config_name='extends', blank=True, null=True,
        help_text="Detailed notes from the counseling session."
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the counseling session was recorded."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the counseling record was last updated."
    )
    
    objects = models.Manager()

    class Meta:
        verbose_name = "Counseling"
        verbose_name_plural = "Counseling Sessions"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Counseling for {self.patient}"

    def clean(self) -> None:
        """
        Validate business logic for Counseling.
        """
        if not self.counselling_notes and not self.visit:
            raise ValidationError("Either counseling notes or visit must be provided.")



class MedicineType(models.Model):
    """
    Represents a type of medicine (e.g., Tablet, Syrup, Injection) with metadata.
    """
    name = models.CharField(
        max_length=50, 
        unique=True, 
        help_text="Name of the medicine type."
    )
    data_recorder = models.ForeignKey(
        "Staffs",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="medicine_types",
        help_text="The staff member who recorded this medicine type."
    )
    explanation = models.TextField(
        blank=True,
        null=True,
        help_text="Optional explanation or notes about this medicine type."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Medicine Type"
        verbose_name_plural = "Medicine Types"
        ordering = ["name"]

    def __str__(self):
        return self.name



class MedicineRoute(models.Model):
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True,related_name='medicine_routes') 
    name = models.CharField(max_length=100)
    explanation = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    
    def __str__(self):
        return self.name  

class Medicine(models.Model):
    """
    Represents a medicine or drug in the clinic's inventory.
    """
    data_recorder = models.ForeignKey(
        "Staffs",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="medicines",
        help_text="The staff member who recorded this medicine."
    )

    # Medicine details
    drug_name = models.CharField(max_length=100, help_text="Name of the medicine or drug.")
    drug_type = models.ForeignKey(
        MedicineType,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="medicines",
        help_text="Type of drug (linked to MedicineType)."
    )
    formulation_value = models.DecimalField(max_digits=10, decimal_places=2, help_text="Numerical part of the formulation (e.g., 500, 5).")
    formulation_unit = models.ForeignKey(
        MedicineUnitMeasure,
        on_delete=models.PROTECT,
        related_name="medicines",
        help_text="Measurement unit (e.g., mg, ml, tablet)."
    )
    is_dividable = models.BooleanField(default=False, help_text="Is this drug divisible in smaller units?")
    manufacturer = models.CharField(max_length=100, help_text="Manufacturer of the medicine.")

    # Link to route of administration
    route = models.ForeignKey(
        MedicineRoute,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="medicines",
        help_text="Route of administration for this medicine."
    )

    # Inventory details
    remain_quantity = models.PositiveIntegerField(blank=True, null=True, help_text="Remaining quantity in stock.")
    quantity = models.PositiveIntegerField(blank=True, null=True, help_text="Total quantity received.")
    batch_number = models.CharField(max_length=20, unique=True, default="12345", help_text="Batch number for tracking.")
    expiration_date = models.DateField(help_text="Expiration date of the medicine.")

    # Cost details
    cash_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Cost for cash-paying patients.")
    insurance_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Cost for insurance-paying patients.")
    nhif_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Cost for NHIF-paying patients.")
    buying_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Purchase price of the medicine.")
    total_buying_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Total purchase price (buying_price * quantity).")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    class Meta:
        verbose_name = "Medicine"
        verbose_name_plural = "Medicines"
        ordering = ["drug_name"]

    def __str__(self) -> str:
        formulation = f"{self.formulation_value}{self.formulation_unit.short_name}" if self.formulation_unit else ""
        return f"{self.drug_name} - {formulation}"

    def clean(self) -> None:
        if self.expiration_date and self.expiration_date < timezone.now().date():
            raise ValidationError({"expiration_date": "Expiration date cannot be in the past."})
        if self.remain_quantity is not None and self.quantity is not None:
            if self.remain_quantity > self.quantity:
                raise ValidationError("Remaining quantity cannot exceed total quantity.")

    def save(self, *args, **kwargs) -> None:
        if self.buying_price is not None and self.quantity is not None:
            self.total_buying_price = float(self.buying_price) * self.quantity
        self.full_clean()
        super().save(*args, **kwargs)
        

class MedicineBatch(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='batches')
    batch_number = models.CharField(max_length=50)
    expiration_date = models.DateField()
    quantity = models.PositiveIntegerField(default=0)
    remain_quantity = models.PositiveIntegerField(default=0)
    buying_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('medicine', 'batch_number')


class MedicineDosage(models.Model):
    """
    Represents available dosage options for a medicine.
    """
    medicine = models.ForeignKey(
        Medicine, 
        on_delete=models.CASCADE, 
        related_name='dosages',
        help_text="The medicine this dosage option belongs to."
    )
    dosage_value = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Dosage value (e.g., 125, 250, 500)"
    )
    unit = models.ForeignKey(
            MedicineUnitMeasure,
            on_delete=models.PROTECT,
            related_name="dosages",
            help_text="Unit of measurement (e.g., mg, ml, tab)."
        )
    is_default = models.BooleanField(
        default=False,
        help_text="Is this the default dosage for this medicine?"
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the medicine was added to inventory."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the medicine was last updated."
    )
    
    class Meta:
        unique_together = ['medicine', 'dosage_value', 'unit']
        ordering = ['dosage_value']
    
    def __str__(self):
        return f"{self.dosage_value} {self.unit}"    


class Prescription(models.Model):
    """
    Represents a prescription for medication given to a patient.
    """

    # ----------------- Choice Definitions -----------------
    VERIFICATION_CHOICES = [
        ("verified", "Verified"),
        ("not_verified", "Not Verified"),
    ]

    ISSUE_CHOICES = [
        ("issued", "Issued"),
        ("not_issued", "Not Issued"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("paid", "Paid"),
        ("unpaid", "Unpaid"),
    ]

    # ----------------- Relationships -----------------
    patient = models.ForeignKey(
        "Patients",
        on_delete=models.CASCADE,
        help_text="The patient for whom the prescription is written."
    )
    entered_by = models.ForeignKey(
        "Staffs",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        help_text="The staff member who entered this prescription."
    )
    visit = models.ForeignKey(
        "PatientVisits",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        help_text="The visit associated with this prescription."
    )
    medicine = models.ForeignKey(
        "Medicine",
        on_delete=models.CASCADE,
        help_text="The medicine being prescribed."
    )
    frequency = models.ForeignKey(
        "PrescriptionFrequency",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        help_text="The frequency of medication administration."
    )

    # ----------------- Prescription Details -----------------
    formulation_dose = models.CharField(
        max_length=50,
        help_text="Dosage instructions for the medication (e.g., 500mg tablet)."
    )
    duration = models.CharField(
        max_length=50,
        help_text="Duration of the prescription treatment (e.g., 7 days)."
    )
    quantity_used = models.PositiveIntegerField(
        help_text="Quantity of medicine prescribed."
    )
    route = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Route of administration (e.g., Oral, IV)."
    )
    dosage = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Human-readable dosage instructions (e.g., 1 tablet twice daily)."
    )

    # ----------------- Financial Details -----------------
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total cost of the prescription."
    )

    # ----------------- Status Fields -----------------
    verified = models.CharField(
        max_length=20,
        choices=VERIFICATION_CHOICES,
        default="not_verified",
        help_text="Whether the prescription has been verified by a pharmacist."
    )
    issued = models.CharField(
        max_length=20,
        choices=ISSUE_CHOICES,
        default="not_issued",
        help_text="Whether the medication has been issued to the patient."
    )
    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="unpaid",
        help_text="Payment status of the prescription."
    )

    # ----------------- Timestamps -----------------
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the prescription was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the prescription was last updated."
    )

    # ----------------- Helper Methods -----------------
    @classmethod
    def get_visit_status(cls, visit):
        """
        Return overall status for a given visit.
        Rules:
        - verified: if ALL prescriptions are verified
        - issued: if ALL prescriptions are issued
        - paid: if ALL prescriptions are paid
        - otherwise return mixed states
        """
        prescriptions = cls.objects.filter(visit=visit)

        if not prescriptions.exists():
            return {
                "verified": "no_prescriptions",
                "issued": "no_prescriptions",
                "status": "no_prescriptions",
            }

        # Verification check
        if all(p.verified == "verified" for p in prescriptions):
            verified_status = "verified"
        elif all(p.verified == "not_verified" for p in prescriptions):
            verified_status = "not_verified"
        else:
            verified_status = "partially_verified"

        # Issue check
        if all(p.issued == "issued" for p in prescriptions):
            issue_status = "issued"
        elif all(p.issued == "not_issued" for p in prescriptions):
            issue_status = "not_issued"
        else:
            issue_status = "partially_issued"

        # Payment check
        if all(p.status == "paid" for p in prescriptions):
            payment_status = "paid"
        elif all(p.status == "unpaid" for p in prescriptions):
            payment_status = "unpaid"
        else:
            payment_status = "partially_paid"

        return {
            "verified": verified_status,
            "issued": issue_status,
            "status": payment_status,
        }

    def clean(self):
        """Validate business rules for Prescription."""
        if self.quantity_used <= 0:
            raise ValidationError({"quantity_used": "Quantity must be greater than zero."})

        if self.total_price is not None and self.total_price < 0:
            raise ValidationError({"total_price": "Total price cannot be negative."})

    # ----------------- Meta & String -----------------
    class Meta:
        verbose_name = "Prescription"
        verbose_name_plural = "Prescriptions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.patient.first_name} - {self.medicine.drug_name}"
            

class WalkInCustomer(models.Model):
    PAYMENT_FORM_CHOICES = (
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('mobile_money', 'Mobile Money'),
        ('insurance', 'Insurance'),
        ('other', 'Other'),
    )

    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )

    # Auto-generated pharmacy number
    pharmacy_number = models.CharField(
        max_length=20,
        unique=True,
        editable=False,  # user cannot edit it manually
        help_text="Unique pharmacy/customer number for tracking."
    )
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True,
        null=True,
        help_text="Customer gender"
    )

    age = models.PositiveIntegerField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    # Payment preference
    payment_form = models.CharField(
        max_length=20,
        choices=PAYMENT_FORM_CHOICES,
        default='cash',
        help_text="Preferred payment method for the customer."
    )

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pharmacy_number:
            # Example format: PH-00001, PH-00002...
            last_customer = WalkInCustomer.objects.all().order_by("id").last()
            if last_customer and last_customer.pharmacy_number.startswith("PH-"):
                last_number = int(last_customer.pharmacy_number.split("-")[1])
                new_number = last_number + 1
            else:
                new_number = 1
            self.pharmacy_number = f"PH-{new_number:05d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.middle_name or ''} {self.last_name or ''}".strip()


class WalkInVisit(models.Model):
    """Represents a pharmacy walk-in visit for a customer."""

    # Relationships
    customer = models.ForeignKey(
        "WalkInCustomer",
        on_delete=models.CASCADE,
        related_name="visits",
        help_text="The customer associated with this walk-in visit.",
    )

    # Core fields
    visit_number = models.CharField(
        max_length=12,
        unique=True,
        editable=False,
        help_text="Unique visit number (auto-generated, e.g. VST-0000001).",
    )
    visit_date = models.DateTimeField(
        auto_now_add=True,
        help_text="The date and time when the visit was created.",
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Optional notes related to the visit.",
    )

    # Receipt fields
    receipt_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        help_text="Unique receipt number generated when payment is processed.",
    )
    receipt_generated_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Timestamp when the receipt number was generated.",
    )

    # Prescription Notes ID (auto-generated)
    prescription_notes_id = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        help_text="Auto-generated unique prescription notes ID for this visit.",
    )
    prescription_notes_generated_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Timestamp when the prescription notes ID was generated.",
    )

    # ----------------------
    # Methods
    # ----------------------
    def save(self, *args, **kwargs):
        """Override save to auto-generate a visit number if missing."""
        if not self.visit_number:
            self.visit_number = self.generate_visit_number()
        super().save(*args, **kwargs)

    def generate_receipt_number(self):
        """Generate a unique receipt number for this visit."""
        if not self.receipt_number:
            timestamp = timezone.now().strftime("%H%M%S")
            self.receipt_number = f"REC-{self.id}-{timestamp}"
            self.receipt_generated_at = timezone.now()
            self.save(update_fields=["receipt_number", "receipt_generated_at"])
        return self.receipt_number

    def generate_prescription_notes_id(self):
        """Generate a unique prescription notes ID for this visit."""
        if not self.prescription_notes_id:
            timestamp = timezone.now().strftime("%H%M%S")
            self.prescription_notes_id = f"PN-{self.id}-{timestamp}"
            self.prescription_notes_generated_at = timezone.now()
            self.save(update_fields=["prescription_notes_id", "prescription_notes_generated_at"])
        return self.prescription_notes_id

    @staticmethod
    def generate_visit_number():
        """Generates the next visit number in the format 'VST-0000001'."""
        last_visit = WalkInVisit.objects.order_by("-id").first()
        if last_visit and last_visit.visit_number:
            last_number = int(last_visit.visit_number.split("-")[-1])
        else:
            last_number = 0
        new_number = last_number + 1
        return f"VST-{new_number:07d}"

    def __str__(self):
        return f"{self.customer.first_name} - {self.visit_number} ({self.visit_date.date()})"



class WalkInPrescription(models.Model):
    VERIFICATION_CHOICES = (
        ('verified', 'Verified'),
        ('not_verified', 'Not Verified'),
    )

    ISSUE_CHOICES = (
        ('issued', 'Issued'),
        ('not_issued', 'Not Issued'),
    )

    STATUS_CHOICES = (
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
    )

    # Relationships
    visit = models.ForeignKey("WalkInVisit", on_delete=models.CASCADE, related_name="prescriptions")
    entered_by = models.ForeignKey("Staffs", on_delete=models.CASCADE, blank=True, null=True)
    medicine = models.ForeignKey("Medicine", on_delete=models.CASCADE)
    frequency = models.ForeignKey("PrescriptionFrequency", on_delete=models.CASCADE, blank=True, null=True)

    # Route as free text
    route = models.CharField(max_length=100, blank=True, null=True, help_text="Route of administration")

    # Prescription details
    formulation_dose = models.CharField(max_length=255, blank=True, null=True, help_text="Human-readable dosage instructions")
    dosage = models.CharField(max_length=255, blank=True, null=True, help_text="Human-readable dosage instructions")

    duration = models.PositiveIntegerField(help_text="Duration of treatment in days")
    quantity_used = models.PositiveIntegerField()

    # Financial details
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Status fields
    verified = models.CharField(max_length=20, choices=VERIFICATION_CHOICES, default='not_verified')
    issued = models.CharField(max_length=20, choices=ISSUE_CHOICES, default='not_issued')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unpaid')

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Walk-In Prescription"
        verbose_name_plural = "Walk-In Prescriptions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.medicine.drug_name} - Visit {self.visit.id} ({self.visit.customer.first_name})"

    def clean(self):
        """Validate numeric fields safely."""
        if self.quantity_used <= 0:
            raise ValidationError({"quantity_used": "Quantity must be greater than zero."})
        if self.total_price is not None and self.total_price < 0:
            raise ValidationError({"total_price": "Total price cannot be negative."})

    def save(self, *args, **kwargs):
        # Combine formulation_value and unit into formulation_dose
        if self.medicine.formulation_value and getattr(self.medicine, 'formulation_unit', None):
            self.formulation_dose = f"{self.medicine.formulation_value} {self.medicine.formulation_unit}"
        super().save(*args, **kwargs)

    # ----------------- Helper Function -----------------
    @classmethod
    def get_visit_status(cls, visit):
        """
        Return overall status for a given visit.
        Rules:
        - Verified: if ALL prescriptions are verified
        - Issued: if ALL prescriptions are issued
        - Paid: if ALL prescriptions are paid
        - Otherwise return mixed states
        """
        prescriptions = cls.objects.filter(visit=visit)

        if not prescriptions.exists():
            return {
                "verified": "no_prescriptions",
                "issued": "no_prescriptions",
                "status": "no_prescriptions"
            }

        # Check verification
        if all(p.verified == "verified" for p in prescriptions):
            verified_status = "verified"
        elif all(p.verified == "not_verified" for p in prescriptions):
            verified_status = "not_verified"
        else:
            verified_status = "partially_verified"

        # Check issue
        if all(p.issued == "issued" for p in prescriptions):
            issue_status = "issued"
        elif all(p.issued == "not_issued" for p in prescriptions):
            issue_status = "not_issued"
        else:
            issue_status = "partially_issued"

        # Check payment
        if all(p.status == "paid" for p in prescriptions):
            payment_status = "paid"
        elif all(p.status == "unpaid" for p in prescriptions):
            payment_status = "unpaid"
        else:
            payment_status = "partially_paid"

        return {
            "verified": verified_status,
            "issued": issue_status,
            "status": payment_status
        }


class Equipment(models.Model):
    """
    Represents medical equipment in the clinic's inventory.
    """
    data_recorder = models.ForeignKey(
        Staffs, on_delete=models.CASCADE, blank=True, null=True, related_name='clinic_equipment_records',
        help_text="The staff member who recorded this equipment."
    )
    
    # Equipment details
    name = models.CharField(
        max_length=100,
        help_text="Name of the medical equipment."
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the equipment."
    )
    manufacturer = models.CharField(
        max_length=100, blank=True,
        help_text="Manufacturer of the equipment."
    )
    serial_number = models.CharField(
        max_length=50, blank=True,
        help_text="Serial number of the equipment for tracking."
    )
    
    # Dates
    acquisition_date = models.DateField(
        null=True, blank=True,
        help_text="Date when the equipment was acquired."
    )
    warranty_expiry_date = models.DateField(
        null=True, blank=True,
        help_text="Expiry date of the warranty."
    )
    
    # Status and location
    location = models.CharField(
        max_length=100, blank=True,
        help_text="Location where the equipment is stored."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the equipment is currently active and operational."
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the equipment was added to inventory."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the equipment was last updated."
    )
    
    objects = models.Manager()

    class Meta:
        verbose_name = "Equipment"
        verbose_name_plural = "Equipment"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        """
        Validate business logic for Equipment.
        """
        if self.warranty_expiry_date and self.acquisition_date:
            if self.warranty_expiry_date < self.acquisition_date:
                raise ValidationError("Warranty expiry date cannot be before acquisition date.")
    

    
class Reagent(models.Model):
    """
    Represents laboratory reagents used in medical testing.
    """
    data_recorder = models.ForeignKey(
        Staffs, on_delete=models.CASCADE, blank=True, null=True, related_name='clinic_reagent_records',
        help_text="The staff member who recorded this reagent."
    )
    
    # Reagent details
    name = models.CharField(
        max_length=100,
        help_text="Name of the laboratory reagent."
    )
    manufacturer = models.CharField(
        max_length=100,
        help_text="Manufacturer of the reagent."
    )
    lot_number = models.CharField(
        max_length=50,
        help_text="Lot number for tracking and quality control."
    )
    
    # Storage and expiration
    expiration_date = models.DateField(
        blank=True, null=True,
        help_text="Expiration date of the reagent."
    )
    storage_conditions = models.TextField(
        blank=True,
        help_text="Storage conditions required for the reagent."
    )
    
    # Inventory details
    quantity_in_stock = models.PositiveIntegerField(
        help_text="Total quantity of reagent in stock."
    )
    remaining_quantity = models.PositiveIntegerField(
        help_text="Remaining quantity of reagent available for use."
    )
    price_per_unit = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Price per unit of the reagent."
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the reagent was added to inventory."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the reagent was last updated."
    )
    
    objects = models.Manager()

    class Meta:
        verbose_name = "Reagent"
        verbose_name_plural = "Reagents"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        """
        Validate business logic for Reagent.
        """
        if self.expiration_date and self.expiration_date < timezone.now().date():
            raise ValidationError({"expiration_date": "Expiration date cannot be in the past."})
        
        if self.remaining_quantity > self.quantity_in_stock:
            raise ValidationError("Remaining quantity cannot exceed total stock quantity.")
        
        if self.price_per_unit < 0:
            raise ValidationError({"price_per_unit": "Price cannot be negative."})

    @property
    def total_price(self) -> Decimal:
        """
        Calculate total price based on quantity in stock and price per unit.
        """
        if self.price_per_unit and self.quantity_in_stock:
            return self.price_per_unit * self.quantity_in_stock
        return Decimal('0')

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == '1':  # HOD
            AdminHOD.objects.create(admin=instance)
        elif instance.user_type == '2':  # Staff
            Staffs.objects.create(admin=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == '1':
        instance.admin_hod.save()
    elif instance.user_type == '2':
        instance.staff.save()


class ClinicCompany(models.Model):
    # Company name
    name = models.CharField(max_length=255, help_text='Name of the company')
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True,related_name='clinic_companies') 
    # Unique registration number for the company
    registration_number = models.CharField(max_length=100, unique=True, help_text='Company registration number')
    
    # Address details
    address = models.TextField(help_text='Address of the company')
    city = models.CharField(max_length=100, help_text='City where the company is located')
    state = models.CharField(max_length=100, help_text='State where the company is located')
    country = models.CharField(max_length=100, help_text='Country where the company is located')
    postal_code = models.CharField(max_length=20, help_text='Postal code of the company')

    # Contact details
    phone_number = models.CharField(max_length=20, help_text='Contact phone number of the company')
    email = models.EmailField(unique=True, help_text='Email address of the company')
    website = models.URLField(blank=True, null=True, help_text='Website URL of the company')

    # Company logo
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True, help_text='Company logo image')

    # Timestamp for record creation and update
    created_at = models.DateTimeField(auto_now_add=True, help_text='Timestamp when the record was created')
    updated_at = models.DateTimeField(auto_now=True, help_text='Timestamp when the record was last updated')

    def __str__(self):
        return self.name



 
class HealthRecord(models.Model):   
    data_recorder = models.ForeignKey('clinic.Staffs', on_delete=models.CASCADE, blank=True, null=True, related_name='clinic_health_records')  
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    # Add more fields for health record information as needed

    def __str__(self):
        return f"{self.name}"  
    


    

class Diagnosis(models.Model):
    diagnosis_name= models.CharField(max_length=255,unique=True)
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True)
    diagnosis_code= models.CharField(max_length=20,unique=True,default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    
    def __str__(self):
        return f"{self.diagnosis_name}-{self.diagnosis_code}"


class PatientDiagnosisRecord(models.Model):
    visit = models.ForeignKey(PatientVisits, on_delete=models.CASCADE) 
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE) 
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True)
    provisional_diagnosis = models.ManyToManyField(Diagnosis, related_name='provisional_diagnosis_record')
    final_diagnosis = models.ManyToManyField(Diagnosis, related_name='final_diagnosis_record')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

 
class ObservationRecord(models.Model):
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE)
    visit = models.ForeignKey(PatientVisits, on_delete=models.CASCADE)    
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True) 
    observation_notes = CKEditor5Field(config_name='extends',blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    def __str__(self):
        return f"Record for {self.patient} - ({self.data_recorder})"
    

 
 

class DischargesNotes(models.Model):    
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True) 
    discharge_condition  = models.CharField(max_length=255)
    discharge_notes = CKEditor5Field(config_name='extends',blank=True, null=True)
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE)
    visit = models.ForeignKey(PatientVisits, on_delete=models.CASCADE,blank=True, null=True) 
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

class Referral(models.Model):
    # Patient who is being referred
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE)   
    visit = models.ForeignKey(PatientVisits, on_delete=models.CASCADE,blank=True, null=True)
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True) 
    source_location  = models.CharField(max_length=255, help_text='Source location of the patient',default="DIVINE TIS Mobile medical clinic")
    destination_location = models.CharField(max_length=255, help_text='Destination location for MedEvac')    
    notes =  CKEditor5Field(config_name='extends',blank=True, null=True) 
    nature_of_referral = models.CharField(max_length=20, choices=NATURE_OF_REFERRAL_CHOICES, default='Referred')
    transport_model = models.CharField(max_length=50, choices=TRANSPORT_MODEL_CHOICES, default='Ground Ambulance',blank=True, null=True)
    
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


class ClinicChiefComplaint(models.Model):   
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True,related_name='clinic_chief_complaints')  
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE)
    visit = models.ForeignKey(PatientVisits, on_delete=models.CASCADE,blank=True, null=True)
    health_record = models.ForeignKey(HealthRecord, on_delete=models.CASCADE,blank=True, null=True)
    other_complaint = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    # Other fields for Chief Complaint
    def __str__(self):
        return f"{self.health_record.name} - {self.duration}"    
    
 
    
class Payroll(models.Model):
    STATUS_CHOICES = [
        ('processed', 'Processed'),
        ('pending', 'Pending'),
        ('canceled', 'Canceled'),
    ]
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True,related_name='payrolls') 
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
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True,related_name='bank_accounts')   
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
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True,related_name='salary_payments') 
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
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True,related_name='employees') 
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

    # Format the employee ID with leading zeros and concatenate with the prefix "RES-"
    new_number= f"RES-{new_employee_number:05d}"

    return new_number    
    
class DeductionOrganization(models.Model):
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True,related_name='deduction_organizations') 
    name = models.CharField(max_length=100)
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    def __str__(self):
        return self.name
    
class EmployeeDeduction(models.Model):
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True,related_name='employee_deductions') 
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
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True,related_name='salary_change_records') 
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
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True,related_name='payment_methods') 
    name = models.CharField(max_length=100,unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 
    objects = models.Manager()
    def __str__(self):
        return self.name    
    
class ExpenseCategory(models.Model):
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True,related_name='expense_categories') 
    name = models.CharField(max_length=100,unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 
    objects = models.Manager()
    def __str__(self):
        return self.name

    
class Expense(models.Model):
    date = models.DateField()
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True,related_name='expenses') 
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
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True,related_name='investments') 
    investment_type = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True)

    # Add any additional fields as needed
    
    def __str__(self):
        return f"{self.investment_type} - {self.amount} - {self.date}"
    
class Grant(models.Model):
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True,related_name='grants') 
    grant_name = models.CharField(max_length=100)
    funding_amount = models.DecimalField(max_digits=10, decimal_places=2)
    donor_name = models.CharField(max_length=100)
    grant_date = models.DateField()
    description = models.TextField(blank=True)

    # Add any additional fields as needed

    def __str__(self):
        return f"{self.grant_name} - {self.funding_amount} - {self.grant_date}"

class GovernmentProgram(models.Model):
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True,related_name='government_programs') 
    program_name = models.CharField(max_length=100)
    funding_amount = models.DecimalField(max_digits=10, decimal_places=2)
    eligibility_criteria = models.TextField()
    description = models.TextField(blank=True)

    # Add any additional fields as needed

    def __str__(self):
        return self.program_name    
    
class Invoice(models.Model):
    """
    Represents an invoice for services or products provided to clients.
    """
    STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('pending', 'Pending'),
        ('overdue', 'Overdue'),
    ]
    
    data_recorder = models.ForeignKey(
        Staffs, on_delete=models.CASCADE, blank=True, null=True, related_name='invoices',
        help_text="The staff member who created this invoice."
    )
    
    # Invoice details
    number = models.CharField(
        max_length=50, unique=True,
        help_text="Unique invoice number for tracking."
    )
    date = models.DateField(
        help_text="Date when the invoice was issued."
    )
    due_date = models.DateField(
        help_text="Date when the invoice payment is due."
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Total amount of the invoice."
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        help_text="Current status of the invoice payment."
    )
    
    # Client relationship
    client = models.ForeignKey(
        'Clients', on_delete=models.CASCADE,
        help_text="The client for whom this invoice was created."
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the invoice was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the invoice was last updated."
    )
    
    objects = models.Manager()

    class Meta:
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"
        ordering = ["-date"]

    def __str__(self) -> str:
        return f"Invoice {self.number} for {self.client} - {self.status}"

    def clean(self) -> None:
        """
        Validate business logic for Invoice.
        """
        if self.amount < 0:
            raise ValidationError({"amount": "Invoice amount cannot be negative."})
        
        if self.due_date < self.date:
            raise ValidationError("Due date cannot be before invoice date.")

    def save(self, *args, **kwargs) -> None:
        """
        Auto-generate invoice number if not provided.
        Format: INV001, INV002, etc.
        """
        if not self.number:
            last_invoice = Invoice.objects.order_by('-id').first()
            if last_invoice:
                last_id = int(last_invoice.number[3:])
                new_id = last_id + 1
            else:
                new_id = 1
            self.number = f'INV{new_id:03}'
        self.full_clean()  # Ensure validation is triggered
        super().save(*args, **kwargs)

class Payment(models.Model):
    """
    Represents a payment made for services or invoices.
    """
    date = models.DateField(
        help_text="Date when the payment was made."
    )
    data_recorder = models.ForeignKey(
        Staffs, on_delete=models.CASCADE, blank=True, null=True, related_name='payments',
        help_text="The staff member who recorded this payment."
    )
    
    # Payment details
    amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Amount of the payment."
    )
    method = models.ForeignKey(
        PaymentMethod, on_delete=models.CASCADE, blank=True, null=True,
        help_text="Method used for the payment."
    )
    invoice = models.ForeignKey(
        Invoice, on_delete=models.SET_NULL, blank=True, null=True,
        help_text="Invoice associated with this payment (if applicable)."
    )
    description = models.TextField(
        blank=True,
        help_text="Description or notes about the payment."
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the payment was recorded."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the payment was last updated."
    )
    
    objects = models.Manager()

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        ordering = ["-date"]

    def __str__(self) -> str:
        return f"Payment of {self.amount} made on {self.date}"

    def clean(self) -> None:
        """
        Validate business logic for Payment.
        """
        if self.amount <= 0:
            raise ValidationError({"amount": "Payment amount must be greater than zero."})
        
        if self.date > timezone.now().date():
            raise ValidationError("Payment date cannot be in the future.")


class Activity(models.Model):
    ACTIVITY_TYPES = (
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
    )
    
    activity_type = models.CharField(max_length=10, choices=ACTIVITY_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        get_user_model(), 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    content_type = models.ForeignKey(
        ContentType, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    details = models.JSONField(null=True, blank=True)
    patient = models.ForeignKey(
        'Patients', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )

    objects = models.Manager()

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Activities'
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['activity_type']),
            models.Index(fields=['patient']),
        ]

    def get_activity_type_display(self):
        """Human-readable activity types"""
        types = {
            'login': 'User Login',
            'logout': 'User Logout',
            'create': 'Object Created',
            'update': 'Object Updated',
            'delete': 'Object Deleted',
        }
        return types.get(self.activity_type, self.activity_type.capitalize())
    
    def safe_content_object(self):
        """Safe method to get content object"""
        if self.content_type and self.object_id:
            try:
                # Get the model class safely
                model_class = self.content_type.model_class()
                if model_class:
                    # Try to get the object
                    return model_class._base_manager.get(pk=self.object_id)
            except Exception:
                pass
        return None

    def __str__(self):
        user_str = self.user.username if self.user else "System"
        return f"{user_str} {self.get_activity_type_display()}"



class Clients(models.Model):
    """
    Represents a client or customer for the clinic, such as a company or individual.
    """
    # Relationships
    data_recorder = models.ForeignKey(
        Staffs, on_delete=models.CASCADE, blank=True, null=True, related_name='clients',
        help_text="The staff member who recorded this client."
    )

    # Client details
    name = models.CharField(
        max_length=100,
        help_text="Full name of the client or company."
    )
    email = models.EmailField(
        blank=True,
        help_text="Email address of the client."
    )
    phone_number = models.CharField(
        max_length=20, blank=True,
        help_text="Contact phone number for the client."
    )
    address = models.CharField(
        max_length=200, blank=True,
        help_text="Physical or mailing address of the client."
    )
    contact_person = models.CharField(
        max_length=100, blank=True,
        help_text="Name of the primary contact person for the client."
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the client record was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the client record was last updated."
    )

    objects = models.Manager()

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """
        Return a human-readable representation of the client, including contact person if available.
        """
        if self.contact_person:
            return f"{self.name} (Contact: {self.contact_person})"
        return self.name

    def clean(self) -> None:
        """
        Validate business logic for Clients.
        """
        if self.email and not self.email.strip():
            raise ValidationError({"email": "Email cannot be blank if provided."})
        if self.phone_number and not self.phone_number.strip():
            raise ValidationError({"phone_number": "Phone number cannot be blank if provided."})
    
    