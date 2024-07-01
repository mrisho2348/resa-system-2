from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponseRedirect

from clinic.models import Staffs


class LoginCheckMiddleWare(MiddlewareMixin):
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        modulename = view_func.__module__
        user = request.user

        # Allow access to login/logout pages and authentication-related views
        if (request.path == reverse("login") or            
            request.path == reverse("clinic:DoLogin") or
            request.path == reverse("kahamahmis:kahama") or
            request.path == reverse("kahamahmis:DoLoginKahama") or
            request.path == reverse("clinic:home") or
            request.path == reverse("clinic:logout_user") or
            modulename.startswith("django.contrib.auth.views")):
            return None
        
        if user.is_authenticated:
            # Check if the user belongs to the clinic or kahamahmis app
            if modulename.startswith("clinic"):
                app_name = "clinic"
            elif modulename.startswith("kahamahmis"):
                app_name = "kahamahmis"
            else:
                app_name = None
            
            if app_name:
                # Redirect based on user type and role in the specific app
                if user.user_type == "1":
                    if app_name == "clinic":
                        allowed_views = [
                            "clinic.views",
                            "clinic.AdminViews",
                            "clinic.HodViews",
                            "clinic.ExcelTemplate",
                            "clinic.delete",
                            "clinic.editView",                         
                            "clinic.imports",                         
                            "clinic.FinancialViews",                         
                            "django.views.static",
                        ]
                        if modulename in allowed_views or request.path == reverse("admin_dashboard"):
                            return None
                        else:
                            return redirect("admin_dashboard")
                    elif app_name == "kahamahmis":
                        allowed_views = [
                            "kahamahmis.kahamaEditView",
                            "kahamahmis.kahamaDelete",
                            "django.views.static",
                            "kahamahmis.views",
                            "kahamahmis.kahamaImports",  
                            "kahamahmis.kahamaExcelTemplate",  
                            "kahamahmis.KahamaReportsView",  
                            "kahamahmis.kahamaViews",
                            "kahamahmis.kahamaAdmin",
                        ]
                        if modulename in allowed_views or request.path == reverse("kahama_dashboard"):
                            return None
                        else:
                            return redirect("kahama_dashboard")
                
                elif user.user_type == "2":
                    try:
                        staff = Staffs.objects.get(admin=user)
                        role = staff.role.lower()  # Convert role to lowercase for consistency

                        if app_name == "kahamahmis":
                            if staff.work_place == 'kahama':
                                allowed_views = [
                                    "kahamahmis.kahamaEditView",
                                    "kahamahmis.kahamaDelete",
                                    "django.views.static",
                                    "kahamahmis.views",
                                    "kahamahmis.kahamaImports",  
                                    "kahamahmis.kahamaExcelTemplate",  
                                    "kahamahmis.KahamaReportsView",  
                                    "kahamahmis.kahamaViews",
                                    "kahamahmis.kahamaAdmin",
                                ]
                                if modulename in allowed_views or request.path == reverse("kahama_dashboard"):
                                    return None
                                else:
                                    return redirect("kahama_dashboard")
                            else:
                                return redirect("kahamahmis:kahama")    
                        elif app_name == "clinic":
                            if staff.work_place == 'resa':
                                if role == "receptionist":
                                    allowed_views = [
                                        "clinic.ReceptionistView",
                                        "clinic.delete",
                                         "django.views.static",
                                    ]
                                    dashboard_url = "receptionist_dashboard"
                                elif role == "doctor":
                                    allowed_views = [
                                        "clinic.DoctorView",
                                        "django.views.static",
                                                     ]
                                    dashboard_url = "doctor_dashboard"
                                    
                                elif role == "admin":
                                    allowed_views = [
                                            "clinic.views",
                                            "clinic.AdminViews",
                                            "clinic.HodViews",
                                            "clinic.ExcelTemplate",
                                            "clinic.delete",
                                            "clinic.editView",                         
                                            "clinic.imports",                         
                                            "clinic.FinancialViews",                         
                                            "django.views.static",
                                        ]
                                    dashboard_url = "admin_dashboard"
                                elif role == "nurse":
                                    allowed_views = [
                                        "clinic.NurseView",
                                         "django.views.static",
                                        ]
                                    dashboard_url = "nurse_dashboard"
                                elif role == "physiotherapist":
                                    allowed_views = [
                                        "clinic.PhysiotherapistView",
                                         "django.views.static",
                                        ]
                                    dashboard_url = "physiotherapist_dashboard"
                                elif role == "labtechnician":
                                    allowed_views = [
                                        "clinic.LabTechnicianView",
                                         "django.views.static",
                                        ]
                                    dashboard_url = "labtechnician_dashboard"
                                elif role == "pharmacist":
                                    allowed_views = [
                                        "clinic.PharmacistView",
                                         "django.views.static",
                                        ]
                                    dashboard_url = "pharmacist_dashboard"
                                else:
                                    allowed_views = []  # For unrecognized roles

                                # Allow specific views for each staff role
                                if modulename in allowed_views:
                                    return None
                                elif request.path == reverse(dashboard_url):
                                    # If already on the dashboard, return None to prevent redirection loop
                                    return None
                                else:
                                    # Redirect to corresponding dashboard based on role
                                    return redirect(dashboard_url)
                            else:
                               return redirect("clinic:login")       
                    except Staffs.DoesNotExist:
                        return HttpResponseRedirect(reverse("clinic:home"))
            
        # Allow unauthenticated users to access all views in clinic and kahamahmis apps
        return None
