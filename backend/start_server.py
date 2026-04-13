#!/usr/bin/env python
"""
简化Django启动诊断脚本
"""
import os
import sys

import django
from django.core.management import execute_from_command_line
from django.core.wsgi import get_wsgi_application


def check_environment():
    """检查环境配置"""
    print("=== 环境检查 ===")
    print(f"Python版本: {sys.version}")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"Python路径: {sys.executable}")

    # 检查Django设置
    print(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE', '未设置')}")


def check_imports():
    """检查关键模块导入"""
    print("\n=== 模块导入检查 ===")

    try:
        import django

        print(f"✅ Django版本: {django.get_version()}")
    except ImportError as e:
        print(f"❌ Django导入失败: {e}")
        return False

    try:
        from django.conf import settings

        print(f"✅ Django settings导入成功: DEBUG={getattr(settings, 'DEBUG', None)}")
    except ImportError as e:
        print(f"❌ Django settings导入失败: {e}")
        return False

    return True


def check_settings():
    """检查Django设置"""
    print("\n=== Django设置检查 ===")

    try:
        from django.conf import settings

        # 检查关键设置
        print(f"DEBUG: {getattr(settings, 'DEBUG', '未设置')}")
        print(f"ALLOWED_HOSTS: {getattr(settings, 'ALLOWED_HOSTS', '未设置')}")
        print(f"INSTALLED_APPS数量: {len(getattr(settings, 'INSTALLED_APPS', []))}")

        # 检查数据库配置
        databases = getattr(settings, "DATABASES", {})
        if "default" in databases:
            db_config = databases["default"]
            print(f"数据库引擎: {db_config.get('ENGINE', '未设置')}")
            print(f"数据库名称: {db_config.get('NAME', '未设置')}")

        return True
    except Exception as e:
        print(f"❌ Django设置检查失败: {e}")
        return False


def test_django_setup():
    """测试Django初始化"""
    print("\n=== Django初始化测试 ===")

    try:
        django.setup()
        print("✅ Django初始化成功")
        return True
    except Exception as e:
        print(f"❌ Django初始化失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_wsgi_app():
    """测试WSGI应用"""
    print("\n=== WSGI应用测试 ===")

    try:
        get_wsgi_application()
        print("✅ WSGI应用创建成功")
        return True
    except Exception as e:
        print(f"❌ WSGI应用创建失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("Django服务器启动诊断工具")
    print("=" * 50)

    # 设置Django环境
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mtm_helper.settings")

    # 逐步检查
    if not check_imports():
        print("\n❌ 模块导入失败，无法继续")
        return

    check_environment()

    if not check_settings():
        print("\n❌ Django设置检查失败，无法继续")
        return

    if not test_django_setup():
        print("\n❌ Django初始化失败，无法继续")
        return

    if not test_wsgi_app():
        print("\n❌ WSGI应用测试失败，无法继续")
        return

    print("\n✅ 所有检查通过，尝试启动开发服务器...")

    # 尝试启动服务器
    try:
        print("启动Django开发服务器 127.0.0.1:8000...")
        execute_from_command_line(["manage.py", "runserver", "127.0.0.1:8000"])
    except KeyboardInterrupt:
        print("\n服务器被用户中断")
    except Exception as e:
        print(f"\n❌ 服务器启动失败: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
