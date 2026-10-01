# Issue Item Troubleshooting Guide

## Fixes Applied

### 1. **CSRF Token Handling**
**Problem:** CSRF token might not be sent correctly  
**Fix:** Now using Django's cookie-based CSRF token method

**Changes:**
```javascript
// Added CSRF helper function
function getCookie(name) { ... }
const csrftoken = getCookie('csrftoken');

// All fetch calls now use:
headers: {
    'X-CSRFToken': csrftoken
}
```

### 2. **Work Order ID Handling**
**Problem:** Work order field expected ID but form allows ticket number  
**Fix:** Backend now accepts both:
- Integer ID: `123`
- Ticket Number: `EQ-12-345`

```python
if work_order_id.isdigit():
    work_order = MachineIssue.objects.get(pk=int(work_order_id))
else:
    work_order = MachineIssue.objects.get(ticket_num=work_order_id)
```

### 3. **Empty String Handling**
**Problem:** Empty strings for machine/work order might cause errors  
**Fix:** Proper validation before database queries

```python
if machine_id and machine_id != '':
    # Only query if not empty
    machine = Machines.objects.get(pk=int(machine_id))
```

### 4. **Enhanced Error Logging**
**Added:** Detailed console logging to help debug

```python
print(f"SPARE ISSUE REQUEST - Item: {spare.item_code}")
print(f"POST data: {request.POST}")
print(f"Quantity: {issue_quantity}")
print(f"Reason: {issue_reason}")
print(f"Machine ID: {machine_id}")
print(f"✓ Transaction created: {transaction}")
```

## How to Test

### Step 1: Check Browser Console

1. Open browser DevTools (F12)
2. Go to Console tab
3. Try issuing an item
4. Look for errors

**What to look for:**
```
❌ CSRF verification failed
❌ 403 Forbidden
❌ TypeError: Cannot read property...
❌ Network error
```

### Step 2: Check Server Console

Look at your Django server output for:
```
SPARE ISSUE REQUEST - Item: MEC-0001
POST data: <QueryDict: ...>
Quantity: 5
Reason: Machine repair
Machine ID: 1
✓ Machine found: Molding Machine M-100
✓ Transaction created: ISSUE: MEC-0001 - -5 units
```

### Step 3: Try Simple Issue First

**Test with minimal data:**
```
Quantity: 1
Reason Type: Other
Reason: Test issuance
Machine: (leave empty)
Work Order: (leave empty)
```

**Expected:**
- Should work without errors
- Success message appears
- Page reloads
- Stock decremented

### Step 4: Then Add Machine

**Test with machine:**
```
Quantity: 1
Reason: Test with machine
Machine: Select any machine from dropdown
Work Order: (leave empty)
```

### Step 5: Test Work Order

**Test with work order:**
```
Quantity: 1
Reason: Test with ticket
Machine: (optional)
Work Order: Type any ticket number (e.g., "EQ-12-345")
```

## Common Errors and Solutions

### Error 1: "An error occurred"
**Cause:** Generic JavaScript error  
**Solution:**
1. Check browser console for details
2. Look for red errors
3. Note the error message
4. Check server logs

### Error 2: "CSRF verification failed"
**Cause:** CSRF token not sent or invalid  
**Solution:**
- ✅ Already fixed with cookie-based token
- Ensure cookies are enabled in browser
- Try hard refresh (Ctrl+F5)

### Error 3: "Item not found"
**Cause:** Wrong item ID  
**Solution:**
- Check the URL being called
- Should be `/home/spares/issueSpare/123`
- Verify item exists in database

### Error 4: "Reason for issue is required"
**Cause:** Empty or whitespace-only reason  
**Solution:**
- Fill in the "Detailed Reason" textarea
- Must have actual text, not just spaces

### Error 5: "Required quantity exceeds available"
**Cause:** Trying to issue more than available  
**Solution:**
- Check available quantity shown in modal
- Enter quantity ≤ available

### Error 6: Network errors
**Cause:** Server not running or wrong URL  
**Solution:**
- Ensure Django server is running
- Check URL in browser console
- Verify URL matches your URL patterns

## Debug Checklist

### Frontend Checks:

- [ ] Browser console shows no errors
- [ ] CSRF token is being sent (check Network tab)
- [ ] Form data includes all fields
- [ ] Modal opens with correct item details
- [ ] Quantity is a valid number
- [ ] Reason is not empty

### Backend Checks:

- [ ] Django server is running
- [ ] URL pattern exists: `/home/spares/issueSpare/<id>`
- [ ] View has correct permissions
- [ ] Database has SpareTransaction table
- [ ] User has change_spares permission

### Data Checks:

- [ ] Spare exists in database
- [ ] Spare has valid quantity
- [ ] Machine exists (if selected)
- [ ] Work order exists (if entered)

## Testing Script

Run this in Django shell to verify database:
```python
from core.models import Spares, SpareTransaction, Machines, MachineIssue
from django.contrib.auth import get_user_model

User = get_user_model()

# Check spare exists
spare = Spares.objects.first()
print(f"Spare: {spare.item_code} - {spare.name}")
print(f"Quantity: {spare.quantity}")

# Check user has permission
user = User.objects.filter(is_staff=True).first()
print(f"User: {user.username}")
print(f"Has permission: {user.has_perm('core.change_spares')}")

# Try creating a transaction manually
transaction = SpareTransaction.objects.create(
    spare=spare,
    transaction_type='ISSUE',
    quantity=-1,
    user=user,
    reason='Test transaction',
    quantity_before=spare.quantity,
    quantity_after=spare.quantity - 1
)
print(f"✓ Transaction created: {transaction}")

# Clean up test
transaction.delete()
print("✓ Test transaction deleted")
```

## Quick Fix Steps

### If Error Persists:

**Step 1:** Clear browser cache
```
Ctrl + Shift + Delete
→ Clear cached images and files
→ Clear cookies
```

**Step 2:** Hard refresh page
```
Ctrl + F5 (Windows)
Cmd + Shift + R (Mac)
```

**Step 3:** Check migrations
```bash
python manage.py showmigrations core
```

Should show:
```
[X] 0008_add_spare_fields
[X] (or latest migration)
```

**Step 4:** Check if SpareTransaction table exists
```bash
python manage.py dbshell
```

```sql
\dt core_*
-- Should show core_sparetransaction table
```

**Step 5:** Check permissions
```bash
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
User = get_user_model()

user = User.objects.get(username='your_username')
print(user.has_perm('core.change_spares'))  # Should be True
```

## Server Log Format

When issuing, you should see this in server console:
```
============================================================
SPARE ISSUE REQUEST - Item: MEC-0001
============================================================
POST data: <QueryDict: {'issue-quantity': ['5'], 'issue-reason': ['Machine repair'], ...}>
Quantity: 5
Reason: Machine repair on M-100
Machine ID: 1
Work Order ID: 
✓ Machine found: Molding Machine M-100
✓ Transaction created: ISSUE: MEC-0001 - -5 units by admin
```

## Browser Network Tab

### Check the Request:

**URL:** `/home/spares/issueSpare/123`  
**Method:** POST  
**Status:** 200 OK  

**Request Headers:**
```
Content-Type: multipart/form-data
X-CSRFToken: <token>
```

**Form Data:**
```
csrfmiddlewaretoken: <token>
issue-quantity: 5
issue-reason: Machine repair
machine-id: 1
work-order-id: 
```

**Response:**
```json
{
    "success": true,
    "message": "Successfully issued 5 pcs of Ball Bearing",
    "remaining_quantity": 45,
    "stock_status": "in-stock",
    "stock_alert": null
}
```

## If Still Not Working

### Provide This Information:

1. **Browser Console Error:**
   ```
   [Copy full error message from Console]
   ```

2. **Server Console Output:**
   ```
   [Copy Django server output when issuing]
   ```

3. **Network Request Details:**
   - URL being called
   - Response status code
   - Response body

4. **Form Data Being Sent:**
   - From browser Network tab
   - Form Data section

## Alternative: Temporary Fallback

If AJAX continues failing, you can temporarily use normal form submission:

### Change issueForm:
```html
<form id="issueForm" method="post" action="{% url 'User:spares_issue' spare.pk %}">
    <!-- Remove the JavaScript submit handler temporarily -->
```

### In JavaScript, comment out:
```javascript
// issueForm.addEventListener('submit', function(e) {
//     e.preventDefault();
//     ...
// });
```

This will use traditional form submission (page reload) until we fix the AJAX issue.

## Files Modified

1. `User/templates/user/sparesDetail.html` - Fixed CSRF token handling
2. `User/views.py` - Added debug logging and better error handling

## Next Steps

1. **Clear browser cache** (important!)
2. **Hard refresh** page (Ctrl + F5)
3. **Try issuing** a simple item (no machine/work order)
4. **Check console** for errors
5. **Check server output** for debug messages
6. **Report back** with any error messages

The fixes I made should resolve most CSRF and validation issues. Try it now!

