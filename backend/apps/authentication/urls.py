from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    # 用户注册
    path('register/', views.register, name='register'),
    
    # 用户登录
    path('login/', views.login, name='login'),
    
    # 发送验证码
    path('send-code/', views.send_verification_code, name='send_verification_code'),
    
    # 用户登出
    path('logout/', views.logout, name='logout'),
]