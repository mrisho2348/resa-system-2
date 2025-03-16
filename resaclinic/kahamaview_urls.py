from django.urls import path
from kahamahmis import kahamaViews

urlpatterns = [

    # Report and Statistics URLs
    path('search_report/', kahamaViews.search_report, name='kahama_search_report'),
    path('patient_statistics/', kahamaViews.patient_statistics, name='kahama_patient_statistics'),


    # Appointments
    path('appointment_view/', kahamaViews.appointment_view, name='kahama_appointment_view'),

    # Drug Division and Prescription related URLs

    path('add_remoteprescription/', kahamaViews.add_remoteprescription, name='kahama_add_remoteprescription'),



    # Patient Observation and Lab Result URLs
    path('patient_observation_history_view/<str:mrn>/view/', kahamaViews.patient_observation_history_view, name="kahama_patient_observation_history_view"),
    path('patient_lab_result_history_view/<str:mrn>/view/', kahamaViews.patient_lab_result_history_view, name="kahama_patient_lab_result_history_view"),
    path('patient_laboratory_view/', kahamaViews.patient_laboratory_view, name="kahama_patient_laboratory_view"),    
    path('lab-details/<str:mrn>/<str:visit_number>/', kahamaViews.patient_lab_details_view, name='kahama_patient_lab_details_view'),
    path('patient_observation_view/', kahamaViews.patient_observation_view, name="kahama_patient_observation_view"),
    
    # Chief Complaint URLs
    path('save_chief_complaint/', kahamaViews.save_chief_complaint, name='kahama_save_chief_complaint'),
    path('chief_complaint/update/<int:chief_complaint_id>/', kahamaViews.update_chief_complaint, name='kahama_update_chief_complaint'),
    path('delete_chief_complaint/<int:chief_complaint_id>/', kahamaViews.delete_chief_complaint, name='kahama_delete_chief_complaint'),
    path('discharge/details/<int:patient_id>/<int:visit_id>/', kahamaViews.discharge_details_view, name='kahama_discharge_details_view'),
    

    
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

    path('fetch-existing-data/', kahamaViews.fetch_existing_data, name='kahama_endpoint_to_fetch_existing_data'),
   
    path('edit_procedure_result/<int:patient_id>/<int:visit_id>/<int:procedure_id>/', kahamaViews.edit_procedure_result, name='kahama_edit_procedure_result'),
    path('edit_lab_result/<int:patient_id>/<int:visit_id>/<int:lab_id>/', kahamaViews.edit_lab_result, name='kahama_edit_lab_result'),
    path('save_patient_health_information/<int:patient_id>/', kahamaViews.save_patient_health_information, name="kahama_save_patient_health_information"),
]
