from django.urls import path
from kahamahmis import kahamaDelete

urlpatterns = [
    # Diagnosis
    path('delete_diagnosis/', kahamaDelete.delete_diagnosis, name='kahama_delete_diagnosis'),
    
    # Consultation Notes
    path('delete_ConsultationNotes/<int:consultation_id>/', kahamaDelete.delete_ConsultationNotes, name='kahama_delete_ConsultationNotes'),
    
    # Patient Vital
    path('delete_patient_vital/<int:vital_id>/', kahamaDelete.delete_patient_vital, name='kahama_delete_patient_vital'),
    
    # Prescription
    path('delete_prescription/<int:prescription_id>/', kahamaDelete.delete_prescription, name='kahama_delete_prescription'),
    path('delete-consultation/<int:appointment_id>/', kahamaDelete.delete_consultation, name='kahama_delete_consultation'),
    
    # Medicine
    path('delete_medicine/<int:medicine_id>/', kahamaDelete.delete_medicine, name='kahama_delete_medicine'),
    
    # Disease Records
    path('disease-records/<int:disease_id>/delete/', kahamaDelete.delete_disease_record, name='kahama_delete_disease_record'),
    
    # Insurance Records
    path('insurance-records/<int:insurance_id>/delete/', kahamaDelete.delete_insurance, name='kahama_delete_insurance'),
    
    # Pathology
    path('pathodology/<int:pathodology_id>/delete/', kahamaDelete.delete_pathodology, name='kahama_delete_pathodology'),
    
    # Company
    path('company/<int:company_id>/delete/', kahamaDelete.delete_company, name='kahama_delete_company'),
    
    # Staff
    path('delete_staff/<int:staff_id>/', kahamaDelete.delete_staff, name='kahama_delete_staff'),
    
    # Patient
    path('delete-patient/<int:patient_id>/', kahamaDelete.delete_patient, name='kahama_delete_patient'),
    path('delete_remoteinsurancecompany/', kahamaDelete.delete_remoteinsurancecompany, name='kahama_delete_remoteinsurancecompany'),
    
    # Drug
    path('delete_drug/', kahamaDelete.delete_drug, name='kahama_delete_drug'),
    
    # Pathology Record
    path('delete_pathology_record/', kahamaDelete.delete_pathology_record, name='kahama_delete_pathology_record'),
    
    # Service
    path('delete_service/', kahamaDelete.delete_service, name='kahama_delete_service'),
    
    # Procedure
    path('delete_procedure/', kahamaDelete.delete_procedure, name='kahama_delete_procedure'),
    
    # Result
    path('delete_result/', kahamaDelete.delete_result, name='kahama_delete_result'),
    
    # Observation
    path('delete_observation/', kahamaDelete.delete_observation, name='kahama_delete_observation'),
    
    # Health Record
    path('delete_health_record/', kahamaDelete.delete_health_record, name='kahama_delete_health_record'),
    
    # Medication Allergy Record
    path('delete_medication_allergy_record/', kahamaDelete.delete_medication_allergy_record, name='kahama_delete_medication_allergy_record'),
    
    # Surgery History Record
    path('delete_surgery_history_record/', kahamaDelete.delete_surgery_history_record, name='kahama_delete_surgery_history_record'),
    
    # Family Medical History Record
    path('delete_family_medical_history_record/', kahamaDelete.delete_family_medical_history_record, name='kahama_delete_family_medical_history_record'),
    
    # Lab Result
    path('delete_lab_result/', kahamaDelete.delete_lab_result, name='kahama_delete_lab_result'),
    
    # Referral
    path('delete_referral/', kahamaDelete.delete_referral, name='kahama_delete_referral'),
    
    # Patient Visit
    path('delete_patient_visit/<int:patient_visit_id>/', kahamaDelete.delete_patient_visit, name='kahama_delete_patient_visit'),
]
