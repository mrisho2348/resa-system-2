
from django.urls import  path

from clinic import FinancialViews



urlpatterns = [
           # NurseView
        path('financial-analysis/', FinancialViews.financial_analysis_view, name='admin_financial_analysis'),  
        path('admin/financial-data/', FinancialViews.get_financial_data, name="admin_get_financial_data"),     
]
