import os
import sys


def _is_test_runtime():
    return (
        os.getenv("PYTEST_CURRENT_TEST") is not None
        or "pytest" in sys.modules
        or any(arg for arg in sys.argv if arg in {"test", "pytest", "py.test"})
    )


def _install_mysql_driver():
    if _is_test_runtime():
        return

    import pymysql

    pymysql.install_as_MySQLdb()


_install_mysql_driver()
