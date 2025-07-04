from django.urls import path

from kahamahmis import divineDelete


urlpatterns = [
    # Diagnosis
    path('delete_diagnosis/', divineDelete.delete_diagnosis, name='divine_delete_diagnosis'),
    
    # Consultation Notes
    path('delete_ConsultationNotes/<int:consultation_id>/', divineDelete.delete_ConsultationNotes, name='divine_delete_ConsultationNotes'),
    
    # Patient Vital
    path('delete_patient_vital/<int:vital_id>/', divineDelete.delete_patient_vital, name='divine_delete_patient_vital'),
    
    # Prescription
    path('delete_prescription/<int:prescription_id>/', divineDelete.delete_prescription, name='divine_delete_prescription'),
   
    
    # Medicine
    path('delete_medicine/<int:medicine_id>/', divineDelete.delete_medicine, name='divine_delete_medicine'),
    
    # Disease Records
    path('delete_disease/', divineDelete.delete_disease_record, name='divine_delete_disease_record'),
    path('delete_remotecompany/', divineDelete.delete_remotecompany, name='divine_delete_remotecompany'),

    # Drug
    path('delete_drug/', divineDelete.delete_drug, name='divine_delete_drug'),
    
    # Pathology Record
    path('delete_pathology_record/', divineDelete.delete_pathology_record, name='divine_delete_pathology_record'),
    
    # Service
    path('delete_service/', divineDelete.delete_service, name='divine_delete_service'),
    
    # Procedure
    path('delete_procedure/', divineDelete.delete_procedure, name='divine_delete_procedure'),
    
    # Result
    path('delete_result/', divineDelete.delete_result, name='divine_delete_result'),
    
    # Observation
    path('delete_observation/', divineDelete.delete_observation, name='divine_delete_observation'),
    
    # Health Record
    path('delete_health_record/', divineDelete.delete_health_record, name='divine_delete_health_record'),
    
    # Medication Allergy Record
    path('delete_medication_allergy_record/', divineDelete.delete_medication_allergy_record, name='divine_delete_medication_allergy_record'),
    
    # Surgery History Record
    path('delete_surgery_history_record/', divineDelete.delete_surgery_history_record, name='divine_delete_surgery_history_record'),
    
    # Family Medical History Record
    path('delete_family_medical_history_record/', divineDelete.delete_family_medical_history_record, name='divine_delete_family_medical_history_record'),
    
    # Lab Result
    path('delete_lab_result/', divineDelete.delete_lab_result, name='divine_delete_lab_result'),
    
    # Referral
    path('delete_referral/', divineDelete.delete_referral, name='divine_delete_referral'),
    
    # Patient Visit
    path('delete_patient_visit/<int:patient_visit_id>/', divineDelete.delete_patient_visit, name='divine_delete_patient_visit'),
]