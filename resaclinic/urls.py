from django.conf.urls.static import static
from django.urls import include, path
from resaclinic import settings

urlpatterns = [
    # -------------------------
    # Main Clinic URLs
    # -------------------------
    path('', include(('clinic.urls', 'clinic'), namespace='clinic')),   # Default homepage
    path('login/', include('clinic.urls')),                             # Login via clinic

    # -------------------------
    # Receptionist URLs
    # -------------------------
    path('receptionist/', include('resaclinic.receptionist_urls')),

    # -------------------------
    # Pharmacist URLs
    # -------------------------
    path('pharmacy/', include('resaclinic.pharmacist_urls')),

    # -------------------------
    # CKEditor URLs
    # -------------------------
    path("ckeditor5/", include('django_ckeditor_5.urls')),

    # -------------------------
    # Lab Technician URLs
    # -------------------------
    path('lab/', include('resaclinic.labtechnician_urls')),

    # -------------------------
    # Head of Department URLs
    # -------------------------
    path('hod/', include('resaclinic.hod_urls')),

    # -------------------------
    # Admin Panel URLs (Clinic & Financial)
    # -------------------------
    path('resa/', include('resaclinic.admin_urls')),
    path('admin-panel/', include('resaclinic.financial_urls')),

    # -------------------------
    # Doctor URLs (Clinic)
    # -------------------------
    path('doctor/', include('resaclinic.doctor_urls')),

    # -------------------------
    # Kahama HMIS URLs
    # -------------------------
    # Kahama Doctor


    # Kahama Admin
    path('kahama', include('kahamahmis.urls')),
    path('pemba', include('pembahmis.urls')),

    # Kahama Report
    path('kahama/report/', include('resaclinic.kahamareport_urls')),

    # -------------------------
    # Pemba HMIS URLs
    # -------------------------
 
]

# Static and media paths for development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
