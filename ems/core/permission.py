from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from core.models import Machines, MachineIssue
from django.shortcuts import get_object_or_404

def create_permission():
    contenttype = ContentType.objects.get_for_model(Machines)
    issuetype = ContentType.objects.get_for_model(MachineIssue)

    #create machine
    create_machine_perm = Permission.objects.get_or_create(
        codename = 'machine_create_perm',
        name = 'Machine Create Permission',
        content_type = contenttype
    )

    create_machine_issue = Permission.objects.get_or_create(
        codename = 'machine_issue_create',
        name = 'Machine Issue Create',
        content_type = issuetype
    )




def create_group(name):
    #check if the group already exists
    if Group.objects.filter(name=name).exists():
        return
    else:
        grp_name = Group.objects.create(name=name)
   
    return grp_name

def assign_permission(group_name, permission):
    
    create_complain_perm = get_object_or_404(Permission, codename=permission)
    user_group = get_object_or_404(Group, name=group_name)
    user_group.permissions.add(create_complain_perm)

    
