from typing import Any
from django.core.management.base import BaseCommand
from core.permission import create_group

class Command(BaseCommand):
    help = "Create Groups for users"

    def handle(self, *args: Any, **options: Any) -> str | None:
        create_group()
        self.stdout.write(self.style.SUCCESS("Group Created Succesfully"))