#!/usr/bin/env python
"""
创建测试数据脚本
用于创建测试用户和药品数据
"""
import os
import sys
from datetime import date, timedelta

import django


def create_test_user(User):
    """创建测试用户"""
    print("🔵 创建测试用户...")

    # 检查用户是否已存在
    if User.objects.filter(username="testuser").exists():
        print("✅ 测试用户已存在")
        return User.objects.get(username="testuser")

    # 创建测试用户
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="test123456",
        phone="13800138000",  # 添加手机号字段
    )
    print(f"✅ 测试用户创建成功: {user.username}")
    return user


def create_test_medicines(Medicine, user):
    """创建测试药品数据"""
    print("🔵 创建测试药品数据...")

    # 清理现有测试数据
    Medicine.objects.filter(user_id=user.id).delete()

    # 测试药品数据
    medicines_data = [
        {
            "name": "阿司匹林肠溶片",
            "specification": "100mg*30片",
            "manufacturer": "拜耳医药",
            "medicine_type": "tablet",
            "quantity": 28,
            "is_prescription": False,
            "expiry_date": date.today() + timedelta(days=365),
            "purchase_date": date.today() - timedelta(days=30),
            "purchase_price": 25.80,
            "batch_number": "ASP20240301",
            "storage_conditions": "密封，在干燥处保存",
            "description": "用于预防心血管疾病，每日一片",
        },
        {
            "name": "氨氯地平片",
            "specification": "5mg*14片",
            "manufacturer": "辉瑞制药",
            "medicine_type": "tablet",
            "quantity": 12,
            "is_prescription": True,
            "expiry_date": date.today() + timedelta(days=180),
            "purchase_date": date.today() - timedelta(days=15),
            "purchase_price": 42.50,
            "batch_number": "AML20240315",
            "storage_conditions": "密闭保存",
            "description": "降压药，每日一次，每次5mg",
        },
        {
            "name": "复方甘草片",
            "specification": "48片",
            "manufacturer": "同仁堂",
            "medicine_type": "tablet",
            "quantity": 35,
            "is_prescription": False,
            "expiry_date": date.today() + timedelta(days=90),
            "purchase_date": date.today() - timedelta(days=10),
            "purchase_price": 12.00,
            "batch_number": "GC20240320",
            "storage_conditions": "密封保存",
            "description": "止咳化痰，一次3-4片，一日3次",
        },
        {
            "name": "维生素D3软胶囊",
            "specification": "400IU*60粒",
            "manufacturer": "汤臣倍健",
            "medicine_type": "capsule",
            "quantity": 45,
            "is_prescription": False,
            "expiry_date": date.today() + timedelta(days=720),
            "purchase_date": date.today() - timedelta(days=5),
            "purchase_price": 89.00,
            "batch_number": "VD20240325",
            "storage_conditions": "避光，密封，在阴凉干燥处保存",
            "description": "补充维生素D，每日一粒",
        },
        {
            "name": "开塞露",
            "specification": "20ml*10支",
            "manufacturer": "华润三九",
            "medicine_type": "liquid",
            "quantity": 8,
            "is_prescription": False,
            "expiry_date": date.today() + timedelta(days=540),
            "purchase_date": date.today() - timedelta(days=20),
            "purchase_price": 15.60,
            "batch_number": "KSL20240305",
            "storage_conditions": "密封保存",
            "description": "通便，临时使用",
        },
    ]

    created_medicines = []
    for medicine_data in medicines_data:
        medicine = Medicine.objects.create(user=user, **medicine_data)
        created_medicines.append(medicine)
        print(f"✅ 创建药品: {medicine.name}")

    print(f"✅ 总共创建了 {len(created_medicines)} 个测试药品")
    return created_medicines


def main():
    """主函数"""
    print("🚀 开始创建测试数据...")

    try:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mtm_helper.settings")
        django.setup()

        from django.contrib.auth import get_user_model

        from apps.medicines.models import Medicine

        User = get_user_model()

        # 创建测试用户
        user = create_test_user(User)

        # 创建测试药品
        medicines = create_test_medicines(Medicine, user)

        print("\n📊 测试数据统计:")
        print(f"   用户: {user.username} (ID: {user.id})")
        print(f"   药品数量: {len(medicines)}")
        print(f"   处方药: {len([m for m in medicines if m.is_prescription])}")
        print(f"   非处方药: {len([m for m in medicines if not m.is_prescription])}")

        print("\n🎉 测试数据创建完成!")
        print("\n📝 测试账号信息:")
        print("   用户名: testuser")
        print("   密码: test123456")
        print("   邮箱: test@example.com")

    except Exception as e:
        print(f"❌ 创建测试数据失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
