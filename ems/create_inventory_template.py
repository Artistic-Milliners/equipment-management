"""
Script to create Excel template for inventory import
Run: python create_inventory_template.py
"""
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def create_template():
    # Create workbook
    wb = openpyxl.Workbook()
    
    # Template sheet
    ws_template = wb.active
    ws_template.title = "Inventory Template"
    
    # Headers
    headers = [
        'Item Name',
        'Category',
        'Description',
        'Manufacturer',
        'Manufacturer Part Number',
        'Initial Quantity',
        'Unit',
        'Min Stock Level',
        'Max Stock Level',
        'Unit Price',
        'Machine Names (comma-separated)'
    ]
    
    # Style for headers
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # Write headers
    for col_num, header in enumerate(headers, 1):
        cell = ws_template.cell(row=1, column=col_num)
        cell.value = header
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment
        cell.border = thin_border
    
    # Set column widths
    column_widths = [30, 15, 40, 20, 25, 15, 10, 15, 15, 12, 35]
    for col_num, width in enumerate(column_widths, 1):
        ws_template.column_dimensions[get_column_letter(col_num)].width = width
    
    # Freeze header row
    ws_template.freeze_panes = 'A2'
    
    # Add instructions sheet
    ws_instructions = wb.create_sheet("Instructions")
    
    instructions = [
        ["INVENTORY IMPORT TEMPLATE - INSTRUCTIONS", ""],
        ["", ""],
        ["How to Use This Template:", ""],
        ["", ""],
        ["1. Fill Data", "Fill in the 'Inventory Template' sheet with your spare parts data"],
        ["2. Save File", "Save this file as Excel (.xlsx)"],
        ["3. Run Command", "python manage.py import_spares_excel path/to/file.xlsx"],
        ["4. Verify", "Check the inventory page to verify imported items"],
        ["", ""],
        ["COLUMN DESCRIPTIONS:", ""],
        ["", ""],
        ["Column", "Description", "Required?", "Example"],
        ["Item Name", "Name of the spare part", "YES", "Ball Bearing 6205"],
        ["Category", "electrical, mechanical, hydraulic, pneumatic, safety, general", "YES", "mechanical"],
        ["Description", "Detailed description and specifications", "No", "Deep groove ball bearing, sealed both sides"],
        ["Manufacturer", "Manufacturer name (will be created if doesn't exist)", "No", "SKF"],
        ["Manufacturer Part Number", "Official manufacturer part number", "No", "6205-2RS"],
        ["Initial Quantity", "Opening stock quantity", "YES", "50"],
        ["Unit", "pcs, kg, m, l, box, set, roll, pack", "YES", "pcs"],
        ["Min Stock Level", "Minimum stock before alert", "No", "10"],
        ["Max Stock Level", "Maximum/target stock level", "No", "100"],
        ["Unit Price", "Price per unit in Rs.", "No", "250.00"],
        ["Machine Names", "Comma-separated machine names (must exist in database)", "No", "M-100, M-101, P-200"],
        ["", ""],
        ["IMPORTANT NOTES:", ""],
        ["", ""],
        ["✓ Item Code", "Will be AUTO-GENERATED based on category (e.g., MEC-0001, ELE-0002)"],
        ["✓ Category Values", "Must be exactly: electrical, mechanical, hydraulic, pneumatic, safety, or general"],
        ["✓ Required Fields", "Item Name, Category, Initial Quantity, Unit are REQUIRED"],
        ["✓ Machines", "Machine names must EXACTLY match existing machines in database"],
        ["✓ Duplicates", "Items with same manufacturer part number will be updated, not duplicated"],
        ["✓ Transactions", "All imports create RECEIPT transactions for audit trail"],
        ["", ""],
        ["CATEGORY PREFIXES:", ""],
        ["", ""],
        ["electrical", "→", "ELE-####", "Example: ELE-0001, ELE-0002"],
        ["mechanical", "→", "MEC-####", "Example: MEC-0001, MEC-0002"],
        ["hydraulic", "→", "HYD-####", "Example: HYD-0001, HYD-0002"],
        ["pneumatic", "→", "PNE-####", "Example: PNE-0001, PNE-0002"],
        ["safety", "→", "SAF-####", "Example: SAF-0001, SAF-0002"],
        ["general", "→", "GEN-####", "Example: GEN-0001, GEN-0002"],
        ["", ""],
        ["EXAMPLES:", ""],
        ["", ""],
        ["Example 1: Machine-Specific Part", ""],
        ["Item Name", "Ball Bearing 6205"],
        ["Category", "mechanical"],
        ["Manufacturer", "SKF"],
        ["Part Number", "6205-2RS"],
        ["Quantity", "50"],
        ["Unit", "pcs"],
        ["Min Stock", "10"],
        ["Max Stock", "100"],
        ["Price", "250.00"],
        ["Machines", "M-100, M-101"],
        ["→ Result", "MEC-0001 - Ball Bearing 6205 (linked to 2 machines)"],
        ["", ""],
        ["Example 2: General Purpose Part", ""],
        ["Item Name", "Hydraulic Oil SAE 10"],
        ["Category", "hydraulic"],
        ["Quantity", "200"],
        ["Unit", "l"],
        ["Machines", "(leave empty for general purpose)"],
        ["→ Result", "HYD-0001 - Hydraulic Oil SAE 10 (general purpose)"],
    ]
    
    # Write instructions
    for row_num, instruction in enumerate(instructions, 1):
        for col_num, value in enumerate(instruction, 1):
            cell = ws_instructions.cell(row=row_num, column=col_num)
            cell.value = value
            
            # Style title
            if row_num == 1:
                cell.font = Font(bold=True, size=14, color="FFFFFF")
                cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            
            # Style headers
            if row_num in [10, 13, 23, 29, 35]:
                cell.font = Font(bold=True, size=12)
                cell.fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
    
    # Set column widths for instructions
    ws_instructions.column_dimensions['A'].width = 30
    ws_instructions.column_dimensions['B'].width = 50
    ws_instructions.column_dimensions['C'].width = 20
    ws_instructions.column_dimensions['D'].width = 30
    
    # Create sample data sheet
    ws_sample = wb.create_sheet("Sample Data")
    
    # Headers
    for col_num, header in enumerate(headers, 1):
        cell = ws_sample.cell(row=1, column=col_num)
        cell.value = header
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment
        cell.border = thin_border
    
    # Sample data
    sample_data = [
        ['Ball Bearing 6205', 'mechanical', 'Deep groove ball bearing, sealed both sides', 'SKF', '6205-2RS', 50, 'pcs', 10, 100, 250.00, 'M-100, M-101'],
        ['Hydraulic Oil SAE 10', 'hydraulic', '10W hydraulic oil for general use', 'Shell', 'SHELL-HYD-10', 200, 'l', 50, 500, 1500.00, ''],
        ['Relay Switch 24V DC', 'electrical', '24V DC relay switch, 10A rated', 'Schneider', 'RLY-24V-10A', 15, 'pcs', 5, 30, 450.00, 'M-100, P-200'],
        ['Pneumatic Cylinder 50mm', 'pneumatic', '50mm bore pneumatic cylinder, double acting', 'Festo', 'DSBC-50-100', 8, 'pcs', 2, 10, 3500.00, 'P-200'],
        ['Safety Gloves (Pair)', 'safety', 'Heat resistant safety gloves, size L', 'Ansell', 'ANSELL-HYP-L', 50, 'pairs', 20, 100, 350.00, ''],
        ['Screws & Bolts Kit', 'general', 'Assorted M6-M12 screws and bolts', 'Generic', '', 500, 'pcs', 100, 1000, 5.00, ''],
    ]
    
    for row_num, data in enumerate(sample_data, 2):
        for col_num, value in enumerate(data, 1):
            cell = ws_sample.cell(row=row_num, column=col_num)
            cell.value = value
            cell.border = thin_border
            
            # Align numbers
            if col_num in [6, 8, 9, 10]:  # Quantity columns
                cell.alignment = Alignment(horizontal="right")
    
    # Set column widths
    for col_num, width in enumerate(column_widths, 1):
        ws_sample.column_dimensions[get_column_letter(col_num)].width = width
    
    # Save workbook
    filename = 'INVENTORY_IMPORT_TEMPLATE.xlsx'
    wb.save(filename)
    
    print(f'✓ Excel template created: {filename}')
    print(f'\nTemplate includes:')
    print(f'  1. "Inventory Template" - Empty template for your data')
    print(f'  2. "Instructions" - Detailed guide on how to use')
    print(f'  3. "Sample Data" - 6 example rows showing format')
    print(f'\nNext steps:')
    print(f'  1. Open {filename}')
    print(f'  2. Go to "Inventory Template" sheet')
    print(f'  3. Fill in your spare parts data')
    print(f'  4. Save the file')
    print(f'  5. Run: python manage.py import_spares_excel {filename}')
    print(f'\n✓ Done!')

if __name__ == '__main__':
    try:
        create_template()
    except ImportError:
        print('✗ Error: openpyxl not installed')
        print('Install it with: pip install openpyxl')
    except Exception as e:
        print(f'✗ Error: {e}')
        import traceback
        traceback.print_exc()

