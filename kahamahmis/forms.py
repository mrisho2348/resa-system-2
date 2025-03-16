from django import forms
from django.core.validators import FileExtensionValidator
from clinic.models import RemoteLaboratoryOrder, RemoteProcedure, Staffs
from django_ckeditor_5.widgets import CKEditor5Widget
class ImportInsuranceCompanyForm(forms.Form):
    file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
class DiseaseRecodeImportForm(forms.Form):
    file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
class RemoteMedicineImportForm(forms.Form):
    file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
class HealthRecordImportForm(forms.Form):
    file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
class RemoteCompanyImportForm(forms.Form):
    file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
class PathodologyRecordImportForm(forms.Form):
    file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
class RemoteServiceImportForm(forms.Form):
    file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
    
class CountryImportForm(forms.Form):
    file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
    
class RemoteReagentForm(forms.Form):
    file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
    
class RemoteEquipmentForm(forms.Form):
    file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
class DiagnosisImportForm(forms.Form):
    file = forms.FileField(
        label='Choose an Excel file',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )

class RemoteProcedureForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make the 'result' field optional
        self.fields["result"].required = False

    class Meta:
        model = RemoteProcedure
        fields = ("result",)
        widgets = {
            "result": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"},  # Add a custom CSS class
                config_name="extends"  # Specify the CKEditor configuration to use
            )
        }
        
class RemoteLaboratoryOrderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make the 'result' field optional
        self.fields["result"].required = False

    class Meta:
        model = RemoteLaboratoryOrder
        fields = ("result",)
        widgets = {
            "result": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"},  # Add a custom CSS class
                config_name="extends"  # Specify the CKEditor configuration to use
            )
        }        


class StaffProfileForm(forms.ModelForm):
    class Meta:
        model = Staffs
        fields = ['profile_picture', 'signature']
        widgets = {
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'signature': forms.FileInput(attrs={'class': 'form-control'}),
        }