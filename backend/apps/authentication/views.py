import logging
import os

# # from apps.core.utils import generate_verification_code, send_sms
import re

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ParseError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.utils import generate_verification_code
from apps.users.models import User

logger = logging.getLogger(__name__)


@api_view(["POST"])
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
        return Response(
            {
                "success": False,
                "message": "请求体格式错误，请使用application/json提交",
                "data": None,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        # 获取请求参数
        username = (data.get("username") or "").strip()
        phone = (data.get("phone") or "").strip()
        password = (data.get("password") or "").strip()
        verification_code = (data.get("verification_code") or "").strip()

        logger.info(f"用户注册请求: username={username}, phone={phone}")

        # 参数验证
        if not all([username, phone, password, verification_code]):
            return Response(
                {"success": False, "message": "所有字段都是必填的", "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 用户名格式验证
        if len(username) < 3 or len(username) > 20:
            return Response(
                {"success": False, "message": "用户名长度必须在3-20个字符之间", "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 手机号格式验证
        phone_pattern = r"^1[3-9]\d{9}$"
        if not re.match(phone_pattern, phone):
            return Response(
                {"success": False, "message": "手机号格式不正确", "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 密码强度验证
        if len(password) < 6:
            return Response(
                {"success": False, "message": "密码长度至少6位", "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 从缓存校验验证码
        cache_key = f"sms:code:{phone}"
        cached_code = None
        try:
            cached_code = cache.get(cache_key)
        except Exception as ce:
            logger.error(f"读取验证码缓存失败，将回退到Session: {str(ce)}")
            # Session 回退
            cached_code = request.session.get(cache_key)

        if not cached_code:
            if not (
                getattr(settings, "DEBUG", False)
                and getattr(settings, "SMS_DEV_ECHO", False)
            ):
                return Response(
                    {"success": False, "message": "验证码错误或已过期", "data": None},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            logger.warning(
                "注册验证码校验降级: 缓存中未命中验证码，开发模式下放行",
                extra={"phone": phone},
            )
        elif verification_code != str(cached_code):
            return Response(
                {"success": False, "message": "验证码错误或已过期", "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 新增（可配置）：是否需要管理员审批后方可使用验证码
        # 通过 settings.REGISTRATION_REQUIRE_APPROVAL 控制，默认 True
        approved_key = f"sms:approved:{phone}:{verification_code}"
        require_approval = getattr(settings, "REGISTRATION_REQUIRE_APPROVAL", True)
        if require_approval:
            is_approved = False
            try:
                is_approved = bool(cache.get(approved_key))
            except Exception as ce:
                logger.warning(f"读取审批标记缓存失败，尝试Session回退: {str(ce)}")
                try:
                    is_approved = bool(request.session.get(approved_key))
                except Exception:
                    is_approved = False

            if not is_approved:
                return Response(
                    {"success": False, "message": "验证码尚未审批，请等待管理员确认", "data": None},
                    status=status.HTTP_403_FORBIDDEN,
                )
        else:
            logger.info("注册审批开关关闭：验证码无需管理员审批")

        # 验证成功后删除验证码，避免重复使用
        try:
            cache.delete(cache_key)
            cache.delete(approved_key)
        except Exception as ce:
            logger.warning(f"删除验证码缓存/审批标记失败，尝试删除Session: {str(ce)}")
            if cache_key in request.session:
                del request.session[cache_key]
            if approved_key in request.session:
                del request.session[approved_key]

        # 检查用户名是否已存在
        if User.objects.filter(username=username).exists():
            return Response(
                {"success": False, "message": "用户名已存在", "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 检查手机号是否已存在
        if User.objects.filter(phone=phone).exists():
            return Response(
                {"success": False, "message": "手机号已被注册", "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 创建用户
        with transaction.atomic():
            user = User.objects.create(
                username=username,
                phone=phone,
                password=make_password(password),
                email=f"{username}@example.com",  # 临时邮箱
                is_active=True,
            )

            # 生成JWT令牌
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            logger.info(f"用户注册成功: user_id={user.id}, username={username}")

            return Response(
                {
                    "success": True,
                    "message": "注册成功",
                    "data": {
                        "user": {
                            "id": user.id,
                            "username": user.username,
                            "phone": user.phone,
                            "email": user.email,
                            "is_admin": user.is_admin,
                            "created_at": user.created_at.isoformat(),
                        },
                        "tokens": {
                            "access": str(access_token),
                            "refresh": str(refresh),
                        },
                    },
                },
                status=status.HTTP_201_CREATED,
            )

    except Exception:
        logger.exception("用户注册失败")
        return Response(
            {"success": False, "message": "注册失败，请稍后重试", "data": None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
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
        return Response(
            {
                "success": False,
                "message": "请求体格式错误，请使用application/json提交",
                "data": None,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        # 获取请求参数
        username = (data.get("username") or "").strip()
        password = (data.get("password") or "").strip()

        logger.info(f"用户登录请求: username={username}")

        # 参数验证
        if not all([username, password]):
            return Response(
                {"success": False, "message": "用户名和密码都是必填的", "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 查找用户（支持用户名或手机号登录）
        user = None
        if re.match(r"^1[3-9]\d{9}$", username):  # 手机号格式
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
            return Response(
                {"success": False, "message": "用户不存在", "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 验证密码
        if not user.check_password(password):
            return Response(
                {"success": False, "message": "密码错误", "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 检查用户状态
        if not user.is_active:
            return Response(
                {"success": False, "message": "账户已被禁用", "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 生成JWT令牌
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        logger.info(f"用户登录成功: user_id={user.id}, username={user.username}")

        # 注意：avatar字段需可JSON序列化，这里返回URL或None
        avatar_value = None
        try:
            avatar_value = (
                user.avatar.url
                if getattr(user, "avatar", None) and user.avatar.name
                else None
            )
        except Exception:
            avatar_value = None

        return Response(
            {
                "success": True,
                "message": "登录成功",
                "data": {
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "phone": user.phone,
                        "email": user.email,
                        "is_admin": user.is_admin,
                        "avatar": avatar_value,
                        "created_at": user.created_at.isoformat(),
                    },
                    "tokens": {"access": str(access_token), "refresh": str(refresh)},
                },
            },
            status=status.HTTP_200_OK,
        )

    except Exception:
        logger.exception("用户登录失败")
        return Response(
            {"success": False, "message": "登录失败，请稍后重试", "data": None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def send_verification_code(request):
    """
    发送验证码API

    请求参数:
    - phone: 手机号

    返回:
    - success: 是否成功
    - message: 提示信息
    - data: 开发模式可回显验证码（生产环境不返回）
    """
    # 仅捕获请求体解析错误，避免客户端提交格式问题导致500
    try:
        data = request.data
    except ParseError as pe:
        logger.warning(f"发送验证码请求体解析失败: {str(pe)}")
        return Response(
            {
                "success": False,
                "message": "请求体格式错误，请使用application/json提交",
                "data": None,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        phone = (data.get("phone") or "").strip()

        logger.info(f"发送验证码请求: phone={phone}")

        # 手机号格式验证
        phone_pattern = r"^1[3-9]\d{9}$"
        if not re.match(phone_pattern, phone):
            return Response(
                {"success": False, "message": "手机号格式不正确", "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 频率限制：同一手机号60秒内只允许发送一次（使用原子 add 防止并发穿透）
        rate_key = f"sms:rate:{phone}"
        rate_limit_seconds = getattr(settings, "SMS_RATE_LIMIT_SECONDS", 60)
        try:
            added = cache.add(rate_key, 1, rate_limit_seconds)
            if added is False:
                return Response(
                    {"success": False, "message": "发送过于频繁，请稍后再试", "data": None},
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )
            if added is None:
                logger.warning(
                    "验证码限流降级: cache.add 返回 None，跳过本次限流判断",
                    extra={"rate_key": rate_key},
                )
        except Exception as ce:
            logger.warning(f"频率限制缓存写入失败，使用Session回退: {str(ce)}")
            try:
                if request.session.get(rate_key):
                    logger.info(f"Session 限流命中: rate_key={rate_key}")
                    return Response(
                        {"success": False, "message": "发送过于频繁，请稍后再试", "data": None},
                        status=status.HTTP_429_TOO_MANY_REQUESTS,
                    )
                request.session[rate_key] = 1
                request.session.set_expiry(min(rate_limit_seconds, 300))
            except Exception as se:
                logger.warning(f"Session 限流写入失败，忽略: {str(se)}")

        # 生成验证码
        verification_code = generate_verification_code(6)
        cache_key = f"sms:code:{phone}"
        ttl = getattr(settings, "SMS_CODE_TTL", 300)

        # 持久化验证码
        try:
            cache.set(cache_key, verification_code, ttl)
        except Exception as ce:
            logger.error(f"写入验证码/限流缓存失败，将回退到Session: {str(ce)}")
            # Session 回退：验证码与限流标记同时写入
            request.session[cache_key] = verification_code
            # 使用 Session 有效期，避免长时间保留（取验证码TTL、限流TTL与上限的最小值）
            try:
                fallback_expiry = min(ttl, 300)
                request.session.set_expiry(fallback_expiry)
            except Exception:
                pass

        # 模板化短信内容
        try:
            minutes = max(1, int(round(ttl / 60)))
        except Exception:
            minutes = 5
        sms_text = (
            getattr(settings, "SMS_TEMPLATES", {})
            .get("verification", "【MTM用药助手】您的验证码是 {code}，{ttl} 分钟内有效。")
            .format(code=verification_code, ttl=minutes)
        )

        # 集成 Spug 推送平台
        spug_enabled = getattr(
            settings,
            "SPUG_PUSH_ENABLED",
            os.getenv("SPUG_PUSH_ENABLED", "false").lower() == "true",
        )
        logger.info(f"Spug推送启用: {spug_enabled}")
        if spug_enabled:
            try:
                import requests

                base_url = getattr(
                    settings,
                    "SPUG_PUSH_URL",
                    os.getenv("SPUG_PUSH_URL", "https://push.spug.cc"),
                )
                template_id = (
                    getattr(settings, "SPUG_TEMPLATE_ID_VERIFICATION", "")
                    or getattr(
                        settings, "SPUG_TEMPLATE_ID", os.getenv("SPUG_TEMPLATE_ID", "")
                    )
                ).strip()
                app_name = getattr(
                    settings, "SPUG_APP_NAME", os.getenv("SPUG_APP_NAME", "MTM用药助手")
                )
                if not template_id:
                    logger.error("SPUG_TEMPLATE_ID 未配置")
                    return Response(
                        {"success": False, "message": "短信通道异常，请稍后重试", "data": None},
                        status=status.HTTP_503_SERVICE_UNAVAILABLE,
                    )
                url = f"{base_url.rstrip('/')}/send/{template_id}"
                payload = {
                    "name": app_name,
                    "code": verification_code,
                    "targets": phone,  # 即时传入的注册手机号
                }
                timeout = int(getattr(settings, "SPUG_PUSH_TIMEOUT_SECONDS", 3))
                token = getattr(settings, "SPUG_PUSH_TOKEN", "")
                headers = {"Content-Type": "application/x-www-form-urlencoded"}
                if token:
                    headers["Authorization"] = f"Bearer {token}"
                # 避免在日志中泄露敏感信息（手机号与验证码做脱敏）
                masked_phone = (
                    (phone[:3] + "****" + phone[-4:])
                    if isinstance(phone, str) and len(phone) == 11
                    else "[masked]"
                )
                masked_payload = {**payload, "code": "****", "targets": masked_phone}
                logger.info(
                    f"调用Spug发送验证码: url={url}, payload={masked_payload}, timeout={timeout}, auth={'yes' if token else 'no'}"
                )
                r = requests.post(url, data=payload, headers=headers, timeout=timeout)
                # 记录响应但不泄露敏感信息
                logger.info(f"Spug响应: status={r.status_code}, text={r.text[:200]}")
                r.raise_for_status()
            except Exception as se:
                logger.error(f"Spug 短信发送失败: {str(se)}")
                return Response(
                    {"success": False, "message": "短信通道异常，请稍后重试", "data": None},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )
        else:
            # 未启用Spug时，按原逻辑打印（仅开发环境允许回显）
            if getattr(settings, "DEBUG", False) or getattr(
                settings, "SMS_DEV_ECHO", False
            ):
                logger.info(f"模拟发送短信验证码: phone={phone}, content={sms_text}")
            else:
                logger.info(f"模拟发送短信验证码: phone={phone}, content=[masked]")

        resp_data = {"phone": phone}
        # 开发环境可回显验证码，生产环境不返回
        sms_dev_echo = getattr(
            settings, "SMS_DEV_ECHO", bool(getattr(settings, "DEBUG", False))
        )
        if sms_dev_echo:
            resp_data["code"] = verification_code

        return Response(
            {"success": True, "message": "验证码发送成功", "data": resp_data},
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.error(f"发送验证码失败: {str(e)}")
        return Response(
            {"success": False, "message": "发送失败，请稍后重试", "data": None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
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
        refresh_token_str = (request.data or {}).get("refresh_token", "")
        refresh_token_str = str(refresh_token_str).strip()

        if refresh_token_str:
            try:
                refresh = RefreshToken(refresh_token_str)
                refresh.blacklist()
                logger.info(f"登出刷新令牌已加入黑名单: user_id={refresh.get('user_id')}")
            except Exception as token_error:
                logger.warning(f"登出刷新令牌加入黑名单失败: {str(token_error)}")

        if hasattr(request, "user") and request.user.is_authenticated:
            logger.info(
                f"用户登出成功: user_id={request.user.id}, username={request.user.username}"
            )
        else:
            logger.info("匿名用户登出")

        return Response(
            {"success": True, "message": "登出成功", "data": None},
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.error(f"用户登出失败: {str(e)}")
        return Response(
            {"success": False, "message": "登出失败，请稍后重试", "data": None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
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
        refresh_token_str = request.data.get("refresh_token", "").strip()

        if not refresh_token_str:
            return Response(
                {"success": False, "message": "刷新令牌不能为空", "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            refresh = RefreshToken(refresh_token_str)
            rotate_refresh = settings.SIMPLE_JWT.get("ROTATE_REFRESH_TOKENS", False)
            blacklist_after_rotation = settings.SIMPLE_JWT.get(
                "BLACKLIST_AFTER_ROTATION", False
            )

            if rotate_refresh:
                if blacklist_after_rotation:
                    try:
                        refresh.blacklist()
                    except Exception as token_error:
                        logger.warning(f"刷新令牌加入黑名单失败: {str(token_error)}")
                user_id = refresh.get("user_id")
                user = User.objects.filter(id=user_id).first()
                if not user:
                    return Response(
                        {"success": False, "message": "用户不存在", "data": None},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )
                new_refresh = RefreshToken.for_user(user)
                access_token = new_refresh.access_token
                response_data = {
                    "access_token": str(access_token),
                    "access": str(access_token),
                    "refresh_token": str(new_refresh),
                    "refresh": str(new_refresh),
                }
            else:
                access_token = refresh.access_token
                response_data = {
                    "access_token": str(access_token),
                    "access": str(access_token),
                }

            logger.info(f"令牌刷新成功: user_id={refresh.get('user_id')}")

            return Response(
                {"success": True, "message": "令牌刷新成功", "data": response_data},
                status=status.HTTP_200_OK,
            )

        except Exception as token_error:
            logger.warning(f"无效的刷新令牌: {str(token_error)}")
            return Response(
                {"success": False, "message": "刷新令牌无效或已过期", "data": None},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    except Exception as e:
        logger.error(f"令牌刷新失败: {str(e)}")
        return Response(
            {"success": False, "message": "令牌刷新失败，请重新登录", "data": None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
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
        logger.info(
            f"令牌验证成功: user_id={request.user.id}, username={request.user.username}"
        )

        return Response(
            {
                "success": True,
                "message": "令牌有效",
                "data": {
                    "user": {
                        "id": request.user.id,
                        "username": request.user.username,
                        "phone": request.user.phone,
                        "email": request.user.email,
                        "is_admin": request.user.is_admin,
                    }
                },
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.error(f"令牌验证失败: {str(e)}")
        return Response(
            {"success": False, "message": "令牌验证失败", "data": None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def approve_verification_code(request):
    """
    管理员审批验证码，使其在注册时可被识别为有效。

    请求参数:
    - phone: 手机号
    - code: 验证码

    返回:
    - success
    - message
    """
    try:
        # 运行时权限校验：允许 is_superuser / is_staff / 自定义 is_admin
        user = getattr(request, "user", None)
        if not user or not (
            getattr(user, "is_superuser", False)
            or getattr(user, "is_staff", False)
            or getattr(user, "is_admin", False)
        ):
            return Response(
                {"success": False, "message": "需要管理员权限"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            data = request.data
        except ParseError as pe:
            logger.warning(f"审批验证码请求体解析失败: {str(pe)}")
            return Response(
                {
                    "success": False,
                    "message": "请求体格式错误，请使用application/json提交",
                    "data": None,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        phone = (data.get("phone") or "").strip()
        code = (data.get("code") or "").strip()

        if not phone or not code:
            return Response(
                {"success": False, "message": "手机号和验证码均为必填", "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 校验当前缓存中是否存在该验证码（未过期）
        cache_key = f"sms:code:{phone}"
        try:
            cached_code = cache.get(cache_key)
        except Exception as ce:
            logger.error(f"读取验证码缓存失败，将回退到Session: {str(ce)}")
            cached_code = request.session.get(cache_key)

        if not cached_code:
            return Response(
                {"success": False, "message": "验证码不存在或已过期", "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )

        if str(cached_code) != str(code):
            return Response(
                {"success": False, "message": "验证码不匹配", "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 设置审批标记
        approved_key = f"sms:approved:{phone}:{code}"
        ttl = getattr(settings, "SMS_CODE_TTL", 300)
        try:
            cache.set(approved_key, 1, ttl)
        except Exception as ce:
            logger.error(f"写入审批标记失败，将回退到Session: {str(ce)}")
            request.session[approved_key] = 1
            try:
                request.session.set_expiry(min(ttl, 300))
            except Exception:
                pass

        masked_phone = (
            (phone[:3] + "****" + phone[-4:])
            if isinstance(phone, str) and len(phone) == 11
            else "[masked]"
        )
        logger.info(
            f"管理员({getattr(request.user, 'username', 'admin')})已审批验证码: phone={masked_phone}"
        )

        return Response(
            {"success": True, "message": "已审批，验证码现在有效"}, status=status.HTTP_200_OK
        )

    except Exception:
        logger.exception("审批验证码失败")
        return Response(
            {"success": False, "message": "审批失败，请稍后重试", "data": None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
