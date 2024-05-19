from django.shortcuts import render
from django.contrib.auth import logout,login
from django.http import HttpResponse,HttpResponseRedirect
from django.template import loader
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic.edit import FormView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import send_mail
from clinic.emailBackEnd import EmailBackend
from clinic.models import ContactDetails

# Create your views here.
def index(request):
    return render(request,"Centric_template/admin_template/home_content.html")

def sales_dashboard(request):
    return render(request,"Centric_template/admin_template/sales_dashboard.html")

def analytics_dashboard(request):
    return render(request,"Centric_template/admin_template/alaytics_dashboard.html")

def ShowLoginCentric(request):  
  return render(request,'Centric_template/login.html')



def DoLoginCentric(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not allowed</h2>")
    else:
        user = EmailBackend.authenticate(request, request.POST.get("email"), request.POST.get("password"))
        if user is not None:
            if not user.is_active:
                messages.error(request, "Your account is not active. Please contact the administrator for support.")
                return HttpResponseRedirect(reverse("ShowLoginCentric"))

            login(request, user)
            if user.user_type == "1":
                return HttpResponseRedirect(reverse("centric_home"))
            elif user.user_type == "2":
                return HttpResponseRedirect(reverse("centric_home"))             
            else:
                return HttpResponseRedirect(reverse("ShowLoginCentric"))
        else:
            messages.error(request, "Invalid Login Details")
            return HttpResponseRedirect(reverse("ShowLoginCentric"))