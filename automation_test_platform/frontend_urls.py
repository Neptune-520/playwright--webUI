from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
    path('groups/', TemplateView.as_view(template_name='groups.html'), name='groups-list'),
    path('global-config/', TemplateView.as_view(template_name='global_config.html'), name='global-config'),
    path('action-sets/', TemplateView.as_view(template_name='action_sets.html'), name='action-sets-list'),
    path('scripts/', TemplateView.as_view(template_name='scripts.html'), name='scripts-list'),
    path('editor/', TemplateView.as_view(template_name='visual_editor.html'), name='visual-editor'),
    path('tasks/', TemplateView.as_view(template_name='tasks.html'), name='tasks-list'),
    path('results/', TemplateView.as_view(template_name='results.html'), name='results-list'),
    path('results/<int:task_id>/', TemplateView.as_view(template_name='result_detail.html'), name='result-detail'),
    path('test-input/', TemplateView.as_view(template_name='test_input.html'), name='test-input'),
    path('error-config/', TemplateView.as_view(template_name='error_config.html'), name='error-config'),
]
