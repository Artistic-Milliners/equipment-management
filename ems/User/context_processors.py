from django.conf import settings
from core.access import visible_machines


def side_bar(request):
    # Group the machines this user may see under their equipment type
    eq_map = {}
    machines = visible_machines(request.user).select_related('type_of_machine').order_by('type_of_machine__name', 'name')
    for machine in machines:
        eq_map.setdefault(machine.type_of_machine, []).append(machine)
    return {
        'equipments':eq_map
    }

def base_api_url(request):
    return {
        'API_BASE_URL': settings.API_BASE_URL,
        'API_PORT': settings.API_PORT
    }
