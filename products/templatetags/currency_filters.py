# products/templatetags/currency_filters.py
from django import template

register = template.Library()


@register.filter
def kes(value):
    """Converts USD to KES at a rate of 130 and formats as KES currency."""
    try:
        kes_value = float(value) * 130
        return f'KES {kes_value:,.2f}'
    except (ValueError, TypeError):
        return 'KES 0.00'