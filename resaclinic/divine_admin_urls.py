from django.urls import path
from kahamahmis import divine_Admin

urlpatterns = [
    # Data retrieval paths
    path('get_patient_data_by_company/', divine_Admin.get_patient_data_by_company, name="divine_get_patient_data_by_company"),
    path('get_gender_yearly_data/', divine_Admin.get_gender_yearly_data, name="divine_get_gender_yearly_data"),
    path('get_gender_monthly_data/', divine_Admin.get_gender_monthly_data, name="divine_get_gender_monthly_data"),    
    # Management paths
    path('manage_country/', divine_Admin.manage_country, name="divine_manage_country"),
    path('save_remote_service/', divine_Admin.save_remote_service, name="divine_save_remote_service"),  
   
    path('individual_visit/<int:patient_id>/', divine_Admin.individual_visit, name="divine_individual_visit"),   
    path('save_diagnosis/', divine_Admin.save_diagnosis, name="divine_save_diagnosis"),
    path('admin/profile/', divine_Admin.admin_profile, name='divine_profile'),
    path('kahama/admin/change-password/', divine_Admin.change_password, name='divine_change_password'),  

    # Dashboard paths
    path('resa/dashboard/', divine_Admin.divine_dashboard, name="divine_dashboard"),    
    # Add data paths
    path('add_disease/', divine_Admin.add_disease, name='divine_add_disease'),   
    path('company/delete', divine_Admin.delete_remotecompany, name='divine_delete_remotecompany'),
    path('company/add', divine_Admin.add_company, name='divine_add_company'),
    path('add_pathodology_record/', divine_Admin.add_pathodology_record, name='divine_add_pathodology_record'),


    # Report paths
    path('resa/resa-report/', divine_Admin.resa_report, name="divine_resa_report"),
    path('resa/reports-adjustments/', divine_Admin.reports_adjustments, name="divine_reports_adjustments"),
    path('resa/reports-by-visit/', divine_Admin.reports_by_visit, name="divine_reports_by_visit"),
    path('resa/reports-comprehensive/', divine_Admin.reports_comprehensive, name="divine_reports_comprehensive"),
    path('resa/reports-patients-visit_summary/', divine_Admin.reports_patients_visit_summary, name="divine_reports_patients_visit_summary"),
    path('resa/reports-patients/', divine_Admin.reports_patients, name="divine_reports_patients"),
    path('resa/reports-service/', divine_Admin.reports_service, name="divine_reports_service"),
    path('resareports-stock-ledger/', divine_Admin.reports_stock_ledger, name="divine_reports_stock_ledger"),
    path('resa/reports-stock-level/', divine_Admin.reports_stock_level, name="divine_reports_stock_level"),
    path('resa/reports-orders/', divine_Admin.reports_orders, name="divine_reports_orders"),
    path('resa/individual-visit/', divine_Admin.individual_visit, name="divine_individual_visit"),
    path('resa/product-summary/', divine_Admin.product_summary, name="divine_product_summary"),
  
    path('diagnosis/', divine_Admin.diagnosis_list, name='divine_diagnosis_list'),

    path('remoteservice_list/', divine_Admin.remoteservice_list, name='divine_remoteservice_list'),
    path('consultation-notes/', divine_Admin.consultation_notes_view, name='divine_consultation_notes'),  


    path('prescriptions/', divine_Admin.prescription_list, name='divine_prescription_list'),
    path('counseling/', divine_Admin.counseling_list_view, name='divine_counseling_list'),
   
    path('discharge_notes/', divine_Admin.discharge_notes_list_view, name='divine_discharge_notes_list'),
   
    path('observation_records/', divine_Admin.observation_record_list_view, name='divine_observation_record_list'),

    # Referral paths
    path('resa/manage-referral/', divine_Admin.manage_referral, name='divine_manage_referral'),
  
    path('resa/patient-procedure-view/', divine_Admin.patient_procedure_view, name='divine_patient_procedure_view'),

    path('resa/manage-company/', divine_Admin.manage_company, name="divine_manage_company"),
    path('resa/manage-disease/', divine_Admin.manage_disease, name="divine_manage_disease"),
    path('resa/manage-staff/', divine_Admin.manage_staff, name="divine_manage_staff"),

    path('resa/manage-adjustment/', divine_Admin.manage_adjustment, name="divine_manage_adjustment"),
    path('resa/manage-pathodology/', divine_Admin.manage_pathodology, name="divine_manage_pathodology"),

    # Appointment paths
    path('resa/appointments/', divine_Admin.appointment_list_view, name='divine_appointment_list'),   
      # Company related URLs
    path('company/add/', divine_Admin.company_registration_view, name='divine_add_clinic_company'),


    # Medicine and Formulation related URLs

    path('add_remote_medicine/', divine_Admin.add_remote_medicine, name='divine_add_remote_medicine'),
    path('remotemedicine_list/', divine_Admin.remotemedicine_list, name='divine_remotemedicine_list'),


    # Report and Statistics URLs
    path('search_report/', divine_Admin.search_report, name='divine_search_report'),
    path('patient_statistics/', divine_Admin.patient_statistics, name='divine_patient_statistics'),



    # Remote Equipment URLs
    path('remote-equipment/', divine_Admin.remote_equipment_list, name='divine_remote_equipment_list'),
    path('add-remote-equipment/', divine_Admin.add_or_edit_remote_equipment, name='divine_add_or_edit_remote_equipment'),
    path('delete_remote_equipment/', divine_Admin.delete_remote_equipment, name='divine_delete_remote_equipment'),

   
    path('patient_laboratory_view/', divine_Admin.patient_laboratory_view, name="divine_patient_laboratory_view"),

   
    path('patient_observation_view/', divine_Admin.patient_observation_view, name="divine_patient_observation_view"),

    # Health Record URLs
    path('health_record_list/', divine_Admin.health_record_list, name="divine_health_record_list"),
    path('save_health_record/', divine_Admin.save_health_record, name="divine_save_health_record"),
    path('delete_healthrecord/', divine_Admin.delete_healthrecord, name='divine_delete_healthrecord'),
    
    # Reagent URLs
    path('reagent_list/', divine_Admin.reagent_list, name="divine_reagent_list"),
    path('add_or_edit_reagent/', divine_Admin.add_or_edit_reagent, name="divine_add_or_edit_reagent"),
    path('delete_reagent/', divine_Admin.delete_reagent, name="divine_delete_reagent"),
    
  

    path('delete-remote-medicine/', divine_Admin.delete_remote_medicine, name='divine_delete_remote_medicine'),

    path('expired-medicine/', divine_Admin.expired_medicine_view, name='divine_expired_medicine_view'),
    path('in-stock-medicine/', divine_Admin.instock_medicine_view, name='divine_instock_medicine_view'),
    path('checklist-medicine/', divine_Admin.checklist_medicine_view, name='divine_checklist_medicine_view'),
    path('out-of-stock-medicine/', divine_Admin.outofstock_medicine_view, name='divine_outofstock_medicine_view'),
    path('api/medicine-counts/', divine_Admin.medicine_count_api, name='divine_medicine_count_api'),
    path('remote/patients/', divine_Admin.remote_patient_list_view, name='divine_patient_list'),
    path('delete-remote-patient/', divine_Admin.delete_remote_patient_view, name='divine_delete_remote_patient'),
    path('delete-appointment/', divine_Admin.delete_consultation, name='divine_delete_consultation'),   
    path('download/consultation-summary/<int:patient_id>/<int:visit_id>/', divine_Admin.download_consultation_summary_pdf, name='divine_download_consultation_summary_pdf' ),
    path('imaging/download/<int:imaging_id>/', divine_Admin.download_imaging_result_pdf, name='divine_download_imaging_result_pdf' ),
    path('imaging/download/all/<str:patient_mrn>/<str:visit_vst>/', divine_Admin.download_all_imaging_results_pdf, name='divine_download_all_imaging_results_pdf'),
    path('lab-result/download/<int:lab_id>/', divine_Admin.download_lab_result_pdf, name='divine_download_lab_result_pdf'),
    path('lab/download/all/<str:patient_mrn>/<str:visit_vst>/',divine_Admin.download_all_lab_results_pdf, name='divine_download_all_lab_results_pdf'),
    path('procedure/download/all/<str:patient_mrn>/<str:visit_vst>/', divine_Admin.download_all_procedures_pdf, name='divine_download_all_procedures_pdf'),
    path('procedure/result/download/<int:procedure_id>/', divine_Admin.download_procedure_result_pdf, name='divine_download_procedure_result_pdf'),
    path('download/prescription-notes/<int:patient_id>/<int:visit_id>/', divine_Admin.download_prescription_notes_pdf, name='divine_download_prescription_notes_pdf'),
    path('download-referral-pdf/<int:patient_id>/<int:visit_id>/', divine_Admin.download_referral_pdf, name='divine_download_referral_pdf'),
    path('download-counseling-pdf/<int:patient_id>/<int:visit_id>/', divine_Admin.download_counseling_pdf, name='divine_download_counseling_pdf'),
    path('download-discharge-pdf/<int:patient_id>/<int:visit_id>/', divine_Admin.download_discharge_pdf, name='divine_download_discharge_pdf'),
    path('download/observation/<int:patient_id>/<int:visit_id>/', divine_Admin.download_observation_pdf, name='divine_download_observation_pdf'),
    path('patient/imaging/view/', divine_Admin.patient_imaging_view, name="divine_patient_imaging_view"), 
  
]
