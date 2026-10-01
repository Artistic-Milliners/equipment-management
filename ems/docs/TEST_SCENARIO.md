# Test Scenario - Complete Workflow

## 🎯 Test Complaint Details

**Ticket Number**: 1-1-5
**Complaint ID**: 5
**Status**: PENDING
**Equipment**: VNA
**Machine**: Power Mover 1
**Created by**: zubair
**Description**: TEST: Machine making unusual noise during operation. Please investigate.

---

## 📋 Step-by-Step Testing

### STEP 1: Engineer Quick Review
**Login as**: Engineer (wahab)
**URL**: http://localhost:8000/complain-view/quick-review/5

**Action**:
- Select: **"UNDER_OBSERVATION"**
- Click Submit

**Expected Result**:
- ✅ Auto-redirects to: http://localhost:8000/home/complain/review/5
- ✅ Review form loads

---

### STEP 2: Fill Detailed Review Form 🆕
**URL**: http://localhost:8000/home/complain/review/5

**Fill the following fields**:
- **Reviewer Description**: "Checked the machine, found loose belt causing vibration"
- **Priority**: Select any (e.g., MODERATE)
- **Issue Type**: Select any (e.g., CORRECTIVE)
- **Problem Nature**: Select any (e.g., MECHANICAL)
- **Assign to Department**: Select maintenance department
- **Assign to Person**: Select engineer
- **Malfunctioning Parts**: (Optional) Select any spare parts
- **Upload Images**: (Optional) Upload images

**🆕 NEW FIELD - Resolution Status**:
```
○ Issue Resolved - Machine is working - user will confirm
● Still Working - Needs approval/further work
```

**For this test, select**: ☑️ **"Issue Resolved"**

**Click**: Submit Review

**Expected Result**:
- ✅ Success message: "Complaint 1-1-5 marked as RESOLVED. User zubair must confirm resolution before you can close it."
- ✅ Redirects to: /complain-view/view-complains
- ✅ Status changed to: **RESOLVED**

**Verify**:
```bash
docker-compose exec -T web python manage.py shell << 'EOF'
from core.models import MachineIssue
issue = MachineIssue.objects.get(pk=5)
print(f'Status: {issue.status}')  # Should show: RESOLVED
EOF
```

---

### STEP 3: User Acknowledgment
**Logout, then login as**: User (zubair) - the original complaint creator
**URL**: http://localhost:8000/home/complain/5/user-close

**View**:
- Complaint details shown
- Form asks: "Confirm if issue is resolved"

**Action**:
- **User Feedback** (optional): "Yes, the noise is gone. Machine working normally now."
- Click: **Submit**

**Expected Result**:
- ✅ Success message shown
- ✅ Redirects to: /home/complain/complainTracking/5
- ✅ Status changed: **RESOLVED → AWAITING_DOCUMENTATION**

**Verify**:
```bash
docker-compose exec -T web python manage.py shell << 'EOF'
from core.models import MachineIssue
issue = MachineIssue.objects.get(pk=5)
print(f'Status: {issue.status}')  # Should show: AWAITING_DOCUMENTATION
print(f'Feedback: {issue.description_user}')  # Should include user feedback
EOF
```

---

### STEP 4: Engineer Closes Complaint
**Logout, then login as**: Engineer (wahab)
**URL**: http://localhost:8000/home/complain/closing/5

**Expected Result**:
- ✅ Closing form loads successfully
- ✅ Review data is populated
- ✅ All fields available for closing

**Fill the following fields**:
- **Machine Hours at Failure**: 1500
- **Resolved By**: Select "Inhouse" or external contractor
- **Technician Name**: "Ahmed Khan"
- **Supervisor**: "Wahab"
- **Solution Description**: "Tightened the loose belt and adjusted tension"
- **Equipment Status**: Select (e.g., OPERATIONAL)
- **Duration (hours)**: 2
- **Installed Spares**: (Optional) Select any spares used
- **Images**: (Optional) Upload closing images
- **Additional Remarks**: "Tested machine for 30 minutes, working fine"

**Click**: Submit

**Expected Result**:
- ✅ Success message
- ✅ Redirects to: /home/complain/closing/complainList
- ✅ Status changed to: **CLOSED**
- ✅ IssueClosing record created

**Verify**:
```bash
docker-compose exec -T web python manage.py shell << 'EOF'
from core.models import MachineIssue, IssueClosing
issue = MachineIssue.objects.get(pk=5)
print(f'Status: {issue.status}')  # Should show: CLOSED

# Check closing record
try:
    closing = IssueClosing.objects.get(issueReview__issue=issue)
    print(f'Closing exists: Yes')
    print(f'Technician: {closing.technician}')
    print(f'Solution: {closing.solutionDescription[:50]}...')
except IssueClosing.DoesNotExist:
    print('Closing exists: No')
EOF
```

---

## ✅ Test Checklist

- [ ] Step 1: Quick review redirects to detailed form ✓
- [ ] Step 2: New "Resolution Status" field visible ✓
- [ ] Step 2: Selecting "Issue Resolved" sets status to RESOLVED ✓
- [ ] Step 2: Message mentions user confirmation ✓
- [ ] Step 3: User can access acknowledgment URL ✓
- [ ] Step 3: User feedback saved correctly ✓
- [ ] Step 3: Status changes to AWAITING_DOCUMENTATION ✓
- [ ] Step 4: Engineer can access closing form ✓
- [ ] Step 4: Closing form accepts all data ✓
- [ ] Step 4: Status changes to CLOSED ✓

---

## 🔄 Alternative Test: "Still Working" Path

To test the approval workflow:

**In Step 2**, instead select:
- ☑️ **"Still Working - Needs approval/further work"**

**Expected Result**:
- Status: **REVIEWED** (not RESOLVED)
- Message: "Awaiting management approval"
- Goes to approval workflow (not user acknowledgment)

---

## 🐛 Common Issues & Solutions

### Issue: 404 on closing form
**Cause**: Review doesn't exist
**Solution**: Make sure you completed Step 2 (detailed review)

### Issue: Can't access user-close URL
**Cause**: Not logged in as complaint creator
**Solution**: Login as user 'zubair'

### Issue: Closing form asks for contractor
**Cause**: Need to select service provider
**Solution**: Select "Inhouse" or choose a contractor

### Issue: Status not changing
**Cause**: Validation error
**Solution**: Check Django logs:
```bash
docker-compose logs -f web
```

---

## 📊 Status Progression

Expected flow for this test:

```
PENDING (Step 1)
   ↓
RESOLVED (Step 2 - Engineer marks as resolved)
   ↓
AWAITING_DOCUMENTATION (Step 3 - User confirms)
   ↓
CLOSED (Step 4 - Engineer closes)
```

---

## 🎯 What This Tests

✅ **New Feature**: Resolution status field in detailed review form
✅ **Integration**: Uses existing user_close_complaint mechanism
✅ **Validation**: Can't close without review
✅ **Validation**: Can't close without user confirmation
✅ **Flow**: Complete PENDING → CLOSED workflow
✅ **Messages**: Informative messages at each step
✅ **Redirects**: Automatic redirects guide the user

---

**Ready to test!** Start with Step 1 above.

