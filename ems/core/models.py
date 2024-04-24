from django.db import models
from datetime import datetime
from django.contrib.auth.models import AbstractUser
from .fields import UnitIDField
from PIL import Image
from django.db import transaction

# Create your models here.

class Unit(models.Model):
    id = UnitIDField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)


# def get_unit():
#     with transaction.atomic():
#         try:
#             unit = Unit.objects.first().pk
#         except Unit.DoesNotExist:
#             unit = Unit.objectss.create(id=int('005'), name='Artistic Millienrs unit 5', location='Landhi Bin Qasim')
#         return unit 

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


# def get_department():
#     try:
#         department = Department.objects.first().pk
#     except Department.DoesNotExist:
#         unit = Department.objectss.create(name='Process Automation', unit=get_unit)
#     return unit 

class Designation(models.Model):
    designation_name = models.CharField(max_length=255, default='Trainee')

    def __str__(self):
        return self.designation_name


class CustomUser(AbstractUser):
    is_employee = models.BooleanField(default=False)
    is_contractor = models.BooleanField(default=False)


# def get_user():
#     try:
#         user_pk = CustomUser.objects.first().pk 
#     except:
#         user = CustomUser.objects.create(username='zohaib', password='abcd@1234') 
#         user_pk = user.pk

#     return user_pk


class Employee(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    designation = models.ForeignKey(Designation, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


# def get_employee():
#     with transaction.atomic():
#         try:
#             emp_pk = Employee.objects.first().pk
#         except AttributeError as e:
#             emp = Employee.objects.create(name='Wahab', department=get_department)
#             emp_pk = emp.pk 
#     return emp_pk


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
    
    item_code = models.CharField(max_length=30, blank=True, null=True)
    name = models.CharField(max_length=255)
    quantity = models.IntegerField()
    unit = models.CharField(max_length=50,blank=True, null=True)

    def __str__(self) -> str:
        return f'{self.name}'

class Machines(models.Model):
    
    name = models.CharField(max_length=50)
    type_of_machine = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='typeOfMachine')
    machine_spare = models.ManyToManyField(Spares,related_name='machines' ,through="MachineSpares", blank=True)
    dop = models.DateField(verbose_name="Date of Purcahse", blank=True, null=True)
    purchase_cost = models.FloatField(default=0)
    model = models.CharField(max_length=50,blank=True, null=True)
    machine_hours = models.IntegerField(blank=True, null=True)
    image = models.ImageField(upload_to='images', blank=True, null=True)
    # #machine department
    # location = models.CharField(max_length=2000, default="Warehouse")
    # #machine site where it is installed
    # site = models.CharField(max_length=100, default="AM5")

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.image:
            img = Image.open(self.image)
            output_size = (250,250)
            img.thumbnail(output_size)
            img.save(self.image.path)

        super().save(*args,**kwargs)

class ImageModel(models.Model):
    image = models.ImageField(upload_to='images')

class MachineSpares(models.Model):
    spare = models.ForeignKey(Spares, on_delete=models.CASCADE)
    machine = models.ForeignKey(Machines, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.spare.name}: {self.machine.name}"

class IssueList(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name="user")
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


def get_department():
    return Department.objects.get(name="Workshop").pk


class MachineIssue(models.Model):

    
    STATUS_CHOICES = [

        ('PENDING','Pending Approvel'),
        ('REVIEWED','Reviewed'),
        ('APPROVED','Approved'),
        ('REJECTED', 'Rejected'),

    ]
    
    user = models.ForeignKey(Employee, on_delete=models.PROTECT, blank=True, null=True, related_name='form_creator')
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    ticket_num = models.CharField(max_length=50,blank=True, null=True)
    machine_id = models.ForeignKey(Machines,on_delete=models.PROTECT)
    machine_hours = models.IntegerField(blank=True, null=True)
    description_user = models.TextField(default="EMPTY", blank=True, null=True) 
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, blank=True, null=True)
    image = models.ManyToManyField(ImageModel)
    date_time = models.DateTimeField(auto_now=True)  
    temp_review_id = models.IntegerField(blank=True, null=True) 


    def generate_ticket(self):

        equipment_id = self.equipment.id
        machine_id = self.machine_id.id
        machine_issue_id = self.pk    
        self.ticket_num = f"{equipment_id}-{machine_id}-{machine_issue_id}"
        return
    

    def __str__(self):
        return f"Work Order: {self.ticket_num} \n Issue Description: {self.description_user}"


class MachineIssueReview(models.Model):
    

    PRIORITY_CHOICES = [
        ('HIGH',"High"),
        ('MODERATE',"MODERATE"),
        ('LOW',"LOW"),
    ]

    STATUS_CHOICES = [

        ('PENDING','Pending Approvel'),
        ('REVIEWED','Reviewed'),
        ('APPROVED','Approved'),
        ('REJECTED', 'Rejected'),

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
    issue = models.OneToOneField(MachineIssue, on_delete=models.CASCADE)
    code = models.ForeignKey(IssueList, on_delete=models.PROTECT, blank=True, null=True)
    description_reviewer = models.TextField(blank=True, null=True)
    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES, blank=True, null=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, blank=True, null=True)
    problemNature = models.CharField(max_length=50, choices=PROBLEM_NATURE_CHOICES, blank=True, null=True)
    assignDepartment = models.ForeignKey(Department, on_delete=models.PROTECT)
    assignPerson = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True, related_name='task_assigned')
    reviewrImages = models.ManyToManyField(ImageModel)
    reviewDate = models.DateTimeField(auto_now=True)
    malfunction_part = models.ForeignKey(Spares, on_delete=models.PROTECT)
    


class Remarks(models.Model):
    user_id = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='user_remarks')
    complain_id = models.OneToOneField(MachineIssue, on_delete=models.CASCADE, related_name = 'issue_remarks')
    comment = models.TextField(max_length = 1000)
    date_time= models.DateTimeField()

    def save(self, *args, **kwargs):
       if not self.date_time:
        self.date_time = datetime.now()
       return super().save(*args, **kwargs)


class IssueResolution(models.Model):
    issue = models.OneToOneField(MachineIssue, on_delete=models.DO_NOTHING)
    date_started = models.DateTimeField(auto_now=True)
    date_ended = models.DateTimeField(blank=True, null=True)
    contractor = models.ForeignKey(Contractor, related_name='resolved_issues', on_delete=models.DO_NOTHING)
    employee = models.ForeignKey(Employee, related_name="employee", on_delete=models.PROTECT, default=None)
    remarks = models.TextField(default="EMPTY")
