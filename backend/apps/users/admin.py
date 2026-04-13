from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    自定义 User 的后台管理配置
    - 继承 Django 内置的 BaseUserAdmin，保留认证相关功能
    - 增加自定义字段在列表与详情中的展示与筛选
    - 注意：新增用户时的表单保持默认（username、password1、password2），避免不必要的表单定制
    """

    list_display = (
        "id",
        "username",
        "phone",
        "email",
        "is_active",
        "is_staff",
        "is_superuser",
        "is_admin",
        "date_joined",
        "last_login",
    )
    list_filter = ("is_active", "is_staff", "is_superuser", "is_admin", "gender")
    search_fields = ("username", "phone", "email", "first_name", "last_name")
    ordering = ("-date_joined",)
    readonly_fields = ("created_at", "updated_at", "last_login", "date_joined")

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "phone",
                    "avatar",
                    "birth_date",
                    "gender",
                    "emergency_contact",
                    "emergency_phone",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_admin",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            _("Important dates"),
            {"fields": ("last_login", "date_joined", "created_at", "updated_at")},
        ),
    )

    # 保留默认的新增用户字段配置（不扩展 email/phone），避免与默认的 add_form 冲突
    # 如需在后台“添加”页面要求填写 email/phone，可自定义 add_form 并在 add_fieldsets 中添加对应字段
