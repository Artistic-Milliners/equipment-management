"""
Management command to import faults into the Fault Library from a CSV file
The CSV needs one column named "fault" or "faults". Each fault is added once for the equipment with no manufacturer,
so it is offered on every machine of that equipment.

Usage: python manage.py import_faults_csv path/to/file.csv --equipment Sizing --category MECHANICAL --dry-run
"""
import csv
import os

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import Equipment, FaultLibrary

FAULT_COLUMNS = ('fault', 'faults')


class Command(BaseCommand):
    help = 'Import faults for one equipment type from a CSV file with a "fault" or "faults" column'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file')
        parser.add_argument('--equipment', type=str, required=True, help='Equipment name, e.g. Sizing')
        parser.add_argument(
            '--category',
            type=str.upper,
            required=True,
            choices=[value for value, _ in FaultLibrary.CATEGORY_CHOICES],
            help='Category given to every fault in the file'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without saving anything'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        category = options['category']
        dry_run = options['dry_run']

        if not os.path.exists(csv_file):
            raise CommandError(f'File not found: {csv_file}')

        equipment = self._get_equipment(options['equipment'])
        faults = self._read_faults(csv_file)

        existing = {
            self._key(description)
            for description in FaultLibrary.objects.filter(equipment=equipment, manufacturer__isnull=True)
            .values_list('fault_description', flat=True)
        }

        new_faults = {}
        blank = duplicates = already_saved = 0
        for fault in faults:
            key = self._key(fault)
            if not key:
                blank += 1
            elif key in existing:
                already_saved += 1
            elif key in new_faults:
                duplicates += 1
            else:
                new_faults[key] = fault

        if not dry_run:
            with transaction.atomic():
                FaultLibrary.objects.bulk_create([
                    FaultLibrary(equipment=equipment, fault_description=fault, fault_category=category)
                    for fault in new_faults.values()
                ])

        self.stdout.write(f'Equipment: {equipment} | Category: {category}')
        self.stdout.write(f'Rows read: {len(faults)}')
        self.stdout.write(f'Blank rows skipped: {blank}')
        self.stdout.write(f'Repeated in the file, skipped: {duplicates}')
        self.stdout.write(f'Already in the Fault Library, skipped: {already_saved}')
        if dry_run:
            self.stdout.write(self.style.WARNING(f'DRY RUN: {len(new_faults)} faults would be added, nothing saved'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Added: {len(new_faults)} faults'))

    def _get_equipment(self, name):
        matches = list(Equipment.objects.filter(name__iexact=name.strip()))
        if len(matches) == 1:
            return matches[0]
        if matches:
            raise CommandError(f'More than one equipment is named "{name}". Rename one in admin first.')
        available = ', '.join(Equipment.objects.order_by('name').values_list('name', flat=True))
        raise CommandError(f'Equipment "{name}" not found. Available: {available}')

    def _read_faults(self, csv_file):
        # Excel saves CSV as UTF-8 with a BOM or as Windows-1252, depending on the "Save as" type
        try:
            return self._read_rows(csv_file, 'utf-8-sig')
        except UnicodeDecodeError:
            return self._read_rows(csv_file, 'cp1252')

    def _read_rows(self, csv_file, encoding):
        with open(csv_file, newline='', encoding=encoding) as file:
            rows = list(csv.reader(file))

        headers = [header.strip().lower() for header in rows[0]] if rows else []
        matches = [index for index, header in enumerate(headers) if header in FAULT_COLUMNS]
        if not matches:
            raise CommandError(f'No "fault" or "faults" column found. Columns in the file: {headers}')

        column = matches[0]
        # Collapse spaces and line breaks left over from Excel cells
        return [' '.join(row[column].split()) if len(row) > column else '' for row in rows[1:]]

    def _key(self, fault):
        return ' '.join(fault.split()).casefold()
