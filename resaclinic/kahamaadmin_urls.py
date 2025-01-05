from django.urls import path
from kahamahmis import kahamaAdmin

urlpatterns = [
    # Data retrieval paths
    path('get_patient_data_by_company/', kahamaAdmin.get_patient_data_by_company, name="kahama_get_patient_data_by_company"),
    path('get_gender_yearly_data/', kahamaAdmin.get_gender_yearly_data, name="kahama_get_gender_yearly_data"),
    path('get_gender_monthly_data/', kahamaAdmin.get_gender_monthly_data, name="kahama_get_gender_monthly_data"),
    
    # Management paths
    path('manage_country/', kahamaAdmin.manage_country, name="kahama_manage_country"),
    path('add_remote_consultation/', kahamaAdmin.add_remote_consultation, name="kahama_add_remote_consultation"),
    path('save_remote_service/', kahamaAdmin.save_remote_service, name="kahama_save_remote_service"),
      # URL for adding a new visit (no visit_id)
    path('save_patient_visit/<int:patient_id>/', kahamaAdmin.save_patient_visit_save, name='kahama_save_patient_visit_save'),
    # URL for editing an existing visit (with visit_id)
    path('save_patient_visit/<int:patient_id>/<int:visit_id>/', kahamaAdmin.save_patient_visit_save, name='kahama_save_patient_visit_edit'),    
    path('individual_visit/<int:patient_id>/', kahamaAdmin.individual_visit, name="kahama_individual_visit"),
    path('patient_info_form_edit/<int:patient_id>/', kahamaAdmin.patient_info_form_edit, name="kahama_patient_info_form_edit"),
    path('health_info_edit/<int:patient_id>/', kahamaAdmin.health_info_edit, name="kahama_health_info_edit"),
    path('patient_info_form/', kahamaAdmin.patient_info_form, name="kahama_patient_info_form"),
    path('patient_info_form/<int:patient_id>/', kahamaAdmin.patient_info_form, name='kahama_edit_patient'),
    path('save_diagnosis/', kahamaAdmin.save_diagnosis, name="kahama_save_diagnosis"),

    # Prescription and laboratory paths
    path('save_nextprescription/<int:patient_id>/<int:visit_id>/', kahamaAdmin.save_nextprescription, name='kahama_nextsave_prescription'),
    path('prescription/<int:patient_id>/<int:visit_id>/', kahamaAdmin.save_prescription, name='kahama_save_prescription'),
    path('save_nextlaboratory/<int:patient_id>/<int:visit_id>/', kahamaAdmin.save_nextlaboratory, name='kahama_nextsave_laboratory'),
    path('nextsave_remotereferral/<int:patient_id>/<int:visit_id>/', kahamaAdmin.save_nextremotereferral, name='kahama_nextsave_remotereferral'),
    path('save_nextcounsel/<int:patient_id>/<int:visit_id>/', kahamaAdmin.save_nextcounsel, name='kahama_nextsave_counsel'),
    path('save_nextremoteprocedure/<int:patient_id>/<int:visit_id>/', kahamaAdmin.save_nextremoteprocedure, name='kahama_nextsave_remoteprocedure'),
    path('save_nextobservation/<int:patient_id>/<int:visit_id>/', kahamaAdmin.save_nextobservation, name='kahama_nextsave_observation'),

    # Remote patient vitals
    path('save_remotepatient_vital/', kahamaAdmin.save_remotepatient_vital, name="kahama_save_remotepatient_vital"),
    path('save_remotepatient_vitals/<int:patient_id>/<int:visit_id>/', kahamaAdmin.save_remotepatient_vitals, name='kahama_save_remotepatient_vitals'),

    # Dashboard paths
    path('resa/dashboard/', kahamaAdmin.kahama_dashboard, name="kahama_dashboard"),
    
    # Add data paths
    path('add_disease/', kahamaAdmin.add_disease, name='kahama_add_disease'),
    path('add_insurance_company/', kahamaAdmin.add_insurance_company, name='kahama_add_insurance_company'),
    path('add_company/', kahamaAdmin.add_company, name='kahama_add_company'),
    path('add_pathodology_record/', kahamaAdmin.add_pathodology_record, name='kahama_add_pathodology_record'),

    # Staff paths
    path('staff_detail/<int:staff_id>/', kahamaAdmin.single_staff_detail, name='kahama_single_staff_detail'),
    path('edit_staff/<str:staff_id>/', kahamaAdmin.edit_staff, name='kahama_edit_staff'),
    path('edit_staff_save/', kahamaAdmin.edit_staff_save, name='kahama_edit_staff_save'),
    path('resa/update-staff-status/', kahamaAdmin.update_staff_status, name="kahama_update_staff_status"),
    path('save_staff_view/', kahamaAdmin.save_staff_view, name="kahama_save_staff_view"),
    
    # Consultation data
    path('save_consultation_data/', kahamaAdmin.save_consultation_data, name="kahama_save_consultation_data"),
    path('patient_procedure_history_view/<str:mrn>/', kahamaAdmin.patient_procedure_history_view, name="kahama_patient_procedure_history_view_mrn"),

    # Report paths
    path('resa/resa-report/', kahamaAdmin.resa_report, name="kahama_resa_report"),
    path('resa/reports-adjustments/', kahamaAdmin.reports_adjustments, name="kahama_reports_adjustments"),
    path('resa/reports-by-visit/', kahamaAdmin.reports_by_visit, name="kahama_reports_by_visit"),
    path('resa/reports-comprehensive/', kahamaAdmin.reports_comprehensive, name="kahama_reports_comprehensive"),
    path('resa/reports-patients-visit_summary/', kahamaAdmin.reports_patients_visit_summary, name="kahama_reports_patients_visit_summary"),
    path('resa/reports-patients/', kahamaAdmin.reports_patients, name="kahama_reports_patients"),
    path('resa/reports-service/', kahamaAdmin.reports_service, name="kahama_reports_service"),
    path('resareports-stock-ledger/', kahamaAdmin.reports_stock_ledger, name="kahama_reports_stock_ledger"),
    path('resa/reports-stock-level/', kahamaAdmin.reports_stock_level, name="kahama_reports_stock_level"),
    path('resa/reports-orders/', kahamaAdmin.reports_orders, name="kahama_reports_orders"),
    path('resa/individual-visit/', kahamaAdmin.individual_visit, name="kahama_individual_visit"),
    path('resa/product-summary/', kahamaAdmin.product_summary, name="kahama_product_summary"),

    # Manage paths
    path('patients/', kahamaAdmin.patients_list, name='kahama_patients_list'),
    path('diagnosis/', kahamaAdmin.diagnosis_list, name='kahama_diagnosis_list'),
    path('generatePDF/<int:patient_id>/<int:visit_id>/', kahamaAdmin.generatePDF, name='kahama_generatePDF'),
    path('remoteservice_list/', kahamaAdmin.remoteservice_list, name='kahama_remoteservice_list'),
    path('consultation-notes/', kahamaAdmin.consultation_notes_view, name='kahama_consultation_notes'),
    path('resa/patient_vital_all_list/', kahamaAdmin.patient_vital_all_list, name='kahama_patient_vital_all_list'),
    path('patient_vital_list/<int:patient_id>/<int:visit_id>/', kahamaAdmin.patient_vital_list, name='kahama_patient_vital_list'),
    path('patient_visit_details_view/<int:patient_id>/<int:visit_id>/', kahamaAdmin.patient_visit_details_view, name='kahama_patient_visit_details_view'),
    path('patient_health_record_view/<int:patient_id>/<int:visit_id>/', kahamaAdmin.patient_health_record_view, name='kahama_patient_health_record_view'),
    path('patient_visit_history/<int:patient_id>/', kahamaAdmin.patient_visit_history_view, name='kahama_patient_visit_history_view'),
    path('prescriptions/<str:visit_number>/<int:patient_id>/', kahamaAdmin.prescription_detail, name='kahama_prescription_detail'),
    path('prescription-billing/<str:visit_number>/<int:patient_id>/', kahamaAdmin.prescription_billing, name='kahama_prescription_billing'),
    path('prescription-notes/<str:visit_id>/<int:patient_id>/', kahamaAdmin.prescription_notes, name='kahama_prescription_notes'),
    path('prescriptions/', kahamaAdmin.prescription_list, name='kahama_prescription_list'),
    path('counseling/', kahamaAdmin.counseling_list_view, name='kahama_counseling_list'),
    path('discharge_notes/', kahamaAdmin.discharge_notes_list_view, name='kahama_discharge_notes_list'),
    path('observation_records/', kahamaAdmin.observation_record_list_view, name='kahama_observation_record_list'),

    # Referral paths
    path('resa/manage-referral/', kahamaAdmin.manage_referral, name='kahama_manage_referral'),
    path('resa/patient-procedure-view/', kahamaAdmin.patient_procedure_view, name='kahama_patient_procedure_view'),
    path('out_of_stock_medicines_view/', kahamaAdmin.out_of_stock_medicines_view, name='kahama_out_of_stock_medicines_view'),
    path('resa/all-patients/', kahamaAdmin.manage_patient, name="kahama_manage_patient"),
    path('resa/consultation-queue/', kahamaAdmin.manage_consultation, name="kahama_manage_consultation"),
    path('resa/manage-company/', kahamaAdmin.manage_company, name="kahama_manage_company"),
    path('resa/manage-disease/', kahamaAdmin.manage_disease, name="kahama_manage_disease"),
    path('resa/manage-staff/', kahamaAdmin.manage_staff, name="kahama_manage_staff"),
    path('resa/manage-insurance/', kahamaAdmin.manage_insurance, name="kahama_manage_insurance"),
    path('resa/manage-adjustment/', kahamaAdmin.manage_adjustment, name="kahama_manage_adjustment"),
    path('resa/manage-pathodology/', kahamaAdmin.manage_pathodology, name="kahama_manage_pathodology"),

    # Appointment paths
    path('resa/appointments/', kahamaAdmin.appointment_list_view, name='kahama_appointment_list'),
    path('in_stock_medicines_view/', kahamaAdmin.in_stock_medicines_view, name='kahama_in_stock_medicines_view'),
    path('confirm_meeting/<int:appointment_id>/', kahamaAdmin.confirm_meeting, name='kahama_confirm_meeting'),
    path('generate-bill/<int:procedure_id>/', kahamaAdmin.generate_billing, name='kahama_generate_billing'),
    path('edit_meeting/<int:appointment_id>/', kahamaAdmin.edit_meeting, name='kahama_edit_meeting'),
    path('resa/medicine-expired-list/', kahamaAdmin.medicine_expired_list, name='kahama_medicine_expired_list'),
    path('save_referral/', kahamaAdmin.save_referral, name='kahama_save_referral'),
    path('change_referral_status/', kahamaAdmin.change_referral_status, name='kahama_change_referral_status'),

    # API paths
    path('api/out-of-stock-medicines/', kahamaAdmin.out_of_stock_medicines, name='kahama_out_of_stock_medicines'),
    path('get_all_medicine_data/', kahamaAdmin.get_all_medicine_data, name='kahama_get_all_medicine_data'),
    path('get_all_frequency_data/', kahamaAdmin.get_all_frequency_data, name='kahama_get_all_frequency_data'),
]
