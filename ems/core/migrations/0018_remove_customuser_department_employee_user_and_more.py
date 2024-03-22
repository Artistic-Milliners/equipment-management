# Generated by Django 5.0.1 on 2024-02-06 11:36

import core.models
import django.db.models.deletion
import django.db.models.query
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_alter_machineissue_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='department',
        ),
        migrations.AddField(
            model_name='employee',
            name='user',
            field=models.OneToOneField(default=core.models.get_user, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='employee',
            name='department',
            field=models.ForeignKey(default=django.db.models.query.QuerySet.first, on_delete=django.db.models.deletion.CASCADE, to='core.department'),
        ),
        migrations.AlterField(
            model_name='machineissue',
            name='type',
            field=models.CharField(choices=[('CORRECTIVE', 'Corrective'), ('PREVENTIVE', 'Preventive'), ('BREAKDOWN', 'Breakdown'), ('CALIBRATION', 'Calibration')], default='Preventive', max_length=20),
        ),
    ]
