import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0031_spares_free_text_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='issueescalation',
            name='reassigned_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='escalations_assigned', to='core.employee'),
        ),
        migrations.AddField(
            model_name='issueescalation',
            name='reassigned_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='escalations_reassigned', to='core.employee'),
        ),
        migrations.AddField(
            model_name='issueescalation',
            name='reassign_remarks',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='issueescalation',
            name='reassigned_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
