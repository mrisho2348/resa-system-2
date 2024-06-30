
from django.urls import include, path
from kahamahmis import KahamaReportsView


urlpatterns = [  
        path('generate_comprehensive_report/', KahamaReportsView.generate_comprehensive_report, name='kahama_generate_comprehensive_report'),
  ]       

