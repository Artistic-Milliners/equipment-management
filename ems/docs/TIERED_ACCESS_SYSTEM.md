# Tiered Access Control System

## Overview
The EMS application now implements a comprehensive tiered access control system that provides different levels of access based on user roles and permissions.

## Access Levels

### 1. **All Users** (No special group required)
**What they can access:**
- ✅ Home page and dashboard
- ✅ Raise complaints (`/home/complain`)
- ✅ View ticket information (only for their department's machines)
- ✅ Basic navigation and user profile

**What they CANNOT access:**
- ❌ Inventory management
- ❌ Machine management (add/edit/delete)
- ❌ Unit management
- ❌ User management

### 2. **Engineering Team** (Engineering Group)
**Additional permissions beyond all users:**
- ✅ Inventory management (`/home/spares`)
- ✅ Add, edit, delete spare parts
- ✅ Issue spare parts
- ✅ View inventory reports

**What they CANNOT access:**
- ❌ Machine management (add/edit/delete)
- ❌ Unit management
- ❌ User management

### 3. **Management Team** (Management Group)
**Additional permissions beyond all users:**
- ✅ Machine management (add/edit/delete machines)
- ✅ Unit management (add/edit/delete units)
- ✅ User management (add/edit/delete users)
- ✅ All management tools

**What they CANNOT access:**
- ❌ Inventory management (unless also in Engineering group)

## Implementation Details

### Groups and Permissions

#### Engineering Group
- **Group Name:** `Engineering`
- **Permissions:**
  - `core.view_spares` - Can view inventory items
  - `core.add_spares` - Can add inventory items
  - `core.change_spares` - Can change inventory items
  - `core.delete_spares` - Can delete inventory items

#### Management Group
- **Group Name:** `Management`
- **Permissions:**
  - `core.view_machines` - Can view machines
  - `core.add_machines` - Can add machines
  - `core.change_machines` - Can change machines
  - `core.delete_machines` - Can delete machines
  - `core.view_unit` - Can view units
  - `core.add_unit` - Can add units
  - `core.change_unit` - Can change units
  - `core.delete_unit` - Can delete units
  - `core.view_employee` - Can view employees
  - `core.add_employee` - Can add employees
  - `core.change_employee` - Can change employees
  - `core.delete_employee` - Can delete employees

### View-Level Protection
All management views are protected with permission checks:

```python
class ListUsers(ListView):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm('core.view_employee'):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
```

### Template-Level Protection
The home template shows different sections based on user permissions:

```html
<!-- Engineering Tools (Inventory Management) -->
{% if user.has_perm('core.view_spares') %}
    <!-- Inventory management tools -->
{% endif %}

<!-- Management Tools (Machines, Units, Users) -->
{% if user.has_perm('core.add_machines') or user.has_perm('core.view_unit') or user.has_perm('core.view_employee') %}
    <!-- Management tools -->
{% endif %}
```

## User Interface Changes

### Home Page Layout
1. **Quick Actions Section** - Available to all users
   - New Complaint
   - Ticket List
   - Inventory (if user has inventory permissions)

2. **Engineering Tools Section** - Only visible to Engineering group
   - Inventory Management card with warning color theme

3. **Management Tools Section** - Only visible to Management group
   - Machine Management (blue theme)
   - Unit Management (info theme)
   - User Management (success theme)
   - Reports (secondary theme)

### Visual Indicators
- **Color-coded sections** for different access levels
- **Descriptive text** explaining what each tool does
- **Icons** that clearly represent each function
- **Conditional visibility** based on permissions

## Setup Commands

### 1. Set up Tiered Permissions
```bash
python manage.py setup_tiered_permissions
```

### 2. Add User to Engineering Group
```bash
python manage.py shell -c "
from django.contrib.auth.models import Group
from core.models import CustomUser
group = Group.objects.get(name='Engineering')
user = CustomUser.objects.get(username='USERNAME')
group.user_set.add(user)
print(f'Added {user.username} to Engineering group')
"
```

### 3. Add User to Management Group
```bash
python manage.py shell -c "
from django.contrib.auth.models import Group
from core.models import CustomUser
group = Group.objects.get(name='Management')
user = CustomUser.objects.get(username='USERNAME')
group.user_set.add(user)
print(f'Added {user.username} to Management group')
"
```

## Testing the System

### Test Users Created
1. **zohaib** - Has both Engineering and Management permissions
2. **testuser** - Regular user with no special permissions (password: testpass123)

### Test Scenarios

#### Scenario 1: Regular User (testuser)
- ✅ Should see home page with basic quick actions
- ✅ Should see "New Complaint" and "Ticket List" cards
- ❌ Should NOT see "Engineering Tools" section
- ❌ Should NOT see "Management Tools" section
- ❌ Should get 403 error when trying to access management URLs

#### Scenario 2: Engineering User
- ✅ Should see home page with basic quick actions
- ✅ Should see "Engineering Tools" section with inventory management
- ❌ Should NOT see "Management Tools" section
- ✅ Should be able to access inventory management
- ❌ Should get 403 error when trying to access machine/unit/user management

#### Scenario 3: Management User
- ✅ Should see home page with basic quick actions
- ❌ Should NOT see "Engineering Tools" section (unless also in Engineering group)
- ✅ Should see "Management Tools" section
- ✅ Should be able to access machine/unit/user management
- ❌ Should get 403 error when trying to access inventory management (unless also in Engineering group)

#### Scenario 4: Combined User (zohaib)
- ✅ Should see all sections
- ✅ Should have access to all management functions
- ✅ Should see both Engineering and Management tools

## Security Benefits

1. **Principle of Least Privilege**: Users only see what they need
2. **Defense in Depth**: Protection at multiple levels (view, template, API)
3. **Clear Separation of Concerns**: Different teams have different access levels
4. **Audit Trail**: Django's permission system provides built-in logging
5. **Scalable**: Easy to add new permissions and groups as needed

## Maintenance

### Adding New Management Tools
1. Add permission decorators to new views
2. Update template permission checks
3. Add permissions to appropriate groups
4. Test with different user permission levels

### Modifying Access Levels
1. Update group permissions
2. Update template permission checks
3. Update view permission decorators
4. Test changes thoroughly

This tiered access system ensures that users only see and can access the tools they need for their role, while maintaining security and providing a clean, intuitive user experience.

