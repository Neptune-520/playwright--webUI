from django.urls import path
from . import views
from . import views_actionset
from . import views_marketplace

app_name = 'script_editor'

urlpatterns = [
    path('', views.script_list, name='script-list'),
    path('export/', views.export_scripts, name='script-export'),
    path('import/', views.import_scripts, name='script-import'),
    path('<int:pk>/', views.script_detail, name='script-detail'),
    path('<int:pk>/export/', views.export_script_detail, name='script-export-detail'),
    path('<int:script_id>/duplicate/', views.duplicate_script, name='script-duplicate'),
    path('<int:script_id>/versions/', views.script_versions, name='script-versions'),
    path('<int:script_id>/versions/<int:version_id>/', views.script_version_detail, name='script-version-detail'),
    path('elements/', views.element_list, name='element-list'),
    path('elements/<int:pk>/', views.element_detail, name='element-detail'),
    path('steps/', views.step_list, name='step-list'),
    path('steps/<int:pk>/', views.step_detail, name='step-detail'),
    path('visual-editor/', views.visual_editor, name='visual-editor'),
    path('validate-script/', views.validate_script, name='validate-script'),
    path('global-config/', views.global_config, name='global-config'),

    path('recording/start/', views.recording_start, name='recording-start'),
    path('recording/<str:session_id>/actions/', views.recording_actions, name='recording-actions'),
    path('recording/<str:session_id>/stop/', views.recording_stop, name='recording-stop'),
    path('recording/<str:session_id>/convert/', views.recording_convert, name='recording-convert'),
    
    path('action-sets/', views_actionset.action_set_list, name='action-set-list'),
    path('action-sets/categories/', views_actionset.action_set_categories, name='action-set-categories'),
    path('action-sets/import/', views_actionset.action_set_import, name='action-set-import'),
    path('action-sets/export/', views_actionset.action_set_batch_export, name='action-set-batch-export'),
    path('action-sets/<int:pk>/', views_actionset.action_set_detail, name='action-set-detail'),
    path('action-sets/<int:pk>/export/', views_actionset.action_set_export, name='action-set-export'),
    path('action-sets/<int:pk>/expand/', views_actionset.action_set_expand, name='action-set-expand'),
    path('action-sets/<int:action_set_id>/steps/', views_actionset.action_set_step_list, name='action-set-step-list'),
    path('action-sets/<int:action_set_id>/steps/reorder/', views_actionset.action_set_step_reorder, name='action-set-step-reorder'),
    path('action-sets/steps/<int:pk>/', views_actionset.action_set_step_detail, name='action-set-step-detail'),
    path('action-sets/<int:action_set_id>/parameters/', views_actionset.action_set_parameter_list, name='action-set-parameter-list'),
    path('action-sets/parameters/<int:pk>/', views_actionset.action_set_parameter_detail, name='action-set-parameter-detail'),

    path('marketplace/items/', views_marketplace.marketplace_list_items, name='marketplace-list-items'),
    path('marketplace/search/', views_marketplace.marketplace_search_items, name='marketplace-search-items'),
    path('marketplace/folder/', views_marketplace.marketplace_create_folder, name='marketplace-create-folder'),
    path('marketplace/download/', views_marketplace.marketplace_download_file, name='marketplace-download-file'),
    path('marketplace/preview/', views_marketplace.marketplace_preview_file, name='marketplace-preview-file'),
    path('marketplace/upload/', views_marketplace.marketplace_upload_file, name='marketplace-upload-file'),
]
