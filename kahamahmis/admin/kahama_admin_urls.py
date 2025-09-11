from django.urls import path

from kahamahmis.admin.kahamaAdmin import *
from kahamahmis.kahamaReports import *

urlpatterns = [
    # Patient management
    path('kahama_patient_list/', kahama_patient_list_view, name='kahama_admin_patient_list'),
    path('delete_kahama_patient/', delete_kahama_patient_view, name='kahama_admin_delete_patient'),
    path('gender-yearly-data/', get_gender_yearly_data, name='kahama_admin_gender_yearly_data'),
    path('gender-monthly-data/', get_gender_monthly_data, name='kahama_admin_gender_monthly_data'),
    path('get_patient_data_by_company/', get_patient_data_by_company, name='kahama_admin_get_patient_data_by_company'),

    path('api/kahama/procedure-order-counts/', fetch_procedure_order_counts, name='kahama_admin_fetch_procedure_order_counts'),
    path('api/kahama/laboratory-order-counts/', fetch_laboratory_order_counts, name='kahama_admin_fetch_laboratory_order_counts'),
    # Dashboard
    path('dashboard', divine_dashboard, name='kahama_admin_dashboard'),
    
    # User profile
    path('admin_profile/', admin_profile, name='kahama_admin_profile'),
    path('change_password/', change_password, name='kahama_admin_change_password'),
    
    # Medicine management
    path('expired_medicine/', expired_medicine_view, name='kahama_admin_expired_medicine'),
    path('instock_medicine/', instock_medicine_view, name='kahama_admin_instock_medicine'),
    path('checklist_medicine/', checklist_medicine_view, name='kahama_admin_checklist_medicine'),
    path('outofstock_medicine/', outofstock_medicine_view, name='kahama_admin_outofstock_medicine'),
    path('kahamamedicine_list/', kahamamedicine_list, name='kahama_admin_kahamamedicine_list'),
    path('add_kahama_medicine/', add_kahama_medicine, name='kahama_admin_add_kahama_medicine'),
    path('delete_kahama_medicine/', delete_kahama_medicine, name='kahama_admin_delete_kahama_medicine'),
    path('medicine_count_api/', medicine_count_api, name='kahama_admin_medicine_count_api'),
    
    # Reference data management
    path('manage_country/', manage_country, name='kahama_admin_manage_country'),
    path('manage_company/', manage_company, name='kahama_admin_manage_company'),
    path('manage_disease/', manage_disease, name='kahama_admin_manage_disease'),
    path('manage_pathodology/', manage_pathodology, name='kahama_admin_manage_pathodology'),
    path('add_disease/', add_disease, name='kahama_admin_add_disease'),
    path('add_company/', add_company, name='kahama_admin_add_company'),
    path('add_pathodology_record/', add_pathodology_record, name='kahama_admin_add_pathodology_record'),
    path('save_diagnosis/', save_diagnosis, name='kahama_admin_save_diagnosis'),
    path('delete_diagnosis/', delete_diagnosis, name='kahama_admin_delete_diagnosis'),
    
    # Reports
    path('reports_by_visit/', reports_by_visit, name='kahama_admin_reports_by_visit'),
    path('reports_patients_visit_summary/', reports_patients_visit_summary, name='kahama_admin_reports_patients_visit_summary'),
    path('reports_patients/', reports_patients, name='kahama_admin_reports_patients'),
    path('individual_visit/<int:patient_id>/', individual_visit, name='kahama_admin_individual_visit'),
    path('patient_statistics/', patient_statistics, name='kahama_admin_patient_statistics'),
    path('search_report/', search_report, name='kahama_admin_search_report'),
    path('update_staff_status/', update_staff_status, name='kahama_admin_update_staff_status'),
    
    # Clinical records
    path('manage_procedure/', patient_procedure_view, name='kahama_admin_manage_procedure'),
    path('manage_referral/', manage_referral, name='kahama_admin_manage_referral'),
    path('manage_appointment/', appointment_list_view, name='kahama_admin_manage_appointment'),
    path('manage_prescription_list/', prescription_list, name='kahama_admin_manage_prescription_list'),
    path('manage_consultation_notes/', consultation_notes_view, name='kahama_admin_manage_consultation_notes'),
    path('manage_diagnosis_list/', diagnosis_list, name='kahama_admin_manage_diagnosis_list'),
    path('service_list/', kahamaservice_list, name='kahama_admin_service_list'),
    path('manage_counselling/', counseling_list_view, name='kahama_admin_manage_counselling'),
    path('manage_observation_record/', observation_record_list_view, name='kahama_admin_manage_observation_record'),
    path('manage_discharge/', discharge_notes_list_view, name='kahama_admin_manage_discharge'),
    path('healthrecord_list/', health_record_list, name='kahama_admin_healthrecord_list'),
    path('patient_laboratory_view/', patient_laboratory_view, name='kahama_admin_patient_laboratory_view'),
    
    # Staff management
    path('manage_staff/', manage_staff, name='kahama_admin_manage_staff'),
    
    # Company registration
    path('add_clinic_company/', company_registration_view, name='kahama_admin_add_clinic_company'),
    
    # Equipment management
    path('kahama_equipment_list/', kahama_equipment_list, name='kahama_admin_kahama_equipment_list'),
    path('add_or_edit_kahama_equipment/', add_or_edit_kahama_equipment, name='kahama_admin_add_or_edit_kahama_equipment'),
    
    # Reagent management
    path('kahama_reagent_list/', kahama_reagent_list, name='kahama_admin_kahama_reagent_list'),
    path('add_or_edit_kahama_reagent/', add_or_edit_kahama_reagent, name='kahama_admin_add_or_edit_kahama_reagent'),
    
    # Delete operations
    path('delete_consultation/', delete_consultation, name='kahama_admin_delete_consultation'),
    path('delete_pathology_record/', delete_pathology_record, name='kahama_admin_delete_pathology_record'),
    path('delete_observation/', delete_observation, name='kahama_admin_delete_observation'),
    path('delete_discharge_note/', delete_discharge_note, name='kahama_admin_delete_discharge_note'),
    path('delete_lab_result/', delete_lab_result, name='kahama_admin_delete_lab_result'),
    path('delete_referral/', delete_referral, name='kahama_admin_delete_referral'),
    path('delete_disease_record/', delete_disease_record, name='kahama_admin_delete_disease_record'),
    path('delete_kahama_company/', delete_kahama_company, name='kahama_admin_delete_kahama_company'),
    path('delete_service/', delete_service, name='kahama_admin_delete_service'),
    path('delete_procedure/', delete_procedure, name='kahama_admin_delete_procedure'),
    path('delete_healthrecord/', delete_healthrecord, name='kahama_admin_delete_healthrecord'),
    path('delete_kahama_equipment/', delete_kahama_equipment, name='kahama_admin_delete_kahama_equipment'),
    path('delete_kahama_reagent/', delete_kahama_reagent, name='kahama_admin_delete_kahama_reagent'),
    path('delete_counseling_session/', delete_counseling_session, name='kahama_admin_delete_counseling_session'),
    path('save_health_record/', save_health_record, name='kahama_admin_save_health_record'),
    path('save_service/', save_kahama_service, name='kahama_admin_save_service'),
    path('report/', generate_year_month_report, name='kahama_admin_generate_year_month_report'),
    path('resa_report/', resa_report, name='kahama_admin_resa_report'),


     path('consultation/download-summary/<int:patient_id>/<int:visit_id>/', download_consultation_summary_pdf, name='kahama_admin_consultation_download_summary'),
    path('laboratory/download-result/<int:lab_id>/', download_lab_result_pdf, name='kahama_admin_laboratory_download_result'),
    path('laboratory/download-all-results/<str:patient_mrn>/<str:visit_vst>/', download_all_lab_results_pdf, name='kahama_admin_laboratory_download_all_results'),
    path('procedure/download-result/<int:procedure_id>/', download_procedure_result_pdf, name='kahama_admin_procedure_download_result'),
    path('procedure/download-all/<str:patient_mrn>/<str:visit_vst>/', download_all_procedures_pdf, name='kahama_admin_procedure_download_all'),
    path('referral/download/<int:patient_id>/<int:visit_id>/', download_referral_pdf, name='kahama_admin_referral_download'),
    path('prescription/download-notes/<int:patient_id>/<int:visit_id>/', download_prescription_notes_pdf, name='kahama_admin_prescription_download_notes'),
    # path('counseling/download-notes/<int:patient_id>/<int:visit_id>/', download_counseling_notes, name='kahama_admin_counseling_download_notes'),
    path('counseling/download-pdf/<int:patient_id>/<int:visit_id>/', download_counseling_pdf, name='kahama_admin_counseling_download_pdf'),
    path('discharge/download-pdf/<int:patient_id>/<int:visit_id>/', download_discharge_pdf, name='kahama_admin_discharge_download_pdf'),
    path('observation/download-pdf/<int:patient_id>/<int:visit_id>/', download_observation_pdf, name='kahama_admin_observation_download_pdf'),
    
]