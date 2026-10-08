from django.db import models
from datetime import datetime, date
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from .fields import UnitIDField
from PIL import Image
from django.db import transaction
from django.utils import timezone

# Create your models here.

class Unit(models.Model):
    id = UnitIDField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)



class Department(models.Model):
    TYPE_CHOICES = (
        ('SERVICES', 'SERVICES'),
        ('PRODUCTION', 'PRODUCTION'),
        ('MAINTENANCE', 'MAINTENANCE')
    )
    name = models.CharField(max_length=255)
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT)
    dpt_type = models.CharField(max_length=50, choices=TYPE_CHOICES, null=True, blank=True)

    def __str__(self):
        return self.name


class Designation(models.Model):
    designation_name = models.CharField(max_length=255, default='Trainee')

    def __str__(self):
        return self.designation_name


class CustomUser(AbstractUser):
    is_employee = models.BooleanField(default=False)
    is_contractor = models.BooleanField(default=False)


class Employee(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, blank=True, null=True)
    designation = models.ForeignKey(Designation, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name



class Contractor(models.Model):
    contractor = models.CharField(max_length=255)

    def __str__(self):
        return self.contractor

class Contractor_Person(models.Model):
    
    contractor_name = models.ForeignKey(Contractor, on_delete=models.CASCADE)
    visiting_person = models.CharField(max_length=255)

    def __str__(self):
        return self.visiting_person

class Manufacturer(models.Model):
    
    name = models.CharField(max_length=255)
    coo = models.CharField(verbose_name="country of origin", max_length=100, null=True)

    def __str__(self) -> str:
        return self.name

class Equipment(models.Model):
    
    name = models.CharField(max_length=255)
    quantity = models.IntegerField()    
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT)
    contractor = models.ForeignKey(Contractor, on_delete=models.PROTECT, null=True, blank=True)
    
    def __str__(self) -> str:
        return self.name
    
class Spares(models.Model):
    
    CATEGORY_CHOICES = [
        ('electrical', 'Electrical'),
        ('mechanical', 'Mechanical'),
        ('hydraulic', 'Hydraulic'),
        ('pneumatic', 'Pneumatic'),
        ('safety', 'Safety'),
        ('general', 'General'),
    ]
    
    CATEGORY_PREFIX = {
        'electrical': 'ELE',
        'mechanical': 'MEC',
        'hydraulic': 'HYD',
        'pneumatic': 'PNE',
        'safety': 'SAF',
        'general': 'GEN',
    }
    
    # Auto-generated unique item code (e.g., ELE-001, MEC-002)
    # Note: unique=True will be added in a later migration after populating existing data
    item_code = models.CharField(max_length=30, editable=False, null=True, blank=True)
    
    # Standardized naming
    name = models.CharField(max_length=255, help_text="Standard item name (e.g., Ball Bearing)")
    description = models.TextField(blank=True, null=True, help_text="Detailed description and specifications")
    
    # Manufacturer information for better identification
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.SET_NULL, null=True, blank=True, 
                                      help_text="Item manufacturer")
    manufacturer_part_number = models.CharField(max_length=100, blank=True, null=True,
                                                 help_text="Official manufacturer part number")
    
    # Stock information
    quantity = models.IntegerField(default=0)
    unit = models.CharField(max_length=50, blank=True, null=True)
    min_stock_level = models.IntegerField(default=5, help_text="Minimum stock level before low stock alert")
    max_stock_level = models.IntegerField(default=100, blank=True, null=True, 
                                           help_text="Maximum stock level for ordering")
    
    # Categorization
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    
    # Additional metadata
    image = models.ImageField(upload_to='inventory/', blank=True, null=True)
    leadtime = models.IntegerField(blank=True, null=True, help_text="Lead time in days")
    shelflife = models.IntegerField(blank=True, null=True, help_text="Shelf life in days")
    servicelife = models.IntegerField(blank=True, null=True, help_text="Service life in days")
    date_of_purchase = models.DateField(default=date.fromisoformat('2024-01-04'))
    
    # Price information
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, 
                                      help_text="Price per unit")
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name = 'Spare Part'
        verbose_name_plural = 'Spare Parts'
        ordering = ['-created_at']  # Changed from item_code since it might be null initially

    def save(self, *args, **kwargs):
        # Auto-generate item code if not set
        if not self.item_code:
            prefix = self.CATEGORY_PREFIX.get(self.category, 'GEN')
            
            # Get the last item code for this category
            last_item = Spares.objects.filter(
                item_code__startswith=prefix
            ).order_by('item_code').last()
            
            if last_item and last_item.item_code:
                # Extract number from last code and increment
                try:
                    last_number = int(last_item.item_code.split('-')[1])
                    new_number = last_number + 1
                except (IndexError, ValueError):
                    new_number = 1
            else:
                new_number = 1
            
            # Generate new code with zero-padding (e.g., ELE-001)
            self.item_code = f"{prefix}-{new_number:04d}"
        
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        if self.manufacturer_part_number:
            return f'{self.item_code} - {self.name} ({self.manufacturer_part_number})'
        return f'{self.item_code} - {self.name}'
    
    @property
    def stock_status(self):
        if self.quantity == 0:
            return 'out-of-stock'
        elif self.quantity <= self.min_stock_level:
            return 'low-stock'
        else:
            return 'in-stock'
    
    @property
    def stock_percentage(self):
        """Calculate stock level as percentage of max stock"""
        if self.max_stock_level and self.max_stock_level > 0:
            return int((self.quantity / self.max_stock_level) * 100)
        return 100 if self.quantity > 0 else 0


class SpareTransaction(models.Model):
    """Track all inventory movements for audit trail"""
    
    TRANSACTION_TYPES = [
        ('RECEIPT', 'Receipt - Stock In'),
        ('ISSUE', 'Issue - Stock Out'),
        ('ADJUSTMENT', 'Stock Adjustment'),
        ('RETURN', 'Return to Stock'),
        ('DAMAGE', 'Damaged/Scrapped'),
    ]
    
    spare = models.ForeignKey(Spares, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField(help_text="Quantity moved (positive or negative)")
    
    # Who did this
    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    
    # Why and where
    reason = models.TextField(help_text="Reason for transaction")
    machine = models.ForeignKey('Machines', on_delete=models.SET_NULL, null=True, blank=True,
                                 help_text="Machine related to this transaction (if applicable)")
    work_order = models.ForeignKey('MachineIssue', on_delete=models.SET_NULL, null=True, blank=True,
                                    help_text="Work order/issue ticket related to this transaction")
    
    # Stock levels at time of transaction
    quantity_before = models.IntegerField(help_text="Stock quantity before transaction")
    quantity_after = models.IntegerField(help_text="Stock quantity after transaction")
    
    # When
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Spare Transaction'
        verbose_name_plural = 'Spare Transactions'
    
    def __str__(self):
        return f"{self.transaction_type}: {self.spare.item_code} - {self.quantity} units by {self.user.username}"


class Machines(models.Model):
    
    name = models.CharField(max_length=50)
    type_of_machine = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='typeOfMachine')
    machine_spare = models.ManyToManyField(Spares,related_name='machines' ,through="MachineSpares", blank=True)
    dop = models.DateField(verbose_name="Date of Purcahse", blank=True, null=True)
    purchase_cost = models.FloatField(default=0)
    model = models.CharField(max_length=50,blank=True, null=True)
    machine_hours = models.IntegerField(blank=True, null=True)
    image = models.ImageField(upload_to='images', blank=True, null=True)
    Department = models.ForeignKey(Department, on_delete=models.CASCADE, blank=True, null=True)
    location = models.CharField(max_length=2000, default="TEST")
    
    # #machine department
    # location = models.CharField(max_length=2000, default="Warehouse")
    # #machine site where it is installed
    # site = models.CharField(max_length=100, default="AM5")

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Save first to ensure the file is written to disk
        super().save(*args, **kwargs)

        # Then process the image if it exists
        if self.image:
            try:
                img = Image.open(self.image.path)
                output_size = (250, 250)
                img.thumbnail(output_size)
                img.save(self.image.path)
            except Exception as e:
                # Log error but don't fail the save operation
                print(f"Error processing image for machine {self.name}: {e}")

class ImageModel(models.Model):
    image = models.ImageField(upload_to='images')


class MachineSpares(models.Model):
    spare = models.ForeignKey(Spares, on_delete=models.CASCADE)
    machine = models.ForeignKey(Machines, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.spare.name}: {self.machine.name}"

class MachineSection(models.Model):
    machine = models.ForeignKey(Machines, on_delete=models.CASCADE, related_name="machine_section", blank=True, null=True)
    section_name = models.CharField(max_length=100)

    def __str__(self):
        return self.section_name

class IssueList(models.Model):
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        related_name="created_issue_list_entries",
        null=True,
        blank=True,
        help_text="Engineer who added this issue to the master list"
    )
    error_code = models.CharField(max_length = 35, null=True, default=None)
    programmer_string = models.CharField(max_length=100, null=True, default=None)
    machine_string = models.CharField(max_length=100, null=True, default=None)
    c_desc = models.TextField(default="EMPTY",verbose_name="code description")
    effect = models.TextField(max_length=250,blank=True,null=True)
    machine_status = models.CharField(max_length=250, blank=True, null=True)
    restart_procedure = models.TextField(max_length=500, blank=True, null=True)
    flashes = models.IntegerField(blank=True, null=True)
    image = models.ImageField(upload_to='images', blank=True, null=True)
    equipment = models.ForeignKey(Equipment, on_delete=models.PROTECT, related_name="equipment")

    def __str__(self):
        return f"Machine: {self.c_desc}"


class TemporaryIssue(models.Model):
    """
    Temporary storage for user-reported issues not yet in the master IssueList.
    Engineer reviews and can promote to IssueList if valid.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name="temporary_issues")
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name="temp_issues")
    machine = models.ForeignKey(Machines, on_delete=models.CASCADE, null=True, blank=True, related_name="temp_issues")

    # User's description of the issue
    user_description = models.TextField(help_text="User-reported issue description")

    # Tracking fields
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default=False, help_text="Has an engineer reviewed this?")
    promoted_to_issuelist = models.BooleanField(default=False, help_text="Has this been added to master IssueList?")
    promoted_issue = models.ForeignKey(IssueList, on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name="promoted_from_temp",
                                        help_text="Link to IssueList record if promoted")

    # Engineer notes during review
    engineer_notes = models.TextField(blank=True, null=True, help_text="Engineer corrections/notes")
    reviewed_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name="reviewed_temp_issues")

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Temporary Issue Report'
        verbose_name_plural = 'Temporary Issue Reports'

    def __str__(self):
        return f"Temp Issue: {self.user_description[:50]} - {self.equipment.name}"


def get_department():
    return Department.objects.get(name="Workshop").pk


class MachineIssue(models.Model):

    # Status constants
    STATUS_PENDING = 'PENDING'
    STATUS_IN_PROGRESS = 'IN_PROGRESS'
    STATUS_USER_FEEDBACK = 'User Feedback'
    STATUS_RESOLVED = 'RESOLVED'
    STATUS_AWAITING_DOCUMENTATION = 'AWAITING_DOCUMENTATION'
    STATUS_UNDER_OBSERVATION = 'UNDER_OBSERVATION'
    STATUS_REVIEWED = 'REVIEWED'
    STATUS_APPROVED = 'APPROVED'
    STATUS_REJECTED = 'REJECTED'
    STATUS_CLOSED = 'CLOSED'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending Review'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_USER_FEEDBACK, 'User Feedback'),
        (STATUS_RESOLVED, 'Resolved - User Can Close'),
        (STATUS_AWAITING_DOCUMENTATION, 'Awaiting Engineer Documentation'),
        (STATUS_UNDER_OBSERVATION, 'Under Observation'),
        (STATUS_REVIEWED, 'Reviewed - Awaiting Approval'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_CLOSED, 'Closed'),
    ]
    
    OPERATIONAL_STATUS_CHOICES = [
        ('OPERATIONAL', 'Operational'),
        ('NON_OPERATIONAL', 'Non-Operational'),
    ]

    
    user = models.ForeignKey(Employee, on_delete=models.PROTECT, blank=True, null=True, related_name='form_creator')
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    ticket_num = models.CharField(max_length=50,blank=True, null=True)
    machine_id = models.ForeignKey(Machines,on_delete=models.PROTECT)
    machine_section = models.ForeignKey(MachineSection, on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name="machine_issues",
                                         help_text="Specific section of the machine affected")
    machine_hours = models.IntegerField(blank=True, null=True)
    description_user = models.TextField(default="EMPTY", blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, blank=True, null=True)
    operational_status = models.CharField(max_length=20, choices=OPERATIONAL_STATUS_CHOICES, default='OPERATIONAL', help_text="Is the machine operational or down?")
    image = models.ManyToManyField(ImageModel)
    date_time = models.DateTimeField(auto_now_add=True)  # Fixed: Only set on creation, not every update
    last_updated = models.DateTimeField(auto_now=True)  # New: Tracks last modification

    # Workflow timestamp tracking for downtime calculation
    quick_review_timestamp = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When engineer performed quick review"
    )
    user_confirmation_timestamp = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When user confirmed/rejected resolution"
    )
    documentation_timestamp = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When engineer completed detailed documentation"
    )
    closure_timestamp = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When complaint was officially closed"
    )

    # Calculated downtime metrics
    total_downtime_hours = models.FloatField(
        null=True,
        blank=True,
        help_text="Total hours from creation to closure"
    )
    engineer_response_hours = models.FloatField(
        null=True,
        blank=True,
        help_text="Hours from creation to engineer quick review"
    )
    user_response_hours = models.FloatField(
        null=True,
        blank=True,
        help_text="Hours from resolved to user confirmation"
    )
    documentation_hours = models.FloatField(
        null=True,
        blank=True,
        help_text="Hours to complete documentation"
    )
    closure_hours = models.FloatField(
        null=True,
        blank=True,
        help_text="Hours to close after documentation"
    )

    error_department = models.ForeignKey( Department, on_delete=models.CASCADE)

    # Issue selection: User can select from existing IssueList OR report new issue
    selected_issue = models.ForeignKey(IssueList, on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name="machine_issues",
                                        help_text="Issue selected from master list (if available)")
    
    temporary_issue = models.ForeignKey(TemporaryIssue, on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name="machine_issues",
                                         help_text="New issue reported by user (pending engineer review)")


    def generate_ticket(self):

        equipment_id = self.equipment.id
        machine_id = self.machine_id.id
        machine_issue_id = self.pk
        self.ticket_num = f"{equipment_id}-{machine_id}-{machine_issue_id}"
        return

    def has_review(self):
        """Check if this issue has a MachineIssueReview record"""
        try:
            return hasattr(self, 'machineissue') and self.machineissue is not None
        except:
            return False

    def validate_status_transition(self, new_status):
        """
        Validate status transitions to ensure proper workflow
        Returns (is_valid, error_message)
        """
        # Only CLOSED status requires a review record
        # This allows: PENDING → RESOLVED (quick fix) → user acknowledges → engineer documents → CLOSED
        requires_review = ['CLOSED']

        if new_status in requires_review and not self.has_review():
            return False, f"Cannot close complaint without engineer documentation. Please fill the MachineIssueReview form first."

        return True, None
    
    def reduce_image_size(self, image):
        '''Utility method to reduce image file size before saving'''
        try:
            img = Image.open(image.path)
            img.thumbnail((800, 800))  # Resize to max 800x800 while maintaining aspect ratio
            img.save(image.path, optimize=True, quality=85)  # Save with optimization
        except Exception as e:
            print(f"Error processing image {image.id}: {e}")

    def save(self, *args, **kwargs):
        """Override save to validate status transitions"""
        if self.pk:  # Only validate on updates, not initial creation
            # Get the original status from database
            try:
                original = MachineIssue.objects.get(pk=self.pk)
                if original.status != self.status:
                    # Status is changing, validate it
                    is_valid, error = self.validate_status_transition(self.status)
                    if not is_valid:
                        raise ValidationError(error)
            except MachineIssue.DoesNotExist:
                pass  # New object, skip validation

        super().save(*args, **kwargs)


    def __str__(self):
        return f"Work Order: {self.ticket_num} \n Issue Description: {self.description_user}"

    class Meta:
        permissions = [
            ('view_all_issues', 'Can view all issues'),
            ('view_own_issues', 'Can view own raised issues'),
        ]


class QuickReviewComments(models.Model):

    issue = models.ForeignKey(MachineIssue, on_delete=models.CASCADE, related_name="quick_review_comments")
    commenter = models.ForeignKey(Employee, on_delete=models.CASCADE)
    comment = models.TextField(default="EMPTY", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class MachineIssueReview(models.Model):
    

    PRIORITY_CHOICES = [
        ('HIGH',"High"),
        ('MODERATE',"MODERATE"),
        ('LOW',"LOW"),
    ]

    STATUS_CHOICES = [

        ('PENDING','Pending Approvel'),
        ('REVIEWED','Reviewed'),

    ]

    TYPE_CHOICES = (
        ('CORRECTIVE', 'Corrective'),
        ('PREVENTIVE', 'Preventive'),
        ('BREAKDOWN', 'Breakdown'),
        ('CALIBRATION', 'Calibration')
    )

    PROBLEM_NATURE_CHOICES = (
        ('ELECTRICAL','Electrical'),
        ('MECHANICAL','Mechanical'),
        ('HYDRAULIC', 'Hydraulic')
    )
    
    reviewer = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='reviewer') 
    issue = models.OneToOneField(MachineIssue, on_delete=models.PROTECT, related_name='machineissue')
    code = models.ForeignKey(IssueList, on_delete=models.PROTECT, blank=True, null=True)
    description_reviewer = models.TextField(blank=True, null=True)
    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES, blank=True, null=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, blank=True, null=True)
    problemNature = models.CharField(max_length=50, choices=PROBLEM_NATURE_CHOICES, blank=True, null=True)
    assignDepartment = models.ForeignKey(Department, on_delete=models.PROTECT, blank=True, null=True)
    assignPerson = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True, related_name='task_assigned')
    reviewerImages = models.ManyToManyField(ImageModel)
    reviewDate = models.DateTimeField(auto_now=True)
    status = models.CharField( max_length=50, default=STATUS_CHOICES[0][0])    
    malfunction_part = models.ManyToManyField(Spares, related_name="spares" )


class MachineIssueApproval(models.Model):

    STATUS_CHOICES = [

        ('PENDING','PENDING APPROVAL'),
        ('APPROVED','APPROVED'),

    ]

    user_id = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='user_remarks')
    complain_id = models.OneToOneField(MachineIssue, on_delete=models.CASCADE, related_name = 'issue_remarks')
    comment = models.TextField(max_length=1000, blank=True, null=True)
    date_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default=STATUS_CHOICES[0][0])

    def __str__(self):
        return f"Approval for {self.complain_id.ticket_num} by {self.user_id.username}"


class IssueClosing(models.Model):

    
    STATUS_CHOICES = [

        ('PENDING','Pending Closing'),
        ('CLOSED','Closed'),

    ]

    issueReview = models.OneToOneField(MachineIssueReview, on_delete=models.DO_NOTHING)
    date_ended = models.DateTimeField(auto_now=True)
    contractor = models.ForeignKey(Contractor, related_name='resolved_issues', on_delete=models.DO_NOTHING, blank=True, null=True)
    machineHours = models.IntegerField()
    supervisor = models.CharField(max_length=50, null=True, blank=True)
    technician = models.CharField(max_length=50, null=True, blank=True)
    solutionDescription = models.TextField(default="EMPTY")
    duration = models.DecimalField(max_digits=16, decimal_places=2)
    remarks = models.TextField(default="EMPTY") 
    image = models.ManyToManyField(ImageModel, related_name="closingImages")
    installed_spares = models.ManyToManyField(Spares, related_name="used_in_repairs", blank=True, help_text="Spares installed during repair")
    equipment_status = models.CharField(max_length=10)
    status = models.CharField(max_length=50, default=STATUS_CHOICES[0][0])
    
    def totalDays(self):
        total_days = self.date_ended.date()-datetime.date()
        
        if self.temprory_close and total_days > 7:
            pass

    def __str__(self) -> str:
        return f"{self.issueReview.reviewer.name}\n{self.issueReview.issue.description_user}"


class WorkSession(models.Model):
    """Tracks each engineer's work period on an issue.
    Multiple sessions per issue allows tracking handoffs between departments/engineers."""

    OUTCOME_IN_PROGRESS = 'IN_PROGRESS'
    OUTCOME_RESOLVED = 'RESOLVED'
    OUTCOME_ESCALATED = 'ESCALATED'
    OUTCOME_UNDER_OBSERVATION = 'UNDER_OBSERVATION'

    OUTCOME_CHOICES = [
        (OUTCOME_IN_PROGRESS, 'In Progress'),
        (OUTCOME_RESOLVED, 'Resolved'),
        (OUTCOME_ESCALATED, 'Escalated'),
        (OUTCOME_UNDER_OBSERVATION, 'Under Observation'),
    ]

    issue = models.ForeignKey(MachineIssue, on_delete=models.CASCADE, related_name='work_sessions')
    engineer = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name='work_sessions')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_hours = models.FloatField(null=True, blank=True, help_text="Hours spent working in this session")
    outcome = models.CharField(max_length=30, choices=OUTCOME_CHOICES, default=OUTCOME_IN_PROGRESS)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"Work on {self.issue.ticket_num} by {self.engineer.name} ({self.outcome})"

    def complete(self, outcome, comments=''):
        """Mark this work session as complete and calculate duration."""
        self.completed_at = timezone.now()
        self.duration_hours = (self.completed_at - self.started_at).total_seconds() / 3600
        self.outcome = outcome
        if comments:
            self.comments = comments
        self.save()