"""
WSGI config for Smart Irrigation System project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sis.settings')

application = get_wsgi_application()
