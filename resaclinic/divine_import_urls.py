from django.urls import path
from kahamahmis import divineImport

urlpatterns = [
    # Import URLs
    path('import_insurance_company_data/', divineImport.import_insurance_company_data, name='divine_import_insurance_company_data'),
    path('import-disease-data/', divineImport.import_disease_recode_data, name='divine_import_disease_recode_data'),
    path('import-remote-medicine-data/', divineImport.import_remote_medicine_data, name='divine_import_remote_medicine_data'),
    path('import-health-record-data/', divineImport.import_health_record_data, name='divine_import_health_record_data'),
    path('import-remote-company-data/', divineImport.import_remote_company_data, name='divine_import_remote_company_data'),
    path('import-pathodology-record-data/', divineImport.import_pathodology_record_data, name='divine_import_pathodology_record_data'),
    path('import-remote-service-data/', divineImport.import_remote_service_data, name='divine_import_remote_service_data'),
    path('import-country-data/', divineImport.import_country_data, name='divine_import_country_data'),
    path('import-remote-reagent/', divineImport.import_remote_reagent_data, name='divine_import_remote_reagent_data'),
    path('import-remote-equipment/', divineImport.import_remote_equipment_data, name='divine_import_remote_equipment_data'),
    path('import-diagnosis-data/', divineImport.import_diagnosis_data, name='divine_import_diagnosis_data'),
]
