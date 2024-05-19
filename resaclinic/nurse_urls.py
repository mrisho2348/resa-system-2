
from django.urls import include, path

from clinic import NurseView



urlpatterns = [
           # NurseView
        path('nurse_dashboard/', NurseView.nurse_dashboard, name='nurse_dashboard'),
        
]
