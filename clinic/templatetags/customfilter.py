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

@register.filter
def total_cost_of_procedure(procedures):
    return sum(procedure.cost for procedure in procedures)

@register.filter
def total_cost_of_lab(lab_tests):
    return sum(lab_test.cost for lab_test in lab_tests)

@register.filter
def total_cost_of_image(imaging_records):
    return sum(imaging_record.cost for imaging_record in imaging_records)


@register.filter(name='attr')
def attr(value, arg):
    """
    Adds an attribute to the field.
    Usage: {{ form.field_name|attr:"class=some-class" }}
    """
    try:
        key, val = arg.split('=')
        value.attrs[key] = val
    except ValueError:
        pass
    return value

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)    