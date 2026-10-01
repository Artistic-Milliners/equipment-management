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
    # TODO: Restore these functions from previous version
    # path('home/spares/receiveStock/<int:pk>', views.spare_receive, name='spares_receive'),
    # path('api/spares/search', views.spare_search_api, name='spares_search_api'),
    # path('api/spares/detail/<int:pk>', views.spare_detail_api, name='spares_detail_api'),
    # path('api/spares/transactions/<int:pk>', views.spare_transactions_api, name='spares_transactions_api'),
    # path('home/spares/export', views.export_inventory_csv, name='export_inventory_csv'),
    # path('home/spares/export/transactions/<int:pk>', views.export_spare_transactions_csv, name='export_spare_transactions_csv'),
    path('home/users/',views.ListUsers.as_view(), name='list_users'),
    path('home/users/<int:pk>',views.DetailUserView.as_view(), name='detail_user'),
    path('home/unit', views.ListUnitView.as_view(),name='list_unit'),
    path('home/unit/create', views.CreateUnitView.as_view(), name='create_unit'),
    path('machine-hours/<int:pk>', views.machineHoursAPIView.as_view(), name='machine_hours'),
    path('machine-issue/<str:filter>', views.filterTicketAPIView.as_view(), name='filter_ticket'),
    path('machine-code/<int:pk>', views.MachineCodeAPIView.as_view(), name='machine_code'),
    path('api/issuelist/<int:equipment_pk>/', views.IssueListAPIView.as_view(), name='api_issuelist'),
    path('api/machine-section/<int:machine_pk>/', views.MachineSectionAPIView.as_view(), name='api_machine_section'),
    path('home/complain', views.InitiateComplainView.as_view(), name='create_complain'),
    path('home/complain/complainTracking/<int:pk>', views.ComplainTrackingView.as_view(), name='complain_track'),
    path('home/complain/<int:pk>/user-close', views.user_close_complaint, name='user_close_complaint'),
    path('home/complain/review/<int:pk>', views.ComplainReviewView.as_view(), name='review_complain'),
    path('home/approvals', views.ApprovalListView.as_view(), name='approval_list'),
    path('home/complain/closing/<int:pk>', views.ComplainClosingView.as_view(), name="complain_closing"),
    path('home/complain/closing/complainList', views.ClosedComplainListView.as_view(), name="complain_closing_list"),
    path('reports/downtime', views.downtime_report, name="downtime_report"),
]