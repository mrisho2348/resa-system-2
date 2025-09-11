from django.urls import include, path

urlpatterns = [
      path('/admin/', include('kahamahmis.admin.kahama_admin_urls')),
      path('/doctor/', include('kahamahmis.doctor.kahama_doctor_urls')),
]
