from django.urls import path
from clinic import PharmacistView

urlpatterns = [

    # ------------------ Dashboard & Profile ------------------
    path('pharmacist_dashboard/', PharmacistView.pharmacist_dashboard, name='pharmacist_dashboard'),
    path('pharmacist/profile/', PharmacistView.pharmacist_profile, name='pharmacist_profile'),
    path('edit-profile/<int:pk>/', PharmacistView.EditStaffProfileView.as_view(), name='pharmacist_edit_staff_profile'),
    path('resa/pharmacist/change-password/', PharmacistView.change_password, name='pharmacist_change_password'),

    path('employee_detail/', PharmacistView.employee_detail, name='pharmacist_employee_detail'),

    # ------------------ Prescription Management ------------------

    path('prescriptions/', PharmacistView.prescription_list, name='pharmacist_prescription_list'),
    path('todays/prescriptions/', PharmacistView.todays_prescriptions, name='pharmacist_todays_prescriptions'),
  

    # Verification & Payment Actions
    path('verify_prescriptions/', PharmacistView.verify_prescriptions, name='pharmacist_verify_prescriptions'),
    path('unverify_prescriptions/', PharmacistView.unverify_prescriptions, name='pharmacist_unverify_prescriptions'),
    path('issue_prescriptions/', PharmacistView.issue_prescriptions, name='pharmacist_issue_prescriptions'),
    path('unissue_prescriptions/', PharmacistView.unissue_prescriptions, name='pharmacist_unissue_prescriptions'),
   

    # ------------------ Medicine Management ------------------
    path('add_medicine/', PharmacistView.add_medicine, name='pharmacist_add_medicine'),
    path('medicine_list/', PharmacistView.medicine_list, name='pharmacist_medicine_list'),
    path('medicine_expired_list/', PharmacistView.medicine_expired_list, name='pharmacist_medicine_expired_list'),

    # Stock Management
    path('in_stock_medicines_view/', PharmacistView.in_stock_medicines_view, name='pharmacist_in_stock_medicines_view'),
    path('out_of_stock_medicines_view/', PharmacistView.out_of_stock_medicines_view, name='pharmacist_out_of_stock_medicines_view'),
    path('pharmacist/medicine-counts/', PharmacistView.medicine_counts_api, name='pharmacist_medicine_counts_api'),

 

    # ------------------ AJAX/Utility Endpoints ------------------
    path('pharmacist/get_unit_price/', PharmacistView.get_unit_price, name='pharmacist_get_unit_price'),
    path('pharmacist/get_drug_division_status/', PharmacistView.get_drug_division_status, name='pharmacist_get_drug_division_status'),
    path('pharmacist/get_medicine_formulation/', PharmacistView.get_medicine_formulation, name='pharmacist_get_medicine_formulation'),
    path('pharmacist/get_formulation_unit/', PharmacistView.get_formulation_unit, name='pharmacist_get_formulation_unit'),
    path('pharmacist/get_frequency_name/', PharmacistView.get_frequency_name, name='pharmacist_get_frequency_name'),
    path('pharmacist/medicine_dosage/', PharmacistView.medicine_dosage, name='pharmacist_medicine_dosage'),

    # ------------------ Reagents ------------------
    path('reagent_list/', PharmacistView.reagent_list, name='pharmacist_reagent_list'),
    path('reagents/expired/', PharmacistView.lab_reagent_expired, name='pharmacist_reagent_expired'),
    path('reagents/expiring-soon/', PharmacistView.lab_reagent_expiring_soon, name='pharmacist_reagent_expiring_soon'),
    path('reagents/out-of-stock/', PharmacistView.lab_reagent_out_of_stock, name='pharmacist_reagent_out_of_stock'),
    path('api/reagent-counts/', PharmacistView.reagent_counts_api, name='pharmacist_reagent_counts_api'),
    path('doctor/add_remoteprescription/', PharmacistView.add_remoteprescription, name='pharmacist_add_remoteprescription'),    
    path('pharmacist/visit-list/', PharmacistView.visit_list, name='pharmacist_visit_list'),
    path('doctor/save_prescription/<int:patient_id>/<int:visit_id>/', PharmacistView.save_prescription, name='pharmacist_save_prescription'),
]
