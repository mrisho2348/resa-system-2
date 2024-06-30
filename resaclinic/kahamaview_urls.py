from django.urls import path
from kahamahmis import kahamaViews

urlpatterns = [
    # Company related URLs
    path('company/add/', kahamaViews.company_registration_view, name='kahama_add_clinic_company'),


    # Medicine and Formulation related URLs
    path('get_formulation_unit/', kahamaViews.get_formulation_unit, name='kahama_get_formulation_unit'),
    path('get_medicine_formulation/', kahamaViews.get_medicine_formulation, name='kahama_get_medicine_formulation'),
    path('add_remote_medicine/', kahamaViews.add_remote_medicine, name='kahama_add_remote_medicine'),
    path('remotemedicine_list/', kahamaViews.remotemedicine_list, name='kahama_remotemedicine_list'),
    path('get_unit_price/', kahamaViews.get_unit_price, name='kahama_get_unit_price'),
    path('get_medicine_dosage/', kahamaViews.medicine_dosage, name='kahama_medicine_dosage'),

    # Report and Statistics URLs
    path('search_report/', kahamaViews.search_report, name='kahama_search_report'),
    path('patient_statistics/', kahamaViews.patient_statistics, name='kahama_patient_statistics'),

    # Service related URLs
    path('add_service/', kahamaViews.add_service, name='kahama_add_service'),

    # Patient related URLs
    path('delete_remote_patient/<int:patient_id>/', kahamaViews.delete_remote_patient, name='kahama_delete_remote_patient'),

    # Appointments
    path('appointment_view/', kahamaViews.appointment_view, name='kahama_appointment_view'),

    # Drug Division and Prescription related URLs
    path('get_drug_division_status/', kahamaViews.get_drug_division_status, name='kahama_get_drug_division_status'),
    path('verify_prescriptions/', kahamaViews.verify_prescriptions, name='kahama_verify_prescriptions'),
    path('unverify_prescriptions/', kahamaViews.unverify_prescriptions, name='kahama_unverify_prescriptions'),
    path('issue_prescriptions/', kahamaViews.issue_prescriptions, name='kahama_issue_prescriptions'),
    path('unissue_prescriptions/', kahamaViews.unissue_prescriptions, name='kahama_unissue_prescriptions'),
    path('update_payment_status/', kahamaViews.update_payment_status, name='kahama_pay_prescriptions'),
    path('unpay_prescriptions/', kahamaViews.unpay_prescriptions, name='kahama_unpay_prescriptions'),
    path('add_remoteprescription/', kahamaViews.add_remoteprescription, name='kahama_add_remoteprescription'),

    # Remote Equipment URLs
    path('remote-equipment/', kahamaViews.remote_equipment_list, name='kahama_remote_equipment_list'),
    path('add-remote-equipment/', kahamaViews.add_or_edit_remote_equipment, name='kahama_add_or_edit_remote_equipment'),
    path('delete_remote_equipment/', kahamaViews.delete_remote_equipment, name='kahama_delete_remote_equipment'),

    # Patient Observation and Lab Result URLs
    path('patient_observation_history_view/<str:mrn>/view/', kahamaViews.patient_observation_history_view, name="kahama_patient_observation_history_view"),
    path('patient_lab_result_history_view/<str:mrn>/view/', kahamaViews.patient_lab_result_history_view, name="kahama_patient_lab_result_history_view"),
    path('patient_laboratory_view/', kahamaViews.patient_laboratory_view, name="kahama_patient_laboratory_view"),
    path('patient_observation_view/', kahamaViews.patient_observation_view, name="kahama_patient_observation_view"),
    
    # Chief Complaint URLs
    path('save_chief_complaint/', kahamaViews.save_chief_complaint, name='kahama_save_chief_complaint'),
    path('delete_chief_complaint/<int:chief_complaint_id>/', kahamaViews.delete_chief_complaint, name='kahama_delete_chief_complaint'),
    path('get_chief_complaints/', kahamaViews.get_chief_complaints, name='kahama_get_chief_complaints'),
    
    # Health Record URLs
    path('health_record_list/', kahamaViews.health_record_list, name="kahama_health_record_list"),
    path('save_health_record/', kahamaViews.save_health_record, name="kahama_save_health_record"),
    path('delete_healthrecord/', kahamaViews.delete_healthrecord, name='kahama_delete_healthrecord'),
    
    # Reagent URLs
    path('reagent_list/', kahamaViews.reagent_list, name="kahama_reagent_list"),
    path('add_or_edit_reagent/', kahamaViews.add_or_edit_reagent, name="kahama_add_or_edit_reagent"),
    path('delete_reagent/', kahamaViews.delete_reagent, name="kahama_delete_reagent"),
    
    # Remote Procedure, Referral, Discharge URLs
    path('save_remoteprocedure/<int:patient_id>/<int:visit_id>/', kahamaViews.save_remoteprocedure, name='kahama_save_remoteprocedure'),
    path('save_remotereferral/<int:patient_id>/<int:visit_id>/', kahamaViews.save_remotereferral, name='kahama_save_remotereferral'),
    path('save_counsel/<int:patient_id>/<int:visit_id>/', kahamaViews.save_counsel, name='kahama_save_remote_counseling'),
    path('save_observation/<int:patient_id>/<int:visit_id>/', kahamaViews.save_observation, name='kahama_save_observation'),
    path('save_laboratory/<int:patient_id>/<int:visit_id>/', kahamaViews.save_laboratory, name='kahama_save_laboratory'),
    path('save_remote_discharges_notes/<int:patient_id>/<int:visit_id>/', kahamaViews.save_remote_discharges_notes, name='kahama_save_remote_discharges_notes'),
    
    # Remote Consultation Notes URLs
    path('save_remotesconsultation_notes/<int:patient_id>/<int:visit_id>/', kahamaViews.save_remotesconsultation_notes, name="kahama_save_remotesconsultation_notes"),
    path('save_remotesconsultation_notes_next/<int:patient_id>/<int:visit_id>/', kahamaViews.save_remotesconsultation_notes_next, name="kahama_save_remotesconsultation_notes_next"),
    
    # Miscellaneous
    path('get_frequency_name/', kahamaViews.get_frequency_name, name='kahama_get_frequency_name'),
    path('fetch-existing-data/', kahamaViews.fetch_existing_data, name='kahama_endpoint_to_fetch_existing_data'),
    path('add_primary_physical_examination/', kahamaViews.add_primary_physical_examination, name='kahama_add_primary_physical_examination'),
    path('edit_procedure_result/<int:patient_id>/<int:visit_id>/<int:procedure_id>/', kahamaViews.edit_procedure_result, name='kahama_edit_procedure_result'),
    path('edit_lab_result/<int:patient_id>/<int:visit_id>/<int:lab_id>/', kahamaViews.edit_lab_result, name='kahama_edit_lab_result'),
    path('save_patient_health_information/<int:patient_id>/', kahamaViews.save_patient_health_information, name="kahama_save_patient_health_information"),
]
