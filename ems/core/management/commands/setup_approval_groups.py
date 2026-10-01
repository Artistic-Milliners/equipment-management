from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from core.models import MachineIssue, MachineIssueReview, MachineIssueApproval

class Command(BaseCommand):
    help = 'Sets up groups for Engineers (review/close) and Approvers (approve/reject)'

    def handle(self, *args, **options):
        # Get or create the 'Engineers' group
        engineers_group, created = Group.objects.get_or_create(name='Engineers')
        if created:
            self.stdout.write(self.style.SUCCESS('Successfully created Engineers group'))
        else:
            self.stdout.write(self.style.WARNING('Engineers group already exists'))

        # Get or create the 'Approvers' group (Management/HOD)
        approvers_group, created = Group.objects.get_or_create(name='Approvers')
        if created:
            self.stdout.write(self.style.SUCCESS('Successfully created Approvers group'))
        else:
            self.stdout.write(self.style.WARNING('Approvers group already exists'))

        # Get content types
        machine_issue_ct = ContentType.objects.get_for_model(MachineIssue)
        machine_issue_review_ct = ContentType.objects.get_for_model(MachineIssueReview)
        machine_issue_approval_ct = ContentType.objects.get_for_model(MachineIssueApproval)

        # Create or get permissions for Engineers (review and close)
        review_permission, _ = Permission.objects.get_or_create(
            codename='can_review_complaint',
            name='Can review complaints',
            content_type=machine_issue_review_ct,
        )
        
        close_permission, _ = Permission.objects.get_or_create(
            codename='can_close_complaint',
            name='Can close complaints',
            content_type=machine_issue_ct,
        )
        
        view_complaint_permission, _ = Permission.objects.get_or_create(
            codename='can_view_complaint',
            name='Can view complaints',
            content_type=machine_issue_ct,
        )

        # Create or get permissions for Approvers
        approve_permission, _ = Permission.objects.get_or_create(
            codename='can_approve_complaint',
            name='Can approve or reject complaints',
            content_type=machine_issue_approval_ct,
        )

        # Assign permissions to Engineers group
        engineers_group.permissions.clear()
        engineers_group.permissions.add(
            review_permission,
            close_permission,
            view_complaint_permission
        )
        self.stdout.write(self.style.SUCCESS('Assigned permissions to Engineers group'))

        # Assign permissions to Approvers group
        approvers_group.permissions.clear()
        approvers_group.permissions.add(
            approve_permission,
            view_complaint_permission
        )
        self.stdout.write(self.style.SUCCESS('Assigned permissions to Approvers group'))

        self.stdout.write(self.style.SUCCESS('\nSetup complete!'))
        self.stdout.write(self.style.SUCCESS('Engineers can: Review and Close complaints'))
        self.stdout.write(self.style.SUCCESS('Approvers can: Approve or Reject complaints'))


