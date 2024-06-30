from django.urls import path
from . import views

urlpatterns = [
    # Authentication paths
    path('kahama_login/', views.ShowLoginKahama, name='kahama'),
    path('logout_user/', views.logout_user, name='logout_user'),
    path('DoLoginKahama/', views.DoLoginKahama, name='DoLoginKahama'),

    # User details path
    path('GetUserDetails/', views.GetUserDetails, name='GetUserDetails'),

    # Contact form path
    path('contact/', views.ContactFormView.as_view(), name='contact_form'),

    # Additional paths under 'resa'
    path('resa/portfolio/details/', views.portfolio_details, name="portfolio_details"),
    path('resa/contact/', views.contact, name="contact"),
    path('resa/blog/single/', views.blog_single, name="blog_single"),
    path('resa/page/404/', views.page_404, name="page_404"),
]
