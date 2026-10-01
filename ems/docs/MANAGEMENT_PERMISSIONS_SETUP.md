# Management Permissions Setup

## Overview
This document outlines the comprehensive permission system implemented for the EMS application's management tools. Only users in the Management group can add, edit, and delete items in the management tools.

## Permissions Structure

### Models with Management Permissions
1. **Spares** (Inventory Management)
   - `view_spares` - Can view inventory items
   - `add_spares` - Can add inventory items
   - `change_spares` - Can change inventory items
   - `delete_spares` - Can delete inventory items

2. **Machines** (Machine Management)
   - `view_machines` - Can view machines
   - `add_machines` - Can add machines
   - `change_machines` - Can change machines
   - `delete_machines` - Can delete machines

3. **Unit** (Unit Management)
   - `view_unit` - Can view units
   - `add_unit` - Can add units
   - `change_unit` - Can change units
   - `delete_unit` - Can delete units

4. **Employee** (User Management)
   - `view_employee` - Can view employees
   - `add_employee` - Can add employees
   - `change_employee` - Can change employees
   - `delete_employee` - Can delete employees

5. **Equipment** (Equipment Management)
   - `view_equipment` - Can view equipment
   - `add_equipment` - Can add equipment
   - `change_equipment` - Can change equipment
   - `delete_equipment` - Can delete equipment

6. **Department** (Department Management)
   - `view_department` - Can view departments
   - `add_department` - Can add departments
   - `change_department` - Can change departments
   - `delete_department` - Can delete departments

## Groups

### Management Group
- Contains all management permissions
- Users in this group can access all management tools
- Created automatically when running the setup command

### Engineering Management Group
- Contains inventory-specific permissions
- Users in this group can only manage inventory items
- Separate from general management permissions

## Implementation Details

### Views with Permission Decorators
All management views now have `@permission_required` decorators:

```python
@permission_required('core.add_machines', raise_exception=True)
def add_machine(request):
    # Machine creation logic

@permission_required('core.change_machines', raise_exception=True)
def edit_machine(request, pk):
    # Machine editing logic

@permission_required('core.delete_machines', raise_exception=True)
def delete_machine(request, pk):
    # Machine deletion logic
```

### Template Permission Checks
The home template now shows management tools only to users with appropriate permissions:

```html
{% if user.has_perm('core.add_machines') or user.has_perm('core.view_unit') or user.has_perm('core.view_employee') or user.has_perm('core.view_spares') %}
    <!-- Management Tools Section -->
{% endif %}
```

## Setup Commands

### 1. Set up Management Permissions
```bash
python manage.py setup_management_permissions
```

### 2. Set up Inventory Permissions (if needed)
```bash
python manage.py setup_inventory_permissions
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

## Access Control Features

### 1. View-Level Protection
- All management views require specific permissions
- Users without permissions get 403 Forbidden error
- Graceful error handling with custom error pages

### 2. Template-Level Protection
- Management tools only visible to authorized users
- Individual tool cards show based on specific permissions
- Clean UI that adapts to user permissions

### 3. API-Level Protection
- All AJAX endpoints protected with permissions
- JSON responses for permission errors
- Consistent error handling across the application

## Security Benefits

1. **Granular Control**: Each management function has its own permission
2. **Role-Based Access**: Users can be assigned to groups with specific permissions
3. **Defense in Depth**: Protection at view, template, and API levels
4. **Audit Trail**: Django's permission system provides built-in logging
5. **Scalable**: Easy to add new permissions and groups as needed

## Testing the Setup

1. **Login as a user without management permissions**:
   - Should not see management tools section
   - Should get 403 error when trying to access management URLs directly

2. **Login as a user with management permissions**:
   - Should see all management tools they have permissions for
   - Should be able to add, edit, and delete items
   - Should see appropriate error messages for actions they can't perform

3. **Test specific permissions**:
   - Users with only `view_spares` should see inventory but not be able to add/edit
   - Users with only `add_machines` should see add machine tool but not edit/delete tools

## Maintenance

### Adding New Management Tools
1. Add permission decorators to new views
2. Update template permission checks
3. Add permissions to Management group
4. Test with different user permission levels

### Modifying Permissions
1. Update permission decorators in views
2. Update template permission checks
3. Run management command to update group permissions
4. Test changes thoroughly

This permission system ensures that only authorized personnel can manage critical system components while maintaining a clean and intuitive user interface.

