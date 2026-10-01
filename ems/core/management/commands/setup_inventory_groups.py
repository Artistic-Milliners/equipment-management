"""
Management command to set up inventory management groups and permissions
Usage: python manage.py setup_inventory_groups
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from core.models import Spares, SpareTransaction


class Command(BaseCommand):
    help = 'Set up inventory management groups with appropriate permissions'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('SETTING UP INVENTORY GROUPS & PERMISSIONS'))
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))
        
        # Get content types
        spares_ct = ContentType.objects.get_for_model(Spares)
        transaction_ct = ContentType.objects.get_for_model(SpareTransaction)
        
        # Get all spare permissions
        view_spares = Permission.objects.get(codename='view_spares', content_type=spares_ct)
        add_spares = Permission.objects.get(codename='add_spares', content_type=spares_ct)
        change_spares = Permission.objects.get(codename='change_spares', content_type=spares_ct)
        delete_spares = Permission.objects.get(codename='delete_spares', content_type=spares_ct)
        
        # Transaction permissions
        view_transaction = Permission.objects.get(codename='view_sparetransaction', content_type=transaction_ct)
        
        # ========================================
        # 1. INVENTORY CONTROLLER GROUP
        # ========================================
        self.stdout.write(self.style.SUCCESS('\n1. Setting up INVENTORY CONTROLLER group...'))
        
        inventory_controller, created = Group.objects.get_or_create(name='Inventory Controller')
        
        if created:
            self.stdout.write('   ✓ Group created')
        else:
            self.stdout.write('   ✓ Group already exists')
            inventory_controller.permissions.clear()
        
        # Inventory Controllers get FULL access
        inventory_controller.permissions.add(
            view_spares,
            add_spares,
            change_spares,
            delete_spares,
            view_transaction
        )
        
        self.stdout.write('   Permissions granted:')
        self.stdout.write('     ✓ View spares')
        self.stdout.write('     ✓ Add spares')
        self.stdout.write('     ✓ Change spares (edit, issue, receive)')
        self.stdout.write('     ✓ Delete spares')
        self.stdout.write('     ✓ View transaction history')
        
        # ========================================
        # 2. ENGINEERING GROUP
        # ========================================
        self.stdout.write(self.style.SUCCESS('\n2. Setting up ENGINEERING group...'))
        
        engineering, created = Group.objects.get_or_create(name='Engineering')
        
        if created:
            self.stdout.write('   ✓ Group created')
        else:
            self.stdout.write('   ✓ Group already exists')
            # Clear existing inventory permissions
            engineering.permissions.remove(add_spares, change_spares, delete_spares)
        
        # Engineering gets VIEW ONLY access
        engineering.permissions.add(
            view_spares,
            view_transaction
        )
        
        self.stdout.write('   Permissions granted:')
        self.stdout.write('     ✓ View spares (read-only)')
        self.stdout.write('     ✓ View transaction history')
        self.stdout.write('     ✗ CANNOT add, edit, issue, or delete')
        
        # ========================================
        # 3. MANAGEMENT GROUP
        # ========================================
        self.stdout.write(self.style.SUCCESS('\n3. Setting up MANAGEMENT group...'))
        
        management, created = Group.objects.get_or_create(name='Management')
        
        if created:
            self.stdout.write('   ✓ Group created')
        else:
            self.stdout.write('   ✓ Group already exists')
            # Clear inventory modification permissions
            management.permissions.remove(add_spares, change_spares, delete_spares)
        
        # Management gets VIEW ONLY access (same as Engineering)
        management.permissions.add(
            view_spares,
            view_transaction
        )
        
        self.stdout.write('   Permissions granted:')
        self.stdout.write('     ✓ View spares (read-only)')
        self.stdout.write('     ✓ View transaction history')
        self.stdout.write('     ✓ Run reports (future feature)')
        self.stdout.write('     ✗ CANNOT add, edit, issue, or delete')
        
        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('SETUP COMPLETE'))
        self.stdout.write('='*60)
        
        self.stdout.write('\nGroup Permissions Summary:')
        self.stdout.write('\n📦 INVENTORY CONTROLLER:')
        self.stdout.write('   ✓ Full access - Add, Edit, Issue, Receive, Delete, View')
        
        self.stdout.write('\n🔧 ENGINEERING:')
        self.stdout.write('   ✓ View only - Can see items and filter')
        self.stdout.write('   ✗ Cannot modify')
        
        self.stdout.write('\n👔 MANAGEMENT:')
        self.stdout.write('   ✓ View only - Can see items and run reports')
        self.stdout.write('   ✗ Cannot modify')
        
        self.stdout.write('\n❌ OTHER USERS:')
        self.stdout.write('   ✗ No inventory access')
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write('\nNext steps:')
        self.stdout.write('1. Assign users to appropriate groups in Django admin')
        self.stdout.write('2. Test with different user accounts')
        self.stdout.write('3. Verify permissions work correctly')
        self.stdout.write('\n✓ Done!\n')

