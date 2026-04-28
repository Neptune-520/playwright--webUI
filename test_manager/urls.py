from django.urls import path
from . import views

app_name = 'test_manager'

urlpatterns = [
    path('tasks/', views.task_list, name='task-list'),
    path('tasks/<int:pk>/', views.task_detail, name='task-detail'),
    path('tasks/<int:task_id>/execute/', views.execute_task_view, name='task-execute'),
    path('tasks/<int:task_id>/stop/', views.stop_task, name='task-stop'),
    path('tasks/<int:task_id>/upload/', views.trigger_upload, name='task-upload'),
    path('results/', views.result_list, name='result-list'),
    path('results/<int:pk>/', views.result_detail, name='result-detail'),
    path('results/<int:result_id>/screenshots/', views.get_test_screenshots, name='result-screenshots'),
    path('results/<int:task_id>/export/', views.export_test_report, name='result-export'),
]
