from django.urls import path, include
from . import views


app_name = 'User'


urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('home', views.home, name='home'),
    path('home/machine/<int:pk>', views.machine_detail, name='machineDetail'),
    path('add', views.add_machine, name='add_machine'),
    path('edit/<int:pk>', views.edit_machine, name='edit_machine'),
    path('update/<int:pk>', views.update_machine, name='update_machine'),
    path('delete/<int:pk>', views.delete_machine, name='delete_machine'),
    path('home/spares', views.spare_view, name='spares'),
    path('home/spares/addSpare', views.spare_add, name='spares_add'),
    path('home/spares/updateSpare/<int:pk>', views.spare_update, name='spares_update'),
    path('home/spares/deleteSpare/<int:pk>', views.spare_delete, name='spares_delete'),
    path('home/spares/issueSpare/<int:pk>', views.spare_issue, name='spares_issue'),
]