# Setup Inventory Permissions - Run These Commands

## 🚀 Quick Setup (3 Commands)

### Step 1: Activate Virtual Environment
```bash
# If using venv in ems folder:
.\ems\Scripts\activate

# OR if using venv in project root:
.\Scripts\activate
```

### Step 2: Run Permission Setup
```bash
python manage.py setup_inventory_groups
```

**Expected Output:**
```
============================================================
SETTING UP INVENTORY GROUPS & PERMISSIONS
============================================================

1. Setting up INVENTORY CONTROLLER group...
   ✓ Group created
   Permissions granted:
     ✓ View spares
     ✓ Add spares
     ✓ Change spares (edit, issue, receive)
     ✓ Delete spares
     ✓ View transaction history

2. Setting up ENGINEERING group...
   ✓ Group already exists
   Permissions granted:
     ✓ View spares (read-only)
     ✓ View transaction history
     ✗ CANNOT add, edit, issue, or delete

3. Setting up MANAGEMENT group...
   ✓ Group already exists
   Permissions granted:
     ✓ View spares (read-only)
     ✓ View transaction history
     ✗ CANNOT add, edit, issue, or delete

✓ Done!
```

### Step 3: Assign Users to Groups

**Go to Django Admin:**
```
http://127.0.0.1:8000/admin/auth/group/
```

**For Inventory Controller:**
1. Click "Inventory Controller" group
2. Add users who should manage inventory
3. Save

**For Engineering:**
1. Click "Engineering" group
2. Add engineers (view-only access)
3. Save

**For Management:**
1. Click "Management" group
2. Add managers (view-only access)
3. Save

---

## ✅ What You Get

### Inventory Controller (Full Access):
```
✓ Add new items
✓ Receive stock
✓ Issue stock
✓ Edit items
✓ Delete items
✓ View everything
```

### Engineering (View Only):
```
✓ View all items
✓ Use filters
✓ View history
✗ Cannot modify
```

### Management (View Only):
```
✓ View all items
✓ Run reports
✓ View history
✗ Cannot modify
```

---

## 🎯 Quick Verification

After setup, test with your account:

**If you're in Inventory Controller:**
- Go to: http://127.0.0.1:8000/home/spares
- Should see: "Add Item" button, "Receive/Issue" buttons, Edit icons

**If you're in Engineering/Management:**
- Go to: http://127.0.0.1:8000/home/spares
- Should see: "View Only" badge, NO modification buttons

---

## 📋 Files Created

1. ✅ `core/management/commands/setup_inventory_groups.py` - Setup command
2. ✅ `INVENTORY_PERMISSIONS_SETUP.md` - Detailed guide
3. ✅ Template updated with permission checks

---

## 🎊 Ready!

Just run:
```bash
python manage.py setup_inventory_groups
```

Then assign users in Django admin!

