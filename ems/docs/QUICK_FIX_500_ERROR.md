# Quick Fix: 500 Error When Issuing Items

## Most Likely Cause: Migrations Not Run

The 500 error is most likely because the database changes haven't been applied yet.

## ✅ Quick Fix (3 Steps):

### Step 1: Run Migrations
```bash
python manage.py migrate
```

**Expected output:**
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, core, sessions
Running migrations:
  Applying core.0008_add_spare_fields... OK
```

### Step 2: Fix Item Codes (if you haven't already)
```bash
python manage.py fix_spare_item_codes
```

**Expected output:**
```
Starting to fix spare item codes...
Found 78 total spares
Found 30 spares with missing/invalid item codes
✓ Successfully generated item codes for 30 spares!
✓ No duplicate item codes found. Safe to add unique constraint!
```

### Step 3: Try Issuing Again
1. Hard refresh browser: **Ctrl + F5**
2. Click "Issue Item"
3. Fill form
4. Submit

**Should now work!**

## Verify Setup

Run this quick check:
```bash
python manage.py shell
```

```python
from core.models import SpareTransaction

# This should NOT give an error
print(SpareTransaction.objects.count())
# Returns: 0 (or any number)
```

**If you get an error:**
```
django.db.utils.ProgrammingError: relation "core_sparetransaction" does not exist
```

→ **Migrations weren't run!** Go back to Step 1.

## After Fix

Once migrations are run:

1. **Refresh page**: Ctrl + F5
2. **Test issuing**: Should work perfectly
3. **Check transaction**: Go to Django admin → Spare Transactions
4. **Verify**: You should see the transaction record

## Check Server Logs

When you try issuing, you should now see:
```
============================================================
SPARE ISSUE REQUEST - Item: MEC-0001
============================================================
POST data: <QueryDict: ...>
Quantity: 5
Reason: Machine repair
✓ Transaction created: ISSUE: MEC-0001 - -5 units by admin
[200] OK
```

Instead of:
```
[500] Internal Server Error
```

## Still Not Working?

Share these details:

1. **Output of:** `python manage.py showmigrations core`
2. **Output of:** `python manage.py migrate`
3. **Server error** from Django console (full traceback)
4. **Browser error** from Console (F12)

---

**TL;DR:** Run `python manage.py migrate` then try again!

