from django import template

register = template.Library()

@register.filter
def dateFormat(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S")
