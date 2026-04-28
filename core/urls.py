from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('groups/', views.group_list, name='group-list'),
    path('groups/<int:pk>/', views.group_detail, name='group-detail'),
    path('scripts/clear-screenshots/', views.clear_screenshots, name='clear-screenshots'),
    path('scripts/clear-task-results/', views.clear_task_results, name='clear-task-results'),
    path('error-config/', views.error_config_list, name='error-config-list'),
    path('error-config/<int:config_id>/', views.update_error_config, name='error-config-update'),
    path('error-config/<int:config_id>/delete/', views.delete_error_config, name='error-config-delete'),
]
