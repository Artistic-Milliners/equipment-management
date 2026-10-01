from core.models import Equipment
from django.conf import settings


def side_bar(request):
    eq_map = {}
    equipments = Equipment.objects.all()
    for e in equipments:
        eq_map[e] = e.typeOfMachine.all()
    return {
        'equipments':eq_map
    }
    
def base_api_url(request):
    return {
        'API_BASE_URL': settings.API_BASE_URL,
        'API_PORT': settings.API_PORT
    }