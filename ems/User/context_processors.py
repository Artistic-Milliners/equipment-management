from core.models import Equipment

def side_bar(request):
    eq_map = {}
    equipments = Equipment.objects.all()
    for e in equipments:
        eq_map[e] = e.typeOfMachine.all()
    return {
        'equipments':eq_map
    }
    