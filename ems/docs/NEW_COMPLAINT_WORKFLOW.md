# EMS Complaint Workflow - Updated Design

## Overview

This document describes the **revised complaint workflow** that better captures the real essence of the application. The workflow separates quick issue resolution from formal documentation requirements.

---

## Workflow Diagram

```
User Creates Complaint (PENDING)
         ↓
Engineer Quick Review
         ↓
    ┌────┴────┐
    │         │
RESOLVED   UNDER_OBSERVATION
(quick fix)  (needs detailed review)
    │         │
    │         ↓
    │    Engineer Fills Full Review Form
    │         │
    │         ↓
    │    Status: REVIEWED
    │         │
    │         ↓
    │    Approver Reviews
    │         │
    │    ┌────┴────┐
    │    │         │
    │ APPROVED  REJECTED
    │    │
    └────┴─→ [User Acknowledges Resolution]
              ↓
         [Engineer Documents]
         (MachineIssueReview)
              ↓
         Engineer Closes
              ↓
         Status: CLOSED
```

---

## Detailed Workflow Steps

### 1. User Creates Complaint
- **Status**: PENDING
- **Action**: User reports machine issue with description, images, operational status
- **Result**: Complaint created and visible to engineering team

### 2. Engineer Quick Review
- **Who**: Engineer with "Engineers" group permission
- **URL**: `/complain-view/quick-review/{id}`
- **Options**:
  - **RESOLVED**: Issue fixed quickly (minor adjustment, reset, etc.)
  - **UNDER_OBSERVATION**: Requires detailed investigation

#### Option A: RESOLVED Path
- **Status**: PENDING → RESOLVED
- **What Happens**:
  - Engineer marks issue as resolved with quick comments
  - NO MachineIssueReview created yet
  - User is notified to acknowledge resolution
  - Engineer's comment added to description field

#### Option B: UNDER_OBSERVATION Path
- **Action**: Redirects to detailed review form
- **URL**: `/home/complain/review/{id}`
- **Status**: PENDING → UNDER_OBSERVATION → REVIEWED
- **What Happens**:
  - Engineer fills complete MachineIssueReview form:
    - Priority (HIGH/MODERATE/LOW)
    - Type (CORRECTIVE/PREVENTIVE/BREAKDOWN/CALIBRATION)
    - Problem Nature (ELECTRICAL/MECHANICAL/HYDRAULIC)
    - Assigned Department & Person
    - Malfunctioning parts
    - Detailed description
  - MachineIssueReview record created
  - Status changes to REVIEWED

### 3. Approver Review (For UNDER_OBSERVATION Path)
- **Who**: User with "Approvers" group permission
- **When**: After status is REVIEWED
- **URL**: `/complain-view/complain-detail/{id}`
- **Actions**:
  - Approve → Status: APPROVED
  - Reject → Status: REJECTED
- **Result**: MachineIssueApproval record created

### 4. User Acknowledges Resolution (TODO: To Be Implemented)
- **Who**: Original complaint creator
- **When**: After engineer marks as RESOLVED or APPROVED
- **Action**: User confirms if issue is actually fixed
- **Options**:
  - **Yes, fixed**: Proceeds to documentation phase
  - **No, still broken**: Returns to engineer for re-work
- **Status**: Remains RESOLVED/APPROVED (or goes back to PENDING)

### 5. Engineer Documents Resolution
- **Who**: Engineer
- **When**: After user acknowledges resolution
- **What**: If MachineIssueReview doesn't exist yet, engineer must create it
- **URL**: `/home/complain/review/{id}`
- **Why**: Formal documentation required for all closures
- **Fields Required**:
  - Complete review details
  - Problem analysis
  - Solution implemented
  - Parts replaced
  - Assigned resources

### 6. Engineer Closes Complaint
- **Who**: Engineer
- **When**: After MachineIssueReview exists and user has acknowledged
- **URL**: `/home/complain/closing/{id}`
- **CRITICAL VALIDATION**: Cannot access closing form without MachineIssueReview
- **Form Fields**:
  - Machine hours at failure
  - Service provider (internal/contractor)
  - Technician name
  - Supervisor
  - Solution description
  - Equipment status
  - Duration
  - Installed spares
  - Images
  - Additional remarks
- **Result**: IssueClosing record created, Status: CLOSED

---

## Key Validations Enforced

### 1. Model-Level Validation (core/models.py)
```python
def validate_status_transition(self, new_status):
    # Only CLOSED status requires MachineIssueReview
    requires_review = ['CLOSED']

    if new_status in requires_review and not self.has_review():
        return False, "Cannot close complaint without engineer documentation."
```

**Result**: Prevents closing without documentation at database level

### 2. View-Level Validation (User/views.py)
```python
class ComplainClosingView:
    def get(self, request, pk):
        # CRITICAL: Closing form requires MachineIssueReview
        try:
            review = MachineIssueReview.objects.get(issue=issue)
        except MachineIssueReview.DoesNotExist:
            return error: 'Engineer must fill MachineIssueReview form before closing'
```

**Result**: Prevents accessing closing form without review

### 3. Quick Review Does NOT Create Review (maintenance/views.py)
```python
def quick_review_submit(request, pk):
    if decision == 'RESOLVED':
        issue.status = 'RESOLVED'
        # NO MachineIssueReview created
        # User acknowledgment next
```

**Result**: Separates quick triage from formal documentation

---

## Status Flow Summary

| Status | Meaning | Next Action |
|--------|---------|-------------|
| **PENDING** | Awaiting engineer review | Engineer does quick review |
| **RESOLVED** | Quick fix applied | User acknowledges → Engineer documents → Close |
| **UNDER_OBSERVATION** | Being investigated | Engineer fills full review |
| **REVIEWED** | Engineer reviewed, awaiting approval | Approver approves/rejects |
| **APPROVED** | Approved by management | User acknowledges → Close |
| **REJECTED** | Rejected by management | Re-work or close |
| **AWAITING_DOCUMENTATION** | Waiting for engineer docs | Engineer fills review form |
| **CLOSED** | Complete and documented | Final state |

---

## Database Records Created

### MachineIssue
- **Created**: When user submits complaint
- **Contains**: User description, images, machine info, timestamps

### MachineIssueReview
- **Created**:
  - When engineer selects "UNDER_OBSERVATION" and fills review form
  - MUST be created before closing (even for quick fixes)
- **Contains**: Priority, type, problem nature, assigned resources, parts

### MachineIssueApproval
- **Created**: When approver approves/rejects
- **Contains**: Approver comments, decision

### IssueClosing
- **Created**: When engineer closes complaint
- **Requires**: MachineIssueReview must exist
- **Contains**: Solution details, spares installed, duration, final status

---

## What Changed from Previous Design

### ❌ Old (Incorrect) Design:
- Quick review automatically created MachineIssueReview with dummy data
- Engineer could skip proper documentation
- Review and closing were conflated

### ✅ New (Correct) Design:
- Quick review only changes status, NO review record
- Engineer MUST document before closing (enforced at model and view levels)
- Clear separation: Quick triage → User acknowledgment → Documentation → Closure

---

## Benefits of New Design

1. **Captures Real Workflow**: Matches how engineers actually work (quick triage first)
2. **Enforces Documentation**: Cannot close without proper review record
3. **User Involvement**: User confirms resolution before formal closure
4. **Flexibility**: Supports both quick fixes and complex investigations
5. **Data Integrity**: Review records are meaningful, not auto-generated placeholders
6. **Compliance**: All closures have proper documentation for audits

---

## TODO: Features to Implement

### User Acknowledgment System
- Add UI for users to view resolved complaints
- Provide "Confirm Resolution" button
- Options: "Yes, fixed" or "No, still broken"
- Track acknowledgment in database
- Notify engineer when user responds

### Enhanced Status Tracking
- Show different dashboards based on role
- Engineers see: PENDING, RESOLVED (awaiting ack), UNDER_OBSERVATION
- Users see: Their complaints with acknowledgment prompts
- Approvers see: REVIEWED items needing approval

### Notifications
- Email/SMS when complaint status changes
- Notify user when marked RESOLVED
- Notify engineer when user acknowledges
- Remind engineer to document if delayed

---

## Current State

**Implemented**:
- ✅ Quick review without auto-creating review
- ✅ Model validation preventing closure without review
- ✅ View validation enforcing review before closing
- ✅ UNDER_OBSERVATION detailed review path
- ✅ Status transitions validated

**Pending**:
- ⏳ User acknowledgment feature
- ⏳ Notification system
- ⏳ Role-based dashboards

---

## Testing the Workflow

### Test Case 1: Quick Resolution
1. User creates complaint (ID: 2, Ticket: 1-6-2)
2. Engineer visits: `http://localhost:8000/complain-view/quick-review/2`
3. Engineer selects "RESOLVED" with comments
4. Status changes to RESOLVED
5. **[TODO]** User acknowledges resolution
6. Engineer visits: `http://localhost:8000/home/complain/review/2`
7. Engineer fills MachineIssueReview form
8. Engineer visits: `http://localhost:8000/home/complain/closing/2`
9. Engineer fills closing form
10. Status changes to CLOSED

### Test Case 2: Complex Investigation
1. User creates complaint
2. Engineer selects "UNDER_OBSERVATION"
3. Redirected to review form automatically
4. Engineer fills complete review
5. Status: REVIEWED
6. Approver approves
7. Status: APPROVED
8. **[TODO]** User acknowledges
9. Engineer closes
10. Status: CLOSED

### Test Case 3: Validation (Should Fail)
1. User creates complaint (PENDING)
2. Engineer marks RESOLVED
3. Engineer tries to access closing form directly
4. **BLOCKED**: "Engineer must fill MachineIssueReview form first"
5. Engineer fills review form
6. Engineer can now access closing form
7. Closes successfully

---

## File Changes Made

### Modified Files:
1. **maintenance/views.py** (line 267)
   - `quick_review_submit()` - Removed auto-creation of review

2. **core/models.py** (line 417)
   - `validate_status_transition()` - Only requires review for CLOSED status

3. **User/views.py** (line 267)
   - `ComplainClosingView.get()` - Enforces review exists
   - `ComplainClosingView.post()` - Sets status to CLOSED correctly

---

**Last Updated**: January 27, 2026
**Status**: Core workflow implemented, user acknowledgment pending
