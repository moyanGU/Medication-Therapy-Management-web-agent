import sys
import os
sys.path.append(os.path.join(os.getcwd(), "backend"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mtm_helper.settings")
try:
    import django
    django.setup()
    print("Django setup successful")
except Exception as e:
    import traceback
    traceback.print_exc()
