# Excel Import System - Complete Guide

## Overview
Bulk import spare parts inventory from Excel file with automatic code generation, duplicate detection, machine linking, and transaction logging.

## Quick Start

### Step 1: Install Required Package
```bash
pip install openpyxl
```

### Step 2: Generate Template
```bash
python create_inventory_template.py
```

This creates: **`INVENTORY_IMPORT_TEMPLATE.xlsx`**

### Step 3: Fill Template
1. Open `INVENTORY_IMPORT_TEMPLATE.xlsx`
2. Go to "Inventory Template" sheet
3. Fill in your spare parts data (see examples)
4. Save the file

### Step 4: Import Data
```bash
python manage.py import_spares_excel INVENTORY_IMPORT_TEMPLATE.xlsx
```

### Step 5: Verify
1. Go to: http://127.0.0.1:8000/home/spares
2. See your imported items with auto-generated codes
3. Click "History" to see import transactions

---

## Excel Template Structure

### Sheet 1: "Inventory Template"
Empty template with headers - **FILL THIS WITH YOUR DATA**

### Sheet 2: "Instructions"
Detailed instructions and examples

### Sheet 3: "Sample Data"
6 pre-filled examples showing correct format

---

## Column Descriptions

| Column | Required? | Description | Example |
|--------|-----------|-------------|---------|
| **Item Name** | ✅ YES | Name of the spare part | Ball Bearing 6205 |
| **Category** | ✅ YES | electrical, mechanical, hydraulic, pneumatic, safety, general | mechanical |
| **Description** | No | Detailed specifications | Deep groove ball bearing, sealed |
| **Manufacturer** | No | Manufacturer name | SKF |
| **Manufacturer Part Number** | No | Official part number | 6205-2RS |
| **Initial Quantity** | ✅ YES | Opening stock quantity | 50 |
| **Unit** | ✅ YES | pcs, kg, m, l, box, set, roll, pack | pcs |
| **Min Stock Level** | No | Minimum before alert (default: 5) | 10 |
| **Max Stock Level** | No | Target stock level (default: 100) | 100 |
| **Unit Price** | No | Price per unit in Rs. | 250.00 |
| **Machine Names** | No | Comma-separated machine names | M-100, M-101, P-200 |

---

## Category Values (Must Be Exact)

| Category | Item Code Prefix | Example Items |
|----------|------------------|---------------|
| `electrical` | ELE-#### | Relays, Motors, Sensors, Switches |
| `mechanical` | MEC-#### | Bearings, Gears, Belts, Pulleys |
| `hydraulic` | HYD-#### | Hydraulic Oil, Seals, Pumps, Hoses |
| `pneumatic` | PNE-#### | Pneumatic Cylinders, Valves, Fittings |
| `safety` | SAF-#### | Gloves, Goggles, First Aid, PPE |
| `general` | GEN-#### | Screws, Bolts, General Supplies |

**⚠️ Important:** Categories must be lowercase and exact match!

---

## Sample Excel Data

### Example 1: Machine-Specific Electrical Part
```
Item Name: Relay Switch 24V DC
Category: electrical
Description: 24V DC relay switch, 10A rated, for control panels
Manufacturer: Schneider
Part Number: RLY-24V-10A
Quantity: 15
Unit: pcs
Min Stock: 5
Max Stock: 30
Price: 450.00
Machines: M-100, P-200

→ Result: ELE-0001 - Relay Switch 24V DC (linked to 2 machines)
```

### Example 2: General Hydraulic Consumable
```
Item Name: Hydraulic Oil SAE 10
Category: hydraulic
Description: 10W hydraulic oil for general use
Manufacturer: Shell
Part Number: SHELL-HYD-10
Quantity: 200
Unit: l
Min Stock: 50
Max Stock: 500
Price: 1500.00
Machines: (leave empty)

→ Result: HYD-0001 - Hydraulic Oil SAE 10 (general purpose)
```

### Example 3: Mechanical Spare for Multiple Machines
```
Item Name: Ball Bearing 6205
Category: mechanical
Description: Deep groove ball bearing, sealed both sides
Manufacturer: SKF
Part Number: 6205-2RS
Quantity: 50
Unit: pcs
Min Stock: 10
Max Stock: 100
Price: 250.00
Machines: M-100, M-101, M-102

→ Result: MEC-0001 - Ball Bearing 6205 (linked to 3 machines)
```

---

## Import Command Options

### Basic Import:
```bash
python manage.py import_spares_excel inventory_data.xlsx
```

### Specify User:
```bash
python manage.py import_spares_excel inventory_data.xlsx --user john_doe
```
(Transactions will be attributed to john_doe)

### Skip Duplicates:
```bash
python manage.py import_spares_excel inventory_data.xlsx --skip-duplicates
```
(Don't update existing items, just skip them)

### Show Help:
```bash
python manage.py import_spares_excel --help
```

---

## Import Process

### What Happens During Import:

```
1. ✓ Reads Excel file
2. ✓ Validates headers
3. ✓ Processes each row:
   
   For each item:
   a. Validates required fields
   b. Validates category
   c. Gets or creates manufacturer
   d. Checks for duplicates (by part number or name)
   e. Creates or updates spare
   f. AUTO-GENERATES item code (MEC-0001, etc.)
   g. Links to machines (if specified)
   h. Creates RECEIPT transaction
   i. Logs success/error
   
4. ✓ Shows summary statistics
5. ✓ Reports any errors
```

---

## Import Output Example

```
============================================================
IMPORTING SPARES FROM EXCEL
============================================================
File: inventory_data.xlsx
User: admin
Skip duplicates: False

Checking headers...
⚠️  Optional column missing: Description

  Row 2: "Ball Bearing 6205" → MEC-0001 - CREATED
    ✓ Linked to machine: M-100
    ✓ Linked to machine: M-101
  Row 3: "Hydraulic Oil SAE 10" → HYD-0001 - CREATED
  Row 4: "Relay Switch 24V DC" → ELE-0001 - CREATED
    ✓ Linked to machine: M-100
    ✓ Linked to machine: P-200
  Row 5: "Ball Bearing 6205" already exists - SKIPPED
  Row 6: "Pneumatic Cylinder 50mm" → PNE-0001 - CREATED
    ⚠️  Machine "XYZ-999" not found

============================================================
IMPORT COMPLETE
============================================================
Total rows processed: 5
✓ Created: 4
⊝ Skipped: 1
✗ Errors: 0

✓ Items successfully imported!

Next steps:
1. Go to: http://127.0.0.1:8000/home/spares
2. Verify imported items
3. Check transaction history
```

---

## Duplicate Handling

### By Default (Updates):
```
If spare exists with same:
- Manufacturer part number, OR
- Exact item name

→ UPDATES the existing spare
→ Creates ADJUSTMENT transaction if quantity changed
```

### With --skip-duplicates Flag:
```
If duplicate found:
→ SKIPS the row
→ Shows warning
→ No changes made
```

---

## Machine Linking

### Excel Format:
```
Machine Names (comma-separated)
M-100, M-101, P-200
```

### What Happens:
```
1. Splits by comma: ["M-100", "M-101", "P-200"]
2. For each machine name:
   - Searches database (case-insensitive)
   - If found: Links spare to machine
   - If not found: Shows warning, continues
3. Final: Spare linked to all found machines
```

### Examples:
```
✓ "M-100, P-200" → Links to both machines
✓ "M-100" → Links to single machine  
✓ "" (empty) → General purpose spare
⚠️ "M-100, XYZ-999" → Links to M-100, warns about XYZ-999
```

---

## Transaction Logging

### For New Items:
```
Type: RECEIPT
Quantity: +50 (initial quantity)
Reason: "Initial stock - Excel import"
User: admin
Before: 0
After: 50
```

### For Updated Items (Quantity Changed):
```
Type: ADJUSTMENT
Quantity: +10 (or -10)
Reason: "Excel import: Stock adjusted 40 → 50"
User: admin
Before: 40
After: 50
```

---

## Validation Rules

### Required Fields:
- ✅ Item Name (cannot be empty)
- ✅ Category (must be valid)
- ✅ Initial Quantity (must be number ≥ 0)
- ✅ Unit (cannot be empty)

### Auto-Corrected:
- Category → Converts to lowercase
- Invalid category → Changed to "general" with warning
- Empty min stock → Defaults to 5
- Empty max stock → Defaults to 100
- Empty price → Defaults to 0.00

### Warnings:
- Missing optional fields
- Machine not found
- Invalid category
- Duplicate items

---

## Error Handling

### Row Skipped - Missing Required Field:
```
Row 5: Missing item name - SKIPPED
```

### Row Error - Invalid Data:
```
Row 7: ERROR - invalid literal for int(): 'abc'
[Full traceback shown]
```

### Warning - Machine Not Found:
```
Row 3: "Ball Bearing" → MEC-0001 - CREATED
  ⚠️  Machine "XYZ-999" not found
```

**Import continues** even if some rows have errors!

---

## Best Practices

### Preparing Excel File:

1. **Use Sample Data** as reference
2. **Check machine names** match database exactly
3. **Use consistent naming** for manufacturers
4. **Include part numbers** when available
5. **Set realistic min/max** stock levels
6. **Verify categories** are spelled correctly
7. **Test with few rows** first

### Before Import:

1. **Backup database**
   ```bash
   python manage.py dumpdata core.Spares > spares_backup.json
   ```

2. **Test with sample**
   ```bash
   # Import just the sample data first
   python manage.py import_spares_excel INVENTORY_IMPORT_TEMPLATE.xlsx
   ```

3. **Verify results** before full import

### After Import:

1. **Check inventory page** - Verify items appear
2. **View history** - Check transactions created
3. **Test filters** - Try machine filter
4. **Verify codes** - Check auto-generated codes
5. **Check machines** - Verify associations

---

## Troubleshooting

### Error: "openpyxl not installed"
```bash
pip install openpyxl
```

### Error: "File not found"
```bash
# Use full path
python manage.py import_spares_excel "D:\path\to\file.xlsx"
```

### Error: "User 'admin' not found"
```bash
# Create superuser
python manage.py createsuperuser

# Or specify different user
python manage.py import_spares_excel file.xlsx --user your_username
```

### Warning: "Machine not found"
- Check machine name spelling
- Verify machine exists in database
- Machine names are case-insensitive but must match exactly

### Items Not Showing:
- Check import output for errors
- Verify categories are correct
- Check if items were actually created
- Refresh browser (Ctrl+F5)

---

## Advanced Usage

### Import Large Files:
```bash
# The script processes row by row
# Even 1000+ rows work fine
# Errors in one row don't stop the import
```

### Update Existing Inventory:
```bash
# Export current inventory (future feature)
# Modify quantities in Excel
# Re-import to update
# Uses ADJUSTMENT transactions
```

### Bulk Machine Linking:
```
All molding machines need same bearing:
Row 2: Ball Bearing, mechanical, ..., M-100, M-101, M-102, M-103
→ Automatically linked to all 4 machines
```

---

## Template File Contents

### Tab 1: Inventory Template (Empty)
```
| Item Name | Category | Description | Manufacturer | ... |
|-----------|----------|-------------|--------------|-----|
| [EMPTY]   |          |             |              |     |
| [EMPTY]   |          |             |              |     |
```

### Tab 2: Instructions (Full Guide)
- How to use
- Column descriptions
- Category values
- Important notes
- Examples

### Tab 3: Sample Data (6 Examples)
- Ball Bearing (mechanical, with machines)
- Hydraulic Oil (hydraulic, general)
- Relay Switch (electrical, with machines)
- Pneumatic Cylinder (pneumatic)
- Safety Gloves (safety, general)
- Screws Kit (general)

---

## Import Statistics

After import, you'll see:
```
Total rows processed: 50
✓ Created: 45
⚠️  Updated: 2
⊝ Skipped: 1
✗ Errors: 2
```

**Means:**
- 45 new items created
- 2 existing items updated
- 1 duplicate skipped (with --skip-duplicates)
- 2 rows had errors (missing required fields)

---

## What Gets Auto-Generated

### Item Codes:
```
Row 1: mechanical → MEC-0001
Row 2: electrical → ELE-0001
Row 3: mechanical → MEC-0002
Row 4: hydraulic → HYD-0001
```

Sequential within each category!

### Transactions:
```
For each item imported:
- Type: RECEIPT
- User: Specified user (default: admin)
- Reason: "Initial stock - Excel import"
- Timestamp: Import time (Karachi timezone)
```

### Manufacturer Records:
```
If manufacturer doesn't exist:
→ Creates new manufacturer automatically
→ Uses in future imports
```

---

## Example Workflow

### Complete Import Process:

**Step 1: Generate Template**
```bash
python create_inventory_template.py
```
Output: `INVENTORY_IMPORT_TEMPLATE.xlsx` created ✓

**Step 2: Fill Data**
Open Excel, go to "Inventory Template" sheet:
```
Row 2: Ball Bearing, mechanical, ..., SKF, 6205-2RS, 50, pcs, 10, 100, 250.00, M-100
Row 3: Hydraulic Oil, hydraulic, ..., Shell, ..., 200, l, 50, 500, 1500.00, (empty)
Row 4: Relay Switch, electrical, ..., Schneider, ..., 15, pcs, 5, 30, 450.00, M-100, P-200
... (add more rows)
```

**Step 3: Save File**
Save as: `my_inventory.xlsx`

**Step 4: Import**
```bash
python manage.py import_spares_excel my_inventory.xlsx
```

**Step 5: Review Output**
```
Row 2: "Ball Bearing" → MEC-0001 - CREATED
  ✓ Linked to machine: M-100
Row 3: "Hydraulic Oil" → HYD-0001 - CREATED
Row 4: "Relay Switch" → ELE-0001 - CREATED
  ✓ Linked to machine: M-100
  ✓ Linked to machine: P-200

✓ Created: 3
```

**Step 6: Verify in Browser**
```
Go to: http://127.0.0.1:8000/home/spares

See:
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ Ball Bearing     │  │ Hydraulic Oil    │  │ Relay Switch     │
│ MEC-0001        │  │ HYD-0001        │  │ ELE-0001        │
│ 📊 SKF          │  │ 📊 Shell        │  │ 📊 Schneider    │
│ 📦 50 pcs       │  │ 📦 200 l        │  │ 📦 15 pcs       │
│ ⚙️ Used by: 1   │  │ ⚙️ General      │  │ ⚙️ Used by: 2   │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

---

## Tips for Large Imports

### Organize Your Data:

**Group by Category:**
```
Rows 2-50:   Electrical parts
Rows 51-100: Mechanical parts
Rows 101-150: Hydraulic parts
```

**Benefits:**
- Easier to review
- Code numbers stay together (ELE-0001 to ELE-0049)
- Simpler to manage

### Start Small:

**First Import:** 10-20 items
```bash
python manage.py import_spares_excel test_batch_1.xlsx
```
→ Verify everything works

**Then:** Import rest
```bash
python manage.py import_spares_excel full_inventory.xlsx
```

### Use Manufacturer Part Numbers:

**Why:**
- Prevents duplicates
- Better identification
- Professional tracking
- Easier reordering

**Example:**
```
Without: "Ball Bearing" (vague, might duplicate)
With: "6205-2RS" (exact, prevents duplicates)
```

---

## Common Scenarios

### Scenario 1: Initial System Setup

**Goal:** Import 200 spare parts for new system

**Steps:**
```
1. Export current inventory from old system (if any)
2. Format into template (copy-paste columns)
3. Verify machine names match
4. Import in batches:
   - Batch 1: 50 items (test)
   - Batch 2: 150 items (rest)
5. Verify all items imported
```

### Scenario 2: Adding New Category of Parts

**Goal:** Add 30 electrical items

**Steps:**
```
1. Create new Excel with just electrical items
2. Category column: all "electrical"
3. Import
4. Codes auto-generated: ELE-0001 to ELE-0030
```

### Scenario 3: Updating Stock Levels

**Goal:** Update quantities for existing items

**Steps:**
```
1. Export current data (or prepare Excel with item names)
2. Update "Initial Quantity" column
3. Import (without --skip-duplicates)
4. Existing items updated
5. ADJUSTMENT transactions created
```

### Scenario 4: Bulk Machine Linking

**Goal:** Link all mechanical parts to molding machines

**Steps:**
```
1. List all mechanical items in Excel
2. Machine Names: "M-100, M-101, M-102, M-103"
3. Import
4. All linked to 4 machines automatically
```

---

## Verification Checklist

After import, check:

- [ ] All items appear on inventory page
- [ ] Item codes auto-generated correctly
- [ ] Categories correct (check badges/filters)
- [ ] Quantities match Excel
- [ ] Manufacturers created/linked
- [ ] Machines linked correctly (check badges)
- [ ] Min/max stock levels set
- [ ] Transactions created (check History)
- [ ] No duplicate items
- [ ] All required machines exist

---

## Template Download

To recreate template:
```bash
python create_inventory_template.py
```

Generates: `INVENTORY_IMPORT_TEMPLATE.xlsx`

**Includes:**
- ✅ Formatted headers
- ✅ Column sizing
- ✅ Detailed instructions
- ✅ Sample data examples
- ✅ Professional formatting

---

## Files Created

1. **create_inventory_template.py** - Template generator script
2. **core/management/commands/import_spares_excel.py** - Import command
3. **INVENTORY_IMPORT_TEMPLATE.xlsx** - Excel template (after running script)

---

## Quick Reference

### Generate Template:
```bash
python create_inventory_template.py
```

### Import Data:
```bash
python manage.py import_spares_excel INVENTORY_IMPORT_TEMPLATE.xlsx
```

### Import with Options:
```bash
python manage.py import_spares_excel file.xlsx --user john --skip-duplicates
```

### Verify Import:
```
Browser: http://127.0.0.1:8000/home/spares
Click: "History" on any imported item
```

---

## Benefits

### For Initial Setup:
✅ Import 100s of items in minutes  
✅ Auto-generate all codes  
✅ Link to machines in bulk  
✅ Create transaction records  

### For Data Entry:
✅ Excel familiar to everyone  
✅ Copy-paste from existing lists  
✅ Bulk edit capabilities  
✅ No web form fatigue  

### For Data Quality:
✅ Validates all data  
✅ Auto-generates codes  
✅ Prevents duplicates  
✅ Creates audit trail  

### For Compliance:
✅ Transaction records  
✅ User attribution  
✅ Timestamps  
✅ Complete audit trail  

---

## Conclusion

The Excel import system provides:

✅ **Professional template** with instructions  
✅ **Bulk import** capability  
✅ **Auto-code generation** during import  
✅ **Duplicate detection** and handling  
✅ **Machine linking** in bulk  
✅ **Transaction logging** for audit  
✅ **Error handling** with detailed messages  
✅ **Flexible options** (skip duplicates, specify user)  

**Perfect for:**
- Initial system setup
- Bulk data entry
- Inventory migrations
- Regular updates
- Audit compliance

Now you can set up your entire inventory from a single Excel file! 🎊

