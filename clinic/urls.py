
from django.urls import include, path
from . import views

urlpatterns = [
        path('',views.index, name="home"),   
        path('create/account', views.add_staff, name='add_staff'),      
        path('check_email_exist', views.check_email_exist, name='check_email_exist'),       
        path('check_username_exist', views.check_username_exist, name='check_username_exist'),       
        path('login', views.ShowLogin, name='login'),       
        path('logout_user', views.logout_user, name='logout_user'),  # Move this line here
        path('contact/', views.ContactFormView.as_view(), name='contact_form'),
        path('GetUserDetails', views.GetUserDetails, name='GetUserDetails'),       
        path('success/', views.account_creation_success, name='success_page'),
        path('dologin', views.DoLogin, name='DoLogin'),   
        path('accounts/', include('django.contrib.auth.urls')),  
        path('resa/portfolio/details',views.portfolio_details, name="portfolio_details"),
        path('resa/contact',views.contact, name="contact"),
        path('resa/blog/single',views.blog_single, name="blog_single"),
        path('resa/page/404',views.page_404, name="page_404"),     
        path('check_mct_number_exist/', views.check_mct_number_exist, name='check_mct_number_exist'),   
        path('profile/', views.profile_view, name='profile'),  # Profile view URL
        path('change_password/', views.change_password_view, name='change_password'),  # Change password view URL

        
]
