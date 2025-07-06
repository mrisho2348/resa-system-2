from django.urls import path
from clinic import LabTechnicianView

urlpatterns = [
    # Dashboard and Profile
    path('labtechnician_dashboard/', LabTechnicianView.labtechnician_dashboard, name='labtechnician_dashboard'),
    path('lab-technician/profile/', LabTechnicianView.labTechnician_profile, name='lab_profile'),
    path('resa/lab/change-password/', LabTechnicianView.change_password, name='lab_change_password'),
    path('edit-profile/<int:pk>/', LabTechnicianView.EditStaffProfileView.as_view(), name='lab_edit_staff_profile'),

    # Lab Orders and Results
    path('fetch_laborders_counts/', LabTechnicianView.fetch_laborders_counts, name='lab_fetch_laborders_counts'),
    path('lab/edit-lab-result/<int:lab_id>/', LabTechnicianView.edit_lab_result, name='lab_edit_lab_result'),
    path('lab/results/', LabTechnicianView.lab_results_view, name='lab_results_view'),
    path('lab/results/today/', LabTechnicianView.todays_lab_results_view, name='lab_todays_lab_results_view'),
    path('lab/results/filter/', LabTechnicianView.filter_lab_results_api, name='lab_filter_lab_results_api'),

    # Reagents
    path('reagent_list/', LabTechnicianView.reagent_list, name='lab_reagent_list'),
    path('api/reagent-counts/', LabTechnicianView.reagent_counts_api, name='lab_reagent_counts_api'),
    path('reagents/expired/', LabTechnicianView.lab_reagent_expired, name='lab_reagent_expired'),
    path('reagents/expiring-soon/', LabTechnicianView.lab_reagent_expiring_soon, name='lab_reagent_expiring_soon'),
    path('reagents/out-of-stock/', LabTechnicianView.lab_reagent_out_of_stock, name='lab_reagent_out_of_stock'),

    # Staff
    path('employee_detail/', LabTechnicianView.employee_detail, name='lab_employee_detail'),
    path('staff_detail/<int:staff_id>/', LabTechnicianView.single_staff_detail, name='lab_single_staff_detail'),
]
