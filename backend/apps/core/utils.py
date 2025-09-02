"""核心工具模块"""

import logging
import hashlib
import secrets
from typing import Any, Dict, Optional
from django.http import JsonResponse
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger('mtm_helper')


def success_response(data: Any = None, message: str = '操作成功', status_code: int = 200) -> Response:
    """
    成功响应格式化器
    
    Args:
        data: 响应数据
        message: 响应消息
        status_code: HTTP状态码
        
    Returns:
        Response: DRF响应对象
    """
    response_data = {
        'success': True,
        'data': data,
        'message': message,
        'status_code': status_code
    }
    return Response(response_data, status=status_code)


def error_response(message: str = '操作失败', 
                  error_code: str = 'ERROR', 
                  status_code: int = 400,
                  data: Any = None) -> Response:
    """
    错误响应格式化器
    
    Args:
        message: 错误消息
        error_code: 错误代码
        status_code: HTTP状态码
        data: 额外数据
        
    Returns:
        Response: DRF响应对象
    """
    response_data = {
        'success': False,
        'data': data,
        'message': message,
        'error_code': error_code,
        'status_code': status_code
    }
    return Response(response_data, status=status_code)


def paginated_response(queryset, serializer_class, request, message: str = '获取成功'):
    """
    分页响应格式化器
    
    Args:
        queryset: 查询集
        serializer_class: 序列化器类
        request: 请求对象
        message: 响应消息
        
    Returns:
        Response: 分页响应
    """
    from rest_framework.pagination import PageNumberPagination
    
    paginator = PageNumberPagination()
    paginator.page_size = 20
    paginated_queryset = paginator.paginate_queryset(queryset, request)
    
    serializer = serializer_class(paginated_queryset, many=True)
    
    return paginator.get_paginated_response({
        'success': True,
        'data': {
            'results': serializer.data,
            'pagination': {
                'count': paginator.page.paginator.count,
                'current_page': paginator.page.number,
                'total_pages': paginator.page.paginator.num_pages,
                'page_size': paginator.page_size,
                'has_next': paginator.page.has_next(),
                'has_previous': paginator.page.has_previous(),
            }
        },
        'message': message
    })


def generate_cache_key(*args, **kwargs) -> str:
    """
    生成缓存键
    
    Args:
        *args: 位置参数
        **kwargs: 关键字参数
        
    Returns:
        str: 缓存键
    """
    # 将所有参数转换为字符串并排序
    key_parts = [str(arg) for arg in args]
    key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
    
    # 生成MD5哈希
    key_string = ":".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


def cache_result(timeout: int = 300, key_prefix: str = 'cache'):
    """
    缓存装饰器
    
    Args:
        timeout: 缓存超时时间（秒）
        key_prefix: 缓存键前缀
        
    Returns:
        function: 装饰器函数
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{key_prefix}:{generate_cache_key(func.__name__, *args, **kwargs)}"
            
            # 尝试从缓存获取结果
            result = cache.get(cache_key)
            if result is not None:
                logger.debug(f"缓存命中: {cache_key}")
                return result
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            logger.debug(f"设置缓存: {cache_key}")
            
            return result
        return wrapper
    return decorator


def generate_verification_code(length: int = 6) -> str:
    """
    生成验证码
    
    Args:
        length: 验证码长度
        
    Returns:
        str: 验证码
    """
    import random
    import string
    
    # 生成数字验证码
    return ''.join(random.choices(string.digits, k=length))


def generate_secure_token(length: int = 32) -> str:
    """
    生成安全令牌
    
    Args:
        length: 令牌长度
        
    Returns:
        str: 安全令牌
    """
    return secrets.token_urlsafe(length)


def validate_phone_number(phone: str) -> bool:
    """
    验证手机号格式
    
    Args:
        phone: 手机号
        
    Returns:
        bool: 是否有效
    """
    import re
    
    # 中国大陆手机号正则表达式
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))


def validate_email(email: str) -> bool:
    """
    验证邮箱格式
    
    Args:
        email: 邮箱地址
        
    Returns:
        bool: 是否有效
    """
    import re
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def mask_sensitive_data(data: str, mask_char: str = '*', visible_chars: int = 4) -> str:
    """
    遮蔽敏感数据
    
    Args:
        data: 原始数据
        mask_char: 遮蔽字符
        visible_chars: 可见字符数
        
    Returns:
        str: 遮蔽后的数据
    """
    if len(data) <= visible_chars:
        return mask_char * len(data)
    
    visible_start = visible_chars // 2
    visible_end = visible_chars - visible_start
    
    masked_length = len(data) - visible_chars
    masked_part = mask_char * masked_length
    
    return data[:visible_start] + masked_part + data[-visible_end:] if visible_end > 0 else data[:visible_start] + masked_part


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小
    
    Args:
        size_bytes: 文件大小（字节）
        
    Returns:
        str: 格式化后的文件大小
    """
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    
    return f"{s} {size_names[i]}"


def get_client_ip(request) -> str:
    """
    获取客户端IP地址
    
    Args:
        request: Django请求对象
        
    Returns:
        str: 客户端IP地址
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_user_action(user, action: str, details: Dict[str, Any] = None):
    """
    记录用户操作日志
    
    Args:
        user: 用户对象
        action: 操作类型
        details: 操作详情
    """
    log_data = {
        'user_id': user.id if user.is_authenticated else None,
        'username': user.username if user.is_authenticated else 'Anonymous',
        'action': action,
        'details': details or {},
    }
    
    logger.info(f"用户操作: {log_data}")


def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除不安全字符
    
    Args:
        filename: 原始文件名
        
    Returns:
        str: 清理后的文件名
    """
    import re
    import os
    
    # 移除路径分隔符和其他不安全字符
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # 移除控制字符
    filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
    
    # 限制文件名长度
    name, ext = os.path.splitext(filename)
    if len(name) > 100:
        name = name[:100]
    
    return name + ext


def convert_to_dict(obj) -> Dict[str, Any]:
    """
    将对象转换为字典
    
    Args:
        obj: 要转换的对象
        
    Returns:
        Dict[str, Any]: 转换后的字典
    """
    if hasattr(obj, '__dict__'):
        return {key: value for key, value in obj.__dict__.items() 
                if not key.startswith('_')}
    return {}


def batch_process(items, batch_size: int = 100, processor_func=None):
    """
    批量处理数据
    
    Args:
        items: 要处理的数据列表
        batch_size: 批次大小
        processor_func: 处理函数
        
    Yields:
        处理结果
    """
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        if processor_func:
            yield processor_func(batch)
        else:
            yield batch


class ResponseFormatter:
    """
    响应格式化器类
    提供统一的API响应格式
    """
    
    @staticmethod
    def success(data=None, message='操作成功', status_code=200):
        """成功响应"""
        return success_response(data, message, status_code)
    
    @staticmethod
    def error(message='操作失败', error_code='ERROR', status_code=400, data=None):
        """错误响应"""
        return error_response(message, error_code, status_code, data)
    
    @staticmethod
    def not_found(message='资源不存在'):
        """404响应"""
        return error_response(message, 'NOT_FOUND', 404)
    
    @staticmethod
    def forbidden(message='权限不足'):
        """403响应"""
        return error_response(message, 'FORBIDDEN', 403)
    
    @staticmethod
    def unauthorized(message='未授权访问'):
        """401响应"""
        return error_response(message, 'UNAUTHORIZED', 401)
    
    @staticmethod
    def validation_error(message='数据验证失败', errors=None):
        """验证错误响应"""
        return error_response(message, 'VALIDATION_ERROR', 400, errors)