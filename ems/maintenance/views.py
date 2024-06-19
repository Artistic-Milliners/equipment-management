from django.shortcuts import render, get_object_or_404, redirect
from core.models import MachineIssue,Equipment, Machines, Spares, MachineSpares, ImageModel, CustomUser, Remarks, Department, Employee  
from django.http import JsonResponse
from django.db.models import Prefetch
from django.contrib.auth.decorators import permission_required, login_required
from django.core.files.storage import default_storage
from User.views import home

# Create your views here.

# @login_required
# @permission_required('core.machine_issue_create', raise_exception=True)
# def createComplain(request):

#     priority_choice = (
#         ('HIGH', 'H'),
#         ('MODERATE', 'M'),
#         ('LOW', 'L')
#     )

#     type_choices = (
#         ('CORRECTIVE', 'C'),
#         ('PREVENTIVE', 'P'),
#         ('BREAKDOWN', 'B'),
#         ('CALIBRATION', 'Ca'),
#     )

#     problem_nature_choices = (
#         ('ELECTRICAL', 'El'),
#         ('MECHANICAL', 'Me'),
#         ('HYDRAULIC', 'Hy')
#     )

#     user_id = request.user.id
#     user = CustomUser.objects.get(pk=user_id)
#     equipments = Equipment.objects.all()
#     departments = Department.objects.filter(dpt_type__in=['SERVICES', 'MAINTENANCE'])
#     users = Employee.objects.filter(department__dpt_type__in=['MAINTENANCE','SERVICES'])
#     print(users)

#     if request.method == 'POST':
        
#         equipment_id = request.POST['machine-select']
#         machine_id = request.POST['machine-num-select']
#         date_time = request.POST['date-time']
#         machine_section = request.POST['machine-section']
#         # malfunction_part = request.POST['malfunction-part']
#         machine_hours = request.POST['machine-hours']
#         # priority = request.POST["issue-priority"]
#         description = request.POST['malfunction-desc']
#         if request.FILES.getlist('machine-images[]'):
#             images = request.FILES.getlist('machine-images[]')
#         issue_type = request.POST["issue-type"]
#         problem_nature = request.POST["problem-nature"]
#         assign_to_dpt = request.POST['assign-to-department']
#         assign_to_person = request.POST['assign-to-person']


#         selected_priority = next((key for key, value in dict(priority_choice).items() if value==priority), None)

#         selected_type = next((key for key, value in dict(type_choices).items() if value==issue_type), None)

#         selected_problem_nature = next((key for key, value in dict(problem_nature_choices).items() if value==problem_nature), None)

#         if equipment_id:
#             equipment_id = Equipment.objects.get(pk=equipment_id)
        
#         if machine_id:
#             machine_id = Machines.objects.get(pk=machine_id)

#         if assign_to_dpt:
#             department = Department.objects.get(pk=assign_to_dpt)

#         if assign_to_person:
#             assign_person = CustomUser.objects.get(pk=assign_to_person)

#         #write code for handling exceptions

#         machine_issue = MachineIssue(
#             user = user,
#             equipment = equipment_id,
#             machine_id = machine_id,
#             date_time = date_time,
#             description=description,
#             machine_hours = machine_hours,
#             priority=selected_priority,
#             type = selected_type,
#             problem_nature = selected_problem_nature,
#             department = department,
#             assign_person = assign_person,
#             # machine_section=machine_section,
#             # malfunction_part = malfunction_part,
#         )
        
#         machine_issue.save()  
#         if images:
#             for image in images:
#                 image_model = ImageModel.objects.create(image=image)
#                 machine_issue.image.add(image_model) 

        

        
#         return redirect('maintenance:complain_list')



#     return render(request, 'maintenance/complain-form.html', {'equipment': equipments, 'departments':departments, 'users':users})


def get_machines(request):
    
    equipment_id = request.GET['equipment_id']
    
    if equipment_id:
        equipment = get_object_or_404(Equipment, pk=equipment_id)
        machines = Machines.objects.filter(type_of_machine=equipment).prefetch_related(
            Prefetch('machine_spare', queryset=Spares.objects.all())
        )
        machine_options = [{'id':machine.id, 'name':machine.name, 'spares':\
                            [{'id':spares.id, 'name':spares.name, 'item_code':spares.item_code} for spares in machine.machine_spare.all()]} \
                                for machine in machines]
    
    else:
        machine_options = []

    return JsonResponse({'machine_options':machine_options})

# def get_status(status):
#     print("inside status")
#     print(status)
#     status_to_url = {
#         'REVIEWED':'User:review_complain',
#         'APPROVED':'maintenance:complain_approve',
#     }
#     url_name = status_to_url.get(status)
    
#     if url_name:
#         print(type(url_name))
#         return f'{url_name}'
#     else:
#         print('status {}'.format(status))
#         return 'maintenace:complain_list'


def view_complains(request):

    user = request.user.id
    issue_list = MachineIssue.objects.all().order_by('-date_time')
    emp = Employee.objects.get(user=user)
    return render(request, "maintenance/complain-view.html", {'issue_list':issue_list, 'emp':emp})


def complain_detail(request, pk):
    issue = MachineIssue.objects.get(pk=pk)
    if issue.status == 'REJECTED':
        return render(request, "maintenance/rejected-complain-detail.html", {'issue':issue})
    if issue.status == 'APPROVED':
        return render(request,"maintenance/accepted-complain-detail.html",{'issue':issue})
    return render(request, "maintenance/complain-detail.html", {'issue':issue})

def complain_delete(request, pk):
    issue = MachineIssue.objects.get(pk=pk)
    issue.delete()
     
    return redirect("maintenance:complain_list")


def complain_reject(request, pk):
    
    issue = MachineIssue.objects.get(pk=pk)
    try: 
        if issue.issue_remarks:
            issue.status = 'REJECTED'
            issue.save()
            return render(request, "maintenance/rejected-complain-detail.html", {'issue':issue})
    except MachineIssue.issue_remarks.RelatedObjectDoesNotExist:
        if request.method == 'POST':
            user = request.user.id
            user_id = CustomUser.objects.get(pk=user)
            remarks = request.POST['man-remarks']
            print(remarks)

            new_comment = Remarks(
                user_id = user_id,
                complain_id = issue,
                comment = remarks
            )

            new_comment.save()

            issue.status = 'REJECTED'
            issue.save()

            return redirect("maintenance:complain_list")
        


def complain_approve(request, pk):
    
    user = CustomUser.objects.get(pk=request.user.id)
    issue = MachineIssue.objects.get(pk=pk)
    issue.status = 'APPROVED'
    issue.save()
    return redirect('maintenance:complain_list')

def complain_edit(request, pk):
    
    try:
        user = CustomUser.objects.get(pk=request.user.id)
        print(request.user.id)
    except CustomUser.DoesNotExist:
        return redirect("User:login")

    issue = MachineIssue.objects.get(pk=pk)
    equipments = Equipment.objects.all()
    
    priority_choice = (
        ('HIGH', 'H'),
        ('MODERATE', 'M'),
        ('LOW', 'L')
    )
 
    type_choices = (
        ('CORRECTIVE', 'C'),
        ('PREVENTIVE', 'P'),
        ('BREAKDOWN', 'B')
    )

    if request.method == 'POST':
        equipment_id = request.POST['machine-select']
        machine_id = request.POST['machine-num-select']
        date_time = request.POST['date-time']
        machine_section = request.POST['machine-section']
        malfunction_part = request.POST['malfunction-part']
        machine_hours = request.POST['machine-hours']
        priority = request.POST["issue-priority"]
        description = request.POST['malfunction-desc']
        images = request.FILES.getlist('machine-images[]')
        issue_type = request.POST["issue-type"]

        selected_priority = next((key for key, value in dict(priority_choice).items() if value==priority), None)

        selected_type = next((key for key, value in dict(type_choices).items() if value==issue_type), None)

        if equipment_id:
            equipment_id = Equipment.objects.get(pk=equipment_id)
        
        if machine_id:
            machine_id = Machines.objects.get(pk=machine_id)

        #write code for handling exceptions

        issue = MachineIssue(
            user = user,
            equipment = equipment_id,
            machine_id = machine_id,
            date_time = date_time,
            description=description,
            machine_hours = machine_hours,
            priority=selected_priority,
            type = selected_type,
            # machine_section=machine_section,
            # malfunction_part = malfunction_part,
        )
        
        issue.save()  

        for image in images:
            image_model = ImageModel.objects.create(image=image)
            issue.image.add(image_model) 

        

        
        return redirect('maintenance:complain_list')



    return render(request, 'maintenance/complain-form.html', {'equipment': equipments, 'issue':issue})
        





