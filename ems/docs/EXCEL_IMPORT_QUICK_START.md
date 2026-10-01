# Excel Import - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Package (One-Time)
```bash
pip install openpyxl
```

### Step 2: Generate Template
```bash
python create_inventory_template.py
```

**Output:**
```
✓ Excel template created: INVENTORY_IMPORT_TEMPLATE.xlsx

Template includes:
  1. "Inventory Template" - Empty template for your data
  2. "Instructions" - Detailed guide on how to use
  3. "Sample Data" - 6 example rows showing format
```

### Step 3: Fill Your Data

Open `INVENTORY_IMPORT_TEMPLATE.xlsx`:

**Option A - Start Fresh:**
- Go to "Inventory Template" tab
- Fill in your spare parts (see Instructions tab)

**Option B - Use Sample:**
- Go to "Sample Data" tab
- Copy the 6 sample rows
- Paste to "Inventory Template" tab
- Modify as needed

### Step 4: Import
```bash
python manage.py import_spares_excel INVENTORY_IMPORT_TEMPLATE.xlsx
```

### Step 5: Check Results
```
Browser: http://127.0.0.1:8000/home/spares
→ See your imported items with auto-generated codes!
```

---

## 📋 Excel Template Columns

| Column | Required | Example |
|--------|----------|---------|
| Item Name | ✅ | Ball Bearing 6205 |
| Category | ✅ | mechanical |
| Description | No | Deep groove ball bearing |
| Manufacturer | No | SKF |
| Manufacturer Part Number | No | 6205-2RS |
| Initial Quantity | ✅ | 50 |
| Unit | ✅ | pcs |
| Min Stock Level | No | 10 |
| Max Stock Level | No | 100 |
| Unit Price | No | 250.00 |
| Machine Names | No | M-100, M-101 |

---

## 📝 Fill Example

```
Row 2:
Item Name: Ball Bearing 6205
Category: mechanical
Description: Deep groove ball bearing, sealed both sides
Manufacturer: SKF
Part Number: 6205-2RS
Quantity: 50
Unit: pcs
Min: 10
Max: 100
Price: 250.00
Machines: M-100, M-101
```

**Save and import!**

---

## ✅ Categories (Must Use Exact Names)

- `electrical` → ELE-####
- `mechanical` → MEC-####
- `hydraulic` → HYD-####
- `pneumatic` → PNE-####
- `safety` → SAF-####
- `general` → GEN-####

---

## 🎯 What You Get

After import:
```
✓ Auto-generated item codes (MEC-0001, ELE-0002, etc.)
✓ Items appear on inventory page
✓ Machine associations created
✓ Transaction history logged
✓ Manufacturers created
✓ Ready to use immediately!
```

---

## ⚠️ Important Notes

1. **Categories** - Must be lowercase (mechanical, not Mechanical)
2. **Machine Names** - Must match database exactly
3. **Required Fields** - Name, Category, Quantity, Unit
4. **Duplicates** - Same part number = updates existing item
5. **Codes** - AUTO-GENERATED, don't include in Excel!

---

## 🧪 Quick Test

### Test with 3 Items:

**Row 2:** Ball Bearing, mechanical, SKF, 6205-2RS, 50, pcs, 10, 100, 250.00, M-100  
**Row 3:** Hydraulic Oil, hydraulic, Shell, , 200, l, 50, 500, 1500.00,  
**Row 4:** Screws Kit, general, , , 500, pcs, 100, 1000, 5.00,  

Import and check!

---

## 📖 Full Documentation

See **EXCEL_IMPORT_GUIDE.md** for:
- Detailed column descriptions
- Advanced options
- Troubleshooting
- Best practices
- Examples and scenarios

---

**Ready to import your inventory? Generate the template now!** 🎊

```bash
python create_inventory_template.py
```

