from datetime import datetime
import re
from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
from kahamahmis.models import (    
    KahamaCounseling, KahamaDischargesNotes, KahamaLaboratoryRequest, KahamaObservationRecord, KahamaProcedure, KahamaReferral)



# --- Model Form Mixins for DRYness ---
class CKEditorOptionalFieldMixin:
    ckeditor_field = None
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.ckeditor_field:
            self.fields[self.ckeditor_field].required = False

# --- LaboratoryOrderForm, ProcedureForm, ImagingRecordForm ---
class KahamaLaboratoryRequestForm(CKEditorOptionalFieldMixin, forms.ModelForm):
    ckeditor_field = "result"
    class Meta:
        model = KahamaLaboratoryRequest
        fields = ("result",)
        widgets = {
            "result": CKEditor5Widget(attrs={"class": "django_ckeditor_5"}, config_name="extends")
        }

class KahamaProcedureForm(CKEditorOptionalFieldMixin, forms.ModelForm):
    ckeditor_field = "result"
    class Meta:
        model = KahamaProcedure
        fields = ("result",)
        widgets = {
            "result": CKEditor5Widget(attrs={"class": "django_ckeditor_5"}, config_name="extends")
        }



class KahamaObservationRecordForm(CKEditorOptionalFieldMixin, forms.ModelForm):
    ckeditor_field = "observation_notes"
    class Meta:
        model = KahamaObservationRecord
        fields = ("observation_notes",)
        widgets = {
            "observation_notes": CKEditor5Widget(attrs={"class": "django_ckeditor_5"}, config_name="extends")
        }

class KahamaCounselingForm(CKEditorOptionalFieldMixin, forms.ModelForm):
    ckeditor_field = "counselling_notes"
    class Meta:
        model = KahamaCounseling
        fields = ("counselling_notes",)
        widgets = {
            "counselling_notes": CKEditor5Widget(attrs={"class": "django_ckeditor_5"}, config_name="extends")
        }


class KahamaReferralForm(forms.ModelForm):
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
            self.initial['transport_model'] = KahamaReferral._meta.get_field('transport_model').default

    class Meta:
        model = KahamaReferral
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
class KahamaDischargesNotesForm(forms.ModelForm):
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
        model = KahamaDischargesNotes
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

