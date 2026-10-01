# User Acknowledgment System - Implementation Plan

## 🐛 Bug Fixed

**Issue**: Review form was setting status to RESOLVED and auto-redirecting to closing form

**Fix Applied** ([User/views.py:256-262](d:\Zohaib\webapps\ems\ems\User\views.py#L256)):
```python
# BEFORE (Bug):
issue.status = MachineIssue.STATUS_CHOICES[1][0]  # RESOLVED - Wrong!
return redirect('User:complain_closing', pk=issue.pk)  # Wrong redirect

# AFTER (Fixed):
issue.status = 'REVIEWED'  # Correct status
return redirect('maintenance:complain_list')  # Correct redirect
```

**Status**: ✅ Fixed

---

## 🎯 Desired Workflow (Your Description)

### Path 1: Quick Review → RESOLVED
```
User creates complaint
↓
Engineer: Quick Review → selects "RESOLVED"
↓
Status: RESOLVED
↓
[User Acknowledgment Required - TODO]
↓
User confirms: "Yes, it's fixed"
↓
Engineer can now access closing form
↓
Engineer documents and closes
```

### Path 2: Detailed Review → Engineer Decides
```
User creates complaint
↓
Engineer: Quick Review → selects "UNDER_OBSERVATION"
↓
Redirects to Review Form
↓
Engineer fills complete review
↓
Engineer chooses in form:
  ├─ "Issue Resolved"
  │   ↓
  │   Status: RESOLVED
  │   ↓
  │   [User Acknowledgment Required - TODO]
  │   ↓
  │   User confirms: "Yes, it's fixed"
  │   ↓
  │   Engineer can access closing form
  │
  └─ "Still Working On It"
      ↓
      Status: REVIEWED or UNDER_OBSERVATION
      ↓
      Approval workflow continues
      ↓
      Approver approves → APPROVED
      ↓
      Engineer works on it
```

---

## 📋 What Needs to Be Implemented

### 1. Add "Resolution Status" Field to Review Form

**File**: `maintenance/templates/maintenance/complain-form.html`

**Add new field in the form**:
```html
<!-- Add after problem nature or before submit button -->
<div class="form-group">
    <label for="resolution-status">Current Status</label>
    <select name="resolution-status" id="resolution-status" class="form-control" required>
        <option value="">-- Select Status --</option>
        <option value="RESOLVED">Issue Resolved - Ready for user confirmation</option>
        <option value="WORKING">Still Working - Needs approval/monitoring</option>
    </select>
    <small class="form-text text-muted">
        Select "Issue Resolved" if the problem is fixed and ready for user confirmation.
        Select "Still Working" if investigation/repair is ongoing.
    </small>
</div>
```

### 2. Update Review Form Processing

**File**: `User/views.py` - ComplainReviewView.post()

**Current code** (lines 194-262):
```python
def post(self, request, *args, **kwargs):
    # ... existing form processing ...

    # CURRENT (Line 256):
    issue.status = 'REVIEWED'
    issue.save()
    return redirect('maintenance:complain_list')
```

**Update to**:
```python
def post(self, request, *args, **kwargs):
    # ... existing form processing ...

    # NEW: Get engineer's resolution decision
    resolution_status = request.POST.get('resolution-status')

    if resolution_status == 'RESOLVED':
        # Engineer says issue is fixed
        issue.status = 'RESOLVED'
        issue.save()

        messages.success(request,
            f'Complaint {issue.ticket_num} marked as RESOLVED. '
            f'Waiting for user {issue.user.name} to confirm resolution.')

        # TODO: Send notification to user to acknowledge
        # send_resolution_notification(issue)

        return redirect('maintenance:complain_list')

    else:  # resolution_status == 'WORKING'
        # Engineer says still working on it
        issue.status = 'REVIEWED'  # For approval workflow
        issue.save()

        messages.success(request,
            f'Review completed for complaint {issue.ticket_num}. '
            f'Awaiting management approval.')

        return redirect('maintenance:complain_list')
```

### 3. Create User Acknowledgment System

#### 3.1 Add Acknowledgment Model

**File**: `core/models.py`

```python
class UserAcknowledgment(models.Model):
    """Track user acknowledgment of resolved complaints"""

    ACKNOWLEDGMENT_CHOICES = [
        ('CONFIRMED', 'Yes - Issue is fixed'),
        ('REJECTED', 'No - Issue still exists'),
    ]

    issue = models.OneToOneField(
        MachineIssue,
        on_delete=models.CASCADE,
        related_name='user_acknowledgment'
    )
    acknowledged_by = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        help_text="User who acknowledged the resolution"
    )
    acknowledgment = models.CharField(
        max_length=20,
        choices=ACKNOWLEDGMENT_CHOICES
    )
    comments = models.TextField(
        blank=True,
        null=True,
        help_text="User's comments about the resolution"
    )
    acknowledged_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.issue.ticket_num} - {self.get_acknowledgment_display()}"
```

**Create migration**:
```bash
python manage.py makemigrations
python manage.py migrate
```

#### 3.2 Create User Acknowledgment View

**File**: `User/views.py`

```python
class UserAcknowledgmentView(View):
    """Allow users to acknowledge if their complaint is actually resolved"""

    def get(self, request, pk):
        issue = MachineIssue.objects.get(pk=pk)

        # Check if user owns this complaint
        if issue.user.user != request.user:
            messages.error(request, "You can only acknowledge your own complaints")
            return redirect('User:home')

        # Check if already acknowledged
        if hasattr(issue, 'user_acknowledgment'):
            messages.info(request, "You have already acknowledged this complaint")
            return redirect('User:complain_track', pk=issue.pk)

        context = {
            'issue': issue,
        }
        return render(request, 'user/acknowledge_resolution.html', context)

    def post(self, request, pk):
        issue = MachineIssue.objects.get(pk=pk)

        # Verify ownership
        if issue.user.user != request.user:
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        acknowledgment_type = request.POST.get('acknowledgment')
        comments = request.POST.get('comments', '')

        # Create acknowledgment record
        UserAcknowledgment.objects.create(
            issue=issue,
            acknowledged_by=issue.user,
            acknowledgment=acknowledgment_type,
            comments=comments
        )

        if acknowledgment_type == 'CONFIRMED':
            # User confirms it's fixed
            # Engineer can now proceed to closing
            issue.status = 'AWAITING_DOCUMENTATION'
            issue.save()

            messages.success(request,
                f"Thank you for confirming. Complaint {issue.ticket_num} is now ready for final documentation.")

        else:  # acknowledgment_type == 'REJECTED'
            # User says it's not fixed
            # Send back to engineer
            issue.status = 'UNDER_OBSERVATION'
            issue.save()

            messages.warning(request,
                f"Complaint {issue.ticket_num} has been reopened. Engineer will review your feedback.")

        return redirect('User:complain_track', pk=issue.pk)
```

#### 3.3 Add URL Pattern

**File**: `User/urls.py`

```python
urlpatterns = [
    # ... existing patterns ...
    path('home/complain/<int:pk>/acknowledge',
         views.UserAcknowledgmentView.as_view(),
         name='acknowledge_resolution'),
]
```

#### 3.4 Create Acknowledgment Template

**File**: `User/templates/user/acknowledge_resolution.html`

```html
{% extends "base.html" %}

{% block main-body %}
<div class="container mt-4">
    <div class="card">
        <div class="card-header bg-primary text-white">
            <h4>Confirm Resolution - {{ issue.ticket_num }}</h4>
        </div>
        <div class="card-body">
            <div class="alert alert-info">
                <i class="fas fa-info-circle"></i>
                The engineer has marked this complaint as <strong>RESOLVED</strong>.
                Please confirm if the issue has been fixed.
            </div>

            <div class="complaint-details mb-4">
                <h5>Complaint Details:</h5>
                <table class="table">
                    <tr>
                        <th>Equipment:</th>
                        <td>{{ issue.equipment.name }}</td>
                    </tr>
                    <tr>
                        <th>Machine:</th>
                        <td>{{ issue.machine_id.name }}</td>
                    </tr>
                    <tr>
                        <th>Description:</th>
                        <td>{{ issue.description_user }}</td>
                    </tr>
                    <tr>
                        <th>Reported:</th>
                        <td>{{ issue.date_time }}</td>
                    </tr>
                </table>
            </div>

            <form method="post">
                {% csrf_token %}

                <div class="form-group">
                    <label><strong>Is the issue actually fixed?</strong></label>
                    <div class="mt-2">
                        <div class="custom-control custom-radio mb-2">
                            <input type="radio" id="confirm-yes" name="acknowledgment"
                                   value="CONFIRMED" class="custom-control-input" required>
                            <label class="custom-control-label" for="confirm-yes">
                                <i class="fas fa-check-circle text-success"></i>
                                <strong>Yes, the issue is fixed</strong> - Machine is working properly
                            </label>
                        </div>

                        <div class="custom-control custom-radio">
                            <input type="radio" id="confirm-no" name="acknowledgment"
                                   value="REJECTED" class="custom-control-input" required>
                            <label class="custom-control-label" for="confirm-no">
                                <i class="fas fa-times-circle text-danger"></i>
                                <strong>No, the issue still exists</strong> - Problem is not resolved
                            </label>
                        </div>
                    </div>
                </div>

                <div class="form-group">
                    <label for="comments">Comments (Optional)</label>
                    <textarea name="comments" id="comments" class="form-control"
                              rows="3" placeholder="Add any additional comments..."></textarea>
                </div>

                <div class="form-group">
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-check"></i> Submit Acknowledgment
                    </button>
                    <a href="{% url 'User:complain_track' issue.pk %}" class="btn btn-secondary">
                        <i class="fas fa-arrow-left"></i> Back to Complaint
                    </a>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}
```

### 4. Update Complaint List/Tracking to Show Acknowledgment Status

**File**: `User/templates/user/complain-tracking.html` or home page

**Add badge for RESOLVED complaints awaiting acknowledgment**:
```html
{% if issue.status == 'RESOLVED' and not issue.user_acknowledgment %}
    <div class="alert alert-warning">
        <i class="fas fa-exclamation-triangle"></i>
        <strong>Action Required:</strong> Please confirm if this issue is actually fixed.
        <a href="{% url 'User:acknowledge_resolution' issue.pk %}" class="btn btn-sm btn-warning ml-2">
            <i class="fas fa-check-circle"></i> Acknowledge Now
        </a>
    </div>
{% endif %}
```

### 5. Update Closing Form Access Logic

**File**: `User/views.py` - ComplainClosingView.get()

**Update validation** (around line 273):
```python
def get(self, request, pk):
    try:
        issue = MachineIssue.objects.get(pk=pk)

        # NEW: Check if user has acknowledged resolution
        if issue.status == 'RESOLVED':
            # Issue marked as resolved but not acknowledged yet
            if not hasattr(issue, 'user_acknowledgment'):
                messages.warning(request,
                    f'Complaint {issue.ticket_num} is waiting for user acknowledgment. '
                    f'Cannot proceed to closing until user confirms resolution.')
                return redirect('maintenance:complain_list')

            # User rejected the resolution
            if issue.user_acknowledgment.acknowledgment == 'REJECTED':
                messages.error(request,
                    f'User has not confirmed resolution. Please re-investigate.')
                return redirect('maintenance:complain_list')

        # Check if review exists
        try:
            review = MachineIssueReview.objects.get(issue=issue)
        except MachineIssueReview.DoesNotExist:
            messages.info(request, f'Please complete the engineer review form first')
            return redirect('User:review_complain', pk=issue.pk)

        # All checks passed, show closing form
        # ... rest of code ...
```

---

## 📊 Updated Status Flow

```
PENDING
  ↓
Quick Review / Detailed Review
  ↓
  ├─ RESOLVED (engineer marks as fixed)
  │   ↓
  │   [Wait for User Acknowledgment]
  │   ↓
  │   ┌─────────────┬─────────────┐
  │   │ Confirmed   │  Rejected   │
  │   │ (Yes fixed) │ (Not fixed) │
  │   ↓             ↓
  │   AWAITING_     UNDER_
  │   DOCUMENTATION OBSERVATION
  │   ↓             (re-work)
  │   Engineer
  │   Documents
  │   ↓
  │   CLOSED
  │
  └─ REVIEWED (still working)
      ↓
      Approval Flow
      ↓
      APPROVED/REJECTED
      ↓
      Engineer works
      ↓
      RESOLVED
      ↓
      [User Acknowledgment]
      ↓
      ...same as above
```

---

## ✅ Implementation Checklist

**Completed**:
- [x] Fix review form status bug (RESOLVED → REVIEWED)
- [x] Fix auto-redirect to closing form

**To Do**:
- [ ] Add "Resolution Status" field to review form template
- [ ] Update review form processing to handle engineer decision
- [ ] Create UserAcknowledgment model
- [ ] Create migration for UserAcknowledgment
- [ ] Create UserAcknowledgmentView
- [ ] Add URL pattern for acknowledgment
- [ ] Create acknowledge_resolution.html template
- [ ] Update complaint tracking to show acknowledgment prompt
- [ ] Update closing form access logic to check acknowledgment
- [ ] Add notification system (email/SMS) when resolved
- [ ] Test complete workflow end-to-end

---

## 🧪 Testing Plan

### Test Case 1: Quick Review → Resolved → User Confirms
1. Create complaint
2. Engineer: Quick Review → RESOLVED
3. User sees prompt: "Acknowledge resolution"
4. User clicks "Yes, fixed"
5. Status: AWAITING_DOCUMENTATION
6. Engineer can access closing form
7. Engineer closes → CLOSED

### Test Case 2: Quick Review → Resolved → User Rejects
1. Create complaint
2. Engineer: Quick Review → RESOLVED
3. User sees prompt: "Acknowledge resolution"
4. User clicks "No, not fixed"
5. Status: UNDER_OBSERVATION (back to engineer)
6. Engineer investigates again

### Test Case 3: Detailed Review → Engineer Says Resolved
1. Create complaint
2. Engineer: Quick Review → UNDER_OBSERVATION
3. Engineer fills detailed review
4. Engineer selects: "Issue Resolved"
5. Status: RESOLVED
6. User acknowledgment flow (same as Test Case 1)

### Test Case 4: Detailed Review → Engineer Says Working
1. Create complaint
2. Engineer: Quick Review → UNDER_OBSERVATION
3. Engineer fills detailed review
4. Engineer selects: "Still Working"
5. Status: REVIEWED
6. Approver approves → APPROVED
7. Engineer continues work

---

**Current Status**: Bug fixed, user acknowledgment system needs implementation
**Priority**: High - This is core to the workflow
**Estimated Work**: 4-6 hours for complete implementation

