from django.db import migrations


def copy_forward(apps, schema_editor):
    Equipment = apps.get_model('core', 'Equipment')
    Machines = apps.get_model('core', 'Machines')

    # Each equipment keeps its existing manufacturer in the new list
    for equipment in Equipment.objects.all():
        if equipment.manufacturer_id:
            equipment.manufacturers.add(equipment.manufacturer_id)

    # Existing machines default to their equipment's manufacturer; fix exceptions in admin
    for machine in Machines.objects.select_related('type_of_machine'):
        machine.manufacturer_id = machine.type_of_machine.manufacturer_id
        machine.save(update_fields=['manufacturer'])


def copy_backward(apps, schema_editor):
    Equipment = apps.get_model('core', 'Equipment')

    for equipment in Equipment.objects.all():
        first = equipment.manufacturers.order_by('pk').first()
        if first:
            equipment.manufacturer_id = first.pk
            equipment.save(update_fields=['manufacturer'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_equipment_manufacturers_machine_manufacturer'),
    ]

    operations = [
        migrations.RunPython(copy_forward, copy_backward),
    ]
