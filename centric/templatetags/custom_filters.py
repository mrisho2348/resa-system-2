from django import template
from datetime import datetime
register = template.Library()

@register.filter(name='strftime')
def strftime(date, format_string):
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d')  # Convert the string to a datetime object
    return date.strftime(format_string)
