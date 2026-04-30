import logging

from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import PushSubscription
from .serializers import PushSubscriptionSerializer, UserProfileSerializer

logger = logging.getLogger(__name__)


def _success(data, message, status_code=status.HTTP_200_OK):
    return Response({"success": True, "data": data, "message": message}, status=status_code)


def _error(message, status_code):
    return Response({"success": False, "data": None, "message": message}, status=status_code)


def _build_push_subscription_payload(request):
    payload = {
        "endpoint": (request.data or {}).get("endpoint"),
        "keys": (request.data or {}).get("keys"),
        "user_agent": (request.data or {}).get("ua") or request.META.get("HTTP_USER_AGENT", ""),
        "time_zone": (request.data or {}).get("timeZone"),
        "app": (request.data or {}).get("app") or "mtm-helper",
    }
    if (request.data or {}).get("expirationTime"):
        payload["expiration_time"] = (request.data or {}).get("expirationTime")
    return payload


def _update_existing_subscription(sub, user, payload):
    sub.user = user
    sub.keys = payload.get("keys") or {}
    sub.user_agent = payload.get("user_agent")
    sub.time_zone = payload.get("time_zone")
    sub.app = payload.get("app")
    sub.is_active = True
    sub.updated_at = timezone.now()
    sub.save()
    return sub


def _create_subscription(user, payload):
    serializer = PushSubscriptionSerializer(data=payload)
    if serializer.is_valid():
        return serializer.save(user=user), None
    return None, serializer.errors


def _parse_delete_endpoint(request):
    endpoint = (request.data or {}).get("endpoint") or request.query_params.get("endpoint")
    return str(endpoint or "").strip()


@api_view(["GET", "PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def profile(request):
    """
    当前登录用户的资料查询与更新
    GET  -> 返回当前用户资料
    PUT  -> 全量更新（仅允许可写字段）
    PATCH-> 部分更新
    """
    user = request.user

    if request.method == "GET":
        serializer = UserProfileSerializer(user)
        return Response({"success": True, "data": serializer.data, "message": "获取成功"})

    # 更新
    partial = request.method == "PATCH"
    serializer = UserProfileSerializer(user, data=request.data, partial=partial)
    if serializer.is_valid():
        serializer.save()
        return Response({"success": True, "data": serializer.data, "message": "更新成功"})

    return Response(
        {"success": False, "data": None, "message": serializer.errors},
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(["POST", "DELETE"])
@permission_classes([IsAuthenticated])
def push_subscriptions(request):
    """
    保存/删除当前登录用户的浏览器 Push 订阅

    POST  -> 保存或更新订阅
      Body: { endpoint, keys: {p256dh, auth}, ua?, timeZone?, app?, expirationTime? }
      Response: { success: true, data: { id, endpoint } }

    DELETE -> 删除订阅
      Body: { endpoint } 或 Query: ?endpoint=...
      Response: { success: true, data: {} }

    注意：遵循统一响应结构，日志详细记录。
    """
    user = request.user

    if request.method == "POST":
        payload = _build_push_subscription_payload(request)
        sub = PushSubscription.objects.filter(endpoint=payload["endpoint"]).first()
        if sub:
            sub = _update_existing_subscription(sub, user, payload)
            logger.info(f"[Push] 更新订阅 user={user.id} endpoint={sub.endpoint}")
            return _success({"id": sub.id, "endpoint": sub.endpoint}, "更新成功")

        sub, errors = _create_subscription(user, payload)
        if sub:
            logger.info(f"[Push] 保存订阅 user={user.id} endpoint={sub.endpoint}")
            return _success(
                {"id": sub.id, "endpoint": sub.endpoint},
                "保存成功",
                status_code=status.HTTP_201_CREATED,
            )
        logger.warning(f"[Push] 订阅数据非法 user={user.id} errors={errors}")
        return _error(errors, status.HTTP_400_BAD_REQUEST)

    # DELETE 分支
    endpoint = _parse_delete_endpoint(request)
    if not endpoint:
        logger.warning(f"[Push] 删除订阅缺少 endpoint user={user.id}")
        return _error("缺少 endpoint", status.HTTP_400_BAD_REQUEST)

    deleted, _ = PushSubscription.objects.filter(user=user, endpoint=endpoint).delete()
    if deleted:
        logger.info(f"[Push] 删除订阅 user={user.id} endpoint={endpoint}")
        return _success({}, "删除成功")

    logger.warning(f"[Push] 未找到订阅 user={user.id} endpoint={endpoint}")
    return _error("订阅不存在", status.HTTP_404_NOT_FOUND)
