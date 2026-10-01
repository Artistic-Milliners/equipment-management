from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError
from core.models import Spares

class Command(BaseCommand):
    help = 'Set up inventory management permissions and groups'

    def handle(self, *args, **options):
        # Get or create content type for Spares
        content_type = ContentType.objects.get_for_model(Spares)
        
        # Create permissions
        permissions = [
            ('view_spares', 'Can view inventory items'),
            ('add_spares', 'Can add inventory items'),
            ('change_spares', 'Can change inventory items'),
            ('delete_spares', 'Can delete inventory items'),
        ]
        
        created_permissions = []
        
        for codename, name in permissions:
            try:
                permission, created = Permission.objects.get_or_create(
                    codename=codename,
                    name=name,
                    content_type=content_type,
                )
                if created:
                    self.stdout.write(f'Created permission: {name}')
                else:
                    self.stdout.write(f'Permission already exists: {name}')
                created_permissions.append(permission)
            except IntegrityError:
                # Permission already exists, get it
                permission = Permission.objects.get(
                    codename=codename,
                    content_type=content_type,
                )
                self.stdout.write(f'Permission already exists: {name}')
                created_permissions.append(permission)
        
        # Create Engineering Management group
        group, created = Group.objects.get_or_create(name='Engineering Management')
        if created:
            self.stdout.write('Created Engineering Management group')
        else:
            self.stdout.write('Engineering Management group already exists')
        
        # Add all spares permissions to the group
        for permission in created_permissions:
            group.permissions.add(permission)
        
        self.stdout.write(
            self.style.SUCCESS('Successfully set up inventory permissions and groups')
        )
