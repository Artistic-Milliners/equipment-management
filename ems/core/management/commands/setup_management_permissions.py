from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from core.models import Spares, Machines, Unit, Employee, Equipment, Department

class Command(BaseCommand):
    help = 'Set up comprehensive management permissions for all management tools'

    def handle(self, *args, **options):
        # Define all models that need management permissions
        models_to_manage = [
            (Spares, 'Inventory Management'),
            (Machines, 'Machine Management'),
            (Unit, 'Unit Management'),
            (Employee, 'User Management'),
            (Equipment, 'Equipment Management'),
            (Department, 'Department Management'),
        ]
        
        all_permissions = []
        
        # Create permissions for each model
        for model, category in models_to_manage:
            content_type = ContentType.objects.get_for_model(model)
            model_name = model.__name__.lower()
            
            permissions_data = [
                (f'view_{model_name}', f'Can view {category}'),
                (f'add_{model_name}', f'Can add {category}'),
                (f'change_{model_name}', f'Can change {category}'),
                (f'delete_{model_name}', f'Can delete {category}'),
            ]
            
            self.stdout.write(f'\nSetting up permissions for {category}:')
            
            for codename, name in permissions_data:
                try:
                    permission, created = Permission.objects.get_or_create(
                        codename=codename,
                        name=name,
                        content_type=content_type,
                    )
                    if created:
                        self.stdout.write(f'  ✓ Created permission: {name}')
                    else:
                        self.stdout.write(f'  - Permission already exists: {name}')
                    all_permissions.append(permission)
                except Exception as e:
                    self.stdout.write(f'  ✗ Error creating permission {name}: {e}')
        
        # Create Management group
        try:
            group, created = Group.objects.get_or_create(name='Management')
            if created:
                self.stdout.write(f'\n✓ Created Management group')
            else:
                self.stdout.write(f'\n- Management group already exists')
        except Exception as e:
            self.stdout.write(f'\n✗ Error creating Management group: {e}')
            return
        
        # Add all permissions to Management group
        try:
            for permission in all_permissions:
                group.permissions.add(permission)
            self.stdout.write(f'✓ Added {len(all_permissions)} permissions to Management group')
        except Exception as e:
            self.stdout.write(f'✗ Error adding permissions to group: {e}')
            return
        
        # Show current permissions in the group
        self.stdout.write(f'\nCurrent permissions in Management group:')
        for permission in group.permissions.all().order_by('content_type__model'):
            self.stdout.write(f'  - {permission.name} ({permission.codename})')
        
        self.stdout.write(
            self.style.SUCCESS('\n✓ Successfully set up comprehensive management permissions!')
        )
        
        # Instructions for assigning users
        self.stdout.write(
            self.style.WARNING(
                '\nTo assign users to the Management group, use Django Admin or run:\n'
                'python manage.py shell -c "'
                'from django.contrib.auth.models import Group; '
                'from core.models import CustomUser; '
                'group = Group.objects.get(name=\"Management\"); '
                'user = CustomUser.objects.get(username=\"USERNAME\"); '
                'group.user_set.add(user); '
                'print(f\"Added {user.username} to Management group\")'
                '"'
            )
        )

