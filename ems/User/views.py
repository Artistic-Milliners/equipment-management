from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, PasswordResetForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.db.models.query import QuerySet
from django.db.models import Q, Avg, Sum, Count
from core.models import (Contractor, CustomUser, MachineIssueReview, Employee,
                         Unit, MachineIssue, Spares, Equipment,
                         Machines, ImageModel, Department,
                         MachineIssueReview, IssueClosing, MachineSpares,
                         FaultLibrary, TemporaryIssue, MachineSection, QuickReviewComments)
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
from core.access import visible_machines
import logging
from decimal import Decimal, InvalidOperation

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
        # Only equipment types that have at least one machine this user may see
        equipment = models.Equipment.objects.filter(typeOfMachine__in=visible_machines(user)).distinct()
        if not equipment.exists():
            return render(request, 'user/error/404.html', {'e': 'No equipment found for your department'})
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
            machine = visible_machines(request.user).get(pk=machine_code)
            error_department = Department.objects.get(pk=error_department)

            if not machine_hours:
                machine_hours = machine.machine_hours

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
            # User selected a fault from the Fault Library; it must apply to this machine
            try:
                issue.selected_issue = FaultLibrary.for_machine(machine).get(pk=selected_issue_id)
            except (FaultLibrary.DoesNotExist, ValueError):
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


def can_view_issue(user, issue):
    """Same scope as the dashboard: reporter, own department's machines, engineers or view-all permission"""
    if user.has_perm('core.view_all_issues') or user.has_perm('core.can_review_complaint'):
        return True
    if user.groups.filter(name='Engineers').exists():
        return True
    if issue.user and issue.user.user_id == user.pk:
        return True
    department = getattr(getattr(user, 'employee', None), 'department_id', None)
    return department is not None and issue.machine_id is not None and issue.machine_id.Department_id == department


def can_confirm_issue(user, issue):
    """The reporter, or anyone in the department that owns the machine, can confirm or reject the engineer's fix"""
    employee = getattr(user, 'employee', None)
    if employee is None:
        return False
    if issue.user_id == employee.pk:
        return True
    return (employee.department_id is not None and issue.machine_id is not None
            and issue.machine_id.Department_id == employee.department_id)


def is_engineer_user(user):
    return user.has_perm('core.can_review_complaint') or user.groups.filter(name='Engineers').exists()


class ComplainTrackingView(LoginRequiredMixin, View):
    login_url = 'User:login'

    def get(self, request, pk):
        issue = get_object_or_404(
            MachineIssue.objects.select_related('user__user', 'equipment', 'machine_id', 'error_department'), pk=pk)
        if not can_view_issue(request.user, issue):
            return render(request, 'user/error/404.html', {'error': 'You do not have access to this complaint.'},
                          status=403)
        context = {
            'issue': issue,
            'work_sessions': issue.work_sessions.select_related('engineer').order_by('started_at'),
            'quick_review_comments': issue.quick_review_comments.select_related('commenter__user').order_by('created_at'),
            'feedback_error': request.session.pop(f'feedback_error_{issue.pk}', None),
            'can_confirm': issue.status == MachineIssue.STATUS_USER_FEEDBACK and can_confirm_issue(request.user, issue),
            'is_engineer_view': is_engineer_user(request.user),
        }
        return render(request, 'user/complain-tracking.html', context)
    
    

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

    # Tickets reach the closing form after the operator confirms the fix, or after approval of a detailed review
    CLOSABLE_STATUSES = [MachineIssue.STATUS_AWAITING_DOCUMENTATION, MachineIssue.STATUS_APPROVED]
    IN_HOUSE_DEPARTMENT_TYPES = ['MAINTENANCE', 'SERVICES']
    NAME_MAX_LENGTH = 50

    def get(self, request, pk):
        """Display the closing form"""
        issue = get_object_or_404(MachineIssue.objects.select_related('machine_id', 'equipment'), pk=pk)
        blocked = self._check_access(request, issue)
        if blocked:
            return blocked
        return self._render_form(request, issue)

    def post(self, request, pk):
        """Validate and process the closing form with an atomic transaction"""
        issue = get_object_or_404(MachineIssue.objects.select_related('machine_id', 'equipment'), pk=pk)
        blocked = self._check_access(request, issue)
        if blocked:
            return blocked

        data, errors = self._validate(request, issue)
        if errors:
            return self._render_form(request, issue, errors=errors)

        try:
            with transaction.atomic():
                self._get_or_create_review(request, issue)
                closing = self._create_closing_record(issue, data)
                image_errors = self._save_images(request, closing)
                self._save_spares(request, closing)
                self._close_issue(issue, data)
        except Exception as e:
            logger.exception(f"Failed to close issue {pk}")
            return self._render_form(request, issue, errors=[f"Could not close the complaint: {e}"])

        if image_errors:
            messages.warning(request, f"Closed successfully, but some images failed: {image_errors}")
        else:
            messages.success(request, f"Complaint {issue.ticket_num} closed successfully.")
        logger.info(f"Issue {issue.ticket_num} closed by {request.user.username}")
        return redirect("User:complain_closing_list")

    def _check_access(self, request, issue):
        """Return a redirect if this user may not close this issue now, else None"""
        if not self._can_close(request.user):
            messages.error(request, "You are not authorized to close this complaint.")
            return redirect('maintenance:complain_list')
        if issue.status not in self.CLOSABLE_STATUSES:
            messages.error(request, f"Complaint {issue.ticket_num} cannot be closed while it is "
                                    f"'{issue.get_status_display() or issue.status}'.")
            return redirect('maintenance:complain_list')
        # A ticket resolved through Quick Review and confirmed by the user has no detailed review; it is
        # documented and closed directly here (the review record is created on save). Only the approval
        # route needs an existing review.
        if issue.status == MachineIssue.STATUS_APPROVED and not getattr(issue, 'machineissue', None):
            messages.info(request, f'Complete the review form before closing {issue.ticket_num}')
            return redirect('User:review_complain', pk=issue.pk)
        return None

    def _get_or_create_review(self, request, issue):
        """IssueClosing needs a MachineIssueReview; create a minimal one for quick-review tickets"""
        review = getattr(issue, 'machineissue', None)
        if review:
            return review
        last_comment = (issue.quick_review_comments.filter(commenter__user=request.user)
                        .order_by('-created_at').values_list('comment', flat=True).first())
        review = MachineIssueReview.objects.create(
            issue=issue,
            reviewer=request.user.employee,
            description_reviewer=last_comment or 'Resolved through quick review; confirmed by the user.',
        )
        issue.machineissue = review
        return review

    def _can_close(self, user):
        """Only engineers (same rule as the engineer ticket views) may close complaints"""
        if not hasattr(user, 'employee'):
            return False
        return user.has_perm('core.can_review_complaint') or user.groups.filter(name='Engineers').exists()

    def _in_house_departments(self):
        return Department.objects.filter(dpt_type__in=self.IN_HOUSE_DEPARTMENT_TYPES).order_by('name')

    def _render_form(self, request, issue, errors=None):
        review = getattr(issue, 'machineissue', None)
        machine_spare_ids = set(MachineSpares.objects.filter(machine=issue.machine_id).values_list('spare_id', flat=True))
        # Spares linked to this machine first, then all others
        spares = sorted(Spares.objects.only('id', 'name'), key=lambda s: (s.pk not in machine_spare_ids, s.name.lower()))

        worked_hours = issue.work_sessions.aggregate(total=Sum('duration_hours'))['total']
        posted = request.POST if errors else None

        context = {
            'issue': issue,
            'review': review,
            'contractors': Contractor.objects.order_by('contractor'),
            'departments': self._in_house_departments(),
            'spares': [{'id': s.pk, 'name': s.name, 'linked': s.pk in machine_spare_ids} for s in spares],
            'selected_spares': [int(x) for x in posted.getlist('states[]') if x.isdigit()] if posted else [],
            'errors': errors or [],
            'posted': posted,
            'default_duration': round(worked_hours, 1) if worked_hours else '',
            'name_max_length': self.NAME_MAX_LENGTH,
        }
        return render(request, "user/complain_closing.html", context)

    def _validate(self, request, issue):
        """Return (cleaned data, list of error messages)"""
        post = request.POST
        errors = []
        data = {}

        try:
            data['machine_hours'] = int(post.get('machine-hours', ''))
            if data['machine_hours'] < 0:
                errors.append('Current machine hours cannot be negative.')
            elif issue.machine_hours is not None and data['machine_hours'] < issue.machine_hours:
                errors.append(f'Current machine hours cannot be lower than the hours at failure ({issue.machine_hours}).')
        except ValueError:
            errors.append('Enter the current machine hours as a whole number.')

        try:
            data['duration'] = Decimal(post.get('duration', '').strip())
            if data['duration'] < 0:
                errors.append('Repair duration cannot be negative.')
        except (InvalidOperation, ValueError):
            errors.append('Enter the repair duration in hours (e.g. 1.5).')

        data['equipment_status'] = post.get('equipment-status')
        if data['equipment_status'] not in dict(IssueClosing.EQUIPMENT_STATUS_CHOICES):
            errors.append('Select the equipment status.')

        data['resolution_type'] = post.get('resolved-by-type')
        data['contractor'] = data['department'] = None
        if data['resolution_type'] == IssueClosing.RESOLUTION_OUTSOURCED:
            data['contractor'] = Contractor.objects.filter(pk=post.get('contractor') or None).first()
            if not data['contractor']:
                errors.append('Select the service provider for an outsourced repair.')
        elif data['resolution_type'] == IssueClosing.RESOLUTION_IN_HOUSE:
            data['department'] = self._in_house_departments().filter(pk=post.get('department') or None).first()
            if not data['department']:
                errors.append('Select the department that did the in-house repair.')
        else:
            errors.append('Select the resolution type.')

        for field, label in (('technician', 'Technician name'), ('supervisor', 'Supervisor name')):
            data[field] = post.get(field, '').strip()
            if len(data[field]) > self.NAME_MAX_LENGTH:
                errors.append(f'{label} must be at most {self.NAME_MAX_LENGTH} characters.')

        data['solution'] = post.get('solution-description', '').strip()
        if not data['solution']:
            errors.append('Describe the solution implemented.')
        data['remarks'] = post.get('additional-remarks', '').strip()

        return data, errors

    def _create_closing_record(self, issue, data):
        """Create the IssueClosing record"""
        return IssueClosing.objects.create(
            issueReview=issue.machineissue,
            resolution_type=data['resolution_type'],
            contractor=data['contractor'],
            resolved_department=data['department'],
            machineHours=data['machine_hours'],
            supervisor=data['supervisor'],
            technician=data['technician'],
            solutionDescription=data['solution'],
            duration=data['duration'],
            remarks=data['remarks'],
            equipment_status=data['equipment_status'],
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

    def _close_issue(self, issue, data):
        """Update issue status, timestamps, operational status and the machine's hour meter"""
        issue.closure_timestamp = timezone.now()
        issue.operational_status = 'OPERATIONAL' if data['equipment_status'] == 'on' else 'NON_OPERATIONAL'

        machine = issue.machine_id
        if machine and (machine.machine_hours is None or data['machine_hours'] > machine.machine_hours):
            machine.machine_hours = data['machine_hours']
            machine.save(update_fields=['machine_hours'])

        # Quick-review tickets are documented by this form itself
        if not issue.documentation_timestamp:
            issue.documentation_timestamp = issue.closure_timestamp
            if issue.user_confirmation_timestamp:
                diff = issue.documentation_timestamp - issue.user_confirmation_timestamp
                issue.documentation_hours = diff.total_seconds() / 3600

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
            'contractor',
            'resolved_department'
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
            machines = visible_machines(request.user).filter(type_of_machine=equipment)
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
            machine = visible_machines(request.user).get(pk=pk)
            machine_hours = machineHoursSerializer(machine)
            # print(machine_hours.data)
            return Response(machine_hours.data)
        
        except models.Machines.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class IssueListAPIView(APIView):
    """API endpoint to fetch Fault Library entries for an equipment, optionally narrowed to a machine's manufacturer"""
    permission_classes = []  # Allow unauthenticated access

    def get(self, request, equipment_pk):
        try:
            machine_id = request.GET.get('machine')
            if machine_id:
                machine = visible_machines(request.user).filter(pk=machine_id, type_of_machine_id=equipment_pk).first()
                faults = FaultLibrary.for_machine(machine) if machine else FaultLibrary.objects.none()
            else:
                faults = FaultLibrary.objects.filter(equipment_id=equipment_pk)

            issues = [{
                'id': fault.pk,
                'fault_description': fault.fault_description,
                'fault_category': fault.get_fault_category_display(),
                'machine_section': fault.machine_section or '',
                'manufacturer': fault.manufacturer.name if fault.manufacturer else '',
                'label': fault.display_label,
            } for fault in faults.select_related('manufacturer')]

            return JsonResponse({
                'success': True,
                'issues': issues
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
            # Get all sections for this machine (only if the user may see the machine)
            sections = MachineSection.objects.filter(
                machine_id=machine_pk, machine__in=visible_machines(request.user)
            ).values(
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


@login_required(login_url='User:login')
def change_password(request):
    """Let the logged-in user change their own password."""
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            # Keep the user logged in; otherwise changing the password ends this session
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been changed successfully.')
            return redirect('User:change_password')
    else:
        form = PasswordChangeForm(user=request.user)

    for field in form.fields.values():
        field.widget.attrs['class'] = 'form-control'
    return render(request, 'user/change_password.html', {'form': form})



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

    # Scope the statistics to the issues this user is allowed to see:
    # view_all_issues (Engineers, admin, superusers) -> every issue
    # everyone else -> issues on machines of their department, plus any they raised themselves
    can_view_all = request.user.has_perm('core.view_all_issues')
    if can_view_all:
        issues = MachineIssue.objects.all()
    else:
        employee = Employee.objects.filter(user=request.user).select_related('department').first()
        scope = Q(user__user=request.user)
        if employee and employee.department:
            scope |= Q(machine_id__Department=employee.department)
        issues = MachineIssue.objects.filter(scope)

    # Calculate statistics
    total_issues = issues.count()
    pending_issues = issues.filter(status='PENDING').count()

    # Get issues resolved today (status RESOLVED, CLOSED, or APPROVED)
    # Note: Using date_time for now until timestamp tracking fields are added
    resolved_today = issues.filter(
        status__in=['RESOLVED', 'CLOSED', 'APPROVED'],
        date_time__date=today
    ).count()

    # Critical issues: machines with operational status NON_OPERATIONAL and status not yet closed
    critical_issues = issues.filter(
        operational_status='NON_OPERATIONAL',
        status__in=['PENDING', 'UNDER_OBSERVATION', 'REVIEWED']
    ).count()

    context = {
        'total_issues': total_issues,
        'pending_issues': pending_issues,
        'resolved_today': resolved_today,
        'critical_issues': critical_issues,
        'can_view_all_issues': can_view_all,
    }

    return render(request, "user/home.html", context)


@login_required(login_url='User:login')
def machine_detail(request,pk):

    machine_detail = get_object_or_404(visible_machines(request.user), pk=pk)
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
        machine.sync_manufacturer()
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
        machine.sync_manufacturer()
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


@login_required(login_url='User:login')
def user_close_complaint(request, pk):
    """
    The reporter (or their department) answers the engineer's fix while the status is 'User Feedback':
    - RESOLVED   "Work Completed"          -> AWAITING_DOCUMENTATION: shown as Closed to users; the engineer
                                              still completes the closing documentation
    - NOT_FIXED  "Problem Still Persists"  -> PENDING: back to the engineer for rework (feedback required)
    """
    if request.method != 'POST':
        return redirect('User:complain_track', pk=pk)

    issue = get_object_or_404(MachineIssue.objects.select_related('user__user', 'machine_id'), pk=pk)
    employee = getattr(request.user, 'employee', None)

    if not can_confirm_issue(request.user, issue):
        return render(request, 'user/error/404.html', {
            'error': "Only the person who raised this complaint or their department can confirm or reopen it."
        }, status=403)

    if issue.status != MachineIssue.STATUS_USER_FEEDBACK:
        # Already answered (e.g. a double submit) - just show the current state
        return redirect('User:complain_track', pk=pk)

    action = request.POST.get('status', '').upper()
    feedback = request.POST.get('user-feedback', '').strip()

    if action not in ('RESOLVED', 'NOT_FIXED'):
        request.session[f'feedback_error_{pk}'] = 'Please choose whether the issue is fixed.'
        return redirect('User:complain_track', pk=pk)
    if action == 'NOT_FIXED' and not feedback:
        request.session[f'feedback_error_{pk}'] = 'Please describe what is still wrong so the engineer can follow up.'
        return redirect('User:complain_track', pk=pk)

    now = timezone.now()
    with transaction.atomic():
        if action == 'RESOLVED':
            if feedback:
                QuickReviewComments.objects.create(issue=issue, commenter=employee, comment=feedback)
            issue.status = MachineIssue.STATUS_AWAITING_DOCUMENTATION
            issue.operational_status = 'OPERATIONAL'
            issue.user_confirmation_timestamp = now
            if issue.quick_review_timestamp:
                issue.user_response_hours = (now - issue.quick_review_timestamp).total_seconds() / 3600
        else:
            QuickReviewComments.objects.create(issue=issue, commenter=employee,
                                               comment=f'Reopened - still not fixed: {feedback}')
            issue.status = MachineIssue.STATUS_PENDING
            if request.POST.get('operational-status') in ('OPERATIONAL', 'NON_OPERATIONAL'):
                issue.operational_status = request.POST['operational-status']
            # Response times are measured again for the new attempt
            issue.quick_review_timestamp = None
            issue.engineer_response_hours = None
        issue.save()

    logger.info(f"Ticket {issue.ticket_num}: user {request.user.username} answered feedback with {action}")
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


