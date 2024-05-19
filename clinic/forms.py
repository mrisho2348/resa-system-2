from django import forms
from django.core.validators import FileExtensionValidator
from django_ckeditor_5.widgets import CKEditor5Widget

from clinic.models import ImagingRecord, LaboratoryOrder, Procedure, RemoteCounseling, RemoteDischargesNotes, RemoteObservationRecord, RemoteReferral
class ImportStaffForm(forms.Form):
    staff_file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
class ImportDiseaseForm(forms.Form):
    disease_recode_file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
    
class ImportInsuranceCompanyForm(forms.Form):
    insurance_company_file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
class ImportCompanyForm(forms.Form):
    company_file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
class ImportPathologyRecordForm(forms.Form):
    pathology_records_file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
class ImportPatientsForm(forms.Form):
    patient_records_file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
    
class ImportMedicineForm(forms.Form):
    medicine_records_file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
class ImportProcedureForm(forms.Form):
    procedure_records_file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
class ImportReferralForm(forms.Form):
    referral_records_file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
class ImportServiceForm(forms.Form):
    service_records_file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
class ImportCategoryForm(forms.Form):
    category_records_file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
class ImportSupplierForm(forms.Form):
    supplier_records_file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
class ImportInventoryItemForm(forms.Form):
    InventoryItem_records_file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
class ImportEquipmentForm(forms.Form):
    equipment_records_file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
class ImportEquipmentMaintenanceForm(forms.Form):
    maintenance_records_file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
class ImportReagentForm(forms.Form):
    reagent_records_file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
class ImportHealthIssueForm(forms.Form):
    health_records_file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
class ImportPrescriptionForm(forms.Form):
    prescription_records_file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
class ImportPatientVitalForm(forms.Form):
    vital_records_file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
class ImportDiagnosisForm(forms.Form):
    diagnosis_records_file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
class ImportConsultationNotesForm(forms.Form):
    consultation_records_file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
class ImportRemoteServiceForm(forms.Form):
    service_records_file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
class ImportRemotePatientForm(forms.Form):
    patient_records_file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
class ImportCountryForm(forms.Form):
    country_records_file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
class ImportHealthRecordForm(forms.Form):
    health_records_file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
class ImportPrescriptionFrequencyForm(forms.Form):
    records_file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
class ImportAmbulanceRouteForm(forms.Form):
    records_file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
class ImportAmbulanceActivityForm(forms.Form):
    records_file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
class ImportMedicineRouteForm(forms.Form):
    records_file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
class ImportMedicineUnitMeasureForm(forms.Form):
    records_file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
class ImportRemoteMedicineForm(forms.Form):
    records_file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
    


# class RemoteObservationRecordForm(forms.Form):
#     observation_notes = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}))

class RemoteObservationRecordForm(forms.ModelForm):
    """Form for observation notes."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["observation_notes"].required = False

    class Meta:
        model = RemoteObservationRecord
        fields = ("observation_notes",)
        widgets = {
            "observation_notes": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, config_name="extends"
            )
        }
        
        
class RemoteCounselingForm(forms.ModelForm):
    """Form for counseling notes."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["counselling_notes"].required = False

    class Meta:
        model = RemoteCounseling
        fields = ("counselling_notes",)
        widgets = {
            "counselling_notes": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, config_name="extends"
            )
        }   
        

class RemoteReferralForm(forms.ModelForm):
    """Form for remote referrals."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["notes"].required = False

        # Add Bootstrap classes to specific form fields
        self.fields["source_location"].widget.attrs['class'] = 'form-control'
        self.fields["destination_location"].widget.attrs['class'] = 'form-control'
        self.fields["destination_location"].widget.attrs['class'] = 'form-control'
        self.fields["nature_of_referral"].widget.attrs['class'] = 'form-control select2bs4'
        self.fields["transport_model"].widget.attrs['class'] = 'form-control select2bs4'
        
        self.fields["source_location"].widget.attrs['disabled'] = 'disabled'
        self.fields["source_location"].initial = "Default Source Location"

    class Meta:
        model = RemoteReferral
        fields = ['notes', 'destination_location', 'nature_of_referral', 'transport_model', 'destination_location', 'source_location']
        widgets = {
            'notes': CKEditor5Widget(attrs={'class': 'django_ckeditor_5'}, config_name='extends'),
        }
        labels = {
            'notes': 'Referral Reason',
            'source_location': 'Source Location',
            'destination_location': 'Patient Destination',
            'nature_of_referral': 'Nature of Referral',
            'transport_model': 'Transport Model',
            'destination_location': 'Destination Location',
        }
        
class RemoteDischargesNotesForm(forms.ModelForm):
    """Form for remote discharge notes."""
    
    DISCHARGE_CONDITION_CHOICES = [
        ('stable', 'Stable'),
        ('unstable', 'Unstable'),
    ]
    
    discharge_condition = forms.ChoiceField(
        choices=DISCHARGE_CONDITION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["discharge_notes"].required = False
        self.fields["discharge_condition"].widget.attrs.update({'class': 'form-control select2bs4'})

    class Meta:
        model = RemoteDischargesNotes
        fields = ['discharge_condition', 'discharge_notes']
        widgets = {
            'discharge_notes': CKEditor5Widget(attrs={'class': 'django_ckeditor_5'}, config_name='extends'),
        }
  

class ProcedureForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make the 'result' field optional
        self.fields["result"].required = False

    class Meta:
        model = Procedure
        fields = ("result",)
        widgets = {
            "result": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"},  # Add a custom CSS class
                config_name="extends"  # Specify the CKEditor configuration to use
            )
        }
        
class ImagingRecordForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make the 'result' field optional
        self.fields["result"].required = False

    class Meta:
        model = ImagingRecord
        fields = ("result",)
        widgets = {
            "result": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"},  # Add a custom CSS class
                config_name="extends"  # Specify the CKEditor configuration to use
            )
        }
class LaboratoryOrderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make the 'result' field optional
        self.fields["result"].required = False

    class Meta:
        model = LaboratoryOrder
        fields = ("result",)
        widgets = {
            "result": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"},  # Add a custom CSS class
                config_name="extends"  # Specify the CKEditor configuration to use
            )
        }
        
class YearSelectionForm(forms.Form):
    year = forms.IntegerField(label='Year', widget=forms.TextInput(attrs={'class': 'form-control'}))       
#------------------------------
#   Editing existing data