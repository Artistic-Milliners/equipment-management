from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from core.models import Spares

class Command(BaseCommand):
    help = 'Set up inventory management permissions and groups (safe version)'

    def handle(self, *args, **options):
        # Get content type for Spares
        try:
            content_type = ContentType.objects.get_for_model(Spares)
            self.stdout.write(f'Found content type for Spares: {content_type}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error getting content type: {e}'))
            return

        # Define permissions
        permissions_data = [
            ('view_spares', 'Can view inventory items'),
            ('add_spares', 'Can add inventory items'),
            ('change_spares', 'Can change inventory items'),
            ('delete_spares', 'Can delete inventory items'),
        ]
        
        # Get or create permissions
        permissions = []
        for codename, name in permissions_data:
            try:
                permission = Permission.objects.get(
                    codename=codename,
                    content_type=content_type,
                )
                self.stdout.write(f'Found existing permission: {name}')
                permissions.append(permission)
            except Permission.DoesNotExist:
                try:
                    permission = Permission.objects.create(
                        codename=codename,
                        name=name,
                        content_type=content_type,
                    )
                    self.stdout.write(f'Created permission: {name}')
                    permissions.append(permission)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating permission {name}: {e}'))
                    continue
        
        # Create or get Engineering Management group
        try:
            group, created = Group.objects.get_or_create(name='Engineering Management')
            if created:
                self.stdout.write('Created Engineering Management group')
            else:
                self.stdout.write('Engineering Management group already exists')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating group: {e}'))
            return
        
        # Add permissions to group
        try:
            for permission in permissions:
                group.permissions.add(permission)
            self.stdout.write(f'Added {len(permissions)} permissions to Engineering Management group')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error adding permissions to group: {e}'))
            return
        
        self.stdout.write(
            self.style.SUCCESS('Successfully set up inventory permissions and groups')
        )
        
        # Show current permissions
        self.stdout.write('\nCurrent permissions in Engineering Management group:')
        for permission in group.permissions.filter(content_type=content_type):
            self.stdout.write(f'  - {permission.name} ({permission.codename})')

