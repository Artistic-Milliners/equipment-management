from tokenize import blank_re
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from PIL import Image

# Create your models here.

class CustomUser(AbstractUser):
    is_employee = models.BooleanField(default=False)
    is_contractor = models.BooleanField(default=False)


class Department(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Designation(models.Model):
    designation_name = models.CharField(max_length=255, default='Trainee')

    def __str__(self):
        return self.designation_name


class Employee(models.Model):
    name = models.CharField(max_length=255)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, default=1)
    designation = models.ForeignKey(Designation, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class Contractor(models.Model):
    contractor = models.CharField(max_length=255)

    def __str__(self):
        return self.contractor


class Contractor_Person(models.Model):
    
    contractor_name = models.ForeignKey(Contractor, on_delete=models.CASCADE, default=1)
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
    spares = models.ManyToManyField(Spares,related_name='machines' ,blank=True)
    dop = models.DateField(verbose_name="Date of Purcahse", blank=True, null=True)
    purchase_cost = models.FloatField(default=0)
    model = models.CharField(max_length=50,blank=True, null=True)
    image = models.ImageField(upload_to='images', blank=True, null=True)


    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.image:
            img = Image.open(self.image)
            output_size = (250,250)
            img.thumbnail(output_size)
            img.save(self.image.path)

        super().save(*args,**kwargs)



class IssueList(models.Model):
    
    error_code = models.CharField(max_length = 35, null=True, default=None)
    programmer_string = models.CharField(max_length=100, null=True, default=None)
    machine_string = models.CharField(max_length=100, null=True, default=None)
    c_desc = models.TextField(default="EMPTY",verbose_name="code description")
    effect = models.TextField(max_length=250,blank=True,null=True)
    machine_status = models.CharField(max_length=250, blank=True, null=True)
    restart_procedure = models.TextField(max_length=500, blank=True, null=True)
    flashes = models.IntegerField(blank=True, null=True)
    image = models.ImageField(upload_to='images', blank=True, null=True)
    equipment = models.ForeignKey(Equipment, on_delete=models.PROTECT, related_name="equipment", default=1)

    def __str__(self):
        return f"Machine: {self.c_desc}"

class MachineIssue(models.Model):
    HIGH = 1
    MODERATE = 2
    LOW = 3

    PENDING = 'Pending'
    COMPLETED = 'Completed'
    IN_PROGRESS = 'In Progress'



    PRIORITY_CHOICES = [
        ('HIGH',HIGH),
        ('MODERATE',MODERATE),
        ('LOW',LOW),
    ]

    

    STATUS_CHOICES = [

        
        ('PENDING',PENDING),
        ('COMPLETED',COMPLETED),
        ('IN_PROGRESS',IN_PROGRESS),

    ]


    user = models.ForeignKey(Employee, on_delete=models.PROTECT, blank=True, null=True)
    machine = models.ForeignKey(Machines,on_delete=models.PROTECT,default=1)
    machine_hours = models.IntegerField(blank=True, null=True)
    code = models.ForeignKey(IssueList, on_delete=models.PROTECT, blank=True, null=True)
    description = models.TextField(default="EMPTY", blank=True, null=True)
    Images = models.ImageField(upload_to = 'images')
    date_time = models.DateTimeField(auto_now=True)
    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES,default=HIGH)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=PENDING)

    def __str__(self):
        return f"Issue Code: {self.code} \n Issue Description: {self.description}"


class IssueResolution(models.Model):
    issue = models.OneToOneField(MachineIssue, on_delete=models.DO_NOTHING)
    date_started = models.DateTimeField(auto_now=True)
    date_ended = models.DateTimeField(blank=True, null=True)
    contractor = models.ForeignKey(Contractor, related_name='resolved_issues', on_delete=models.DO_NOTHING)
    employee = models.ForeignKey(Employee, related_name="employee", on_delete=models.PROTECT, default=None)
    remarks = models.TextField(default="EMPTY")


class Pub(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.name
    
class author(models.Model):
    name = models.CharField(max_length=50)
    pub = models.ManyToManyField(Pub)

    def __str__(self):
        return f"Name: {self.name}\nPub:{self.pub.name}" 