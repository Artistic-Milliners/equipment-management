from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_machines_view_all_permission'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipment',
            name='manufacturers',
            field=models.ManyToManyField(blank=True, related_name='equipments', to='core.manufacturer'),
        ),
        migrations.AddField(
            model_name='machines',
            name='manufacturer',
            field=models.ForeignKey(blank=True, help_text='Must be one of the manufacturers of the selected equipment',
                                    null=True, on_delete=django.db.models.deletion.PROTECT,
                                    related_name='machines', to='core.manufacturer'),
        ),
    ]
