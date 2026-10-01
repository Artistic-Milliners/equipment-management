# Complain View Empty List Fix

## Problem
The complain-view page was not showing any issues/tickets in the list, appearing completely empty.

## Root Causes Found

### 1. **Double Filtering** (Primary Issue)
The template had a restrictive filter on line 49 that was filtering tickets AGAIN after the view already filtered them:

**Old Code:**
```django
{% if issue.user.id == emp.id or issue.user.department == emp.department or issue.error_department == emp.department %}
```

This caused problems because:
- **Approvers** couldn't see tickets from other departments (even though they should approve all reviewed tickets)
- **Engineers** couldn't see tickets from other departments (even though they should work on all approved tickets)
- **If `emp` was None**, this would fail completely
- It conflicted with the role-based filtering we added in the view

### 2. **Template Structure Issue**
The if/endif structure was malformed with two `{% endif %}` tags, causing template rendering issues.

### 3. **No Debug Information**
There was no way to know why tickets weren't showing up - was it a permission issue, a filtering issue, or a data issue?

## Fixes Applied

### Fix 1: Removed Restrictive Template Filter

**Before:**
```django
{% for issue in issue_list %}
{% if issue.user.id == emp.id or issue.user.department == emp.department or issue.error_department == emp.department %}
    {# Show ticket #}
{% endif %}
{% endfor %}
```

**After:**
```django
{% if issue_list %}
{% for issue in issue_list %}
    {# Only hide production user's confirmed tickets #}
    {% if emp and emp.department and emp.department.dpt_type == 'PRODUCTION' and issue.user.id == emp.id and issue.status in 'AWAITING_DOCUMENTATION, APPROVED, CLOSED' %}
        {# Skip #}
    {% else %}
        {# Show ticket #}
    {% endif %}
{% empty %}
    {# No tickets message #}
{% endfor %}
{% else %}
    {# Account configuration error #}
{% endif %}
```

**Key Changes:**
- ✅ Removed the department/user matching filter
- ✅ Only keep the production-user-specific filter (to hide tickets they've already confirmed)
- ✅ Added safety checks (`emp and emp.department`) to prevent errors
- ✅ Trust the view-level filtering instead of double-filtering

### Fix 2: Enhanced Empty State Messages

Added role-specific messages when no tickets are found:

```django
{% if is_approver %}
    There are no tickets awaiting your approval at this time.
{% elif is_engineer %}
    There are no tickets requiring your attention at this time.
{% else %}
    You haven't created any tickets yet.
{% endif %}
```

Also added a separate message for account configuration issues when `issue_list` is None.

### Fix 3: Added Comprehensive Debug Output

Added detailed logging in `maintenance/views.py`:

```python
print(f"[ROLE] User: {username}, Found {count} tickets")
print(f"Employee: {emp.name if emp else 'None'}")
print(f"Department: {dept.name if dept else 'None'}")
print(f"Is Approver: {is_approver}")
print(f"Is Engineer: {is_engineer}")
print(f"Total issues in list: {count}")
```

This will help diagnose issues immediately.

## How the Fixed System Works

### Role-Based Filtering (View Level Only)

1. **Approvers** see:
   - ✅ REVIEWED (awaiting their approval)
   - ✅ APPROVED (for reference)
   - ✅ REJECTED (for reference)

2. **Engineers** see:
   - ✅ PENDING (needs review)
   - ✅ APPROVED (ready to work on)
   - ✅ AWAITING_DOCUMENTATION (needs documentation)
   - ✅ RESOLVED (successfully fixed)
   - ✅ UNDER_OBSERVATION (being monitored)

3. **Regular Users** see:
   - ✅ All their own tickets (any status)
   - ❌ Hidden: Their tickets in AWAITING_DOCUMENTATION/APPROVED/CLOSED if they're from production department (since they already confirmed them)

### No More Department Restrictions

Users can now see tickets from ANY department based on their role:
- **Approvers** see all tickets needing approval (regardless of department)
- **Engineers** see all tickets needing work (regardless of department)
- **Regular users** see only their own tickets

## Debugging Guide

When you visit the complain-view page now, **check your console/terminal** for output like this:

```
============================================================
COMPLAIN VIEW DEBUG
============================================================
User: raza.hussain
Employee: Raza Hussain
Department: general management
Is Approver: False
Is Engineer: False
Total issues in list: 5
First 3 tickets:
  - Ticket #1-2-3: PENDING - Machine not working properly
  - Ticket #1-3-4: RESOLVED - Fixed the issue
  - Ticket #2-1-5: UNDER_OBSERVATION - Monitoring the machine
============================================================
```

### If You See:

**"Total issues in list: 0"** 
- The user has no tickets (if regular user)
- No tickets match the role filter (if approver/engineer)
- The user's role isn't being detected properly

**"Employee: None"**
- The user account is not linked to an Employee record
- Need to run the fix from DEPARTMENT_CHANGE_TROUBLESHOOTING.md

**"Is Approver: False, Is Engineer: False"**
- User is a regular user (will only see their own tickets)
- If they should be approver/engineer, assign them to the proper group

**"[REGULAR USER] User: raza, Employee: Raza Hussain, Found 0 tickets"**
- The employee exists but has created no tickets yet
- Or the employee record is correct but was recently changed

## Quick Diagnostic Commands

Run in Django shell to check everything:

```bash
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
from core.models import Employee, MachineIssue, Department

User = get_user_model()

# Check user and employee
username = 'raza'  # Replace with actual username
user = User.objects.get(username=username)
print(f"User: {user.username}")

try:
    emp = Employee.objects.get(user=user)
    print(f"✓ Employee: {emp.name}")
    print(f"✓ Department: {emp.department}")
    
    # Check tickets
    tickets = MachineIssue.objects.filter(user=emp)
    print(f"✓ Tickets created: {tickets.count()}")
    for t in tickets[:3]:
        print(f"  - {t.ticket_num}: {t.status}")
        
except Employee.DoesNotExist:
    print("✗ No Employee record!")

# Check permissions
print(f"\nPermissions:")
print(f"Is Approver: {user.has_perm('core.can_approve_complaint')}")
print(f"Is Engineer: {user.has_perm('core.can_review_complaint')}")
print(f"Groups: {list(user.groups.values_list('name', flat=True))}")

# Check all tickets in system
all_tickets = MachineIssue.objects.all()
print(f"\nTotal tickets in system: {all_tickets.count()}")
print("Status breakdown:")
from django.db.models import Count
status_counts = all_tickets.values('status').annotate(count=Count('id'))
for s in status_counts:
    print(f"  {s['status']}: {s['count']}")
```

## Expected Behavior After Fix

### For Regular Users (like Raza):
1. ✅ Visit complain-view page
2. ✅ See all their own tickets
3. ✅ Tickets they've confirmed as resolved are hidden (if from production dept)
4. ✅ Can click "Create New Ticket" if none exist

### For Engineers:
1. ✅ Visit complain-view page
2. ✅ See all PENDING, APPROVED, AWAITING_DOCUMENTATION, RESOLVED, UNDER_OBSERVATION tickets
3. ✅ See tickets from ALL departments (not just their own)
4. ✅ Can take action on any ticket

### For Approvers:
1. ✅ Visit complain-view page
2. ✅ See all REVIEWED, APPROVED, REJECTED tickets
3. ✅ See tickets from ALL departments (not just their own)
4. ✅ Can approve/reject any reviewed ticket

## Testing Checklist

- [ ] Login as Raza (regular user)
- [ ] Visit `/complain-view/`
- [ ] Check console output for debug information
- [ ] Verify tickets show up (if any exist)
- [ ] Check that "Create New Ticket" button works
- [ ] Login as an Engineer
- [ ] Verify they see PENDING tickets from all departments
- [ ] Login as an Approver
- [ ] Verify they see REVIEWED tickets from all departments

---

**The complain-view page should now properly display tickets based on user roles without restrictive department filtering!** 🎉


