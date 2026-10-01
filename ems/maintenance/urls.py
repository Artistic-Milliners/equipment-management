from django.urls import path
from .import views

app_name='maintenance'

urlpatterns = [
    # path('complain/', views.createComplain, name='complain'),
    path('get_machines/',views.get_machines, name='get_machines'),
    path('complain-view/', views.view_complains, name='complain_list'),
    path('closed-archive/', views.closed_complaints_archive, name='closed_archive'),
    path('complain-view/quick-review/<int:pk>', views.quick_review, name='quick_review'),
    path('complain-view/start-working/<int:pk>', views.start_working, name='start_working'),
    path('complain-view/complain-detail/<int:pk>', views.complain_detail, name='complain_detail'),
    path('complain-view/complain-detail/complain-delete/<int:pk>', views.complain_delete, name='complain_delete'),
    # path('complain-view/complain-detail/complain-reject/<int:pk>', views.complain_reject, name='complain_reject'),
    path('complain-view/complain-detail/complain-accept/<int:pk>', views.complain_approve, name='complain_approve'),
    path('complain_edit/<int:pk>',views.complain_edit, name='complain_edit'),
    # Temporary Issue Review
    path('temporary-issues/', views.temporary_issue_review_list, name='temp_issue_list'),
    path('temporary-issues/<int:pk>/review', views.temporary_issue_review_detail, name='temp_issue_review'),
]