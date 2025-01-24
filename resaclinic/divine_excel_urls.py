from django.urls import path
from kahamahmis import divineExcel

urlpatterns = [
    # Excel template downloads
    path('download-disease-template/', divineExcel.download_disease_recode_excel_template, name='divine_disease_recode_template_download'),
    path('download-health-template/', divineExcel.download_health_record_excel_template, name='divine_health_record_template_download'),
    path('download-remote-company-template/', divineExcel.download_remote_company_excel_template, name='divine_remote_company_template_download'),
    path('download-pathodology-template/', divineExcel.download_pathodology_record_excel_template, name='divine_pathodology_record_template_download'),
    path('download-supplier-template/', divineExcel.download_supplier_excel_template, name='divine_supplier_template_download'),
    path('download-category-template/', divineExcel.download_category_excel_template, name='divine_category_template_download'),
    path('download-service-template/', divineExcel.download_service_excel_template, name='divine_service_template_download'),
    path('download-insurance-company-template/', divineExcel.download_insurance_company_excel_template, name='divine_insurance_company_template_download'),
    path('download-staffs-template/', divineExcel.download_staffs_excel_template, name='divine_staffs_template_download'),
    path('download-prescription-frequency-template/', divineExcel.download_prescription_frequency_excel_template, name='divine_prescription_frequency_template_download'),
    path('download-ambulance-route-template/', divineExcel.download_ambulance_route_excel_template, name='divine_ambulance_route_template_download'),
    path('download-ambulance-vehicle-order-template/', divineExcel.download_ambulance_vehicle_order_excel_template, name='divine_ambulance_vehicle_order_template_download'),
    path('download-hospital-vehicle-template/', divineExcel.download_hospital_vehicle_excel_template, name='divine_hospital_vehicle_template_download'),
    path('download-remote-medicine-template/', divineExcel.download_remote_medicine_excel_template, name='divine_remote_medicine_template_download'),
    path('download-remote-service-template/', divineExcel.download_remote_service_excel_template, name='divine_remote_service_template_download'),
    path('download-country-template/', divineExcel.download_country_excel_template, name='divine_country_template_download'),
    path('download-remote-reagent-template/', divineExcel.download_remote_reagent_excel_template, name='divine_remote_reagent_template_download'),
    path('download-remote-equipment-template/', divineExcel.download_remote_equipment_excel_template, name='divine_remote_equipment_template_download'),
    path('download-diagnosis-template/', divineExcel.download_diagnosis_excel_template, name='divine_diagnosis_template_download'),
]
