from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

from clinic.models import Staffs

class LoginCheckMiddleWare(MiddlewareMixin):
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        modulename = view_func.__module__
        user = request.user

        # Allow access to login/logout pages and authentication-related views
        if (request.path == reverse("login") or
            request.path == reverse("admin:index") or
            request.path == reverse("clinic:DoLogin") or
            request.path == reverse("kahamahmis:kahama") or
            request.path == reverse("kahamahmis:DoLoginKahama") or
            request.path == reverse("clinic:home") or
            request.path == reverse("clinic:logout_user") or
            modulename.startswith("django.contrib.auth.views")):
            return None
        
        if user.is_authenticated:
            # Check if the user belongs to the clinic or kahama app
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
                            "clinic.delete",
                            "clinic.editView",                         
                            "clinic.imports",                         
                            "django.views.static",
                            "admin:index", 
                           
                        ]
                    elif app_name == "kahamahmis":  # For kahama app
                        allowed_views = [
                            "kahamahmis.editView",
                            "kahamahmis.delete",
                            "django.views.static",
                            "kahamahmis.views",
                            "kahamahmis.kahamaImports",  
                            "kahamahmis.KahamaReportsView",  
                            "kahamahmis.kahamaViews",
                        ]
                    else:
                        return HttpResponseRedirect(reverse("home"))       
                    if modulename in allowed_views or request.path == reverse(f"{app_name}:dashboard"):
                        return None
                    else:
                        return redirect(f"{app_name}:dashboard")
                
                elif user.user_type == "2":
                    if app_name == "kahamahmis":
                        # Allow user type 2 within the kahama app to access its views
                        allowed_views = [
                            "kahamahmis.editView",
                            "kahamahmis.delete",
                            "django.views.static",
                            "kahamahmis.views",
                            "kahamahmis.KahamaReportsView",  
                            "kahamahmis.kahamaImports",  
                            "kahamahmis.kahamaViews",
                        ]
                        if modulename in allowed_views:
                            return None
                        else:
                            return HttpResponseRedirect(reverse("kahamahmis:dashboard"))
                    elif app_name == "clinic":
                        staff = Staffs.objects.filter(admin=user).first()
                        if staff:
                            role = staff.role.lower()
                            # Define allowed views and corresponding dashboard for each role
                            if role == "receptionist":
                                allowed_views = [
                                    "clinic.ReceptionistView",
                                    "clinic.delete",
                                                 ]
                                dashboard_url = "receptionist_dashboard"
                            elif role == "doctor":
                                allowed_views = ["clinic.DoctorView"]
                                dashboard_url = "doctor_dashboard"
                            elif role == "nurse":
                                allowed_views = ["clinic.NurseView"]
                                dashboard_url = "nurse_dashboard"
                            elif role == "physiotherapist":
                                allowed_views = ["clinic.PhysiotherapistView"]
                                dashboard_url = "physiotherapist_dashboard"
                            elif role == "labtechnician":
                                allowed_views = ["clinic.LabTechnicianView"]
                                dashboard_url = "labtechnician_dashboard"
                            elif role == "pharmacist":
                                allowed_views = ["clinic.PharmacistView"]
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
                        return HttpResponseRedirect(reverse("clinic:home"))        
            
        # Redirect to the landing page if the user is not authenticated
        return HttpResponseRedirect(reverse("clinic:home"))
