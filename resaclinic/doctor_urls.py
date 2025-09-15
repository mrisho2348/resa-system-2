from django.urls import path
from clinic.DoctorView import *

urlpatterns = [
    # Dashboard & Profile
    path("dashboard/", doctor_dashboard, name="doctor_dashboard"),
    path("profile/", doctor_profile, name="doctor_profile"),
    path("edit-profile/<int:pk>/", EditStaffProfileView.as_view(), name="doctor_edit_staff_profile"),
    path("change-password/", change_password, name="doctor_change_password"),

    # Consultations
    path("today-patients/", doctor_today_patients, name="doctor_today_patients"),
    path("in-progress-consultations/", doctor_in_progress_consultations, name="doctor_in_progress_consultations"),
    path("completed-consultations/", doctor_completed_consultations, name="doctor_completed_consultations"),
    path("consultation-list/", doctor_consultation_list, name="doctor_consultation_list"),
    path("consultation-notes/", consultation_notes_view, name="doctor_consultation_notes"),
    path("new-consultation-order/", new_consultation_order, name="doctor_new_consultation_order"),

    path("consultation-order/<int:consultation_id>/", consultation_order_redirect, name="doctor_consultation_order_redirect"),


    # Imaging / Radiology
    path("today-imaging-orders/", doctor_today_imaging_orders, name="doctor_today_imaging_orders"),
    path("pending-imaging/", doctor_pending_imaging, name="doctor_pending_imaging"),
    path("completed-imaging/", doctor_completed_imaging, name="doctor_completed_imaging"),
    path("new-radiology-order/", new_radiology_order, name="doctor_new_radiology_order"),
    path("imaging-order/<int:radiology_id>/", edit_radiology_result, name="doctor_edit_radiology_result"),
    path("add-radiology/<int:patient_id>/<int:visit_id>/", add_radiology, name="doctor_add_radiology"),
    path("radiology-order/", radiology_order, name="doctor_radiology_order"),

    # Procedures
    path("today-procedures/", doctor_today_procedures, name="doctor_today_procedures"),
    path("pending-procedures/", doctor_pending_procedures, name="doctor_pending_procedures"),
    path("completed-procedures/", doctor_completed_procedures, name="doctor_completed_procedures"),
    path("new-procedure-order/", new_procedure_order, name="doctor_new_procedure_order"),
    path("procedure/<int:procedure_id>/", edit_procedure_result, name="doctor_edit_procedure_result"),
  

    # Chief Complaints
    path("save-chief-complaint/", save_chief_complaint, name="doctor_save_chief_complaint"),
    path("delete-chief-complaint/<int:chief_complaint_id>/", delete_chief_complaint, name="doctor_delete_chief_complaint"),
    path("update-chief-complaint/<int:chief_complaint_id>/", update_chief_complaint, name="doctor_update_chief_complaint"),
    path('fetch-existing-data/', fetch_existing_data, name='doctor_endpoint_to_fetch_existing_data'), 

    # Notes, Referrals & Counseling
    path("save-remotesconsultation-notes/<int:patient_id>/<int:visit_id>/", save_remotesconsultation_notes, name="doctor_save_remotesconsultation_notes"),
    path("save-remotesconsultation-notes-next/<int:patient_id>/<int:visit_id>/", save_remotesconsultation_notes_next, name="doctor_save_remotesconsultation_notes_next"),
    path("save-remotereferral/<int:patient_id>/<int:visit_id>/", save_remotereferral, name="doctor_save_remotereferral"),
    path("save-remote-discharges-notes/<int:patient_id>/<int:visit_id>/", save_remote_discharges_notes, name="doctor_save_remote_discharges_notes"),
    path("counsel/<int:patient_id>/<int:visit_id>/", save_counsel, name="doctor_save_remote_counseling"),
    path("counseling/", counseling_list_view, name="doctor_counseling_list"),

    # Orders & Records
    path("add-investigation/", add_investigation, name="doctor_add_investigation"),
    path("add-imaging/", add_imaging, name="doctor_add_imaging"),
    path("add-procedure/", add_procedure, name="doctor_add_procedure"),
    path("add-remoteprescription/", add_remoteprescription, name="doctor_add_remoteprescription"),
    path("save-prescription/<int:patient_id>/<int:visit_id>/", save_prescription, name="doctor_save_prescription"),
    path("save-laboratory/<int:patient_id>/<int:visit_id>/", save_laboratory, name="doctor_save_laboratory"),
    path("save-remoteprocedure/<int:patient_id>/<int:visit_id>/", save_remoteprocedure, name="doctor_save_remoteprocedure"),
    path("save-observation/<int:patient_id>/<int:visit_id>/", save_observation, name="doctor_save_observation"),
    path("save-procedure/", save_procedure, name="doctor_save_procedure"),
    path("change-referral-status/", change_referral_status, name="doctor_change_referral_status"),
    path("observation-records/", observation_record_list_view, name="doctor_observation_record_list"),

    # Meetings & Appointments
    path("edit-meeting/<int:appointment_id>/", edit_meeting, name="doctor_edit_meeting"),
    path("confirm-meeting/<int:appointment_id>/", confirm_meeting, name="doctor_confirm_meeting"),
    path("appointments/", appointment_list_view, name="doctor_appointment_list"),
    path("appointment-view/<int:patient_id>/", appointment_view_remote, name="doctor_appointment_view_remote"),
    path("appointment/<int:appointment_id>/", appointment_redirect, name="doctor_appointment_redirect"),

    # Patient Views
    path("patient-lab-view/", patient_laboratory_view, name="doctor_patient_lab_view"),
    path("patient-visit-history/<int:patient_id>/", patient_visit_history_view, name="doctor_patient_visit_history_view"),
   
    path("patient-procedure-view/", patient_procedure_view, name="doctor_patient_procedure_view"),
    path("manage-patients/", manage_patient, name="doctor_manage_patient"),
    path("manage-consultation/", manage_consultation, name="doctor_manage_consultation"),

    # Stats & Analytics
    path("get-gender-yearly-data/", get_gender_yearly_data, name="doctor_get_gender_yearly_data"),
    path("get-gender-monthly-data/", get_gender_monthly_data, name="doctor_get_gender_monthly_data"),
    path("get-procedure-cost/", get_procedure_cost, name="doctor_get_procedure_cost"),
    path("get-patient-details/<int:patient_id>/", get_patient_details, name="doctor_get_patient_details"),
    path("get-unit-price/", get_unit_price, name="doctor_get_unit_price"),
    path("dashboard-stats/", doctor_dashboard_stats_api, name="doctor_dashboard_stats_api"),

    # Notifications
    path("notifications/", doctor_notifications_api, name="doctor_notifications_api"),
    path("all-notifications/", doctor_all_notifications, name="doctor_all_notifications"),
    path("api/notifications/", doctor_all_notifications_api, name="doctor_all_notifications_api"),
    path("api/notifications/toggle/", doctor_toggle_notification_api, name="doctor_toggle_notification_api"),
    path("api/notifications/delete/", doctor_delete_notification_api, name="doctor_delete_notification_api"),

    # Employees
    path("employee-detail/", employee_detail, name="doctor_employee_detail"),
]
