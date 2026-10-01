from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, PasswordResetForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.db.models.query import QuerySet
from django.db.models import Q, Avg, Sum, Count
from core.models import (Contractor, CustomUser, MachineIssueReview, Employee,
                         Unit, MachineIssue, Spares, Equipment,
                         Machines, ImageModel, Department,
                         MachineIssueReview, IssueClosing, MachineSpares,
                         IssueList, TemporaryIssue, MachineSection, QuickReviewComments)
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.views import View
from django.views.generic import ListView, CreateView, DetailView
from .forms import UnitForm
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
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
from core.serializers import machineHoursSerializer,MachineCodeSerializer, IssueSerializer
from django.db.models import Prefetch
from django.http import Http404
import logging

# Create your views here.

logger = logging.getLogger(__name__)


class ListUsers(ListView):
    
    model = Employee
    context_object_name = "users"
    template_name = "user/listusers.html"

class DetailUserView(DetailView):
    
    model = Employee
    context_object_name = 'user'
    template_name = "user/detailUser.html"


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
        try:
            emp = Employee.objects.get(user=user)
        except Exception as e:
            return render(request, 'user/error/404.html', {'e': str(e)})
        department = emp.department
        if department.dpt_type not in ['SERVICES', 'MAINTENANCE']:
            equipment = models.Equipment.objects.filter(typeOfMachine__Department=department).distinct()
            if equipment.count() == 0:
                return render(request, 'user/error/404.html', {'e': 'No equipment found for your department'})
        else:
            equipment = models.Equipment.objects.all()
        departments = Department.objects.filter(dpt_type__in=['SERVICES','MAINTENANCE'])
        return render(request, self.template_name, {'user':user, 'equipments':equipment, 'departments':departments})
    
    
    def post(self,request, *args, **kwargs):


        user_id = request.user.id
        equipment_id = request.POST['equipment']
        machine_code = request.POST['code']
        machine_hours = request.POST['machine-hours']
        description = request.POST['description']
        image = request.FILES.getlist('image[]')
        error_department = request.POST["error-department"]

        # New fields for issue selection
        issue_type = request.POST.get('issue-type')  # 'existing' or 'other'
        selected_issue_id = request.POST.get('selected-issue-id', None)
        custom_issue_description = request.POST.get('custom-issue-description', None)
        machine_section_id = request.POST.get('machine-section', None)


        try:
            employee = Employee.objects.get(user=user_id)
            equipment = Equipment.objects.get(pk=equipment_id)
            machine = Machines.objects.get(pk=machine_code)
            error_department = Department.objects.get(pk=error_department)
            
            if not machine_hours:
                machine_hours = Machines.objects.get(pk=machine_code).machine_hours

        except ObjectDoesNotExist as e:
            return render(request, 'user/error/404.html', {'e': str(e)})



        issue = MachineIssue(
            user = employee,
            equipment = equipment,
            machine_id=machine,
            machine_hours=machine_hours,
            description_user=description,
            error_department=error_department
        )

        # Handle machine section
        if machine_section_id:
            try:
                machine_section = MachineSection.objects.get(pk=machine_section_id)
                issue.machine_section = machine_section
            except MachineSection.DoesNotExist:
                pass

        # Handle issue selection
        if issue_type == 'existing' and selected_issue_id:
            # User selected from existing IssueList
            try:
                selected_issue = IssueList.objects.get(pk=selected_issue_id)
                print(selected_issue)
                issue.selected_issue = selected_issue
            except IssueList.DoesNotExist:
                pass

        elif issue_type == 'other' and custom_issue_description:
            # User entered custom issue - create TemporaryIssue
            temp_issue = TemporaryIssue.objects.create(
                user=request.user,
                equipment=equipment,
                machine=machine,
                user_description=custom_issue_description
            )
            issue.temporary_issue = temp_issue

        issue.status = MachineIssue.STATUS_PENDING
        issue.save()
        print(issue.status)


        if image:
            for img in image:
                try:
                    image_model = ImageModel.objects.create(image=img)
                    issue.reduce_image_size(image_model)  # Reduce image size before saving
                    issue.image.add(image_model)
                except Exception as e:
                    return render(request, 'user/error/404.html', {'e': str(e)})

        
        return redirect('maintenance:complain_list')


class ComplainTrackingView(View):
    def get(self, request, pk):
        issue = MachineIssue.objects.get(pk=pk)
        return render(request, 'user/complain-tracking.html', {'issue':issue})
    
    

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


        status_choices=MachineIssueReview.STATUS_CHOICES

        user_id = request.user.id
        issue_id = request.POST['issue-number']
        description_reviewer = request.POST['description-reviewer']
        reviewer_issue = request.POST.getlist('selected-issue')

        type = request.POST['issue-type']
        problemNature = request.POST['problem-nature']
        malfunction_part = request.POST.getlist('malfunction-part')
        reviewerImages = request.FILES.getlist('machine-images[]')
        
        try: 
            user = CustomUser.objects.get(pk=user_id)
            reviewer = Employee.objects.get(user=user)
            issue = MachineIssue.objects.get(pk=issue_id)
            with transaction.atomic():                
                
                review = MachineIssueReview.objects.create(
                    issue=issue,
                    reviewer=reviewer,
                    description_reviewer=description_reviewer,
                    type=type,
                    problemNature=problemNature,
                )
                
                if reviewerImages:
                    for img in reviewerImages:
                        image = ImageModel.objects.create(image=img)
                        print(image)
                        review.reviewerImages.add(image)

                if malfunction_part:
                    for pk in malfunction_part:
                        part = Spares.objects.get(pk=pk)
                        review.malfunction_part.add(part)
                    

                review.save()
        except Exception as e:
            # logging.error("Error Occured in ComplainReview Post Function:", exc_info=True)
            print(str(e))
            return render(request, 'user/error/404.html', {'error':str(e)})

        # Record documentation timestamp
        issue.documentation_timestamp = timezone.now()

        # Calculate documentation time
        if issue.user_confirmation_timestamp:
            time_diff = issue.documentation_timestamp - issue.user_confirmation_timestamp
            issue.documentation_hours = time_diff.total_seconds() / 3600

        # Get engineer's resolution decision from form
        # This field should be added to the review template
        engineer_resolution = request.POST.get('engineer-resolution', 'WORKING')

        if engineer_resolution == 'RESOLVED':
            # Engineer says issue is fixed
            # Use existing user acknowledgment flow
            issue.status = MachineIssue.STATUS_RESOLVED
            issue.save()

            messages.success(request,
                f'Complaint {issue.ticket_num} marked as RESOLVED. '
                f'User {issue.user.name} must confirm resolution before you can close it.')

        else:  # engineer_resolution == 'WORKING'
            # Engineer says still working on it - needs approval
            issue.status = MachineIssue.STATUS_REVIEWED
            issue.save()

            messages.success(request,
                f'Review completed for complaint {issue.ticket_num}. '
                f'Awaiting management approval.')

        return redirect('maintenance:complain_list')




class ComplainClosingView(LoginRequiredMixin, View):
    
    """
    
    Uses atomic transactions for data integrity and proper logging.
    
    """

    def get(self, request, pk):
        """Display the closing form"""
        issue = get_object_or_404(MachineIssue, pk=pk)

        # Authorization check
        if not self._can_close(request.user, issue):
            messages.error(request, "You are not authorized to close this complaint.")
            return redirect('maintenance:complain_list')

        # Ensure review exists
        review = getattr(issue, 'machineissue', None)
        if not review:
            messages.info(request, f'Complete the review form before closing {issue.ticket_num}')
            return redirect('User:review_complain', pk=pk)

        context = {
            'issue': issue,
            'review': review,
            'contractors': Contractor.objects.all(),
            'spares': MachineSpares.objects.filter(machine=issue.machine_id),
        }
        return render(request, "user/complain_closing.html", context)

    def post(self, request, pk):
        
        """Process the closing form with atomic transaction"""
        issue = get_object_or_404(MachineIssue, pk=pk)

        # Authorization check
        if not self._can_close(request.user, issue):
            messages.error(request, "You are not authorized to close this complaint.")
            return redirect('maintenance:complain_list')

        try:
            with transaction.atomic():
                # Create closing record
                closing = self._create_closing_record(request, issue)

                # Save images (collect errors but don't fail)
                image_errors = self._save_images(request, closing)

                # Save spares
                self._save_spares(request, closing)

                # Update issue status
                self._close_issue(issue)

                # User feedback
                if image_errors:
                    messages.warning(request, f"Closed successfully, but some images failed: {image_errors}")
                else:
                    messages.success(request, f"Complaint {issue.ticket_num} closed successfully.")

                logger.info(f"Issue {issue.ticket_num} closed by {request.user.username}")
                return redirect("User:complain_closing_list")

        except Exception as e:
            logger.exception(f"Failed to close issue {pk}")
            messages.error(request, f"Failed to close complaint: {str(e)}")
            return redirect('User:complain_closing', pk=pk)

    def _can_close(self, user, issue):
        """Check if user is authorized to close this issue"""
        try:
            emp = user.employee
            is_engineer = user.groups.filter(name="Engineer").exists()
            return not is_engineer or emp.department == issue.error_department
        except Employee.DoesNotExist:
            return False

    def _create_closing_record(self, request, issue):
        """Create the IssueClosing record"""
        contractor = None
        contractor_id = request.POST.get("resolvedby")
        if contractor_id:
            contractor = Contractor.objects.filter(pk=contractor_id).first()

        return IssueClosing.objects.create(
            issueReview=issue.machineissue,
            contractor=contractor,
            machineHours=request.POST["machine-hours"],
            supervisor=request.POST["supervisor"],
            technician=request.POST["technician"],
            solutionDescription=request.POST["solution-description"],
            duration=request.POST["duration"],
            remarks=request.POST["additional-remarks"],
            equipment_status=request.POST["equipment-status"],
            status='CLOSED'
        )

    def _save_images(self, request, closing):
        """Save uploaded images, return error message if any fail"""
        errors = []
        for image in request.FILES.getlist("image[]"):
            try:
                img = ImageModel.objects.create(image=image)
                closing.image.add(img)
            except Exception as e:
                errors.append(str(e))
                logger.warning(f"Failed to save image: {e}")
        return ", ".join(errors) if errors else None

    def _save_spares(self, request, closing):
        """Save installed spares"""
        for spare_id in request.POST.getlist("states[]"):
            spare = Spares.objects.filter(pk=spare_id).first()
            if spare:
                closing.installed_spares.add(spare)

    def _close_issue(self, issue):
        """Update issue status and timestamps"""
        issue.closure_timestamp = timezone.now()

        if issue.documentation_timestamp:
            diff = issue.closure_timestamp - issue.documentation_timestamp
            issue.closure_hours = diff.total_seconds() / 3600

        if issue.date_time:
            diff = issue.closure_timestamp - issue.date_time
            issue.total_downtime_hours = diff.total_seconds() / 3600

        issue.status = 'CLOSED'
        issue.save()
        

class ClosedComplainListView(ListView):
    template_name = 'user/closedComplainList.html'
    context_object_name = 'closedComplains'
    paginate_by = 20

    def get_queryset(self):
        # Optimized query with all related data
        queryset = IssueClosing.objects.select_related(
            'issueReview__issue__user',
            'issueReview__issue__equipment',
            'issueReview__issue__machine_id',
            'issueReview__issue__error_department',
            'issueReview__reviewer',
            'issueReview__assignDepartment',
            'contractor'
        ).prefetch_related(
            'installed_spares',
            'image',
            'issueReview__malfunction_part'
        ).order_by('-date_ended')

        # Apply filters from GET parameters
        equipment_id = self.request.GET.get('equipment')
        contractor_id = self.request.GET.get('contractor')
        status = self.request.GET.get('status')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        search_query = self.request.GET.get('search')

        if equipment_id:
            queryset = queryset.filter(issueReview__issue__equipment_id=equipment_id)

        if contractor_id:
            queryset = queryset.filter(contractor_id=contractor_id)

        if status:
            queryset = queryset.filter(status=status)

        if date_from:
            queryset = queryset.filter(date_ended__gte=date_from)

        if date_to:
            queryset = queryset.filter(date_ended__lte=date_to)

        if search_query:
            queryset = queryset.filter(
                Q(issueReview__issue__ticket_num__icontains=search_query) |
                Q(issueReview__issue__description_user__icontains=search_query) |
                Q(solutionDescription__icontains=search_query) |
                Q(technician__icontains=search_query) |
                Q(supervisor__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get all closed complains for statistics (before pagination)
        all_closed = IssueClosing.objects.all()

        # Calculate statistics
        from django.utils import timezone
        from django.db.models import Avg, Count, Q
        from datetime import timedelta

        total_closed = all_closed.count()

        # Closed this month
        today = timezone.now()
        first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        closed_this_month = all_closed.filter(date_ended__gte=first_day_of_month).count()

        # Average resolution time (in hours)
        avg_duration = all_closed.aggregate(avg=Avg('duration'))['avg'] or 0

        # Count by status
        status_closed = all_closed.filter(status='CLOSED').count()
        status_pending = all_closed.filter(status='PENDING').count()

        # Count with spares installed
        with_spares = all_closed.annotate(
            spares_count=Count('installed_spares')
        ).filter(spares_count__gt=0).count()

        # Filter options
        from core.models import Equipment, Contractor
        all_equipment = Equipment.objects.all()
        all_contractors = Contractor.objects.all()

        context.update({
            'total_closed': total_closed,
            'closed_this_month': closed_this_month,
            'avg_resolution_time': round(avg_duration, 1) if avg_duration else 0,
            'status_closed': status_closed,
            'status_pending': status_pending,
            'with_spares_count': with_spares,
            'all_equipment': all_equipment,
            'all_contractors': all_contractors,
            'status_choices': IssueClosing.STATUS_CHOICES,
        })

        return context


class ApprovalListView(ListView):
    status = MachineIssue.STATUS_CHOICES
    template_name = 'user/approvalList.html'
    queryset = MachineIssueReview.objects.all()
    context_object_name = 'reviews'



class UserDetailAPIView(APIView):
    pass



class filterTicketAPIView(APIView):
    def get_queryset(self):
        return MachineIssue.objects.all()
    
    def get(self, request, filter):
        # print("User views inside filterTicketAPIView")
        if filter == 'department':
            print('inside if condition')
            qs = self.get_queryset().order_by('-user__department')
            print('Data for department query is {}'.format(qs))
        else:
            qs = self.get_queryset().order_by('date_time')
            print(qs)
        issueList = IssueSerializer(qs, many=True).data
        return JsonResponse(issueList, safe=False)
        


class MachineCodeAPIView(APIView):
    
    def get_queryset(self):
        return models.Equipment.objects.all() 
    
    def get(self, request, pk):
        
        try:
            equipment = self.get_queryset().get(pk=pk)
            machines = models.Machines.objects.filter(type_of_machine=equipment)
            machine_code = MachineCodeSerializer(machines, many=True).data
            # print(machine_code)
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


class IssueListAPIView(APIView):
    """API endpoint to fetch IssueList based on equipment selection"""
    permission_classes = []  # Allow unauthenticated access

    def get(self, request, equipment_pk):
        try:
            # Get all issues for this equipment
            issues = IssueList.objects.filter(equipment_id=equipment_pk).values(
                'id', 'c_desc', 'error_code', 'programmer_string', 'machine_string', 'machine_status'
            )

            return JsonResponse({
                'success': True,
                'issues': list(issues)
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class MachineSectionAPIView(APIView):
    """API endpoint to fetch MachineSection based on machine selection"""
    permission_classes = []  # Allow unauthenticated access

    def get(self, request, machine_pk):
        try:
            # Get all sections for this machine
            sections = MachineSection.objects.filter(machine_id=machine_pk).values(
                'id', 'section_name'
            )

            return JsonResponse({
                'success': True,
                'sections': list(sections)
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


def login_view(request):
    
    if request.method == "POST":
        
        try:
            username = request.POST['username']
            password = request.POST['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('User:home')
            
            else:
                error_message = 'Invalid Login credentials'
                return render(request, "registration/login.html", {'error': error_message}) 
        
        except MultiValueDictKeyError:
                
                form = AuthenticationForm()
                return render(request,'registration/login.html',{'form':form})
        
    else:
        # form = AuthenticationForm()
        return render(request,'registration/login.html')

def logout_view(request):
    logout(request)
    return redirect("User:login")



def index(request):
    """
    Root URL handler - redirects based on authentication status
    - If user is logged in: redirect to home/dashboard
    - If user is not logged in: redirect to login page
    """
    if request.user.is_authenticated:
        # User is logged in, redirect to home
        return redirect('User:home')
    else:
        # User is not logged in, redirect to login
        return redirect('User:login')

@login_required
def home(request):
    from datetime import datetime, date

    # Get today's date
    today = date.today()

    # Calculate statistics
    total_issues = MachineIssue.objects.count()
    pending_issues = MachineIssue.objects.filter(status='PENDING').count()

    # Get issues resolved today (status RESOLVED, CLOSED, or APPROVED)
    # Note: Using date_time for now until timestamp tracking fields are added
    resolved_today = MachineIssue.objects.filter(
        status__in=['RESOLVED', 'CLOSED', 'APPROVED'],
        date_time__date=today
    ).count()

    # Critical issues: machines with operational status NON_OPERATIONAL and status not yet closed
    critical_issues = MachineIssue.objects.filter(
        operational_status='NON_OPERATIONAL',
        status__in=['PENDING', 'UNDER_OBSERVATION', 'REVIEWED']
    ).count()

    context = {
        'total_issues': total_issues,
        'pending_issues': pending_issues,
        'resolved_today': resolved_today,
        'critical_issues': critical_issues,
    }

    return render(request, "user/home.html", context)


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


@login_required
def user_close_complaint(request, pk):
    """
    Allow user who raised complaint to confirm resolution when status is ~User Feedback~.
    Changes status from User Feedback to either AWAITING_DOCUMENTATION or PENDING depending on the user selection.
    """
    if request.method == 'POST':
        
        employee = request.user.employee   
        
        try:      
            issue = MachineIssue.objects.get(pk=pk)

            # Verify the current user is the one who created the complaint
            if issue.user.user != request.user:
                return render(request, 'user/error/404.html', {
                    'error': 'You can only close complaints that you created'
                })

            # Verify status is User Feedback
            if issue.status != 'User Feedback':
                return render(request, 'user/error/404.html', {
                    'error': f'The engineer is still working on the complain you cannot close it {str(issue.status)}'
                })

            # Get optional user feedback
            user_feedback = request.POST.get('user-feedback', '')
            status = request.POST.get('status', '')
            
            if status.lower() != 'resolved':
                # Update status to pending
                print("inside if condition")
                try:
                    
                    comment = QuickReviewComments.objects.create(
                        issue=issue,
                        commenter= employee,
                        comment=user_feedback,
                    )
                    
                    issue.status = issue.STATUS_CHOICES[0][0]  # PENDING

                    issue.save()

                    return redirect('User:complain_track', pk=pk)

                except Exception as e:
                    print(str(e))
                    return render(request, 'user/error/404.html', {
                        'error': f'Error saving feedback: {str(e)}'
                    })
 
            
            try:
                comment = QuickReviewComments.objects.create(
                    issue=issue,
                    commenter= employee,
                    comment=user_feedback,
                )
                issue.status = 'AWAITING_DOCUMENTATION'
            except Exception as e:
                print(str(e))
                return render(request, 'user/error/404.html', {
                    'error': f'Error saving feedback: {str(e)}'
                })
            
            


            # Record user confirmation timestamp
            issue.user_confirmation_timestamp = timezone.now()

            # Calculate user response time
            if issue.quick_review_timestamp:
                time_diff = issue.user_confirmation_timestamp - issue.quick_review_timestamp
                issue.user_response_hours = time_diff.total_seconds() / 3600

            # Store user feedback if provided (you might want to add this to description or a new field)
            # if user_feedback:
            #     issue.description_user = f"{issue.description_user}\n\n[User Confirmation Feedback]: {user_feedback}"

            issue.save()

            print(f"\n{'='*60}")
            print(f"USER COMPLAINT CLOSURE")
            print(f"{'='*60}")
            print(f"Issue ID: {issue.pk}")
            print(f"Ticket #: {issue.ticket_num}")
            print(f"User: {request.user.username}")
            print(f"Status changed: RESOLVED → AWAITING_DOCUMENTATION")
            print(f"User feedback: {'Yes' if user_feedback else 'No'}")
            print(f"{'='*60}\n")

            # Redirect back to tracking page
            return redirect('User:complain_track', pk=pk)

        except MachineIssue.DoesNotExist:
            return render(request, 'user/error/404.html', {
                'error': 'Complaint not found'
            })
        except Exception as e:
            return render(request, 'user/error/404.html', {
                'error': str(e)
            })

    # GET request - redirect to tracking page
    return redirect('User:complain_track', pk=pk)


@login_required
def downtime_report(request):
    """
    Display downtime metrics for complaints
    """
    # Get filter parameters
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    equipment_id = request.GET.get('equipment')

    # Base queryset - only closed complaints with timestamps
    complaints = MachineIssue.objects.filter(
        status='CLOSED',
        closure_timestamp__isnull=False
    ).select_related('user', 'equipment', 'machine_id')

    # Apply filters
    if date_from:
        complaints = complaints.filter(date_time__gte=date_from)
    if date_to:
        complaints = complaints.filter(date_time__lte=date_to)
    if equipment_id:
        complaints = complaints.filter(equipment_id=equipment_id)

    # Calculate aggregate metrics
    metrics = complaints.aggregate(
        total_complaints=Count('id'),
        avg_total_downtime=Avg('total_downtime_hours'),
        avg_engineer_response=Avg('engineer_response_hours'),
        avg_user_response=Avg('user_response_hours'),
        avg_documentation=Avg('documentation_hours'),
        avg_closure=Avg('closure_hours'),
        total_downtime=Sum('total_downtime_hours')
    )

    # Get detailed complaint list with downtime
    complaint_details = complaints.values(
        'id', 'ticket_num',
        'equipment__name', 'machine_id__name',
        'date_time', 'closure_timestamp',
        'total_downtime_hours',
        'engineer_response_hours',
        'user_response_hours',
        'documentation_hours',
        'closure_hours'
    ).order_by('-date_time')[:100]  # Last 100 complaints

    # Get equipment list for filter
    equipment_list = Equipment.objects.all()

    context = {
        'metrics': metrics,
        'complaints': complaint_details,
        'equipment_list': equipment_list,
        'date_from': date_from,
        'date_to': date_to,
        'selected_equipment': equipment_id,
    }

    return render(request, 'user/downtime-report.html', context)


