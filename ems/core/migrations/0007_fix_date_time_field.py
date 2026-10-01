# Generated manually to fix date_time field issue
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_add_operational_status_to_machineissue'),
    ]

    operations = [
        # Add new last_updated field
        migrations.AddField(
            model_name='machineissue',
            name='last_updated',
            field=models.DateTimeField(auto_now=True),
        ),
        # Change date_time from auto_now to auto_now_add
        migrations.AlterField(
            model_name='machineissue',
            name='date_time',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]



