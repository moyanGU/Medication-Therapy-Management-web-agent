import logging

from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import PushSubscription
from .serializers import PushSubscriptionSerializer, UserProfileSerializer

logger = logging.getLogger(__name__)


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
        # 组装序列化输入（字段名规范化）
        payload = {
            "endpoint": request.data.get("endpoint"),
            "keys": request.data.get("keys"),
            "user_agent": request.data.get("ua")
            or request.META.get("HTTP_USER_AGENT", ""),
            "time_zone": request.data.get("timeZone"),
            "app": request.data.get("app") or "mtm-helper",
        }
        # 支持可选 expirationTime（兼容浏览器返回）
        if request.data.get("expirationTime"):
            try:
                # 如果是 ISO 字符串，直接赋值；否则忽略
                payload["expiration_time"] = request.data.get("expirationTime")
            except Exception:
                pass

        # 若已存在同 endpoint 的订阅则更新
        sub = PushSubscription.objects.filter(endpoint=payload["endpoint"]).first()
        if sub:
            # 限定为当前用户的订阅；若是其他用户的同端点，重新归属当前用户
            sub.user = user
            sub.keys = payload["keys"] or {}
            sub.user_agent = payload["user_agent"]
            sub.time_zone = payload["time_zone"]
            sub.app = payload["app"]
            sub.is_active = True
            sub.updated_at = timezone.now()
            sub.save()
            logger.info(f"[Push] 更新订阅 user={user.id} endpoint={sub.endpoint}")
            return Response(
                {
                    "success": True,
                    "data": {"id": sub.id, "endpoint": sub.endpoint},
                    "message": "更新成功",
                }
            )

        serializer = PushSubscriptionSerializer(data=payload)
        if serializer.is_valid():
            sub = serializer.save(user=user)
            logger.info(f"[Push] 保存订阅 user={user.id} endpoint={sub.endpoint}")
            return Response(
                {
                    "success": True,
                    "data": {"id": sub.id, "endpoint": sub.endpoint},
                    "message": "保存成功",
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            logger.warning(f"[Push] 订阅数据非法 user={user.id} errors={serializer.errors}")
            return Response(
                {"success": False, "data": None, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

    # DELETE 分支
    endpoint = request.data.get("endpoint") or request.query_params.get("endpoint")
    if not endpoint:
        logger.warning(f"[Push] 删除订阅缺少 endpoint user={user.id}")
        return Response(
            {"success": False, "data": None, "message": "缺少 endpoint"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    deleted, _ = PushSubscription.objects.filter(user=user, endpoint=endpoint).delete()
    if deleted:
        logger.info(f"[Push] 删除订阅 user={user.id} endpoint={endpoint}")
        return Response({"success": True, "data": {}, "message": "删除成功"})
    else:
        logger.warning(f"[Push] 未找到订阅 user={user.id} endpoint={endpoint}")
        return Response(
            {"success": False, "data": None, "message": "订阅不存在"},
            status=status.HTTP_404_NOT_FOUND,
        )
