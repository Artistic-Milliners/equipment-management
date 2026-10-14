from django.db import migrations


def wipe_complaints(apps, schema_editor):
    # All complaints so far are test data; clear them before IssueList is replaced by FaultLibrary.
    # Order matters: closings and reviews block deletion of the records they point to.
    for model_name in ['IssueClosing', 'MachineIssueReview', 'MachineIssue', 'TemporaryIssue', 'IssueList']:
        apps.get_model('core', model_name).objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_remove_equipment_manufacturer'),
    ]

    operations = [
        # Irreversible in practice: the deleted test data is only recoverable from a backup
        migrations.RunPython(wipe_complaints, migrations.RunPython.noop),
    ]
