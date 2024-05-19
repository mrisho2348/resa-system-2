
from django.urls import  path
from . import views

urlpatterns = [   
    path('resa/centric', views.index, name="centric_home"),
    path('resa/centric/login_page', views.ShowLoginCentric, name="ShowLoginCentric"),
    path('resa/centric/login', views.DoLoginCentric, name="DoLoginCentric"),
    path('dashboard/sales', views.sales_dashboard, name="sales_dashboard"),
    path('dashboard/analytics', views.analytics_dashboard, name="analytics_dashboard"),
]
