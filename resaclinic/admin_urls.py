from django.urls import path
from clinic.AdminViews import *
from clinic.resa_delete import *


urlpatterns = [
    # Dashboard and reports
    path('resa_admin/dashboard/', dashboard, name='resa_admin_dashboard'),
    path('resa_admin/earnings-data/', get_earnings_data, name='resa_admin_earnings_data'),
    path('api/financial-chart-data/', financial_chart_data, name='resa_financial_chart_data'),
    path('api/today-activities/', TodayActivitiesView.as_view(), name='resa_admin_today_activities'),
    path('resa_admin/monthly-earnings/', get_monthly_earnings_by_year, name='resa_admin_monthly_earnings'),
    path('activity_log/', ActivityLogView.as_view(), name='resa_admin_activity_log'),
    path('restock_medicine/', restock_medicine, name='resa_admin_restock_medicine'),
    
    path('medicine-types/', medicine_types_management, name='resa_admin_manage_medicine_types'),
    path('add-medicine-type/', add_medicine_type, name='resa_admin_add_medicine_type'),
    path('edit-medicine-type/', edit_medicine_type, name='resa_admin_edit_medicine_type'),
    path('delete-medicine-type/', delete_medicine_type, name='resa_admin_delete_medicine_type'),

    path('medicine/<int:medicine_id>/dosages/', medicine_dosage_management, name='resa_admin_medicine_dosage_management'),
    path('add_dosage/', add_dosage, name='resa_admin_add_dosage'),
    path('edit_dosage/', edit_dosage, name='resa_admin_edit_dosage'),
    path('delete_dosage/', delete_dosage, name='resa_admin_delete_dosage'),
    path('set_default_dosage/', set_default_dosage, name='resa_admin_set_default_dosage'),
    # Profile management
    path('resa_admin/profile/', admin_profile, name='resa_admin_profile'),
    path('resa_admin/change-password/', change_password, name='resa_admin_change_password'),
    path('resa_admin/edit-staff-profile/<int:pk>/', EditStaffProfileView.as_view(), name='resa_admin_edit_staff_profile'),
    
    # Patient management
    path('resa_admin/manage-patients/', manage_patient, name='resa_admin_manage_patient'),
    path('resa_admin/gender-yearly-data/', get_gender_yearly_data, name='resa_admin_gender_yearly_data'),
    path('resa_admin/gender-monthly-data/', get_gender_monthly_data, name='resa_admin_gender_monthly_data'),
    
    # Medical records
    path('resa_admin/manage-disease/', manage_disease, name='resa_admin_manage_disease'),
    path('resa_admin/manage-pathodology/', manage_pathodology, name='resa_admin_manage_pathodology'),
    path('resa_admin/health-records/', health_record_list, name='resa_admin_health_record_list'),
    
    # Staff management
    path('resa_admin/manage-staff/', manage_staff, name='resa_admin_manage_staff'),
    path('resa_admin/edit-staff/<int:staff_id>/', edit_staff, name='resa_admin_edit_staff'),
    path('resa_admin/edit-staff-save/', edit_staff_save, name='resa_admin_edit_staff_save'),
    path('resa_admin/update-staff-status/', update_staff_status, name='resa_admin_update_staff_status'),
    
    # Medicine management
    path('resa_admin/manage-medicine/', medicine_list, name='resa_admin_medicine_list'),
    path('resa_admin/out-of-stock-medicines/', out_of_stock_medicines_view, name='resa_admin_out_of_stock_medicines'),
    path('resa_admin/in-stock-medicines/', in_stock_medicines_view, name='resa_admin_in_stock_medicines'),
    
    # Services management
    path('resa_admin/manage-service/', manage_service, name='resa_admin_manage_service'),
    
    # Reports
    path('resa_admin/reports/adjustments/', reports_adjustments, name='resa_admin_reports_adjustments'),
    path('resa_admin/reports/by-visit/', reports_by_visit, name='resa_admin_reports_by_visit'),
    path('resa_admin/reports/comprehensive/', reports_comprehensive, name='resa_admin_reports_comprehensive'),
    path('resa_admin/reports/patients-visit-summary/', reports_patients_visit_summary, name='resa_admin_reports_patients_visit_summary'),
    path('resa_admin/reports/patients/', reports_patients, name='resa_admin_reports_patients'),
    path('resa_admin/reports/service/', reports_service, name='resa_admin_reports_service'),
    path('resa_admin/reports/stock-ledger/', reports_stock_ledger, name='resa_admin_reports_stock_ledger'),
    path('resa_admin/reports/stock-level/', reports_stock_level, name='resa_admin_reports_stock_level'),
    path('resa_admin/reports/orders/', reports_orders, name='resa_admin_reports_orders'),
    path('resa_admin/reports/individual-visit/', individual_visit, name='resa_admin_individual_visit'),
    path('resa_admin/reports/product-summary/', product_summary, name='resa_admin_product_summary'),
    
    # Orders and prescriptions
    path('resa_admin/orders/', all_orders_view, name='resa_admin_all_orders'),
    path('resa_admin/orders-by-date/<str:date>/', orders_by_date, name='resa_admin_orders_by_date'),
    path('resa_admin/prescriptions/', prescription_list, name='resa_admin_prescription_list'),
    
    path('walkin-prescriptions/', walkin_prescription_list, name='resa_admin_walkin_prescription_list'),  
    path('generate_walkin_receipt_pdf/<int:visit_id>/', generate_walkin_receipt_pdf, name='resa_admin_generate_walkin_receipt_pdf'),
    path('download_prescription_notes/<int:visit_id>/', download_prescription_notes, name='resa_admin_download_prescription_notes'),
    # Diagnostics
    path('resa_admin/procedures/', patient_procedure_view, name='resa_admin_patient_procedure'),
    path('resa_admin/lab-results/', patient_laboratory_view, name='resa_admin_patient_laboratory'),
    path('resa_admin/imaging-results/', patient_imaging_view, name='resa_admin_patient_imaging'),
    
    # Vehicles and ambulance
    path('resa_admin/vehicles/', hospital_vehicle_list, name='resa_admin_hospital_vehicle_list'),
    path('resa_admin/ambulance-orders/', ambulance_order_view, name='resa_admin_ambulance_order'),
    path('resa_admin/ambulance-activities/', ambulance_activity_list, name='resa_admin_ambulance_activity_list'),
    path('resa_admin/ambulance-routes/', ambulance_route_list, name='resa_admin_ambulance_route_list'),
    
    # Consultation records
    path('resa_admin/consultation-notes/', consultation_notes_view, name='resa_admin_consultation_notes'),
    path('resa_admin/counseling/', counseling_list_view, name='resa_admin_counseling_list'),
    path('resa_admin/discharges/', discharge_notes_list_view, name='resa_admin_discharge_list'),
    path('resa_admin/observations/', observation_record_list_view, name='resa_admin_observation_list'),
    path('resa_admin/referrals/', manage_referral, name='resa_admin_referral_list'),
    path('resa_admin/appointments/', appointment_list_view, name='resa_admin_appointment_list'),
    
    # Employee management
    path('resa_admin/employee-detail/', employee_detail, name='resa_admin_employee_detail'),
    
    # Medicine configuration
    path('resa_admin/medicine-routes/', medicine_routes, name='resa_admin_medicine_routes'),
    path('resa_admin/medicine-unit-measures/', medicine_unit_measures, name='resa_admin_medicine_unit_measures'),

    path('medicine-dosages/', medicine_dosage_managements, name='resa_admin_medicine_dosage_management'),
    path('add-medicine-dosage/', add_medicine_dosage, name='resa_admin_add_medicine_dosage'),
    path('update-medicine-dosage/', update_medicine_dosage, name='resa_admin_update_medicine_dosage'),
    path('set-default-dosage/', set_default_dosages, name='resa_admin_set_default_dosage'),
    path('delete-medicine-dosage/', delete_medicine_dosage, name='resa_admin_delete_medicine_dosage'),
    
    # PDF reports
    path('resa_admin/download-observation-pdf/<int:patient_id>/<int:visit_id>/', download_observation_pdf, name='resa_admin_download_observation_pdf'),
    path('resa_admin/download-discharge-pdf/<int:patient_id>/<int:visit_id>/', download_discharge_pdf, name='resa_admin_download_discharge_pdf'),
    path('resa_admin/download-counseling-pdf/<int:patient_id>/<int:visit_id>/', download_counseling_pdf, name='resa_admin_download_counseling_pdf'),
    path('resa_admin/download-referral-pdf/<int:patient_id>/<int:visit_id>/', download_referral_pdf, name='resa_admin_download_referral_pdf'),
    path('resa_admin/download-prescription-notes/<int:patient_id>/<int:visit_id>/', download_prescription_notes_pdf, name='resa_admin_download_prescription_notes'),
    path('resa_admin/download-prescription-bill/<int:patient_id>/<int:visit_id>/', download_prescription_bill_pdf, name='resa_admin_download_prescription_bill'),
    path('resa_admin/download-procedure-result/<int:procedure_id>/', download_procedure_result_pdf, name='resa_admin_download_procedure_result'),
    path('resa_admin/download-all-procedures/<str:patient_mrn>/<str:visit_vst>/', download_all_procedures_pdf, name='resa_admin_download_all_procedures'),
    path('resa_admin/download-lab-result/<int:lab_id>/', download_lab_result_pdf, name='resa_admin_download_lab_result'),
    path('resa_admin/download-all-lab-results/<str:patient_mrn>/<str:visit_vst>/', download_all_lab_results_pdf, name='resa_admin_download_all_lab_results'),
    path('resa_admin/download-imaging-result/<int:imaging_id>/', download_imaging_result_pdf, name='resa_admin_download_imaging_result'),
    path('resa_admin/download-all-imaging-results/<str:patient_mrn>/<str:visit_vst>/', download_all_imaging_results_pdf, name='resa_admin_download_all_imaging_results'),
    path('resa_admin/download-consultation-summary/<int:patient_id>/<int:visit_id>/', download_consultation_summary_pdf, name='resa_admin_download_consultation_summary'),
    path('resa_admin/download-invoice/<int:patient_id>/<int:visit_id>/', download_invoice_bill_pdf, name='resa_admin_download_invoice'),
    
    # AJAX handlers
    path('financial-analytics/', financial_analytics, name='resa_admin_financial_analytics'),
    path('export-financial-report/', export_financial_report, name='resa_admin_export_financial_report'),
    path('resa_admin/save-health-record/', save_health_record, name='resa_admin_save_health_record'),
    path('resa_admin/delete-health-record/', delete_healthrecord, name='resa_admin_delete_health_record'),
    path('resa_admin/save-staff/', save_staff_view, name='resa_admin_save_staff'),
    path('resa_admin/add-medicine/', add_medicine, name='resa_admin_add_medicine'),
    path('resa_admin/add-disease/', add_disease, name='resa_admin_add_disease'),
    path('resa_admin/add-pathodology/', add_pathodology_record, name='resa_admin_add_pathodology'),
    path('resa_admin/add-equipment/', add_equipment, name='resa_admin_add_equipment'),
    path('resa_admin/equipment_list/', equipment_list, name='resa_admin_equipment_list'),
    path('resa_admin/add-reagent/', add_reagent, name='resa_admin_add_reagent'),
    path('resa_admin/reagent_list/', reagent_list, name='resa_admin_reagent_list'),
    path('resa_admin/add-service/', add_service, name='resa_admin_add_service'),
    path('resa_admin/add-vehicle/', add_vehicle, name='resa_admin_add_vehicle'),
    path('resa_admin/update-vehicle-status/', update_vehicle_status, name='resa_admin_update_vehicle_status'),
    path('resa_admin/update-equipment-status/', update_equipment_status, name='resa_admin_update_equipment_status'),
    path('resa_admin/add-ambulance-route/', add_or_edit_ambulance_route, name='resa_admin_add_ambulance_route'),
    path('resa_admin/add-ambulance-activity/', add_ambulance_activity, name='resa_admin_add_ambulance_activity'),
    path('resa_admin/add-medicine-route/', add_medicine_route, name='resa_admin_add_medicine_route'),
    path('resa_admin/add-medicine-unit/', add_medicine_unit_measure, name='resa_admin_add_medicine_unit'),
    path('resa_admin/delete-ambulance-order/', delete_ambulancedorder, name='resa_admin_delete_ambulance_order'),
    path('resa_admin/delete-ambulance-vehicle-order/', delete_ambulancecardorder, name='resa_admin_delete_ambulance_vehicle_order'),
    path('resa_admin/delete-ambulance-route/', delete_ambulance_route, name='resa_admin_delete_ambulance_route'),
    path('resa_admin/delete-ambulance-activity/', delete_ambulance_activity, name='resa_admin_delete_ambulance_activity'),
    path('resa_admin/delete-medicine-route/', delete_medicine_route, name='resa_admin_delete_medicine_route'),
    path('resa_admin/delete-medicine-unit/', delete_medicine_unit_measure, name='resa_admin_delete_medicine_unit'),
    path('resa_admin/delete-vehicle/', delete_vehicle, name='resa_admin_delete_vehicle'),
    path('resa_admin/add-frequency/', add_frequency, name='resa_admin_add_frequency'),
    path('resa_admin/delete-frequency/', delete_frequency, name='resa_admin_delete_frequency'),
    path('resa_admin/save-diagnosis/', save_diagnosis, name='resa_admin_save_diagnosis'),
    path('resa_admin/diagnosis-list/', diagnosis_list, name='resa_admin_diagnosis_list'),
    path('resa_admin/requency/', prescription_frequency_list, name='resa_admin_prescription_frequency_list'),
    
    # Data endpoints
    path('resa_admin/out-of-stock-count/', out_of_stock_medicines, name='resa_admin_out_of_stock_count'),
    path('resa_admin/reagent-out-of-stock-count/', get_out_of_stock_count_reagent, name='resa_admin_reagent_out_of_stock_count'),
    path('resa_admin/fetch-order-counts/', fetch_order_counts_view, name='resa_admin_fetch_order_counts'),
    path('resa_admin/fetch-radiology-order-counts/', fetch_radiology_order_counts_view, name='resa_admin_fetch_radiology_order_counts'),
    path('resa_admin/fetch-procedure-order-counts/', fetch_procedure_order_counts_view, name='resa_admin_fetch_procedure_order_counts'),
    path('resa_admin/fetch-prescription-counts/', fetch_prescription_counts_view, name='resa_admin_fetch_prescription_counts'),

     # Delete views
    path('resa_admin/delete-medicine/', delete_medicine, name='resa_admin_delete_medicine'),
    path('resa_admin/delete-patient/', delete_patient, name='resa_admin_delete_patient'),
    path('resa_admin/delete-procedure/', delete_procedure, name='resa_admin_delete_procedure'),
    path('resa_admin/delete-referral/', delete_referral, name='resa_admin_delete_referral'),
    path('resa_admin/delete-service/', delete_service, name='resa_admin_delete_service'),
    path('resa_admin/delete-equipment/', delete_equipment, name='resa_admin_delete_equipment'),
    path('resa_admin/delete-patient-visit/', delete_patient_visit, name='resa_admin_delete_patient_visit'),
    path('resa_admin/delete-prescription/<int:prescription_id>/', delete_prescription, name='resa_admin_delete_prescription'),
    path('resa_admin/delete-pathology/', delete_pathology_record, name='resa_admin_delete_pathology'),
    path('resa_admin/delete-reagent/', delete_reagent, name='resa_admin_delete_reagent'),
    path('resa_admin/delete-patient-vital/', delete_patient_vital, name='resa_admin_delete_patient_vital'),
    path('resa_admin/delete-diagnosis/', delete_diagnosis, name='resa_admin_delete_diagnosis'),
    path('delete-disease/', delete_disease, name='resa_admin_delete_disease'),
    path('resa_admin/delete-consultation/<int:consultation_id>/', delete_ConsultationNotes, name='resa_admin_delete_consultation'),
]