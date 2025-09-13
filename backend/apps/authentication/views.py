from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.db import transaction
from apps.users.models import User
# # from apps.core.utils import generate_verification_code, send_sms
import re
import logging
from rest_framework.exceptions import ParseError

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    用户注册API
    
    请求参数:
    - username: 用户名
    - phone: 手机号
    - password: 密码
    - verification_code: 验证码
    
    返回:
    - success: 是否成功
    - data: 用户信息和令牌
    - message: 提示信息
    """
    # 仅捕获请求体解析错误，避免误将客户端错误转为500
    try:
        data = request.data
    except ParseError as pe:
        logger.warning(f"用户注册请求体解析失败: {str(pe)}")
        return Response({
            'success': False,
            'message': '请求体格式错误，请使用application/json提交',
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        # 获取请求参数
        username = (data.get('username') or '').strip()
        phone = (data.get('phone') or '').strip()
        password = (data.get('password') or '').strip()
        verification_code = (data.get('verification_code') or '').strip()
        
        logger.info(f"用户注册请求: username={username}, phone={phone}")
        
        # 参数验证
        if not all([username, phone, password, verification_code]):
            return Response({
                'success': False,
                'message': '所有字段都是必填的',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 用户名格式验证
        if len(username) < 3 or len(username) > 20:
            return Response({
                'success': False,
                'message': '用户名长度必须在3-20个字符之间',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 手机号格式验证
        phone_pattern = r'^1[3-9]\d{9}$'
        if not re.match(phone_pattern, phone):
            return Response({
                'success': False,
                'message': '手机号格式不正确',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 密码强度验证
        if len(password) < 6:
            return Response({
                'success': False,
                'message': '密码长度至少6位',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证码验证（模拟实现）
        if verification_code != '123456':  # 临时使用固定验证码
            return Response({
                'success': False,
                'message': '验证码错误',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查用户名是否已存在
        if User.objects.filter(username=username).exists():
            return Response({
                'success': False,
                'message': '用户名已存在',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查手机号是否已存在
        if User.objects.filter(phone=phone).exists():
            return Response({
                'success': False,
                'message': '手机号已被注册',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 创建用户
        with transaction.atomic():
            user = User.objects.create(
                username=username,
                phone=phone,
                password=make_password(password),
                email=f"{username}@example.com",  # 临时邮箱
                is_active=True
            )
            
            # 生成JWT令牌
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            logger.info(f"用户注册成功: user_id={user.id}, username={username}")
            
            return Response({
                'success': True,
                'message': '注册成功',
                'data': {
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'phone': user.phone,
                        'email': user.email,
                        'is_admin': user.is_admin,
                        'created_at': user.created_at.isoformat()
                    },
                    'tokens': {
                        'access': str(access_token),
                        'refresh': str(refresh)
                    }
                }
            }, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        logger.exception("用户注册失败")
        return Response({
            'success': False,
            'message': '注册失败，请稍后重试',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    用户登录API
    
    请求参数:
    - username: 用户名或手机号
    - password: 密码
    
    返回:
    - success: 是否成功
    - data: 用户信息和令牌
    - message: 提示信息
    """
    # 仅捕获请求体解析错误，避免误将客户端错误转为500
    try:
        data = request.data
    except ParseError as pe:
        logger.warning(f"用户登录请求体解析失败: {str(pe)}")
        return Response({
            'success': False,
            'message': '请求体格式错误，请使用application/json提交',
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        # 获取请求参数
        username = (data.get('username') or '').strip()
        password = (data.get('password') or '').strip()
        
        logger.info(f"用户登录请求: username={username}")
        
        # 参数验证
        if not all([username, password]):
            return Response({
                'success': False,
                'message': '用户名和密码都是必填的',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 查找用户（支持用户名或手机号登录）
        user = None
        if re.match(r'^1[3-9]\d{9}$', username):  # 手机号格式
            try:
                user = User.objects.get(phone=username)
            except User.DoesNotExist:
                pass
        else:  # 用户名格式
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                pass
        
        if not user:
            return Response({
                'success': False,
                'message': '用户不存在',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证密码
        if not user.check_password(password):
            return Response({
                'success': False,
                'message': '密码错误',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查用户状态
        if not user.is_active:
            return Response({
                'success': False,
                'message': '账户已被禁用',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 生成JWT令牌
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        logger.info(f"用户登录成功: user_id={user.id}, username={user.username}")
        
        # 注意：avatar字段需可JSON序列化，这里返回URL或None
        avatar_value = None
        try:
            avatar_value = user.avatar.url if getattr(user, 'avatar', None) and user.avatar.name else None
        except Exception:
            avatar_value = None
        
        return Response({
            'success': True,
            'message': '登录成功',
            'data': {
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'phone': user.phone,
                    'email': user.email,
                    'is_admin': user.is_admin,
                    'avatar': avatar_value,
                    'created_at': user.created_at.isoformat()
                },
                'tokens': {
                    'access': str(access_token),
                    'refresh': str(refresh)
                }
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.exception("用户登录失败")
        return Response({
            'success': False,
            'message': '登录失败，请稍后重试',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_verification_code(request):
    """
    发送验证码API
    
    请求参数:
    - phone: 手机号
    
    返回:
    - success: 是否成功
    - message: 提示信息
    """
    try:
        phone = request.data.get('phone', '').strip()
        
        logger.info(f"发送验证码请求: phone={phone}")
        
        # 手机号格式验证
        phone_pattern = r'^1[3-9]\d{9}$'
        if not re.match(phone_pattern, phone):
            return Response({
                'success': False,
                'message': '手机号格式不正确',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 生成验证码（模拟实现）
        verification_code = '123456'  # 临时使用固定验证码
        
        # 发送短信（模拟实现）
        # 在实际项目中，这里应该调用短信服务API
        logger.info(f"模拟发送验证码: phone={phone}, code={verification_code}")
        
        return Response({
            'success': True,
            'message': '验证码发送成功',
            'data': {
                'phone': phone,
                'code': verification_code  # 开发环境返回验证码，生产环境不应返回
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"发送验证码失败: {str(e)}")
        return Response({
            'success': False,
            'message': '发送失败，请稍后重试',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def logout(request):
    """
    用户登出API
    
    请求头:
    - Authorization: Bearer <access_token>
    
    返回:
    - success: 是否成功
    - message: 提示信息
    """
    try:
        # 安全地获取用户信息
        if hasattr(request, 'user') and request.user.is_authenticated:
            logger.info(f"用户登出成功: user_id={request.user.id}, username={request.user.username}")
        else:
            logger.info("匿名用户登出")
        
        return Response({
            'success': True,
            'message': '登出成功',
            'data': None
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"用户登出失败: {str(e)}")
        return Response({
            'success': False,
            'message': '登出失败，请稍后重试',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """
    刷新访问令牌API
    
    请求参数:
    - refresh_token: 刷新令牌
    
    返回:
    - success: 是否成功
    - data: 新的访问令牌
    - message: 提示信息
    """
    try:
        refresh_token_str = request.data.get('refresh_token', '').strip()
        
        if not refresh_token_str:
            return Response({
                'success': False,
                'message': '刷新令牌不能为空',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 验证刷新令牌
            refresh = RefreshToken(refresh_token_str)
            
            # 生成新的访问令牌
            access_token = refresh.access_token
            
            logger.info(f"令牌刷新成功: user_id={refresh.get('user_id')}")
            
            return Response({
                'success': True,
                'message': '令牌刷新成功',
                'data': {
                    'access': str(access_token)
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as token_error:
            logger.warning(f"无效的刷新令牌: {str(token_error)}")
            return Response({
                'success': False,
                'message': '刷新令牌无效或已过期',
                'data': None
            }, status=status.HTTP_401_UNAUTHORIZED)
            
    except Exception as e:
        logger.error(f"令牌刷新失败: {str(e)}")
        return Response({
            'success': False,
            'message': '令牌刷新失败，请重新登录',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_token(request):
    """
    验证令牌有效性API
    
    请求头:
    - Authorization: Bearer <access_token>
    
    返回:
    - success: 是否成功
    - data: 用户信息
    - message: 提示信息
    """
    try:
        logger.info(f"令牌验证成功: user_id={request.user.id}, username={request.user.username}")
        
        return Response({
            'success': True,
            'message': '令牌有效',
            'data': {
                'user': {
                    'id': request.user.id,
                    'username': request.user.username,
                    'phone': request.user.phone,
                    'email': request.user.email,
                    'is_admin': request.user.is_admin,
                }
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"令牌验证失败: {str(e)}")
        return Response({
            'success': False,
            'message': '令牌验证失败',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)