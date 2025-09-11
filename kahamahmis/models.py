from django.db import models
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.fields import CKEditor5Field
from django.core.exceptions import ValidationError
from django.utils import timezone
from clinic.models import NATURE_OF_REFERRAL_CHOICES, TRANSPORT_MODEL_CHOICES, Country,  PathodologyRecord, Staffs,   PrescriptionFrequency
# Make sure KahamaMedicine, KahamaPatient, NATURE_OF_REFERRAL_CHOICES, TRANSPORT_MODEL_CHOICES are imported or defined above


class KahamaDiseaseRecode(models.Model):
    data_recorder = models.ForeignKey(Staffs, on_delete=models.CASCADE,blank=True, null=True,related_name='kahama_disease_records') 
    disease_name = models.CharField(max_length=255, unique=True)  
    code = models.CharField(max_length=25,unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    def __str__(self):
        return self.disease_name

class KahamaHealthRecord(models.Model):
    """
    Model to store health record information for Kahama patients.
    """
    data_recorder = models.ForeignKey(
        'clinic.Staffs',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='kahama_health_records',
        help_text="Staff member who recorded this health record."
    )
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Name or title of the health record."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the health record was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the health record was last updated."
    )

    objects = models.Manager()

    def __str__(self):
        return self.name

class KahamaDiagnosis(models.Model):
    """
    Model to store diagnosis information for Kahama patients.
    """
    diagnosis_name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Name of the diagnosis."
    )
    data_recorder = models.ForeignKey(
        Staffs, on_delete=models.CASCADE,
        blank=True,
        null=True,
        help_text="Staff member who recorded this diagnosis."
    )
    diagnosis_code = models.CharField(
        max_length=20,
        unique=True,
        default="",
        help_text="Unique code for the diagnosis (e.g., ICD-10 code)."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the diagnosis was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the diagnosis was last updated."
    )

    objects = models.Manager()

    def __str__(self):
        return f"{self.diagnosis_name} - {self.diagnosis_code}"
    
class KahamaCompany(models.Model):
    """
    Represents a company or organization associated with kahama patients.
    """
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Name of the kahama company or organization."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the company was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the company was last updated."
    )

    objects = models.Manager()

    def __str__(self):
        return self.name
    
class KahamaMedicine(models.Model):
    """
    Represents medicines available at kahama locations or partner clinics.
    """
    data_recorder = models.ForeignKey(
        'clinic.Staffs', on_delete=models.CASCADE, blank=True, null=True, related_name='kahama_medicines',
        help_text="The staff member who recorded this kahama medicine."
    )
    
    # Medicine details
    drug_name = models.CharField(
        max_length=100,
        help_text="Name of the medicine or drug."
    )
    drug_type = models.CharField(
        max_length=20, blank=True, null=True,
        help_text="Type of drug (e.g., Tablet, Syrup, Injection)."
    )
    formulation_unit = models.CharField(
        max_length=50,
        help_text="Formulation unit (e.g., '500mg', '5ml')."
    )
    dividing_unit = models.PositiveIntegerField(
        blank=True, null=True,
        help_text="Smallest divisible unit in mg or ml, e.g., 125."
    )
    is_dividable = models.BooleanField(
        default=False,
        help_text="Is this drug divisible in smaller units?"
    )
    
    # Stock management
    is_clinic_stock = models.BooleanField(
        default=True,
        help_text="Is this drug part of clinic stock?"
    )
    
    # These fields only apply if is_clinic_stock is True
    manufacturer = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="Manufacturer of the medicine."
    )
    quantity = models.PositiveIntegerField(
        blank=True, null=True,
        help_text="Total quantity available."
    )
    remain_quantity = models.PositiveIntegerField(
        blank=True, null=True,
        help_text="Remaining quantity in stock."
    )
    batch_number = models.CharField(
        max_length=20, unique=True, blank=True, null=True,
        help_text="Batch number for tracking."
    )
    expiration_date = models.DateField(
        blank=True, null=True,
        help_text="Expiration date of the medicine."
    )
    minimum_stock_level = models.PositiveIntegerField(
        default=0,
        help_text="Minimum threshold before restocking."
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the kahama medicine was added."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the kahama medicine was last updated."
    )

    objects = models.Manager()

    class Meta:
        verbose_name = "Kahama Medicine"
        verbose_name_plural = "Kahama Medicines"
        ordering = ["drug_name"]

    def __str__(self) -> str:
        return self.drug_name

    def clean(self) -> None:
        """
        Validate business logic for KahamaMedicine.
        """
        if self.is_clinic_stock:
            required_fields = {
                'quantity': self.quantity,
                'remain_quantity': self.remain_quantity,
                'batch_number': self.batch_number,
                'expiration_date': self.expiration_date,
                'minimum_stock_level': self.minimum_stock_level,
                'manufacturer': self.manufacturer,
            }
            for field_name, value in required_fields.items():
                if value in [None, '']:
                    raise ValidationError({field_name: f"{field_name.replace('_', ' ').capitalize()} is required for clinic stock."})
        
        if self.expiration_date and self.expiration_date < timezone.now().date():
            raise ValidationError({"expiration_date": "Expiration date cannot be in the past."})    

class KahamaPatientMedicationAllergy(models.Model):
    """
    Records a medication allergy for a kahama patient.
    """
    data_recorder = models.ForeignKey(
        Staffs, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='kahama_patient_medication_allergies',
        help_text="Staff member who recorded the allergy."
    )
    patient = models.ForeignKey(
        'kahamahmis.KahamaPatient', on_delete=models.CASCADE,
        related_name='medication_allergies',
        help_text="Patient with the medication allergy."
    )
    medicine = models.ForeignKey(
        'kahamahmis.KahamaMedicine', on_delete=models.CASCADE,
        related_name='allergy_records',
        help_text="Medicine to which the patient is allergic."
    )
    reaction = models.CharField(
        max_length=200,
        help_text="Description of the allergic reaction."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the allergy was recorded."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the allergy record was last updated."
    )

    def __str__(self):
        return f"{self.patient} - {self.medicine} ({self.reaction})"

class KahamaPatientSurgery(models.Model):
    """
    Stores information about a kahama patient's past surgeries.
    """
    data_recorder = models.ForeignKey(
        Staffs, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='kahama_patient_surgeries',
        help_text="Staff member who recorded the surgery."
    )
    patient = models.ForeignKey(
        'kahamahmis.KahamaPatient', on_delete=models.CASCADE,
        related_name='surgeries',
        help_text="Patient who underwent the surgery."
    )
    surgery_name = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="Name of the surgery."
    )
    surgery_date = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="Date when the surgery was performed."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the surgery record was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the surgery record was last updated."
    )

    objects = models.Manager()

    def __str__(self):
        return f"{self.patient} - {self.surgery_name} ({self.surgery_date})"

class KahamaPatientLifestyleBehavior(models.Model):
    """
    Captures lifestyle and behavioral information for a kahama patient.
    """
    data_recorder = models.ForeignKey(
        Staffs, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='kahama_patient_lifestyle_behaviors',
        help_text="Staff member who recorded the lifestyle behavior."
    )
    patient = models.OneToOneField(
        'kahamahmis.KahamaPatient', on_delete=models.CASCADE,
        related_name='lifestyle_behavior',
        help_text="Patient whose lifestyle is being recorded."
    )
    weekly_exercise_frequency = models.CharField(
        max_length=32, blank=True, null=True,
        help_text="How often the patient exercises per week."
    )
    smoking = models.CharField(
        max_length=32, blank=True, null=True,
        help_text="Smoking status of the patient."
    )
    alcohol_consumption = models.CharField(
        max_length=32, blank=True, null=True,
        help_text="Alcohol consumption status."
    )
    healthy_diet = models.CharField(
        max_length=32, blank=True, null=True,
        help_text="Whether the patient follows a healthy diet."
    )
    stress_management = models.CharField(
        max_length=32, blank=True, null=True,
        help_text="Patient's stress management habits."
    )
    sufficient_sleep = models.CharField(
        max_length=32, blank=True, null=True,
        help_text="Whether the patient gets sufficient sleep."
    )

    def __str__(self):
        return f"Lifestyle for {self.patient}"

def generate_for_kahama_mrn():
    """
    Generates a unique Medical Record Number (MRN) for a new kahama patient.
    """
    last_patient = KahamaPatient.objects.order_by('-id').first()
    if last_patient and last_patient.mrn and '-' in last_patient.mrn:
        try:
            last_mrn_number = int(last_patient.mrn.split('-')[-1])
        except (ValueError, IndexError):
            last_mrn_number = 0
    else:
        last_mrn_number = 0
    new_mrn_number = last_mrn_number + 1
    return f"PAT-{new_mrn_number:05d}"

class KahamaPatient(models.Model):
    """
    Represents a kahama patient and their core demographic and contact information.
    """
    mrn = models.CharField(
        max_length=20, unique=True, editable=False, verbose_name='MRN',
        help_text="Medical Record Number (auto-generated)."
    )
    data_recorder = models.ForeignKey(
        Staffs, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='recorded_kahama_patients',
        help_text="Staff member who registered the patient."
    )
    first_name = models.CharField(
        max_length=100,
        help_text="Patient's first name."
    )
    middle_name = models.CharField(
        max_length=100, blank=True, default="",
        help_text="Patient's middle name (optional)."
    )
    last_name = models.CharField(
        max_length=100,
        help_text="Patient's last name."
    )
    gender = models.CharField(
        max_length=10,
        choices=[('Male', 'Male'), ('Female', 'Female')],
        help_text="Patient's gender."
    )
    age = models.PositiveIntegerField(
        blank=True, null=True,
        help_text="Patient's age."
    )
    dob = models.DateField(
        null=True, blank=True,
        help_text="Date of birth."
    )
    nationality = models.ForeignKey(
        Country, on_delete=models.PROTECT,
        help_text="Patient's nationality."
    )
    phone = models.CharField(
        max_length=20,
        help_text="Patient's phone number."
    )
    osha_certificate = models.BooleanField(
        default=False,
        help_text="Whether the patient has an OSHA certificate."
    )
    date_of_osha_certification = models.DateField(
        null=True, blank=True,
        help_text="Date of OSHA certification."
    )
    ftw_certificate = models.BooleanField(
        default=False,
        help_text="Whether the patient has an FTW certificate."
    )
    date_of_ftw_certification = models.DateField(
        null=True, blank=True,
        help_text="Date of FTW certification."
    )
    insurance = models.CharField(
        max_length=20,
        choices=[('Uninsured', 'Uninsured'), ('Insured', 'Insured'), ('Unknown', 'Unknown')],
        help_text="Insurance status."
    )
    insurance_company = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="Name of the insurance company."
    )
    other_insurance_company = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="Other insurance company (if not listed)."
    )
    insurance_number = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="Insurance policy number."
    )
    emergency_contact_name = models.CharField(
        max_length=100,
        help_text="Name of emergency contact."
    )
    emergency_contact_relation = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="Relationship to emergency contact."
    )
    other_emergency_contact_relation = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="Other relationship to emergency contact."
    )
    emergency_contact_phone = models.CharField(
        max_length=20,
        help_text="Phone number of emergency contact."
    )
    marital_status = models.CharField(
        max_length=20,
        choices=[('Single', 'Single'), ('Married', 'Married'), ('Divorced', 'Divorced'), ('Widowed', 'Widowed')],
        default="Single",
        help_text="Marital status."
    )
    occupation = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="Patient's occupation."
    )
    other_occupation = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="Other occupation (if not listed)."
    )
    patient_type = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="Type of patient."
    )
    other_patient_type = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="Other patient type (if not listed)."
    )
    company = models.ForeignKey(
        KahamaCompany, on_delete=models.PROTECT,
        help_text="Company or organization associated with the patient."
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Created At',
        help_text="Timestamp when the patient was registered."
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name='Updated At',
        help_text="Timestamp when the patient record was last updated."
    )

    objects = models.Manager()

    @property
    def full_name(self):
        """
        Returns the full name of the patient.
        """
        return " ".join(filter(None, [self.first_name, self.middle_name, self.last_name]))

    def save(self, *args, **kwargs):
        if not self.mrn:
            self.mrn = generate_for_kahama_mrn()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} ({self.company})"

class KahamaPatientHealthCondition(models.Model):
    """
    Stores a health condition for a kahama patient.
    """
    patient = models.ForeignKey(
        KahamaPatient, on_delete=models.CASCADE,
        related_name='health_conditions',
        verbose_name='Patient',
        help_text="Patient with the health condition."
    )
    data_recorder = models.ForeignKey(
        Staffs, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='recorded_kahama_health_conditions',
        help_text="Staff member who recorded the health condition."
    )
    health_condition = models.CharField(
        max_length=200, blank=True, null=True,
        verbose_name='Health Condition',
        help_text="Name of the health condition."
    )
    health_condition_notes = models.CharField(
        max_length=200, blank=True, null=True,
        verbose_name='Health Condition Notes',
        help_text="Additional notes about the health condition."
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Created At',
        help_text="Timestamp when the health condition was recorded."
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name='Updated At',
        help_text="Timestamp when the health condition was last updated."
    )

    objects = models.Manager()

    def __str__(self):
        return f"{self.patient} - {self.health_condition}"

class KahamaFamilyMedicalHistory(models.Model):
    """
    Records a family medical history entry for a kahama patient.
    """
    patient = models.ForeignKey(
        KahamaPatient, on_delete=models.CASCADE,
        related_name='family_medical_history',
        verbose_name='Patient',
        help_text="Patient whose family history is being recorded."
    )
    data_recorder = models.ForeignKey(
        Staffs, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='recorded_kahama_family_histories',
        help_text="Staff member who recorded the family history."
    )
    condition = models.CharField(
        max_length=100, verbose_name='Condition',
        help_text="Medical condition present in the family."
    )
    relationship = models.CharField(
        max_length=100, blank=True, null=True, verbose_name='Relationship',
        help_text="Relationship of the family member to the patient."
    )
    comments = models.CharField(
        max_length=100, blank=True, null=True, verbose_name='Comments',
        help_text="Additional comments."
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Created At',
        help_text="Timestamp when the family history was recorded."
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name='Updated At',
        help_text="Timestamp when the family history was last updated."
    )

    objects = models.Manager()

    def __str__(self):
        return f"{self.patient} - {self.condition}"

class KahamaService(models.Model):
    """
    Represents a kahama service that can be ordered or provided to a patient.
    """
    name = models.CharField(
        max_length=225, unique=True,
        help_text="Name of the kahama service."
    )
    data_recorder = models.ForeignKey(
        Staffs, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='kahama_services',
        help_text="Staff member who created the service record."
    )
    description = models.TextField(
        default="",
        help_text="Description of the service."
    )
    category = models.CharField(
        max_length=50, null=True, blank=True,
        help_text="Category of the service."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the service was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the service was last updated."
    )

    objects = models.Manager()

    def __str__(self):
        return f"{self.name} ({self.category})"

class KahamaPatientVisits(models.Model):
    """
    Represents a visit by a kahama patient.
    """
    VISIT_TYPES = (
        ('Normal', _('Normal')),
        ('Emergency', _('Emergency')),
        ('Referral', _('Referral')),
        ('Follow up', _('Follow up')),
    )
    data_recorder = models.ForeignKey(
        Staffs, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='kahama_patient_visits',
        help_text="Staff member who recorded the visit."
    )
    patient = models.ForeignKey(
        KahamaPatient, on_delete=models.CASCADE,
        related_name='visits',
        help_text="Patient attending the visit."
    )
    vst = models.CharField(
        max_length=20, unique=True, editable=False,
        help_text="Visit serial number (auto-generated)."
    )
    visit_type = models.CharField(
        max_length=15, choices=VISIT_TYPES,
        help_text="Type of the visit."
    )
    primary_service = models.CharField(
        max_length=50,
        help_text="Primary service for the visit."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the visit was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the visit was last updated."
    )

    class Meta:
        verbose_name = _('Visit')
        verbose_name_plural = _('Visits')
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.vst:
            self.vst = kahamagenerate_vst()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.patient.full_name} - {self.get_visit_type_display()}"

def kahamagenerate_vst():
    """
    Generates a unique visit serial number for a kahama patient visit.
    """
    last_visit = KahamaPatientVisits.objects.order_by('-id').first()
    if last_visit and last_visit.vst and '-' in last_visit.vst:
        try:
            last_vst_number = int(last_visit.vst.split('-')[-1])
        except (ValueError, IndexError):
            last_vst_number = 0
    else:
        last_vst_number = 0
    new_vst_number = last_vst_number + 1
    return f"VST-{new_vst_number:07d}"

class KahamaPatientVital(models.Model):
    """
    Stores vital signs for a kahama patient during a visit.
    """
    patient = models.ForeignKey(
        KahamaPatient, on_delete=models.CASCADE,
        related_name='vitals',
        help_text="Patient whose vitals are recorded."
    )
    visit = models.ForeignKey(
        KahamaPatientVisits, on_delete=models.CASCADE,
        related_name='vitals',
        help_text="Visit during which vitals were recorded."
    )
    doctor = models.ForeignKey(
        Staffs, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='recorded_kahama_vitals',
        help_text="Doctor who recorded the vitals."
    )
    recorded_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the vitals were recorded."
    )

    respiratory_rate = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Respiratory rate (breaths per minute)."
    )
    pulse_rate = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Pulse rate (beats per minute)."
    )
    sbp = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Systolic Blood Pressure (mmHg)."
    )
    dbp = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Diastolic Blood Pressure (mmHg)."
    )
    blood_pressure = models.CharField(
        max_length=7, null=True, blank=True,
        help_text="Blood pressure in format 'SBP/DBP'."
    )
    spo2 = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Oxygen saturation (SPO2) in percent."
    )
    temperature = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True, default=37.5,
        help_text="Body temperature in Celsius."
    )
    gcs = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Glasgow Coma Scale score."
    )

    # New fields
    height = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="Height in centimeters."
    )
    weight = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="Weight in kilograms."
    )
    bmi = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True,
        help_text="Body Mass Index (BMI)."
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the vitals were last updated."
    )

    objects = models.Manager()

    def __str__(self):
        return f"Vitals for {self.patient.full_name} at {self.recorded_at}"

    def save(self, *args, **kwargs):
        """
        Automatically calculate BMI when height and weight are provided.
        """
        if self.height and self.weight:
            # convert height cm → m
            height_m = float(self.height) / 100
            if height_m > 0:
                self.bmi = round(float(self.weight) / (height_m ** 2), 1)
        super().save(*args, **kwargs)


class KahamaPatientDiagnosisRecord(models.Model):
    """
    Stores provisional and final diagnoses for a kahama patient during a visit.
    """
    visit = models.ForeignKey(
        KahamaPatientVisits, on_delete=models.CASCADE,
        related_name='diagnosis_records',
        help_text="Visit associated with the diagnosis."
    )
    patient = models.ForeignKey(
        KahamaPatient, on_delete=models.CASCADE,
        related_name='diagnosis_records',
        help_text="Patient for whom the diagnosis is recorded."
    )
    data_recorder = models.ForeignKey(
        Staffs, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='recorded_kahama_diagnosis_records',
        help_text="Staff member who recorded the diagnosis."
    )
    provisional_diagnosis = models.ManyToManyField(
        KahamaDiagnosis, related_name='kahama_provisional_diagnosis_records',
        help_text="Provisional diagnoses."
    )
    final_diagnosis = models.ManyToManyField(
        KahamaDiagnosis, related_name='kahama_final_diagnosis_records',
        help_text="Final diagnoses."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the diagnosis record was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the diagnosis record was last updated."
    )

    objects = models.Manager()

    def __str__(self):
        provisional = ", ".join([str(d) for d in self.provisional_diagnosis.all()])
        final = ", ".join([str(d) for d in self.final_diagnosis.all()])
        return f"Patient: {self.patient.full_name} | Provisional: [{provisional}] | Final: [{final}]"

class KahamaConsultationNotes(models.Model):
    """
    Stores consultation notes for a kahama patient visit.
    """
    doctor = models.ForeignKey(
        Staffs, on_delete=models.PROTECT,
        related_name='kahama_consultation_notes',
        help_text="Doctor who wrote the consultation notes."
    )
    patient = models.ForeignKey(
        KahamaPatient, on_delete=models.CASCADE,
        related_name='consultation_notes',
        help_text="Patient for whom the notes are written."
    )
    visit = models.ForeignKey(
        KahamaPatientVisits, on_delete=models.CASCADE, null=True, blank=True,
        related_name='consultation_notes',
        help_text="Visit associated with the consultation notes."
    )
    history_of_presenting_illness = models.TextField(
        null=True, blank=True,
        help_text="History of presenting illness."
    )
    review_of_systems = models.TextField(
        null=True, blank=True,
        help_text="Review of systems."
    )
    physical_examination = models.TextField(
        null=True, blank=True,
        help_text="Physical examination findings."
    )
    doctor_plan = models.TextField(
        help_text="Doctor's plan."
    )
    doctor_plan_note = models.TextField(
        null=True, blank=True,
        help_text="Additional notes on the doctor's plan."
    )
    pathology = models.ManyToManyField(
        PathodologyRecord, blank=True,
        help_text="Pathology records associated with the consultation."
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the consultation notes were created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the consultation notes were last updated."
    )

    objects = models.Manager()

    def __str__(self):
        return f"Consultation for {self.patient.full_name} by Dr. {self.doctor}"


class KahamaObservationRecord(models.Model):
    """
    Stores observation notes for a kahama patient during a visit.
    """
    patient = models.ForeignKey(
        KahamaPatient, on_delete=models.CASCADE,
        related_name='observation_records',
        help_text="Patient for whom the observation is recorded."
    )
    visit = models.ForeignKey(
        KahamaPatientVisits, on_delete=models.CASCADE,
        related_name='observation_records',
        help_text="Visit associated with the observation."
    )
    data_recorder = models.ForeignKey(
        Staffs, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='recorded_kahama_observations',
        help_text="Staff member who recorded the observation."
    )
    observation_notes = CKEditor5Field(
        config_name='extends', blank=True, null=True,
        help_text="Observation notes."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the observation was recorded."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the observation was last updated."
    )

    objects = models.Manager()

    def __str__(self):
        return f"Observation for {self.patient.full_name} ({self.data_recorder})"



class KahamaLaboratoryRequest(models.Model):
    """
    Represents a laboratory request for a kahama patient.
    """
    patient = models.ForeignKey(
        KahamaPatient, on_delete=models.CASCADE,
        related_name='laboratory_requests',
        help_text="Patient for whom the laboratory request is made."
    )
    visit = models.ForeignKey(
        KahamaPatientVisits, on_delete=models.CASCADE, blank=True, null=True,
        related_name='laboratory_requests',
        help_text="Visit associated with the laboratory request."
    )
    data_recorder = models.ForeignKey(
        Staffs, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='recorded_kahama_lab_requests',
        help_text="Staff member who recorded the laboratory request."
    )
    name = models.ForeignKey(
        KahamaService, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='laboratory_requests',
        help_text="Laboratory service requested."
    )
    result = CKEditor5Field(
        config_name='extends', blank=True, null=True,
        help_text="Result of the laboratory test."
    )
    lab_number = models.CharField(
        max_length=20, unique=True,
        help_text="Laboratory request number (auto-generated)."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the laboratory request was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the laboratory request was last updated."
    )

    objects = models.Manager()

    def __str__(self):
        return f"Laboratory Request: {self.name} for {self.patient.full_name}"

    def save(self, *args, **kwargs):
        if not self.lab_number:
            last_lab = KahamaLaboratoryRequest.objects.order_by('-id').first()
            if last_lab and last_lab.lab_number and '-' in last_lab.lab_number:
                try:
                    last_number = int(last_lab.lab_number.split('-')[-1])
                except (ValueError, IndexError):
                    last_number = 0
            else:
                last_number = 0
            self.lab_number = f"LAB-{last_number + 1:07d}"
        super().save(*args, **kwargs)

class KahamaProcedure(models.Model):
    """
    Stores a procedure performed for a kahama patient during a visit.
    """
    patient = models.ForeignKey(
        KahamaPatient, on_delete=models.CASCADE,
        related_name='procedures',
        help_text="Patient who underwent the procedure."
    )
    doctor = models.ForeignKey(
        Staffs, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='performed_kahama_procedures',
        help_text="Doctor who performed the procedure."
    )
    visit = models.ForeignKey(
        KahamaPatientVisits, on_delete=models.CASCADE,
        related_name='procedures',
        help_text="Visit associated with the procedure."
    )
    name = models.ForeignKey(
        KahamaService, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='procedure_records',
        help_text="Name of the procedure."
    )
    description = models.TextField(
        help_text="Description of the procedure."
    )
    result = CKEditor5Field(
        config_name='extends', blank=True, null=True,
        help_text="Result of the procedure."
    )
    image = models.ImageField(
        upload_to='procedure_images/', blank=True, null=True,
        help_text="Image related to the procedure."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the procedure was recorded."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the procedure record was last updated."
    )

    objects = models.Manager()

    def __str__(self):
        return f"Procedure: {self.name} for {self.patient.full_name}"

class KahamaAppointment(models.Model):
    """
    Represents a scheduled kahama appointment for a patient.
    """
    data_recorder = models.ForeignKey(
        Staffs, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='recorded_kahama_appointments',
        help_text="Staff member who recorded the appointment."
    )
    doctor = models.ForeignKey(
        Staffs, on_delete=models.PROTECT,
        related_name='kahama_appointments',
        help_text="Doctor assigned to the appointment."
    )
    patient = models.ForeignKey(
        KahamaPatient, on_delete=models.CASCADE,
        related_name='appointments',
        help_text="Patient for whom the appointment is scheduled."
    )
    visit = models.ForeignKey(
        KahamaPatientVisits, on_delete=models.CASCADE, blank=True, null=True,
        related_name='appointments',
        help_text="Visit associated with the appointment."
    )
    created_by = models.ForeignKey(
        Staffs, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='created_kahama_appointments',
        help_text="Staff member who created the appointment record."
    )
    appointment_date = models.DateField(
        help_text="Date of the appointment."
    )
    start_time = models.TimeField(
        blank=True, null=True,
        help_text="Start time of the appointment."
    )
    end_time = models.TimeField(
        blank=True, null=True,
        help_text="End time of the appointment."
    )
    description = models.TextField(
        blank=True, null=True,
        help_text="Description or notes for the appointment."
    )
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
    status = models.IntegerField(
        choices=STATUS_CHOICES, default=0,
        help_text="Status of the appointment."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the appointment was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the appointment was last updated."
    )

    objects = models.Manager()

    def __str__(self):
        doctor_name = f"{self.doctor.admin.first_name} {self.doctor.middle_name} {self.doctor.admin.last_name}" if hasattr(self.doctor, 'admin') else str(self.doctor)
        return f"Appointment with {doctor_name} for {self.patient.full_name} on {self.appointment_date} from {self.start_time} to {self.end_time}"

class KahamaCounseling(models.Model):
    """
    Stores counseling notes for a kahama patient during a visit.
    """
    data_recorder = models.ForeignKey(
        Staffs, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='recorded_kahama_counselings',
        help_text="Staff member who recorded the counseling."
    )
    counselling_notes = CKEditor5Field(
        config_name='extends', blank=True, null=True,
        help_text="Counseling notes."
    )
    patient = models.ForeignKey(
        KahamaPatient, on_delete=models.CASCADE,
        related_name='counselings',
        help_text="Patient who received counseling."
    )
    visit = models.ForeignKey(
        KahamaPatientVisits, on_delete=models.CASCADE, blank=True, null=True,
        related_name='counselings',
        help_text="Visit associated with the counseling."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the counseling was recorded."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the counseling record was last updated."
    )

    objects = models.Manager()

    def __str__(self):
        return f"Counseling for {self.patient.full_name}"

class KahamaDischargesNotes(models.Model):
    """
    Stores discharge notes for a kahama patient.
    """
    data_recorder = models.ForeignKey(
        Staffs, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='recorded_kahama_discharges',
        help_text="Staff member who recorded the discharge."
    )
    discharge_condition = models.CharField(
        max_length=255,
        help_text="Condition of the patient at discharge."
    )
    discharge_notes = CKEditor5Field(
        config_name='extends', blank=True, null=True,
        help_text="Discharge notes."
    )
    patient = models.ForeignKey(
        KahamaPatient, on_delete=models.CASCADE,
        related_name='discharge_notes',
        help_text="Patient being discharged."
    )
    visit = models.ForeignKey(
        KahamaPatientVisits, on_delete=models.CASCADE, blank=True, null=True,
        related_name='discharge_notes',
        help_text="Visit associated with the discharge."
    )
    discharge_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the patient was discharged."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the discharge record was last updated."
    )

    objects = models.Manager()

    def __str__(self):
        return f"Discharge notes for {self.patient.full_name}"

class KahamaReferral(models.Model):
    """
    Represents a referral for a kahama patient to another facility or service.
    """
    patient = models.ForeignKey(
        KahamaPatient, on_delete=models.CASCADE,
        related_name='referrals',
        help_text="Patient being referred."
    )
    visit = models.ForeignKey(
        KahamaPatientVisits, on_delete=models.CASCADE, blank=True, null=True,
        related_name='referrals',
        help_text="Visit associated with the referral."
    )
    data_recorder = models.ForeignKey(
        Staffs, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='recorded_kahama_referrals',
        help_text="Staff member who recorded the referral."
    )
    source_location = models.CharField(
        max_length=255, default="resa medical hospital",
        help_text="Source location of the patient."
    )
    destination_location = models.CharField(
        max_length=255,
        help_text="Destination location for MedEvac."
    )
    rfn = models.CharField(
        max_length=20, unique=True, editable=False,
        help_text="Referral number (auto-generated)."
    )
    notes = CKEditor5Field(
        config_name='extends', blank=True, null=True,
        help_text="Referral notes."
    )
    nature_of_referral = models.CharField(
        max_length=20, choices=NATURE_OF_REFERRAL_CHOICES, default='Referred',
        help_text="Nature of the referral."
    )
    transport_model = models.CharField(
        max_length=50, choices=TRANSPORT_MODEL_CHOICES, default='Ground Ambulance',
        help_text="Mode of transport for the referral."
    )
    REFERRAL_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    status = models.CharField(
        max_length=20, choices=REFERRAL_STATUS_CHOICES, default='pending',
        help_text="Status of the referral."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the referral was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the referral was last updated."
    )

    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.rfn:
            last_referral = KahamaReferral.objects.order_by('-id').first()
            if last_referral and last_referral.rfn and '-' in last_referral.rfn:
                try:
                    last_rfn = int(last_referral.rfn.split('-')[-1])
                except (ValueError, IndexError):
                    last_rfn = 0
            else:
                last_rfn = 0
            self.rfn = f"RFN-{last_rfn + 1:07d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Referral for {self.patient.full_name} to {self.destination_location} from {self.source_location} on {self.created_at:%Y-%m-%d}"

    def get_status_class(self):
        return {
            'pending': 'text-warning',
            'accepted': 'text-success',
            'rejected': 'text-danger'
        }.get(self.status, '')

    def get_status_color(self):
        return {
            'pending': 'warning',
            'accepted': 'success',
            'rejected': 'danger'
        }.get(self.status, '')


class KahamaChiefComplaint(models.Model):
    """
    Represents a chief complaint record for a kahama patient during a visit.
    """
    # Relationships
    data_recorder = models.ForeignKey(
        Staffs, on_delete=models.CASCADE, blank=True, null=True, related_name='kahama_chief_complaints',
        help_text="The staff member who recorded this chief complaint."
    )
    patient = models.ForeignKey(
        'kahamahmis.KahamaPatient', on_delete=models.CASCADE,
        help_text="The kahama patient reporting the chief complaint."
    )
    visit = models.ForeignKey(
        'kahamahmis.KahamaPatientVisits', on_delete=models.CASCADE, blank=True, null=True,
        help_text="The visit associated with this chief complaint."
    )
    health_record = models.ForeignKey(
        KahamaHealthRecord, on_delete=models.CASCADE, blank=True, null=True,
        help_text="The health record associated with this complaint."
    )

    # Complaint details
    other_complaint = models.CharField(
        max_length=100,
        help_text="Description of the chief complaint or other symptoms."
    )
    duration = models.CharField(
        max_length=100,
        help_text="Duration of the complaint or symptoms."
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the chief complaint was recorded."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the chief complaint was last updated."
    )

    objects = models.Manager()

    class Meta:
        verbose_name = "Kahama Chief Complaint"
        verbose_name_plural = "Kahama Chief Complaints"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """
        Return a human-readable representation of the chief complaint, including health record if available.
        """
        if self.health_record:
            return f"{self.health_record.name} - {self.duration}"
        return f"Chief Complaint: {self.other_complaint} ({self.duration})"

    def clean(self) -> None:
        """
        Validate business logic for KahamaChiefComplaint.
        """
        if not self.other_complaint.strip():
            raise ValidationError({"other_complaint": "Chief complaint description cannot be empty."})
        if not self.duration.strip():
            raise ValidationError({"duration": "Duration cannot be empty."})

class KahamaPrescription(models.Model):
    """
    Represents a prescription for a kahama patient during a visit.
    
    This model tracks medication prescriptions including dosage, frequency,
    duration, and quantity prescribed to kahama patients.
    """
    
    # ==================== RELATIONSHIPS ====================
    patient = models.ForeignKey(
        KahamaPatient,
        on_delete=models.CASCADE,
        related_name="kahama_prescriptions",
        help_text="The kahama patient to whom this prescription belongs."
    )
    
    visit = models.ForeignKey(
        KahamaPatientVisits,
        on_delete=models.CASCADE,
        related_name="prescriptions",
        help_text="The kahama patient visit associated with this prescription."
    )
    
    medicine = models.ForeignKey(
        'kahamahmis.KahamaMedicine',
        on_delete=models.PROTECT,
        related_name="prescriptions",
        help_text="The medicine prescribed to the patient."
    )
    
    frequency = models.ForeignKey(
        PrescriptionFrequency,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="kahama_prescriptions",
        help_text="Frequency at which the medicine should be taken."
    )
    
    # ==================== STAFF RELATIONSHIPS ====================
    entered_by = models.ForeignKey(
        Staffs,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="entered_kahama_prescriptions",
        help_text="Staff member who entered the prescription."
    )
    
    # ==================== PRESCRIPTION DETAILS ====================
    prs_no = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        help_text="Unique prescription number, auto-generated."
    )
    
    dose = models.CharField(
        max_length=50,
        help_text="Dosage instructions for the medicine (e.g., '1 tablet', '10ml')."
    )
    
    duration = models.CharField(
        max_length=50,
        help_text="Duration for which the medicine should be taken (e.g., '7 days', '2 weeks')."
    )
    
    quantity_used = models.PositiveIntegerField(
        help_text="Quantity of the medicine prescribed."
    )
    
    # ==================== TIMESTAMPS ====================
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the prescription was created."
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the prescription was last updated."
    )
    
    # ==================== META CONFIGURATION ====================
    class Meta:
        verbose_name = "Kahama Prescription"
        verbose_name_plural = "Kahama Prescriptions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['patient', 'visit']),
            models.Index(fields=['prs_no']),
            models.Index(fields=['created_at']),
        ]
    
    # ==================== METHODS ====================
    def save(self, *args, **kwargs):
        """
        Override save method to auto-generate prescription number if not provided.
        """
        if not self.prs_no:
            self.prs_no = self._generate_prescription_id()
        super().save(*args, **kwargs)
    
    def _generate_prescription_id(self):
        """
        Generate a unique prescription ID in format PRS-XXXXXXX.
        
        Returns:
            str: A unique prescription number
        """
        last_prescription = KahamaPrescription.objects.order_by('-id').first()
        
        if last_prescription and last_prescription.prs_no and last_prescription.prs_no.startswith("PRS-"):
            try:
                last_number = int(last_prescription.prs_no.split('-')[-1])
            except (ValueError, IndexError):
                last_number = 0
        else:
            last_number = 0
        
        new_number = last_number + 1
        return f"PRS-{new_number:07d}"
    
    def __str__(self):
        """
        Return a human-readable representation of the prescription.
        
        Returns:
            str: Prescription description with patient name, medicine, and prescription number
        """
        return f"Prescription for {self.patient.full_name} - {self.medicine.drug_name} (PRS No: {self.prs_no})"
 


class KahamaReagent(models.Model):
    data_recorder = models.ForeignKey('clinic.Staffs', on_delete=models.CASCADE, blank=True, null=True, related_name='kahama_reagent_records')
    name = models.CharField(max_length=255, unique=True)
    supplier = models.CharField(max_length=255, blank=True, null=True)
    quantity = models.PositiveIntegerField()
    expiry_date = models.DateField()
    storage_conditions = models.TextField(blank=True, null=True)
    date_received = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name

class KahamaEquipment(models.Model):
    data_recorder = models.ForeignKey('clinic.Staffs', on_delete=models.CASCADE, blank=True, null=True, related_name='kahama_equipment_records')
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
