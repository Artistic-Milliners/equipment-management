from typing import Any
from django.core.management.base import BaseCommand
from core.permission import create_permission

class Command(BaseCommand):
    help = 'Create permissions for groups and users'
    
    def handle(self, *args: Any, **options: Any) -> str | None:
        try:
            create_permission()
            self.stdout.write(self.style.SUCCESS('Permission Created succesfully'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(str(e)))
