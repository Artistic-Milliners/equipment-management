"""
Management command to populate item codes for existing spares
Run this BEFORE applying migrations with unique constraint
"""
from django.core.management.base import BaseCommand
from core.models import Spares


class Command(BaseCommand):
    help = 'Populate item codes for existing spares that have duplicate or missing codes'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to fix spare item codes...'))
        
        # Get all spares
        all_spares = Spares.objects.all()
        total_count = all_spares.count()
        
        self.stdout.write(f'Found {total_count} total spares')
        
        # Find spares with problematic codes (None, empty, '-', or 'nan')
        problematic_codes = [None, '', '-', 'nan', 'NaN', 'NAN']
        spares_to_fix = all_spares.filter(item_code__in=problematic_codes) | all_spares.filter(item_code__isnull=True)
        problem_count = spares_to_fix.count()
        
        self.stdout.write(f'Found {problem_count} spares with missing/invalid item codes')
        
        if problem_count == 0:
            self.stdout.write(self.style.SUCCESS('✓ All spares already have valid item codes!'))
            return
        
        # Clear invalid item codes first
        spares_to_fix.update(item_code=None)
        
        # Now regenerate codes by saving each spare
        fixed_count = 0
        for spare in spares_to_fix:
            old_code = spare.item_code
            spare.save()  # This triggers auto-generation in the save() method
            
            self.stdout.write(
                f'  Fixed: "{spare.name}" - Code: {old_code} → {spare.item_code}'
            )
            fixed_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Successfully generated item codes for {fixed_count} spares!'))
        
        # Verify no duplicates remain
        from django.db.models import Count
        duplicates = Spares.objects.values('item_code').annotate(
            count=Count('item_code')
        ).filter(count__gt=1)
        
        if duplicates.exists():
            self.stdout.write(self.style.ERROR('\n✗ WARNING: Duplicate item codes still exist:'))
            for dup in duplicates:
                self.stdout.write(f'  - Code "{dup["item_code"]}" appears {dup["count"]} times')
        else:
            self.stdout.write(self.style.SUCCESS('\n✓ No duplicate item codes found. Safe to add unique constraint!'))

