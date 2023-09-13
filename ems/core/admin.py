from dataclasses import field
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Department, Designation,Contractor,Manufacturer,IssueList,Employee,Machines,Spares, MachineIssue, Equipment

from django import forms
# Register your models here.


class UserCreationForm(forms.ModelForm):
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ("username","email","is_employee", "is_contractor","password")
        widgets={
            "password":forms.PasswordInput(),
        }


    def clean(self):
         cleaned_data =  super().clean()
         password = cleaned_data.get("password")
         confirm_password = cleaned_data.get("password2") 
         if confirm_password != password:
            self.add_error("password2","Passowrd and Confirm Password does not match")


class DepartmentCreationForm(forms.ModelForm):

    class Meta:
        model = Department
        fields = "__all__"


class DesignationCreationForm(forms.ModelForm):

    class Meta:
        model = Designation
        fields = "__all__"

class ContractorCreationForm(forms.ModelForm):

    class Meta:
        model = Contractor
        fields = "__all__"

class ManufacturerCreationForm(forms.ModelForm):

    class Meta:
        model = Manufacturer
        fields = "__all__"

class IssueListCreationForm(forms.ModelForm):


    class Meta:
        model = IssueList
        fields = "__all__"

class SparesCreationForm(forms.ModelForm):
    model = Spares
    fields = '__all__'


class MachinesForm(forms.ModelForm):

    class Meta:
        model = Machines
        fields = '__all__'

class EmployeeCreationForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = "__all__"

class MachineIssueForm(forms.ModelForm):
    class Meta:
        model = MachineIssue
        fields = "__all__"

class EquipmentForm(forms.ModelForm):
    class Meta:
        model= Equipment
        fields = '__all__'


@admin.register(CustomUser)
class UserCreation(admin.ModelAdmin):
    form = UserCreationForm

@admin.register(Department)
class DepartmentCreation(admin.ModelAdmin):
    form = DepartmentCreationForm

@admin.register(Designation)
class DesignationCreation(admin.ModelAdmin):
    form = DesignationCreationForm

@admin.register(Contractor)
class ContratorCreation(admin.ModelAdmin):
    form = ContractorCreationForm

@admin.register(Manufacturer)
class ManufacturerCreation(admin.ModelAdmin):
    form = ManufacturerCreationForm

@admin.register(Spares)
class SpareCreation(admin.ModelAdmin):
    form = SparesCreationForm
    list_display = ['item_code', 'name', 'quantity']
@admin.register(IssueList)
class IssuelistCreation(admin.ModelAdmin):
    form = IssueListCreationForm
    search_fields = ['equipment__name']
    list_display = ['equipment', 'programmer_string','machine_string','c_desc', 'error_code', 'image']

@admin.register(Machines)
class Machine(admin.ModelAdmin):
    form = MachinesForm

@admin.register(Employee)
class EmployeeCreation(admin.ModelAdmin):
    form = EmployeeCreationForm
    

@admin.register(MachineIssue)
class MachineIssueCreate(admin.ModelAdmin):
    form = MachineIssueForm

@admin.register(Equipment)
class Equipment(admin.ModelAdmin):
    form = EquipmentForm