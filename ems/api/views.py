from django.contrib.auth import authenticate
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserLoginSerializer
from core.models import CustomUser
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import AuthenticationFailed
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



