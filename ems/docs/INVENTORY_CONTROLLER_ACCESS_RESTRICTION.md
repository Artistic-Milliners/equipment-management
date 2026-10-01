# Inventory Controller Access Restriction

## 🔒 Overview

Users in the **Inventory Controller** group are restricted to **ONLY** the Inventory Management section. They cannot access any other part of the EMS system.

---

## ✅ What's Implemented

### 1. **UI Restriction (Frontend)**
- Sidebar shows **ONLY** the Inventory link for Inventory Controllers
- All other menu items are hidden:
  - ❌ Dashboard
  - ❌ New Complaint
  - ❌ Ticket List
  - ❌ Closed Archive
  - ❌ Add Machine
  - ❌ Units
  - ❌ Users
  - ❌ Equipment Tree
- ✅ Only "Inventory" link is visible

### 2. **Backend Restriction (Security)**
- All non-inventory views check if user is Inventory Controller
- If yes, they are redirected back to Inventory page with a message
- Protected views include:
  - `home` - Dashboard
  - `machine_detail` - Machine details
  - `add_machine` - Add new machine
  - `edit_machine` - Edit machine
  - `update_machine` - Update machine
  - `delete_machine` - Delete machine
  - `InitiateComplainView` - Create new complaint
  - `ListUsers` - View users list
  - `DetailUserView` - View user details
  - `CreateUnitView` - Create new unit
  - `ListUnitView` - View units list

---

## 🎯 User Experience

### **Inventory Controller User Login:**

1. **Logs in** → Automatically redirected to `/home/spares` (Inventory page)
2. **Sees sidebar** → Only "Inventory" link visible
3. **Tries to access other URLs directly** → Automatically redirected back to Inventory with warning message

**Example:**
```
User tries: http://127.0.0.1:8000/home
↓
System detects: User is in "Inventory Controller" group
↓
Action: Redirect to http://127.0.0.1:8000/home/spares
↓
Message: "You only have access to the Inventory Management section."
```

---

## 📁 Files Modified

### 1. **Template Tags**
**File:** `User/templatetags/user_tags.py`
```python
@register.filter(name='is_inventory_controller')
def is_inventory_controller(user):
    """Check if user is in Inventory Controller group"""
    if not user.is_authenticated:
        return False
    return user.groups.filter(name='Inventory Controller').exists()
```

### 2. **Base Template**
**File:** `templates/index.html`
```django
{% load user_tags %}

{% if user|is_inventory_controller %}
    <!-- Show only Inventory link -->
    <a href="{% url 'User:spares' %}">Inventory</a>
{% else %}
    <!-- Show full menu -->
    ...all other links...
{% endif %}
```

### 3. **Decorator**
**File:** `User/decorators.py`
```python
def inventory_controller_restricted(view_func):
    """
    Prevent Inventory Controller users from accessing non-inventory views.
    Redirects them to spares page with a message.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            user_groups = request.user.groups.values_list('name', flat=True)
            if 'Inventory Controller' in user_groups:
                messages.warning(
                    request, 
                    'You only have access to the Inventory Management section.'
                )
                return redirect('User:spares')
        return view_func(request, *args, **kwargs)
    return wrapper
```

### 4. **Views Protected**
**File:** `User/views.py`

**Function-based views:**
```python
@login_required
@inventory_controller_restricted
def home(request):
    ...

@inventory_controller_restricted
def machine_detail(request, pk):
    ...

@permission_required('core.machine_create_perm', raise_exception=True)
@inventory_controller_restricted
def add_machine(request):
    ...

@permission_required('core.change_machines', raise_exception=True)
@inventory_controller_restricted
def edit_machine(request, pk):
    ...

@permission_required('core.change_machines', raise_exception=True)
@inventory_controller_restricted
def update_machine(request, pk):
    ...

@permission_required('core.delete_machines', raise_exception=True)
@inventory_controller_restricted
def delete_machine(request, pk):
    ...
```

**Class-based views:**
```python
class InitiateComplainView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.groups.filter(name='Inventory Controller').exists():
            messages.warning(request, 'You only have access to the Inventory Management section.')
            return redirect('User:spares')
        return super().dispatch(request, *args, **kwargs)

class ListUsers(ListView):
    def dispatch(self, request, *args, **kwargs):
        # Same check as above
        ...

class DetailUserView(DetailView):
    def dispatch(self, request, *args, **kwargs):
        # Same check as above
        ...

class CreateUnitView(CreateView):
    def dispatch(self, request, *args, **kwargs):
        # Same check as above
        ...

class ListUnitView(ListView):
    def dispatch(self, request, *args, **kwargs):
        # Same check as above
        ...
```

---

## 🔐 Security Layers

### Layer 1: UI (UX)
- Sidebar conditionally renders based on group
- Users don't see links they can't access
- Better user experience

### Layer 2: Backend (Security)
- All views check group membership
- Redirect with warning message if unauthorized
- Prevents URL manipulation bypass

### Layer 3: Permissions (Django)
- Existing permission decorators still work
- `@permission_required` checks still apply
- Multi-level security

---

## 🎯 Access Matrix

| Section | Inventory Controller | Engineering | Management | Other Users |
|---------|---------------------|-------------|------------|-------------|
| **Dashboard** | ❌ | ✅ | ✅ | ✅* |
| **New Complaint** | ❌ | ✅ | ✅ | ✅* |
| **Ticket List** | ❌ | ✅ | ✅ | ✅* |
| **Inventory** | ✅ Full Access | ✅ View Only | ✅ View Only | ❌ |
| **Add Machine** | ❌ | ✅* | ✅* | ✅* |
| **Units** | ❌ | ✅* | ✅* | ✅* |
| **Users** | ❌ | ✅* | ✅* | ✅* |
| **Equipment** | ❌ | ✅* | ✅* | ✅* |

*Subject to other permission checks

---

## 📊 User Flow Diagrams

### Inventory Controller Login:
```
┌──────────────┐
│ Login        │
└──────┬───────┘
       │
       ▼
┌──────────────────────────┐
│ Check User Groups        │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Is "Inventory Controller"│
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Redirect to /home/spares │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Show ONLY Inventory Menu │
└──────────────────────────┘
```

### Inventory Controller Tries Other Page:
```
┌────────────────────────────┐
│ Try to access /home        │
└──────┬─────────────────────┘
       │
       ▼
┌────────────────────────────┐
│ @inventory_controller_     │
│ restricted decorator runs  │
└──────┬─────────────────────┘
       │
       ▼
┌────────────────────────────┐
│ Check if Inventory         │
│ Controller?                │
└──────┬─────────────────────┘
       │ YES
       ▼
┌────────────────────────────┐
│ Show warning message       │
└──────┬─────────────────────┘
       │
       ▼
┌────────────────────────────┐
│ Redirect to /home/spares   │
└────────────────────────────┘
```

### Other Users (Normal Flow):
```
┌──────────────┐
│ Login        │
└──────┬───────┘
       │
       ▼
┌──────────────────────────┐
│ Check User Groups        │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ NOT Inventory Controller │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Show FULL Menu           │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Access all pages         │
│ (subject to other perms) │
└──────────────────────────┘
```

---

## 🧪 Testing

### Test Scenario 1: Login as Inventory Controller
```
1. Login as user in "Inventory Controller" group
2. Check sidebar → Should show ONLY "Inventory"
3. Try to access /home → Should redirect to /home/spares
4. Try to access /home/users → Should redirect to /home/spares
5. Try to access /home/unit → Should redirect to /home/spares
```

### Test Scenario 2: Login as Engineering
```
1. Login as user in "Engineering" group
2. Check sidebar → Should show FULL menu
3. Can access /home → YES
4. Can access /home/users → YES (if has permission)
5. Can access /home/spares → YES (view only)
```

### Test Scenario 3: Login as Management
```
1. Login as user in "Management" group
2. Check sidebar → Should show FULL menu
3. Can access /home → YES
4. Can access /home/spares → YES (view only)
5. Can view reports → YES
```

### Test Scenario 4: URL Bypass Attempt
```
Inventory Controller tries:
1. /home → Redirected to /home/spares ✅
2. /home/machine/1 → Redirected to /home/spares ✅
3. /add → Redirected to /home/spares ✅
4. /home/complain → Redirected to /home/spares ✅
5. /home/users → Redirected to /home/spares ✅
```

---

## 🎨 UI Indicators

### Inventory Controller Sidebar:
```
┌─────────────────────────┐
│ 📦 EMS                  │
├─────────────────────────┤
│ 📦 Inventory           │  ← Only visible item
└─────────────────────────┘
```

### Other Users Sidebar:
```
┌─────────────────────────┐
│ 📦 EMS                  │
├─────────────────────────┤
│ 🏠 Dashboard           │
│ ➕ New Complaint        │
│ 🎫 Ticket List          │
│ 📦 Inventory            │
│ ➕ Add Machine          │
│ 🏢 Units                │
│ 👥 Users                │
│ ⚙️ Equipment            │
└─────────────────────────┘
```

---

## 🚨 Important Notes

### 1. **Inventory Access is NOT Blocked**
- Inventory Controllers CAN access `/home/spares`
- They have FULL access to inventory features:
  - Add items
  - Receive stock
  - Issue stock
  - Edit items
  - View history

### 2. **Other Groups Can Still Access Inventory**
- Engineering → View only
- Management → View only
- Inventory Controller → Full access

### 3. **Superusers Bypass All Restrictions**
- Django superusers can access everything
- They are not affected by these restrictions

### 4. **Group Name is Case-Sensitive**
- Must be exactly: `Inventory Controller`
- With capital I and C
- With space in between

---

## ⚙️ Configuration

### Create Inventory Controller Group:
```bash
python manage.py setup_inventory_groups
```

### Assign User to Group:
```
1. Django Admin → Groups
2. Click "Inventory Controller"
3. Add users
4. Save
```

### Verify User is in Group:
```bash
python manage.py shell
```
```python
from django.contrib.auth import get_user_model
User = get_user_model()

user = User.objects.get(username='john')
print(user.groups.all())  # Should show "Inventory Controller"
```

---

## 🔄 How It Works

### Template Level:
```django
{% load user_tags %}

{% if user|is_inventory_controller %}
    <!-- Show limited menu -->
{% else %}
    <!-- Show full menu -->
{% endif %}
```

### View Level:
```python
@inventory_controller_restricted
def my_view(request):
    # If user is Inventory Controller, redirects before reaching here
    # Otherwise, continues normally
    ...
```

### Class-Based View:
```python
class MyView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.groups.filter(name='Inventory Controller').exists():
            return redirect('User:spares')
        return super().dispatch(request, *args, **kwargs)
```

---

## 📝 Summary

✅ **UI Restriction:** Sidebar shows only Inventory link  
✅ **Backend Security:** All non-inventory views blocked  
✅ **User Messages:** Clear warning when trying to access restricted areas  
✅ **Inventory Access:** Full inventory features available  
✅ **Other Groups:** Not affected, have normal access  

**Inventory Controllers are now locked to ONLY the Inventory Management section!** 🔒

