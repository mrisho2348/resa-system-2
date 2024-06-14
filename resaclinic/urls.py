
"""
URL configuration for the resaclinic project.

The `urlpatterns` list routes URLs to views. For more information, please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import include, path
from resaclinic import settings
from django.views.i18n import set_language
from clinic.views import logout_user, DoLogin

# Override the default admin logout view
admin.site.logout = logout_user

urlpatterns = [
    path('admin/login/', DoLogin, name='custom_login'),
    path('admin/', admin.site.urls, name='hmis_admin'),
    path('', include(('clinic.urls', 'clinic'), namespace='clinic')),
    path('resa/', include('centric.urls')),
    path('reception/', include('resaclinic.receptionist_urls')),
    path('pharmacy/', include('resaclinic.pharmacist_urls')),
    path('lab/', include('resaclinic.labtechnician_urls')),
    path('hod/', include('resaclinic.hod_urls')),
    path('admin-panel/', include('resaclinic.admin_urls')),
    path('admin-imports/', include('resaclinic.imports_urls')),
    path('admin-delete/', include('resaclinic.admin_delete_urls')),
    path('admin-edit/', include('resaclinic.admin_edit_urls')),
    path('doctor/', include('resaclinic.doctor_urls')),
    path('nurse/', include('resaclinic.nurse_urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('ckeditor5/', include('django_ckeditor_5.urls'), name='ck_editor_5_upload_file'),
    path('kahama/', include(('kahamahmis.urls', 'kahamahmis'), namespace='kahamahmis')),
    path('i18n/', set_language, name='set_language'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_URL)

# Customize admin site appearance
admin.site.login = 'custom_login'
admin.site.index_title = "Resa Clinic"
admin.site.site_header = "Resa Clinic"
admin.site.site_title = "Resa Clinic"