
from django.urls import include, path
from kahamahmis import divineReport


urlpatterns = [             
      path('generate-year-month-report/', divineReport.generate_year_month_report, name='divine_generate_year_month_report'),
  ]       

