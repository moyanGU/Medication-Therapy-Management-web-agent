from django.urls import path

from . import views

app_name = "authentication"

urlpatterns = [
    # 用户注册
    path("register/", views.register, name="register"),
    # 用户登录
    path("login/", views.login, name="login"),
    # 发送验证码
    path("send-code/", views.send_verification_code, name="send_verification_code"),
    # 管理员审批验证码（只有管理员登录后可调用）
    path(
        "admin/approve-code/",
        views.approve_verification_code,
        name="approve_verification_code",
    ),
    # 用户登出
    path("logout/", views.logout, name="logout"),
    # 刷新令牌
    path("refresh/", views.refresh_token, name="refresh_token"),
    # 验证令牌
    path("verify/", views.verify_token, name="verify_token"),
]
