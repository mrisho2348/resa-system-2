from datetime import datetime
import re
from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
from clinic.models import (
    # Financial models
    BankAccount, Expense, ExpenseCategory, GovernmentProgram, Grant, Investment, Payroll, Payment, PaymentMethod, SalaryPayment,
    # Staff and HR models
    Clients, Counseling, DeductionOrganization, DischargesNotes, Employee,  Staffs,
    # Medical/Clinical models
      ImagingRecord, LaboratoryOrder,  ObservationRecord, Procedure, Referral)


# --- Model Form Mixins for DRYness ---
class CKEditorOptionalFieldMixin:
    ckeditor_field = None
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.ckeditor_field:
            self.fields[self.ckeditor_field].required = False

# --- LaboratoryOrderForm, ProcedureForm, ImagingRecordForm ---
class LaboratoryOrderForm(CKEditorOptionalFieldMixin, forms.ModelForm):
    ckeditor_field = "result"
    class Meta:
        model = LaboratoryOrder
        fields = ("result",)
        widgets = {
            "result": CKEditor5Widget(attrs={"class": "django_ckeditor_5"}, config_name="extends")
        }

class ProcedureForm(CKEditorOptionalFieldMixin, forms.ModelForm):
    ckeditor_field = "result"
    class Meta:
        model = Procedure
        fields = ("result",)
        widgets = {
            "result": CKEditor5Widget(attrs={"class": "django_ckeditor_5"}, config_name="extends")
        }

class ImagingRecordForm(CKEditorOptionalFieldMixin, forms.ModelForm):
    ckeditor_field = "result"
    class Meta:
        model = ImagingRecord
        fields = ("result",)
        widgets = {
            "result": CKEditor5Widget(attrs={"class": "django_ckeditor_5"}, config_name="extends")
        }



class ObservationRecordForm(CKEditorOptionalFieldMixin, forms.ModelForm):
    ckeditor_field = "observation_notes"
    class Meta:
        model = ObservationRecord
        fields = ("observation_notes",)
        widgets = {
            "observation_notes": CKEditor5Widget(attrs={"class": "django_ckeditor_5"}, config_name="extends")
        }

class RemoteCounselingForm(CKEditorOptionalFieldMixin, forms.ModelForm):
    ckeditor_field = "counselling_notes"
    class Meta:
        model = Counseling
        fields = ("counselling_notes",)
        widgets = {
            "counselling_notes": CKEditor5Widget(attrs={"class": "django_ckeditor_5"}, config_name="extends")
        }

class CounselingForm(CKEditorOptionalFieldMixin, forms.ModelForm):
    ckeditor_field = "counselling_notes"
    class Meta:
        model = Counseling
        fields = ("counselling_notes",)
        widgets = {
            "counselling_notes": CKEditor5Widget(attrs={"class": "django_ckeditor_5"}, config_name="extends")
        }


class ReferralForm(forms.ModelForm):
    """Form for referrals."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ["source_location", "destination_location"]:
            self.fields[field].widget.attrs['class'] = 'form-control'
        self.fields["nature_of_referral"].widget.attrs['class'] = 'form-control select2bs4'
        self.fields["transport_model"].widget.attrs['class'] = 'form-control select2bs4'
        self.fields["notes"].required = False
        self.fields["transport_model"].required = False
        self.fields["source_location"].required = False
        self.fields["source_location"].widget.attrs['disabled'] = 'disabled'
        self.fields["source_location"].initial = "Default Source Location"
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

# --- Discharge Notes Forms ---
class RemoteDischargesNotesForm(forms.ModelForm):
    DISCHARGE_CONDITION_CHOICES = [
        ('stable', 'Stable'),
        ('unstable', 'Unstable'),
    ]
    discharge_condition = forms.ChoiceField(
        choices=DISCHARGE_CONDITION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control select2bs4'})
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["discharge_notes"].required = False

    class Meta:
        model = DischargesNotes
        fields = ['discharge_condition', 'discharge_notes']
        widgets = {
            'discharge_notes': CKEditor5Widget(attrs={'class': 'django_ckeditor_5'}, config_name='extends'),
        }

class DischargesNotesForm(forms.ModelForm):
    DISCHARGE_CONDITION_CHOICES = [
        ('stable', 'Stable'),
        ('unstable', 'Unstable'),
    ]
    discharge_condition = forms.ChoiceField(
        choices=DISCHARGE_CONDITION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control select2bs4'})
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["discharge_notes"].required = False

    class Meta:
        model = DischargesNotes
        fields = ['discharge_condition', 'discharge_notes']
        widgets = {
            'discharge_notes': CKEditor5Widget(attrs={'class': 'django_ckeditor_5'}, config_name='extends'),
        }

# --- Year/Month Selection Form ---
class YearMonthSelectionForm(forms.Form):
    current_year = datetime.now().year
    year_choices = [(year, str(year)) for year in range(current_year - 10, current_year + 1)]
    month_choices = [
        (0, 'All months'),
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
    ]
    year = forms.ChoiceField(
        label='Year',
        choices=year_choices,
        widget=forms.Select(attrs={'class': 'form-control select2bs4'})
    )
    month = forms.ChoiceField(
        label='Month',
        choices=month_choices,
        widget=forms.Select(attrs={'class': 'form-control select2bs4'})
    )
    def clean_month(self):
        return int(self.cleaned_data['month'])
    def clean_year(self):
        return int(self.cleaned_data['year'])

# --- BankAccountForm ---
class BankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = ['bank_name']
        widgets = {
            'bank_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
    def clean_bank_name(self):
        name = self.cleaned_data['bank_name']
        instance = getattr(self, 'instance', None)
        qs = BankAccount.objects.filter(bank_name=name)
        if instance and instance.pk:
            qs = qs.exclude(pk=instance.pk)
        if qs.exists():
            raise forms.ValidationError("A bank account with this name already exists.")
        return name

# --- PayrollForm ---
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
        qs = Payroll.objects.all()
        if instance and instance.pk:
            qs = qs.exclude(pk=instance.pk)
        if payroll_date and payment_method and qs.filter(payroll_date=payroll_date, payment_method=payment_method).exists():
            raise forms.ValidationError("A payroll with this date and payment method already exists.")
        return cleaned_data

# --- PaymentMethodForm ---
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
        qs = PaymentMethod.objects.filter(name=name)
        if instance and instance.pk:
            qs = qs.exclude(pk=instance.pk)
        if qs.exists():
            raise forms.ValidationError("A payment method with this name already exists.")
        return name

# --- ExpenseCategoryForm ---
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
        qs = ExpenseCategory.objects.filter(name=name)
        if instance and instance.pk:
            qs = qs.exclude(pk=instance.pk)
        if qs.exists():
            raise forms.ValidationError("An expense category with this name already exists.")
        return name

# --- ExpenseForm ---
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
        qs = Expense.objects.filter(date=date, amount=amount, category=category)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("An expense with this date, amount, and category already exists.")
        return cleaned_data

# --- DeductionOrganizationForm ---
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
        qs = DeductionOrganization.objects.filter(name=name)
        if instance and instance.pk:
            qs = qs.exclude(pk=instance.pk)
        if qs.exists():
            raise forms.ValidationError("An organization with this name already exists.")
        return name

# --- EmployeeForm ---
class EmployeeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
        qs = Employee.objects.filter(employee_id=employee_id)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if employee_id and qs.exists():
            raise forms.ValidationError("An employee with this ID already exists.")
        return cleaned_data

# --- SalaryPaymentForm ---
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
        qs = SalaryPayment.objects.filter(employee=employee, payment_date=payment_date)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if employee and payment_date and qs.exists():
            raise forms.ValidationError("A salary payment for this employee on the same date already exists.")
        return cleaned_data

# --- PaymentForm ---
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

# --- ClientForm ---
class ClientForm(forms.ModelForm):
    class Meta:
        model = Clients
        fields = ['name', 'email', 'phone_number', 'address', 'contact_person']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
    def clean_name(self):
        name = self.cleaned_data['name']
        instance = getattr(self, 'instance', None)
        qs = Clients.objects.filter(name=name)
        if instance and instance.pk:
            qs = qs.exclude(pk=instance.pk)
        if qs.exists():
            raise forms.ValidationError("A client with this name already exists.")
        return name

# --- Investment/Grant/GovernmentProgram Forms ---
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

# --- Choices ---
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
WORK_PLACE_CHOICES = [
    ('resa', 'Resa'),
    ('kahama', 'Kahama'),
    ('pemba', 'Pemba'),
    # Add more choices as needed
]
GENDER_CHOICES = [
    ('male', 'Male'),
    ('female', 'Female'),
]

# --- AddStaffForm ---
class AddStaffForm(forms.Form):
    first_name = forms.CharField(
        label='First Name',
        max_length=50,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter First Name"})
    )
    middle_name = forms.CharField(
        label='Middle Name',
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Middle Name"})
    )
    last_name = forms.CharField(
        label='Last Name',
        max_length=50,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Last Name"})
    )
    phone_number = forms.CharField(
        label='Phone Number',
        max_length=10,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Phone Number"})
    )
    email = forms.EmailField(
        label='Email',
        max_length=50,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Enter Email"})
    )
    username = forms.CharField(
        label='Username',
        max_length=50,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Username"})
    )
    password = forms.CharField(
        label='Password',
        max_length=50,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Enter Password"})
    )
    confirm_password = forms.CharField(
        label='Confirm Password',
        max_length=50,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirm Password"})
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
    mct_number = forms.CharField(
        label='MCT Number',
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter MCT Number"})
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match. Please try again.")
        return cleaned_data

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if phone_number and not re.match(r'^\d{10}$', phone_number):
            raise forms.ValidationError("Phone number must be exactly 10 digits long.")
        return phone_number


class StaffProfileForm(forms.ModelForm):
    class Meta:
        model = Staffs
        fields = ['profile_picture', 'signature']
        widgets = {
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'signature': forms.FileInput(attrs={'class': 'form-control'}),
        }        