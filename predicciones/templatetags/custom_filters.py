# predicciones/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def pluck(list_of_dicts, key):
    """Extrae una lista de valores desde una lista de diccionarios."""
    try:
        return [d.get(key) for d in list_of_dicts]
    except Exception:
        return []
