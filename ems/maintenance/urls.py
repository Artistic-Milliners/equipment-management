from django.urls import path
from .import views

app_name='maintenance'

urlpatterns = [
    # path('complain/', views.createComplain, name='complain'),
    path('get_machines/',views.get_machines, name='get_machines'),
    path('complain-view/', views.view_complains, name='complain_list'),
    path('complain-view/complain-detail/<int:pk>', views.complain_detail, name='complain_detail'),
    path('complain-view/complain-detail/complain-delete/<int:pk>', views.complain_delete, name='complain_delete'),
    path('complain-view/complain-detail/complain-reject/<int:pk>', views.complain_reject, name='complain_reject'),
    path('complain-view/complain-detail/complain-accept/<int:pk>', views.complain_approve, name='complain_approve'),
    path('complain_edit/<int:pk>',views.complain_edit, name='complain_edit')
]