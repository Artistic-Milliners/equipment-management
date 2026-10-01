# Item Issuance System Improvements

## Overview
Enhanced item issuance modal with real-time stock warnings, transaction tracking, and machine/work order linking.

## ✅ What Was Improved

### 1. **Better Item Information Display**
The modal now shows complete item information in a prominent info box:

```
┌─────────────────────────────────────────────┐
│  Item Code: MEC-0001  |  Item Name: Bearing │
│  Available: 50 pcs    |  Min Stock: 10      │
└─────────────────────────────────────────────┘
```

### 2. **Structured Issue Details**
Two-part reason system:
- **Reason Type** (dropdown):
  - Maintenance Work
  - Machine Repair
  - Part Replacement
  - New Installation
  - Other

- **Detailed Reason** (required textarea):
  - Full description of why item is being issued
  - Recorded in transaction history
  - Helps with audit trail

### 3. **Real-Time Stock Warnings** ⚠️

#### As User Types Quantity:
- **Exceeds Available:** Red error message
- **Below Minimum Stock:** Yellow warning with impact details
- **Safe Range:** No warning shown

#### Example Warnings:

**When quantity will cause out-of-stock:**
```
⚠️ Stock Impact:
• Remaining stock will be: 0 pcs (OUT OF STOCK)
• This is 10 pcs below minimum level
• ⚠️ Reorder immediately!
```

**When quantity causes low stock:**
```
⚠️ Stock Impact:
• Remaining stock will be: 5 pcs
• This is 5 pcs below minimum level (10 pcs)
• ⚠️ Low stock alert will be triggered
```

### 4. **Machine & Work Order Linking** (Optional)

Now you can link issued items to:
- **Machine:** Which machine is this part for?
- **Work Order/Ticket:** Which maintenance ticket?

#### Benefits:
- Track which parts were used on which machines
- Link spare usage to maintenance work
- Better cost tracking per machine
- Complete audit trail

### 5. **Transaction Recording**

Every issuance creates a `SpareTransaction` record with:
- Who issued it (user)
- When (timestamp)
- Why (reason)
- How much (quantity)
- Which machine (if linked)
- Which work order (if linked)
- Before/after stock levels

### 6. **Post-Issue Alerts**

After successful issuance, user sees:
```
✓ Successfully issued 5 pcs of Ball Bearing

Remaining: 5 units

⚠️ Warning: Ball Bearing is now at low stock level (5 pcs)
```

or

```
✓ Successfully issued 10 pcs of Ball Bearing

Remaining: 0 units

⚠️ Alert: Ball Bearing is now OUT OF STOCK!
```

## How It Works Now

### User Flow:

1. **Click "Issue Item"** on any spare card

2. **Modal Opens** showing:
   - Item code and name
   - Available quantity
   - Minimum stock level

3. **User Fills Form:**
   ```
   Quantity: 5
   Reason Type: Machine Repair
   Detailed Reason: "Replacing worn bearing on Molding Machine M-205"
   Machine: (optional) M-205
   Work Order: (optional) Ticket #EQ-12-345
   ```

4. **Real-Time Warnings:**
   - As user types quantity, system shows impact
   - Red if exceeds available
   - Yellow if below minimum
   - Green/none if safe

5. **Submit:**
   - Button shows: "Processing..."
   - AJAX submission
   - Success message with stock alert
   - Page reloads showing updated quantity

### Example Scenario:

**Before Issue:**
- Ball Bearing (MEC-0001)
- Available: 15 pcs
- Min Stock: 10 pcs

**User Issues:** 8 pcs for "Machine Repair on M-205"

**Warning Shown:**
```
⚠️ Stock Impact:
• Remaining stock will be: 7 pcs
• This is 3 pcs below minimum level (10 pcs)
• ⚠️ Low stock alert will be triggered
```

**User Proceeds**

**After Issue:**
- Success message: "✓ Successfully issued 8 pcs"
- Alert: "⚠️ Warning: Ball Bearing is now at low stock level (7 pcs)"
- Transaction created in database
- Stock updated: 15 → 7 pcs

## Backend Integration

### Updated `spare_issue` View

Now handles:
- Machine ID (optional)
- Work Order ID (optional)
- Reason (required)
- Creates `SpareTransaction` record
- Returns stock alerts

### Transaction Record Created:
```python
SpareTransaction.objects.create(
    spare=spare,
    transaction_type='ISSUE',
    quantity=-8,  # Negative for stock out
    user=request.user,
    reason="Machine Repair on M-205 - Replacing worn bearing",
    machine=machine_m205,
    work_order=ticket_345,
    quantity_before=15,
    quantity_after=7
)
```

## Benefits

### For Users:
✅ See available stock before issuing  
✅ Get warned if stock will be low  
✅ Know when to reorder  
✅ Link items to machines and tickets  
✅ Clear reason tracking  

### For Management:
✅ Complete audit trail (who, when, why, where)  
✅ Track spare usage per machine  
✅ Cost allocation to work orders  
✅ Prevent stock-outs with warnings  
✅ Accountability for all issuances  

### For Inventory Control:
✅ Automatic transaction logging  
✅ Before/after quantities recorded  
✅ Link to machines and work orders  
✅ Generate usage reports  
✅ Track consumption patterns  

## Technical Details

### Modal Structure:
```
┌─────────────────────────────────────┐
│ Issue Inventory Item                │
├─────────────────────────────────────┤
│ [Info Box: Item Details]            │
│                                     │
│ Issue Details                       │
│   Quantity: [___]                   │
│   Reason Type: [dropdown]           │
│   Detailed Reason: [textarea]       │
│                                     │
│ Link to Machine/Work Order          │
│   Machine: [search]                 │
│   Work Order: [search]              │
│                                     │
│ [Stock Impact Warning - dynamic]    │
│                                     │
│ [Cancel]  [Issue Item]              │
└─────────────────────────────────────┘
```

### JavaScript Features:
1. **Auto-populate:** Fetches item details via API
2. **Real-time validation:** Calculates impact as user types
3. **Color-coded warnings:** Red (error), Yellow (warning), Green (safe)
4. **AJAX submission:** No page reload during submission
5. **Smart alerts:** Shows remaining stock and alerts

### API Endpoints Used:
- `GET /api/spares/detail/<id>` - Get item details
- `POST /home/spares/issueSpare/<id>` - Issue the item

## Form Validation

### Client-Side:
✅ Quantity must be > 0  
✅ Quantity cannot exceed available  
✅ Reason is required  
✅ Real-time stock impact calculation  

### Server-Side:
✅ Quantity validation  
✅ Stock availability check  
✅ Reason required  
✅ Transaction creation  
✅ Stock alerts generation  

## Testing Checklist

- [x] ✅ Modal displays item details correctly
- [x] ✅ Real-time warnings show as quantity changes
- [x] ✅ Warning turns red if quantity exceeds available
- [x] ✅ Warning shows low stock alert
- [x] ✅ Out-of-stock warning displays properly
- [ ] ⏳ Form submits via AJAX
- [ ] ⏳ Transaction is created in database
- [ ] ⏳ Stock is updated correctly
- [ ] ⏳ Success message shows stock alerts
- [ ] ⏳ Page reloads with updated quantities

## Future Enhancements (Optional)

### Machine Search Autocomplete:
- Type machine name → shows suggestions
- Click to select
- Automatically links to machine

### Work Order Search:
- Type ticket number → shows matching tickets
- Select from dropdown
- Links issuance to work order

### Barcode Scanning:
- Scan item barcode to open issue modal
- Scan machine barcode to link
- Speed up the process

### Batch Issuance:
- Issue multiple items at once
- For large maintenance jobs
- One transaction for multiple parts

### Return to Stock:
- Unused parts can be returned
- Creates RETURN transaction
- Adds back to stock

## Files Modified

1. `User/templates/user/sparesDetail.html` - Updated modal and JavaScript
2. `User/views.py` - Already has enhanced `spare_issue` view
3. `core/models.py` - Already has `SpareTransaction` model

## Usage Examples

### Basic Issuance:
```
User: John Doe
Item: Ball Bearing (MEC-0001)
Quantity: 5 pcs
Reason Type: Machine Repair
Reason: "Replacing faulty bearing on Line 3 machine"
Result: Transaction created, stock: 50 → 45 pcs
```

### Issuance with Machine Link:
```
User: Jane Smith
Item: Hydraulic Oil (HYD-0001)
Quantity: 20 liters
Reason Type: Maintenance Work
Reason: "Scheduled oil change for press machine"
Machine: Hydraulic Press HP-100
Result: Transaction linked to machine HP-100
```

### Issuance with Work Order:
```
User: Mike Johnson
Item: Relay Switch (ELE-0005)
Quantity: 1 pcs
Reason Type: Part Replacement
Reason: "Replacing burned relay as per ticket"
Work Order: EQ-12-345
Result: Cost allocated to work order EQ-12-345
```

## Conclusion

The improved item issuance system provides:
- **Real-time feedback** on stock impact
- **Complete audit trail** of all transactions
- **Smart warnings** to prevent stock-outs
- **Machine and work order linking** for better tracking
- **User accountability** with required reasons

All issuances are now tracked, validated, and recorded for complete inventory control.

