from django.conf import settings
from datetime import datetime, timedelta
from functools import wraps
from django.http import JsonResponse
from core.models import CustomUser
from django.utils.deprecation import MiddlewareMixin
import jwt 

def generateToken(user):
    payload = {
        'user_id':user.id,
        'username': user.username,
        'exp':datetime.now()+settings.JWT_EXPIRATION_DELTA,
        'iat':datetime.now()
    }

    access_token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    refresh_token = jwt.encode({
        'user_id':user.id,
        'exp':datetime.utcnow()+timedelta(days=7),
        'iat':datetime.utcnow()

    }, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    return access_token, refresh_token



def jwt_required(func):
     
    @wraps(func)
    def wrapped(request, *args, **kwargs):
        
        print(request)
        print(request["message"])
        print(request.headers)
        token = request.headers.get('Authorization')
        print(token)

        print(request.data)

        if not token:
            return JsonResponse({"Error": "Please provide a Valid Token"}, status=401)
        
        try:
            token = token.split(' ')[1]
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

        except(jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
            return JsonResponse({'Error':'Invalid Token'}, status=401)
        
        request.user = CustomUser.objects.get(id=payload["user_id"])
        return func(request, *args, **kwargs)
    
    return wrapped

# class DisableCSRFForAPI(MiddlewareMixin):
#     def process_request(self, request):
#         if request.path.startswith("/api/"):
#             setattr(request, '_dont_enforce_csrf_checks', True)





