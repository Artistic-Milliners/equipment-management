from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, PasswordResetForm
from django.contrib.auth.models import User
from core.models import CustomUser, MachineIssueReview, Employee, Unit, MachineIssue, Spares, Equipment, Machines, ImageModel, Department,MachineIssueReview
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.views import View
from django.views.generic import ListView, CreateView, DetailView
from .forms import UnitForm
from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from core import models
from django.views.decorators.cache import never_cache
from django.core.files.storage import default_storage
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
from django.urls import reverse_lazy
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from core.serializers import machineHoursSerializer,MachineCodeSerializer
from django.db.models import Prefetch
from django.http import Http404
import logging

# Create your views here.


class ListUsers(ListView):
    model = Employee
    context_object_name = "users"
    template_name = "user/listusers.html"

class DetailUserView(DetailView):
    pass


class CreateUnitView(CreateView):
    model = Unit
    fields = ["id", "name", "location"]
    template_name = "user/createunit.html"
    success_url = reverse_lazy("User:list_unit")

class ListUnitView(ListView):
    model = Unit
    template_name = "user/listunit.html"
    context_object_name = "units"


class InitiateComplainView(View):
    template_name = "user/initiate-complain.html"
    
    def get(self, request):
        user = request.user
        # print(user)
        equipment = models.Equipment.objects.all()
        return render(request, self.template_name, {'user':user, 'equipments':equipment})
    
    
    def post(self,request, *args, **kwargs):


        user_id = request.user.id
        equipment_id = request.POST['equipment']
        machine_code = request.POST['code']
        machine_hours = request.POST['machine-hours']
        description = request.POST['description']
        image = request.FILES.getlist('image[]')
        status_choice = MachineIssue.STATUS_CHOICES
        # print(request.user)
        
        try:
            employee = Employee.objects.get(user=user_id)
            equipment = Equipment.objects.get(pk=equipment_id)    
            machine = Machines.objects.get(pk=machine_code)
        
        except ObjectDoesNotExist as e:
            return render(request, 'user/error/404.html', {'e': str(e)})
        
        

        issue = MachineIssue(
            user = employee,
            equipment = equipment,
            machine_id=machine,
            machine_hours=machine_hours,
            description_user=description,
        )

        issue.status = status_choice[0][0]    
        issue.save() 
        print(issue.status)


        if image:
            for img in image:
                try:
                    image_model = ImageModel.objects.create(image=img)
                    issue.image.add(image_model)
                except Exception as e:
                    return render(request, 'user/error/404.html', {'e': str(e)})

        
        return redirect('maintenance:complain_list')



class ComplainReviewView(View):
    def get(self, request, pk):


        departments = Department.objects.filter(dpt_type__in=['SERVICES','MAINTENANCE'])
        users = Employee.objects.filter(department__in=departments)
        
        issue = MachineIssue.objects.select_related(
                'machine_id'
                ).prefetch_related(Prefetch(
                    'machine_id__machine_spare',  queryset=Spares.objects.all())).get(pk=pk)
        
        priorityChoices = MachineIssueReview.PRIORITY_CHOICES
        statusChoices = MachineIssueReview.STATUS_CHOICES
        typeChoices = MachineIssueReview.TYPE_CHOICES 
        problemNatureChoices = MachineIssueReview.PROBLEM_NATURE_CHOICES

        print(type(issue.date_time))

        context = {'priorityChoices':priorityChoices, 
                    'statusChoices':statusChoices,
                     'typeChoices':typeChoices,
                      'problemNatureChoices':problemNatureChoices,
                       "issue":issue, 
                       'departments':departments,
                       'users':users,
                       }

        return render(request, 'maintenance/complain-form.html',context)

    def post(self, request, *args, **kwargs):
        
        user_id = request.user.id
        issue_id = request.POST['issue-number']
        description_reviewer = request.POST['description-reviewer']
        priority = request.POST['issue-priority']
        type = request.POST['issue-type']
        problemNature = request.POST['problem-nature']
        assignDepartment= request.POST['assign-to-department']
        person = request.POST['assign-to-person']
        reviewrImages = request.FILES.getlist('machine-images[]')

        try: 
            user = CustomUser.objects.get(pk=user_id)
            reviewer = Employee.objects.get(user=user)
            issue = MachineIssue.objects.get(pk=issue_id)
            departmentName = Department.objects.get(pk=assignDepartment)
            assignPerson = Employee.objects.get(pk=person)
            
            review = MachineIssueReview(
            reviewer = reviewer,
            issue = issue,
            description_reviewer = description_reviewer,
            priority = priority,
            type = type,
            problemNature = problemNature,
            assignDepartment = departmentName,
            assignPerson = assignPerson
             )
            review.save()
            if reviewrImages:
                for img in reviewrImages:
                    image = ImageModel.objects.create(img)
                    review.reviewrImages.add(image) 
            
        except Exception as e:
            logging.error("Error Occured in ComplainReview Post Function:", exc_info=True)
            return render(request, 'user/error/404.html', {'error':str(e)})
        


        
        
        issue.status = MachineIssue.STATUS_CHOICES[1][0]
        # print(issue.status)
        issue.save()



        # print(review.reviewer)
        return redirect('User:approval_list')
        

class ApprovalListView(ListView):
    status = MachineIssue.STATUS_CHOICES
    template_name = 'user/approvalList.html'
    queryset = MachineIssueReview.objects.all()
    context_object_name = 'reviews'



class UserDetailAPIView(APIView):
    pass
    

class MachineCodeAPIView(APIView):
    
    def get_queryset(self):
        return models.Equipment.objects.all() 
    
    def get(self, request, pk):
        
        try:
            equipment = self.get_queryset().get(pk=pk)
            machines = models.Machines.objects.filter(type_of_machine=equipment)
            machine_code = MachineCodeSerializer(machines, many=True).data
            print(machine_code)
            return JsonResponse(machine_code, safe=False)

        except models.Equipment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class machineHoursAPIView(APIView):
    def get_queryset(self):
        return models.Machines.objects.all()
    
    
    def get(self, request, pk):
        
        try: 
            machine = models.Machines.objects.get(pk=pk)
            machine_hours = machineHoursSerializer(machine)
            # print(machine_hours.data)
            return Response(machine_hours.data)
        
        except models.Machines.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

def login_view(request):
    
    if request.method == "POST":
        try:
            username = request.POST['username']
            password = request.POST['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                
                login(request, user)
                return redirect('User:home')
            
            else :
                error_message = 'Invalid Login credentials'
                return render(request, "registration/login.html", {'error': error_message}) 
        except MultiValueDictKeyError:
                form = AuthenticationForm()
                return render(request,'registration/login.html',{'form':form})
        
    else:
        form = AuthenticationForm()
        return render(request,'registration/login.html',{'form':form})

def logout_view(request):
    logout(request)
    return redirect("User:login")



def index(request):
    return render(request, "user/index.html")

@login_required
def home(request):
    
    return render(request, "user/home.html")


def machine_detail(request,pk):
    
    machine_detail = models.Machines.objects.get(pk=pk)
    return render(request, "user/machine_detail.html", {"machine_detail":machine_detail})

@permission_required('core.machine_create_perm', raise_exception=True)
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
        image = request.FILES.get('machine-image')


        
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


        machine.machine_spare.add(*spares)

        return redirect("User:home")


    return render(request, "user/add_machine.html",{'spares': spares, 'equipments':equipments})


def edit_machine(request,pk):

    machine_val = models.Machines.objects.get(pk=pk)
    return render(request, "user/update_machine.html", {'machine_val':machine_val})

@csrf_exempt
def update_machine(request,pk):
    
    machine = models.Machines.objects.get(pk=pk)

    if request.method == "POST":
        type_of_machine = request.POST.get('type-of-machine')
        name = request.POST.get('name')
        model = request.POST.get('model')
        purchase_cost = request.POST.get('purchase_cost')
        machine_hours = request.POST.get('machine-hours')
        # print(type_of_machine)

        machine_type = models.Equipment.objects.get(name=type_of_machine)
        # print(machine_type)
        
        if request.FILES.get('machine-image'):
            img = request.FILES.get('machine-image')
            filename = default_storage.save('images/'+img.name, img)
            machine.image = filename


        machine.type_of_machine = machine_type
        machine.name=name
        machine.model=model
        machine.purchase_cost=purchase_cost
        machine.machine_hours=machine_hours
        
        machine.save()

        return redirect( 'User:home' )
        
        
        
        # machine = models.Machines(
        #     pk=pk,
        #     )

        
    # elif request.method == "POST":
    #     type_of_machine = request.POST.get('type-of-machine')
    #     name = request.POST.get('name')
    #     model = request.POST.get('model')
    #     purchase_cost = request.POST.get('purchase_cost')
    #     machine_type = models.Equipment.objects.get(name=type_of_machine)
    #     # print(default_storage.url())

    #     machine = models.Machines(
    #         pk=pk,
    #         type_of_machine = machine_type,
    #         name=name,
    #         model=model,
    #         purchase_cost=purchase_cost,
    #     )

    #     machine.save()

    # return redirect( 'User:home' )


def delete_machine(request, pk):
    if pk:
        machine = models.Machines.objects.get(pk=pk)
        machine.delete()
        return redirect("User:home") 
    return redirect("User:home") 


def spare_view(request):
    if request.method == "GET":
        search_filter = request.GET.get("search-bar")
        if search_filter:
            spares = models.Spares.objects.filter(name__icontains=search_filter).order_by("-pk")
        else :
            spares = models.Spares.objects.all().order_by("-pk")
    
    return render(request, 'user/sparesDetail.html', {'spares':spares})



def spare_add(request):
    
    if request.method=='POST':
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


def spare_update(request,pk):
    spare = models.Spares.objects.get(pk=pk)

    try:
        if request.method == "POST":
            item_code = request.POST.get('update-item-code')
            item_name = request.POST.get('update-name')
            item_quantity = request.POST.get('update-quantity')
            item_unit = request.POST.get('update-unit')

            spare = models.Spares(
                pk = pk,
                item_code = item_code,
                name = item_name,
                quantity = item_quantity,
                unit = item_unit
            )

            spare.save()

        return JsonResponse({"MESSAGE":"Spare data updated successfully"})

    except Exception as e:
        return JsonResponse({"Error": e})


def spare_delete(request,pk):
    try:
        
        spare = models.Spares.objects.get(pk=pk)
        
        if spare:

            spare.delete()
            return redirect('User:spares')
    
    except ObjectDoesNotExist:
        return JsonResponse({'message': "Object not found"})
    
    return redirect("User:spares")

def spare_issue(request, pk):

    current_quantity = models.Spares.objects.filter(pk=pk).values()[0]["quantity"]
    try:        
        if request.method == 'POST':
            
            quantity = int(request.POST.get("issue-quantity"))
            
            if quantity <= current_quantity:
                updated_quantity = current_quantity-quantity
            else:
                return JsonResponse({"Quantity":"Required quantity is more than available quantity"})


            item_code = request.POST.get("issue-item-code")
            name = request.POST.get("issue-name")
            unit = request.POST.get("issue-unit")




            spare = models.Spares(
                pk = pk,
                item_code=item_code,
                name=name,
                unit=unit,
                quantity = updated_quantity
            )

            spare.save()

            return JsonResponse({"Successful: Issue Successfully"})
    except Exception as e:
            return JsonResponse({"Error": e})

    



        