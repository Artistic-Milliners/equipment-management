"""
Custom template tags for user-related checks
"""
from django import template

register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    """
    Check if user belongs to a specific group
    Usage in template: {% if user|has_group:"Inventory Controller" %}
    """
    if not user.is_authenticated:
        return False
    return user.groups.filter(name=group_name).exists()


@register.filter(name='get_item')
def get_item(mapping, key):
    """
    Look up a key that isn't a valid template variable name (e.g. a form field like "machine-hours")
    Usage in template: {{ posted|get_item:"machine-hours" }}
    Returns '' when the mapping is empty/None or the key is missing.
    """
    if not mapping:
        return ''
    return mapping.get(key, '')


@register.filter(name='is_inventory_controller')
def is_inventory_controller(user):
    """
    Check if user is in Inventory Controller group
    Usage in template: {% if user|is_inventory_controller %}
    """
    if not user.is_authenticated:
        return False
    return user.groups.filter(name='Inventory Controller').exists()

