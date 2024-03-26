from typing import Any
from django.core.management.base import BaseCommand, CommandParser
from core.permission import create_group

class Command(BaseCommand):
    help = "Create Groups for users"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('group_name', type=str)

    def handle(self, *args: Any, **options: Any) -> str | None:
        groupName=options['group_name']
        name = create_group(groupName)
        self.stdout.write(self.style.SUCCESS(f"{name} Group Created Succesfully"))