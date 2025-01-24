from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from clinic.models import Staffs

class LoginCheckMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        modulename = view_func.__module__
        user = request.user

        # List of paths accessible without authentication
        public_paths = [
            reverse("login"),
            reverse("clinic:DoLogin"),
            reverse("kahamahmis:kahama"),
            reverse("kahamahmis:DoLoginKahama"),
            reverse("clinic:home"),
            reverse("clinic:logout_user")
        ]

        if request.path in public_paths or modulename.startswith("django.contrib.auth.views"):
            return None

        if user.is_authenticated:
            app_name = self.get_app_name(modulename)

            if app_name:
                if user.user_type == "1":
                    return self.handle_admin_user(request, modulename, app_name)
                elif user.user_type == "2":
                    return self.handle_staff_user(request, modulename, app_name, user)

        return None

    def get_app_name(self, modulename):
        if modulename.startswith("clinic"):
            return "clinic"
        elif modulename.startswith("kahamahmis"):
            return "kahamahmis"
        return None

    def handle_admin_user(self, request, modulename, app_name):
        allowed_views = {
            "clinic": [
                "clinic.views",
                "clinic.AdminViews",
                "clinic.HodViews",
                "clinic.ExcelTemplate",
                "clinic.delete",
                "clinic.editView",
                "clinic.imports",
                "clinic.FinancialViews",
                "django.views.static",
            ],
            "kahamahmis": [
                "kahamahmis.kahamaEditView",
                "kahamahmis.kahamaDelete",
                "django.views.static",
                "kahamahmis.views",
                "kahamahmis.kahamaImports",
                "kahamahmis.kahamaExcelTemplate",
                "kahamahmis.KahamaReportsView",
                "kahamahmis.kahamaViews",
                "kahamahmis.kahamaAdmin",
            ],
        }

        dashboard_url = {
            "clinic": "admin_dashboard",
            "kahamahmis": "kahama_dashboard",
        }

        if modulename in allowed_views.get(app_name, []) or request.path == reverse(dashboard_url[app_name]):
            return None

        return redirect(dashboard_url[app_name])

    def handle_staff_user(self, request, modulename, app_name, user):
        try:
            staff = Staffs.objects.get(admin=user)
            role = staff.role.lower()

            app_specific_views = self.get_staff_allowed_views(app_name, staff, role)
            dashboard_url = self.get_staff_dashboard_url(app_name, staff, role)

            if modulename in app_specific_views or request.path == reverse(dashboard_url):
                return None

            return redirect(dashboard_url)

        except Staffs.DoesNotExist:
            return HttpResponseRedirect(reverse("clinic:home"))

    def get_staff_allowed_views(self, app_name, staff, role):
        views = {
            "clinic": {
                "receptionist": ["clinic.ReceptionistView", "clinic.delete", "django.views.static"],
                "doctor": ["clinic.DoctorView", "django.views.static"],
                "admin": [
                    "clinic.views",
                    "clinic.AdminViews",
                    "clinic.HodViews",
                    "clinic.ExcelTemplate",
                    "clinic.delete",
                    "clinic.editView",
                    "clinic.imports",
                    "clinic.FinancialViews",
                    "django.views.static",
                ],
                "nurse": ["clinic.NurseView", "django.views.static"],
                "physiotherapist": ["clinic.PhysiotherapistView", "django.views.static"],
                "labtechnician": ["clinic.LabTechnicianView", "django.views.static"],
                "pharmacist": ["clinic.PharmacistView", "django.views.static"],
            },
            "kahamahmis": {
                "admin": [                  
                    "kahamahmis.divineDelete",
                    "django.views.static",
                    "kahamahmis.views",
                    "kahamahmis.divineImport",
                    "kahamahmis.divineExcel",
                    "kahamahmis.divineReport",
                    "kahamahmis.divine_Admin",
                   
                ],
                "doctor": [
                    "kahamahmis.kahamaEditView",
                    "django.views.static",
                    "kahamahmis.views",                 
                    "kahamahmis.KahamaReportsView",
                    "kahamahmis.kahamaViews",
                    "kahamahmis.kahamaAdmin",
                ],
            },
        }

        return views.get(app_name, {}).get(role, [])

    def get_staff_dashboard_url(self, app_name, staff, role):
        dashboards = {
            "clinic": {
                "receptionist": "receptionist_dashboard",
                "doctor": "doctor_dashboard",
                "admin": "admin_dashboard",
                "nurse": "nurse_dashboard",
                "physiotherapist": "physiotherapist_dashboard",
                "labtechnician": "labtechnician_dashboard",
                "pharmacist": "pharmacist_dashboard",
            },
            "kahamahmis": {
                "admin": "divine_dashboard",
                "doctor": "kahama_dashboard",
            },
        }

        return dashboards.get(app_name, {}).get(role, "clinic:login")
