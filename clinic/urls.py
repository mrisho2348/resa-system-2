from django.urls import include, path
from . import views
from django.contrib.auth import views as auth_views  # Add this import

urlpatterns = [
    path('', views.index, name="home"),   
    path('create/account', views.add_staff, name='add_staff'),      
    path('check_email_exist', views.check_email_exist, name='check_email_exist'),       
    path('check_username_exist', views.check_username_exist, name='check_username_exist'),       
    path('logout_user', views.logout_user, name='logout_user'),
    path('contact/', views.ContactFormView.as_view(), name='contact_form'),
    path('GetUserDetails', views.GetUserDetails, name='GetUserDetails'),       
    path('success/', views.account_creation_success, name='success_page'), 
    path('resa/portfolio/details', views.portfolio_details, name="portfolio_details"),
    path('resa/contact', views.contact, name="contact"),
    path('resa/blog/single', views.blog_single, name="blog_single"),
    path('resa/page/404', views.page_404, name="page_404"),     
    path('check_mct_number_exist/', views.check_mct_number_exist, name='check_mct_number_exist'),   
    path('profile/', views.profile_view, name='profile'),
    path('change_password/', views.change_password_view, name='change_password'),

    # RESA Portal URLs
    path('portal/', views.RESAPortal, name='resa_portal'),
    path('portal/login/', views.RESAPortalLogin, name='resa_portal_login'),
    
    # Forgot Password URLs
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    
    # Fixed password reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset_form.html', email_template_name='password_reset_email.html', subject_template_name='password_reset_subject.txt'    ),  name='password_reset'),
    
    path('password_reset/done/',  auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html' ),  name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/',  views.password_reset_confirm,  name='password_reset_confirm'),
    
    path('reset/done/',  auth_views.PasswordResetCompleteView.as_view( template_name='password_reset_complete.html' ),  name='password_reset_complete'),
]