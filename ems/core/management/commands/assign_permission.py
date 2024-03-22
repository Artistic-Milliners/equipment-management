from typing import Any
from django.core.management.base import BaseCommand
from core.permission import assign_permission

class Command(BaseCommand):
    help = 'Assign permission to group'

    def handle(self, *args: Any, **options: Any) -> str | None:
        assign_permission()
        self.stdout.write(self.style.SUCCESS('Permission assigned to group'))
