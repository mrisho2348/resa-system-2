from django import template
from datetime import date

register = template.Library()

@register.filter
def calculate_age(birthdate):
    """Return age in years from a given date of birth."""
    if not birthdate:
        return ""
    today = date.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age
