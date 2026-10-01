from django.urls import path
from .views import UserLoginAPIView, UserTokenRefreshAPIView, HomeAPIView, TicketDetailAPIView


app_name='api'

urlpatterns = [
    path('user/login/', UserLoginAPIView.as_view(), name="login"),
    path('user/login/refreshtoken/', UserTokenRefreshAPIView.as_view(), name="tokenRefresh"),
    path('user/home/', HomeAPIView.as_view()),
    path('ticket-detail/<int:pk>/', TicketDetailAPIView.as_view(), name="ticket_detail"),
]
