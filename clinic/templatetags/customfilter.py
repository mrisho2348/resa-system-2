from django import template

register = template.Library()

@register.filter
def divide(value, arg):
    try:
        return round(value / arg, 2)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def replace_blank(value, string_val=""):
    value = str(value).replace(string_val, '')
    return value

@register.filter
def encrypt_data(value):
    from cryptography.fernet import Fernet
    from django.conf import settings
    
    fernet = Fernet(settings.ID_ENCRYPTION_KEY)
    value = fernet.encrypt(str(value).encode())
    return value

@register.filter
def total_cost(orders):
    return sum(order.cost for order in orders)

@register.filter
def total_cost_of_prescription(prescriptions):
    return sum(prescription.total_price for prescription in prescriptions)