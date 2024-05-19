
from django.urls import include, path

from clinic import LabTechnicianView, delete, editView, imports


urlpatterns = [    
        path('add_consultation/', LabTechnicianView.add_consultation, name='lab_add_consultation'),
        path('labtechnician_dashboard/', LabTechnicianView.labtechnician_dashboard, name='labtechnician_dashboard'),
        path('new_procedure_order/', LabTechnicianView.new_procedure_order, name='lab_new_procedure_order'),
        path('new_radiology_order/', LabTechnicianView.new_radiology_order, name='lab_new_radiology_order'),
        path('fetch_order_counts/', LabTechnicianView.fetch_order_counts_view, name='fetch_order_counts'),
        path('fetch_laborders_counts/', LabTechnicianView.fetch_laborders_counts, name='fetch_laborders_counts'),
        path('lab_unread_orders/', LabTechnicianView.lab_unread_orders_view, name='lab_unread_orders'),
        path('lab_read_orders/', LabTechnicianView.lab_read_orders_view, name='lab_read_orders'),
        path('save_lab_order_result/<int:order_id>/', LabTechnicianView.save_lab_order_result, name='save_lab_order_result'),
        path('prescriptions/<str:visit_number>/<int:patient_id>/', LabTechnicianView.prescription_detail, name='lab_prescription_detail'),
        path('new_consultation_order/',LabTechnicianView.new_consultation_order, name="lab_new_consultation_order"),
        path('all_orders_view/', LabTechnicianView.all_orders_view, name='lab_all_orders_view'),
        path('save_edited_patient/',LabTechnicianView.save_edited_patient, name="lab_save_edited_patient"),
        
        path('fetch_model_data/', LabTechnicianView.fetch_model_data, name='lab_fetch_model_data'),
        path('manage_laboratory/', LabTechnicianView.manage_laboratory, name='lab_manage_laboratory'),
        path('save_consultation_data/', LabTechnicianView.save_consultation_data, name='lab_save_consultation_data'),
      
        path('add_pathodology_record/', LabTechnicianView.add_pathodology_record, name='lab_add_pathodology_record'),

        path('accounts/', include('django.contrib.auth.urls')), 
        path('staff_detail/<int:staff_id>/', LabTechnicianView.single_staff_detail, name='lab_single_staff_detail'),
        path('view-patient/<int:patient_id>/', LabTechnicianView.view_patient, name='lab_view_patient'),        
      
   
        
          
        # manage urls      
        path('get-procedure-cost/', LabTechnicianView.get_procedure_cost, name='lab_get_procedure_cost'),   
        path('get_patient_details/<int:patient_id>/', LabTechnicianView.get_patient_details, name='lab_get_patient_details'),
    
        path('add_investigation/', LabTechnicianView.add_investigation, name='lab_add_investigation'),
        path('add_imaging/', LabTechnicianView.add_imaging, name='lab_add_imaging'),
        path('add_procedure/', LabTechnicianView.add_procedure, name='lab_add_procedure'),    
        path('get_unit_price/', LabTechnicianView.get_unit_price, name='lab_get_unit_price'),     
    
        path('resa/patient_vital_all_listt/', LabTechnicianView.patient_vital_all_list, name='lab_patient_vital_all_list'),  
        path('patient_consultation_detail/<int:patient_id>/<int:visit_id>/', LabTechnicianView.patient_consultation_detail, name='lab_patient_consultation_detail'),
        path('save_laboratory/<int:patient_id>/<int:visit_id>/', LabTechnicianView.save_laboratory, name='lab_save_laboratory'),
        path('save_remoteprocedure/<int:patient_id>/<int:visit_id>/', LabTechnicianView.save_remoteprocedure, name='lab_save_remoteprocedure'),
        path('save_observation/<int:patient_id>/<int:visit_id>/', LabTechnicianView.save_observation, name='lab_save_observation'),
        path('patient_vital_list/<int:patient_id>/', LabTechnicianView.patient_vital_list, name='lab_patient_vital_list'),
        path('patient_health_record_view/<int:patient_id>/<int:visit_id>/', LabTechnicianView.patient_health_record_view, name='lab_patient_health_record_view'),
        path('patient_visit_history/<int:patient_id>/', LabTechnicianView.patient_visit_history_view, name='lab_patient_visit_history_view'),
        path('prescriptions/', LabTechnicianView.prescription_list, name='lab_prescription_list'),       
        path('resa/all-patients',LabTechnicianView.manage_patient, name="lab_manage_patient"),
        path('resa/consultation-queue',LabTechnicianView.manage_consultation, name="lab_manage_consultation"),          
        
        path('resa/appointments/', LabTechnicianView.appointment_list_view, name='lab_appointment_list'),
        path('notifications/', LabTechnicianView.notification_view, name='lab_notification_view'),
        path('confirm_meeting/<int:appointment_id>/', LabTechnicianView.confirm_meeting, name='lab_confirm_meeting'),
        path('generate-bill/<int:procedure_id>/', LabTechnicianView.generate_billing, name='lab_generate_billing'),
        path('edit_meeting/<int:appointment_id>/', LabTechnicianView.edit_meeting, name='lab_edit_meeting'), 
        path('save_radiology/', LabTechnicianView.save_radiology, name='lab_save_radiology'),
        path('save_procedure/', LabTechnicianView.save_procedure, name='lab_save_procedure'),  
        path('invoice/<int:order_id>/', LabTechnicianView.generate_invoice_bill, name='lab_generate_invoice_bill'),
        
        # imports urls 
        path('resa/import_Import/import_patient_vital_records',imports.import_patient_vital_records, name="lab_import_patient_vital_records"),      
        path('import_prescription_records', imports.import_prescription_records, name='lab_import_prescription_records'),
        path('import_consultation_notes_records', imports.import_consultation_notes_records, name='lab_import_consultation_notes_records'),   
        path('import-patients/', imports.import_patient_records, name='lab_import_patient_records'),
        path('import-pathology-records/', imports.import_pathology_records, name='lab_import_pathology_records'),
        path('import-medicine-records/', imports.import_medicine_records, name='lab_import_medicine_records'),
        path('import-procedure-records/', imports.import_procedure_records, name='lab_import_procedure_records'),
        path('import-referral-records/', imports.import_referral_records, name='lab_import_referral_records'),
              
        # edit urls              
        path('pathodology/<int:pathodology_id>/edit/', editView.edit_pathodology, name='lab_edit_pathodology'),    
        path('update_consultation_data/<int:appointment_id>/', editView.update_consultation_data, name='lab_update_consultation_data'),         
        path('update_consultation_fee/', editView.update_consultation_fee, name='lab_update_consultation_fee'), 
        path('edit_procedure/', editView.edit_procedure, name='lab_edit_procedure'), 
        path('edit_referral/', editView.edit_referral, name='lab_edit_referral'), 
        path('Patient/<int:patient_id>/add/', LabTechnicianView.appointment_view, name='lab_appointment_view'), 
        path('appointment_view/<int:patient_id>/', LabTechnicianView.appointment_view_remote, name='lab_appointment_view_remote'),
        path('patient-procedure-history/<str:mrn>/view/', LabTechnicianView.patient_procedure_history_view, name='lab_patient_procedure_history_view_mrn'),   
        
        # delete urls        
      
        
]
