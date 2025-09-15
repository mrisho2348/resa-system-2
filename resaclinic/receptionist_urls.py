
from django.urls import include, path, re_path

from clinic.ReceptionistView import * 


urlpatterns = [
      
        path('save_laboratory/<int:patient_id>/<int:visit_id>/', save_laboratory, name='receptionist_save_laboratory'),

        path('save_remoteprocedure/<int:patient_id>/<int:visit_id>/', save_remoteprocedure, name='receptionist_save_remoteprocedure'),
        path('save_observation/<int:patient_id>/<int:visit_id>/', save_observation, name='receptionist_save_observation'),
      
        path('update_payment_status/', update_payment_status, name='receptionist_pay_prescriptions'),
   
        path('add_investigation/', add_investigation, name='receptionist_add_investigation'),

        path('receptionist/get-gender-yearly-data/', get_gender_yearly_data, name="receptionist_get_gender_yearly_data"),
        path('receptionist/get-gender-monthly-data/', get_gender_monthly_data, name="receptionist_get_gender_monthly_data"),
        path('add_imaging/', add_imaging, name='receptionist_add_imaging'),
        path('ambulance_order/', ambulance_order_create_or_update, name='receptionist_ambulance_order_create_or_update'),
        path('ambulance_order/<int:order_id>/', ambulance_order_create_or_update, name='receptionist_ambulance_order_edit'),
        path('receptionist/update-orderpayment-status/', update_orderpayment_status, name='receptionist_update_orderpayment_status'),

        path('patients/<int:patient_id>/visits/<int:visit_id>/ambulance_order/', save_ambulance_order, name='receptionist_save_ambulance_order'),
        path('patients/<int:patient_id>/visits/<int:visit_id>/ambulance_order/<int:ambulance_id>/', save_ambulance_order, name='receptionist_edit_ambulance_order'),
        path('walkin-prescriptions/', walkin_prescription_list, name='receptionist_walkin_prescription_list'),
        path('update-walkin-payment-status/', update_walkin_payment_status, name='receptionist_update_walkin_payment_status'),
        path('generate_walkin_receipt_pdf/<int:visit_id>/', generate_walkin_receipt_pdf, name='receptionist_generate_walkin_receipt_pdf'),
        path('download_prescription_notes/<int:visit_id>/', download_prescription_notes, name='receptionist_download_prescription_notes'),
        path('add_consultation/', add_consultation, name='receptionist_add_consultation'),
        path('add_procedure/', add_procedure, name='receptionist_add_procedure'),
        path('get-procedure-cost/', get_procedure_cost, name='receptionist_get_procedure_cost'),   
        path('receptionist_dashboard/', receptionist_dashboard, name='receptionist_dashboard'),    
        path('receptionist/profile/', receptionist_profile, name='receptionist_profile'),
        path('resa/receptionist/change-password/', change_password, name='receptionist_change_password'),
        path('edit-profile/<int:pk>/', EditStaffProfileView.as_view(), name='receptionist_edit_staff_profile'),
        path('add_patient/', add_patient, name='receptionist_add_patient'),

        path('vehicle_detail/<int:order_id>/', vehicle_detail, name='receptionist_vehicle_detail'),    
        path('vehicle_ambulance_view/',vehicle_ambulance_view, name="receptionist_vehicle_ambulance_view"),        
        path('ambulance_order_detail/<int:order_id>/', ambulance_order_detail, name='receptionist_ambulance_order_detail'),        

        path('ambulance_order_view/',ambulance_order_view, name="receptionist_ambulance_order_view"),     
    
        path('save_edited_patient/',save_edited_patient, name="receptionist_save_edited_patient"),
        path('add_patient_visit/',add_patient_visit, name="receptionist_add_patient_visit"),      
        
        path('vitals/save/<int:patient_id>/<int:visit_id>/', save_remotepatient_vitals, name='doctor_vitals_save'),
        path('resa/patient_vital_all_listt/', patient_vital_all_list, name='receptionist_patient_vital_all_list'),
        path('patient_consultation_detail/<int:patient_id>/<int:visit_id>/', patient_consultation_detail, name='receptionist_patient_consultation_detail'),
       
        path('patient_health_record/<int:patient_id>/<int:visit_id>/', patient_health_record, name='receptionist_patient_health_record'),
     
        path('patient_visit_history/<int:patient_id>/', patient_visit_history_view, name='receptionist_patient_visit_history_view'),       
        path('prescriptions/', prescription_list, name='receptionist_prescription_list'),       
        path('resa/manage-referral/', manage_referral, name='receptionist_manage_referral'),
    
        path('manage_patients/',manage_patients, name="receptionist_manage_patients"),
        path('resa/save/remotepatient/vital',save_remotepatient_vital, name="receptionist_save_remotepatient_vital"),
        path('resa/consultation-queue',manage_consultation, name="receptionist_manage_consultation"),
        path('resa/manage-service',manage_service, name="receptionist_manage_service"),
        path('employee/', employee_detail, name='receptionist_employee_detail'),
        path('appointment_list/', appointment_list_view, name='receptionist_appointment_list'),       
      
        path('save_referral/', save_referral, name='receptionist_save_referral'),
        path('all_orders_view/', all_orders_view, name='receptionist_all_orders_view'),
        path('change_referral_status/', change_referral_status, name='receptionist_change_referral_status'),     
        path('receptionist/notifications/', receptionist_notifications_view, name='receptionist_notifications'),
        path('receptionist/notifications/api/', receptionist_all_notifications_api, name='receptionist_all_notifications_api'),
        path('receptionist/notifications/toggle/', receptionist_toggle_notification_api, name='receptionist_toggle_notification_api'),
        path('receptionist/notifications/delete/', receptionist_delete_notification_api, name='receptionist_delete_notification_api'),

        path('service_status_data/', service_status_data, name='receptionist_service_status_data'),
        path('update-appointment-status/', update_appointment_status, name='receptionist_update_appointments'),  
        path('update-appointment-details/', update_appointment_details, name='receptionist_update_appointment_details'),   
        # edit urls        
      
        path('appointment_view/', appointment_view, name='receptionist_appointment_view'), 


        path('patient/imaging/view/', patient_imaging_view, name="receptionist_patient_imaging_view"), 
        path('patient/laboratory/view/', patient_laboratory_view, name="receptionist_patient_laboratory_view"), 

        path('resa/patient-procedure-view/', patient_procedure_view, name='receptionist_patient_procedure_view'),   

        path('resa/manage-referral/', manage_referral, name='receptionist_manage_referral'), 
       
        path('counseling/', counseling_list_view, name='receptionist_counseling_list'),

        path('discharge_notes/', discharge_notes_list_view, name='receptionist_discharge_notes_list'),

        path('observation_records/', observation_record_list_view, name='receptionist_observation_record_list'),
        path('save_observation/<int:patient_id>/<int:visit_id>/', save_observation, name='receptionist_save_observation'),
     
        path('consultation-notes/', consultation_notes_view, name='receptionist_consultation_notes'),
        path('api/earnings/', get_earnings_data, name='receptionist_get_earnings_data'),
        path('add/radiology/<int:patient_id>/<int:visit_id>/', add_radiology, name='receptionist_add_radiology'),
        re_path(r'^doctor/add_imaging/$', add_imaging, name='receptionist_add_imaging'),
        path('reception-dashboard-counts/', reception_dashboard_counts, name='reception_dashboard_counts'),
        path('receptionist/dashboard-data/', receptionist_dashboard_data, name='receptionist_dashboard_data'),

        path('receptionist/download-invoice/<int:patient_id>/<int:visit_id>/', download_invoice_bill_pdf, name='receptionist_download_invoice_bill'),
        path('download/consultation-summary/<int:patient_id>/<int:visit_id>/', download_consultation_summary_pdf, name='receptionist_download_consultation_summary_pdf' ),
        path('imaging/download/<int:imaging_id>/', download_imaging_result_pdf, name='receptionist_download_imaging_result_pdf' ),
        path('imaging/download/all/<str:patient_mrn>/<str:visit_vst>/', download_all_imaging_results_pdf, name='receptionist_download_all_imaging_results_pdf'),
        path('lab-result/download/<int:lab_id>/', download_lab_result_pdf, name='receptionist_download_lab_result_pdf'),
        path('lab/download/all/<str:patient_mrn>/<str:visit_vst>/',download_all_lab_results_pdf, name='receptionist_download_all_lab_results_pdf'),
        path('procedure/download/all/<str:patient_mrn>/<str:visit_vst>/', download_all_procedures_pdf, name='receptionist_download_all_procedures_pdf'),
        path('procedure/result/download/<int:procedure_id>/', download_procedure_result_pdf, name='receptionist_download_procedure_result_pdf'),
        path('download/prescription-bill/<int:patient_id>/<int:visit_id>/', download_prescription_bill_pdf, name='receptionist_download_prescription_bill_pdf'),
        path('download/prescription-notes/<int:patient_id>/<int:visit_id>/', download_prescription_notes_pdf, name='receptionist_download_prescription_notes_pdf'),
        path('download-referral-pdf/<int:patient_id>/<int:visit_id>/', download_referral_pdf, name='receptionist_download_referral_pdf'),
        path('download-counseling-pdf/<int:patient_id>/<int:visit_id>/', download_counseling_pdf, name='receptionist_download_counseling_pdf'),
        path('download-discharge-pdf/<int:patient_id>/<int:visit_id>/', download_discharge_pdf, name='receptionist_download_discharge_pdf'),
        path('download/observation/<int:patient_id>/<int:visit_id>/', download_observation_pdf, name='receptionist_download_observation_pdf'),
        path('analytics/patient-status/', get_patient_completion_status, name='receptionist_patient_status_report'),

     

]
