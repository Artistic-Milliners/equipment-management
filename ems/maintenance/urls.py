from django.urls import path
from .import views

app_name='maintenance'

urlpatterns = [
    path('complain/', views.createComplain, name='complain'),
    path('get_machines/',views.get_machines, name='get_machines'),
    path('complain-view/', views.view_complains, name='complain_list'),
    path('complain-view/complain-detail/<int:pk>', views.complain_detail, name='complain_detail' )
]