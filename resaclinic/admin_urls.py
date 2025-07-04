from django.urls import  path, re_path
from clinic import AdminViews

urlpatterns = [
    path('admin/delete-medicine-route/', AdminViews.delete_medicine_route, name="admin_delete_medicine_route"),
    path('admin/profile/', AdminViews.admin_profile, name='admin_profile'),
    path('resa/pharmacist/change-password/', AdminViews.change_password, name='admin_change_password'),
    path('edit-profile/<int:pk>/', AdminViews.EditStaffProfileView.as_view(), name='admin_edit_staff_profile'),
    path('admin/get-gender-yearly-data/', AdminViews.get_gender_yearly_data, name="admin_get_gender_yearly_data"),
    path('admin/get-gender-monthly-data/', AdminViews.get_gender_monthly_data, name="admin_get_gender_monthly_data"),
    path('admin/delete-medicine-unit-measure/', AdminViews.delete_medicine_unit_measure, name="admin_delete_medicine_unit_measure"),
    path('admin/add-medicine-unit-measure/', AdminViews.add_medicine_unit_measure, name="admin_add_medicine_unit_measure"),
    path('admin/add-medicine-route/', AdminViews.add_medicine_route, name="admin_add_medicine_route"),
    path('admin/medicine-routes/', AdminViews.medicine_routes, name="admin_medicine_routes"),
    path('admin/medicine-unit-measures/', AdminViews.medicine_unit_measures, name="admin_medicine_unit_measures"),
    path('admin/add-service/', AdminViews.add_service, name="admin_add_service"),  
   
    path('admin/fetch-prescription-counts/', AdminViews.fetch_prescription_counts_view, name="admin_fetch_prescription_counts"),
    path('admin/fetch-order-counts/', AdminViews.fetch_order_counts_view, name="admin_fetch_order_counts"),
    path('admin/fetch-radiology-order-counts/', AdminViews.fetch_radiology_order_counts_view, name="admin_fetch_radiology_order_counts"),
    path('admin/fetch-procedure-order-counts/', AdminViews.fetch_procedure_order_counts_view, name="admin_fetch_procedure_order_counts"),
   
   
    path('admin/save-diagnosis/', AdminViews.save_diagnosis, name="admin_save_diagnosis"),
    path('admin/delete-ambulance-activity/', AdminViews.delete_ambulance_activity, name="admin_delete_ambulance_activity"),
    path('admin/add-ambulance-activity/', AdminViews.add_ambulance_activity, name="admin_add_ambulance_activity"),
    path('admin/ambulance-route-list/', AdminViews.ambulance_route_list, name="admin_ambulance_route_list"),
    path('admin/dashboard/', AdminViews.dashboard, name="admin_dashboard"),
    path('admin/employee-detail/', AdminViews.employee_detail, name="admin_employee_detail"),
    path('admin/add-disease/', AdminViews.add_disease, name="admin_add_disease"),    

    path('admin/add-pathology-record/', AdminViews.add_pathodology_record, name="admin_add_pathology_record"),
    path('admin/update-equipment-status/', AdminViews.update_equipment_status, name="admin_update_equipment_status"),


  
    re_path(r'^admin/edit-staff/(?P<staff_id>\w+)/$', AdminViews.edit_staff, name="admin_edit_staff"),
    path('admin/edit-staff-save/', AdminViews.edit_staff_save, name="admin_edit_staff_save"),
    path('admin/delete-ambulance-route/', AdminViews.delete_ambulance_route, name="admin_delete_ambulance_route"),
    path('admin/add-or-edit-ambulance-route/', AdminViews.add_or_edit_ambulance_route, name="admin_add_or_edit_ambulance_route"),
    path('admin/ambulance-routes/', AdminViews.ambulance_route_list, name="admin_ambulance_routes"),
    path('admin/update-staff-status/', AdminViews.update_staff_status, name="admin_update_staff_status"),
    path('admin/update-vehicle-status/', AdminViews.update_vehicle_status, name="admin_update_vehicle_status"),

   
    path('admin/save-staff-view/', AdminViews.save_staff_view, name="admin_save_staff_view"),

    path('admin/add-equipment/', AdminViews.add_equipment, name="admin_add_equipment"),

    path('admin/add-reagent/', AdminViews.add_reagent, name="admin_add_reagent"),


 
    path('admin/resa-report/', AdminViews.resa_report, name="admin_resa_report"),
    path('admin/reports-adjustments/', AdminViews.reports_adjustments, name="admin_reports_adjustments"),
    path('admin/reports-by-visit/', AdminViews.reports_by_visit, name="admin_reports_by_visit"),
    path('admin/reports-comprehensive/', AdminViews.reports_comprehensive, name="admin_reports_comprehensive"),
    path('admin/reports-patients-visit-summary/', AdminViews.reports_patients_visit_summary, name="admin_reports_patients_visit_summary"),
    path('admin/reports-patients/', AdminViews.reports_patients, name="admin_reports_patients"),
    path('admin/reports-service/', AdminViews.reports_service, name="admin_reports_service"),
    path('admin/reports-stock-ledger/', AdminViews.reports_stock_ledger, name="admin_reports_stock_ledger"),
    path('admin/reports-stock-level/', AdminViews.reports_stock_level, name="admin_reports_stock_level"),
    path('admin/reports-orders/', AdminViews.reports_orders, name="admin_reports_orders"),
    path('admin/individual-visit/', AdminViews.individual_visit, name="admin_individual_visit"),
    path('admin/product-summary/', AdminViews.product_summary, name="admin_product_summary"),

  
    path('admin/add-frequency/', AdminViews.add_frequency, name="admin_add_frequency"),
    path('admin/delete-frequency/', AdminViews.delete_frequency, name="admin_delete_frequency"),
    re_path(r'^admin/orders/(?P<date>[\w-]+)/$', AdminViews.orders_by_date, name="admin_orders_by_date"),
    path('admin/prescription-frequencies/', AdminViews.prescription_frequency_list, name="admin_prescription_frequency_list"),
    path('admin/diagnosis/', AdminViews.diagnosis_list, name="admin_diagnosis_list"),
    path('admin/all-orders-view/', AdminViews.all_orders_view, name="admin_all_orders_view"),
  
    path('admin/equipment-list/', AdminViews.equipment_list, name="admin_equipment_list"),
  
    path('admin/reagent-list/', AdminViews.reagent_list, name="admin_reagent_list"),
    path('admin/prescription-list/', AdminViews.prescription_list, name="admin_prescription_list"),

    path('admin/manage-referral/', AdminViews.manage_referral, name="admin_manage_referral"),
    path('admin/patient-procedure-view/', AdminViews.patient_procedure_view, name="admin_patient_procedure_view"),

    path('admin/ambulance-order-view/', AdminViews.ambulance_order_view, name="admin_ambulance_order_view"), 

    path('admin/delete-ambulance-card-order/', AdminViews.delete_ambulancecardorder, name="admin_delete_ambulance_card_order"),
    path('admin/delete-ambulance-order/', AdminViews.delete_ambulancedorder, name="admin_delete_ambulance_order"),
    path('admin/hospital-vehicles/', AdminViews.hospital_vehicle_list, name="admin_hospital_vehicle_list"),
    path('admin/delete-vehicle/', AdminViews.delete_vehicle, name="admin_delete_vehicle"),
    path('admin/add-vehicle/', AdminViews.add_vehicle, name="admin_add_vehicle"),
    path('admin/activity-list/', AdminViews.ambulance_activity_list, name="admin_ambulance_activity_list"),
    path('admin/out-of-stock-medicines/', AdminViews.out_of_stock_medicines_view, name="admin_out_of_stock_medicines_view"),
    path('admin/vehicle-ambulance-view/', AdminViews.vehicle_ambulance_view, name="admin_vehicle_ambulance_view"),

    path('admin/manage-patients/', AdminViews.manage_patient, name="admin_manage_patient"),


    path('admin/manage-disease/', AdminViews.manage_disease, name="admin_manage_disease"),
    path('admin/manage-staff/', AdminViews.manage_staff, name="admin_manage_staff"),

    path('admin/manage-service/', AdminViews.manage_service, name="admin_manage_service"),
    path('admin/manage-pathology/', AdminViews.manage_pathodology, name="admin_manage_pathology"),
    path('admin/appointments/', AdminViews.appointment_list_view, name="admin_appointment_list"),
    re_path(r'^admin/health-record-list/$', AdminViews.health_record_list, name='admin_health_record_list'),
    re_path(r'^admin/save-health-record/$', AdminViews.save_health_record, name='admin_save_health_record'),
    re_path(r'^admin/delete-health-record/$', AdminViews.delete_healthrecord, name='admin_delete_health_record'),
    path('admin/in-stock-medicines/', AdminViews.in_stock_medicines_view, name="admin_in_stock_medicines_view"),
  
    path('admin/medicine-list/', AdminViews.medicine_list, name="admin_medicine_list"),
    path('admin/medicine-expired-list/', AdminViews.medicine_expired_list, name="admin_medicine_expired_list"),
    path('admin/add-medicine/', AdminViews.add_medicine, name="admin_add_medicine"),
    re_path(r'^admin/vehicle-detail/(?P<order_id>\d+)/$', AdminViews.vehicle_detail, name="admin_vehicle_detail"),
    path('api/admin/out-of-stock-medicines/', AdminViews.out_of_stock_medicines, name="api_admin_out_of_stock_medicines"),
    path('api/admin/out-of-stock-reagent-count/', AdminViews.get_out_of_stock_count_reagent, name="admin_get_out_of_stock_count_reagent"),

    path('api/earnings/', AdminViews.get_earnings_data, name='admin_get_earnings_data'),
    path('earnings/monthly-by-year/', AdminViews.get_monthly_earnings_by_year, name='admin_monthly_earnings_by_year'),
    path('counseling/', AdminViews.counseling_list_view, name='admin_counseling_list'),
    path('discharge_notes/', AdminViews.discharge_notes_list_view, name='admin_discharge_notes_list'),
    path('observation_records/', AdminViews.observation_record_list_view, name='admin_observation_record_list'),  

    path('admin/download-invoice/<int:patient_id>/<int:visit_id>/', AdminViews.download_invoice_bill_pdf, name='admin_download_invoice_bill'),
    path('download/consultation-summary/<int:patient_id>/<int:visit_id>/', AdminViews.download_consultation_summary_pdf, name='admin_download_consultation_summary_pdf' ),
    path('imaging/download/<int:imaging_id>/', AdminViews.download_imaging_result_pdf, name='admin_download_imaging_result_pdf' ),
    path('imaging/download/all/<str:patient_mrn>/<str:visit_vst>/', AdminViews.download_all_imaging_results_pdf, name='admin_download_all_imaging_results_pdf'),
    path('lab-result/download/<int:lab_id>/', AdminViews.download_lab_result_pdf, name='admin_download_lab_result_pdf'),
    path('lab/download/all/<str:patient_mrn>/<str:visit_vst>/',AdminViews.download_all_lab_results_pdf, name='admin_download_all_lab_results_pdf'),
    path('procedure/download/all/<str:patient_mrn>/<str:visit_vst>/', AdminViews.download_all_procedures_pdf, name='admin_download_all_procedures_pdf'),
    path('procedure/result/download/<int:procedure_id>/', AdminViews.download_procedure_result_pdf, name='admin_download_procedure_result_pdf'),
    path('download/prescription-bill/<int:patient_id>/<int:visit_id>/', AdminViews.download_prescription_bill_pdf, name='admin_download_prescription_bill_pdf'),
    path('download/prescription-notes/<int:patient_id>/<int:visit_id>/', AdminViews.download_prescription_notes_pdf, name='admin_download_prescription_notes_pdf'),
    path('download-referral-pdf/<int:patient_id>/<int:visit_id>/', AdminViews.download_referral_pdf, name='admin_download_referral_pdf'),
    path('download-counseling-pdf/<int:patient_id>/<int:visit_id>/', AdminViews.download_counseling_pdf, name='admin_download_counseling_pdf'),
    path('download-discharge-pdf/<int:patient_id>/<int:visit_id>/', AdminViews.download_discharge_pdf, name='admin_download_discharge_pdf'),
    path('download/observation/<int:patient_id>/<int:visit_id>/', AdminViews.download_observation_pdf, name='admin_download_observation_pdf'),
    path('consultation-notes/', AdminViews.consultation_notes_view, name='admin_consultation_notes'), 
    path('patient/imaging/view/', AdminViews.patient_imaging_view, name="admin_patient_imaging_view"),  
    path('resa/patient-procedure-view/', AdminViews.patient_procedure_view, name='admin_patient_procedure_view'),
     path('patient_laboratory_view/', AdminViews.patient_laboratory_view, name="admin_patient_laboratory_view"),
   
]

