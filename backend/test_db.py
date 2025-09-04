#!/usr/bin/env python
"""
数据库连接测试脚本
"""
import pymysql
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_mysql_connection():
    """测试MySQL连接"""
    print("=== MySQL连接测试 ===")
    
    # 数据库配置
    config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', '3306')),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', '{Ghp880218}.'),
        'charset': 'utf8mb4'
    }
    
    print(f"连接配置: {config['host']}:{config['port']}")
    print(f"用户: {config['user']}")
    
    try:
        # 测试连接到MySQL服务器（不指定数据库）
        connection = pymysql.connect(**config)
        print("✅ MySQL服务器连接成功")
        
        with connection.cursor() as cursor:
            # 检查数据库是否存在
            db_name = os.getenv('DB_NAME', 'mtm_helper')
            cursor.execute("SHOW DATABASES LIKE %s", (db_name,))
            result = cursor.fetchone()
            
            if result:
                print(f"✅ 数据库 '{db_name}' 已存在")
            else:
                print(f"❌ 数据库 '{db_name}' 不存在，正在创建...")
                cursor.execute(f"CREATE DATABASE {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                print(f"✅ 数据库 '{db_name}' 创建成功")
        
        connection.close()
        
        # 测试连接到指定数据库
        config['database'] = db_name
        connection = pymysql.connect(**config)
        print(f"✅ 连接到数据库 '{db_name}' 成功")
        connection.close()
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

def test_django_db():
    """测试Django数据库连接"""
    print("\n=== Django数据库连接测试 ===")
    
    try:
        import os
        import django
        
        # 设置Django环境
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtm_helper.settings')
        django.setup()
        
        from django.db import connection
        
        # 测试数据库连接
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
        print("✅ Django数据库连接成功")
        return True
        
    except Exception as e:
        print(f"❌ Django数据库连接失败: {e}")
        return False

def main():
    """主函数"""
    print("数据库连接诊断工具")
    print("=" * 50)
    
    # 测试PyMySQL连接
    mysql_ok = test_mysql_connection()
    
    if mysql_ok:
        # 测试Django连接
        django_ok = test_django_db()
        
        if django_ok:
            print("\n✅ 所有数据库连接测试通过")
        else:
            print("\n❌ Django数据库连接失败")
    else:
        print("\n❌ MySQL连接失败，无法继续测试")

if __name__ == '__main__':
    main()