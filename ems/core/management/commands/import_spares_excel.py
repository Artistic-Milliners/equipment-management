"""
Management command to import spares from Excel file
Usage: python manage.py import_spares_excel path/to/file.xlsx
"""
from django.core.management.base import BaseCommand
from core.models import Spares, Manufacturer, SpareTransaction, Machines
from django.contrib.auth import get_user_model
import openpyxl
from datetime import datetime
import os

User = get_user_model()


class Command(BaseCommand):
    help = 'Import spares from Excel file'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help='Path to Excel file')
        parser.add_argument(
            '--user',
            type=str,
            default='admin',
            help='Username to attribute imports to (default: admin)'
        )
        parser.add_argument(
            '--skip-duplicates',
            action='store_true',
            help='Skip items that already exist instead of updating them'
        )

    def handle(self, *args, **options):
        excel_file = options['excel_file']
        username = options['user']
        skip_duplicates = options['skip_duplicates']
        
        # Verify file exists
        if not os.path.exists(excel_file):
            self.stdout.write(self.style.ERROR(f'✗ File not found: {excel_file}'))
            return
        
        # Get user for transaction logging
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'✗ User "{username}" not found'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'\n{"="*60}'))
        self.stdout.write(self.style.SUCCESS(f'IMPORTING SPARES FROM EXCEL'))
        self.stdout.write(self.style.SUCCESS(f'{"="*60}'))
        self.stdout.write(f'File: {excel_file}')
        self.stdout.write(f'User: {username}')
        self.stdout.write(f'Skip duplicates: {skip_duplicates}\n')
        
        # Load Excel file
        try:
            workbook = openpyxl.load_workbook(excel_file)
            sheet = workbook.active
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error loading Excel file: {e}'))
            return
        
        # Verify headers
        expected_headers = [
            'Item Name', 'Category', 'Description', 'Manufacturer', 
            'Manufacturer Part Number', 'Initial Quantity', 'Unit',
            'Min Stock Level', 'Max Stock Level', 'Unit Price',
            'Machine Names (comma-separated)'
        ]
        
        header_row = [cell.value for cell in sheet[1]]
        
        self.stdout.write('\nChecking headers...')
        for expected in expected_headers:
            if expected not in header_row:
                self.stdout.write(self.style.WARNING(f'⚠️  Optional column missing: {expected}'))
        
        # Statistics
        total_rows = 0
        created_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0
        
        # Process each row
        for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            if not row[0]:  # Skip empty rows
                continue
            
            total_rows += 1
            
            try:
                # Extract data from row
                item_name = str(row[0]).strip() if row[0] else None
                category = str(row[1]).lower().strip() if row[1] else 'general'
                description = str(row[2]).strip() if row[2] else ''
                manufacturer_name = str(row[3]).strip() if row[3] else None
                mfg_part_number = str(row[4]).strip() if row[4] else ''
                quantity = int(row[5]) if row[5] else 0
                unit = str(row[6]).strip() if row[6] else 'pcs'
                min_stock = int(row[7]) if row[7] else 5
                max_stock = int(row[8]) if row[8] else 100
                unit_price = float(row[9]) if row[9] else 0.00
                machine_names = str(row[10]).strip() if row[10] else ''
                
                # Validate required fields
                if not item_name:
                    self.stdout.write(self.style.ERROR(f'  Row {row_num}: Missing item name - SKIPPED'))
                    error_count += 1
                    continue
                
                # Validate category
                valid_categories = ['electrical', 'mechanical', 'hydraulic', 'pneumatic', 'safety', 'general']
                if category not in valid_categories:
                    self.stdout.write(self.style.WARNING(f'  Row {row_num}: Invalid category "{category}", using "general"'))
                    category = 'general'
                
                # Get or create manufacturer
                manufacturer = None
                if manufacturer_name:
                    manufacturer, _ = Manufacturer.objects.get_or_create(
                        name=manufacturer_name,
                        defaults={'coo': 'Unknown'}
                    )
                
                # Check if spare already exists
                existing_spare = None
                if mfg_part_number:
                    existing_spare = Spares.objects.filter(
                        manufacturer_part_number=mfg_part_number
                    ).first()
                
                if not existing_spare:
                    existing_spare = Spares.objects.filter(
                        name__iexact=item_name
                    ).first()
                
                if existing_spare:
                    if skip_duplicates:
                        self.stdout.write(f'  Row {row_num}: "{item_name}" already exists - SKIPPED')
                        skipped_count += 1
                        continue
                    else:
                        # Update existing spare
                        existing_spare.description = description
                        existing_spare.manufacturer = manufacturer
                        existing_spare.manufacturer_part_number = mfg_part_number
                        
                        old_quantity = existing_spare.quantity
                        existing_spare.quantity = quantity
                        existing_spare.unit = unit
                        existing_spare.min_stock_level = min_stock
                        existing_spare.max_stock_level = max_stock
                        existing_spare.unit_price = unit_price
                        existing_spare.save()
                        
                        # Create adjustment transaction if quantity changed
                        if old_quantity != quantity:
                            SpareTransaction.objects.create(
                                spare=existing_spare,
                                transaction_type='ADJUSTMENT',
                                quantity=quantity - old_quantity,
                                user=user,
                                reason=f'Excel import: Stock adjusted {old_quantity} → {quantity}',
                                quantity_before=old_quantity,
                                quantity_after=quantity
                            )
                        
                        self.stdout.write(self.style.WARNING(f'  Row {row_num}: "{item_name}" ({existing_spare.item_code}) - UPDATED'))
                        updated_count += 1
                        spare = existing_spare
                else:
                    # Create new spare
                    spare = Spares(
                        name=item_name,
                        category=category,
                        description=description,
                        manufacturer=manufacturer,
                        manufacturer_part_number=mfg_part_number,
                        quantity=quantity,
                        unit=unit,
                        min_stock_level=min_stock,
                        max_stock_level=max_stock,
                        unit_price=unit_price
                    )
                    spare.save()  # This auto-generates item_code
                    
                    # Create initial stock transaction
                    if quantity > 0:
                        SpareTransaction.objects.create(
                            spare=spare,
                            transaction_type='RECEIPT',
                            quantity=quantity,
                            user=user,
                            reason='Initial stock - Excel import',
                            quantity_before=0,
                            quantity_after=quantity
                        )
                    
                    self.stdout.write(self.style.SUCCESS(f'  Row {row_num}: "{item_name}" → {spare.item_code} - CREATED'))
                    created_count += 1
                
                # Handle machine associations
                if machine_names:
                    machine_list = [m.strip() for m in machine_names.split(',') if m.strip()]
                    for machine_name in machine_list:
                        try:
                            machine = Machines.objects.get(name__iexact=machine_name)
                            machine.machine_spare.add(spare)
                            self.stdout.write(f'    ✓ Linked to machine: {machine.name}')
                        except Machines.DoesNotExist:
                            self.stdout.write(self.style.WARNING(f'    ⚠️  Machine "{machine_name}" not found'))
                        except Machines.MultipleObjectsReturned:
                            self.stdout.write(self.style.WARNING(f'    ⚠️  Multiple machines named "{machine_name}"'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  Row {row_num}: ERROR - {str(e)}'))
                error_count += 1
                import traceback
                traceback.print_exc()
                continue
        
        # Summary
        self.stdout.write(f'\n{"="*60}')
        self.stdout.write(self.style.SUCCESS('IMPORT COMPLETE'))
        self.stdout.write(f'{"="*60}')
        self.stdout.write(f'Total rows processed: {total_rows}')
        self.stdout.write(self.style.SUCCESS(f'✓ Created: {created_count}'))
        if updated_count > 0:
            self.stdout.write(self.style.WARNING(f'⚠️  Updated: {updated_count}'))
        if skipped_count > 0:
            self.stdout.write(f'⊝ Skipped: {skipped_count}')
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'✗ Errors: {error_count}'))
        
        self.stdout.write(f'\n{"="*60}\n')
        
        if created_count > 0 or updated_count > 0:
            self.stdout.write(self.style.SUCCESS('✓ Items successfully imported!'))
            self.stdout.write('\nNext steps:')
            self.stdout.write('1. Go to: http://127.0.0.1:8000/home/spares')
            self.stdout.write('2. Verify imported items')
            self.stdout.write('3. Check transaction history')

