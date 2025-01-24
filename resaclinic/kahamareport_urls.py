
from django.urls import include, path
from kahamahmis import KahamaReportsView


urlpatterns = [  
         path('generate-year-month-report/', KahamaReportsView.generate_year_month_report, name='kahama_generate_year_month_report'),
  ]       

