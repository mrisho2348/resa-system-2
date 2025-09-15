from django.urls import path
from clinic.LabTechnicianView import *

urlpatterns = [
    # Dashboard and Profile
    path('labtechnician_dashboard/', labtechnician_dashboard, name='labtechnician_dashboard'),
    path('lab-technician/profile/', labTechnician_profile, name='lab_profile'),
    path('resa/lab/change-password/', change_password, name='lab_change_password'),
    path('edit-profile/<int:pk>/', EditStaffProfileView.as_view(), name='lab_edit_staff_profile'),
    path('api/lab-technician-stats/', technician_stats_api, name='lab_technician_stats_api'),
    path('api/lab-technician-notifications/', technician_notifications_api, name='lab_technician_notifications_api'),
     path('lab-dashboard-counts/', lab_dashboard_counts, name='lab_dashboard_counts'),

    path('lab-test-status-data/', test_status_data, name='lab_test_status_data'),
    path('lab-reagent-stock-data/', reagent_stock_data, name='lab_reagent_stock_data'),
    path('pending-tests/', pending_tests, name='lab_pending_tests'),
    path('completed-tests/', completed_tests, name='lab_completed_tests'),
    path('reagents-expiring-soon/', reagent_expiring_soon, name='lab_reagent_expiring_soon'),
    path('reagents-out-of-stock/', reagent_out_of_stock, name='lab_reagent_out_of_stock'),
    path('reagents-low-stock/', reagent_low_stock, name='lab_reagent_low_stock'),
    # Lab Orders and Results
    path('fetch_laborders_counts/', fetch_laborders_counts, name='lab_fetch_laborders_counts'),
    path('lab/edit-lab-result/<int:lab_id>/', edit_lab_result, name='lab_edit_lab_result'),
    path('lab/results/', lab_results_view, name='lab_results_view'),
    path('lab/results/today/', todays_lab_results_view, name='lab_todays_lab_results_view'),
    path('lab/results/filter/', filter_lab_results_api, name='lab_filter_lab_results_api'),

    # Reagents
    path('reagent_list/', reagent_list, name='lab_reagent_list'),
    path('api/reagent-counts/', reagent_counts_api, name='lab_reagent_counts_api'),
    path('reagents/expired/', lab_reagent_expired, name='lab_reagent_expired'),
    path('reagents/expiring-soon/', lab_reagent_expiring_soon, name='lab_reagent_expiring_soon'),
    path('reagents/out-of-stock/', lab_reagent_out_of_stock, name='lab_reagent_out_of_stock'),

    # Staff
    path('employee_detail/', employee_detail, name='lab_employee_detail'),
    path('staff_detail/<int:staff_id>/', single_staff_detail, name='lab_single_staff_detail'),
]
