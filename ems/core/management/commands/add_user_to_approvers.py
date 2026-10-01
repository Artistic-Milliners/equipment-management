from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from core.models import CustomUser

class Command(BaseCommand):
    help = 'Add a specific user to the Approvers group'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to add to Approvers group')

    def handle(self, *args, **options):
        username = options['username']
        
        try:
            # Get the user
            user = CustomUser.objects.get(username=username)
            
            # Get or create the Approvers group
            approvers_group, created = Group.objects.get_or_create(name='Approvers')
            
            # Add user to the group
            user.groups.add(approvers_group)
            
            self.stdout.write(self.style.SUCCESS(f'Successfully added {username} to Approvers group'))
            self.stdout.write(self.style.SUCCESS(f'User groups: {", ".join([g.name for g in user.groups.all()])}'))
            
        except CustomUser.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User "{username}" not found'))
            self.stdout.write(self.style.WARNING('Available users:'))
            for user in CustomUser.objects.all():
                self.stdout.write(f'  - {user.username}')


