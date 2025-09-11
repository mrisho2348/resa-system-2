
from django.urls import include, path

from kahamahmis import kahamaReports



urlpatterns = [  
         path('generate-year-month-report/', kahamaReports.generate_year_month_report, name='kahama_generate_year_month_report'),
  ]       

