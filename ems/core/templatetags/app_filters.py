from django import template
# from maintenance.views import get_status
register = template.Library()

@register.filter
def dateFormat(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S")

# @register.filter
# def status_url(status):
#     return get_status(status)
