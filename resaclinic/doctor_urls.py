from django.urls import path, re_path

from clinic import DoctorView

urlpatterns = [
    re_path(r'^doctor/doctor_dashboard/$', DoctorView.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/profile/', DoctorView.doctor_profile, name='doctor_profile'),
    path('edit-profile/<int:pk>/', DoctorView.EditStaffProfileView.as_view(), name='doctor_edit_staff_profile'),
    re_path(r'^doctor/fetch_lab_order_counts_view/$', DoctorView.fetch_lab_order_counts_view, name='doctor_fetch_lab_order_counts_view'),
    path('doctor/get-gender-yearly-data/', DoctorView.get_gender_yearly_data, name="doctor_get_gender_yearly_data"),
    path('doctor/get-gender-monthly-data/', DoctorView.get_gender_monthly_data, name="doctor_get_gender_monthly_data"),
    re_path(r'^doctor/patient_lab_view/$', DoctorView.patient_lab_view, name='doctor_patient_lab_view'),
    re_path(r'^doctor/new_procedure_order/$', DoctorView.new_procedure_order, name='doctor_new_procedure_order'),
    re_path(r'^doctor/edit_procedure_result/(?P<patient_id>\d+)/(?P<visit_id>\d+)/(?P<procedure_id>\d+)/$', DoctorView.edit_procedure_result, name='doctor_edit_procedure_result'),
    re_path(r'^doctor/edit_radiology_result/(?P<patient_id>\d+)/(?P<visit_id>\d+)/(?P<radiology_id>\d+)/$', DoctorView.edit_radiology_result, name='doctor_edit_radiology_result'),
    re_path(r'^doctor/edit_lab_result/(?P<patient_id>\d+)/(?P<visit_id>\d+)/(?P<lab_id>\d+)/$', DoctorView.edit_lab_result, name='doctor_edit_lab_result'),
    re_path(r'^doctor/new_lab_order/$', DoctorView.new_lab_order, name='doctor_new_lab_order'),
    re_path(r'^doctor/fetch_procedure_order_counts_view/$', DoctorView.fetch_procedure_order_counts_view, name='doctor_fetch_procedure_order_counts_view'),
    re_path(r'^doctor/fetch_radiology_order_counts_view/$', DoctorView.fetch_radiology_order_counts_view, name='doctor_fetch_radiology_order_counts_view'),
    re_path(r'^doctor/new_radiology_order/$', DoctorView.new_radiology_order, name='doctor_new_radiology_order'),
    re_path(r'^doctor/fetch_order_counts/$', DoctorView.fetch_order_counts_view, name='doctor_fetch_order_counts_view'),
    re_path(r'^doctor/fetch_consultation_counts/$', DoctorView.fetch_consultation_counts, name='doctor_fetch_consultation_counts'),

    re_path(r'^doctor_/radiology_order/$', DoctorView.radiology_order, name='doctor_radiology_order'),

 
   
 
    path('prescriptions/<str:visit_number>/<int:patient_id>/',  DoctorView.prescription_detail, name='doctor_prescription_detail'),
    re_path(r'^doctor/prescriptions-billing/(?P<visit_number>[\w-]+)/(?P<patient_id>\d+)/$', DoctorView.prescription_billing, name='doctor_prescription_billing'),
    re_path(r'^doctor/prescriptions-notes/(?P<visit_number>[\w-]+)/(?P<patient_id>\d+)/$', DoctorView.prescription_notes, name='doctor_prescription_notes'),
    re_path(r'^doctor/new_consultation_order/$', DoctorView.new_consultation_order, name='doctor_new_consultation_order'), 
    re_path(r'^doctor/save_patient_vital/$', DoctorView.save_remotepatient_vital, name='doctor_save_remotepatient_vital'),

    path('save_chief_complaint/', DoctorView.save_chief_complaint, name='doctor_save_chief_complaint'),
    path('delete_chief_complaint/<int:chief_complaint_id>/', DoctorView.delete_chief_complaint, name='doctor_delete_chief_complaint'),
    path('chief_complaint/update/<int:chief_complaint_id>/', DoctorView.update_chief_complaint, name='doctor_update_chief_complaint'),       
    path('fetch-existing-data/', DoctorView.fetch_existing_data, name='doctor_endpoint_to_fetch_existing_data'), 

  
    re_path(r'^doctor/manage_laboratory/$', DoctorView.manage_laboratory, name='doctor_manage_laboratory'),
    path('save_remotesconsultation_notes_next/<int:patient_id>/<int:visit_id>/',DoctorView.save_remotesconsultation_notes_next, name="doctor_save_remotesconsultation_notes_next"),

    
    path('save_remotereferral/<int:patient_id>/<int:visit_id>/', DoctorView.save_remotereferral, name='doctor_save_remotereferral'),
    path('procedure/detail/<str:mrn>/<str:visit_number>/', DoctorView.patient_procedure_detail_view, name='doctor_patient_procedure_detail_view'),
    path('add/radiology/<int:patient_id>/<int:visit_id>/', DoctorView.add_radiology, name='doctor_add_radiology'),
    path('counsel/<int:patient_id>/<int:visit_id>/', DoctorView.save_counsel, name='doctor_save_remote_counseling'),

    path('save_remote_discharges_notes/<int:patient_id>/<int:visit_id>/', DoctorView.save_remote_discharges_notes, name='doctor_save_remote_discharges_notes'),

    # manage urls
    re_path(r'^doctor/get-procedure-cost/$', DoctorView.get_procedure_cost, name='doctor_get_procedure_cost'),
    re_path(r'^doctor/get_patient_details/(?P<patient_id>\d+)/$', DoctorView.get_patient_details, name='doctor_get_patient_details'),   
    re_path(r'^doctor/add_investigation/$', DoctorView.add_investigation, name='doctor_add_investigation'),
    re_path(r'^doctor/add_imaging/$', DoctorView.add_imaging, name='doctor_add_imaging'),
    re_path(r'^doctor/add_procedure/$', DoctorView.add_procedure, name='doctor_add_procedure'),
    re_path(r'^doctor/add_remoteprescription/$', DoctorView.add_remoteprescription, name='doctor_add_remoteprescription'),
    re_path(r'^doctor/get_unit_price/$', DoctorView.get_unit_price, name='doctor_get_unit_price'),
    re_path(r'^doctor/get_drug_division_status/$', DoctorView.get_drug_division_status, name='doctor_get_drug_division_status'),
    re_path(r'^doctor/get_medicine_formulation/$', DoctorView.get_medicine_formulation, name='doctor_get_medicine_formulation'),
    re_path(r'^doctor/get_formulation_unit/$', DoctorView.get_formulation_unit, name='doctor_get_formulation_unit'),
    re_path(r'^doctor/get_frequency_name/$', DoctorView.get_frequency_name, name='doctor_get_frequency_name'),
    re_path(r'^doctor/medicine_dosage/$', DoctorView.medicine_dosage, name='doctor_medicine_dosage'),
    re_path(r'^doctor/consultation-notes/$', DoctorView.consultation_notes_view, name='doctor_consultation_notes'),

    re_path(r'^doctor/save_prescription/(?P<patient_id>\d+)/(?P<visit_id>\d+)/$', DoctorView.save_prescription, name='doctor_save_prescription'),
    re_path(r'^doctor/save_laboratory/(?P<patient_id>\d+)/(?P<visit_id>\d+)/$', DoctorView.save_laboratory, name='doctor_save_laboratory'),
    re_path(r'^doctor/save_remoteprocedure/(?P<patient_id>\d+)/(?P<visit_id>\d+)/$', DoctorView.save_remoteprocedure, name='doctor_save_remoteprocedure'),
    re_path(r'^doctor/save_observation/(?P<patient_id>\d+)/(?P<visit_id>\d+)/$', DoctorView.save_observation, name='doctor_save_observation'),
    re_path(r'^doctor/save_remotesconsultation_notes/(?P<patient_id>\d+)/(?P<visit_id>\d+)/$', DoctorView.save_remotesconsultation_notes, name='doctor_save_remotesconsultation_notes'),

  
    re_path(r'^doctor/patient_health_record_view/(?P<patient_id>\d+)/(?P<visit_id>\d+)/$', DoctorView.patient_health_record_view, name='doctor_patient_health_record_view'),
    re_path(r'^doctor/patient_visit_history/(?P<patient_id>\d+)/$', DoctorView.patient_visit_history_view, name='doctor_patient_visit_history_view'),

    re_path(r'^doctor/resa/patient-procedure-view/$', DoctorView.patient_procedure_view, name='doctor_patient_procedure_view'),
    re_path(r'^doctor/resa/all-patients/$', DoctorView.manage_patient, name='doctor_manage_patient'),
    re_path(r'^doctor/resa/consultation-queue/$', DoctorView.manage_consultation, name='doctor_manage_consultation'),

    re_path(r'^doctor/resa/appointments/$', DoctorView.appointment_list_view, name='doctor_appointment_list'),
    path('counseling/', DoctorView.counseling_list_view, name='doctor_counseling_list'),

    path('observation_records/', DoctorView.observation_record_list_view, name='doctor_observation_record_list'),   
    re_path(r'^doctor/confirm_meeting/(?P<appointment_id>\d+)/$', DoctorView.confirm_meeting, name='doctor_confirm_meeting'),
  
    re_path(r'^doctor/edit_meeting/(?P<appointment_id>\d+)/$', DoctorView.edit_meeting, name='doctor_edit_meeting'),
    re_path(r'^doctor/save_radiology/$', DoctorView.save_radiology, name='doctor_save_radiology'),
    re_path(r'^doctor/save_procedure/$', DoctorView.save_procedure, name='doctor_save_procedure'),  
    re_path(r'^doctor/change_referral_status/$', DoctorView.change_referral_status, name='doctor_change_referral_status'),
   
    path('employee_detail/', DoctorView.employee_detail, name='doctor_employee_detail'),

 

    # edit urls

    re_path(r'^doctor/appointment_view/(?P<patient_id>\d+)/$', DoctorView.appointment_view_remote, name='doctor_appointment_view_remote'),
    re_path(r'^doctor/patient-procedure-history/(?P<mrn>[\w-]+)/view/$', DoctorView.patient_procedure_history_view, name='doctor_patient_procedure_history_view_mrn'),


    path('resa/doctor/change-password/', DoctorView.change_password, name='doctor_change_password'),
]
