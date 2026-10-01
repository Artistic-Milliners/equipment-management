# Ticket Filtering System by User Role

## Overview
The complaint/ticket list view has been updated to show role-specific tickets, ensuring users only see tickets relevant to their responsibilities.

## Ticket Status Flow
Understanding the status progression:
1. **PENDING** → Initial status when ticket is created
2. **REVIEWED** → Engineer has reviewed, awaiting management approval
3. **APPROVED** → Management/HOD approved the review
4. **REJECTED** → Management/HOD rejected the review
5. **RESOLVED** → Issue resolved, waiting for user confirmation
6. **AWAITING_DOCUMENTATION** → User confirmed resolution, engineer needs to document
7. **UNDER_OBSERVATION** → Issue being monitored
8. **CLOSED** → Fully completed and closed

## Role-Based Filtering

### 🔵 **Approvers** (Management/HOD)
**Permission:** `core.can_approve_complaint` or member of 'Approvers' group

**Can See:**
- ✅ **REVIEWED** - Tickets reviewed by engineers, awaiting approval *(primary focus)*
- ✅ **APPROVED** - Tickets they've already approved *(for reference)*
- ✅ **REJECTED** - Tickets they've rejected *(for reference)*

**Purpose:** Approvers focus on reviewing and approving/rejecting engineer assessments.

### 🟢 **Engineers**
**Permission:** `core.can_review_complaint` or member of 'Engineers' group

**Can See:**
- ✅ **PENDING** - New tickets that need their review
- ✅ **APPROVED** - Tickets approved by management, ready to work on
- ✅ **AWAITING_DOCUMENTATION** - Resolved tickets needing documentation
- ✅ **RESOLVED** - Successfully resolved tickets
- ✅ **UNDER_OBSERVATION** - Tickets being monitored

**Purpose:** Engineers handle the technical assessment, resolution, and documentation.

### 🟡 **Regular Users**
**No special permissions**

**Can See:**
- ✅ **All their own tickets** - Regardless of status

**Purpose:** Users can track their submitted tickets through the entire lifecycle.

## Code Implementation

### File: `maintenance/views.py`

```python
@login_required
def view_complains(request):
    user = request.user.id
    emp = Employee.objects.get(user=user)
    
    # Check user roles
    is_approver = request.user.has_perm('core.can_approve_complaint') or \
                  request.user.groups.filter(name='Approvers').exists()
    is_engineer = request.user.has_perm('core.can_review_complaint') or \
                  request.user.groups.filter(name='Engineers').exists()
    
    # Filter tickets based on user role
    if is_approver:
        # Approvers see REVIEWED, APPROVED, REJECTED tickets
        issue_list = MachineIssue.objects.filter(
            status__in=['REVIEWED', 'APPROVED', 'REJECTED']
        ).order_by('-date_time')
        
    elif is_engineer:
        # Engineers see PENDING, APPROVED, AWAITING_DOCUMENTATION, etc.
        issue_list = MachineIssue.objects.filter(
            status__in=['PENDING', 'APPROVED', 'AWAITING_DOCUMENTATION', 
                       'RESOLVED', 'UNDER_OBSERVATION']
        ).order_by('-date_time')
        
    else:
        # Regular users see only their own tickets
        issue_list = MachineIssue.objects.filter(
            user=emp
        ).order_by('-date_time')
    
    return render(request, "maintenance/complain-view.html", {
        'issue_list': issue_list, 
        'emp': emp,
        'is_approver': is_approver,
        'is_engineer': is_engineer
    })
```

## Benefits

### ✅ **Reduced Clutter**
- Each role sees only tickets relevant to their work
- No overwhelming list of all tickets in the system

### ✅ **Clear Responsibilities**
- Approvers focus on pending approvals
- Engineers focus on technical work
- Users track their own submissions

### ✅ **Better Workflow**
- Tickets requiring action are immediately visible
- Historical decisions (approved/rejected) remain accessible
- Logical progression through the system

### ✅ **Improved Security**
- Users can't see other people's tickets (unless they're approvers/engineers)
- Role-based access control enforced at the view level

## Example Scenarios

### Scenario 1: New Ticket Flow
1. **User** creates ticket → Status: `PENDING`
2. **Engineer** sees it in their list → Reviews it → Status: `REVIEWED`
3. **Approver** sees it in their list → Approves it → Status: `APPROVED`
4. **Engineer** sees it again → Works on it → Status: `RESOLVED`
5. **User** sees it → Confirms resolution → Status: `AWAITING_DOCUMENTATION`
6. **Engineer** documents → Status: `CLOSED`

### Scenario 2: Rejected Ticket
1. **Engineer** reviews → Status: `REVIEWED`
2. **Approver** rejects → Status: `REJECTED`
3. Ticket remains in **Approver's** view for reference
4. No longer appears in **Engineer's** active queue

## User Assignment

To assign users to roles, run:

```bash
# Set up groups and permissions
python manage.py setup_approval_groups

# Then in Django Admin or shell:
from django.contrib.auth.models import User, Group

# Add user to Approvers group
user = User.objects.get(username='manager_username')
approvers_group = Group.objects.get(name='Approvers')
user.groups.add(approvers_group)

# Add user to Engineers group
user = User.objects.get(username='engineer_username')
engineers_group = Group.objects.get(name='Engineers')
user.groups.add(engineers_group)
```

## Testing

### Test as Approver:
1. Login as user with Approver permissions
2. Navigate to complaint list
3. Should only see REVIEWED, APPROVED, REJECTED tickets
4. Verify you can approve/reject REVIEWED tickets

### Test as Engineer:
1. Login as user with Engineer permissions
2. Navigate to complaint list
3. Should see PENDING, APPROVED, AWAITING_DOCUMENTATION, etc.
4. Verify you can review PENDING tickets

### Test as Regular User:
1. Login as regular user
2. Navigate to complaint list
3. Should only see your own tickets (all statuses)
4. Verify you can create new tickets

## Notes

- Multiple roles are supported (a user can be both Engineer and Approver)
- If a user has multiple roles, the most privileged role's filter applies (Approver > Engineer > Regular)
- All queries are ordered by date (newest first)
- The filtering happens at the database level for efficiency

---

**Result:** Clean, role-based ticket management that shows each user exactly what they need to see! 🎯


