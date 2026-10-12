from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_copy_manufacturer_data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='equipment',
            name='manufacturer',
        ),
    ]
