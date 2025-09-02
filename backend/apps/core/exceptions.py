"""自定义异常处理器模块"""

import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.core.exceptions import PermissionDenied, ValidationError
from rest_framework.exceptions import (
    AuthenticationFailed,
    NotAuthenticated,
    PermissionDenied as DRFPermissionDenied,
    ValidationError as DRFValidationError,
    NotFound,
    MethodNotAllowed,
    Throttled,
)

logger = logging.getLogger('mtm_helper')


def custom_exception_handler(exc, context):
    """
    自定义异常处理器
    统一处理API异常，返回标准格式的错误响应
    
    Args:
        exc: 异常实例
        context: 异常上下文
        
    Returns:
        Response: 标准格式的错误响应
    """
    # 调用DRF默认的异常处理器
    response = exception_handler(exc, context)
    
    # 获取请求信息用于日志记录
    request = context.get('request')
    view = context.get('view')
    
    # 记录异常信息
    if request:
        logger.error(
            f"API异常: {exc.__class__.__name__} - {str(exc)} - "
            f"URL: {request.get_full_path()} - "
            f"Method: {request.method} - "
            f"User: {getattr(request.user, 'username', 'Anonymous')} - "
            f"View: {view.__class__.__name__ if view else 'Unknown'}"
        )
    
    # 如果DRF处理了异常，自定义响应格式
    if response is not None:
        custom_response_data = {
            'success': False,
            'data': None,
            'message': _get_error_message(exc, response.data),
            'error_code': _get_error_code(exc),
            'status_code': response.status_code
        }
        response.data = custom_response_data
        return response
    
    # 处理Django原生异常
    if isinstance(exc, Http404):
        return Response({
            'success': False,
            'data': None,
            'message': '请求的资源不存在',
            'error_code': 'NOT_FOUND',
            'status_code': 404
        }, status=status.HTTP_404_NOT_FOUND)
    
    if isinstance(exc, PermissionDenied):
        return Response({
            'success': False,
            'data': None,
            'message': '权限不足',
            'error_code': 'PERMISSION_DENIED',
            'status_code': 403
        }, status=status.HTTP_403_FORBIDDEN)
    
    if isinstance(exc, ValidationError):
        return Response({
            'success': False,
            'data': None,
            'message': '数据验证失败',
            'error_code': 'VALIDATION_ERROR',
            'status_code': 400
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 处理未捕获的异常
    logger.error(f"未处理的异常: {exc.__class__.__name__} - {str(exc)}", exc_info=True)
    return Response({
        'success': False,
        'data': None,
        'message': '服务器内部错误',
        'error_code': 'INTERNAL_ERROR',
        'status_code': 500
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _get_error_message(exc, response_data):
    """
    获取错误消息
    
    Args:
        exc: 异常实例
        response_data: DRF响应数据
        
    Returns:
        str: 错误消息
    """
    # 认证相关异常
    if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
        return '身份验证失败，请重新登录'
    
    # 权限相关异常
    if isinstance(exc, DRFPermissionDenied):
        return '权限不足，无法执行此操作'
    
    # 资源不存在异常
    if isinstance(exc, NotFound):
        return '请求的资源不存在'
    
    # 方法不允许异常
    if isinstance(exc, MethodNotAllowed):
        return '请求方法不被允许'
    
    # 限流异常
    if isinstance(exc, Throttled):
        return f'请求过于频繁，请在{exc.wait}秒后重试'
    
    # 验证异常
    if isinstance(exc, DRFValidationError):
        if isinstance(response_data, dict):
            # 提取第一个字段的第一个错误消息
            for field, errors in response_data.items():
                if isinstance(errors, list) and errors:
                    if field == 'non_field_errors':
                        return str(errors[0])
                    return f'{field}: {str(errors[0])}'
                elif isinstance(errors, str):
                    return f'{field}: {errors}'
        elif isinstance(response_data, list) and response_data:
            return str(response_data[0])
        return '数据验证失败'
    
    # 默认返回异常字符串表示
    return str(exc) if str(exc) else '未知错误'


def _get_error_code(exc):
    """
    获取错误代码
    
    Args:
        exc: 异常实例
        
    Returns:
        str: 错误代码
    """
    error_code_mapping = {
        NotAuthenticated: 'NOT_AUTHENTICATED',
        AuthenticationFailed: 'AUTHENTICATION_FAILED',
        DRFPermissionDenied: 'PERMISSION_DENIED',
        NotFound: 'NOT_FOUND',
        MethodNotAllowed: 'METHOD_NOT_ALLOWED',
        Throttled: 'THROTTLED',
        DRFValidationError: 'VALIDATION_ERROR',
    }
    
    return error_code_mapping.get(exc.__class__, 'UNKNOWN_ERROR')


class APIException(Exception):
    """
    自定义API异常基类
    """
    def __init__(self, message, error_code='API_ERROR', status_code=400):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(message)


class BusinessException(APIException):
    """
    业务逻辑异常
    """
    def __init__(self, message, error_code='BUSINESS_ERROR'):
        super().__init__(message, error_code, 400)


class ResourceNotFoundException(APIException):
    """
    资源不存在异常
    """
    def __init__(self, message='资源不存在', error_code='RESOURCE_NOT_FOUND'):
        super().__init__(message, error_code, 404)


class PermissionException(APIException):
    """
    权限异常
    """
    def __init__(self, message='权限不足', error_code='PERMISSION_DENIED'):
        super().__init__(message, error_code, 403)