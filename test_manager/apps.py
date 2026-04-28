from django.apps import AppConfig


class TestManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'test_manager'
    verbose_name = '测试管理'
