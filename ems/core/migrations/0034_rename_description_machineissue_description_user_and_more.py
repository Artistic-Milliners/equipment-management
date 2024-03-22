# Generated by Django 5.0.1 on 2024-03-16 12:39

import django.db.models.deletion
import django.db.models.query
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0033_alter_employee_department_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='machineissue',
            old_name='description',
            new_name='description_user',
        ),
        migrations.AddField(
            model_name='machineissue',
            name='description_reviewer',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='employee',
            name='department',
            field=models.ForeignKey(default=django.db.models.query.QuerySet.first, on_delete=django.db.models.deletion.CASCADE, to='core.department'),
        ),
    ]