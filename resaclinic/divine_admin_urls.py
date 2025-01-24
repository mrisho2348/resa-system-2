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
      # URL for adding a new visit (no visit_id)
    path('save_patient_visit/<int:patient_id>/', divine_Admin.save_patient_visit_save, name='divine_save_patient_visit_save'),
    # URL for editing an existing visit (with visit_id)
    path('save_patient_visit/<int:patient_id>/<int:visit_id>/', divine_Admin.save_patient_visit_save, name='divine_save_patient_visit_edit'),    
    path('individual_visit/<int:patient_id>/', divine_Admin.individual_visit, name="divine_individual_visit"),
    path('patient_info_form_edit/<int:patient_id>/', divine_Admin.patient_info_form_edit, name="divine_patient_info_form_edit"),
    path('health_info_edit/<int:patient_id>/', divine_Admin.health_info_edit, name="divine_health_info_edit"),
    path('save_diagnosis/', divine_Admin.save_diagnosis, name="divine_save_diagnosis"),


    # Remote patient vitals

    path('save_remotepatient_vitals/<int:patient_id>/<int:visit_id>/', divine_Admin.save_remotepatient_vitals, name='divine_save_remotepatient_vitals'),

    # Dashboard paths
    path('resa/dashboard/', divine_Admin.divine_dashboard, name="divine_dashboard"),
    
    # Add data paths
    path('add_disease/', divine_Admin.add_disease, name='divine_add_disease'),
    path('add_insurance_company/', divine_Admin.add_insurance_company, name='divine_add_insurance_company'),
    path('add_company/', divine_Admin.add_company, name='divine_add_company'),
    path('add_pathodology_record/', divine_Admin.add_pathodology_record, name='divine_add_pathodology_record'),

    # Staff paths
    path('staff_detail/<int:staff_id>/', divine_Admin.single_staff_detail, name='divine_single_staff_detail'),
    path('edit_staff/<str:staff_id>/', divine_Admin.edit_staff, name='divine_edit_staff'),
    path('edit_staff_save/', divine_Admin.edit_staff_save, name='divine_edit_staff_save'),
    path('resa/update-staff-status/', divine_Admin.update_staff_status, name="divine_update_staff_status"),
    path('save_staff_view/', divine_Admin.save_staff_view, name="divine_save_staff_view"),
    
    # Consultation data

    path('patient_procedure_history_view/<str:mrn>/', divine_Admin.patient_procedure_history_view, name="divine_patient_procedure_history_view_mrn"),

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

    # Manage paths
    path('patients/', divine_Admin.patients_list, name='divine_patients_list'),
    path('diagnosis/', divine_Admin.diagnosis_list, name='divine_diagnosis_list'),
    path('generatePDF/<int:patient_id>/<int:visit_id>/', divine_Admin.generatePDF, name='divine_generatePDF'),
    path('remoteservice_list/', divine_Admin.remoteservice_list, name='divine_remoteservice_list'),
    path('consultation-notes/', divine_Admin.consultation_notes_view, name='divine_consultation_notes'),
    path('resa/patient_vital_all_list/', divine_Admin.patient_vital_all_list, name='divine_patient_vital_all_list'),
    path('details/<str:patient_mrn>/<str:visit_number>/', divine_Admin.patient_vital_detail, name='divine_patient_vital_detail'),

    path('patient_visit_details_view/<int:patient_id>/<int:visit_id>/', divine_Admin.patient_visit_details_view, name='divine_patient_visit_details_view'),
   
    path('patient_visit_history/<int:patient_id>/', divine_Admin.patient_visit_history_view, name='divine_patient_visit_history_view'),

    path('prescription-notes/<str:visit_id>/<int:patient_id>/', divine_Admin.prescription_notes, name='divine_prescription_notes'),
    path('prescriptions/', divine_Admin.prescription_list, name='divine_prescription_list'),
    path('counseling/', divine_Admin.counseling_list_view, name='divine_counseling_list'),
    path('discharge_notes/', divine_Admin.discharge_notes_list_view, name='divine_discharge_notes_list'),
    path('observation_records/', divine_Admin.observation_record_list_view, name='divine_observation_record_list'),

    # Referral paths
    path('resa/manage-referral/', divine_Admin.manage_referral, name='divine_manage_referral'),
    path('resa/patient-procedure-view/', divine_Admin.patient_procedure_view, name='divine_patient_procedure_view'),
    path('procedure/detail/<str:mrn>/<str:visit_number>/', divine_Admin.patient_procedure_detail_view, name='divine_patient_procedure_detail_view'),
    path('out_of_stock_medicines_view/', divine_Admin.out_of_stock_medicines_view, name='divine_out_of_stock_medicines_view'),

    path('resa/manage-company/', divine_Admin.manage_company, name="divine_manage_company"),
    path('resa/manage-disease/', divine_Admin.manage_disease, name="divine_manage_disease"),
    path('resa/manage-staff/', divine_Admin.manage_staff, name="divine_manage_staff"),
    path('resa/manage-insurance/', divine_Admin.manage_insurance, name="divine_manage_insurance"),
    path('resa/manage-adjustment/', divine_Admin.manage_adjustment, name="divine_manage_adjustment"),
    path('resa/manage-pathodology/', divine_Admin.manage_pathodology, name="divine_manage_pathodology"),

    # Appointment paths
    path('resa/appointments/', divine_Admin.appointment_list_view, name='divine_appointment_list'),
    path('in_stock_medicines_view/', divine_Admin.in_stock_medicines_view, name='divine_in_stock_medicines_view'),
    # API paths
    path('api/out-of-stock-medicines/', divine_Admin.out_of_stock_medicines, name='divine_out_of_stock_medicines'),    
      # Company related URLs
    path('company/add/', divine_Admin.company_registration_view, name='divine_add_clinic_company'),


    # Medicine and Formulation related URLs

    path('add_remote_medicine/', divine_Admin.add_remote_medicine, name='divine_add_remote_medicine'),
    path('remotemedicine_list/', divine_Admin.remotemedicine_list, name='divine_remotemedicine_list'),


    # Report and Statistics URLs
    path('search_report/', divine_Admin.search_report, name='divine_search_report'),
    path('patient_statistics/', divine_Admin.patient_statistics, name='divine_patient_statistics'),

    # Service related URLs
    path('add_service/', divine_Admin.add_service, name='divine_add_service'),

    # Patient related URLs
    path('delete_remote_patient/<int:patient_id>/', divine_Admin.delete_remote_patient, name='divine_delete_remote_patient'),


    # Remote Equipment URLs
    path('remote-equipment/', divine_Admin.remote_equipment_list, name='divine_remote_equipment_list'),
    path('add-remote-equipment/', divine_Admin.add_or_edit_remote_equipment, name='divine_add_or_edit_remote_equipment'),
    path('delete_remote_equipment/', divine_Admin.delete_remote_equipment, name='divine_delete_remote_equipment'),

    # Patient Observation and Lab Result URLs
    path('patient_observation_history_view/<str:mrn>/view/', divine_Admin.patient_observation_history_view, name="divine_patient_observation_history_view"),
    path('patient_lab_result_history_view/<str:mrn>/view/', divine_Admin.patient_lab_result_history_view, name="divine_patient_lab_result_history_view"),
    path('patient_laboratory_view/', divine_Admin.patient_laboratory_view, name="divine_patient_laboratory_view"),

    path('lab-details/<str:mrn>/<str:visit_number>/', divine_Admin.patient_lab_details_view, name='divine_patient_lab_details_view'),
    path('patient_observation_view/', divine_Admin.patient_observation_view, name="divine_patient_observation_view"),
    
    # Chief Complaint URLs

    path('delete_chief_complaint/<int:chief_complaint_id>/', divine_Admin.delete_chief_complaint, name='divine_delete_chief_complaint'),

    
    # Health Record URLs
    path('health_record_list/', divine_Admin.health_record_list, name="divine_health_record_list"),
    path('save_health_record/', divine_Admin.save_health_record, name="divine_save_health_record"),
    path('delete_healthrecord/', divine_Admin.delete_healthrecord, name='divine_delete_healthrecord'),
    
    # Reagent URLs
    path('reagent_list/', divine_Admin.reagent_list, name="divine_reagent_list"),
    path('add_or_edit_reagent/', divine_Admin.add_or_edit_reagent, name="divine_add_or_edit_reagent"),
    path('delete_reagent/', divine_Admin.delete_reagent, name="divine_delete_reagent"),
    
    # Remote Procedure, Referral, Discharge URLs
  
    path('save_remotereferral/<int:patient_id>/<int:visit_id>/', divine_Admin.save_remotereferral, name='divine_save_remotereferral'),
    path('save_counsel/<int:patient_id>/<int:visit_id>/', divine_Admin.save_counsel, name='divine_save_remote_counseling'),
    path('save_observation/<int:patient_id>/<int:visit_id>/', divine_Admin.save_observation, name='divine_save_observation'),   
    path('save_remote_discharges_notes/<int:patient_id>/<int:visit_id>/', divine_Admin.save_remote_discharges_notes, name='divine_save_remote_discharges_notes'),
    
    # Remote Consultation Notes URLs
    path('save_remotesconsultation_notes/<int:patient_id>/<int:visit_id>/', divine_Admin.save_remotesconsultation_notes, name="divine_save_remotesconsultation_notes"),
    
    
    # Miscellaneous

    path('fetch-existing-data/', divine_Admin.fetch_existing_data, name='divine_endpoint_to_fetch_existing_data'),    
    path('edit_procedure_result/<int:patient_id>/<int:visit_id>/<int:procedure_id>/', divine_Admin.edit_procedure_result, name='divine_edit_procedure_result'),
    path('edit_lab_result/<int:patient_id>/<int:visit_id>/<int:lab_id>/', divine_Admin.edit_lab_result, name='divine_edit_lab_result'),
  
]
