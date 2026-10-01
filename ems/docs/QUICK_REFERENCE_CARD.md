# Inventory System Quick Reference Card

## 🎯 Quick Actions

### On Each Spare Card:

| Button | Color | Action | Creates Transaction |
|--------|-------|--------|-------------------|
| **🟢 Receive Stock** | Green | Add incoming stock | RECEIPT |
| **🟡 Issue Item** | Yellow | Issue to machine/job | ISSUE |
| **📜 History** | Blue | View complete ledger | - |
| **✏️ Edit** | Gray | Edit all details | ADJUSTMENT (if qty changed) |

---

## ➕ Adding New Spare

```
1. Click "Add Item"
2. Fill:
   ✓ Name, Category (auto-generates code!)
   ✓ Manufacturer + Part Number
   ✓ Select machines (use search!)
   ✓ Quantity, Min/Max levels
3. Submit → Code generated: MEC-0015
```

**Auto-generates:** `ELE-####`, `MEC-####`, `HYD-####`, etc.

---

## 📥 Receiving Stock (New Deliveries)

```
1. Click "🟢 Receive Stock"
2. Fill:
   ✓ Quantity: 50
   ✓ Type: New Purchase
   ✓ Details: "PO #12345 from SKF"
   ✓ PO Number: PO-2025-001
   ✓ Invoice: INV-12345
3. Submit → Stock: 10 → 60
```

**Logs:** Who, when, PO, invoice, before/after

---

## 📤 Issuing Stock (To Machines/Jobs)

```
1. Click "🟡 Issue Item"
2. Fill:
   ✓ Quantity: 5
   ✓ Reason: "Machine repair"
   ✓ Machine: M-100 (use search!)
   ✓ Work Order: EQ-12-345
3. Watch stock warning if going low
4. Submit → Stock: 60 → 55
```

**Logs:** Who, when, why, which machine, work order

---

## 📜 Viewing Transaction History

```
1. Click "📜 History"
2. See:
   ✓ Current stock & status
   ✓ Total transaction count
   ✓ Complete transaction table
   ✓ Color-coded types
3. Export CSV if needed
```

**Shows:** Every movement since item was created

---

## 🔍 Filtering Spares

### By Machine:
```
Filter: Machine → M-100
→ Shows only spares for M-100
```

### By Category:
```
Filter: Category → Electrical
→ Shows only electrical parts
```

### By Status:
```
Filter: Status → Low Stock
→ Shows items needing reorder
```

### Combined:
```
Category: Mechanical
Status: Low Stock  
Machine: M-100
→ Shows mechanical parts for M-100 that are low
```

---

## ✏️ Editing Spares

```
1. Click "✏️ Edit" icon
2. Update:
   ✓ Name, description
   ✓ Manufacturer, part number
   ✓ Machines (search to add/remove)
   ✓ Quantity, min/max, price
3. Submit → Changes saved
```

**If quantity changed:** Creates ADJUSTMENT transaction

---

## 🎨 Color Codes

### Transaction Types:
- 🟢 **RECEIPT** - Stock In
- 🟡 **ISSUE** - Stock Out
- 🔵 **ADJUSTMENT** - Correction
- 🟣 **RETURN** - Returned
- 🔴 **DAMAGE** - Scrapped

### Stock Status:
- 🟢 **In Stock** - Above minimum
- 🟡 **Low Stock** - At/below minimum
- 🔴 **Out of Stock** - Zero quantity

---

## 📊 Item Code System

| Category | Prefix | Example |
|----------|--------|---------|
| Electrical | ELE- | ELE-0001 |
| Mechanical | MEC- | MEC-0001 |
| Hydraulic | HYD- | HYD-0001 |
| Pneumatic | PNE- | PNE-0001 |
| Safety | SAF- | SAF-0001 |
| General | GEN- | GEN-0001 |

**Auto-generated** - No manual entry!

---

## 🕐 Timestamps

All times shown in **Pakistan Standard Time (PKT = UTC+5)**

Example:
```
Oct 31, 2025
02:30 PM PKT
```

---

## 🚨 Warnings

### When Issuing:

**Below Minimum:**
```
⚠️ Stock Impact:
• Remaining will be: 5 pcs
• This is 5 below minimum (10)
• Low stock alert triggered
```

**Out of Stock:**
```
🛑 Stock Impact:
• Remaining will be: 0 pcs
• OUT OF STOCK!
• Reorder immediately!
```

---

## 📝 Best Practices

### Receiving Stock:
✓ Always include PO number  
✓ Add invoice number  
✓ Record actual receipt date  
✓ Note any discrepancies  

### Issuing Stock:
✓ Link to machine when possible  
✓ Add work order if applicable  
✓ Describe purpose clearly  
✓ Check stock warnings  

### Managing Inventory:
✓ Use machine filter for maintenance planning  
✓ Review ledger monthly  
✓ Set appropriate min/max levels  
✓ Link spares to machines  

---

## 🔑 Keyboard Tips

### Machine Search (in modals):
- Type to filter
- Ctrl + Click = Multi-select
- Shift + Click = Range select
- Click "Select All" for filtered results

### Filters (main page):
- Type in search = instant filter
- Use dropdowns for categories
- Click "Clear" to reset all

---

## 📞 Quick Troubleshooting

### Can't Issue Item?
→ Check stock > 0  
→ Fill reason field  
→ Hard refresh (Ctrl+F5)  

### Can't See Transactions?
→ Run: `python manage.py migrate`  
→ Refresh page  

### Time Wrong?
→ Check Django settings: `TIME_ZONE = 'Asia/Karachi'`  
→ Hard refresh browser  

### Duplicate Warning?
→ Check if similar item exists  
→ Use different name or verify not duplicate  

---

## 📋 Transaction Record Example

```
{
  "Type": "RECEIPT",
  "Quantity": +50,
  "Item": "Ball Bearing (MEC-0001)",
  "User": "John Doe",
  "Reason": "PO #12345 from SKF | PO: PO-2025-001 | Invoice: INV-12345",
  "Before": 10,
  "After": 60,
  "Time": "Oct 31, 2025 02:30 PM PKT"
}
```

**Every transaction has:** Who, What, When, Why, How Much, Before, After

---

## 🎊 System Summary

**You can now:**
✅ Add items with auto-generated codes  
✅ Receive stock with PO tracking  
✅ Issue stock to machines  
✅ View complete transaction history  
✅ Filter by machine  
✅ Search and find parts easily  
✅ Track every movement  
✅ Generate audit reports  
✅ Maintain accountability  

**All in Karachi local time!** 🇵🇰

---

**For detailed guides, see the documentation files created in your project folder.**

