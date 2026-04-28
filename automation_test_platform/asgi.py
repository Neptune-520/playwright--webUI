"""
ASGI config for automation_test_platform project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'automation_test_platform.settings')

application = get_asgi_application()
