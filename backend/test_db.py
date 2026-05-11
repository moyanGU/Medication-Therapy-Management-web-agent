#!/usr/bin/env python
"""
Local database smoke tests used by pytest.
"""

import os
from pathlib import Path

import pymysql
import pytest
from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).resolve().parent
DOTENV_PATH = SCRIPT_DIR / ".env"
if DOTENV_PATH.exists():
    load_dotenv(dotenv_path=str(DOTENV_PATH), override=False)


def test_mysql_connection():
    config = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "charset": "utf8mb4",
    }

    assert config["user"], "DB_USER is required"
    assert config["password"], "DB_PASSWORD is required"

    connection = pymysql.connect(**config)
    try:
        with connection.cursor() as cursor:
            db_name = os.getenv("DB_NAME", "mtm_helper")
            cursor.execute("SHOW DATABASES LIKE %s", (db_name,))
            result = cursor.fetchone()
            assert result, f"Database {db_name!r} does not exist"
    finally:
        connection.close()

    config["database"] = os.getenv("DB_NAME", "mtm_helper")
    db_connection = pymysql.connect(**config)
    db_connection.close()


@pytest.mark.django_db
def test_django_db():
    import django

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mtm_helper.settings")
    django.setup()

    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        assert cursor.fetchone()[0] == 1
