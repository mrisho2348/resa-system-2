# pembahmis/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.fields import CKEditor5Field
from django.core.exceptions import ValidationError
from django.utils import timezone
from clinic.models import COVERAGE_CHOICES, NATURE_OF_REFERRAL_CHOICES, TRANSPORT_MODEL_CHOICES, TYPE_CHOICES, Country, PathodologyRecord, Staffs, PrescriptionFrequency, Service

# =========================
# Administrative Models
# =========================

class PembaCompany(models.Model):
    """
    Represents a company or organization associated with Pemba patients.
    """
    name = models.CharField(max_length=255, unique=True, help_text="Name of the company or organization.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Pemba Company"
        verbose_name_plural = "Pemba Companies"

    def __str__(self):
        return self.name

# =========================
# Patient Models
# =========================

def generate_for_pemba_mrn():
    """
    Utility function to generate a unique MRN for Pemba patients.
    """
    last_patient = PembaPatient.objects.order_by('-id').first()
    if last_patient and last_patient.mrn and '-' in last_patient.mrn:
        try:
            last_mrn_number = int(last_patient.mrn.split('-')[-1])
        except (ValueError, IndexError):
            last_mrn_number = 0
    else:
        last_mrn_number = 0
    new_mrn_number = last_mrn_number + 1
    return f"PAT-{new_mrn_number:05d}"

class PembaPatient(models.Model):
    """
    Represents a patient in the Pemba system.
    """
    mrn = models.CharField(max_length=20, unique=True, editable=False, verbose_name='MRN', help_text="Medical Record Number (auto-generated).")
    data_recorder = models.ForeignKey('clinic.Staffs', on_delete=models.SET_NULL, blank=True, null=True, related_name='recorded_pemba_patients', help_text="Staff member who registered the patient.")
    first_name = models.CharField(max_length=100, help_text="Patient's first name.")
    middle_name = models.CharField(max_length=100, blank=True, default="", help_text="Patient's middle name (optional).")
    last_name = models.CharField(max_length=100, help_text="Patient's last name.")
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], help_text="Patient's gender.")
    age = models.PositiveIntegerField(blank=True, null=True, help_text="Patient's age.")
    dob = models.DateField(null=True, blank=True, help_text="Date of birth.")
    nationality = models.ForeignKey('clinic.Country', on_delete=models.PROTECT, help_text="Patient's nationality.")
    phone = models.CharField(max_length=20, help_text="Patient's phone number.")
    osha_certificate = models.BooleanField(default=False, help_text="Whether the patient has an OSHA certificate.")
    date_of_osha_certification = models.DateField(null=True, blank=True, help_text="Date of OSHA certification.")
    insurance = models.CharField(max_length=20, choices=[('Uninsured', 'Uninsured'), ('Insured', 'Insured'), ('Unknown', 'Unknown')], help_text="Insurance status.")
    insurance_company = models.CharField(max_length=100, blank=True, null=True, help_text="Name of the insurance company.")
    other_insurance_company = models.CharField(max_length=100, blank=True, null=True, help_text="Other insurance company (if not listed).")
    insurance_number = models.CharField(max_length=100, blank=True, null=True, help_text="Insurance policy number.")
    emergency_contact_name = models.CharField(max_length=100, help_text="Name of emergency contact.")
    emergency_contact_relation = models.CharField(max_length=100, blank=True, null=True, help_text="Relationship to emergency contact.")
    other_emergency_contact_relation = models.CharField(max_length=100, blank=True, null=True, help_text="Other relationship to emergency contact.")
    emergency_contact_phone = models.CharField(max_length=20, help_text="Phone number of emergency contact.")
    marital_status = models.CharField(max_length=20, choices=[('Single', 'Single'), ('Married', 'Married'), ('Divorced', 'Divorced'), ('Widowed', 'Widowed')], default="Single", help_text="Marital status.")
    occupation = models.CharField(max_length=100, blank=True, null=True, help_text="Patient's occupation.")
    other_occupation = models.CharField(max_length=100, blank=True, null=True, help_text="Other occupation (if not listed).")
    patient_type = models.CharField(max_length=100, blank=True, null=True, help_text="Type of patient.")
    other_patient_type = models.CharField(max_length=100, blank=True, null=True, help_text="Other patient type (if not listed).")
    company = models.ForeignKey('PembaCompany', on_delete=models.PROTECT, help_text="Company or organization associated with the patient.")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At', help_text="Timestamp when the patient was registered.")
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At', help_text="Timestamp when the patient record was last updated.")
    objects = models.Manager()
    @property
    def full_name(self):
        return " ".join(filter(None, [self.first_name, self.middle_name, self.last_name]))
    def save(self, *args, **kwargs):
        if not self.mrn:
            self.mrn = generate_for_pemba_mrn()
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.full_name} ({self.company})"

# =========================
# Clinical Models
# =========================

class PembaHealthRecord(models.Model):
    """
    Represents a health record type/category (e.g., chronic disease, allergy, etc.).
    """
    data_recorder = models.ForeignKey('clinic.Staffs', on_delete=models.CASCADE, blank=True, null=True, related_name='pemba_health_records')
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Pemba Health Record"
        verbose_name_plural = "Pemba Health Records"

    def __str__(self):
        return self.name

class PembaDiagnosis(models.Model):
    """
    Represents a diagnosis entry for a patient in the Pemba system.
    """
    diagnosis_name = models.CharField(max_length=255, unique=True, help_text="Name of the diagnosis (e.g., 'Hypertension').")
    data_recorder = models.ForeignKey('clinic.Staffs', on_delete=models.CASCADE, blank=True, null=True, help_text="Staff member who recorded this diagnosis.")
    diagnosis_code = models.CharField(max_length=20, unique=True, default="", help_text="Unique code for the diagnosis (e.g., ICD-10 code).")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["diagnosis_name"]
        verbose_name = "Pemba Diagnosis"
        verbose_name_plural = "Pemba Diagnoses"

    def __str__(self):
        return f"{self.diagnosis_name} - {self.diagnosis_code}"



# --- Medicine Model ---
class PembaMedicine(models.Model):
    """
    Represents medicines available at pemba locations or partner clinics.
    """
    data_recorder = models.ForeignKey('clinic.Staffs', on_delete=models.CASCADE, blank=True, null=True, related_name='pemba_medicines', help_text="The staff member who recorded this pemba medicine.")
    drug_name = models.CharField(max_length=100, help_text="Name of the medicine or drug.")
    drug_type = models.CharField(max_length=20, blank=True, null=True, help_text="Type of drug (e.g., Tablet, Syrup, Injection).")
    formulation_unit = models.CharField(max_length=50, help_text="Formulation unit (e.g., '500mg', '5ml').")
    dividing_unit = models.PositiveIntegerField(blank=True, null=True, help_text="Smallest divisible unit in mg or ml, e.g., 125.")
    is_dividable = models.BooleanField(default=False, help_text="Is this drug divisible in smaller units?")
    is_clinic_stock = models.BooleanField(default=True, help_text="Is this drug part of clinic stock?")
    manufacturer = models.CharField(max_length=100, blank=True, null=True, help_text="Manufacturer of the medicine.")
    quantity = models.PositiveIntegerField(blank=True, null=True, help_text="Total quantity available.")
    remain_quantity = models.PositiveIntegerField(blank=True, null=True, help_text="Remaining quantity in stock.")
    batch_number = models.CharField(max_length=20, unique=True, blank=True, null=True, help_text="Batch number for tracking.")
    expiration_date = models.DateField(blank=True, null=True, help_text="Expiration date of the medicine.")
    minimum_stock_level = models.PositiveIntegerField(default=0, help_text="Minimum threshold before restocking.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the pemba medicine was added.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp when the pemba medicine was last updated.")
    objects = models.Manager()
    class Meta:
        verbose_name = "Pemba Medicine"
        verbose_name_plural = "Pemba Medicines"
        ordering = ["drug_name"]
    def __str__(self) -> str:
        return self.drug_name
    def clean(self) -> None:
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

# --- Patient Medication Allergy ---
class PembaPatientMedicationAllergy(models.Model):
    data_recorder = models.ForeignKey('clinic.Staffs', on_delete=models.SET_NULL, blank=True, null=True, related_name='patient_medication_allergies', help_text="Staff member who recorded the allergy.")
    patient = models.ForeignKey('pembahmis.PembaPatient', on_delete=models.CASCADE, related_name='medication_allergies', help_text="Patient with the medication allergy.")
    medicine = models.ForeignKey('PembaMedicine', on_delete=models.CASCADE, related_name='allergy_records', help_text="Medicine to which the patient is allergic.")
    reaction = models.CharField(max_length=200, help_text="Description of the allergic reaction.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the allergy was recorded.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp when the allergy record was last updated.")
    def __str__(self):
        return f"{self.patient} - {self.medicine} ({self.reaction})"

# --- Patient Surgery ---
class PembaPatientSurgery(models.Model):
    data_recorder = models.ForeignKey('clinic.Staffs', on_delete=models.SET_NULL, blank=True, null=True, related_name='patient_surgeries', help_text="Staff member who recorded the surgery.")
    patient = models.ForeignKey('pembahmis.PembaPatient', on_delete=models.CASCADE, related_name='surgeries', help_text="Patient who underwent the surgery.")
    surgery_name = models.CharField(max_length=100, blank=True, null=True, help_text="Name of the surgery.")
    surgery_date = models.DateField(blank=True, null=True, help_text="Date when the surgery was performed.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the surgery record was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp when the surgery record was last updated.")
    objects = models.Manager()
    def __str__(self):
        return f"{self.patient} - {self.surgery_name} ({self.surgery_date})"

# --- Patient Lifestyle Behavior ---
class PembaPatientLifestyleBehavior(models.Model):
    data_recorder = models.ForeignKey('clinic.Staffs', on_delete=models.SET_NULL, blank=True, null=True, related_name='patient_lifestyle_behaviors', help_text="Staff member who recorded the lifestyle behavior.")
    patient = models.OneToOneField('pembahmis.PembaPatient', on_delete=models.CASCADE, related_name='lifestyle_behavior', help_text="Patient whose lifestyle is being recorded.")
    weekly_exercise_frequency = models.CharField(max_length=32, blank=True, null=True, help_text="How often the patient exercises per week.")
    smoking = models.CharField(max_length=32, blank=True, null=True, help_text="Smoking status of the patient.")
    alcohol_consumption = models.CharField(max_length=32, blank=True, null=True, help_text="Alcohol consumption status.")
    healthy_diet = models.CharField(max_length=32, blank=True, null=True, help_text="Whether the patient follows a healthy diet.")
    stress_management = models.CharField(max_length=32, blank=True, null=True, help_text="Patient's stress management habits.")
    sufficient_sleep = models.CharField(max_length=32, blank=True, null=True, help_text="Whether the patient gets sufficient sleep.")
    def __str__(self):
        return f"Lifestyle for {self.patient}"

# --- Utility function for MRN ---
def generate_for_pemba_mrn():
    last_patient = PembaPatient.objects.order_by('-id').first()
    if last_patient and last_patient.mrn and '-' in last_patient.mrn:
        try:
            last_mrn_number = int(last_patient.mrn.split('-')[-1])
        except (ValueError, IndexError):
            last_mrn_number = 0
    else:
        last_mrn_number = 0
    new_mrn_number = last_mrn_number + 1
    return f"PAT-{new_mrn_number:05d}"

# --- Patient Health Condition ---
class PembaPatientHealthCondition(models.Model):
    patient = models.ForeignKey('pembahmis.PembaPatient', on_delete=models.CASCADE, related_name='health_conditions', verbose_name='Patient', help_text="Patient with the health condition.")
    data_recorder = models.ForeignKey('clinic.Staffs', on_delete=models.SET_NULL, blank=True, null=True, related_name='recorded_health_conditions', help_text="Staff member who recorded the health condition.")
    health_condition = models.CharField(max_length=200, blank=True, null=True, verbose_name='Health Condition', help_text="Name of the health condition.")
    health_condition_notes = models.CharField(max_length=200, blank=True, null=True, verbose_name='Health Condition Notes', help_text="Additional notes about the health condition.")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At', help_text="Timestamp when the health condition was recorded.")
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At', help_text="Timestamp when the health condition was last updated.")
    objects = models.Manager()
    def __str__(self):
        return f"{self.patient} - {self.health_condition}"

# --- Family Medical History ---
class PembaFamilyMedicalHistory(models.Model):
    patient = models.ForeignKey('pembahmis.PembaPatient', on_delete=models.CASCADE, related_name='family_medical_history', verbose_name='Patient', help_text="Patient whose family history is being recorded.")
    data_recorder = models.ForeignKey('clinic.Staffs', on_delete=models.SET_NULL, blank=True, null=True, related_name='recorded_family_histories', help_text="Staff member who recorded the family history.")
    condition = models.CharField(max_length=100, verbose_name='Condition', help_text="Medical condition present in the family.")
    relationship = models.CharField(max_length=100, blank=True, null=True, verbose_name='Relationship', help_text="Relationship of the family member to the patient.")
    comments = models.CharField(max_length=100, blank=True, null=True, verbose_name='Comments', help_text="Additional comments.")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At', help_text="Timestamp when the family history was recorded.")
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At', help_text="Timestamp when the family history was last updated.")
    objects = models.Manager()
    def __str__(self):
        return f"{self.patient} - {self.condition}"

# --- Service Model ---
class PembaService(models.Model):
    name = models.CharField(max_length=225, unique=True, help_text="Name of the pemba service.")
    data_recorder = models.ForeignKey('clinic.Staffs', on_delete=models.SET_NULL, blank=True, null=True, related_name='pemba_services', help_text="Staff member who created the service record.")
    description = models.TextField(default="", help_text="Description of the service.")
    category = models.CharField(max_length=50, null=True, blank=True, help_text="Category of the service.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the service was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp when the service was last updated.")
    objects = models.Manager()
    def __str__(self):
        return f"{self.name} ({self.category})"

# --- Patient Visits ---
class PembaPatientVisits(models.Model):
    VISIT_TYPES = (
        ('Normal', _('Normal')),
        ('Emergency', _('Emergency')),
        ('Referral', _('Referral')),
        ('Follow up', _('Follow up')),
    )
    data_recorder = models.ForeignKey('clinic.Staffs', on_delete=models.SET_NULL, blank=True, null=True, related_name='pemba_patient_visits', help_text="Staff member who recorded the visit.")
    patient = models.ForeignKey('pembahmis.PembaPatient', on_delete=models.CASCADE, related_name='visits', help_text="Patient attending the visit.")
    vst = models.CharField(max_length=20, unique=True, editable=False, help_text="Visit serial number (auto-generated).")
    visit_type = models.CharField(max_length=15, choices=VISIT_TYPES, help_text="Type of the visit.")
    primary_service = models.CharField(max_length=50, help_text="Primary service for the visit.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the visit was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp when the visit was last updated.")
    class Meta:
        verbose_name = _('Visit')
        verbose_name_plural = _('Visits')
        ordering = ['-created_at']
    def save(self, *args, **kwargs):
        if not self.vst:
            self.vst = pembagenerate_vst()
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.patient.full_name} - {self.get_visit_type_display()}"

def pembagenerate_vst():
    last_visit = PembaPatientVisits.objects.order_by('-id').first()
    if last_visit and last_visit.vst and '-' in last_visit.vst:
        try:
            last_vst_number = int(last_visit.vst.split('-')[-1])
        except (ValueError, IndexError):
            last_vst_number = 0
    else:
        last_vst_number = 0
    new_vst_number = last_vst_number + 1
    return f"VST-{new_vst_number:07d}"

# --- Patient Vital ---
class PembaPatientVital(models.Model):
    patient = models.ForeignKey('pembahmis.PembaPatient', on_delete=models.CASCADE, related_name='vitals', help_text="Patient whose vitals are recorded.")
    visit = models.ForeignKey('PembaPatientVisits', on_delete=models.CASCADE, related_name='vitals', help_text="Visit during which vitals were recorded.")
    doctor = models.ForeignKey('clinic.Staffs', on_delete=models.SET_NULL, blank=True, null=True, related_name='recorded_vitals', help_text="Doctor who recorded the vitals.")
    recorded_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the vitals were recorded.")
    respiratory_rate = models.PositiveIntegerField(null=True, blank=True, help_text="Respiratory rate (breaths per minute).")
    pulse_rate = models.PositiveIntegerField(null=True, blank=True, help_text="Pulse rate (beats per minute).")
    sbp = models.PositiveIntegerField(null=True, blank=True, help_text="Systolic Blood Pressure (mmHg).")
    dbp = models.PositiveIntegerField(null=True, blank=True, help_text="Diastolic Blood Pressure (mmHg).")
    blood_pressure = models.CharField(max_length=7, null=True, blank=True, help_text="Blood pressure in format 'SBP/DBP'.")
    spo2 = models.PositiveIntegerField(null=True, blank=True, help_text="Oxygen saturation (SPO2) in percent.")
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, default=37.5, help_text="Body temperature in Celsius.")
    gcs = models.PositiveIntegerField(null=True, blank=True, help_text="Glasgow Coma Scale score.")
    avpu = models.CharField(max_length=20, null=True, blank=True, help_text="AVPU scale value.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp when the vitals were last updated.")
    objects = models.Manager()
    def __str__(self):
        return f"Vitals for {self.patient.full_name} at {self.recorded_at}"

# --- Patient Diagnosis Record ---
class PembaPatientDiagnosisRecord(models.Model):
    visit = models.ForeignKey('PembaPatientVisits', on_delete=models.CASCADE, related_name='diagnosis_records', help_text="Visit associated with the diagnosis.")
    patient = models.ForeignKey('pembahmis.PembaPatient', on_delete=models.CASCADE, related_name='diagnosis_records', help_text="Patient for whom the diagnosis is recorded.")
    data_recorder = models.ForeignKey('clinic.Staffs', on_delete=models.SET_NULL, blank=True, null=True, related_name='recorded_diagnosis_records', help_text="Staff member who recorded the diagnosis.")
    provisional_diagnosis = models.ManyToManyField('PembaDiagnosis', related_name='pemba_provisional_diagnosis_records', help_text="Provisional diagnoses.")
    final_diagnosis = models.ManyToManyField('PembaDiagnosis', related_name='pemba_final_diagnosis_records', help_text="Final diagnoses.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the diagnosis record was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp when the diagnosis record was last updated.")
    objects = models.Manager()
    def __str__(self):
        provisional = ", ".join([str(d) for d in self.provisional_diagnosis.all()])
        final = ", ".join([str(d) for d in self.final_diagnosis.all()])
        return f"Patient: {self.patient.full_name} | Provisional: [{provisional}] | Final: [{final}]"

# --- Consultation Notes ---
class PembaConsultationNotes(models.Model):
    doctor = models.ForeignKey('clinic.Staffs', on_delete=models.PROTECT, related_name='pemba_consultation_notes', help_text="Doctor who wrote the consultation notes.")
    patient = models.ForeignKey('pembahmis.PembaPatient', on_delete=models.CASCADE, related_name='consultation_notes', help_text="Patient for whom the notes are written.")
    visit = models.ForeignKey('PembaPatientVisits', on_delete=models.CASCADE, null=True, blank=True, related_name='consultation_notes', help_text="Visit associated with the consultation notes.")
    history_of_presenting_illness = models.TextField(null=True, blank=True, help_text="History of presenting illness.")
    review_of_systems = models.TextField(null=True, blank=True, help_text="Review of systems.")
    physical_examination = models.TextField(null=True, blank=True, help_text="Physical examination findings.")
    doctor_plan = models.TextField(help_text="Doctor's plan.")
    doctor_plan_note = models.TextField(null=True, blank=True, help_text="Additional notes on the doctor's plan.")
    pathology = models.ManyToManyField('clinic.PathodologyRecord', blank=True, help_text="Pathology records associated with the consultation.")
    allergy_summary = models.TextField(null=True, blank=True, help_text="Summary of allergies.")
    known_comorbidities_summary = models.TextField(null=True, blank=True, help_text="Summary of known comorbidities.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the consultation notes were created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp when the consultation notes were last updated.")
    objects = models.Manager()
    def __str__(self):
        return f"Consultation for {self.patient.full_name} by Dr. {self.doctor}"

# --- Observation Record ---
class PembaObservationRecord(models.Model):
    patient = models.ForeignKey('pembahmis.PembaPatient', on_delete=models.CASCADE, related_name='observation_records', help_text="Patient for whom the observation is recorded.")
    visit = models.ForeignKey('PembaPatientVisits', on_delete=models.CASCADE, related_name='observation_records', help_text="Visit associated with the observation.")
    data_recorder = models.ForeignKey('clinic.Staffs', on_delete=models.SET_NULL, blank=True, null=True, related_name='recorded_observations', help_text="Staff member who recorded the observation.")
    observation_notes = CKEditor5Field(config_name='extends', blank=True, null=True, help_text="Observation notes.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the observation was recorded.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp when the observation was last updated.")
    objects = models.Manager()
    def __str__(self):
        return f"Observation for {self.patient.full_name} ({self.data_recorder})"



# --- Imaging Record ---
class PembaImagingRecord(models.Model):
    patient = models.ForeignKey('pembahmis.PembaPatient', on_delete=models.CASCADE, related_name='imaging_records', help_text="Patient for whom the imaging was performed.")
    visit = models.ForeignKey('PembaPatientVisits', on_delete=models.CASCADE, related_name='imaging_records', help_text="Visit associated with the imaging.")
    data_recorder = models.ForeignKey('clinic.Staffs', on_delete=models.SET_NULL, blank=True, null=True, related_name='recorded_imaging', help_text="Staff member who recorded the imaging.")
    imaging = models.ForeignKey('clinic.Service', on_delete=models.SET_NULL, blank=True, null=True, related_name='pemba_imaging_records', help_text="Imaging service performed.")
    description = models.TextField(blank=True, null=True, help_text="Description of the imaging.")
    result = models.TextField(null=True, blank=True, help_text="Result of the imaging.")
    image = models.ImageField(upload_to='imaging_records/', null=True, blank=True, help_text="Image file of the imaging result.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the imaging record was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp when the imaging record was last updated.")
    objects = models.Manager()
    def __str__(self):
        return f"Imaging Record for {self.patient.full_name} - {self.imaging} ({self.data_recorder})"

# --- Laboratory Request ---
class PembaLaboratoryRequest(models.Model):
    patient = models.ForeignKey('pembahmis.PembaPatient', on_delete=models.CASCADE, related_name='laboratory_requests', help_text="Patient for whom the laboratory request is made.")
    visit = models.ForeignKey('PembaPatientVisits', on_delete=models.CASCADE, blank=True, null=True, related_name='laboratory_requests', help_text="Visit associated with the laboratory request.")
    data_recorder = models.ForeignKey('clinic.Staffs', on_delete=models.SET_NULL, blank=True, null=True, related_name='recorded_lab_requests', help_text="Staff member who recorded the laboratory request.")
    name = models.ForeignKey('PembaService', on_delete=models.SET_NULL, blank=True, null=True, related_name='laboratory_requests', help_text="Laboratory service requested.")
    result = CKEditor5Field(config_name='extends', blank=True, null=True, help_text="Result of the laboratory test.")
    lab_number = models.CharField(max_length=20, unique=True, help_text="Laboratory request number (auto-generated).")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the laboratory request was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp when the laboratory request was last updated.")
    objects = models.Manager()
    def __str__(self):
        return f"Laboratory Request: {self.name} for {self.patient.full_name}"
    def save(self, *args, **kwargs):
        if not self.lab_number:
            last_lab = PembaLaboratoryRequest.objects.order_by('-id').first()
            if last_lab and last_lab.lab_number and '-' in last_lab.lab_number:
                try:
                    last_number = int(last_lab.lab_number.split('-')[-1])
                except (ValueError, IndexError):
                    last_number = 0
            else:
                last_number = 0
            self.lab_number = f"LAB-{last_number + 1:07d}"
        super().save(*args, **kwargs)

# --- Procedure ---
class PembaProcedure(models.Model):
    patient = models.ForeignKey('pembahmis.PembaPatient', on_delete=models.CASCADE, related_name='procedures', help_text="Patient who underwent the procedure.")
    doctor = models.ForeignKey('clinic.Staffs', on_delete=models.SET_NULL, blank=True, null=True, related_name='performed_procedures', help_text="Doctor who performed the procedure.")
    visit = models.ForeignKey('PembaPatientVisits', on_delete=models.CASCADE, related_name='procedures', help_text="Visit associated with the procedure.")
    name = models.ForeignKey('PembaService', on_delete=models.SET_NULL, blank=True, null=True, related_name='procedure_records', help_text="Name of the procedure.")
    description = models.TextField(help_text="Description of the procedure.")
    result = CKEditor5Field(config_name='extends', blank=True, null=True, help_text="Result of the procedure.")
    image = models.ImageField(upload_to='procedure_images/', blank=True, null=True, help_text="Image related to the procedure.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the procedure was recorded.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp when the procedure record was last updated.")
    objects = models.Manager()
    def __str__(self):
        return f"Procedure: {self.name} for {self.patient.full_name}"

# --- Consultation ---
class PembaAppointment(models.Model):
    data_recorder = models.ForeignKey('clinic.Staffs', on_delete=models.SET_NULL, blank=True, null=True, related_name='recorded_pemba_consultations', help_text="Staff member who recorded the consultation.")
    doctor = models.ForeignKey('clinic.Staffs', on_delete=models.PROTECT, related_name='pemba_consultations', help_text="Doctor assigned to the consultation.")
    patient = models.ForeignKey('pembahmis.PembaPatient', on_delete=models.CASCADE, related_name='consultations', help_text="Patient for whom the consultation is scheduled.")
    visit = models.ForeignKey('PembaPatientVisits', on_delete=models.CASCADE, blank=True, null=True, related_name='consultations', help_text="Visit associated with the consultation.")
    created_by = models.ForeignKey('clinic.Staffs', on_delete=models.SET_NULL, blank=True, null=True, related_name='created_pemba_consultations', help_text="Staff member who created the consultation record.")
    appointment_date = models.DateField(help_text="Date of the consultation appointment.")
    start_time = models.TimeField(blank=True, null=True, help_text="Start time of the consultation.")
    end_time = models.TimeField(blank=True, null=True, help_text="End time of the consultation.")
    description = models.TextField(blank=True, null=True, help_text="Description or notes for the consultation.")
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
    status = models.IntegerField(choices=STATUS_CHOICES, default=0, help_text="Status of the consultation.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the consultation was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp when the consultation was last updated.")
    objects = models.Manager()
    def __str__(self):
        doctor_name = f"{self.doctor.admin.first_name} {self.doctor.middle_name} {self.doctor.admin.last_name}" if hasattr(self.doctor, 'admin') else str(self.doctor)
        return f"Appointment with {doctor_name} for {self.patient.full_name} on {self.appointment_date} from {self.start_time} to {self.end_time}"

# --- Counseling ---
class PembaCounseling(models.Model):
    data_recorder = models.ForeignKey('clinic.Staffs', on_delete=models.SET_NULL, blank=True, null=True, related_name='recorded_pemba_counselings', help_text="Staff member who recorded the counseling.")
    counselling_notes = CKEditor5Field(config_name='extends', blank=True, null=True, help_text="Counseling notes.")
    patient = models.ForeignKey('pembahmis.PembaPatient', on_delete=models.CASCADE, related_name='counselings', help_text="Patient who received counseling.")
    visit = models.ForeignKey('PembaPatientVisits', on_delete=models.CASCADE, blank=True, null=True, related_name='counselings', help_text="Visit associated with the counseling.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the counseling was recorded.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp when the counseling record was last updated.")
    objects = models.Manager()
    def __str__(self):
        return f"Counseling for {self.patient.full_name}"

# --- Discharges Notes ---
class PembaDischargesNotes(models.Model):
    data_recorder = models.ForeignKey('clinic.Staffs', on_delete=models.SET_NULL, blank=True, null=True, related_name='recorded_pemba_discharges', help_text="Staff member who recorded the discharge.")
    discharge_condition = models.CharField(max_length=255, help_text="Condition of the patient at discharge.")
    discharge_notes = CKEditor5Field(config_name='extends', blank=True, null=True, help_text="Discharge notes.")
    patient = models.ForeignKey('pembahmis.PembaPatient', on_delete=models.CASCADE, related_name='discharge_notes', help_text="Patient being discharged.")
    visit = models.ForeignKey('PembaPatientVisits', on_delete=models.CASCADE, blank=True, null=True, related_name='discharge_notes', help_text="Visit associated with the discharge.")
    discharge_date = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the patient was discharged.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp when the discharge record was last updated.")
    objects = models.Manager()
    def __str__(self):
        return f"Discharge notes for {self.patient.full_name}"

# --- Referral ---
class PembaReferral(models.Model):
    patient = models.ForeignKey('pembahmis.PembaPatient', on_delete=models.CASCADE, related_name='referrals', help_text="Patient being referred.")
    visit = models.ForeignKey('PembaPatientVisits', on_delete=models.CASCADE, blank=True, null=True, related_name='referrals', help_text="Visit associated with the referral.")
    data_recorder = models.ForeignKey('clinic.Staffs', on_delete=models.SET_NULL, blank=True, null=True, related_name='recorded_pemba_referrals', help_text="Staff member who recorded the referral.")
    source_location = models.CharField(max_length=255, default="resa medical hospital", help_text="Source location of the patient.")
    destination_location = models.CharField(max_length=255, help_text="Destination location for MedEvac.")
    rfn = models.CharField(max_length=20, unique=True, editable=False, help_text="Referral number (auto-generated).")
    notes = CKEditor5Field(config_name='extends', blank=True, null=True, help_text="Referral notes.")
    nature_of_referral = models.CharField(max_length=20, choices=NATURE_OF_REFERRAL_CHOICES, default='Referred', help_text="Nature of the referral.")
    transport_model = models.CharField(max_length=50, choices=TRANSPORT_MODEL_CHOICES, default='Ground Ambulance', help_text="Mode of transport for the referral.")
    REFERRAL_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    status = models.CharField(max_length=20, choices=REFERRAL_STATUS_CHOICES, default='pending', help_text="Status of the referral.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the referral was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp when the referral was last updated.")
    objects = models.Manager()
    def save(self, *args, **kwargs):
        if not self.rfn:
            last_referral = PembaReferral.objects.order_by('-id').first()
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

# --- Chief Complaint ---
class PembaChiefComplaint(models.Model):
    data_recorder = models.ForeignKey('clinic.Staffs', on_delete=models.CASCADE, blank=True, null=True, related_name='chief_complaints', help_text="The staff member who recorded this chief complaint.")
    patient = models.ForeignKey('pembahmis.PembaPatient', on_delete=models.CASCADE, help_text="The pemba patient reporting the chief complaint.")
    visit = models.ForeignKey('PembaPatientVisits', on_delete=models.CASCADE, blank=True, null=True, help_text="The visit associated with this chief complaint.")
    health_record = models.ForeignKey('PembaHealthRecord', on_delete=models.CASCADE, blank=True, null=True, help_text="The health record associated with this complaint.")
    other_complaint = models.CharField(max_length=100, help_text="Description of the chief complaint or other symptoms.")
    duration = models.CharField(max_length=100, help_text="Duration of the complaint or symptoms.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the chief complaint was recorded.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp when the chief complaint was last updated.")
    objects = models.Manager()
    class Meta:
        verbose_name = "Chief Complaint"
        verbose_name_plural = "Chief Complaints"
        ordering = ["-created_at"]
    def __str__(self) -> str:
        if self.health_record:
            return f"{self.health_record.name} - {self.duration}"
        return f"Chief Complaint: {self.other_complaint} ({self.duration})"
    def clean(self) -> None:
        if not self.other_complaint.strip():
            raise ValidationError({"other_complaint": "Chief complaint description cannot be empty."})
        if not self.duration.strip():
            raise ValidationError({"duration": "Duration cannot be empty."})

# --- Prescription ---
class PembaPrescription(models.Model):
    patient = models.ForeignKey('pembahmis.PembaPatient', on_delete=models.CASCADE, related_name="pemba_prescriptions", help_text="The pemba patient to whom this prescription belongs.")
    visit = models.ForeignKey('PembaPatientVisits', on_delete=models.CASCADE, related_name="prescriptions", help_text="The pemba patient visit associated with this prescription.")
    medicine = models.ForeignKey('PembaMedicine', on_delete=models.PROTECT, related_name="prescriptions", help_text="The medicine prescribed to the patient.")
    frequency = models.ForeignKey('clinic.PrescriptionFrequency', on_delete=models.SET_NULL, blank=True, null=True, related_name="pemba_prescriptions", help_text="Frequency at which the medicine should be taken.")
    entered_by = models.ForeignKey('clinic.Staffs', on_delete=models.SET_NULL, blank=True, null=True, related_name="entered_pemba_prescriptions", help_text="Staff member who entered the prescription.")
    prs_no = models.CharField(max_length=20, unique=True, editable=False, help_text="Unique prescription number, auto-generated.")
    dose = models.CharField(max_length=50, help_text="Dosage instructions for the medicine (e.g., '1 tablet', '10ml').")
    duration = models.CharField(max_length=50, help_text="Duration for which the medicine should be taken (e.g., '7 days', '2 weeks').")
    quantity_used = models.PositiveIntegerField(help_text="Quantity of the medicine prescribed.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the prescription was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp when the prescription was last updated.")
    class Meta:
        verbose_name = "Pemba Prescription"
        verbose_name_plural = "Pemba Prescriptions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['patient', 'visit']),
            models.Index(fields=['prs_no']),
            models.Index(fields=['created_at']),
        ]
    def save(self, *args, **kwargs):
        if not self.prs_no:
            self.prs_no = self._generate_prescription_id()
        super().save(*args, **kwargs)
    def _generate_prescription_id(self):
        last_prescription = PembaPrescription.objects.order_by('-id').first()
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
        return f"Prescription for {self.patient.full_name} - {self.medicine.drug_name} (PRS No: {self.prs_no})"
    def get_total_cost(self):
        if hasattr(self.medicine, 'unit_price'):
            return self.medicine.unit_price * self.quantity_used
        return 0
    def is_active(self):
        return True

def generate_pembaprescription_id():
    last_prescription = PembaPrescription.objects.order_by('-id').first()
    if last_prescription and last_prescription.prs_no and last_prescription.prs_no.startswith("PRS-"):
        try:
            last_number = int(last_prescription.prs_no.split('-')[-1])
        except (ValueError, IndexError):
            last_number = 0
    else:
        last_number = 0
    new_number = last_number + 1
    return f"PRS-{new_number:07d}"

class PembaEquipment(models.Model):
    data_recorder = models.ForeignKey('clinic.Staffs', on_delete=models.CASCADE, blank=True, null=True, related_name='pemba_equipment_records')
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


class PembaReagent(models.Model):
    data_recorder = models.ForeignKey('clinic.Staffs', on_delete=models.CASCADE, blank=True, null=True, related_name='pemba_reagent_records')
    name = models.CharField(max_length=255, unique=True)
    supplier = models.CharField(max_length=255, blank=True, null=True)
    quantity = models.PositiveIntegerField()
    expiry_date = models.DateField()
    storage_conditions = models.TextField(blank=True, null=True)
    date_received = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name