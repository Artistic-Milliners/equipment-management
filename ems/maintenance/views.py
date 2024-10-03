from django.shortcuts import render, get_object_or_404, redirect
from core.models import MachineIssue,Equipment, Machines, Spares, MachineSpares, ImageModel, CustomUser, MachineIssueApproval, Department, Employee  
from django.http import JsonResponse
from django.db.models import Prefetch
from django.contrib.auth.decorators import permission_required, login_required
from django.core.files.storage import default_storage
from User.views import home


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


@login_required
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
   

def complain_approve(request, pk):
    
    choices = MachineIssue.STATUS_CHOICES

    if request.method == 'POST':
        
        user = CustomUser.objects.get(pk=request.user.id)   
        issue = MachineIssue.objects.get(pk=pk)
        status = request.POST["status"]

        if status == 'Approved':
            issue.status = choices[2][1]
        else:
            issue.status = choices[3][1]
        
        comment = request.POST['man-remarks']    
            
        issue.save()
        
        try:
            approval = MachineIssueApproval(
            user_id = user,
            complain_id = issue,
            comment = comment,
            )
            approval.status = approval.STATUS_CHOICES[1][0]
            approval.save()
            # print("approved complain")
            
        
        except Exception as e:
            print(str(e))
        

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
        





