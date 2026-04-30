"""自定义异常处理器模块"""

import logging

from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import (
    AuthenticationFailed,
    MethodNotAllowed,
    NotAuthenticated,
    NotFound,
)
from rest_framework.exceptions import PermissionDenied as DRFPermissionDenied
from rest_framework.exceptions import Throttled
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger("mtm_helper")


def _summarize_error_payload(payload):
    if isinstance(payload, dict):
        fields = list(payload.keys())
        return {
            "field_count": len(fields),
            "fields": fields[:10],
        }

    if isinstance(payload, list):
        return {
            "item_count": len(payload),
            "preview": payload[:3],
        }

    if payload is None:
        return None

    return str(payload)


def _get_request_id(request):
    if not request:
        return None
    return getattr(request, "request_id", None) or request.META.get("HTTP_X_REQUEST_ID")


def _log_api_exception(exc, request, view):
    if not request:
        return
    request_id = _get_request_id(request)
    logger.error(
        f"API异常: {exc.__class__.__name__} - {str(exc)} - "
        f"URL: {request.get_full_path()} - "
        f"Method: {request.method} - "
        f"Request ID: {request_id or 'unknown'} - "
        f"User: {getattr(request.user, 'username', 'Anonymous')} - "
        f"View: {view.__class__.__name__ if view else 'Unknown'}"
    )


def _normalize_validation_payload(exc, payload):
    if isinstance(exc, DRFValidationError) and isinstance(payload, list):
        return {"non_field_errors": payload}
    return payload


def _build_custom_response_data(exc, response, request, view):
    response_payload = _normalize_validation_payload(exc, response.data)
    custom_response_data = {
        "success": False,
        "data": response_payload if isinstance(exc, DRFValidationError) else None,
        "message": _get_error_message(exc, response.data),
        "error_code": _get_error_code(exc),
        "status_code": response.status_code,
        "request_id": getattr(request, "request_id", None) if request else None,
    }
    if request:
        logger.error(
            "API异常摘要: %s",
            {
                "exception": exc.__class__.__name__,
                "url": request.get_full_path(),
                "method": request.method,
                "user": getattr(request.user, "username", "Anonymous"),
                "view": view.__class__.__name__ if view else "Unknown",
                "request_id": custom_response_data["request_id"],
                "status_code": response.status_code,
                "error_code": custom_response_data["error_code"],
                "payload_summary": _summarize_error_payload(
                    response_payload if isinstance(exc, DRFValidationError) else response.data
                ),
            },
        )
    return custom_response_data


def _handle_django_exception(exc):
    if isinstance(exc, Http404):
        return Response(
            {
                "success": False,
                "data": None,
                "message": "请求的资源不存在",
                "error_code": "NOT_FOUND",
                "status_code": 404,
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    if isinstance(exc, PermissionDenied):
        return Response(
            {
                "success": False,
                "data": None,
                "message": "权限不足",
                "error_code": "PERMISSION_DENIED",
                "status_code": 403,
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    if isinstance(exc, ValidationError):
        return Response(
            {
                "success": False,
                "data": None,
                "message": "数据验证失败",
                "error_code": "VALIDATION_ERROR",
                "status_code": 400,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    return None


def _internal_error_response(exc):
    logger.error(f"未处理的异常: {exc.__class__.__name__} - {str(exc)}", exc_info=True)
    return Response(
        {
            "success": False,
            "data": None,
            "message": "服务器内部错误",
            "error_code": "INTERNAL_ERROR",
            "status_code": 500,
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


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
    request = context.get("request")
    view = context.get("view")

    # 记录异常信息
    _log_api_exception(exc, request, view)

    # 如果DRF处理了异常，自定义响应格式
    if response is not None:
        response.data = _build_custom_response_data(exc, response, request, view)
        return response

    # 处理Django原生异常
    django_resp = _handle_django_exception(exc)
    if django_resp is not None:
        return django_resp

    return _internal_error_response(exc)


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
        return "身份验证失败，请重新登录"

    # 权限相关异常
    if isinstance(exc, DRFPermissionDenied):
        return "权限不足，无法执行此操作"

    # 资源不存在异常
    if isinstance(exc, NotFound):
        return "请求的资源不存在"

    # 方法不允许异常
    if isinstance(exc, MethodNotAllowed):
        return "请求方法不被允许"

    # 限流异常
    if isinstance(exc, Throttled):
        return f"请求过于频繁，请在{exc.wait}秒后重试"

    if isinstance(exc, DRFValidationError):
        msg = _validation_error_message(response_data)
        return msg or "数据验证失败"

    # 默认返回异常字符串表示
    if getattr(settings, "DEBUG", False):
        return str(exc) if str(exc) else "未知错误"
    return "请求处理失败，请稍后重试"


def _validation_error_message(response_data):
    if isinstance(response_data, dict):
        for field, errors in response_data.items():
            if isinstance(errors, list) and errors:
                if field == "non_field_errors":
                    return str(errors[0])
                return f"{field}: {str(errors[0])}"
            if isinstance(errors, str):
                return f"{field}: {errors}"
        return None
    if isinstance(response_data, list) and response_data:
        return str(response_data[0])
    return None


def _get_error_code(exc):
    """
    获取错误代码

    Args:
        exc: 异常实例

    Returns:
        str: 错误代码
    """
    error_code_mapping = {
        NotAuthenticated: "NOT_AUTHENTICATED",
        AuthenticationFailed: "AUTHENTICATION_FAILED",
        DRFPermissionDenied: "PERMISSION_DENIED",
        NotFound: "NOT_FOUND",
        MethodNotAllowed: "METHOD_NOT_ALLOWED",
        Throttled: "THROTTLED",
        DRFValidationError: "VALIDATION_ERROR",
    }

    return error_code_mapping.get(exc.__class__, "UNKNOWN_ERROR")


class APIException(Exception):
    """
    自定义API异常基类
    """

    def __init__(self, message, error_code="API_ERROR", status_code=400):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(message)


class BusinessException(APIException):
    """
    业务逻辑异常
    """

    def __init__(self, message, error_code="BUSINESS_ERROR"):
        super().__init__(message, error_code, 400)


class ResourceNotFoundException(APIException):
    """
    资源不存在异常
    """

    def __init__(self, message="资源不存在", error_code="RESOURCE_NOT_FOUND"):
        super().__init__(message, error_code, 404)


class PermissionException(APIException):
    """
    权限异常
    """

    def __init__(self, message="权限不足", error_code="PERMISSION_DENIED"):
        super().__init__(message, error_code, 403)
