from django.contrib.auth import authenticate
from django.conf import settings
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserLoginSerializer
from core.models import CustomUser
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import AuthenticationFailed
from core.models import MachineIssue
from django.http import JsonResponse
import traceback
from .utils import jwt_required
from .utils import generateToken
import jwt

# Create your views here.
class UserLoginAPIView(APIView):
    
    serializer_class = UserLoginSerializer
    permission_classes = (AllowAny,)

    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data.get('username')
        password = serializer.validated_data.get('password')

        user = authenticate(username=username, password=password)

        if not user:
            raise AuthenticationFailed('User does not exist')
        
        else:
            user_access_token, user_refresh_token = generateToken(user)
            response = Response()
            response.data = {
                'access_token':user_access_token,
                'refresh_token':user_refresh_token
            }
            return response
        
        return Response({
            'message': 'Something went Wrong'
        })
        

class UserTokenRefreshAPIView(APIView):
    permission_classes = (AllowAny,)
    
    def post(self, request):
        
        refresh_token = request.data.get('refresh_token')
        print(refresh_token)
        if not refresh_token:
            return Response({'Message': 'Refresh Token is required for Token Generations'})
        try:
            payload = jwt.decode(refresh_token, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)
            user = CustomUser.objects.get(id=payload['user_id'])
            print(user.username)
            access_token = generateToken(user)[0]
            return Response({'access_token':access_token})
        
        except jwt.ExpiredSignatureError:
            return Response({'Message': 'Expired Refresh Token'})
        
        except jwt.InvalidTokenError as e:
            return Response({'Error': str(e)})
        


class HomeAPIView(APIView):
    permission_classes = (AllowAny,)
    
    @jwt_required
    def post(self, request):
        pass


class TicketDetailAPIView(APIView):
    """API endpoint to fetch ticket details for the 3-column view"""
    permission_classes = (AllowAny,)  # Allow any authenticated user to access
    
    def get(self, request, pk):

        
        try:
            # Only select_related for ForeignKey fields, not OneToOne


            issue = MachineIssue.objects.select_related(
                'user',
                'equipment',
                'machine_id',
                'error_department',

            ).prefetch_related('image').get(pk=pk)
            
            # Build response data with safe attribute access
            # Convert UTC datetime to local timezone (Asia/Karachi)
            local_datetime = timezone.localtime(issue.date_time) if issue.date_time else None

            data = {
                'id': issue.pk,
                'ticket_num': issue.ticket_num or 'N/A',
                'status': issue.status or 'PENDING',
                'equipment': issue.equipment.name if issue.equipment else 'N/A',
                'machine': issue.machine_id.name if issue.machine_id else 'N/A',
                'description': issue.description_user or 'No description provided',
                'user': issue.user.name if issue.user else 'N/A',
                'department': issue.error_department.name if issue.error_department else 'N/A',
                'date_display': local_datetime.strftime('%b %d, %Y') if local_datetime else 'N/A',
                'time_display': local_datetime.strftime('%I:%M %p') if local_datetime else 'N/A',
                'operational_status': issue.operational_status or 'OPERATIONAL',
                'machine_hours': issue.machine_hours or 0,
                'images':[image.image.url for image in issue.image.all()] if issue.image.exists() else []
            }

            if issue.selected_issue:
                selected = issue.selected_issue
                data['issue_info'] = {
                    'type': "EXISTING",
                    'error_code': selected.error_code or '',
                    'programmer_string': selected.programmer_string or '',
                    'machine_string': selected.machine_string or '',
                    'description': selected.c_desc or '',
                    'display': f"[{selected.error_code}]-{selected.c_desc}" if selected.error_code else selected.c_desc or 'N/A'                    
                }
            elif issue.temporary_issue:
                temporary = issue.temporary_issue
                data['issue_info'] = {
                    'type': "NEW",
                    'description': temporary.user_description or '',
                    'reviewed': temporary.reviewed,
                    'display': f"🔧 New Issue: {temporary.user_description[:100]}" if temporary.user_description else 'Custom issue reported'                    
                }
            else:
                # No issue information (shouldn't happen in normal flow)
                data['issue_info'] = {
                    'type': 'UNKNOWN',
                    'display': 'No issue information available'
                }


            
            # Add review data if exists (use try/except for OneToOne)
            try:
                review = issue.machineissue
                if review:
                    data['review'] = {
                        'reviewer': review.reviewer.name if hasattr(review, 'reviewer') and review.reviewer else 'N/A',
                        'description': review.description_reviewer or '',
                        'priority': review.priority or '',
                        'type': review.get_type_display() if hasattr(review, 'type') and review.type else '',
                        'problem_nature': review.get_problemNature_display() if hasattr(review, 'problemNature') and review.problemNature else '',
                        'assigned_person': review.assignPerson.name if hasattr(review, 'assignPerson') and review.assignPerson else '',
                        'assigned_department': review.assignDepartment.name if hasattr(review, 'assignDepartment') and review.assignDepartment else '',
                    }
            except Exception as e:
                print(f"No review data: {e}")
            
            # Add approval data if exists
            try:
                approval = issue.issue_remarks
                if approval:
                    data['approval'] = {
                        'approver': approval.user_id.username if hasattr(approval, 'user_id') and approval.user_id else 'N/A',
                        'comment': approval.comment or '',
                        'status': issue.status,
                        'date': approval.date_time.strftime('%b %d, %Y %I:%M %p') if hasattr(approval, 'date_time') and approval.date_time else '',
                    }
            except Exception as e:
                print(f"No approval data: {e}")
            
            # Add closing data if exists
            try:
                review = issue.machineissue
                if review and hasattr(review, 'issueclosing'):
                    closing = review.issueclosing
                    if closing:
                        data['closing'] = {
                            'technician': closing.technician or '',
                            'supervisor': closing.supervisor or '',
                            'solution': closing.solutionDescription or '',
                            'duration': closing.duration or 0,
                            'remarks': closing.remarks or '',
                            'equipment_status': closing.equipment_status or '',
                        }
            except Exception as e:
                print(f"No closing data: {e}")
            
            return JsonResponse(data)
            
        except MachineIssue.DoesNotExist:
            print(f"Ticket with pk={pk} not found")
            return JsonResponse({'error': 'Ticket not found'}, status=404)
        except Exception as e:
            print(f"Error in TicketDetailAPIView: {str(e)}")
            traceback.print_exc()
            return JsonResponse({
                'error': str(e),
                'type': type(e).__name__,
                'traceback': traceback.format_exc()
            }, status=500)



