from django.urls import  path, re_path
from clinic import delete

urlpatterns = [   
    # delete urls 
    path('admin/delete-diagnosis/', delete.delete_diagnosis, name='admin_delete_diagnosis'),
    re_path(r'^admin/delete-consultation-notes/(?P<consultation_id>\d+)/$', delete.delete_ConsultationNotes, name='admin_delete_consultation_notes'),
    path('admin/delete-patient-vital/', delete.delete_patient_vital, name='admin_delete_patient_vital'),
    re_path(r'^admin/delete-prescription/(?P<prescription_id>\d+)/$', delete.delete_prescription, name='admin_delete_prescription'),
   
    path('admin/delete-medicine/', delete.delete_medicine, name='admin_delete_medicine'),
   
    path('admin/delete-patient/', delete.delete_patient, name='admin_delete_patient'),
    path('admin/delete-equipmnt/', delete.delete_equipment, name='admin_delete_equipment'),  
  
    path('admin/delete-reagent/', delete.delete_reagent, name='admin_delete_reagent'), 
    
 
    re_path(r'^admin/delete-service/$', delete.delete_service, name='admin_delete_service'),
    re_path(r'^admin/delete-procedure/$', delete.delete_procedure, name='admin_delete_procedure'),
    re_path(r'^admin/delete-referral/$', delete.delete_referral, name='admin_delete_referral'),  

   
    path('admin/delete-pathology-record/', delete.delete_pathology_record, name='admin_delete_pathology_record'),
    re_path(r'^admin/delete-patient-visit/', delete.delete_patient_visit, name='admin_delete_patient_visit'),
]
