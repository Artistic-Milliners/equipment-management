# CSV Export Feature - Inventory Management

## 🎯 Overview

Export inventory data and transaction histories to CSV format for further analysis, reporting, and record-keeping.

---

## 📊 Two Export Types

### 1. **Full Inventory Export**
Exports all spare parts with complete details

### 2. **Transaction History Export**
Exports transaction ledger for a specific item

---

## 🚀 How to Use

### **Export Full Inventory:**

1. Go to Inventory Management page: `/home/spares`
2. Click the **"Export"** button at the top right
3. CSV file downloads automatically
4. File name format: `inventory_export_YYYYMMDD_HHMMSS.csv`

**Example:** `inventory_export_20251031_143022.csv`

---

### **Export Transaction History:**

1. Go to Inventory Management page
2. Click **"History"** button on any item card
3. Transaction Ledger modal opens
4. Click **"Export CSV"** button in the modal
5. CSV file downloads automatically
6. File name format: `{ITEM_CODE}_transactions_YYYYMMDD_HHMMSS.csv`

**Example:** `ELE-0001_transactions_20251031_143230.csv`

---

## 📄 CSV File Contents

### **Full Inventory Export**

**Columns:**
```
1.  Item Code
2.  Name
3.  Description
4.  Category
5.  Manufacturer
6.  Manufacturer Part Number
7.  Quantity
8.  Unit
9.  Min Stock
10. Max Stock
11. Unit Price
12. Stock Status
13. Lead Time (days)
14. Service Life (days)
15. Shelf Life (days)
16. Date of Purchase
17. Machines Using
18. Created Date
19. Updated Date
```

**Example Row:**
```csv
ELE-0001,Ball Bearing,SKF Ball Bearing 6205,Electrical,SKF,6205-2RS,50,Pcs,10,100,250.00,In Stock,7,365,730,2024-01-15,"Machine-1, Machine-2",2025-10-20 10:30:00,2025-10-31 14:25:00
```

---

### **Transaction History Export**

**Header Section:**
```
Transaction History Report
Item Code:,ELE-0001
Item Name:,Ball Bearing
Current Stock:,50,Pcs
Min Stock Level:,10,Pcs
Stock Status:,In Stock
Report Generated:,2025-10-31 14:30:22
```

**Transaction Data Columns:**
```
1. Date & Time
2. Transaction Type
3. Quantity
4. Unit
5. Stock Before
6. Stock After
7. User
8. Machine
9. Work Order
10. Reason
```

**Summary Section:**
```
Summary
Total Transactions:,25
Receipts:,10
Issues:,12
Adjustments:,2
Returns:,1
Damages:,0
```

**Example Transaction Row:**
```csv
2025-10-31 14:25:00,Issue,5,Pcs,55,50,john_doe,Machine-1,WO-12345,Routine maintenance
```

---

## 📋 File Specifications

### **Format:**
- CSV (Comma-Separated Values)
- UTF-8 encoding
- Compatible with Excel, Google Sheets, LibreOffice

### **Timestamps:**
- All timestamps in Karachi Local Time (UTC+5)
- Format: `YYYY-MM-DD HH:MM:SS`

### **Transaction Types:**
- `RECEIPT` - Stock received
- `ISSUE` - Stock issued
- `ADJUSTMENT` - Stock adjusted
- `RETURN` - Stock returned
- `DAMAGE` - Stock damaged

---

## 🔐 Permissions Required

### **Full Inventory Export:**
- Permission: `core.view_spares`
- Groups: Inventory Controller, Engineering, Management

### **Transaction History Export:**
- Permission: `core.view_spares`
- Groups: Inventory Controller, Engineering, Management

**Note:** Inventory Controllers, Engineering, and Management can all export data for reporting purposes.

---

## 💡 Use Cases

### **1. Monthly Inventory Reports**
```
1. Export full inventory at month-end
2. Import into Excel
3. Create pivot tables and charts
4. Share with management
```

### **2. Audit Trail**
```
1. Export transaction history for specific item
2. Review all movements
3. Verify quantities and users
4. Compliance documentation
```

### **3. Low Stock Analysis**
```
1. Export full inventory
2. Filter by quantity < min stock
3. Create purchase orders
4. Track reorder patterns
```

### **4. Cost Analysis**
```
1. Export full inventory with unit prices
2. Calculate total inventory value
3. Identify high-value items
4. Budget planning
```

### **5. Machine-Specific Parts**
```
1. Export full inventory
2. Filter by specific machine
3. Create machine-specific spare kits
4. Maintenance planning
```

---

## 📊 Opening CSV Files

### **In Excel:**
```
1. Download CSV file
2. Open Excel
3. File → Open → Select CSV file
4. Data imports automatically
5. Format as table (Ctrl+T)
```

### **In Google Sheets:**
```
1. Open Google Sheets
2. File → Import
3. Upload CSV file
4. Import location: Replace spreadsheet
5. Separator type: Comma
6. Click "Import data"
```

### **In LibreOffice Calc:**
```
1. Download CSV file
2. Open LibreOffice Calc
3. File → Open → Select CSV file
4. Set character set: UTF-8
5. Set separator: Comma
6. Click OK
```

---

## 🎨 Example Uses in Excel

### **1. Create Pivot Table:**
```
1. Import CSV
2. Insert → PivotTable
3. Rows: Category
4. Values: Sum of Quantity, Sum of Unit Price
5. Analyze inventory by category
```

### **2. Low Stock Alert:**
```
1. Import CSV
2. Add column: =IF(Quantity<MinStock,"REORDER","OK")
3. Filter for "REORDER"
4. Create purchase list
```

### **3. Value Analysis:**
```
1. Import CSV
2. Add column: =Quantity*UnitPrice
3. Sort by value (descending)
4. Identify high-value items
```

### **4. Transaction Summary:**
```
1. Import transaction CSV
2. PivotTable: Transaction Type vs Count
3. Visualize with chart
4. Monthly trend analysis
```

---

## 🔄 Export Workflow

### **Regular Reporting:**
```
Daily:
- Export transactions for items with activity
- Review and verify

Weekly:
- Export full inventory
- Check low stock items
- Generate purchase requests

Monthly:
- Export full inventory
- Full audit and reconciliation
- Management reports
```

---

## 📁 File Management Tips

### **Naming Convention:**
```
YYYY-MM-DD_inventory_report.csv
YYYY-MM-DD_item-code_transactions.csv
```

### **Organization:**
```
Reports/
├── Inventory/
│   ├── 2025-10/
│   │   ├── 2025-10-01_inventory.csv
│   │   ├── 2025-10-15_inventory.csv
│   │   └── 2025-10-31_inventory.csv
│   └── 2025-11/
└── Transactions/
    ├── ELE-0001/
    │   ├── 2025-10-15_transactions.csv
    │   └── 2025-10-31_transactions.csv
    └── MEC-0002/
```

---

## 🔍 Data Analysis Examples

### **1. Stock Turnover:**
```
From transaction CSV:
- Count issues per item
- Divide by average stock
- Identify fast/slow movers
```

### **2. User Activity:**
```
From transaction CSV:
- Count transactions by user
- Identify active users
- Training needs analysis
```

### **3. Machine Reliability:**
```
From transaction CSV:
- Count issues per machine
- Identify high-maintenance machines
- Spare usage patterns
```

### **4. Cost Tracking:**
```
From inventory CSV:
- Total value = Σ(Quantity × Unit Price)
- Category-wise breakdown
- Budget vs actual analysis
```

---

## ⚡ Quick Reference

| Action | Button Location | File Name Format |
|--------|----------------|------------------|
| **Export All Items** | Top right of inventory page | `inventory_export_YYYYMMDD_HHMMSS.csv` |
| **Export Transactions** | Inside transaction ledger modal | `ITEMCODE_transactions_YYYYMMDD_HHMMSS.csv` |

---

## 🎯 Key Features

✅ **One-Click Export** - No complex setup  
✅ **Automatic Download** - File downloads immediately  
✅ **Timestamped Files** - Never overwrite previous exports  
✅ **Complete Data** - All fields included  
✅ **Ready for Analysis** - Compatible with Excel, Google Sheets  
✅ **Karachi Timezone** - All timestamps in local time  
✅ **Transaction Summary** - Automatic counts by type  
✅ **Professional Format** - Clean, structured CSV  

---

## 🛠️ Technical Details

### **Backend Views:**

**Full Inventory Export:**
```python
@permission_required('core.view_spares', raise_exception=True)
def export_inventory_csv(request):
    # Generates CSV with all spare details
    # URL: /home/spares/export
```

**Transaction History Export:**
```python
@permission_required('core.view_spares', raise_exception=True)
def export_spare_transactions_csv(request, pk):
    # Generates CSV for specific item transactions
    # URL: /home/spares/export/transactions/{pk}
```

### **Frontend Functions:**

```javascript
function exportInventory() {
    // Redirects to inventory export URL
    window.location.href = "{% url 'User:export_inventory_csv' %}";
}

function exportLedger() {
    // Exports current spare's transaction history
    window.location.href = `/home/spares/export/transactions/${currentLedgerSpareId}`;
}
```

---

## 📊 Sample Output

### **Inventory Export Sample:**
```csv
Item Code,Name,Description,Category,Manufacturer,Manufacturer Part Number,Quantity,Unit,Min Stock,Max Stock,Unit Price,Stock Status,Lead Time (days),Service Life (days),Shelf Life (days),Date of Purchase,Machines Using,Created Date,Updated Date
ELE-0001,Ball Bearing,SKF Ball Bearing 6205,Electrical,SKF,6205-2RS,50,Pcs,10,100,250.00,In Stock,7,365,730,2024-01-15,"Machine-1, Machine-2",2025-10-20 10:30:00,2025-10-31 14:25:00
MEC-0002,Hydraulic Oil,Shell Tellus S2 M 46,Mechanical,Shell,Tellus S2 M 46,200,Liters,50,500,450.00,In Stock,14,180,365,2024-02-20,"Machine-3",2025-10-15 09:15:00,2025-10-30 16:45:00
```

### **Transaction Export Sample:**
```csv
Transaction History Report
Item Code:,ELE-0001
Item Name:,Ball Bearing
Current Stock:,50,Pcs
Min Stock Level:,10,Pcs
Stock Status:,In Stock
Report Generated:,2025-10-31 14:30:22

Date & Time,Transaction Type,Quantity,Unit,Stock Before,Stock After,User,Machine,Work Order,Reason
2025-10-31 14:25:00,Issue,5,Pcs,55,50,john_doe,Machine-1,WO-12345,Routine maintenance
2025-10-30 10:15:00,Receipt,20,Pcs,35,55,admin,,,Supplier delivery PO-5678
2025-10-28 16:30:00,Issue,3,Pcs,38,35,jane_smith,Machine-2,WO-12340,Emergency repair

Summary
Total Transactions:,3
Receipts:,1
Issues:,2
Adjustments:,0
Returns:,0
Damages:,0
```

---

## 🎊 Ready to Use!

Simply click the **Export** buttons and your CSV files will download automatically!

**Perfect for:**
- 📊 Management Reports
- 📈 Trend Analysis
- 🔍 Audits
- 💰 Cost Tracking
- 📝 Documentation
- 📧 Sharing with Teams

**Your inventory data is now export-ready!** 🚀

