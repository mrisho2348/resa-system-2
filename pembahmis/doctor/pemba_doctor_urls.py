from django.urls import path
from pembahmis.doctor.pembaDoctor import *

urlpatterns = [
    # Profile and Authentication URLs
    path('edit-profile/<int:pk>/', EditStaffProfileView.as_view(), name='pemba_doctor_edit_profile'),
    path('profile/', doctor_profile, name='pemba_doctor_profile'),
    path('change-password/', change_password, name='pemba_doctor_change_password'),
    
    # Dashboard URLs
    path('dashboard/', pemba_dashboard, name='pemba_doctor_dashboard'),
    
    # Reports URLs
    path('reports/generate_year_month_report/', generate_year_month_report, name='pemba_doctor_generate_year_month_report'),
    path('reports/search-report/', search_report, name='pemba_doctor_search_report'),
    path('reports/get-gender-yearly-data/', get_gender_yearly_data, name='pemba_doctor_gender_yearly_data'),
    path('reports/get-patient-data-by-company/', get_patient_data_by_company, name='pemba_doctor_patient_data_by_company'),
    path('reports/get-gender-monthly-data/', get_gender_monthly_data, name='pemba_doctor_gender_monthly_data'),
    path('reports/resa/', resa_report, name='pemba_doctor_resa_report'),
    path('reports/comprehensive/', reports_comprehensive, name='pemba_doctor_reports_comprehensive'),
    path('reports/patients/', reports_patients, name='pemba_doctor_reports_patients'),
    path('reports/service/', reports_service, name='pemba_doctor_reports_service'),
    path('reports/stock-level/', reports_stock_level, name='pemba_doctor_reports_stock_level'),
    path('reports/visit-summary/', reports_patients_visit_summary, name='pemba_doctor_reports_visit_summary'),
    path('reports/individual-visit/<int:patient_id>/', individual_visit, name='pemba_doctor_individual_visit'),
    path('reports/by-visit/', reports_by_visit, name='pemba_doctor_reports_by_visit'),
    
    # Appointment URLs
    path('appointment/create/', appointment_view, name='pemba_doctor_appointment_create'),
    path('add_appointment/', add_appointment, name='pemba_doctor_add_appointment'),
    path('appointment/list/', appointment_list_view, name='pemba_doctor_appointment_list'),
    path('appointment/confirm/<int:appointment_id>/', confirm_meeting, name='pemba_doctor_appointment_confirm'),
    path('appointment/edit/<int:appointment_id>/', edit_meeting, name='pemba_doctor_appointment_edit'),
    
    # Patient Management URLs
    path('patients/', patients_list, name='pemba_doctor_patients_list'),
    path('patients/add/', patient_info_form, name='pemba_doctor_patient_add'),
    path('patients/edit/<int:patient_id>/', patient_info_form_edit, name='pemba_doctor_patient_edit'),
    path('patients/health-info/<int:patient_id>/', save_patient_health_information, name='pemba_doctor_patient_health_info'),
    path('patients/health-edit/<int:patient_id>/', health_info_edit, name='pemba_doctor_patient_health_edit'),
    path('patients/visit-history/<int:patient_id>/', patient_visit_history_view, name='pemba_doctor_patient_visit_history'),
    
    # Visit Management URLs
    path('visit/save/<int:patient_id>/', save_patient_visit_save, name='pemba_doctor_visit_save'),
    path('visit/save/<int:patient_id>/<int:visit_id>/', save_patient_visit_save, name='pemba_doctor_visit_edit'),
    
    # Consultation URLs
    path('consultation/save/<int:patient_id>/<int:visit_id>/', save_remotesconsultation_notes, name='pemba_doctor_consultation_save'),
    path('consultation/save-next/<int:patient_id>/<int:visit_id>/', save_remotesconsultation_notes_next, name='pemba_doctor_consultation_save_next'),
    path('consultation/list/', consultation_notes_view, name='pemba_doctor_consultation_list'),
    path('consultation/download-summary/<int:patient_id>/<int:visit_id>/', download_consultation_summary_pdf, name='pemba_doctor_consultation_download_summary'),
    
    # Vital Signs URLs
    path('vitals/save/<int:patient_id>/<int:visit_id>/', save_remotepatient_vitals, name='pemba_doctor_vitals_save'),
 
    path('vitals/save-ajax/', save_remotepatient_vital, name='pemba_doctor_vitals_save_ajax'),
    
    # Chief Complaint URLs
    path('chief-complaint/save/', save_chief_complaint, name='pemba_doctor_chief_complaint_save'),
    path('chief-complaint/update/<int:chief_complaint_id>/', update_chief_complaint, name='pemba_doctor_chief_complaint_update'),
    path('chief-complaint/fetch-existing/', fetch_existing_data, name='pemba_doctor_chief_complaint_fetch'),
    path('chief-complaint/delete/<int:chief_complaint_id>/', delete_chief_complaint, name='pemba_doctor_chief_complaint_delete'),
    
    # Laboratory URLs
    path('laboratory/save/<str:mrn>/', patient_lab_result_history_view, name='pemba_doctor_patient_lab_result_history_view'),
    path('laboratory/save/<int:patient_id>/<int:visit_id>/', save_laboratory, name='pemba_doctor_laboratory_save'),
    path('laboratory/list/', patient_laboratory_view, name='pemba_doctor_laboratory_list'),

    path('laboratory/download-result/<int:lab_id>/', download_lab_result_pdf, name='pemba_doctor_laboratory_download_result'),
    path('laboratory/download-all-results/<str:patient_mrn>/<str:visit_vst>/', download_all_lab_results_pdf, name='pemba_doctor_laboratory_download_all_results'),
    path('laboratory/edit/<int:patient_id>/<int:visit_id>/<int:lab_id>/', edit_lab_result, name='pemba_doctor_laboratory_edit'),
    
    # Procedure URLs
    path('procedure/save/<int:patient_id>/<int:visit_id>/', save_remoteprocedure, name='pemba_doctor_procedure_save'),
    path('procedure/list/', patient_procedure_view, name='pemba_doctor_procedure_list'),
    path('procedure/history/<str:mrn>/', patient_procedure_history_view, name='pemba_doctor_procedure_history'),
    path('procedure/edit/<int:patient_id>/<int:visit_id>/<int:procedure_id>/', edit_procedure_result, name='pemba_doctor_procedure_edit'),
    path('procedure/download-result/<int:procedure_id>/', download_procedure_result_pdf, name='pemba_doctor_procedure_download_result'),
    path('procedure/download-all/<str:patient_mrn>/<str:visit_vst>/', download_all_procedures_pdf, name='pemba_doctor_procedure_download_all'),
    
    # Referral URLs
    path('referral/save/<int:patient_id>/<int:visit_id>/', save_remotereferral, name='pemba_doctor_referral_save'),
    path('referral/list/', manage_referral, name='pemba_doctor_referral_list'),
    path('referral/change-status/', change_referral_status, name='pemba_doctor_referral_change_status'),
    path('referral/download/<int:patient_id>/<int:visit_id>/', download_referral_pdf, name='pemba_doctor_referral_download'),
    
    # Prescription URLs
    path('prescription/save/<int:patient_id>/<int:visit_id>/', save_prescription, name='pemba_doctor_prescription_save'),
    path('prescription/list/', prescription_list, name='pemba_doctor_prescription_list'),
    path('prescription/download-notes/<int:patient_id>/<int:visit_id>/', download_prescription_notes_pdf, name='pemba_doctor_prescription_download_notes'),
    path('prescription/add/', add_remoteprescription, name='pemba_doctor_prescription_add'),
    path('prescription/medicines/', get_all_medicine_data, name='pemba_doctor_prescription_medicines'),
    path('prescription/frequencies/', get_all_frequency_data, name='pemba_doctor_prescription_frequencies'),
    
    # Counseling URLs
    path('counseling/save/<int:patient_id>/<int:visit_id>/', save_counsel, name='pemba_doctor_counseling_save'),
    path('counseling/list/', counseling_list_view, name='pemba_doctor_counseling_list'),
    path('counseling/download-pdf/<int:patient_id>/<int:visit_id>/', download_counseling_pdf, name='pemba_doctor_counseling_download_pdf'),
    
    # Discharge URLs
    path('discharge/save/<int:patient_id>/<int:visit_id>/', save_remote_discharges_notes, name='pemba_doctor_discharge_save'),
    path('discharge/list/', discharge_notes_list_view, name='pemba_doctor_discharge_list'),
    path('discharge/download-pdf/<int:patient_id>/<int:visit_id>/', download_discharge_pdf, name='pemba_doctor_discharge_download_pdf'),
    
    # Observation URLs
    path('observation/<int:patient_id>/<int:visit_id>/', save_observation, name='pemba_doctor_save_observation'),
    path('observation/list/', patient_observation_view, name='pemba_doctor_observation_list'),
    path('observation/records/', observation_record_list_view, name='pemba_doctor_observation_records'),
    path('observation/download-pdf/<int:patient_id>/<int:visit_id>/', download_observation_pdf, name='pemba_doctor_observation_download_pdf'),
    
    # Health Record Deletion URLs
    path('health-record/delete/', delete_health_record, name='pemba_doctor_health_record_delete'),
    path('family-history/delete/', delete_family_medical_history_record, name='pemba_doctor_family_history_delete'),
    path('medication-allergy/delete/', delete_medication_allergy_record, name='pemba_doctor_medication_allergy_delete'),
    path('surgery-history/delete/', delete_surgery_history_record, name='pemba_doctor_surgery_history_delete'),
]