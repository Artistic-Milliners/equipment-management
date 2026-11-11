from django.db import migrations, models

OLD_LABELS = {
    'electrical': 'Electrical',
    'mechanical': 'Mechanical',
    'hydraulic': 'Hydraulic',
    'pneumatic': 'Pneumatic',
    'safety': 'Safety',
    'general': 'General',
}


def use_labels(apps, schema_editor):
    # Store the readable label instead of the old choice key, so imported categories look the same
    Spares = apps.get_model('core', 'Spares')
    for key, label in OLD_LABELS.items():
        Spares.objects.filter(category=key).update(category=label)


def use_keys(apps, schema_editor):
    Spares = apps.get_model('core', 'Spares')
    for key, label in OLD_LABELS.items():
        Spares.objects.filter(category=label).update(category=key)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_issue_escalation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spares',
            name='category',
            field=models.CharField(default='General', help_text='Major category, e.g. Electrical, Mechanical (free text, as in the stock sheet)', max_length=100),
        ),
        migrations.RunPython(use_labels, use_keys),
    ]
