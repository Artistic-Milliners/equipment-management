from django.shortcuts import render, get_object_or_404, redirect
from core.models import MachineIssue,Equipment, Machines, Spares, MachineSpares, ImageModel, CustomUser
from django.http import JsonResponse
from django.db.models import Prefetch
from django.core.files.storage import default_storage
from User.views import home
# Create your views here.

def createComplain(request):

    priority_choice = (
        ('High', 'H'),
        ('Moderate', 'M'),
        ('Low', 'L')
    )

    user_id = request.user.id
    user = CustomUser.objects.get(pk=user_id)
    equipments = Equipment.objects.all()

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

        selected_priority = next((key for key, value in dict(priority_choice).items() if value==priority), None)


        if equipment_id:
            equipment_id = Equipment.objects.get(pk=equipment_id)
        
        if machine_id:
            machine_id = Machines.objects.get(pk=machine_id)

        #write code for handling exceptions


        machine_issue = MachineIssue(
            user = user,
            equipment = equipment_id,
            machine_id = machine_id,
            date_time = date_time,
            # machine_section=machine_section,
            # malfunction_part = malfunction_part,
            description=description,
            machine_hours = machine_hours,
            priority=selected_priority,
        )
        
        machine_issue.save()  

        for image in images:
            image_model = ImageModel.objects.create(image=image)
            machine_issue.image.add(image_model) 

        

        
        return redirect('maintenance:complain_list')



    return render(request, 'maintenance/complain-form.html', {'equipment': equipments})


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

def view_complains(request):
    
    issue_list = MachineIssue.objects.all().order_by("priority")

    return render(request, "maintenance/complain-view.html", {'issue_list':issue_list})


def complain_detail(request, pk):
    issue = MachineIssue.objects.get(pk=pk)
    return render(request, "maintenance/complain-detail.html", {'issue':issue})

def complain_delete(request, pk):
    issue = MachineIssue.objects.get(pk=pk)
    issue.delete()
     
    return redirect("maintenance:complain_list")