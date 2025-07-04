from django.urls import path

from clinic import ExcelTemplate, imports

urlpatterns = [
 
    path('admin/import/import-service-data/', imports.import_service_data, name='admin_import_service_data'),

    path('admin/import/import-service-records/', imports.import_service_records, name='admin_import_service_records'),
    path('admin/import/import-disease-records/', imports.import_disease_recode, name='admin_import_disease_recode'),

    path('admin/import/import-reagent/', imports.import_reagent, name='admin_import_reagent'),
    path('admin/import/import-diagnosis-records/', imports.import_diagnosis_records, name='admin_import_diagnosis_records'),
    path('admin/import/import-equipment/', imports.import_equipment, name='admin_import_equipment'),
   
    path('admin/import/import-companies/', imports.import_companies, name='admin_import_companies'),
    path('admin/import/import-ambulance-route-list/', imports.import_ambulance_route_list, name='admin_import_ambulance_route_list'),
    path('admin/import/import-patient-records/', imports.import_patient_records, name='admin_import_patient_records'),
    path('admin/import/import-pathology-records/', imports.import_pathology_records, name='admin_import_pathology_records'),
    path('admin/import/import-medicine-records/', imports.import_medicine_records, name='admin_import_medicine_records'),
    path('admin/import/import-procedure-records/', imports.import_procedure_records, name='admin_import_procedure_records'),
    path('admin/import/import-referral-records/', imports.import_referral_records, name='admin_import_referral_records'),
    path('admin/import/import-prescription-frequency/', imports.import_prescription_frequency, name='admin_import_prescription_frequency'),
    path('admin/import/import-ambulance-activity-list/', imports.import_ambulance_activity_list, name='admin_import_ambulance_activity_list'),
    path('admin/import/import-medicine-routes-records/', imports.import_medicine_routes_records, name='admin_import_medicine_routes_records'),
    path('admin/import/import-medicine-unit-measures-records/', imports.import_medicine_unit_measures_records, name='admin_import_medicine_unit_measures_records'),


    # Excel Template URLs
    path('admin/download-template/', ExcelTemplate.download_excel_template, name='admin_download_template'),
    path('admin/download-medicine-excel-template/', ExcelTemplate.download_medicine_excel_template, name='admin_download_medicine_excel_template'),
]
