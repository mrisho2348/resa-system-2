
from django.shortcuts import render

from django.template import loader
from django.shortcuts import render

from clinic.models import Patients, Staffs


# Create your views here.
def index(request):
    return render(request,"index.html")

def nurse_dashboard(request):
    total_patients = Patients.objects.count()
    recently_added_patients = Patients.objects.order_by('-created_at')[:6]
    doctors = Staffs.objects.filter(role='doctor')
    context = {
        'total_patients': total_patients,
        'recently_added_patients': recently_added_patients,
        'doctors': doctors,
        # 'gender_based_monthly_counts': gender_based_monthly_counts,
    }
    return render(request,"receptionist_template/home_content.html",context)