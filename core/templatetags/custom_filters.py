from django import template

register = template.Library()

@register.filter
def divide(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0
    
@register.filter
def tax_amount(sub_total, tax_rate):
    try:
        sub_total = float(sub_total)
        tax_rate = float(tax_rate)
        return (sub_total * tax_rate) / 100
    except (ValueError, TypeError):
        return 0