from django.shortcuts import render
from django.db.models import Sum
from django.db.models.functions import TruncMonth, ExtractYear
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from clinic.models import AmbulanceOrder, AmbulanceVehicleOrder, ConsultationOrder, EquipmentMaintenance, ImagingRecord, LaboratoryOrder, Medicine, Prescription, Procedure, Reagent, SalaryPayment

@require_GET
def get_financial_data(request):
    year = request.GET.get('year', None)
    if not year:
        return JsonResponse({'error': 'Year parameter is required.'}, status=400)

    # Fetch income and expenditure data for the specified year
    income = calculate_yearly_income(year)
    expenditure = calculate_yearly_expenditures(year)

    # Prepare data to send back to the client
    data = {
        'income': income,
        'expenditure': expenditure,
    }

    return JsonResponse(data)

def calculate_yearly_income(year):
    income_models = [
        ImagingRecord,
        ConsultationOrder,
        Procedure,
        LaboratoryOrder,
        AmbulanceOrder,
        AmbulanceVehicleOrder,
        Prescription,
    ]
    total_income = 0

    for model in income_models:
        if model == Prescription:
            total_income += model.objects.filter(created_at__year=year).aggregate(total=Sum('total_price'))['total'] or 0
        else:
            total_income += model.objects.filter(order_date__year=year).aggregate(total=Sum('cost'))['total'] or 0

    return total_income

def calculate_yearly_expenditures(year):
    expenditure_models = {
        'Medicine': ('total_buying_price', Medicine),
        'EquipmentMaintenance': ('cost', EquipmentMaintenance),
        'Reagent': ('price_per_unit', 'quantity_in_stock', Reagent),
        'SalaryPayment': ('payroll__total_salary', SalaryPayment),
    }
    total_expenditure = 0

    for model_name, fields in expenditure_models.items():
        if model_name == 'Reagent':
            price_field, quantity_field, model = fields
            expenditure = model.objects.filter(created_at__year=year).annotate(
                total_price=ExpressionWrapper(F(price_field) * F(quantity_field), output_field=DecimalField())
            ).aggregate(total=Sum('total_price'))['total'] or 0
        elif model_name == 'SalaryPayment':
            cost_field, model = fields
            expenditure = model.objects.filter(payroll__payroll_date__year=year).aggregate(total=Sum(cost_field))['total'] or 0
        else:
            cost_field, model = fields
            expenditure = model.objects.aggregate(total=Sum(cost_field))['total'] or 0
        
        total_expenditure += expenditure

    return total_expenditure





def calculate_monthly_income(year):
    income_models = {
        'ImagingRecord': ImagingRecord,
        'ConsultationOrder': ConsultationOrder,
        'Procedure': Procedure,
        'LaboratoryOrder': LaboratoryOrder,
        'AmbulanceOrder': AmbulanceOrder,
        'AmbulanceVehicleOrder': AmbulanceVehicleOrder,
        'Prescription': Prescription,
    }
    monthly_income = {}

    for model_name, model in income_models.items():
        date_field = 'order_date' if model_name != 'Prescription' else 'created_at'
        price_field = 'cost' if model_name != 'Prescription' else 'total_price'

        income = model.objects.filter(**{f'{date_field}__year': year}).annotate(month=TruncMonth(date_field)).values('month').annotate(total=Sum(price_field)).order_by('month')
        
        for entry in income:
            month = entry['month'].strftime('%B')
            if month not in monthly_income:
                monthly_income[month] = 0
            monthly_income[month] += entry['total']

    return monthly_income


def calculate_yearly_expenditure():
    expenditure_models = {
        'Medicine': ('total_buying_price', Medicine),
        'EquipmentMaintenance': ('cost', EquipmentMaintenance),
        'Reagent': ('price_per_unit', 'quantity_in_stock', Reagent),
        'SalaryPayment': ('payroll__total_salary', SalaryPayment),
    }
    yearly_expenditure = {}

    for model_name, fields in expenditure_models.items():
        if model_name == 'Reagent':
            price_field, quantity_field, model = fields
            expenditure = model.objects.annotate(
                total_price=ExpressionWrapper(F(price_field) * F(quantity_field), output_field=DecimalField())
            ).annotate(year=ExtractYear('created_at')).values('year').annotate(total=Sum('total_price')).order_by('year')
        else:
            cost_field, model = fields
            expenditure = model.objects.annotate(year=ExtractYear('created_at')).values('year').annotate(total=Sum(cost_field)).order_by('year')
        
        for entry in expenditure:
            year = entry['year']
            if year not in yearly_expenditure:
                yearly_expenditure[year] = 0
            yearly_expenditure[year] += entry['total']

    return yearly_expenditure

def highest_income_entity(year):
    income_models = {
        'ImagingRecord': ImagingRecord,
        'ConsultationOrder': ConsultationOrder,
        'Procedure': Procedure,
        'LaboratoryOrder': LaboratoryOrder,
        'AmbulanceOrder': AmbulanceOrder,
        'AmbulanceVehicleOrder': AmbulanceVehicleOrder,
        'Prescription': Prescription,
    }
    highest_entity = None
    highest_amount = 0

    for model_name, model in income_models.items():
        date_field = 'order_date' if model_name != 'Prescription' else 'created_at'
        price_field = 'cost' if model_name != 'Prescription' else 'total_price'

        total_income = model.objects.filter(**{f'{date_field}__year': year}).aggregate(total=Sum(price_field))['total'] or 0
        if total_income > highest_amount:
            highest_amount = total_income
            highest_entity = model_name

    return highest_entity, highest_amount

def financial_analysis_view(request):
    year = datetime.now().year
    monthly_income = calculate_monthly_income(year)    
    yearly_expenditure = calculate_yearly_expenditure()
    highest_entity, highest_amount = highest_income_entity(year)
    
    context = {
        'year': year,
        'monthly_income': monthly_income,
        'yearly_expenditure': yearly_expenditure,
        'highest_income_entity': highest_entity,
        'highest_income_amount': highest_amount,
    }
    return render(request, 'hod_template/financial_analysis.html', context)
