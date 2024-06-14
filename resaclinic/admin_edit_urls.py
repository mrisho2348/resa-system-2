from django.urls import include, path, re_path

from clinic import AdminViews, editView

urlpatterns = [    
    re_path(r'^admin/disease-records/(?P<disease_id>\d+)/edit/$', editView.edit_disease_record, name='admin_edit_disease_record'),
    re_path(r'^admin/insurance-records/(?P<insurance_id>\d+)/edit/$', editView.edit_insurance, name='admin_edit_insurance'),
    re_path(r'^admin/pathology/(?P<pathodology_id>\d+)/edit/$', editView.edit_pathodology, name='admin_edit_pathology'),
    re_path(r'^admin/company/(?P<company_id>\d+)/edit/$', editView.edit_company, name='admin_edit_company'),
    re_path(r'^admin/update-consultation-data/(?P<appointment_id>\d+)/$', editView.update_consultation_data, name='admin_update_consultation_data'), 
    re_path(r'^admin/patient/(?P<patient_id>\d+)/edit/$', editView.edit_patient, name='admin_edit_patient'),
    path('admin/edit-procedure/', editView.edit_procedure, name='admin_edit_procedure'), 
    path('admin/edit-referral/', editView.edit_referral, name='admin_edit_referral'),      
    re_path(r'^admin/patient-procedure-history/(?P<mrn>\w+)/view/$', AdminViews.patient_procedure_history_view, name='admin_patient_procedure_history_view_mrn'), 
    re_path(r'^admin/edit-medicine/(?P<medicine_id>\d+)/$', editView.edit_medicine, name='admin_edit_medicine'),        
    re_path(r'^admin/edit-inventory/(?P<inventory_id>\d+)/$', editView.edit_inventory, name='admin_edit_inventory'),
]
