# bookstore/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def dict_get(d, key):
    if isinstance(d, dict):
        return d.get(str(key)) or d.get(int(key))
    return None  # dict가 아니면 그냥 None 반환
@register.filter
def mul(value, arg):
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return ''

@register.filter
def calc_order_total(items):
    return sum(item.book.price * item.quantity for item in items)