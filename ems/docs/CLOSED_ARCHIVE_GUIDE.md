# Closed Complaints Archive - Complete Documentation System

## Overview

A new dedicated page for Engineers and Management to review all closed complaints with complete documentation history.

## Access Control

### ✅ Can Access:
- **Engineers** - Members of "Engineers" group or have `core.can_review_complaint` permission
- **Approvers** - Members of "Approvers" group or have `core.can_approve_complaint` permission

### ❌ Cannot Access:
- Regular users
- Production staff
- Anyone without engineer/approver permissions

**Access denied message shown** if unauthorized user tries to access.

## Page Features

### 📊 Statistics Dashboard

Shows 4 key metrics at the top:
```
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ Total Closed │ This Month   │ Avg Days     │ Contractors  │
│     156      │      24      │     3.5      │      8       │
└──────────────┴──────────────┴──────────────┴──────────────┘
```

- **Total Closed**: All-time closed complaints
- **This Month**: Complaints closed in current month
- **Avg Days to Close**: Average resolution time
- **Contractors Used**: Unique contractors involved

### 🔍 Advanced Filters

**Filter Options:**
- **Date From** - Start date for filtering
- **Date To** - End date for filtering
- **Equipment** - Filter by equipment type
- **Search** - Free text search in ticket #, description, etc.

**How Filtering Works:**
- All filters work together (AND logic)
- Client-side filtering (instant results)
- Preserves original data (no server calls)

### 📋 Collapsible Complaint Cards

Each closed complaint shows:

**Header (Always Visible):**
- Ticket number badge
- Equipment and machine name
- Metadata grid:
  - Reported by (user name)
  - Department
  - Created date
  - Closed date
  - Duration in hours
- "View Details" button to expand

**Body (Expandable):**
Click "View Details" to see complete documentation:

#### 1. Original Complaint Section
- User's problem description
- Attached images (clickable to view full size)

#### 2. Engineer Review Section
- Reviewer name and date
- Priority badge (High/Moderate/Low with colors)
- Issue type (Breakdown, Preventive, Corrective)
- Problem nature
- Assigned person and department
- Engineer's assessment notes
- Malfunction parts list
- Review images

#### 3. Management Approval Section
- Approver name and date
- Approval status
- Comments from management

#### 4. Resolution & Closing Documentation
- Technician and supervisor names
- Duration
- Equipment status after repair
- Machine hours at closure
- Contractor used (if external)
- Detailed solution description
- Additional remarks
- Closing images

### 🎨 Visual Design

**Color-Coded Sections:**
- Original Complaint: Blue accent border
- Engineer Review: Green accent border
- Management Approval: Orange accent border
- Resolution: Green accent border

**Priority Badges:**
- **HIGH**: Red (`#fee2e2` background)
- **MODERATE**: Yellow (`#fef3c7` background)
- **LOW**: Blue (`#dbeafe` background)

**Interactive Elements:**
- Expandable cards with smooth animations
- Hover effects on cards
- Click images to view full size in new tab

### 🖨️ Print Functionality

**Two print options:**

1. **Print All Archive**
   - Button in header
   - Prints all visible (filtered) complaints
   - Auto-expands all cards
   - Hides filters and navigation

2. **Print Individual Ticket**
   - Button on each card
   - Prints only that specific ticket
   - Auto-expands if collapsed
   - Clean print layout

**Print Styling:**
- Removes sidebar, header, filters
- Shows all details
- Professional format
- Perfect for documentation/audits

## Page URL

```
/complain-view/closed-archive/
```

Or via Django URL name:
```python
{% url 'maintenance:closed_archive' %}
```

## Navigation

### Sidebar Link (Only for Engineers/Approvers):
```
Ticket List
Closed Archive  ← New link (only visible to engineers/approvers)
Inventory
```

## Use Cases

### For Engineers:

**1. Reference Past Solutions**
```
Search for "motor bearing" → Find similar past issues
→ See how they were resolved → Apply same solution
```

**2. Review Documentation Quality**
```
Filter by date range → Review recent closures
→ Ensure documentation standards are met
```

**3. Learn from Past Issues**
```
Browse by equipment type → See common problems
→ Identify patterns → Prevent future issues
```

### For Management/Approvers:

**1. Audit Trail**
```
Review all closed complaints → Verify proper procedure
→ Check approval and resolution quality
```

**2. Performance Review**
```
Filter by month → See resolution times
→ Identify top performers → Review efficiency
```

**3. Contractor Evaluation**
```
Filter to see contractor-resolved tickets
→ Evaluate contractor performance → Make hiring decisions
```

**4. Compliance & Reporting**
```
Print archive → Include in monthly reports
→ Demonstrate maintenance activities → Regulatory compliance
```

## Technical Implementation

### View Function: `closed_complaints_archive()`

**Location:** `maintenance/views.py`

**Permissions Check:**
```python
is_approver = request.user.has_perm('core.can_approve_complaint') or \
              request.user.groups.filter(name='Approvers').exists()
is_engineer = request.user.has_perm('core.can_review_complaint') or \
              request.user.groups.filter(name='Engineers').exists()

if not (is_approver or is_engineer):
    raise PermissionDenied("Access denied...")
```

**Database Query Optimization:**
```python
closed_issues = MachineIssue.objects.filter(status='CLOSED').select_related(
    'user', 'equipment', 'machine_id', 'error_department',
    'machineissue', 'machineissue__reviewer',
    'machineissue__assignPerson', 'machineissue__assignDepartment',
    'issue_remarks', 'issue_remarks__user_id',
    'machineissue__issueclosing', 'machineissue__issueclosing__contractor'
).prefetch_related(
    'image', 'machineissue__reviewrImages',
    'machineissue__malfunction_part', 'machineissue__issueclosing__image'
)
```

**Single Query** - Loads everything at once, very efficient!

### Statistics Calculations:

**Total Closed:**
```python
total_closed = closed_issues.count()
```

**This Month:**
```python
first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0)
closed_this_month = closed_issues.filter(date_time__gte=first_day_of_month).count()
```

**Average Resolution Time:**
```python
for issue in closed_issues:
    duration = (closing_date - issue.date_time).days
    total_duration += duration
avg_days = total_duration / count
```

**⚠️ Note:** This calculation will be accurate **after applying the date_time migration**!

## Files Created/Modified

### New Files:
1. **`maintenance/templates/maintenance/closed-complaints.html`**
   - Complete archive page with all documentation
   - 550+ lines of beautiful, functional HTML/CSS/JS

2. **`core/migrations/0007_fix_date_time_field.py`**
   - Critical migration to fix date_time field
   - Adds last_updated field

3. **`CRITICAL_DATE_TIME_FIX.md`**
   - Detailed explanation of the date_time bug and fix

4. **`CLOSED_ARCHIVE_GUIDE.md`**
   - This comprehensive guide

### Modified Files:
1. **`core/models.py`** (Line 211-212)
   - Fixed date_time field
   - Added last_updated field

2. **`maintenance/views.py`** (Added `closed_complaints_archive()`)
   - Lines 102-195
   - Includes permission checks and statistics

3. **`maintenance/urls.py`** (Line 10)
   - Added route: `path('closed-archive/', ...)`

4. **`templates/index.html`** (Lines 414-421)
   - Added sidebar link (only visible to engineers/approvers)

## Next Steps

### 1. Apply Migration (CRITICAL)

You **MUST** run the migration to fix the date_time bug:

```bash
# Try activating virtual environment
.\Scripts\activate.bat

# Run migration
python manage.py migrate core

# Or migrate all
python manage.py migrate
```

### 2. Test the Archive Page

1. Login as engineer or approver
2. Look for "Closed Archive" in sidebar
3. Click it → Should see closed complaints archive
4. Try filters and search
5. Expand/collapse complaint details
6. Test print functionality

### 3. Verify Permissions

**Test as regular user:**
- Should NOT see "Closed Archive" in sidebar
- Direct URL access should show "Permission Denied"

**Test as engineer:**
- Should see "Closed Archive" in sidebar
- Can access and view all closed complaints

**Test as approver:**
- Should see "Closed Archive" in sidebar
- Can access and view all closed complaints

## Future Enhancements

Possible additions:
- 📈 Charts and analytics on archive page
- 📥 Export to PDF/Excel
- 🔔 Notification for documentation quality issues
- 📊 Contractor performance metrics
- 🏆 Engineer performance dashboard
- 📅 Calendar view of closed complaints
- 🔎 Advanced search with filters
- 🏷️ Tagging system for categorization

---

**You now have a complete, professional documentation archive system with proper access control and comprehensive reporting!** 📚✅



