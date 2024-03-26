from typing import Any
from django.core.management.base import BaseCommand, CommandParser
from core.permission import assign_permission

class Command(BaseCommand):
    help = 'Assign permission to group'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('group_name', type=str)
        parser.add_argument('permission', type=str)

    def handle(self, *args: Any, **options: Any) -> str | None:
        assign_permission(options['group_name'],options['permission'])
        self.stdout.write(self.style.SUCCESS('Permission assigned to group'))
