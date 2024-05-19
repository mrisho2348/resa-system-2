
from django.urls import include, path

from clinic import DoctorView, delete, editView, imports


urlpatterns = [
     
   
        path('doctor_dashboard/', DoctorView.doctor_dashboard, name='doctor_dashboard'),
        path('fetch_lab_order_counts_view/', DoctorView.fetch_lab_order_counts_view, name='fetch_lab_order_counts_view'),
        path('patient_lab_view/', DoctorView.patient_lab_view, name='patient_lab_view'),
        path('new_procedure_order/', DoctorView.new_procedure_order, name='new_procedure_order'),
        path('edit_procedure_result/<int:patient_id>/<int:visit_id>/<int:procedure_id>/', DoctorView.edit_procedure_result, name='edit_procedure_result'),
        path('edit_radiology_result/<int:patient_id>/<int:visit_id>/<int:radiology_id>/', DoctorView.edit_radiology_result, name='edit_radiology_result'),
        path('edit_lab_result/<int:patient_id>/<int:visit_id>/<int:lab_id>/', DoctorView.edit_lab_result, name='edit_lab_result'),
        path('new_lab_order/', DoctorView.new_lab_order, name='new_lab_order'),
        path('fetch_procedure_order_counts_view/', DoctorView.fetch_procedure_order_counts_view, name='fetch_procedure_order_counts_view'),
        path('fetch_radiology_order_counts_view/', DoctorView.fetch_radiology_order_counts_view, name='fetch_radiology_order_counts_view'),
        path('new_radiology_order/', DoctorView.new_radiology_order, name='new_radiology_order'),
        path('fetch_order_counts/', DoctorView.fetch_order_counts_view, name='fetch_order_counts'),
        path('fetch_consultation_counts/', DoctorView.fetch_consultation_counts, name='fetch_consultation_counts'),
        path('unread_appointments/', DoctorView.unread_appointments_view, name='unread_appointments'),
        path('read_appointments/', DoctorView.read_appointments_view, name='read_appointments'),
        path('prescriptions/<str:visit_number>/<int:patient_id>/', DoctorView.prescription_detail, name='prescription_detail'),
        path('prescriptions-billing/<str:visit_number>/<int:patient_id>/', DoctorView.prescription_billing, name='prescription_billing'),
        path('prescriptions-notes/<str:visit_number>/<int:patient_id>/', DoctorView.prescription_notes, name='prescription_notes'),
        path('new_consultation_order/',DoctorView.new_consultation_order, name="new_consultation_order"),
        path('add_remotepatient_visit/',DoctorView.add_remotepatient_visit, name="add_remotepatient_visit"),
        path('save_consultation_notes/',DoctorView.save_consultation_notes, name="save_consultation_notes"),
        path('save_patient_vital/',DoctorView.save_patient_vital, name="save_patient_vital"),
        path('add_prescription/',DoctorView.add_prescription, name="add_prescription"),
        path('save_edited_patient/',DoctorView.save_edited_patient, name="save_edited_patient"),
        path('add_patient_visit/',DoctorView.add_patient_visit, name="add_patient_visit"),
        path('fetch_model_data/', DoctorView.fetch_model_data, name='fetch_model_data'),
        path('manage_laboratory/', DoctorView.manage_laboratory, name='manage_laboratory'),
        path('save_consultation_data/', DoctorView.save_consultation_data, name='save_consultation_data'),
        path('save_consultation_fee/', DoctorView.save_consultation_fee, name='save_consultation_fee'),
        path('add_pathodology_record/', DoctorView.add_pathodology_record, name='add_pathodology_record'),
        path('add_remotepatient_visit', DoctorView.add_remotepatient_visit, name='add_remotepatient_visit'),  # Move this line here
        path('add_patient/', DoctorView.add_patient, name='add_patient'),
        path('accounts/', include('django.contrib.auth.urls')), 
        path('staff_detail/<int:staff_id>/', DoctorView.single_staff_detail, name='single_staff_detail'),
        path('view-patient/<int:patient_id>/', DoctorView.view_patient, name='view_patient'),        
        path('get_item_quantity/',DoctorView.get_item_quantity, name="get_item_quantity"),
   
        
          
        # manage urls      
        path('get-procedure-cost/', DoctorView.get_procedure_cost, name='get_procedure_cost'),   
        path('get_patient_details/<int:patient_id>/', DoctorView.get_patient_details, name='get_patient_details'),
        path('save_counseling/', DoctorView.save_counseling, name='save_counseling'),
        path('add_investigation/', DoctorView.add_investigation, name='add_investigation'),
        path('add_imaging/', DoctorView.add_imaging, name='add_imaging'),
        path('add_procedure/', DoctorView.add_procedure, name='add_procedure'),
        path('add_remoteprescription/', DoctorView.add_remoteprescription, name='add_remoteprescription'),
        path('get_unit_price/', DoctorView.get_unit_price, name='get_unit_price'),        
        path('get_drug_division_status/', DoctorView.get_drug_division_status, name='get_drug_division_status'),        
        path('get_medicine_formulation/', DoctorView.get_medicine_formulation, name='get_medicine_formulation'),        
        path('get_formulation_unit/', DoctorView.get_formulation_unit, name='get_formulation_unit'),        
        path('get_frequency_name/', DoctorView.get_frequency_name, name='get_frequency_name'),        
        path('medicine_dosage/', DoctorView.medicine_dosage, name='medicine_dosage'),        
        path('save_remoteconsultation_notes/', DoctorView.save_remoteconsultation_notes, name='save_remoteconsultation_notes'),
        path('consultation-notes/', DoctorView.consultation_notes_view, name='consultation_notes'),
        path('resa/patient_vital_all_listt/', DoctorView.patient_vital_all_list, name='patient_vital_all_list'),    
        path('save_prescription/<int:patient_id>/<int:visit_id>/', DoctorView.save_prescription, name='save_prescription'),
        path('save_laboratory/<int:patient_id>/<int:visit_id>/', DoctorView.save_laboratory, name='save_laboratory'),
        path('save_remotereferral/<int:patient_id>/<int:visit_id>/', DoctorView.save_remotereferral, name='save_remotereferral'),
        path('save_remoteprocedure/<int:patient_id>/<int:visit_id>/', DoctorView.save_remoteprocedure, name='save_remoteprocedure'),
        path('save_observation/<int:patient_id>/<int:visit_id>/', DoctorView.save_observation, name='save_observation'),
        path('save_remotesconsultation_notes/<int:patient_id>/<int:visit_id>/', DoctorView.save_remotesconsultation_notes, name='save_remotesconsultation_notes'),
        path('patient_consultation_detail/<int:patient_id>/<int:visit_id>/', DoctorView.patient_consultation_detail, name='patient_consultation_detail'),
        path('patient_vital_list/<int:patient_id>/', DoctorView.patient_vital_list, name='patient_vital_list'),
        path('patient_health_record_view/<int:patient_id>/<int:visit_id>/', DoctorView.patient_health_record_view, name='patient_health_record_view'),
        path('patient_visit_history/<int:patient_id>/', DoctorView.patient_visit_history_view, name='patient_visit_history_view'),
        path('prescriptions/', DoctorView.prescription_list, name='prescription_list'),
        path('resa/manage-referral/', DoctorView.manage_referral, name='manage_referral'),
        path('resa/patient-procedure-view/', DoctorView.patient_procedure_view, name='patient_procedure_view'),
        path('resa/all-patients',DoctorView.manage_patient, name="manage_patient"),
        path('resa/consultation-queue',DoctorView.manage_consultation, name="manage_consultation"),
        path('consultation-fees/', DoctorView.consultation_fee_list, name='consultation_fee_list'),       
        path('resa/manage-pathodology',DoctorView.manage_pathodology, name="manage_pathodology"),
        path('resa/appointments/', DoctorView.appointment_list_view, name='appointment_list'),
        path('notifications/', DoctorView.notification_view, name='notification_view'),
        path('confirm_meeting/<int:appointment_id>/', DoctorView.confirm_meeting, name='confirm_meeting'),
        path('generate-bill/<int:procedure_id>/', DoctorView.generate_billing, name='generate_billing'),
        path('edit_meeting/<int:appointment_id>/', DoctorView.edit_meeting, name='edit_meeting'), 
        path('save_radiology/', DoctorView.save_radiology, name='save_radiology'),
        path('save_procedure/', DoctorView.save_procedure, name='save_procedure'),
        path('save_referral/', DoctorView.save_referral, name='save_referral'),  
        path('change_referral_status/', DoctorView.change_referral_status, name='change_referral_status'), 
        path('invoice/<int:patient_id>/<int:visit_id>/', DoctorView.generate_invoice_bill, name='generate_invoice_bill'),
        
        # imports urls 
        path('resa/import_Import/import_patient_vital_records',imports.import_patient_vital_records, name="import_patient_vital_records"),      
        path('import_prescription_records', imports.import_prescription_records, name='import_prescription_records'),
        path('import_consultation_notes_records', imports.import_consultation_notes_records, name='import_consultation_notes_records'),   
        path('import-patients/', imports.import_patient_records, name='import_patient_records'),
        path('import-pathology-records/', imports.import_pathology_records, name='import_pathology_records'),
        path('import-medicine-records/', imports.import_medicine_records, name='import_medicine_records'),
        path('import-procedure-records/', imports.import_procedure_records, name='import_procedure_records'),
        path('import-referral-records/', imports.import_referral_records, name='import_referral_records'),
              
        # edit urls              
        path('pathodology/<int:pathodology_id>/edit/', editView.edit_pathodology, name='edit_pathodology'),    
        path('update_consultation_data/<int:appointment_id>/', editView.update_consultation_data, name='update_consultation_data'),         
        path('update_consultation_fee/', editView.update_consultation_fee, name='update_consultation_fee'), 
        path('edit_procedure/', editView.edit_procedure, name='edit_procedure'), 
        path('edit_referral/', editView.edit_referral, name='edit_referral'), 
        path('Patient/<int:patient_id>/add/', DoctorView.appointment_view, name='appointment_view'), 
        path('appointment_view/<int:patient_id>/', DoctorView.appointment_view_remote, name='appointment_view_remote'),
        path('patient-procedure-history/<str:mrn>/view/', DoctorView.patient_procedure_history_view, name='patient_procedure_history_view_mrn'),   
        
        # delete urls        
        path('delete_ConsultationNotes/<int:consultation_id>/', delete.delete_ConsultationNotes, name='delete_ConsultationNotes'),
        path('delete_patient_vital/<int:vital_id>/', delete.delete_patient_vital, name='delete_patient_vital'),
        path('delete_prescription/<int:prescription_id>/', delete.delete_prescription, name='delete_prescription'),
        path('delete-consultation-fee/<int:fee_id>/', delete.delete_consultation_fee, name='delete_consultation_fee'),
        path('delete-consultation/<int:appointment_id>/', delete.delete_consultation, name='delete_consultation'),    
        path('pathodology/<int:pathodology_id>/delete/', delete.delete_pathodology, name='delete_pathodology'),     
        path('delete_remote_patient/<int:patient_id>/', delete.delete_remote_patient, name='delete_remote_patient'),
        path('delete-patient/<int:patient_id>/', delete.delete_patient, name='delete_patient'),     
        path('delete_procedure/', delete.delete_procedure, name='delete_procedure'),        
        path('delete_referral/', delete.delete_referral, name='delete_referral'),
        path('delete_patient_visit/<int:patient_visit_id>/', delete.delete_patient_visit, name='delete_patient_visit'),

   
        

        
      
        

]
