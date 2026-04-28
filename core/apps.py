from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = '核心功能'
    
    def ready(self):
        from core import signal_handlers
        from core.signals import script_execution_completed
        
        script_execution_completed.connect(signal_handlers.on_script_execution_completed)
