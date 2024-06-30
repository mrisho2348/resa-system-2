from django.urls import path
from kahamahmis import kahamaExcelTemplate

urlpatterns = [
    # Excel template downloads
    path('download-disease-template/', kahamaExcelTemplate.download_disease_recode_excel_template, name='kahama_disease_recode_template_download'),
    path('download-health-template/', kahamaExcelTemplate.download_health_record_excel_template, name='kahama_health_record_template_download'),
    path('download-remote-company-template/', kahamaExcelTemplate.download_remote_company_excel_template, name='kahama_remote_company_template_download'),
    path('download-pathodology-template/', kahamaExcelTemplate.download_pathodology_record_excel_template, name='kahama_pathodology_record_template_download'),
    path('download-supplier-template/', kahamaExcelTemplate.download_supplier_excel_template, name='kahama_supplier_template_download'),
    path('download-category-template/', kahamaExcelTemplate.download_category_excel_template, name='kahama_category_template_download'),
    path('download-service-template/', kahamaExcelTemplate.download_service_excel_template, name='kahama_service_template_download'),
    path('download-insurance-company-template/', kahamaExcelTemplate.download_insurance_company_excel_template, name='kahama_insurance_company_template_download'),
    path('download-staffs-template/', kahamaExcelTemplate.download_staffs_excel_template, name='kahama_staffs_template_download'),
    path('download-prescription-frequency-template/', kahamaExcelTemplate.download_prescription_frequency_excel_template, name='kahama_prescription_frequency_template_download'),
    path('download-ambulance-route-template/', kahamaExcelTemplate.download_ambulance_route_excel_template, name='kahama_ambulance_route_template_download'),
    path('download-ambulance-vehicle-order-template/', kahamaExcelTemplate.download_ambulance_vehicle_order_excel_template, name='kahama_ambulance_vehicle_order_template_download'),
    path('download-hospital-vehicle-template/', kahamaExcelTemplate.download_hospital_vehicle_excel_template, name='kahama_hospital_vehicle_template_download'),
    path('download-remote-medicine-template/', kahamaExcelTemplate.download_remote_medicine_excel_template, name='kahama_remote_medicine_template_download'),
    path('download-remote-service-template/', kahamaExcelTemplate.download_remote_service_excel_template, name='kahama_remote_service_template_download'),
    path('download-country-template/', kahamaExcelTemplate.download_country_excel_template, name='kahama_country_template_download'),
    path('download-remote-reagent-template/', kahamaExcelTemplate.download_remote_reagent_excel_template, name='kahama_remote_reagent_template_download'),
    path('download-remote-equipment-template/', kahamaExcelTemplate.download_remote_equipment_excel_template, name='kahama_remote_equipment_template_download'),
    path('download-diagnosis-template/', kahamaExcelTemplate.download_diagnosis_excel_template, name='kahama_diagnosis_template_download'),
]
