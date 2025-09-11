from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from clinic.models import Staffs


class LoginCheckMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        modulename = view_func.__module__
        user = request.user

        # Public paths accessible without login
        public_paths = [
            reverse("clinic:home"),
            reverse("clinic:logout_user"),
            reverse("resa_portal"),
            reverse("resa_portal_login"),
            reverse("forgot_password"),
            reverse("portfolio_details"),
            reverse("contact"),
            reverse("blog_single"),
            reverse("page_404"),
        ]

        if (request.path in public_paths
            or modulename.startswith("django.contrib.auth.views")
            or modulename == "django.views.static"):
            return None

        if user.is_authenticated:
            if user.user_type == "1":  # super admin
                return None  # full access

            elif user.user_type == "2":  # staff
                try:
                    staff = Staffs.objects.get(admin=user)
                    role = staff.role.lower()
                    workplace = staff.work_place.lower()  # <-- assuming you have this field

                    # Get dashboard and allowed views from lookup table
                    dashboard_url = self.get_staff_dashboard(role, workplace)
                    allowed_views = self.get_staff_allowed_views(role, workplace)

                    if modulename in allowed_views or request.path == reverse(dashboard_url):
                        return None
                    return redirect(dashboard_url)

                except Staffs.DoesNotExist:
                    return HttpResponseRedirect(reverse("clinic:home"))

        return None

    def get_staff_allowed_views(self, role, workplace):
        """Return allowed view modules for staff based on role + workplace."""
        views = {
            # Clinic staff
            ("receptionist", "resa"): ["clinic.ReceptionistView", "clinic.delete", "django.views.static"],
            ("doctor", "resa"): ["clinic.DoctorView", "django.views.static"],
            ("nurse", "resa"): ["clinic.NurseView", "django.views.static"],
            ("labtechnician", "resa"): ["clinic.LabTechnicianView", "django.views.static"],
            ("pharmacist", "resa"): ["clinic.PharmacistView", "django.views.static"],
            ("admin", "resa"): [
                "clinic.views",
                "clinic.AdminViews",
                "clinic.HodViews",
                "clinic.ExcelTemplate",
                "clinic.resa_delete",
                "clinic.editView",
                "clinic.imports",
                "clinic.FinancialViews",
                "django.views.static",
            ],

            # Kahama staff
            ("doctor", "kahama"): [
                "kahamahmis.doctor.kahamaDoctor",
                "kahamahmis.kahamaReports",             
                "django.views.static",
            ],
            ("admin", "kahama"): [
                "kahamahmis.views",
                "kahamahmis.kahamaExcelTemplate",
                "kahamahmis.kahamaReports",
                "kahamahmis.admin.kahamaAdmin",
                "django.views.static",
            ],

            # Pemba staff
            ("doctor", "pemba"): [
                "pembahmis.doctor.pembaDoctor",
                "pembahmis.pembaReports",
                "pembahmis.views",
                "django.views.static",
            ],
            ("admin", "pemba"): [
                "pembahmis.views",
                "pembahmis.admin.pembaAdmin",
                "pembahmis.pembaReports",
                "django.views.static",
            ],
        }
        return views.get((role, workplace), [])

    def get_staff_dashboard(self, role, workplace):
        """Return dashboard url name for staff based on role + workplace."""
        dashboards = {
            # Clinic staff dashboards
            ("receptionist", "resa"): "receptionist_dashboard",
            ("doctor", "resa"): "doctor_dashboard",
            ("nurse", "resa"): "nurse_dashboard",
            ("labtechnician", "resa"): "labtechnician_dashboard",
            ("pharmacist", "resa"): "pharmacist_dashboard",
            ("admin", "resa"): "admin_dashboard",

            # Kahama staff dashboards
            ("admin", "kahama"): "kahama_admin_dashboard",
            ("doctor", "kahama"): "kahama_doctor_dashboard",

            # Pemba staff dashboards
            ("admin", "pemba"): "pemba_admin_dashboard",
            ("doctor", "pemba"): "pemba_doctor_dashboard",
        }
        return dashboards.get((role, workplace), "resa_portal")
