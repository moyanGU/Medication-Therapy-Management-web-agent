"""ASGI config for mtm_helper project."""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtm_helper.settings')

application = get_asgi_application()