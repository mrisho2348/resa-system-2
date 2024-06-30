from django.conf.urls.static import static
from django.urls import include, path
from resaclinic import settings

urlpatterns = [
    # Main clinic paths
    path('', include(('clinic.urls', 'clinic'), namespace='clinic')),
    
    # Centric app paths
    path('resa/', include('centric.urls')),
    
    # Receptionist paths
    path('reception/', include('resaclinic.receptionist_urls')),
    
    # Pharmacist paths
    path('pharmacy/', include('resaclinic.pharmacist_urls')),
    path("ckeditor5/", include('django_ckeditor_5.urls')),
    # Lab technician paths
    path('lab/', include('resaclinic.labtechnician_urls')),
    
    # Head of department paths
    path('hod/', include('resaclinic.hod_urls')),
    
    # Admin panel paths
    path('admin-panel/', include('resaclinic.admin_urls')),
    path('admin-imports/', include('resaclinic.imports_urls')),
    path('admin-delete/', include('resaclinic.admin_delete_urls')),
    path('admin-edit/', include('resaclinic.admin_edit_urls')),
    
    # Doctor paths
    path('doctor/', include('resaclinic.doctor_urls')),
    
    # Nurse paths
    path('nurse/', include('resaclinic.nurse_urls')),
    
    # Kahama paths
    path('kahama/admin/', include('resaclinic.kahamaadmin_urls')),
    path('kahama/delete/', include('resaclinic.kahamadelete_urls')),
    path('kahama/edit/', include('resaclinic.kahamaedit_urls')),
    path('kahama/report/', include('resaclinic.kahamareport_urls')),
    path('kahama/view/', include('resaclinic.kahamaview_urls')),
    path('kahama/imports/', include('resaclinic.kahamaimports_urls')),
    path('kahama/excel/', include('resaclinic.kahamaexcel_urls')),
    path('kahama/hmis/', include(('kahamahmis.urls', 'kahamahmis'), namespace='kahamahmis')),

    # Authentication paths
    path('accounts/', include('django.contrib.auth.urls')),
]

# Static and media paths for development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
