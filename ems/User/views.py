from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from core import models
from django.views.decorators.cache import never_cache
from django.core.files.storage import default_storage
from django.core.exceptions import ObjectDoesNotExist
from PIL import Image

# Create your views here.

def index(request):
    return render(request, "user/index.html")

def home(request):
    return render(request, "user/home.html")


def machine_detail(request,pk):
    
    machine_detail = models.Machines.objects.get(pk=pk)
    return render(request, "user/machine_detail.html", {"machine_detail":machine_detail})


def add_machine(request):

    spares = models.Spares.objects.all()
    equipments = models.Equipment.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        type_of_machine = request.POST.get('type-of-machine')
        spares_list = request.POST.getlist('spares-list')
        model = request.POST.get('model')
        dop = request.POST.get('dop')
        purchase_cost = request.POST.get('purchase_cost')
        image = request.POST.get('image')

        
        machine_type = models.Equipment.objects.get(pk=type_of_machine)
        spares = models.Spares.objects.filter(pk__in=spares_list)


        machine = models.Machines(
            name=name,
            type_of_machine = machine_type,
            model = model,
            dop = dop,
            purchase_cost = purchase_cost,
            image=image, 
        )

        machine.save()

        machine.spares.add(*spares)

        return redirect("User:home")


    return render(request, "user/add_machine.html",{'spares': spares, 'equipments':equipments})


def edit_machine(request,pk):

    machine_val = models.Machines.objects.get(pk=pk)
    return render(request, "user/update_machine.html", {'machine_val':machine_val})

@csrf_exempt
def update_machine(request,pk):
    machine = models.Machines.objects.get(pk=pk)
    if request.method == "POST" and request.FILES.getlist('machine-image'):
        type_of_machine = request.POST.get('type-of-machine')
        name = request.POST.get('name')
        model = request.POST.get('model')
        purchase_cost = request.POST.get('purchase_cost')
        machine_type = models.Equipment.objects.get(name=type_of_machine)

        img = request.FILES.get('machine-image')
        filename = default_storage.save(img.name, img)
        
        
        machine = models.Machines(
            pk=pk,
            type_of_machine = machine_type,
            name=name,
            model=model,
            purchase_cost=purchase_cost,
            image = filename
        )

        machine.save()

        return JsonResponse({"message": "Form data received"})

    elif request.method == "POST":
        type_of_machine = request.POST.get('type-of-machine')
        name = request.POST.get('name')
        model = request.POST.get('model')
        purchase_cost = request.POST.get('purchase_cost')

        machine_type = models.Equipment.objects.get(name=type_of_machine)

        machine = models.Machines(
            pk=pk,
            type_of_machine = machine_type,
            name=name,
            model=model,
            purchase_cost=purchase_cost,
        )

        machine.save()

        return JsonResponse({"message": "Form data received"})


def delete_machine(request, pk):
    if pk:
        machine = models.Machines.objects.get(pk=pk)
        machine.delete()
        return redirect("User:home") 
    return redirect("User:home") 


def spare_view(request):
    spares = models.Spares.objects.all().order_by("pk")
    return render(request, 'user/sparesDetail.html', {'spares':spares})



def spare_add(request):
    
    if request.method=='POST':
        print("i am here")
        item_code = request.POST.get('item-code')
        name = request.POST.get('name')
        quantity = request.POST.get('quantity')
        unit = request.POST.get('unit')

        spare = models.Spares(
            item_code=item_code,
            name=name,
            quantity=quantity,
            unit=unit)
        
        spare.save()

        return JsonResponse({"message": "Form data received"})
    return JsonResponse({"message": "Form data received"})


def spare_delete(request,pk):
    try:
        
        spare = models.Spares.objects.get(pk=pk)
        
        if spare:
    
            spare.delete()
            return redirect('User:spares')
    except ObjectDoesNotExist:
        return JsonResponse({'message': "Object not found"})
    
    return redirect("User:spares")