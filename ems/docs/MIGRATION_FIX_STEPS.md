# How to Fix the Migration Issue - Step by Step

## Problem
Your existing data has duplicate `item_code` values (probably "-"), which prevents adding a unique constraint.

## Solution - Follow These Steps Exactly

### Step 1: Create Migration Without Unique Constraint
```bash
python manage.py makemigrations core --name add_spare_fields
```

This will create a migration adding all the new fields **without** the unique constraint on `item_code`.

### Step 2: Apply the Migration
```bash
python manage.py migrate
```

This adds the new fields to your database.

### Step 3: Fix Existing Data
Run our custom management command to populate unique item codes:

```bash
python manage.py fix_spare_item_codes
```

This will:
- Find all spares with missing/invalid item codes
- Clear them (set to NULL)
- Regenerate unique codes for each one
- Verify no duplicates remain

**Expected Output:**
```
Starting to fix spare item codes...
Found 45 total spares
Found 12 spares with missing/invalid item codes
  Fixed: "Ball Bearing" - Code: - → MEC-0001
  Fixed: "Motor Oil" - Code: - → GEN-0001
  ...
✓ Successfully generated item codes for 12 spares!
✓ No duplicate item codes found. Safe to add unique constraint!
```

### Step 4: Add Unique Constraint Back to Model

Edit `core/models.py` line 108:

**Change FROM:**
```python
item_code = models.CharField(max_length=30, editable=False, null=True, blank=True)
```

**Change TO:**
```python
item_code = models.CharField(max_length=30, unique=True, editable=False, null=True)
```

### Step 5: Create Final Migration
```bash
python manage.py makemigrations core --name add_item_code_unique_constraint
```

### Step 6: Apply Final Migration
```bash
python manage.py migrate
```

Now your `item_code` field has a unique constraint and all existing data has proper codes!

### Step 7: Verify Everything Works
```bash
python manage.py shell
```

Then:
```python
from core.models import Spares

# Check all spares have codes
spares = Spares.objects.all()
print(f"Total spares: {spares.count()}")

# Show some examples
for spare in spares[:5]:
    print(f"{spare.item_code} - {spare.name}")

# Check for any without codes
no_code = spares.filter(item_code__isnull=True).count()
print(f"\nSpares without codes: {no_code}")

# Try creating a new spare - should auto-generate code
new_spare = Spares.objects.create(
    name="Test Spare",
    category="mechanical",
    quantity=10,
    unit="pcs"
)
print(f"\nNew spare created with code: {new_spare.item_code}")

# Clean up test
new_spare.delete()
print("Test spare deleted")
```

**Expected Output:**
```
Total spares: 45
MEC-0001 - Ball Bearing
ELE-0001 - Relay Switch
HYD-0001 - Hydraulic Oil
...
Spares without codes: 0
New spare created with code: MEC-0002
Test spare deleted
```

## If Something Goes Wrong

### Reset and Start Over
```bash
# Roll back migrations
python manage.py migrate core 0007

# Delete migration files
# Delete: core/migrations/0008_*.py (if it exists)

# Start from Step 1 again
```

### Check Your Database Directly (PostgreSQL)
```sql
-- See duplicate item codes
SELECT item_code, COUNT(*) 
FROM core_spares 
GROUP BY item_code 
HAVING COUNT(*) > 1;

-- See all item codes
SELECT id, item_code, name 
FROM core_spares 
ORDER BY item_code;
```

## Summary

The key is to:
1. ✅ Add fields WITHOUT unique constraint
2. ✅ Fix existing data (populate codes)
3. ✅ Add unique constraint
4. ✅ Verify everything works

This way you don't get the IntegrityError!

