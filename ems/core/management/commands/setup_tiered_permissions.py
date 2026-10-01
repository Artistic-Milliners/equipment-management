from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from core.models import Spares, Machines, Unit, Employee, Equipment, Department

class Command(BaseCommand):
    help = 'Set up tiered permission system: All users, Engineering team, and Management'

    def handle(self, *args, **options):
        # Define permissions for each tier
        engineering_permissions = [
            ('core.view_spares', 'Can view inventory items'),
            ('core.add_spares', 'Can add inventory items'),
            ('core.change_spares', 'Can change inventory items'),
            ('core.delete_spares', 'Can delete inventory items'),
        ]
        
        management_permissions = [
            ('core.view_machines', 'Can view machines'),
            ('core.add_machines', 'Can add machines'),
            ('core.change_machines', 'Can change machines'),
            ('core.delete_machines', 'Can delete machines'),
            ('core.view_unit', 'Can view units'),
            ('core.add_unit', 'Can add units'),
            ('core.change_unit', 'Can change units'),
            ('core.delete_unit', 'Can delete units'),
            ('core.view_employee', 'Can view employees'),
            ('core.add_employee', 'Can add employees'),
            ('core.change_employee', 'Can change employees'),
            ('core.delete_employee', 'Can delete employees'),
        ]
        
        # Create Engineering group
        engineering_group, created = Group.objects.get_or_create(name='Engineering')
        if created:
            self.stdout.write('✓ Created Engineering group')
        else:
            self.stdout.write('- Engineering group already exists')
        
        # Add engineering permissions
        for codename, name in engineering_permissions:
            try:
                permission = Permission.objects.get(codename=codename)
                engineering_group.permissions.add(permission)
                self.stdout.write(f'  ✓ Added {name} to Engineering group')
            except Permission.DoesNotExist:
                self.stdout.write(f'  ✗ Permission {codename} not found')
        
        # Create Management group
        management_group, created = Group.objects.get_or_create(name='Management')
        if created:
            self.stdout.write('✓ Created Management group')
        else:
            self.stdout.write('- Management group already exists')
        
        # Add management permissions
        for codename, name in management_permissions:
            try:
                permission = Permission.objects.get(codename=codename)
                management_group.permissions.add(permission)
                self.stdout.write(f'  ✓ Added {name} to Management group')
            except Permission.DoesNotExist:
                self.stdout.write(f'  ✗ Permission {codename} not found')
        
        # Show current group permissions
        self.stdout.write(f'\n=== Engineering Group Permissions ===')
        for permission in engineering_group.permissions.all().order_by('codename'):
            self.stdout.write(f'  - {permission.name} ({permission.codename})')
        
        self.stdout.write(f'\n=== Management Group Permissions ===')
        for permission in management_group.permissions.all().order_by('codename'):
            self.stdout.write(f'  - {permission.name} ({permission.codename})')
        
        self.stdout.write(
            self.style.SUCCESS('\n✓ Successfully set up tiered permission system!')
        )
        
        # Instructions
        self.stdout.write(
            self.style.WARNING(
                '\nTo assign users to groups:\n'
                '1. Engineering group: Can access inventory management\n'
                '2. Management group: Can access machine/unit/user management\n'
                '3. All users: Can access complaints and tickets (no group needed)\n\n'
                'Use Django Admin or run:\n'
                'python manage.py shell -c "'
                'from django.contrib.auth.models import Group; '
                'from core.models import CustomUser; '
                'group = Group.objects.get(name=\"GROUP_NAME\"); '
                'user = CustomUser.objects.get(username=\"USERNAME\"); '
                'group.user_set.add(user); '
                'print(f\"Added {user.username} to {group.name} group\")'
                '"'
            )
        )

