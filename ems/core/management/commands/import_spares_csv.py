"""
Management command to import spare parts from the stock sheet saved as CSV
Expected columns: S.N, Item Code, Item Description, UOM, Quantity, Major Category, Minor-SubCategory, Amount (PKR)
Amount is the value of the whole quantity, so the unit price is Amount / Quantity.
Every imported part is linked to all machines of the given equipment, and opening stock is logged as a receipt.
Nothing is saved if any row has a problem.

Usage: python manage.py import_spares_csv path/to/file.csv --equipment "Sizing Machine" --user admin --dry-run
"""
import csv
import os
import re
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import Equipment, Machines, MachineSpares, Spares, SpareTransaction

# Normalised header (letters and digits only, lower case) -> field in this command
COLUMNS = {
    'itemcode': 'code',
    'itemdescription': 'name',
    'uom': 'unit',
    'quantity': 'quantity',
    'majorcategory': 'category',
    'amountpkr': 'amount',
    'amount': 'amount',
}
REQUIRED = ['code', 'name', 'quantity', 'category', 'amount']
MAX_LENGTHS = {'code': 30, 'name': 255, 'unit': 50, 'category': 100}
MAX_ERRORS_SHOWN = 30


class Command(BaseCommand):
    help = 'Import spare parts from a stock sheet CSV and link them to every machine of one equipment'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file')
        parser.add_argument('--equipment', type=str, required=True, help='Equipment name, e.g. "Sizing Machine"')
        parser.add_argument('--user', type=str, required=True, help='Username recorded on the opening stock receipts')
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Check the file and show what would be imported without saving anything'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        if not os.path.exists(csv_file):
            raise CommandError(f'File not found: {csv_file}')

        equipment = self._get_equipment(options['equipment'])
        user = get_user_model().objects.filter(username=options['user']).first()
        if user is None:
            raise CommandError(f'User "{options["user"]}" not found')
        machines = list(Machines.objects.filter(type_of_machine=equipment).order_by('name'))

        rows = self._read_rows(csv_file)
        items, errors, blank = self._parse(rows)
        if errors:
            for error in errors[:MAX_ERRORS_SHOWN]:
                self.stdout.write(self.style.ERROR(f'  {error}'))
            if len(errors) > MAX_ERRORS_SHOWN:
                self.stdout.write(self.style.ERROR(f'  ... and {len(errors) - MAX_ERRORS_SHOWN} more'))
            raise CommandError(f'{len(errors)} problem(s) found in the file. Nothing was imported.')

        existing = {
            spare.item_code.casefold(): spare
            for spare in Spares.objects.filter(item_code__in=[item['code'] for item in items])
        }
        new_items = [item for item in items if item['code'].casefold() not in existing]

        self.stdout.write(f'Equipment: {equipment} ({len(machines)} machines: {", ".join(m.name for m in machines) or "none"})')
        self.stdout.write(f'Rows read: {len(items) + blank} | blank rows skipped: {blank}')
        self.stdout.write(f'Already in inventory (item code exists), not changed: {len(items) - len(new_items)}')
        categories = sorted({item['category'] for item in new_items})
        self.stdout.write(f'Categories: {", ".join(categories) or "-"}')
        if not machines:
            self.stdout.write(self.style.WARNING('No machines found for this equipment, so parts will not be linked to any machine.'))

        if options['dry_run']:
            self.stdout.write(self.style.WARNING(f'DRY RUN: {len(new_items)} spare parts would be added, nothing saved'))
            return

        with transaction.atomic():
            for item in new_items:
                spare = Spares.objects.create(
                    item_code=item['code'], name=item['name'], unit=item['unit'] or None,
                    quantity=item['quantity'], category=item['category'], unit_price=item['unit_price'],
                )
                existing[item['code'].casefold()] = spare
                if item['quantity']:
                    SpareTransaction.objects.create(
                        spare=spare, transaction_type='RECEIPT', quantity=item['quantity'], user=user,
                        reason=f'Opening stock imported from {os.path.basename(csv_file)}',
                        quantity_before=0, quantity_after=item['quantity'],
                    )

            # Link every part in the file (new or existing) to every machine of the equipment
            spares = [existing[item['code'].casefold()] for item in items]
            linked = set(MachineSpares.objects.filter(machine__in=machines, spare__in=spares)
                         .values_list('machine_id', 'spare_id'))
            links = [MachineSpares(machine=machine, spare=spare)
                     for machine in machines for spare in spares if (machine.pk, spare.pk) not in linked]
            MachineSpares.objects.bulk_create(links)

        self.stdout.write(self.style.SUCCESS(f'Added: {len(new_items)} spare parts | machine links added: {len(links)}'))

    def _get_equipment(self, name):
        matches = list(Equipment.objects.filter(name__iexact=name.strip()))
        if len(matches) == 1:
            return matches[0]
        if matches:
            raise CommandError(f'More than one equipment is named "{name}". Rename one in admin first.')
        available = ', '.join(Equipment.objects.order_by('name').values_list('name', flat=True))
        raise CommandError(f'Equipment "{name}" not found. Available: {available}')

    def _read_rows(self, csv_file):
        # Excel saves CSV as UTF-8 with a BOM or as Windows-1252, depending on the "Save as" type
        for encoding in ('utf-8-sig', 'cp1252'):
            try:
                with open(csv_file, newline='', encoding=encoding) as file:
                    return list(csv.reader(file))
            except UnicodeDecodeError:
                continue
        raise CommandError('Could not read the file. Save it from Excel as "CSV UTF-8".')

    def _parse(self, rows):
        """Find the header row, then validate every row. Returns (items, errors, blank_rows)."""
        header_index, columns = None, {}
        for index, row in enumerate(rows[:15]):
            found = {COLUMNS[key]: position for position, cell in enumerate(row)
                     if (key := re.sub(r'[^a-z0-9]', '', cell.lower())) in COLUMNS}
            if 'code' in found and 'name' in found:
                header_index, columns = index, found
                break
        if header_index is None:
            raise CommandError('Header row not found. The file needs "Item Code" and "Item Description" columns.')
        missing = [field for field in REQUIRED if field not in columns]
        if missing:
            raise CommandError(f'Missing columns: {", ".join(missing)}. Found: {rows[header_index]}')

        items, errors, blank, seen = [], [], 0, {}
        for line, row in enumerate(rows[header_index + 1:], start=header_index + 2):
            values = {field: ' '.join(row[position].split()) if position < len(row) else ''
                      for field, position in columns.items()}
            if not any(values.values()):
                blank += 1
                continue

            problems = [f'{field} is empty' for field in ('code', 'name', 'category') if not values[field]]
            problems += [f'{field} is longer than {limit} characters' for field, limit in MAX_LENGTHS.items()
                         if len(values.get(field, '')) > limit]

            quantity = self._number(values['quantity'])
            amount = self._number(values['amount'])
            if quantity is None or quantity < 0 or quantity != quantity.to_integral_value():
                problems.append(f'quantity "{values["quantity"]}" is not a whole number')
            if amount is None or amount < 0:
                problems.append(f'amount "{values["amount"]}" is not a number')

            key = values['code'].casefold()
            if key and key in seen:
                problems.append(f'item code {values["code"]} is repeated (first on line {seen[key]})')
            seen.setdefault(key, line)

            if problems:
                errors.append(f'Line {line}: ' + '; '.join(problems))
                continue

            quantity = int(quantity)
            unit_price = (amount / quantity).quantize(Decimal('0.01'), ROUND_HALF_UP) if quantity else Decimal('0.00')
            items.append({**values, 'quantity': quantity, 'unit_price': unit_price})
        return items, errors, blank

    def _number(self, value):
        # Accepts "1,250.00", "Rs 1250" and blanks (treated as 0)
        cleaned = re.sub(r'[^0-9.\-]', '', value)
        if not cleaned:
            return Decimal('0')
        try:
            return Decimal(cleaned)
        except InvalidOperation:
            return None
