from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from core.models import Machines, MachineIssue

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




def create_group():
    pass


def assign_permission():
    
    create_complain_perm = Permission.objects.get(codename='machine_issue_create')
    user_group = Group.objects.get(name='User')
    user_group.permissions.add(create_complain_perm)
