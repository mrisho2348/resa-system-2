from django.urls import path, re_path

from clinic.DoctorView import *

urlpatterns = [
    re_path(r'^doctor/doctor_dashboard/$', doctor_dashboard, name='doctor_dashboard'),
    path('doctor/profile/', doctor_profile, name='doctor_profile'),
    path('doctor/today-patients/', doctor_today_patients, name='doctor_today_patients'),
    path('doctor/in-progress-consultations/', doctor_in_progress_consultations, name='doctor_in_progress_consultations'),
    path('doctor/completed-consultations/', doctor_completed_consultations, name='doctor_completed_consultations'),
    path('doctor/today-lab-orders/', doctor_today_lab_orders, name='doctor_today_lab_orders'),
    path('doctor/today-imaging-orders/', doctor_today_imaging_orders, name='doctor_today_imaging_orders'),
    path('doctor/pending-imaging/', doctor_pending_imaging, name='doctor_pending_imaging'),
    path('doctor/completed-imaging/', doctor_completed_imaging, name='doctor_completed_imaging'),
    path('doctor/today-procedures/', doctor_today_procedures, name='doctor_today_procedures'),
    path('doctor/pending-procedures/', doctor_pending_procedures, name='doctor_pending_procedures'),
    path('doctor/completed-procedures/', doctor_completed_procedures, name='doctor_completed_procedures'),
    path('doctor/consultation-list/', doctor_consultation_list, name='doctor_consultation_list'),
    path('api/dashboard-stats/', dashboard_stats_api, name='doctor_dashboard_stats_api'),
    path('edit-profile/<int:pk>/', EditStaffProfileView.as_view(), name='doctor_edit_staff_profile'),
    re_path(r'^doctor/fetch_lab_order_counts_view/$', fetch_lab_order_counts_view, name='doctor_fetch_lab_order_counts_view'),
    path('doctor/get-gender-yearly-data/', get_gender_yearly_data, name="doctor_get_gender_yearly_data"),
    path('doctor/get-gender-monthly-data/', get_gender_monthly_data, name="doctor_get_gender_monthly_data"),
    re_path(r'^doctor/patient_lab_view/$', patient_lab_view, name='doctor_patient_lab_view'),
    re_path(r'^doctor/new_procedure_order/$', new_procedure_order, name='doctor_new_procedure_order'),
    re_path(r'^doctor/edit_procedure_result/(?P<patient_id>\d+)/(?P<visit_id>\d+)/(?P<procedure_id>\d+)/$', edit_procedure_result, name='doctor_edit_procedure_result'),
    re_path(r'^doctor/edit_radiology_result/(?P<patient_id>\d+)/(?P<visit_id>\d+)/(?P<radiology_id>\d+)/$', edit_radiology_result, name='doctor_edit_radiology_result'),
    re_path(r'^doctor/edit_lab_result/(?P<patient_id>\d+)/(?P<visit_id>\d+)/(?P<lab_id>\d+)/$', edit_lab_result, name='doctor_edit_lab_result'),
    re_path(r'^doctor/new_lab_order/$', new_lab_order, name='doctor_new_lab_order'),
    re_path(r'^doctor/fetch_procedure_order_counts_view/$', fetch_procedure_order_counts_view, name='doctor_fetch_procedure_order_counts_view'),
    re_path(r'^doctor/fetch_radiology_order_counts_view/$', fetch_radiology_order_counts_view, name='doctor_fetch_radiology_order_counts_view'),
    re_path(r'^doctor/new_radiology_order/$', new_radiology_order, name='doctor_new_radiology_order'),
    re_path(r'^doctor/fetch_order_counts/$', fetch_order_counts_view, name='doctor_fetch_order_counts_view'),
    re_path(r'^doctor/fetch_consultation_counts/$', fetch_consultation_counts, name='doctor_fetch_consultation_counts'),

    re_path(r'^doctor_/radiology_order/$', radiology_order, name='doctor_radiology_order'),

 
   
 
    path('prescriptions/<str:visit_number>/<int:patient_id>/',  prescription_detail, name='doctor_prescription_detail'),
    re_path(r'^doctor/prescriptions-billing/(?P<visit_number>[\w-]+)/(?P<patient_id>\d+)/$', prescription_billing, name='doctor_prescription_billing'),
    re_path(r'^doctor/prescriptions-notes/(?P<visit_number>[\w-]+)/(?P<patient_id>\d+)/$', prescription_notes, name='doctor_prescription_notes'),
    re_path(r'^doctor/new_consultation_order/$', new_consultation_order, name='doctor_new_consultation_order'), 
    re_path(r'^doctor/save_patient_vital/$', save_remotepatient_vital, name='doctor_save_remotepatient_vital'),

    path('save_chief_complaint/', save_chief_complaint, name='doctor_save_chief_complaint'),
    path('delete_chief_complaint/<int:chief_complaint_id>/', delete_chief_complaint, name='doctor_delete_chief_complaint'),
    path('chief_complaint/update/<int:chief_complaint_id>/', update_chief_complaint, name='doctor_update_chief_complaint'),       
    path('fetch-existing-data/', fetch_existing_data, name='doctor_endpoint_to_fetch_existing_data'), 

  
    re_path(r'^doctor/manage_laboratory/$', manage_laboratory, name='doctor_manage_laboratory'),
    path('save_remotesconsultation_notes_next/<int:patient_id>/<int:visit_id>/',save_remotesconsultation_notes_next, name="doctor_save_remotesconsultation_notes_next"),

    
    path('save_remotereferral/<int:patient_id>/<int:visit_id>/', save_remotereferral, name='doctor_save_remotereferral'),
    path('procedure/detail/<str:mrn>/<str:visit_number>/', patient_procedure_detail_view, name='doctor_patient_procedure_detail_view'),
    path('add/radiology/<int:patient_id>/<int:visit_id>/', add_radiology, name='doctor_add_radiology'),
    path('counsel/<int:patient_id>/<int:visit_id>/', save_counsel, name='doctor_save_remote_counseling'),

    path('save_remote_discharges_notes/<int:patient_id>/<int:visit_id>/', save_remote_discharges_notes, name='doctor_save_remote_discharges_notes'),

    # manage urls
    re_path(r'^doctor/get-procedure-cost/$', get_procedure_cost, name='doctor_get_procedure_cost'),
    re_path(r'^doctor/get_patient_details/(?P<patient_id>\d+)/$', get_patient_details, name='doctor_get_patient_details'),   
    re_path(r'^doctor/add_investigation/$', add_investigation, name='doctor_add_investigation'),
    re_path(r'^doctor/add_imaging/$', add_imaging, name='doctor_add_imaging'),
    re_path(r'^doctor/add_procedure/$', add_procedure, name='doctor_add_procedure'),
    re_path(r'^doctor/add_remoteprescription/$', add_remoteprescription, name='doctor_add_remoteprescription'),
    re_path(r'^doctor/get_unit_price/$', get_unit_price, name='doctor_get_unit_price'),
    re_path(r'^doctor/get_drug_division_status/$', get_drug_division_status, name='doctor_get_drug_division_status'),
    re_path(r'^doctor/get_medicine_formulation/$', get_medicine_formulation, name='doctor_get_medicine_formulation'),
    re_path(r'^doctor/get_formulation_unit/$', get_formulation_unit, name='doctor_get_formulation_unit'),
    re_path(r'^doctor/get_frequency_name/$', get_frequency_name, name='doctor_get_frequency_name'),
    re_path(r'^doctor/medicine_dosage/$', medicine_dosage, name='doctor_medicine_dosage'),
    re_path(r'^doctor/consultation-notes/$', consultation_notes_view, name='doctor_consultation_notes'),

    re_path(r'^doctor/save_prescription/(?P<patient_id>\d+)/(?P<visit_id>\d+)/$', save_prescription, name='doctor_save_prescription'),
    re_path(r'^doctor/save_laboratory/(?P<patient_id>\d+)/(?P<visit_id>\d+)/$', save_laboratory, name='doctor_save_laboratory'),
    re_path(r'^doctor/save_remoteprocedure/(?P<patient_id>\d+)/(?P<visit_id>\d+)/$', save_remoteprocedure, name='doctor_save_remoteprocedure'),
    re_path(r'^doctor/save_observation/(?P<patient_id>\d+)/(?P<visit_id>\d+)/$', save_observation, name='doctor_save_observation'),
    re_path(r'^doctor/save_remotesconsultation_notes/(?P<patient_id>\d+)/(?P<visit_id>\d+)/$', save_remotesconsultation_notes, name='doctor_save_remotesconsultation_notes'),


    path('edit-meeting/<int:appointment_id>/', edit_meeting, name='doctor_edit_meeting'),
    path('confirm-meeting/<int:appointment_id>/', confirm_meeting, name='doctor_confirm_meeting'),
    path('start-consultation/<int:appointment_id>/', start_consultation, name='start_consultation'),
    path('complete-consultation/<int:appointment_id>/', complete_consultation, name='complete_consultation'),
    path('cancel-appointment/<int:appointment_id>/', cancel_appointment, name='cancel_appointment'),
    path('appointment-details/<int:appointment_id>/', get_appointment_details, name='get_appointment_details'),
    path('bulk-update-appointments/', bulk_update_appointments, name='bulk_update_appointments'),
    
    re_path(r'^doctor/patient_visit_history/(?P<patient_id>\d+)/$', patient_visit_history_view, name='doctor_patient_visit_history_view'),

    re_path(r'^doctor/resa/patient-procedure-view/$', patient_procedure_view, name='doctor_patient_procedure_view'),
    re_path(r'^doctor/resa/all-patients/$', manage_patient, name='doctor_manage_patient'),
    re_path(r'^doctor/resa/consultation-queue/$', manage_consultation, name='doctor_manage_consultation'),

    re_path(r'^doctor/resa/appointments/$', appointment_list_view, name='doctor_appointment_list'),
    path('counseling/', counseling_list_view, name='doctor_counseling_list'),

    path('observation_records/', observation_record_list_view, name='doctor_observation_record_list'),   
    re_path(r'^doctor/confirm_meeting/(?P<appointment_id>\d+)/$', confirm_meeting, name='doctor_confirm_meeting'),
  
    re_path(r'^doctor/edit_meeting/(?P<appointment_id>\d+)/$', edit_meeting, name='doctor_edit_meeting'),
    re_path(r'^doctor/save_radiology/$', save_radiology, name='doctor_save_radiology'),
    re_path(r'^doctor/save_procedure/$', save_procedure, name='doctor_save_procedure'),  
    re_path(r'^doctor/change_referral_status/$', change_referral_status, name='doctor_change_referral_status'),
    path('doctor-fetch-lab-stats/', doctor_fetch_lab_stats, name='doctor_fetch_lab_stats'),
    path('employee_detail/', employee_detail, name='doctor_employee_detail'),

 

    # edit urls

    re_path(r'^doctor/appointment_view/(?P<patient_id>\d+)/$', appointment_view_remote, name='doctor_appointment_view_remote'),
    re_path(r'^doctor/patient-procedure-history/(?P<mrn>[\w-]+)/view/$', patient_procedure_history_view, name='doctor_patient_procedure_history_view_mrn'),


    path('resa/doctor/change-password/', change_password, name='doctor_change_password'),
]
