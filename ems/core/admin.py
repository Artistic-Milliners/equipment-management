from dataclasses import field
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import (CustomUser, Department, Designation, Contractor, Manufacturer,
                     IssueList, TemporaryIssue, Employee, Machines, Spares, MachineIssue, Equipment,
                     SpareTransaction, IssueClosing, Unit, WorkSession, MachineSection)
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django import forms
from .forms import UserCreationForm
# Register your models here.

CustomUser = get_user_model()



class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ("username", "email", "is_employee", "is_contractor")  # <-- no 'password' here

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise ValidationError("Password and Confirm Password do not match")
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])  # hash the password
        if commit:
            user.save()
        return user


class DepartmentCreationForm(forms.ModelForm):

    class Meta:
        model = Department
        fields = "__all__"

class UnitCreationForm(forms.ModelForm):
    class Meta:
        model = Unit
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

class MachineSectionForm(forms.ModelForm):

    class Meta:
        model = MachineSection
        fields = ['machine', 'section_name']

    def clean_section_name(self):
        return self.cleaned_data['section_name'].strip()

    def clean(self):
        cleaned_data = super().clean()
        machine = cleaned_data.get('machine')
        section_name = cleaned_data.get('section_name')
        if machine and section_name:
            duplicates = MachineSection.objects.filter(machine=machine, section_name__iexact=section_name)
            if self.instance.pk:
                duplicates = duplicates.exclude(pk=self.instance.pk)
            if duplicates.exists():
                raise forms.ValidationError(f'"{section_name}" already exists for {machine}.')
        return cleaned_data

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


# @admin.register(CustomUser)
# class UserCreation(admin.ModelAdmin):
#     form = UserCreationForm


@admin.register(Unit)
class UnitCreation(admin.ModelAdmin):
    form = UnitCreationForm
    list_display = ['id', 'name', 'location']

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

class SpareTransactionInline(admin.TabularInline):
    model = SpareTransaction
    extra = 0
    readonly_fields = ['transaction_type', 'quantity', 'user', 'reason', 'machine', 
                       'work_order', 'quantity_before', 'quantity_after', 'created_at']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Spares)
class SpareCreation(admin.ModelAdmin):
    form = SparesCreationForm
    list_display = ['item_code', 'name', 'manufacturer', 'manufacturer_part_number', 
                    'category', 'quantity', 'unit', 'stock_status', 'min_stock_level']
    list_filter = ['category', 'manufacturer']
    search_fields = ['item_code', 'name', 'manufacturer_part_number', 'description']
    readonly_fields = ['item_code', 'created_at', 'updated_at', 'stock_status']
    inlines = [SpareTransactionInline]
    
    fieldsets = (
        ('Item Identification', {
            'fields': ('item_code', 'name', 'description', 'category')
        }),
        ('Manufacturer Information', {
            'fields': ('manufacturer', 'manufacturer_part_number')
        }),
        ('Stock Information', {
            'fields': ('quantity', 'unit', 'min_stock_level', 'max_stock_level', 'unit_price')
        }),
        ('Additional Details', {
            'fields': ('image', 'leadtime', 'shelflife', 'servicelife', 'date_of_purchase'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def stock_status(self, obj):
        status = obj.stock_status
        colors = {
            'in-stock': 'green',
            'low-stock': 'orange',
            'out-of-stock': 'red'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(status, 'black'),
            status.upper()
        )
    stock_status.short_description = 'Stock Status'

@admin.register(SpareTransaction)
class SpareTransactionAdmin(admin.ModelAdmin):
    list_display = ['spare', 'transaction_type', 'quantity', 'user', 'machine', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['spare__item_code', 'spare__name', 'reason']
    readonly_fields = ['spare', 'transaction_type', 'quantity', 'user', 'reason', 
                       'machine', 'work_order', 'quantity_before', 'quantity_after', 'created_at']
    
    def has_add_permission(self, request):
        # Transactions should only be created through the system, not manually
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion of transaction history
        return False
@admin.register(IssueList)
class IssuelistCreation(admin.ModelAdmin):
    form = IssueListCreationForm
    search_fields = ['equipment__name', 'c_desc']
    list_display = ['equipment', 'programmer_string','machine_string','c_desc', 'error_code', 'created_by', 'image']
    list_filter = ['equipment', 'created_by']
    readonly_fields = ['created_by']

    def save_model(self, request, obj, form, change):
        # Set created_by when creating through admin
        if not change and not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(TemporaryIssue)
class TemporaryIssueAdmin(admin.ModelAdmin):
    list_display = ['id', 'equipment', 'machine', 'user_description_short', 'reviewed', 'promoted_to_issuelist', 'created_at']
    list_filter = ['reviewed', 'promoted_to_issuelist', 'equipment', 'created_at']
    search_fields = ['user_description', 'equipment__name', 'machine__name']
    readonly_fields = ['created_at', 'user', 'equipment', 'machine']

    fieldsets = (
        ('Issue Details', {
            'fields': ('user', 'equipment', 'machine', 'user_description')
        }),
        ('Review Status', {
            'fields': ('reviewed', 'reviewed_by', 'engineer_notes')
        }),
        ('Promotion', {
            'fields': ('promoted_to_issuelist', 'promoted_issue')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def user_description_short(self, obj):
        return obj.user_description[:50] + '...' if len(obj.user_description) > 50 else obj.user_description
    user_description_short.short_description = 'User Description'

    actions = ['mark_as_reviewed', 'promote_to_issuelist']

    def mark_as_reviewed(self, request, queryset):
        queryset.update(reviewed=True, reviewed_by=request.user.employee)
        self.message_user(request, f'{queryset.count()} temporary issues marked as reviewed.')
    mark_as_reviewed.short_description = 'Mark selected as reviewed'

@admin.register(Machines)
class Machine(admin.ModelAdmin):
    form = MachinesForm

@admin.register(MachineSection)
class MachineSectionAdmin(admin.ModelAdmin):
    form = MachineSectionForm
    list_display = ['section_name', 'machine', 'equipment']
    list_filter = ['machine__type_of_machine', 'machine']
    search_fields = ['section_name', 'machine__name']
    list_select_related = ['machine__type_of_machine']
    ordering = ['machine__name', 'section_name']

    def equipment(self, obj):
        return obj.machine.type_of_machine if obj.machine else '-'
    equipment.short_description = 'Equipment'

@admin.register(Employee)
class EmployeeCreation(admin.ModelAdmin):
    form = EmployeeCreationForm
    

@admin.register(MachineIssue)
class MachineIssueCreate(admin.ModelAdmin):
    form = MachineIssueForm

@admin.register(Equipment)
class Equipment(admin.ModelAdmin):
    form = EquipmentForm

@admin.register(WorkSession)
class WorkSessionAdmin(admin.ModelAdmin):
    list_display = ['issue', 'engineer', 'started_at', 'completed_at', 'duration_hours', 'outcome']
    list_filter = ['outcome', 'started_at']
    search_fields = ['issue__ticket_num', 'engineer__name']
    readonly_fields = ['started_at']

@admin.register(IssueClosing)
class IssueClosingAdmin(admin.ModelAdmin):
    list_display = ['id', 'issueReview', 'contractor', 'technician', 'equipment_status', 'status', 'date_ended']
    list_filter = ['status', 'equipment_status', 'contractor', 'date_ended']
    search_fields = ['issueReview__issue__ticket_num', 'technician', 'supervisor', 'solutionDescription']
    readonly_fields = ['date_ended']
    filter_horizontal = ['installed_spares', 'image']

    fieldsets = (
        ('Issue Information', {
            'fields': ('issueReview', 'status')
        }),
        ('Resolution Details', {
            'fields': ('contractor', 'technician', 'supervisor', 'solutionDescription', 'remarks')
        }),
        ('Machine Details', {
            'fields': ('machineHours', 'duration', 'equipment_status')
        }),
        ('Parts & Documentation', {
            'fields': ('installed_spares', 'image')
        }),
        ('Metadata', {
            'fields': ('date_ended',),
            'classes': ('collapse',)
        }),
    )


User = get_user_model()

# --- Show and edit group members on the Group page ---
class UserInline(admin.TabularInline):
    # Use YOUR CustomUser's M2M-through table
    model = User.groups.through
    fk_name = "group"  
    extra = 1
    verbose_name = "member"
    verbose_name_plural = "members"
    autocomplete_fields = ["customuser"]  # nice for large user lists

class CustomGroupAdmin(admin.ModelAdmin):
    inlines = [UserInline]
    exclude = ("permissions",)  # optional: tidier page
    list_display = ("name", "user_count")
    search_fields = ("name",)

    def user_count(self, obj):
        return obj.user_set.count()

admin.site.unregister(Group)
admin.site.register(Group, CustomGroupAdmin)

# --- Register your CustomUser admin and expose groups there too ---
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Add your extra booleans to the form
    fieldsets = UserAdmin.fieldsets + (
        ("Roles", {"fields": ("is_employee", "is_contractor")}),
    )
    # Add fields to the user creation form
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Roles", {"fields": ("is_employee", "is_contractor")}),
    )
    list_display = ("username", "email", "is_staff", "is_employee", "is_contractor")
    list_filter = UserAdmin.list_filter + ("is_employee", "is_contractor")
    filter_horizontal = ("groups", "user_permissions")  # ensures the Groups selector appears
    search_fields = ("username", "email")
