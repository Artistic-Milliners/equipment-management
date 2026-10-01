# Department Change Troubleshooting Guide

## Issue
After moving Raza Hussain to the "general management" department, the ticket tracking page and other pages are not showing anything.

## Possible Causes

### 1. **Employee Record Not Linked to User Account**
When you moved Raza to a new department, the Employee record might have become disconnected from the User account.

### 2. **Missing Employee Record**
The user account might exist, but there's no corresponding Employee record in the database.

### 3. **Department Cascade Issue**
The Department foreign key has `on_delete=models.CASCADE`, which means if you deleted and recreated the department, it might have deleted related Employee records.

## Fixes Applied

I've added comprehensive error handling to prevent crashes and show helpful error messages:

### 1. **Home View** (`User/views.py`)
```python
try:
    employee = Employee.objects.get(user=request.user)
except Employee.DoesNotExist:
    employee = None
    # Shows all issues if no employee record
```

### 2. **Ticket List View** (`maintenance/views.py`)
```python
try:
    emp = Employee.objects.get(user=request.user)
except Employee.DoesNotExist:
    # Shows warning message and empty list
    messages.warning(request, "Your user account is not linked...")
```

### 3. **Tracking View** (`User/views.py`)
```python
try:
    issue = MachineIssue.objects.select_related(...).get(pk=pk)
    # Full error handling and debugging
except Exception as e:
    messages.error(request, f"An error occurred: {str(e)}")
```

## How to Diagnose the Issue

### Step 1: Check the Console/Terminal Output

When you access the tracking page now, look at your Django development server console. You should see output like:

```
============================================================
TRACKING PAGE DEBUG - Issue #X-X-X
============================================================
Issue ID: X
Status: PENDING
User: Raza Hussain
Equipment: Equipment Name
Machine: Machine Name
Department: general management
✓ Review found:
  - Reviewer: Engineer Name
  - Priority: HIGH
============================================================
```

**If you see:**
- "No user" - The issue's user field is not set correctly
- "No equipment" - The equipment relationship is broken
- "ERROR: Issue with pk=X does not exist" - The ticket doesn't exist
- "ERROR in ComplainTrackingView: ..." - There's a database or relationship error

### Step 2: Check for Warning Messages

When you log in as Raza and visit the ticket list page, look for this warning message:
> "Your user account is not linked to an employee record. Please contact the administrator."

If you see this, it means **the Employee record is missing or not linked**.

### Step 3: Verify Database Records

Run these commands in Django shell to check the data:

```bash
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
from core.models import Employee, Department

User = get_user_model()

# Check if user exists
user = User.objects.filter(username='raza_username').first()
print(f"User found: {user}")

# Check if employee record exists
if user:
    try:
        emp = Employee.objects.get(user=user)
        print(f"Employee found: {emp.name}")
        print(f"Department: {emp.department}")
    except Employee.DoesNotExist:
        print("ERROR: No Employee record for this user!")

# Check if department exists
dept = Department.objects.filter(name__icontains='general management').first()
print(f"Department found: {dept}")
```

## Solutions

### Solution 1: Recreate the Employee Record

If the Employee record is missing:

```python
from django.contrib.auth import get_user_model
from core.models import Employee, Department, Designation

User = get_user_model()

# Get the user
user = User.objects.get(username='raza_username')  # Replace with actual username

# Get the department
dept = Department.objects.get(name='general management')  # Exact name

# Create or update employee record
employee, created = Employee.objects.get_or_create(
    user=user,
    defaults={
        'name': 'Raza Hussain',
        'department': dept,
        'designation': None  # or a Designation object
    }
)

if not created:
    # Update existing employee
    employee.department = dept
    employee.save()
    
print(f"Employee record {'created' if created else 'updated'}")
```

### Solution 2: Fix Department Assignment

If the Employee record exists but department is None:

```python
from core.models import Employee, Department

# Get Raza's employee record
emp = Employee.objects.get(name='Raza Hussain')

# Get the department
dept = Department.objects.get(name='general management')

# Assign department
emp.department = dept
emp.save()

print("Department assigned successfully")
```

### Solution 3: Verify User Permissions

If Raza can't see tickets, check their permissions:

```python
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(username='raza_username')

# Check groups
print("Groups:", user.groups.all())

# Check permissions
print("Is Approver:", user.has_perm('core.can_approve_complaint'))
print("Is Engineer:", user.has_perm('core.can_review_complaint'))

# Check if is_employee flag is set
print("Is Employee:", user.is_employee)
```

### Solution 4: Verify Ticket Ownership

Check if Raza's tickets still reference the correct Employee:

```python
from core.models import MachineIssue, Employee

# Get Raza's employee record
emp = Employee.objects.get(name='Raza Hussain')

# Check tickets
tickets = MachineIssue.objects.filter(user=emp)
print(f"Found {tickets.count()} tickets for Raza")

for ticket in tickets:
    print(f"Ticket #{ticket.ticket_num}: {ticket.status}")
```

## Prevention Tips

### 1. **Use Department Update, Not Delete+Create**

When changing departments:
```python
# GOOD - Update existing department
dept = Department.objects.get(name='old_department')
dept.name = 'new_department'
dept.save()

# BAD - Delete and recreate (can break relationships)
# dept.delete()  # DON'T DO THIS
# Department.objects.create(name='new_department')
```

### 2. **Always Verify Employee Record After Changes**

After moving someone to a new department:
```python
emp = Employee.objects.get(name='User Name')
print(f"User: {emp.user.username}")
print(f"Department: {emp.department}")
print(f"Still linked: {emp.user is not None}")
```

### 3. **Use Django Admin to Change Departments**

The Django admin interface handles relationships properly:
1. Go to Django Admin: `http://localhost:8000/admin/`
2. Navigate to Employees
3. Click on the employee
4. Change the department dropdown
5. Save

This is safer than manual database changes.

## Quick Fix Command

If you need a quick fix, run this management command:

Create a file: `core/management/commands/fix_employee_links.py`

```python
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Employee

User = get_user_model()

class Command(BaseCommand):
    help = 'Fix employee-user relationships'

    def handle(self, *args, **options):
        # Find users without employee records
        users = User.objects.filter(is_employee=True)
        
        for user in users:
            try:
                emp = user.employee
                self.stdout.write(f"✓ {user.username} -> {emp.name}")
            except Employee.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f"✗ {user.username} has no employee record!"
                    )
                )
```

Run with:
```bash
python manage.py fix_employee_links
```

## Testing After Fix

1. **Login as Raza** - Should not see any errors
2. **Visit Home Page** - Should see statistics
3. **Visit Ticket List** - Should see Raza's tickets
4. **Click on a Ticket** - Should see full tracking page with all details
5. **Check Console** - Should see debug output without errors

---

**If the issue persists after trying these solutions, please:**
1. Share the console output from the debugging prints
2. Run the Django shell commands above and share the results
3. Check if there are any error messages in the browser or console

This will help identify the exact issue! 🔍


