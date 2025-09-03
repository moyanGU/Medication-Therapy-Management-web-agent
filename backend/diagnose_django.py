#!/usr/bin/env python3
"""
Django启动诊断脚本
"""
import os
import sys

def diagnose_django():
    """诊断Django启动问题"""
    print("=== Django启动诊断 ===")
    
    # 检查Python环境
    print(f"Python版本: {sys.version}")
    print(f"Python路径: {sys.executable}")
    
    # 检查当前目录
    current_dir = os.getcwd()
    print(f"当前目录: {current_dir}")
    
    # 检查manage.py文件
    manage_py_path = os.path.join(current_dir, 'manage.py')
    if os.path.exists(manage_py_path):
        print("✅ manage.py 文件存在")
    else:
        print("❌ manage.py 文件不存在")
        print("请确保在backend目录中运行此脚本")
        return False
    
    # 检查settings.py文件
    settings_path = os.path.join(current_dir, 'mtm_helper', 'settings.py')
    if os.path.exists(settings_path):
        print("✅ settings.py 文件存在")
    else:
        print("❌ settings.py 文件不存在")
        return False
    
    # 检查关键依赖
    try:
        import django
        print(f"✅ Django版本: {django.get_version()}")
    except ImportError:
        print("❌ Django未安装")
        return False
    
    try:
        import rest_framework
        print("✅ Django REST Framework 已安装")
    except ImportError:
        print("❌ Django REST Framework 未安装")
    
    try:
        import corsheaders
        print("✅ django-cors-headers 已安装")
    except ImportError:
        print("❌ django-cors-headers 未安装")
    
    # 尝试导入Django设置
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtm_helper.settings')
        import django
        django.setup()
        from django.conf import settings
        print("✅ Django设置加载成功")
        print(f"SECRET_KEY: {settings.SECRET_KEY[:20]}...")
        print(f"DEBUG模式: {settings.DEBUG}")
    except Exception as e:
        print(f"❌ Django设置加载失败: {e}")
        return False
    
    # 测试数据库连接
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        print("✅ 数据库连接正常")
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        print("可能需要运行: python manage.py migrate")
    
    return True

if __name__ == "__main__":
    success = diagnose_django()
    if success:
        print("\n🚀 Django配置看起来正常，尝试启动服务器...")
        print("运行命令: python manage.py runserver 127.0.0.1:8000")
    else:
        print("\n❌ 发现配置问题，请先解决上述问题")