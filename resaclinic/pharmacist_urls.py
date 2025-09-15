from django.urls import path
from clinic.PharmacistView import *

urlpatterns = [

    # ------------------ Dashboard & Profile ------------------
    path('dashboard/', pharmacist_dashboard, name='pharmacist_dashboard'),
    path('today-dispensed/', today_dispensed, name='pharmacist_today_dispensed'),
    path('restock-medicine/', restock_medicine, name='pharmacist_restock_medicine'),
    path('low-stock-medicines/', low_stock_medicines, name='pharmacist_low_stock_medicines'),
    path('manage-patient/', manage_patient, name='pharmacist_manage_patient'),
    path('expired-medicines/', expired_medicines, name='pharmacist_expired_medicines'),
    path('expiring-soon-medicines/', expiring_soon_medicines, name='pharmacist_expiring_soon_medicines'),
    path('api/stock-data/', pharmacy_stock_data, name='pharmacy_stock_data'),
    path('api/prescription-status-data/', pharmacy_prescription_status_data, name='pharmacy_prescription_status_data'),
    path('pharmacist/profile/', pharmacist_profile, name='pharmacist_profile'),
    path('edit-profile/<int:pk>/', EditStaffProfileView.as_view(), name='pharmacist_edit_staff_profile'),
    path('resa/pharmacist/change-password/', change_password, name='pharmacist_change_password'),
      path('pharmacist-dashboard-counts/', pharmacist_dashboard_counts, name='pharmacist_dashboard_counts'),
      

    path('employee_detail/', employee_detail, name='pharmacist_employee_detail'),

    # ------------------ Prescription Management ------------------

    path('prescriptions/', prescription_list, name='pharmacist_prescription_list'),
    path('todays/prescriptions/', todays_prescriptions, name='pharmacist_todays_prescriptions'),
  

    # Verification & Payment Actions
    path('verify_prescriptions/', verify_prescriptions, name='pharmacist_verify_prescriptions'),
    path('unverify_prescriptions/', unverify_prescriptions, name='pharmacist_unverify_prescriptions'),
    path('issue_prescriptions/', issue_prescriptions, name='pharmacist_issue_prescriptions'),
    path('unissue_prescriptions/', unissue_prescriptions, name='pharmacist_unissue_prescriptions'),
    path('generate_walkin_receipt_pdf/<int:visit_id>/', generate_walkin_receipt_pdf, name='pharmacist_generate_walkin_receipt_pdf'),
    path('download_prescription_notes/<int:visit_id>/', download_prescription_notes, name='pharmacist_download_prescription_notes'),
    # ------------------ Medicine Management ------------------
    path('add_medicine/', add_medicine, name='pharmacist_add_medicine'),
    path('medicine_list/', medicine_list, name='pharmacist_medicine_list'),
    path('medicine_expired_list/', medicine_expired_list, name='pharmacist_medicine_expired_list'),

    # Stock Management
    path('in_stock_medicines_view/', in_stock_medicines_view, name='pharmacist_in_stock_medicines_view'),
    path('out_of_stock_medicines_view/', out_of_stock_medicines_view, name='pharmacist_out_of_stock_medicines_view'),
    path('pharmacist/medicine-counts/', medicine_counts_api, name='pharmacist_medicine_counts_api'),



    # ------------------ Reagents ------------------ 
    path('doctor/add_remoteprescription/', add_remoteprescription, name='pharmacist_add_remoteprescription'),    
    path('pharmacist/visit-list/', visit_list, name='pharmacist_visit_list'),
    path('doctor/save_prescription/<int:patient_id>/<int:visit_id>/', save_prescription, name='pharmacist_save_prescription'),
    path('get-cash-price/', get_cash_price, name='pharmacist_get_cash_price'),
    path('non-registered-prescription/', add_non_registered_prescription, name='pharmacist_add_non_registered_prescription'),
    path('add-walkin-prescription/', add_walkin_prescription, name='pharmacist_add_walkin_prescription'),
    path('get-medicine-details/', get_medicine_details,    name='pharmacist_get_medicine_details'),
    path('walkin-prescriptions/', walkin_prescription_list, name='pharmacist_walkin_prescription_list'),

    path('update-walkin-payment-status/', update_walkin_payment_status, name='pharmacist_update_walkin_payment_status'),
    path('walkin-prescription-stats/', walkin_prescription_stats, name='pharmacist_walkin_prescription_stats'),
]
