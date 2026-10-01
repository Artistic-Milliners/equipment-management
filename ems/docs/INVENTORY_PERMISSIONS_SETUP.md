# Inventory Permissions Setup Guide

## Overview
Role-based access control for inventory management with three permission levels: Inventory Controller (full access), Engineering (view only), and Management (view only).

---

## 📋 Permission Structure

### 1. **Inventory Controller** 📦
**Full Access - Can Modify Inventory**

**Permissions:**
- ✅ View spares
- ✅ Add spares
- ✅ Change spares (edit, issue, receive)
- ✅ Delete spares
- ✅ View transaction history

**Can Do:**
- ✓ Add new items
- ✓ Receive stock (from suppliers)
- ✓ Issue stock (to machines/jobs)
- ✓ Edit item details
- ✓ Adjust quantities
- ✓ Delete items
- ✓ View all filters
- ✓ View transaction history
- ✓ Export reports

**UI Access:**
- ✓ "Add Item" button visible
- ✓ "Receive Stock" button visible
- ✓ "Issue Item" button visible
- ✓ "Edit" icon visible
- ✓ All modals functional

---

### 2. **Engineering** 🔧
**View Only - Read Access**

**Permissions:**
- ✅ View spares
- ✅ View transaction history
- ❌ Cannot add/edit/delete

**Can Do:**
- ✓ View all items
- ✓ Use all filters (category, status, machine)
- ✓ Search items
- ✓ View item details
- ✓ View transaction history
- ✓ Export reports (view only)

**Cannot Do:**
- ✗ Add new items
- ✗ Receive stock
- ✗ Issue stock
- ✗ Edit items
- ✗ Delete items

**UI Access:**
- ✗ "Add Item" button hidden
- ✗ "Receive Stock" button hidden
- ✗ "Issue Item" button hidden
- ✗ "Edit" icon hidden
- ✓ "History" button visible
- ✓ View badge shows "View Only"

---

### 3. **Management** 👔
**View Only - Read Access**

**Permissions:**
- ✅ View spares
- ✅ View transaction history
- ❌ Cannot add/edit/delete

**Can Do:**
- ✓ View all items
- ✓ Use all filters
- ✓ View transaction history
- ✓ Run reports
- ✓ Export data

**Cannot Do:**
- ✗ Add new items
- ✗ Receive stock
- ✗ Issue stock
- ✗ Edit items
- ✗ Delete items

**UI Access:**
- Same as Engineering group
- Read-only access

---

### 4. **Other Users** ❌
**No Access**

**Permissions:**
- ❌ No inventory permissions

**UI Access:**
- ✗ Cannot access `/home/spares` page
- ✗ Shows "Access Denied" page

---

## 🚀 Setup Instructions

### Step 1: Run Setup Command
```bash
python manage.py setup_inventory_groups
```

**Output:**
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
     ✓ Run reports (future feature)
     ✗ CANNOT add, edit, issue, or delete

============================================================
SETUP COMPLETE
============================================================

✓ Done!
```

### Step 2: Assign Users to Groups

**Go to Django Admin:**
```
http://127.0.0.1:8000/admin/auth/group/
```

**For each group:**

#### Inventory Controller:
1. Click "Inventory Controller"
2. Select users who should manage inventory
3. Move to "Chosen users" box
4. Save

#### Engineering:
1. Click "Engineering"
2. Select engineering team members
3. Move to "Chosen users"
4. Save

#### Management:
1. Click "Management"
2. Select management users
3. Move to "Chosen users"
4. Save

### Step 3: Test Permissions

**Test with Inventory Controller user:**
```
1. Login as inventory controller
2. Go to: http://127.0.0.1:8000/home/spares
3. Should see:
   ✓ "Add Item" button
   ✓ "Receive Stock" buttons on cards
   ✓ "Issue Item" buttons on cards
   ✓ "Edit" icons on cards
   ✓ All modals work
```

**Test with Engineering user:**
```
1. Login as engineering user
2. Go to: http://127.0.0.1:8000/home/spares
3. Should see:
   ✓ All items visible
   ✓ "View Only" badge in header
   ✓ "View-only access" message on cards
   ✓ "History" button works
   ✗ No "Add Item" button
   ✗ No "Receive/Issue" buttons
   ✗ No "Edit" icons
```

**Test with Management user:**
```
Same as Engineering - view only access
```

**Test with unauthorized user:**
```
1. Login as user NOT in any group
2. Try to access: http://127.0.0.1:8000/home/spares
3. Should see:
   ✗ "Access Denied" page
```

---

## 🎯 Permission Matrix

| Action | Inventory Controller | Engineering | Management | Other Users |
|--------|---------------------|-------------|------------|-------------|
| **View Items** | ✅ | ✅ | ✅ | ❌ |
| **Search & Filter** | ✅ | ✅ | ✅ | ❌ |
| **View History** | ✅ | ✅ | ✅ | ❌ |
| **Add Item** | ✅ | ❌ | ❌ | ❌ |
| **Receive Stock** | ✅ | ❌ | ❌ | ❌ |
| **Issue Stock** | ✅ | ❌ | ❌ | ❌ |
| **Edit Item** | ✅ | ❌ | ❌ | ❌ |
| **Delete Item** | ✅ | ❌ | ❌ | ❌ |
| **Export Reports** | ✅ | ✅ | ✅ | ❌ |

---

## 🖥️ UI Differences by Role

### Inventory Controller View:
```
┌────────────────────────────────────────┐
│ Inventory Management                   │
│                                        │
│ [+ Add Item] [Export]                  │
├────────────────────────────────────────┤
│ [Search] [Filters...]                  │
├────────────────────────────────────────┤
│ ┌──────────────┐  ┌──────────────┐    │
│ │ [👁️] [✏️]   │  │ [👁️] [✏️]   │    │
│ │ Ball Bearing │  │ Hydraulic Oil│    │
│ │              │  │              │    │
│ │ [+Receive]   │  │ [+Receive]   │    │
│ │ [-Issue]     │  │ [-Issue]     │    │
│ │ [📜History]  │  │ [📜History]  │    │
│ └──────────────┘  └──────────────┘    │
└────────────────────────────────────────┘
```

### Engineering/Management View:
```
┌────────────────────────────────────────┐
│ Inventory Management [View Only]       │
│                                        │
│ [Export]                               │
├────────────────────────────────────────┤
│ [Search] [Filters...]                  │
├────────────────────────────────────────┤
│ ┌──────────────┐  ┌──────────────┐    │
│ │ [👁️]        │  │ [👁️]        │    │
│ │ Ball Bearing │  │ Hydraulic Oil│    │
│ │              │  │              │    │
│ │ ℹ️ View-only │  │ ℹ️ View-only │    │
│ │ [📜History]  │  │ [📜History]  │    │
│ └──────────────┘  └──────────────┘    │
└────────────────────────────────────────┘
```

---

## 🔐 Backend Enforcement

### All Views Protected:

```python
# spare_view - View items
@permission_required('core.view_spares', raise_exception=True)

# spare_add - Add new items
@permission_required('core.add_spares', raise_exception=True)

# spare_update - Edit items
@permission_required('core.change_spares', raise_exception=True)

# spare_issue - Issue stock
@permission_required('core.change_spares', raise_exception=True)

# spare_receive - Receive stock
@permission_required('core.change_spares', raise_exception=True)

# spare_delete - Delete items
@permission_required('core.delete_spares', raise_exception=True)
```

**If user doesn't have permission:**
- Returns 403 Forbidden
- Shows permission denied error
- No unauthorized access possible

---

## 👥 User Assignment Examples

### Example 1: Warehouse Manager

**Role:** Full inventory control

**Assign to:**
- ✓ Inventory Controller group

**Can do:**
- Receive deliveries
- Issue parts
- Add new items
- Adjust quantities
- Delete obsolete items

### Example 2: Maintenance Engineer

**Role:** Check parts availability for maintenance

**Assign to:**
- ✓ Engineering group

**Can do:**
- View all items
- Filter by machine
- View transaction history
- Check stock levels
- Plan maintenance

**Cannot:**
- Issue parts themselves
- Add/edit items

### Example 3: Production Manager

**Role:** Monitor inventory and generate reports

**Assign to:**
- ✓ Management group

**Can do:**
- View all items
- Run reports
- View transaction history
- Monitor stock levels

**Cannot:**
- Modify inventory
- Issue/receive stock

### Example 4: Production Operator

**Role:** No inventory access

**Assign to:**
- No inventory groups

**Result:**
- Cannot access inventory page
- Shows "Access Denied"

---

## 🧪 Testing Permissions

### Create Test Users:

```bash
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

# Create test users
inv_user = User.objects.create_user('inv_controller', password='test123')
eng_user = User.objects.create_user('engineer', password='test123')
mgmt_user = User.objects.create_user('manager', password='test123')
other_user = User.objects.create_user('operator', password='test123')

# Assign to groups
inv_controller = Group.objects.get(name='Inventory Controller')
engineering = Group.objects.get(name='Engineering')
management = Group.objects.get(name='Management')

inv_user.groups.add(inv_controller)
eng_user.groups.add(engineering)
mgmt_user.groups.add(management)
# other_user - no groups

print("✓ Test users created:")
print("  inv_controller / test123 - Full access")
print("  engineer / test123 - View only")
print("  manager / test123 - View only")
print("  operator / test123 - No access")
```

### Test Each User:

**Login as inv_controller:**
```
✓ See "Add Item" button
✓ See "Receive Stock" buttons
✓ See "Issue Item" buttons
✓ See "Edit" icons
✓ All forms work
```

**Login as engineer:**
```
✓ See all items
✓ See "View Only" badge
✗ No "Add Item" button
✗ No "Receive/Issue" buttons
✗ No "Edit" icons
✓ Can view history
```

**Login as manager:**
```
Same as engineer - view only
```

**Login as operator:**
```
✗ Access Denied page
```

---

## 🔄 Changing User Permissions

### Add User to Inventory Controller:
```
Django Admin → Users → Select user → Groups → Add "Inventory Controller" → Save
```

### Remove User from Group:
```
Django Admin → Users → Select user → Groups → Remove group → Save
```

### Bulk Assignment:
```
Django Admin → Groups → "Inventory Controller" → Choose users → Save
```

---

## 🎨 Visual Indicators

### Inventory Controller:
```
┌────────────────────────────┐
│ Inventory Management       │
│                            │
│ [+ Add Item] [Export]      │
└────────────────────────────┘
```

### Engineering/Management:
```
┌────────────────────────────┐
│ Inventory Management       │
│ [View Only]                │
│ [Export]                   │
└────────────────────────────┘
```

### Spare Card - Controller:
```
┌──────────────┐
│ [👁️] [✏️]   │ ← Both icons
│ Ball Bearing │
│ [+Receive]   │ ← Green button
│ [-Issue]     │ ← Yellow button
│ [📜History]  │ ← Blue button
└──────────────┘
```

### Spare Card - Engineering/Management:
```
┌──────────────┐
│ [👁️]        │ ← Only view icon
│ Ball Bearing │
│ ℹ️ View-only │ ← Info message
│ [📜History]  │ ← Only history button
└──────────────┘
```

---

## 📊 Permission Enforcement

### Template Level (UI):
```django
{% if perms.core.add_spares %}
  <button>Add Item</button>
{% endif %}

{% if perms.core.change_spares %}
  <button>Receive Stock</button>
  <button>Issue Item</button>
  <button>Edit</button>
{% endif %}

<!-- Everyone with view permission -->
{% if perms.core.view_spares %}
  <button>History</button>
{% endif %}
```

### View Level (Backend):
```python
@permission_required('core.view_spares', raise_exception=True)
def spare_view(request):
    # View items
    
@permission_required('core.add_spares', raise_exception=True)
def spare_add(request):
    # Add items
    
@permission_required('core.change_spares', raise_exception=True)
def spare_issue(request, pk):
    # Issue stock
    
@permission_required('core.change_spares', raise_exception=True)
def spare_receive(request, pk):
    # Receive stock
```

---

## 🔍 Permission Checking

### In Templates:
```django
{% if perms.core.view_spares %}
  <!-- User can view -->
{% endif %}

{% if perms.core.change_spares %}
  <!-- User can modify -->
{% endif %}

{% if not perms.core.change_spares %}
  <!-- User is read-only -->
  <span class="badge">View Only</span>
{% endif %}
```

### In Python Code:
```python
# Check if user has permission
if request.user.has_perm('core.view_spares'):
    # Allow view
    
if request.user.has_perm('core.change_spares'):
    # Allow edit/issue/receive
```

---

## 🎯 Use Cases

### Use Case 1: Warehouse Staff

**Scenario:** Daily receiving and issuing of parts

**Setup:**
- Assign to: **Inventory Controller**
- Access level: Full

**Daily workflow:**
- Morning: Receive deliveries (PO tracking)
- During day: Issue parts to production
- Evening: Adjust counts, generate reports

### Use Case 2: Maintenance Engineers

**Scenario:** Check parts before scheduling maintenance

**Setup:**
- Assign to: **Engineering**
- Access level: View only

**Workflow:**
- Filter by machine (e.g., M-100)
- Check if all parts in stock
- View transaction history
- Plan maintenance when parts available
- Request parts from inventory controller

### Use Case 3: Department Head

**Scenario:** Monitor inventory levels and costs

**Setup:**
- Assign to: **Management**
- Access level: View only

**Workflow:**
- View all inventory
- Filter by status (low stock)
- Check transaction history
- Review monthly usage reports
- Approve purchase requests

### Use Case 4: Production Operator

**Scenario:** No inventory access needed

**Setup:**
- No groups assigned
- Access level: None

**Result:**
- Cannot access inventory page
- Access denied

---

## 🛡️ Security Features

### Backend Protection:
✅ All views check permissions  
✅ Raises 403 if unauthorized  
✅ No way to bypass via URL manipulation  

### Frontend Protection:
✅ Buttons hidden if no permission  
✅ Visual indicators (View Only badge)  
✅ Better UX - no confusing buttons  

### Audit Trail:
✅ Every transaction logs the user  
✅ Can track who did what  
✅ Accountability enforced  

---

## 📝 Permission Details

### Django Permissions Created:

```
core | spares | Can view spares
core | spares | Can add spares
core | spares | Can change spares
core | spares | Can delete spares
core | spare transaction | Can view spare transaction
```

### Group Assignments:

**Inventory Controller:**
- `core.view_spares`
- `core.add_spares`
- `core.change_spares`
- `core.delete_spares`
- `core.view_sparetransaction`

**Engineering:**
- `core.view_spares`
- `core.view_sparetransaction`

**Management:**
- `core.view_spares`
- `core.view_sparetransaction`

---

## 🔄 Permission Workflow

### Request Flow:

```
User → Access /home/spares
  ↓
Check: has 'core.view_spares'?
  ↓
Yes → Show page
  ↓
Check: has 'core.change_spares'?
  ↓
Yes → Show all buttons (Controller)
No → Show view-only (Engineering/Management)
```

### Action Flow:

```
User → Click "Issue Item"
  ↓
Check: has 'core.change_spares'?
  ↓
Yes → Process issue
No → 403 Forbidden
```

---

## 🧪 Testing Checklist

- [ ] Run `python manage.py setup_inventory_groups`
- [ ] Assign test user to Inventory Controller
- [ ] Login and verify full access
- [ ] Assign test user to Engineering
- [ ] Login and verify view-only
- [ ] Test unauthorized user gets denied
- [ ] Verify buttons show/hide correctly
- [ ] Test backend returns 403 for unauthorized
- [ ] Check transaction logs show correct users

---

## 📖 Quick Commands

### Setup Groups:
```bash
python manage.py setup_inventory_groups
```

### Create Test User:
```bash
python manage.py createsuperuser
# Then assign to group in admin
```

### Check User Permissions:
```bash
python manage.py shell
```
```python
from django.contrib.auth import get_user_model
User = get_user_model()

user = User.objects.get(username='john')
print(f"Can view: {user.has_perm('core.view_spares')}")
print(f"Can change: {user.has_perm('core.change_spares')}")
print(f"Groups: {[g.name for g in user.groups.all()]}")
```

---

## 🎊 Summary

✅ **3 Groups Created:** Inventory Controller, Engineering, Management  
✅ **Permissions Configured:** Full vs. View-only  
✅ **UI Updated:** Buttons show/hide based on permissions  
✅ **Backend Protected:** All views check permissions  
✅ **Visual Indicators:** "View Only" badges  
✅ **Audit Trail:** User accountability  

**Your inventory system now has proper access control!**

Run the setup command and assign users to groups:
```bash
python manage.py setup_inventory_groups
```

Then go to Django admin to assign users! 🚀

