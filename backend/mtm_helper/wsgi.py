"""WSGI config for mtm_helper project."""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtm_helper.settings')

application = get_wsgi_application()