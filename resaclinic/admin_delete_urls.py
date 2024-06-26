from django.urls import include, path, re_path
from clinic import delete

urlpatterns = [   
    # delete urls 
    path('admin/delete-diagnosis/', delete.delete_diagnosis, name='admin_delete_diagnosis'),
    re_path(r'^admin/delete-consultation-notes/(?P<consultation_id>\d+)/$', delete.delete_ConsultationNotes, name='admin_delete_consultation_notes'),
    path('admin/delete-patient-vital/', delete.delete_patient_vital, name='admin_delete_patient_vital'),
    re_path(r'^admin/delete-prescription/(?P<prescription_id>\d+)/$', delete.delete_prescription, name='admin_delete_prescription'),
    re_path(r'^admin/delete-consultation/(?P<appointment_id>\d+)/$', delete.delete_consultation, name='admin_delete_consultation'),
    path('admin/delete-medicine/', delete.delete_medicine, name='admin_delete_medicine'),
    re_path(r'^admin/delete-disease-record/(?P<disease_id>\d+)/$', delete.delete_disease_record, name='admin_delete_disease_record'),
    path('admin/delete-supplier/', delete.delete_supplier, name='admin_delete_supplier'),
    path('admin/delete-patient/', delete.delete_patient, name='admin_delete_patient'),
    path('admin/delete-equipment/', delete.delete_equipment, name='admin_delete_equipment'),
    path('admin/delete-inventory/', delete.delete_inventory_item, name='admin_delete_inventory'),
    path('admin/delete-category/', delete.delete_category, name='admin_delete_category'),
    re_path(r'^admin/delete-remote-service/(?P<service_id>\d+)/$', delete.delete_remote_service, name='admin_delete_remote_service'),
    path('admin/delete-maintenance/', delete.delete_maintenance, name='admin_delete_maintenance'),
    path('admin/delete-reagent/', delete.delete_reagent, name='admin_delete_reagent'),
    path('admin/delete_insurance_company/', delete.delete_insurance_company, name='admin_delete_insurance_company'),
    path('admin/delete-usage-history/', delete.delete_usage_history, name='admin_delete_usage_history'),
    path('admin/delete-reagent-used/', delete.delete_reagent_used, name='admin_delete_reagent_used'),
    re_path(r'^admin/delete-insurance/(?P<insurance_id>\d+)/$', delete.delete_insurance, name='admin_delete_insurance'),
    re_path(r'^admin/delete-pathology/(?P<pathodology_id>\d+)/$', delete.delete_pathodology, name='admin_delete_pathology'),
    re_path(r'^admin/delete-company/(?P<company_id>\d+)/$', delete.delete_company, name='admin_delete_company'),
    re_path(r'^admin/delete-staff/(?P<staff_id>\d+)/$', delete.delete_staff, name='admin_delete_staff'),
    re_path(r'^admin/delete-service/$', delete.delete_service, name='admin_delete_service'),
    re_path(r'^admin/delete-procedure/$', delete.delete_procedure, name='admin_delete_procedure'),
    re_path(r'^admin/delete-referral/$', delete.delete_referral, name='admin_delete_referral'),  
    path('delete_qualitycontrol/', delete.delete_quality_control, name='admin_delete_qualitycontrol'),
    path('admin/delete-remote-company/', delete.delete_remotecompany, name='admin_delete_remote_company'),
    path('admin/delete-pathology-record/', delete.delete_pathology_record, name='admin_delete_pathology_record'),
    re_path(r'^admin/delete-patient-visit/', delete.delete_patient_visit, name='admin_delete_patient_visit'),
]
