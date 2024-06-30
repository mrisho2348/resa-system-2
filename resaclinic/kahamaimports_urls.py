from django.urls import path
from kahamahmis import kahamaImports

urlpatterns = [
    # Import URLs
    path('import_insurance_company_data/', kahamaImports.import_insurance_company_data, name='kahama_import_insurance_company_data'),
    path('import-disease-data/', kahamaImports.import_disease_recode_data, name='kahama_import_disease_recode_data'),
    path('import-remote-medicine-data/', kahamaImports.import_remote_medicine_data, name='kahama_import_remote_medicine_data'),
    path('import-health-record-data/', kahamaImports.import_health_record_data, name='kahama_import_health_record_data'),
    path('import-remote-company-data/', kahamaImports.import_remote_company_data, name='kahama_import_remote_company_data'),
    path('import-pathodology-record-data/', kahamaImports.import_pathodology_record_data, name='kahama_import_pathodology_record_data'),
    path('import-remote-service-data/', kahamaImports.import_remote_service_data, name='kahama_import_remote_service_data'),
    path('import-country-data/', kahamaImports.import_country_data, name='kahama_import_country_data'),
    path('import-remote-reagent/', kahamaImports.import_remote_reagent_data, name='kahama_import_remote_reagent_data'),
    path('import-remote-equipment/', kahamaImports.import_remote_equipment_data, name='kahama_import_remote_equipment_data'),
    path('import-diagnosis-data/', kahamaImports.import_diagnosis_data, name='kahama_import_diagnosis_data'),
]
