# Machine-Spare Relationship Feature

## Overview
Link spare parts to specific machines to track which spares are used by which machines. This helps with maintenance planning, stock management, and cost allocation.

## ✅ What Was Added

### 1. **Machine Selection in Add Form**

When adding a new spare, users can now select which machines use this part:

```
┌──────────────────────────────────────────────┐
│ Machine Association                          │
│                                              │
│ Which machines use this spare?               │
│ ┌──────────────────────────────────────────┐│
│ │ -- No machines selected --               ││
│ │ Molding Machine M-100 - Injection        ││
│ │ Press Machine P-200 - Hydraulic Press   ││
│ │ Finishing Machine F-300 - Finishing     ││
│ │ Packing Line PL-400 - Packaging         ││
│ └──────────────────────────────────────────┘│
│                                              │
│ Hold Ctrl/Cmd to select multiple            │
│ Leave empty for general-purpose spares       │
└──────────────────────────────────────────────┘
```

### 2. **Machine Display on Spare Cards**

Each spare card now shows which machines use it:

#### Example 1: Specific Machine Spare
```
┌────────────────────────────┐
│ Ball Bearing 6205          │
│ 📊 MEC-0001                │
│ 🏭 SKF                     │
│ 🏷️ 6205-2RS               │
│                            │
│ 📦 Quantity: 50 pcs        │
│                            │
│ ⚙️ Used by: 2 machines    │
│ [M-100] [P-200]           │
│                            │
│ Stock Level    Min: 10     │
│ [████████████░░░] 75%      │
└────────────────────────────┘
```

#### Example 2: General Purpose Spare
```
┌────────────────────────────┐
│ Hydraulic Oil SAE 10       │
│ 📊 HYD-0001                │
│                            │
│ 📦 Quantity: 200 l         │
│                            │
│ ⚙️ General purpose spare  │
│                            │
│ Stock Level    Min: 50     │
│ [████████████████] 100%    │
└────────────────────────────┘
```

#### Example 3: Multiple Machines
```
┌────────────────────────────┐
│ Drive Belt Type-A          │
│ 📊 MEC-0005                │
│                            │
│ 📦 Quantity: 15 pcs        │
│                            │
│ ⚙️ Used by: 5 machines    │
│ [M-100] [M-101] +3 more   │
│                            │
│ Stock Level    Min: 5      │
│ [████████░░░░░░░] 60%      │
└────────────────────────────┘
```

### 3. **Backend Integration**

The relationship is stored in the `MachineSpares` table:
```
Machine ID | Spare ID
-----------|---------
    1      |   45
    2      |   45
    3      |   45
```

### 4. **API Enhancement**

The spare details API now includes machine information:
```json
{
  "success": true,
  "data": {
    "item_code": "MEC-0001",
    "name": "Ball Bearing 6205",
    "quantity": 50,
    "machines_using": [
      {
        "id": 1,
        "name": "Molding Machine M-100",
        "type": "Injection Molding"
      },
      {
        "id": 2,
        "name": "Press Machine P-200",
        "type": "Hydraulic Press"
      }
    ],
    "machines_count": 2
  }
}
```

## Benefits

### For Maintenance Planning:
✅ **Know which spares are needed for each machine**  
✅ **Plan preventive maintenance based on spare availability**  
✅ **See which machines will be affected if spare is out of stock**  

### For Inventory Management:
✅ **Track spare usage per machine**  
✅ **Better stock level planning (more machines = higher min stock)**  
✅ **Identify machine-specific vs. general-purpose spares**  

### For Cost Allocation:
✅ **Allocate spare costs to specific machines**  
✅ **Track total maintenance cost per machine**  
✅ **Generate machine-wise expense reports**  

### For Purchasing:
✅ **Order right quantities based on number of machines**  
✅ **Prioritize spares used by critical machines**  
✅ **Better vendor negotiations (bulk orders for common spares)**  

## How It Works

### Adding a New Spare with Machine Association:

**Step 1:** User fills basic information
- Name: "Ball Bearing"
- Category: "Mechanical"
- Manufacturer: "SKF"

**Step 2:** User selects machines
- Selects: "Molding Machine M-100"
- Selects: "Press Machine P-200"
- (Holds Ctrl to select multiple)

**Step 3:** User saves
- Spare is created with code: `MEC-0001`
- System creates 2 `MachineSpares` entries:
  - M-100 ↔ MEC-0001
  - P-200 ↔ MEC-0001

**Result:**
```
✓ Item added successfully with code: MEC-0001 (Linked to 2 machine(s))
```

### Viewing Spare Cards:

**User sees:**
```
Ball Bearing (MEC-0001)
⚙️ Used by: 2 machines
[M-100] [P-200]
```

**Quick insights:**
- This spare is used by 2 machines
- If stock runs out, 2 machines will be affected
- Need to maintain higher stock level

### Adding General-Purpose Spare:

**User adds:**
- Name: "Screws & Bolts (small)"
- Category: "General"
- Machines: **(leaves empty)**

**Result:**
```
✓ Item added successfully with code: GEN-0014
```

**Display:**
```
Screws & Bolts (GEN-0014)
⚙️ General purpose spare
```

## Use Cases

### Use Case 1: Machine-Specific Parts

**Scenario:** Molding Machine M-100 uses a specific type of heating element

**Solution:**
```
Add Spare:
  Name: Heating Element Type-HE500
  Category: Electrical
  Machines: [M-100]
  Quantity: 2
  Min Stock: 1
```

**Benefit:** When issuing this part, system knows exactly which machine it's for

### Use Case 2: Common Parts Across Multiple Machines

**Scenario:** All injection molding machines use the same hydraulic seals

**Solution:**
```
Add Spare:
  Name: Hydraulic Seal 50mm
  Category: Hydraulic
  Machines: [M-100, M-101, M-102, M-103]
  Quantity: 20
  Min Stock: 8 (2 per machine)
```

**Benefit:** 
- Stock level reflects usage across 4 machines
- Alerts trigger before any machine runs out
- Can see which machines will be affected

### Use Case 3: Planning Preventive Maintenance

**Scenario:** Need to do preventive maintenance on all molding machines

**Steps:**
1. Filter spares by "Used by Molding Machines"
2. Check stock levels for all required spares
3. Order any parts below minimum
4. Schedule maintenance when all parts available

### Use Case 4: Cost Tracking

**Scenario:** Want to know total spare costs for Machine M-100

**Query:** 
```sql
SELECT SUM(s.unit_price * st.quantity)
FROM spare_transactions st
JOIN spares s ON st.spare_id = s.id
WHERE st.machine_id = 100  -- M-100
  AND st.transaction_type = 'ISSUE'
  AND st.created_at >= '2024-01-01'
```

**Result:** Total spare costs for M-100 in 2024

## Database Structure

### Existing Many-to-Many Relationship:

```python
# In Machines model
machine_spare = models.ManyToManyField(
    Spares, 
    related_name='machines',
    through="MachineSpares",
    blank=True
)

# Through table
class MachineSpares(models.Model):
    spare = models.ForeignKey(Spares, on_delete=models.CASCADE)
    machine = models.ForeignKey(Machines, on_delete=models.CASCADE)
```

### Querying:

```python
# Get all spares for a machine
machine = Machines.objects.get(pk=1)
spares = machine.machine_spare.all()

# Get all machines using a spare
spare = Spares.objects.get(pk=45)
machines = spare.machines.all()

# Count machines using a spare
count = spare.machines.count()
```

## Display Logic

### In Template:
```django
{% with machine_count=spare.machines.count %}
{% if machine_count > 0 %}
    Used by: {{ machine_count }} machine{{ machine_count|pluralize }}
    {% for machine in spare.machines.all|slice:":2" %}
        <span class="badge">{{ machine.name }}</span>
    {% endfor %}
    {% if machine_count > 2 %}
        <span class="badge">+{{ machine_count|add:"-2" }} more</span>
    {% endif %}
{% else %}
    General purpose spare
{% endif %}
{% endwith %}
```

## Future Enhancements

### 1. Machine-Specific Stock Levels
```
Min stock = Number of machines × Recommended stock per machine
Example: 4 machines × 2 units = 8 minimum
```

### 2. Smart Reorder Alerts
```
Alert: "Hydraulic Seal 50mm is low. 
This affects 4 machines: M-100, M-101, M-102, M-103"
```

### 3. Machine Spare List View
```
View all spares for Machine M-100:
- Ball Bearing 6205 (Stock: 50)
- Hydraulic Seal 50mm (Stock: 5) ⚠️ LOW
- Heating Element (Stock: 2)
```

### 4. Compatibility Checking
```
When issuing spare to Machine X:
- Check if spare is compatible with Machine X
- Warn if spare is not linked to that machine
```

### 5. Bulk Association
```
"Link this spare to all injection molding machines"
Automatically selects all machines of type "Injection Molding"
```

## Testing Checklist

- [x] ✅ Machine dropdown appears in add form
- [x] ✅ Multiple machines can be selected
- [x] ✅ Backend creates machine relationships
- [x] ✅ Success message shows machine count
- [x] ✅ Spare cards display machine badges
- [x] ✅ "General purpose" shown if no machines
- [x] ✅ API returns machine information
- [ ] ⏳ Can add spare and link to 1 machine
- [ ] ⏳ Can add spare and link to multiple machines
- [ ] ⏳ Can add spare with no machines
- [ ] ⏳ Machine badges display correctly
- [ ] ⏳ "+X more" badge shows for >2 machines

## Migration Notes

### For Existing Spares

Existing spares won't have machine associations. This is fine:
- They'll show as "General purpose spare"
- You can edit them later to add machines
- Or leave them as general-purpose

### No Data Migration Needed

The relationship is optional (`blank=True`), so:
- Existing data works as-is
- No migration script needed
- Add relationships as needed

## Files Modified

1. `User/templates/user/sparesDetail.html` - Added machine selector and display
2. `User/views.py` - Updated to handle machine relationships
3. Documentation added

## Conclusion

The machine-spare relationship feature provides:
- **Better visibility** into which machines use which spares
- **Smarter stock management** based on machine count
- **Cost tracking** per machine
- **Maintenance planning** capabilities

All while maintaining backward compatibility with existing data!

