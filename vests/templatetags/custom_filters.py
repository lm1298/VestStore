from django import template
register = template.Library()


@register.filter
def calculate_subtotal(quantity, price):
    subtotal = quantity * price
    return round(subtotal, 2)