from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def days_since(expiration_date):
    """Return number of days since the given date."""
    if not expiration_date:
        return 0
    today = timezone.now().date()
    return (today - expiration_date).days
