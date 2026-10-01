# Modal Timing Fix - Issue & Edit Forms

## Problem Identified

The modals were opening BEFORE the JavaScript had time to:
1. Fetch item data from API
2. Populate form fields
3. **Set the form action URL** ← THIS WAS THE MAIN ISSUE

Result: Form posted to wrong URL (`/home/spares` instead of `/home/spares/issueSpare/{id}`)

## Root Cause

**Before (WRONG):**
```html
<button data-bs-toggle="modal" 
        data-bs-target="#issueModal" 
        onclick="issueItem(123)">
```

What happened:
1. `data-bs-toggle` opens modal IMMEDIATELY
2. `onclick` starts fetching data (slow, async)
3. User can click submit BEFORE data loads
4. Form action still = "#" or wrong URL
5. POST goes to wrong endpoint → 500 error

## Fix Applied

**After (CORRECT):**
```html
<button onclick="issueItem(123)">
```

What happens now:
1. Button click → `issueItem()` function runs
2. Fetches data from API
3. Populates all fields
4. **Sets form action** to correct URL
5. THEN opens modal programmatically
6. User sees fully-loaded modal
7. Submit goes to correct URL ✓

## Code Changes

### Issue Button (Line 232):
```html
<!-- REMOVED: data-bs-toggle="modal" data-bs-target="#issueModal" -->
<button onclick="issueItem({{ spare.pk }})">
```

### Edit Button (Line 142):
```html
<!-- REMOVED: data-bs-toggle="modal" data-bs-target="#editModal" -->
<button onclick="editItem({{ spare.pk }})">
```

### issueItem() Function:
```javascript
function issueItem(itemId) {
    // 1. Fetch data
    fetch(`/api/spares/detail/${itemId}`)
        .then(data => {
            // 2. Populate fields
            // 3. Set form action
            form.action = `/home/spares/issueSpare/${itemId}`;
            
            // 4. THEN open modal
            const modal = new bootstrap.Modal(document.getElementById('issueModal'));
            modal.show();
        });
}
```

### editItem() Function:
Same pattern - fetch, populate, set action, then open modal.

## Console Logging Added

Now when you click "Issue Item", you'll see:
```
Loading item data for issue modal, ID: 123
Spare data loaded: {id: 123, item_code: "MEC-0001", ...}
✓ Form action set to: /home/spares/issueSpare/123
✓ Modal opened
```

When you submit:
```
Issue form submitted
Form action: http://127.0.0.1:8000/home/spares/issueSpare/123
Posting to: http://127.0.0.1:8000/home/spares/issueSpare/123
```

## Expected Behavior Now

### Clicking "Issue Item":
1. **Brief pause** (fetching data - usually < 100ms)
2. **Modal appears** with all data loaded
3. **Form ready** with correct action URL
4. **Submit works** correctly

### Clicking "Edit":
1. **Brief pause** (fetching data)
2. **Modal appears** with pre-filled form
3. **Machines pre-selected**
4. **Submit works** correctly

## Testing

### Step 1: Hard Refresh
```
Ctrl + F5
```

### Step 2: Open Console
```
F12 → Console tab
```

### Step 3: Click "Issue Item"
**Watch console for:**
```
✓ Loading item data for issue modal, ID: 123
✓ Spare data loaded: {object}
✓ Form action set to: /home/spares/issueSpare/123
✓ Modal opened
```

### Step 4: Fill Form and Submit
**Watch console for:**
```
✓ Issue form submitted
✓ Form action: http://127.0.0.1:8000/home/spares/issueSpare/123
✓ Posting to: http://127.0.0.1:8000/home/spares/issueSpare/123
```

**Should NOT see:**
```
❌ POST /home/spares 500
❌ Form action: http://127.0.0.1:8000/home/spares
```

## Still Getting 500 Error?

If you STILL get 500 error after this fix, it means:

### Most Likely: Migrations Not Run

```bash
python manage.py migrate
```

The `SpareTransaction` table doesn't exist yet!

### Check Server Console:

Should show:
```
SPARE ISSUE REQUEST - Item: MEC-0001
POST data: {...}
✓ Transaction created
```

NOT:
```
Traceback (most recent call last):
ProgrammingError: relation "core_sparetransaction" does not exist
```

## Summary

✅ **Fixed:** Modal timing issue  
✅ **Fixed:** Form action URL  
✅ **Fixed:** Function definition errors  
✅ **Added:** Console logging for debugging  
✅ **Added:** Form action validation  

Now modals load data FIRST, THEN open, so the form is always ready!

