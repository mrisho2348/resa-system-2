from django.urls import include, path

urlpatterns = [
      path('/admin/', include('pembahmis.admin.pemba_admin_urls')),
      path('/doctor/', include('pembahmis.doctor.pemba_doctor_urls')),
]
