from django.shortcuts import render, get_object_or_404, redirect
from core.models import (MachineIssue, Equipment, Machines, Spares, MachineSpares, ImageModel,
                        CustomUser, MachineIssueApproval, MachineIssueReview, Department, Employee,
                        TemporaryIssue, IssueList, QuickReviewComments, WorkSession)
from django.contrib.auth.decorators import permission_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.db.models import Prefetch
from django.contrib.auth.decorators import permission_required, login_required
from django.core.files.storage import default_storage
from User.views import home
from django.utils import timezone
import logging
from django.contrib import messages
from core.access import visible_machines

@login_required
def get_machines(request):

    equipment_id = request.GET['equipment_id']
    if equipment_id:
        equipment = get_object_or_404(Equipment, pk=equipment_id)
        machines = visible_machines(request.user).filter(type_of_machine=equipment).prefetch_related(
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
    # Try to get employee record
    try:
        emp = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        # If no employee record exists, create a basic context
        
        messages.warning(request, "Your user account is not linked to an employee record. Please contact the administrator.")
        return render(request, "maintenance/complain-view.html", {
            'issue_list': [], 
            'emp': None,
            'is_approver': False,
            'is_engineer': False
        })
    
    # Check user roles
    is_approver = request.user.has_perm('core.can_approve_complaint') or request.user.groups.filter(name='Approvers').exists()
    is_engineer = request.user.has_perm('core.can_review_complaint') or request.user.groups.filter(name='Engineers').exists()

    # Filter tickets based on user role
    # Check for users with BOTH roles first
    if is_approver and is_engineer:
        # Users with both roles see ALL relevant tickets
        # - PENDING (need engineer review)
        # - User Feedback (awaiting user acknowledgment after quick review)
        # - REVIEWED (need approver decision)
        # - APPROVED (engineers can work on)
        # - REJECTED (for reference)
        # - AWAITING_DOCUMENTATION, RESOLVED, UNDER_OBSERVATION (engineers working on)
        issue_list = MachineIssue.objects.filter(
            status__in=[
                MachineIssue.STATUS_PENDING, MachineIssue.STATUS_IN_PROGRESS, MachineIssue.STATUS_USER_FEEDBACK,
                MachineIssue.STATUS_REVIEWED, MachineIssue.STATUS_APPROVED, MachineIssue.STATUS_REJECTED,
                MachineIssue.STATUS_AWAITING_DOCUMENTATION, MachineIssue.STATUS_RESOLVED, MachineIssue.STATUS_UNDER_OBSERVATION,
            ]
        ).select_related('user', 'equipment', 'machine_id', 'error_department', 'temporary_issue', 'selected_issue').order_by('-date_time')
        print(f"[ENGINEER + APPROVER] User: {request.user.username}, Found {issue_list.count()} tickets")

    elif is_approver:
        issue_list = MachineIssue.objects.filter(
            status__in=[MachineIssue.STATUS_REVIEWED, MachineIssue.STATUS_APPROVED, MachineIssue.STATUS_REJECTED]
        ).select_related('user', 'equipment', 'machine_id', 'error_department', 'temporary_issue', 'selected_issue').order_by('-date_time')
        print(f"[APPROVER] User: {request.user.username}, Found {issue_list.count()} tickets")

    elif is_engineer:
        issue_list = MachineIssue.objects.filter(
            status__in=[
                MachineIssue.STATUS_PENDING, MachineIssue.STATUS_IN_PROGRESS, MachineIssue.STATUS_USER_FEEDBACK,
                MachineIssue.STATUS_APPROVED, MachineIssue.STATUS_AWAITING_DOCUMENTATION,
                MachineIssue.STATUS_RESOLVED, MachineIssue.STATUS_UNDER_OBSERVATION,
            ]
        ).select_related('user', 'equipment', 'machine_id', 'error_department', 'temporary_issue', 'selected_issue').order_by('-date_time')

    else:
        # Regular users see only their own tickets (all statuses)
        issue_list = MachineIssue.objects.filter(
            user=emp
        ).select_related('user', 'equipment', 'machine_id', 'error_department', 'temporary_issue', 'selected_issue').order_by('-date_time')

    
    # Debug: Print details about what we're showing
    # Get count of pending temporary issues for engineers/approvers
    pending_temp_issues_count = 0
    if is_engineer or is_approver:
        pending_temp_issues_count = TemporaryIssue.objects.filter(reviewed=False).count()

    print(f"\n{'='*60}")
    print(f"COMPLAIN VIEW DEBUG")
    print(f"{'='*60}")
    print(f"User: {request.user.username}")
    print(f"Employee: {emp.name if emp else 'None'}")
    print(f"Department: {emp.department.name if emp and emp.department else 'None'}")
    print(f"Is Approver: {is_approver}")
    print(f"Is Engineer: {is_engineer}")
    print(f"Total issues in list: {issue_list.count()}")
    print(f"Pending Temporary Issues: {pending_temp_issues_count}")
    if issue_list.count() > 0:
        print(f"First 3 tickets:")
        for issue in issue_list[:3]:
            print(f"  - Ticket #{issue.ticket_num}: {issue.status} - {issue.description_user[:50]}")
    print(f"{'='*60}\n")

    return render(request, "maintenance/complain-view.html", {
        'issue_list': issue_list,
        'emp': emp,
        'is_approver': is_approver,
        'is_engineer': is_engineer,
        'pending_temp_issues_count': pending_temp_issues_count
    })


def closed_complaints_archive(request):
    """
    Archive view for closed complaints - Only accessible to Engineers and Approvers
    Shows complete documentation and review history
    """
    from django.core.exceptions import PermissionDenied
    from datetime import timedelta
    from django.db.models import Avg, Count
    
    # Check permissions - only Engineers and Approvers can access
    is_approver = request.user.has_perm('core.can_approve_complaint') or request.user.groups.filter(name='Approvers').exists()
    is_engineer = request.user.has_perm('core.can_review_complaint') or request.user.groups.filter(name='Engineers').exists()
    
    if not (is_approver or is_engineer):
        raise PermissionDenied("Access denied. Only Engineers and Management can view closed complaints archive.")
    
    # Get all closed complaints with all related data
    closed_issues = MachineIssue.objects.filter(
        status=MachineIssue.STATUS_CLOSED
    ).select_related(
        'user',
        'equipment',
        'machine_id',
        'error_department',
        'machineissue',
        'machineissue__reviewer',
        'machineissue__assignPerson',
        'machineissue__assignDepartment',
        'issue_remarks',
        'issue_remarks__user_id',
        'machineissue__issueclosing',
        'machineissue__issueclosing__contractor'
    ).prefetch_related(
        'image',
        'machineissue__reviewrImages',
        'machineissue__malfunction_part',
        'machineissue__issueclosing__image'
    ).order_by('-date_time')
    
    # Calculate statistics
    total_closed = closed_issues.count()
    
    # Closed this month

    today = timezone.now()
    first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    closed_this_month = closed_issues.filter(date_time__gte=first_day_of_month).count()
    
    # Average resolution time
    avg_days = 0
    if total_closed > 0:
        total_duration = 0
        count_with_duration = 0
        for issue in closed_issues:
            try:
                if issue.machineissue and issue.machineissue.issueclosing:
                    closing_date = issue.machineissue.issueclosing.date_ended
                    duration = (closing_date - issue.date_time).days
                    total_duration += duration
                    count_with_duration += 1
            except:
                pass
        avg_days = total_duration / count_with_duration if count_with_duration > 0 else 0
    
    # Count unique contractors used
    total_contractors_used = closed_issues.filter(
        machineissue__issueclosing__contractor__isnull=False
    ).values('machineissue__issueclosing__contractor').distinct().count()
    
    # Get all equipment for filter dropdown
    all_equipment = Equipment.objects.all()

    # Get count of pending temporary issues
    pending_temp_issues_count = TemporaryIssue.objects.filter(reviewed=False).count()

    context = {
        'closed_issues': closed_issues,
        'total_closed': total_closed,
        'closed_this_month': closed_this_month,
        'avg_resolution_time': avg_days,
        'total_contractors_used': total_contractors_used,
        'all_equipment': all_equipment,
        'is_approver': is_approver,
        'is_engineer': is_engineer,
        'pending_temp_issues_count': pending_temp_issues_count,
    }
    
    print(f"\n{'='*60}")
    print(f"CLOSED COMPLAINTS ARCHIVE")
    print(f"{'='*60}")
    print(f"User: {request.user.username}")
    print(f"Is Approver: {is_approver}")
    print(f"Is Engineer: {is_engineer}")
    print(f"Total Closed: {total_closed}")
    print(f"Closed This Month: {closed_this_month}")
    print(f"{'='*60}\n")
    
    return render(request, "maintenance/closed-complaints.html", context)


def complain_detail(request, pk):
    issue = MachineIssue.objects.get(pk=pk)
    
    # Check if user has permission to approve
    can_approve = request.user.has_perm('core.can_approve_complaint') or request.user.groups.filter(name='Approvers').exists()
    
    # If not an approver, redirect engineers to closing page if approved/rejected
    if not can_approve:
        if issue.status == MachineIssue.STATUS_APPROVED:
            return redirect('User:complain_closing', pk=issue.pk)
        elif issue.status == MachineIssue.STATUS_REJECTED:
            return render(request, "maintenance/rejected-complain-detail.html", {'issue':issue})
        else:
            return render(request, "maintenance/awaiting-approval.html", {'issue':issue})

    # Approvers logic
    if issue.status == MachineIssue.STATUS_PENDING:
        return render(request, "maintenance/review-pending.html", {'issue':issue})
    elif issue.status == MachineIssue.STATUS_REJECTED:
        return render(request, "maintenance/rejected-complain-detail.html", {'issue':issue})
    elif issue.status == MachineIssue.STATUS_APPROVED:
        return render(request,"maintenance/accepted-complain-detail.html",{'issue':issue})
    elif issue.status == MachineIssue.STATUS_REVIEWED:
        return render(request, "maintenance/complain-detail.html", {'issue':issue})
    else:
        # Fallback
        return render(request, "maintenance/complain-detail.html", {'issue':issue})


def quick_review(request, pk):
    """Quick review page for engineers to decide if complaint is resolved or needs observation"""

    logger = logging.getLogger(__name__)
    if request.method == 'GET':
        issue = MachineIssue.objects.get(pk=pk)
        # Calculate elapsed time since complaint was raised
        elapsed = timezone.now() - issue.date_time
        elapsed_hours = int(elapsed.total_seconds() // 3600)
        elapsed_minutes = int((elapsed.total_seconds() % 3600) // 60)

        # Check for active work session
        active_session = issue.work_sessions.filter(outcome=WorkSession.OUTCOME_IN_PROGRESS).first()

        return render(request, "maintenance/quick-review.html", {
            'issue': issue,
            'elapsed_hours': elapsed_hours,
            'elapsed_minutes': elapsed_minutes,
            'active_session': active_session,
        })

    elif request.method == 'POST':
        issue = MachineIssue.objects.get(pk=pk)
        decision = request.POST.get('decision')
        print(f"quick review decision for the issue {issue.ticket_num} is {issue.status}")
        comments = request.POST.get('engineer-comments', '')

        logger.info(f"\n{'='*60}")
        logger.info(f"QUICK REVIEW SUBMISSION")
        logger.info(f"{'='*60}")
        logger.info(f"Issue ID: {issue.pk}")
        logger.info(f"Ticket #: {issue.ticket_num}")
        logger.info(f"Decision: {decision}")
        logger.info(f"Comments: {comments}")

        # Close any active work session for this issue
        active_session = issue.work_sessions.filter(outcome=WorkSession.OUTCOME_IN_PROGRESS).first()

        if decision == 'User_Feedback':
            # Mark issue as resolved - NO review record yet
            # User will acknowledge, then engineer documents before closing
            issue.status = MachineIssue.STATUS_USER_FEEDBACK

            # Record quick review timestamp
            issue.quick_review_timestamp = timezone.now()

            # Calculate engineer response time
            time_diff = issue.quick_review_timestamp - issue.date_time
            issue.engineer_response_hours = time_diff.total_seconds() / 3600

            issue.save()

            # Close active work session
            if active_session:
                active_session.complete(WorkSession.OUTCOME_RESOLVED, comments)

            # Save engineer's comment as QuickReviewComments record
            if comments:
                engineer = Employee.objects.get(user=request.user)
                QuickReviewComments.objects.create(
                    issue=issue,
                    commenter=engineer,
                    comment=comments,
                )
            logger.info(f"✓ Status updated to RESOLVED")
            logger.info(f"  - Quick review timestamp: {issue.quick_review_timestamp}")
            logger.info(f"  - Engineer response time: {issue.engineer_response_hours:.2f} hours")

            return redirect('maintenance:complain_list')

        elif decision == 'UNDER_OBSERVATION':
            # Close active work session
            if active_session:
                active_session.complete(WorkSession.OUTCOME_UNDER_OBSERVATION, comments)

            logger.info(f"✓ Issue requires detailed review - Redirecting to review form")
            return redirect('User:review_complain', pk=issue.pk)

        elif decision == 'ESCALATE':
            # Close active work session
            if active_session:
                active_session.complete(WorkSession.OUTCOME_ESCALATED, comments)

            # Save engineer's comment as QuickReviewComments record
            if comments:
                engineer = Employee.objects.get(user=request.user)
                QuickReviewComments.objects.create(
                    issue=issue,
                    commenter=engineer,
                    comment=comments,
                )
            logger.info(f"✓ Issue escalated")

            return redirect('maintenance:complain_list')

        logger.info(f"{'='*60}\n")

        return redirect('maintenance:complain_list')


@login_required
def start_working(request, pk):
    """Engineer clicks Start Working - creates a WorkSession and updates issue status to IN_PROGRESS"""
    if request.method == 'POST':
        issue = get_object_or_404(MachineIssue, pk=pk)
        engineer = Employee.objects.get(user=request.user)

        # Check if there's already an active session on this issue
        active_session = issue.work_sessions.filter(outcome=WorkSession.OUTCOME_IN_PROGRESS).first()
        if active_session:
            return JsonResponse({
                'status': 'already_started',
                'engineer': active_session.engineer.name,
                'started_at': active_session.started_at.isoformat(),
            })

        # Create new work session
        session = WorkSession.objects.create(
            issue=issue,
            engineer=engineer,
        )

        # Update issue status to IN_PROGRESS
        issue.status = MachineIssue.STATUS_IN_PROGRESS
        issue.save()

        return JsonResponse({
            'status': 'started',
            'session_id': session.pk,
            'started_at': session.started_at.isoformat(),
            'engineer': engineer.name,
        })

    return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)



def complain_delete(request, pk):
    issue = MachineIssue.objects.get(pk=pk)
    issue.delete()
     
    return redirect("maintenance:complain_list")
   

def complain_approve(request, pk):
    # Check if user has permission to approve
    can_approve = request.user.has_perm('core.can_approve_complaint') or request.user.groups.filter(name='Approvers').exists()

    if not can_approve:
        raise PermissionDenied("You don't have permission to approve complaints. Only Approvers/Management can approve.")

    logger = logging.getLogger(__name__)

    if request.method == 'POST':
        logger.info(f"\n{'='*60}")
        logger.info(f"APPROVAL PROCESS STARTED")
        logger.info(f"{'='*60}")

        user = CustomUser.objects.get(pk=request.user.id)
        issue = MachineIssue.objects.get(pk=pk)
        status = request.POST.get("status")
        comment = request.POST.get('man-remarks', '')

        logger.info(f"User: {user.username}")
        logger.info(f"Issue ID: {issue.pk}")
        logger.info(f"Ticket #: {issue.ticket_num}")
        logger.info(f"Current Status: {issue.status}")
        logger.info(f"New Status: {status}")
        logger.info(f"Comment: {comment}")

        # Update issue status
        if status == 'Approved':
            issue.status = MachineIssue.STATUS_APPROVED
        else:
            issue.status = MachineIssue.STATUS_REJECTED

        issue.save()
        logger.info(f"Issue status updated to: {issue.status}")
        
        # Create or update approval record
        try:
            approval, created = MachineIssueApproval.objects.get_or_create(
                complain_id=issue,
                defaults={
                    'user_id': user,
                    'comment': comment,
                }
            )
            
            if not created:
                # Update existing approval
                approval.user_id = user
                approval.comment = comment
                approval.save()
                print(f"✓ Updated existing approval record")
            else:
                print(f"✓ Created new approval record")
            
            print(f"Approval ID: {approval.pk}")
            print(f"Approval Date: {approval.date_time}")
            print(f"Approver: {approval.user_id.username}")
            print(f"Comment saved: {approval.comment}")
            
            # Verify it's accessible
            test_approval = MachineIssueApproval.objects.get(complain_id=issue)
            print(f"✓ Verification: Approval can be retrieved from database")
            
            # Test the reverse relation
            try:
                test_reverse = issue.issue_remarks
                print(f"✓ Verification: Reverse relation works - issue.issue_remarks exists")
            except Exception as e:
                print(f"✗ Warning: Reverse relation issue - {e}")
        
        except Exception as e:
            print(f"✗ ERROR saving approval: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print(f"{'='*60}\n")

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


@login_required
def temporary_issue_review_list(request):
    """
    List all temporary issues that need engineer review
    Only accessible to Engineers and Approvers
    """
    # Check permissions
    is_approver = request.user.has_perm('core.can_approve_complaint') or request.user.groups.filter(name='Approvers').exists()
    is_engineer = request.user.has_perm('core.can_review_complaint') or request.user.groups.filter(name='Engineers').exists()

    if not (is_approver or is_engineer):
        raise PermissionDenied("Access denied. Only Engineers and Management can review temporary issues.")

    # Get all temporary issues with related data
    temp_issues = TemporaryIssue.objects.select_related(
        'user', 'equipment', 'machine', 'reviewed_by', 'promoted_issue'
    ).order_by('reviewed', '-created_at')

    # Calculate statistics
    total_issues = temp_issues.count()
    pending_review = temp_issues.filter(reviewed=False).count()
    reviewed = temp_issues.filter(reviewed=True, promoted_to_issuelist=False).count()
    promoted = temp_issues.filter(promoted_to_issuelist=True).count()

    context = {
        'temp_issues': temp_issues,
        'total_issues': total_issues,
        'pending_review': pending_review,
        'reviewed': reviewed,
        'promoted': promoted,
        'is_approver': is_approver,
        'is_engineer': is_engineer,
    }

    print(f"\n{'='*60}")
    print(f"TEMPORARY ISSUE REVIEW LIST")
    print(f"{'='*60}")
    print(f"User: {request.user.username}")
    print(f"Is Engineer: {is_engineer}")
    print(f"Is Approver: {is_approver}")
    print(f"Total Issues: {total_issues}")
    print(f"Pending Review: {pending_review}")
    print(f"Promoted: {promoted}")
    print(f"{'='*60}\n")

    return render(request, "maintenance/temporary-issue-list.html", context)


@login_required
def temporary_issue_review_detail(request, pk):
    """
    Review and promote individual temporary issues
    Only accessible to Engineers and Approvers
    """
    # Check permissions
    is_approver = request.user.has_perm('core.can_approve_complaint') or request.user.groups.filter(name='Approvers').exists()
    is_engineer = request.user.has_perm('core.can_review_complaint') or request.user.groups.filter(name='Engineers').exists()

    if not (is_approver or is_engineer):
        raise PermissionDenied("Access denied. Only Engineers and Management can review temporary issues.")

    temp_issue = get_object_or_404(
        TemporaryIssue.objects.select_related('user', 'equipment', 'machine', 'reviewed_by', 'promoted_issue'),
        pk=pk
    )

    # Get all issue lists for this equipment
    issue_lists = IssueList.objects.filter(equipment=temp_issue.equipment)

    if request.method == 'POST':
        action = request.POST.get('action')

        # Get current engineer
        try:
            engineer = Employee.objects.get(user=request.user)
        except Employee.DoesNotExist:
            return render(request, 'user/error/404.html', {'error': 'You must be an employee to review issues'})

        print(f"\n{'='*60}")
        print(f"TEMPORARY ISSUE REVIEW SUBMISSION")
        print(f"{'='*60}")
        print(f"Temp Issue ID: {temp_issue.pk}")
        print(f"Action: {action}")
        print(f"Reviewer: {engineer.name}")

        if action == 'mark_reviewed':
            # Just mark as reviewed without promoting
            temp_issue.reviewed = True
            temp_issue.reviewed_by = engineer
            temp_issue.engineer_notes = request.POST.get('engineer_notes', '')
            temp_issue.save()
            print(f"✓ Marked as reviewed (not promoted)")
            print(f"{'='*60}\n")
            return redirect('maintenance:temp_issue_list')

        elif action == 'promote_new':
            # Create new IssueList entry
            c_desc = request.POST.get('c_desc')
            error_code = request.POST.get('error_code', '')
            machine_status = request.POST.get('machine_status', 'operational')

            if not c_desc:
                return render(request, 'user/error/404.html', {'error': 'Description is required'})

            new_issue = IssueList.objects.create(
                equipment=temp_issue.equipment,
                c_desc=c_desc,
                error_code=error_code,
                machine_status=machine_status,
                created_by=request.user  # Track who added this to master list
            )

            temp_issue.reviewed = True
            temp_issue.reviewed_by = engineer
            temp_issue.promoted_to_issuelist = True
            temp_issue.promoted_issue = new_issue
            temp_issue.engineer_notes = request.POST.get('engineer_notes', '')
            temp_issue.save()

            print(f"✓ Created new IssueList entry (ID: {new_issue.pk})")
            print(f"  Description: {c_desc}")
            print(f"  Error Code: {error_code}")
            print(f"{'='*60}\n")
            return redirect('maintenance:temp_issue_list')

        elif action == 'link_existing':
            # Link to existing IssueList
            existing_issue_id = request.POST.get('existing_issue_id')

            if not existing_issue_id:
                return render(request, 'user/error/404.html', {'error': 'Please select an existing issue'})

            existing_issue = IssueList.objects.get(pk=existing_issue_id)

            temp_issue.reviewed = True
            temp_issue.reviewed_by = engineer
            temp_issue.promoted_to_issuelist = True
            temp_issue.promoted_issue = existing_issue
            temp_issue.engineer_notes = request.POST.get('engineer_notes', '')
            temp_issue.save()

            print(f"✓ Linked to existing IssueList (ID: {existing_issue.pk})")
            print(f"  Description: {existing_issue.c_desc}")
            print(f"{'='*60}\n")
            return redirect('maintenance:temp_issue_list')

        else:
            return render(request, 'user/error/404.html', {'error': 'Invalid action'})

    # GET request - show review form
    context = {
        'temp_issue': temp_issue,
        'issue_lists': issue_lists,
        'is_approver': is_approver,
        'is_engineer': is_engineer,
    }

    return render(request, 'maintenance/temporary-issue-review.html', context)



