# Check Inventory Setup

## Quick Diagnostics

Run these commands to verify everything is set up correctly:

### 1. Check if migrations are applied
```bash
python manage.py showmigrations core
```

**Should show:**
```
core
 [X] 0001_initial
 [X] 0002_...
 ...
 [X] 0008_add_spare_fields (or similar)
```

**If NOT all checked:**
```bash
python manage.py migrate
```

### 2. Verify SpareTransaction table exists

```bash
python manage.py shell
```

```python
from core.models import SpareTransaction
print(SpareTransaction.objects.count())
# Should NOT give error
# Returns: 0 (or any number)
```

**If error:**
```
The migrations haven't been run!
Run: python manage.py migrate
```

### 3. Check if item codes are populated

```bash
python manage.py shell
```

```python
from core.models import Spares

# Check for spares without codes
no_codes = Spares.objects.filter(item_code__isnull=True).count()
print(f"Spares without codes: {no_codes}")

# If > 0, run:
# python manage.py fix_spare_item_codes
```

### 4. Verify a spare can be issued manually

```bash
python manage.py shell
```

```python
from core.models import Spares, SpareTransaction
from django.contrib.auth import get_user_model

User = get_user_model()

# Get a spare and user
spare = Spares.objects.first()
user = User.objects.filter(is_staff=True).first()

print(f"Testing with: {spare.item_code} - {spare.name}")
print(f"Current quantity: {spare.quantity}")

# Try creating a transaction
transaction = SpareTransaction.objects.create(
    spare=spare,
    transaction_type='ISSUE',
    quantity=-1,
    user=user,
    reason='Manual test',
    quantity_before=spare.quantity,
    quantity_after=spare.quantity - 1
)

print(f"✓ Transaction created successfully: {transaction}")
print("Test passed! Database is working.")

# Clean up
transaction.delete()
print("✓ Test transaction deleted")
```

**If this works:** The database is fine, issue is in the form/JavaScript  
**If this fails:** There's a database/migration issue

## Most Likely Issues

### Issue 1: Migrations Not Run

**Symptom:** 500 error, HTML response instead of JSON  
**Cause:** SpareTransaction table doesn't exist  
**Fix:**
```bash
python manage.py migrate
```

### Issue 2: Item Codes Not Populated

**Symptom:** Error when issuing items with NULL item_code  
**Cause:** Old spares don't have codes  
**Fix:**
```bash
python manage.py fix_spare_item_codes
```

### Issue 3: Permission Issue

**Symptom:** 403 Forbidden or permission denied  
**Cause:** User doesn't have `core.change_spares` permission  
**Fix:**
- Go to Django admin
- Add user to "Engineering" group
- Or grant permission directly

### Issue 4: CSRF Token

**Symptom:** CSRF verification failed  
**Cause:** Token not sent correctly  
**Fix:**
- ✅ Already fixed in template
- Clear browser cache
- Hard refresh (Ctrl + F5)

## Step-by-Step Fix

### Step 1: Run Migrations
```bash
cd D:\Zohaib\webapps\ems\ems
python manage.py migrate
```

### Step 2: Fix Item Codes (if needed)
```bash
python manage.py fix_spare_item_codes
```

### Step 3: Verify in Shell
```bash
python manage.py shell
```

```python
from core.models import Spares, SpareTransaction

# Verify tables exist
print(f"Spares count: {Spares.objects.count()}")
print(f"Transactions count: {SpareTransaction.objects.count()}")

# Check a spare has item_code
spare = Spares.objects.first()
print(f"Sample spare: {spare.item_code} - {spare.name}")
```

### Step 4: Test in Browser
1. Hard refresh: Ctrl + F5
2. Open browser console (F12)
3. Click "Issue Item" on any spare
4. Fill form and submit
5. Watch console and server logs

## Expected Server Output

When issuing successfully:
```
============================================================
SPARE ISSUE REQUEST - Item: MEC-0001
============================================================
POST data: <QueryDict: {'issue-quantity': ['5'], 'issue-reason': ['Test'], ...}>
Quantity: 5
Reason: Test issuance
Machine ID: 
Work Order ID: 
✓ Transaction created: ISSUE: MEC-0001 - -5 units by admin
[31/Oct/2025 12:34:56] "POST /home/spares/issueSpare/123 HTTP/1.1" 200 157
```

## Quick Test Script

Save this as `test_issue.py` and run `python test_issue.py`:

```python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ems.settings')
django.setup()

from core.models import Spares, SpareTransaction, Machines
from django.contrib.auth import get_user_model

User = get_user_model()

print("Testing Inventory Issue System...")
print("="*60)

# Test 1: Check tables exist
try:
    spare_count = Spares.objects.count()
    trans_count = SpareTransaction.objects.count()
    machine_count = Machines.objects.count()
    print(f"✓ Spares table: {spare_count} items")
    print(f"✓ Transactions table: {trans_count} records")
    print(f"✓ Machines table: {machine_count} machines")
except Exception as e:
    print(f"✗ Database error: {e}")
    exit(1)

# Test 2: Check item codes
try:
    no_codes = Spares.objects.filter(item_code__isnull=True).count()
    if no_codes > 0:
        print(f"⚠️  {no_codes} spares without item codes!")
        print("   Run: python manage.py fix_spare_item_codes")
    else:
        print(f"✓ All spares have item codes")
except Exception as e:
    print(f"✗ Error checking codes: {e}")

# Test 3: Test transaction creation
try:
    spare = Spares.objects.exclude(item_code__isnull=True).first()
    user = User.objects.filter(is_staff=True).first()
    
    if not spare:
        print("✗ No spares with valid item codes found")
        exit(1)
    
    if not user:
        print("✗ No staff user found")
        exit(1)
    
    print(f"\nTesting with:")
    print(f"  Spare: {spare.item_code} - {spare.name}")
    print(f"  User: {user.username}")
    print(f"  Current qty: {spare.quantity}")
    
    transaction = SpareTransaction.objects.create(
        spare=spare,
        transaction_type='ISSUE',
        quantity=-1,
        user=user,
        reason='Automated test',
        quantity_before=spare.quantity,
        quantity_after=spare.quantity - 1
    )
    
    print(f"✓ Transaction created: {transaction}")
    
    # Clean up
    transaction.delete()
    print(f"✓ Test transaction deleted")
    
    print("\n" + "="*60)
    print("✓ ALL TESTS PASSED - System is ready!")
    print("="*60)
    
except Exception as e:
    print(f"✗ Transaction creation failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
```

Run this to verify everything is set up correctly!

