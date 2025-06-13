from datetime import datetime
import re
from django import forms
from django.core.validators import FileExtensionValidator
from django_ckeditor_5.widgets import CKEditor5Widget
from clinic.models import BankAccount, Clients, Counseling, DeductionOrganization, DischargesNotes, Employee, Expense, ExpenseCategory, GovernmentProgram, Grant, ImagingRecord, Investment, LaboratoryOrder, ObservationRecord, Payment, PaymentMethod, Payroll, Procedure, Referral, RemoteCounseling, RemoteDischargesNotes, RemoteObservationRecord, RemoteReferral, SalaryPayment, Staffs
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
        
class ObservationRecordForm(forms.ModelForm):
    """Form for observation notes."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["observation_notes"].required = False

    class Meta:
        model = ObservationRecord
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
          
class CounselingForm(forms.ModelForm):
    """Form for counseling notes."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["counselling_notes"].required = False

    class Meta:
        model = Counseling
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
        self.fields["transport_model"].required = False
        self.fields["source_location"].required = False

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
        
        
class ReferralForm(forms.ModelForm):
    """Form for remote referrals."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["notes"].required = False
        self.fields["transport_model"].required = False
        self.fields["source_location"].required = False

        # Add Bootstrap classes to specific form fields
        self.fields["source_location"].widget.attrs['class'] = 'form-control'
        self.fields["destination_location"].widget.attrs['class'] = 'form-control'
        self.fields["nature_of_referral"].widget.attrs['class'] = 'form-control select2bs4'
        self.fields["transport_model"].widget.attrs['class'] = 'form-control select2bs4'
        
        self.fields["source_location"].widget.attrs['disabled'] = 'disabled'
        self.fields["source_location"].initial = "Default Source Location"

        # Ensure transport_model has the correct initial value
        if 'transport_model' not in self.initial:
            self.initial['transport_model'] = Referral._meta.get_field('transport_model').default

    class Meta:
        model = Referral
        fields = ['notes', 'destination_location', 'nature_of_referral', 'transport_model', 'source_location']
        widgets = {
            'notes': CKEditor5Widget(attrs={'class': 'django_ckeditor_5'}, config_name='extends'),
        }
        labels = {
            'notes': 'Referral Reason',
            'source_location': 'Source Location',
            'destination_location': 'Patient Destination',
            'nature_of_referral': 'Nature of Referral',
            'transport_model': 'Transport Model',
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
        
class DischargesNotesForm(forms.ModelForm):
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
        model = DischargesNotes
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
        
class YearMonthSelectionForm(forms.Form):
    # Generate a list of years: last ten years and future ten years from the current year
    current_year = datetime.now().year
    year_choices = [(year, str(year)) for year in range(current_year - 10, current_year + 1)]
    
    # Months dropdown choices (including 'All months' option)
    month_choices = [
        (0, 'All months'),  # 'None' to represent "All months"
        (1, 'January'), 
        (2, 'February'), 
        (3, 'March'), 
        (4, 'April'),
        (5, 'May'), 
        (6, 'June'), 
        (7, 'July'), 
        (8, 'August'),
        (9, 'September'), 
        (10, 'October'), 
        (11, 'November'), 
        (12, 'December')
    ]
    
    # Year dropdown field
    year = forms.ChoiceField(
        label='Year',
        choices=year_choices,
        widget=forms.Select(attrs={'class': 'form-control select2bs4'})
    )
    
    # Month dropdown field
    month = forms.ChoiceField(
        label='Month',
        choices=month_choices,
        widget=forms.Select(attrs={'class': 'form-control select2bs4'})
    )
    
class BankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = ['bank_name']
        widgets = {
            'bank_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            if BankAccount.objects.exclude(pk=instance.pk).filter(name=name).exists():
                raise forms.ValidationError("A bank account with this name already exists.")
        else:
            if BankAccount.objects.filter(name=name).exists():
                raise forms.ValidationError("A bank account with this name already exists.")
        return name
    
class PayrollForm(forms.ModelForm):
    class Meta:
        model = Payroll
        fields = ['payroll_date', 'total_salary', 'status', 'payment_method', 'details']
        widgets = {
            'payroll_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'total_salary': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control select2bs4'}),
            'payment_method': forms.Select(attrs={'class': 'form-control select2bs4'}),
            'details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        payroll_date = cleaned_data.get('payroll_date')
        payment_method = cleaned_data.get('payment_method')
        instance = self.instance

        # Check if the form is in update mode (instance exists and has an ID)
        if instance and instance.id:
            # Exclude the current instance from the queryset
            existing_payrolls = Payroll.objects.exclude(id=instance.id)
        else:
            existing_payrolls = Payroll.objects.all()

        # Check if a payroll with the same date and payment method already exists
        if existing_payrolls.filter(payroll_date=payroll_date, payment_method=payment_method).exists():
            raise forms.ValidationError("A payroll with this date and payment method already exists.")

        return cleaned_data
    
class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = PaymentMethod
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        instance = self.instance
        if PaymentMethod.objects.filter(name=name).exclude(pk=instance.pk).exists():
            raise forms.ValidationError("A payment method with this name already exists.")
        return name
    
class ExpenseCategoryForm(forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        instance = getattr(self, 'instance', None)
        if instance and ExpenseCategory.objects.filter(name=name).exclude(id=instance.id).exists():
            raise forms.ValidationError("An expense category with this name already exists.")
        return name  

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['date', 'amount', 'description', 'category', 'additional_details', 'receipt']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-control select2bs4'}),
            'additional_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'receipt': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        amount = cleaned_data.get('amount')
        category = cleaned_data.get('category')
        
        # Exclude the current instance from the check if it exists
        qs = Expense.objects.filter(date=date, amount=amount, category=category)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError("An expense with this date, amount, and category already exists.")
        
        return cleaned_data
 
    
class DeductionOrganizationForm(forms.ModelForm):
    class Meta:
        model = DeductionOrganization
        fields = ['name', 'rate', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        instance = getattr(self, 'instance', None)
        if DeductionOrganization.objects.filter(name=name).exclude(pk=instance.pk).exists():
            raise forms.ValidationError("An organization with this name already exists.")
        return name   
    
class EmployeeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EmployeeForm, self).__init__(*args, **kwargs)
        # Filter employee names based on working place
        self.fields['name'].queryset = Staffs.objects.filter(work_place='resa')

    class Meta:
        model = Employee
        fields = [
            'name',  'department', 'employment_type', 'start_date', 'end_date', 
            'salary', 'bank_account', 'bank_account_number', 'account_holder_name', 
            'tin_number', 'nssf_membership_number', 'nhif_number', 'wcf_number',
            'tra_deduction_status', 'nssf_deduction_status', 'wcf_deduction_status', 'heslb_deduction_status'
        ]
        widgets = {
            'name': forms.Select(attrs={'class': 'form-control select2bs4'}),      
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'employment_type': forms.Select(attrs={'class': 'form-control select2bs4'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'salary': forms.NumberInput(attrs={'class': 'form-control'}),
            'bank_account': forms.Select(attrs={'class': 'form-control select2bs4'}),
            'bank_account_number': forms.TextInput(attrs={'class': 'form-control'}),
            'account_holder_name': forms.TextInput(attrs={'class': 'form-control'}),
            'tin_number': forms.TextInput(attrs={'class': 'form-control'}),
            'nssf_membership_number': forms.TextInput(attrs={'class': 'form-control'}),
            'nhif_number': forms.TextInput(attrs={'class': 'form-control'}),
            'wcf_number': forms.TextInput(attrs={'class': 'form-control'}),
            'tra_deduction_status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'nssf_deduction_status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'wcf_deduction_status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'heslb_deduction_status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        employee_id = cleaned_data.get('employee_id')
        
        # Check if the employee_id already exists in other records
        qs = Employee.objects.filter(employee_id=employee_id)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError("An employee with this ID already exists.")
        
        return cleaned_data

    
class SalaryPaymentForm(forms.ModelForm):
    class Meta:
        model = SalaryPayment
        fields = ['employee', 'payroll', 'payment_date', 'payment_status', 'payment_details']
        widgets = {
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'payment_status': forms.Select(attrs={'class': 'form-control select2bs4'}),
            'payment_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].widget.attrs.update({'class': 'form-control select2bs4'})
        self.fields['payroll'].widget.attrs.update({'class': 'form-control select2bs4'})

    def clean(self):
        cleaned_data = super().clean()
        payment_date = cleaned_data.get('payment_date')
        employee = cleaned_data.get('employee')

        if self.instance.pk:
            if SalaryPayment.objects.filter(employee=employee, payment_date=payment_date).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("A salary payment for this employee on the same date already exists.")
        else:
            if SalaryPayment.objects.filter(employee=employee, payment_date=payment_date).exists():
                raise forms.ValidationError("A salary payment for this employee on the same date already exists.")
        
        return cleaned_data

    
class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['date', 'amount', 'method', 'invoice', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget.attrs.update({'class': 'form-control'})
        self.fields['amount'].widget.attrs.update({'class': 'form-control'})
        self.fields['method'].widget.attrs.update({'class': 'form-control select2bs4'})
        self.fields['invoice'].widget.attrs.update({'class': 'form-control select2bs4'})
        self.fields['description'].widget.attrs.update({'class': 'form-control'})    
        
class ClientForm(forms.ModelForm):
    class Meta:
        model = Clients
        fields = ['name', 'email', 'phone_number', 'address', 'contact_person']

    def __init__(self, *args, **kwargs):
        super(ClientForm, self).__init__(*args, **kwargs)
        # Apply Bootstrap classes to each field
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

    def clean_name(self):
        name = self.cleaned_data['name']
        # If instance exists (updating), exclude it from the queryset
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            existing_clients = Clients.objects.exclude(pk=instance.pk)
        else:
            existing_clients = Clients.objects.all()

        if existing_clients.filter(name=name).exists():
            raise forms.ValidationError("A client with this name already exists.")
        return name
      
class InvestmentForm(forms.ModelForm):
    class Meta:
        model = Investment
        fields = ['investment_type', 'amount', 'date', 'description']
        widgets = {
            'investment_type': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }

class GrantForm(forms.ModelForm):
    class Meta:
        model = Grant
        fields = ['grant_name', 'funding_amount', 'donor_name', 'grant_date', 'description']
        widgets = {
            'grant_name': forms.TextInput(attrs={'class': 'form-control'}),
            'funding_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'donor_name': forms.TextInput(attrs={'class': 'form-control'}),
            'grant_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }

class GovernmentProgramForm(forms.ModelForm):
    class Meta:
        model = GovernmentProgram
        fields = ['program_name', 'funding_amount', 'eligibility_criteria', 'description']
        widgets = {
            'program_name': forms.TextInput(attrs={'class': 'form-control'}),
            'funding_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'eligibility_criteria': forms.Textarea(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }      
 
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
        ('specialist', 'Specialist'),
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
WORK_PLACE_CHOICES = [
        ('resa', 'Resa'),
        ('kahama', 'Kahama'),
        # Add more choices as needed
    ]

GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),    
    ]        



class AddStaffForm(forms.Form):
    email = forms.CharField(
        label='Email',
        max_length=50,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Enter Email"})
    )
    password = forms.CharField(
        label='Password',
        max_length=50,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Enter Password"})
    )
    confirm_password = forms.CharField(  # ✅ New field for password confirmation
        label='Confirm Password',
        max_length=50,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirm Password"})
    )
    first_name = forms.CharField(
        label='First Name',
        max_length=50,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter First Name"})
    )
    last_name = forms.CharField(
        label='Last Name',
        max_length=50,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Last Name"})
    )
    username = forms.CharField(
        label='Username',
        max_length=50,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Username"})
    )
    phone_number = forms.CharField(
        label='Phone Number',
        max_length=10,       
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Phone Number"})
    )
    middle_name = forms.CharField(
        label='Middle Name',
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Middle Name"})
    )
    date_of_birth = forms.DateField(
        label='Date of Birth',
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"})
    )
    gender = forms.ChoiceField(
        label='Gender',
        choices=GENDER_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"})
    )
    marital_status = forms.ChoiceField(
        label='Marital Status',
        choices=MARITAL_STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"})
    )
    profession = forms.ChoiceField(
        label='Profession',
        choices=PROFESSION_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"})
    )
    role = forms.ChoiceField(
        label='Role',
        choices=ROLE_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"})
    )
    work_place = forms.ChoiceField(
        label='Work Place',
        choices=WORK_PLACE_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"})
    )
    joining_date = forms.DateField(
        label='Joining Date',
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"})
    )

    # ✅ MCT Number field
    mct_number = forms.CharField(
        label='MCT Number',
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter MCT Number"})
    )

    # ✅ Custom validation to ensure passwords match
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match. Please try again.")

        return cleaned_data

    # Custom validation for phone number (10 digits)
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if phone_number:
            # Check if phone number is 10 digits long
            if not re.match(r'^\d{10}$', phone_number):
                raise forms.ValidationError("Phone number must be exactly 10 digits long.")
        return phone_number


       