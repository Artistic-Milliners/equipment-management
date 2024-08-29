from django.urls import path
from .views import UserLoginAPIView, UserTokenRefreshAPIView, HomeAPIView


app_name='api'

urlpatterns = [
    path('user/login/', UserLoginAPIView.as_view(), name="login"),
    path('user/login/refreshtoken/', UserTokenRefreshAPIView.as_view(), name="tokenRefresh"),
    path('user/home/', HomeAPIView.as_view())
]
