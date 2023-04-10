from django.urls import path, include
from . import views


machine_crud_patterns = [

]

app_name = 'User'


urlpatterns = [
    path('', views.index, name='index'),
    path('home', views.home, name='home'),
    path('home/machine/<int:pk>', views.machine_detail, name='machineDetail'),
    path('add', views.add_machine, name='add_machine'),
    path('edit/<int:pk>', views.edit_machine, name='edit_machine'),
    path('update/<int:pk>', views.update_machine, name='update_machine'),
    path('delete/<int:pk>', views.delete_machine, name='delete_machine'),
    path('home/spares', views.spare_view, name='spares'),
    path('home/spares/addSpare', views.spare_add, name='spares_add'),
    path('home/spares/deleteSpare/<int:pk>', views.spare_delete, name='spares_delete'),
]