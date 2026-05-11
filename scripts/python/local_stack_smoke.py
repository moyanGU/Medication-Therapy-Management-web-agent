import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2] / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mtm_helper.settings")

import django

django.setup()

from django.core.cache import cache
from django.db import connection


def main():
    result = {"db": None, "cache": None}

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result["db"] = cursor.fetchone()[0]
    except Exception as exc:
        result["db"] = f"ERROR: {exc}"

    try:
        cache.set("local_stack_smoke", "ok", 30)
        result["cache"] = cache.get("local_stack_smoke")
    except Exception as exc:
        result["cache"] = f"ERROR: {exc}"

    print(result)


if __name__ == "__main__":
    main()
