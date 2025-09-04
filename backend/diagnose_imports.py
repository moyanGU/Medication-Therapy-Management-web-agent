#!/usr/bin/env python
"""
模块导入诊断脚本
"""
import os
import sys

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtm_helper.settings')

def test_import(module_name):
    """测试模块导入"""
    try:
        __import__(module_name)
        print(f"✅ {module_name} - 导入成功")
        return True
    except Exception as e:
        print(f"❌ {module_name} - 导入失败: {e}")
        return False

def main():
    """主函数"""
    print("开始诊断模块导入...")
    
    # 测试基础Django导入
    print("\n1. 测试基础Django模块:")
    test_import('django')
    test_import('django.conf')
    
    # 测试设置模块
    print("\n2. 测试设置模块:")
    test_import('mtm_helper.settings')
    
    # 初始化Django
    print("\n3. 初始化Django...")
    try:
        import django
        django.setup()
        print("✅ Django初始化成功")
    except Exception as e:
        print(f"❌ Django初始化失败: {e}")
        return
    
    # 测试核心应用
    print("\n4. 测试应用模块:")
    apps_to_test = [
        'apps.authentication',
        'apps.users', 
        'apps.medicines',
        'apps.records',
        'apps.reminders',
        'apps.plans',
        'apps.medical_records',
        'apps.core',
    ]
    
    for app in apps_to_test:
        test_import(app)
    
    # 测试具体的视图和模型
    print("\n5. 测试具体模块:")
    specific_modules = [
        'apps.medicines.models',
        'apps.medicines.views', 
        'apps.medicines.serializers',
        'apps.medicines.upload_views',
        'apps.core.middleware',
        'apps.authentication.views',
    ]
    
    for module in specific_modules:
        test_import(module)

if __name__ == '__main__':
    main()