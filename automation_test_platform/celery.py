"""
Celery configuration for automation_test_platform project.
"""

import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'automation_test_platform.settings')

app = Celery('automation_test_platform')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
