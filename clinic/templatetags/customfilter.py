from django import template

from clinic.models import WalkInPrescription

register = template.Library()

@register.filter
def divide(value, arg):
    try:
        return round(value / arg, 2)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def filter_visit_type(queryset, visit_type):
    return queryset.filter(visit_type=visit_type)

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

@register.filter
def absolute(value):
    try:
        return abs(int(value))
    except (ValueError, TypeError):
        return value     

@register.filter
def div(value, arg):
    try:
        return float(value) / float(arg) if arg else 0
    except (ValueError, TypeError):
        return 0

@register.filter
def mul(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0        

@register.filter
def multiply(value, arg):
    """Multiplies the value by the argument."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''        

@register.filter
def div(value, arg):
    """Divide value by arg safely."""
    try:
        return float(value) / float(arg) if arg else 0
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def mul(value, arg):
    """Multiply value by arg."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0        

@register.filter
def heatmap_class(count):
    if not count:
        return 0
    if count % 10 == 0:
        return count
    return count        

@register.filter
def get_range(start, end):
    """
    Usage: {{ some_number|get_range:end }}
    Generates range(start, end).
    Example: 3|get_range:6 → [3, 4, 5]
    """
    try:
        return range(int(start), int(end))
    except (ValueError, TypeError):
        return []    

@register.filter
def bmi(weight, height_cm):
    try:
        height_m = height_cm / 100
        return round(weight / (height_m ** 2), 1)
    except (TypeError, ZeroDivisionError):
        return None        

@register.filter
def map_attribute(objects, attr_name):
    """Return a list of attribute values from a queryset or list of objects."""
    return [getattr(obj, attr_name, None) for obj in objects]        

@register.filter
def unique(value_list):
    return list(set(value_list))   

@register.filter
def get_visit_status(visit):
    return WalkInPrescription.get_visit_status(visit)     

@register.filter
def filter_status(queryset, status):
    """Filter appointments by status code."""
    return queryset.filter(status=status)    