from dataclasses import field
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import (CustomUser, Department, Designation, Contractor, Manufacturer,
                     FaultLibrary, TemporaryIssue, Employee, Machines, Spares, MachineIssue, Equipment,
                     SpareTransaction, IssueClosing, Unit, WorkSession, MachineSection)
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django import forms
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse
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

class FaultLibraryForm(forms.ModelForm):
    # Section names come from MachineSection, grouped by equipment; the model's clean() checks the combination
    machine_section = forms.ChoiceField(required=False)

    class Meta:
        model = FaultLibrary
        fields = ['equipment', 'manufacturer', 'fault_category', 'machine_section',
                  'fault_description', 'fault_effect', 'restart_procedure', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        grouped = {}
        rows = (MachineSection.objects.filter(machine__isnull=False)
                .values_list('machine__type_of_machine__name', 'section_name')
                .order_by('machine__type_of_machine__name', 'section_name').distinct())
        for equipment_name, section_name in rows:
            names = grouped.setdefault(equipment_name, [])
            if section_name.lower() not in [n.lower() for n in names]:
                names.append(section_name)

        choices = [('', '---------')]
        current = self.instance.machine_section
        if current and not any(current.lower() == n.lower() for names in grouped.values() for n in names):
            choices.append((current, f'{current} (no longer on any machine)'))
        choices += [(equipment, [(n, n) for n in names]) for equipment, names in grouped.items()]
        self.fields['machine_section'].choices = choices
        self.fields['machine_section'].help_text = 'Optional. Must be a section of a machine of the selected equipment.'

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


class MachineSectionBulkForm(forms.Form):
    machine = forms.ModelChoiceField(
        queryset=Machines.objects.select_related('type_of_machine').order_by('type_of_machine__name', 'name'))


class SectionNameForm(forms.Form):
    section_name = forms.CharField(max_length=100, required=False, label='Section name')


class BaseSectionNameFormSet(forms.BaseFormSet):
    """Section names for one machine: blank rows are ignored, duplicates rejected."""

    def __init__(self, *args, machine=None, **kwargs):
        self.machine = machine
        super().__init__(*args, **kwargs)

    def clean(self):
        if any(self.errors):
            return
        existing = set()
        if self.machine:
            existing = {name.lower() for name in
                        MachineSection.objects.filter(machine=self.machine).values_list('section_name', flat=True)}
        seen = set()
        for form in self.forms:
            name = (form.cleaned_data.get('section_name') or '').strip()
            form.cleaned_data['section_name'] = name
            if not name:
                continue
            if name.lower() in seen:
                form.add_error('section_name', f'"{name}" is entered more than once.')
            elif name.lower() in existing:
                form.add_error('section_name', f'"{name}" already exists for {self.machine}.')
            seen.add(name.lower())
        if not seen:
            raise forms.ValidationError('Enter at least one section name.')

    @property
    def section_names(self):
        return [f.cleaned_data['section_name'] for f in self.forms if f.cleaned_data.get('section_name')]


SectionNameFormSet = forms.formset_factory(SectionNameForm, formset=BaseSectionNameFormSet, extra=3)


class MachineSectionInlineFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        seen = set()
        for form in self.forms:
            if not hasattr(form, 'cleaned_data') or form.cleaned_data.get('DELETE'):
                continue
            name = (form.cleaned_data.get('section_name') or '').strip()
            if not name:
                continue
            if name.lower() in seen:
                form.add_error('section_name', f'"{name}" is entered more than once.')
            seen.add(name.lower())
            form.cleaned_data['section_name'] = name
            form.instance.section_name = name


class MachineSectionInline(admin.TabularInline):
    model = MachineSection
    formset = MachineSectionInlineFormSet
    fields = ['section_name']
    extra = 1

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
@admin.register(FaultLibrary)
class FaultLibraryAdmin(admin.ModelAdmin):
    form = FaultLibraryForm
    list_display = ['fault_description_short', 'equipment', 'manufacturer', 'machine_section', 'fault_category']
    list_filter = ['equipment', 'manufacturer', 'fault_category']
    search_fields = ['fault_description', 'machine_section', 'equipment__name']
    list_select_related = ['equipment', 'manufacturer']

    def fault_description_short(self, obj):
        return obj.fault_description[:60] + '...' if len(obj.fault_description) > 60 else obj.fault_description
    fault_description_short.short_description = 'Fault'

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
    list_display = ['name', 'type_of_machine', 'manufacturer', 'Department']
    list_filter = ['type_of_machine', 'manufacturer', 'Department']
    search_fields = ['name', 'model']
    list_select_related = ['type_of_machine', 'manufacturer', 'Department']
    inlines = [MachineSectionInline]

@admin.register(MachineSection)
class MachineSectionAdmin(admin.ModelAdmin):
    form = MachineSectionForm
    list_display = ['section_name', 'machine', 'equipment']
    list_filter = ['machine__type_of_machine', 'machine']
    search_fields = ['section_name', 'machine__name']
    list_select_related = ['machine__type_of_machine']
    ordering = ['machine__name', 'section_name']

    def add_view(self, request, form_url='', extra_context=None):
        # Add many sections to one machine at once instead of the default one-object form
        if not self.has_add_permission(request):
            raise PermissionDenied

        if request.method == 'POST':
            machine_form = MachineSectionBulkForm(request.POST)
            machine = machine_form.cleaned_data['machine'] if machine_form.is_valid() else None
            formset = SectionNameFormSet(request.POST, machine=machine)
            if machine and formset.is_valid():
                names = formset.section_names
                with transaction.atomic():
                    MachineSection.objects.bulk_create(
                        [MachineSection(machine=machine, section_name=name) for name in names])
                self.message_user(request, f'Added {len(names)} section{"s" if len(names) != 1 else ""} '
                                           f'to {machine}: {", ".join(names)}.', messages.SUCCESS)
                if '_addanother' in request.POST:
                    return redirect(f"{reverse('admin:core_machinesection_add')}?machine={machine.pk}")
                return redirect(f"{reverse('admin:core_machinesection_changelist')}?machine__id__exact={machine.pk}")
        else:
            machine_form = MachineSectionBulkForm(initial={'machine': request.GET.get('machine')})
            formset = SectionNameFormSet()

        context = {
            **self.admin_site.each_context(request),
            'title': 'Add machine sections',
            'opts': self.model._meta,
            'machine_form': machine_form,
            'formset': formset,
            **(extra_context or {}),
        }
        return render(request, 'admin/core/machinesection/bulk_add.html', context)

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
    filter_horizontal = ['manufacturers']
    list_display = ['name', 'manufacturer_list', 'quantity']
    search_fields = ['name']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('manufacturers')

    def manufacturer_list(self, obj):
        return ', '.join(m.name for m in obj.manufacturers.all()) or '-'
    manufacturer_list.short_description = 'Manufacturers'

@admin.register(WorkSession)
class WorkSessionAdmin(admin.ModelAdmin):
    list_display = ['issue', 'engineer', 'started_at', 'completed_at', 'duration_hours', 'outcome']
    list_filter = ['outcome', 'started_at']
    search_fields = ['issue__ticket_num', 'engineer__name']
    readonly_fields = ['started_at']

@admin.register(IssueClosing)
class IssueClosingAdmin(admin.ModelAdmin):
    list_display = ['id', 'issueReview', 'resolution_type', 'contractor', 'resolved_department', 'technician',
                    'equipment_status', 'status', 'date_ended']
    list_filter = ['status', 'resolution_type', 'equipment_status', 'contractor', 'resolved_department', 'date_ended']
    search_fields = ['issueReview__issue__ticket_num', 'technician', 'supervisor', 'solutionDescription']
    readonly_fields = ['date_ended']
    filter_horizontal = ['installed_spares', 'image']

    fieldsets = (
        ('Issue Information', {
            'fields': ('issueReview', 'status')
        }),
        ('Resolution Details', {
            'fields': ('resolution_type', 'contractor', 'resolved_department', 'technician', 'supervisor',
                       'solutionDescription', 'remarks')
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
