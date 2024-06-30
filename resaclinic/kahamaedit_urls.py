from django.urls import path
from kahamahmis import kahamaEditView

urlpatterns = [
    # Disease records
    path('disease-records/<int:disease_id>/edit/', kahamaEditView.edit_disease_record, name='kahama_edit_disease_record'),
    
    # Insurance records
    path('insurance-records/<int:insurance_id>/edit/', kahamaEditView.edit_insurance, name='kahama_edit_insurance'),
    
    # Pathology records
    path('pathodology/<int:pathodology_id>/edit/', kahamaEditView.edit_pathodology, name='kahama_edit_pathodology'),
    
    # Company records
    path('company/<int:company_id>/edit/', kahamaEditView.edit_company, name='kahama_edit_company'),
    
    # Consultation data
    path('update_consultation_data/<int:appointment_id>/', kahamaEditView.update_consultation_data, name='kahama_update_consultation_data'),
    
    # Procedure edits
    path('edit_procedure/', kahamaEditView.edit_procedure, name='kahama_edit_procedure'),
    
    # Lab result edits
    path('edit_lab_result/', kahamaEditView.edit_lab_result, name='kahama_edit_lab_result'),
    
    # Observation edits
    path('edit_observation/', kahamaEditView.edit_observation, name='kahama_edit_observation'),
    
    # Referral edits
    path('edit_referral/', kahamaEditView.edit_referral, name='kahama_edit_referral'),
    
    # Medicine edits
    path('edit_medicine/<int:medicine_id>/', kahamaEditView.edit_medicine, name='kahama_edit_medicine'),
]
