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


def _response_error(message: str, http_status: int):
    return Response(
        {"success": False, "message": message, "data": None},
        status=http_status,
    )


def _parse_request_data(request, action: str):
    try:
        return request.data, None
    except ParseError as pe:
        logger.warning(f"{action}请求体解析失败: {str(pe)}")
        return None, Response(
            {
                "success": False,
                "message": "请求体格式错误，请使用application/json提交",
                "data": None,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


def _is_valid_phone(phone: str) -> bool:
    return bool(re.match(r"^1[3-9]\d{9}$", phone or ""))


def _mask_phone(phone: str) -> str:
    if isinstance(phone, str) and len(phone) == 11:
        return phone[:3] + "****" + phone[-4:]
    return "[masked]"


def _cache_get_with_session_fallback(request, key: str):
    try:
        return cache.get(key)
    except Exception as ce:
        logger.warning(f"读取缓存失败，使用Session回退: {str(ce)}")
        try:
            return request.session.get(key)
        except Exception:
            return None


def _cache_set_with_session_fallback(request, key: str, value, ttl: int):
    try:
        cache.set(key, value, ttl)
        return True
    except Exception as ce:
        logger.warning(f"写入缓存失败，使用Session回退: {str(ce)}")
        try:
            request.session[key] = value
            request.session.set_expiry(min(int(ttl or 0), 300) if ttl else 300)
            return True
        except Exception:
            return False


def _cache_add_with_session_fallback(request, key: str, value, ttl: int):
    try:
        added = cache.add(key, value, ttl)
        return added, None
    except Exception as ce:
        logger.warning(f"缓存写入失败，使用Session回退: {str(ce)}")
        try:
            if request.session.get(key):
                return False, None
            request.session[key] = value
            request.session.set_expiry(min(int(ttl or 0), 300) if ttl else 300)
            return True, None
        except Exception as se:
            return None, str(se)


def _cache_delete_with_session_fallback(request, *keys: str):
    for key in keys:
        try:
            cache.delete(key)
        except Exception:
            try:
                if key in request.session:
                    del request.session[key]
            except Exception:
                continue


def _should_skip_code_check_in_dev() -> bool:
    return bool(getattr(settings, "DEBUG", False) and getattr(settings, "SMS_DEV_ECHO", False))


def _build_user_payload(user):
    role = (
        "pharmacist"
        if getattr(user, "is_staff", False) or getattr(user, "is_admin", False)
        else "patient"
    )
    return {
        "id": user.id,
        "username": user.username,
        "phone": user.phone,
        "email": user.email,
        "is_admin": user.is_admin,
        "role": role,
        "created_at": user.created_at.isoformat(),
    }


def _find_user_by_identifier(identifier: str):
    ident = str(identifier or "").strip()
    if not ident:
        return None
    if _is_valid_phone(ident):
        return User.objects.filter(phone=ident).first()
    return User.objects.filter(username=ident).first()


def _safe_avatar_url(user):
    try:
        avatar = getattr(user, "avatar", None)
        if avatar and getattr(avatar, "name", None):
            return avatar.url
        return None
    except Exception:
        return None


def _build_login_payload(user, refresh, access_token):
    payload = _build_user_payload(user)
    payload["avatar"] = _safe_avatar_url(user)
    return {
        "user": payload,
        "tokens": {"access": str(access_token), "refresh": str(refresh)},
    }


def _send_verification_via_spug(phone: str, code: str) -> tuple[bool, str | None]:
    if not _is_spug_enabled():
        return True, None

    try:
        import requests

        base_url = getattr(
            settings,
            "SPUG_PUSH_URL",
            os.getenv("SPUG_PUSH_URL", "https://push.spug.cc"),
        )
        template_id = (
            getattr(settings, "SPUG_TEMPLATE_ID_VERIFICATION", "")
            or getattr(settings, "SPUG_TEMPLATE_ID", os.getenv("SPUG_TEMPLATE_ID", ""))
        ).strip()
        app_name = getattr(settings, "SPUG_APP_NAME", os.getenv("SPUG_APP_NAME", "MTM用药助手"))
        if not template_id:
            logger.error("SPUG_TEMPLATE_ID 未配置")
            return False, "template_id_missing"

        url = f"{base_url.rstrip('/')}/send/{template_id}"
        payload = {"name": app_name, "code": code, "targets": phone}
        timeout = int(getattr(settings, "SPUG_PUSH_TIMEOUT_SECONDS", 3))
        token = getattr(settings, "SPUG_PUSH_TOKEN", "")
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        masked_payload = {**payload, "code": "****", "targets": _mask_phone(phone)}
        logger.info(
            f"调用Spug发送验证码: url={url}, payload={masked_payload}, timeout={timeout}, auth={'yes' if token else 'no'}"
        )
        r = requests.post(url, data=payload, headers=headers, timeout=timeout)
        logger.info(f"Spug响应: status={r.status_code}, text={r.text[:200]}")
        r.raise_for_status()
        return True, None
    except Exception as se:
        logger.error(f"Spug 短信发送失败: {str(se)}")
        return False, "spug_failed"


def _is_spug_enabled() -> bool:
    return bool(
        getattr(
            settings,
            "SPUG_PUSH_ENABLED",
            os.getenv("SPUG_PUSH_ENABLED", "false").lower() == "true",
        )
    )


def _validate_register_input(username: str, phone: str, password: str, code: str):
    if not all([username, phone, password, code]):
        return _response_error("所有字段都是必填的", status.HTTP_400_BAD_REQUEST)
    if len(username) < 3 or len(username) > 20:
        return _response_error("用户名长度必须在3-20个字符之间", status.HTTP_400_BAD_REQUEST)
    if not _is_valid_phone(phone):
        return _response_error("手机号格式不正确", status.HTTP_400_BAD_REQUEST)
    if len(password) < 6:
        return _response_error("密码长度至少6位", status.HTTP_400_BAD_REQUEST)
    return None


def _verify_registration_code(request, phone: str, verification_code: str):
    cache_key = f"sms:code:{phone}"
    cached_code = _cache_get_with_session_fallback(request, cache_key)
    if not cached_code:
        if not _should_skip_code_check_in_dev():
            return None, None, _response_error("验证码错误或已过期", status.HTTP_400_BAD_REQUEST)
        logger.warning(
            "注册验证码校验降级: 缓存中未命中验证码，开发模式下放行",
            extra={"phone": phone},
        )
    elif verification_code != str(cached_code):
        return None, None, _response_error("验证码错误或已过期", status.HTTP_400_BAD_REQUEST)

    approved_key = f"sms:approved:{phone}:{verification_code}"
    require_approval = getattr(settings, "REGISTRATION_REQUIRE_APPROVAL", True)
    if require_approval:
        is_approved = bool(_cache_get_with_session_fallback(request, approved_key))
        if not is_approved:
            return None, None, _response_error(
                "验证码尚未审批，请等待管理员确认", status.HTTP_403_FORBIDDEN
            )

    return cache_key, approved_key, None


def _create_user(username: str, phone: str, password: str):
    with transaction.atomic():
        return User.objects.create(
            username=username,
            phone=phone,
            password=make_password(password),
            email=f"{username}@example.com",
            is_active=True,
        )


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
    data, error_resp = _parse_request_data(request, "用户注册")
    if error_resp is not None:
        return error_resp

    try:
        username = str((data or {}).get("username") or "").strip()
        phone = str((data or {}).get("phone") or "").strip()
        password = str((data or {}).get("password") or "").strip()
        verification_code = str((data or {}).get("verification_code") or "").strip()

        logger.info(f"用户注册请求: username={username}, phone={phone}")

        error = _validate_register_input(username, phone, password, verification_code)
        if error is not None:
            return error

        cache_key, approved_key, error = _verify_registration_code(
            request, phone, verification_code
        )
        if error is not None:
            return error

        _cache_delete_with_session_fallback(request, cache_key, approved_key)

        if User.objects.filter(username=username).exists():
            return _response_error("用户名已存在", status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(phone=phone).exists():
            return _response_error("手机号已被注册", status.HTTP_400_BAD_REQUEST)

        user = _create_user(username, phone, password)

        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        logger.info(f"用户注册成功: user_id={user.id}, username={username}")
        return Response(
            {
                "success": True,
                "message": "注册成功",
                "data": {
                    "user": _build_user_payload(user),
                    "tokens": {"access": str(access_token), "refresh": str(refresh)},
                },
            },
            status=status.HTTP_201_CREATED,
        )
    except Exception:
        logger.exception("用户注册失败")
        return _response_error("注册失败，请稍后重试", status.HTTP_500_INTERNAL_SERVER_ERROR)


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
    data, error_resp = _parse_request_data(request, "用户登录")
    if error_resp is not None:
        return error_resp

    try:
        username = str((data or {}).get("username") or "").strip()
        password = str((data or {}).get("password") or "").strip()

        logger.info(f"用户登录请求: username={username}")

        if not all([username, password]):
            return _response_error("用户名和密码都是必填的", status.HTTP_400_BAD_REQUEST)

        user = _find_user_by_identifier(username)
        if not user:
            return _response_error("用户不存在", status.HTTP_400_BAD_REQUEST)

        if not user.check_password(password):
            return _response_error("密码错误", status.HTTP_400_BAD_REQUEST)

        if not user.is_active:
            return _response_error("账户已被禁用", status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        logger.info(f"用户登录成功: user_id={user.id}, username={user.username}")

        return Response(
            {
                "success": True,
                "message": "登录成功",
                "data": _build_login_payload(user, refresh, access_token),
            },
            status=status.HTTP_200_OK,
        )
    except Exception:
        logger.exception("用户登录失败")
        return _response_error("登录失败，请稍后重试", status.HTTP_500_INTERNAL_SERVER_ERROR)


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
    data, error_resp = _parse_request_data(request, "发送验证码")
    if error_resp is not None:
        return error_resp

    try:
        phone = str((data or {}).get("phone") or "").strip()
        logger.info(f"发送验证码请求: phone={phone}")

        if not _is_valid_phone(phone):
            return _response_error("手机号格式不正确", status.HTTP_400_BAD_REQUEST)

        rate_key = f"sms:rate:{phone}"
        rate_limit_seconds = int(getattr(settings, "SMS_RATE_LIMIT_SECONDS", 60))
        added, session_err = _cache_add_with_session_fallback(
            request, rate_key, 1, rate_limit_seconds
        )
        if added is False:
            return _response_error("发送过于频繁，请稍后再试", status.HTTP_429_TOO_MANY_REQUESTS)
        if added is None and session_err is None:
            logger.warning(
                "验证码限流降级: cache.add 返回 None，跳过本次限流判断",
                extra={"rate_key": rate_key},
            )

        verification_code = generate_verification_code(6)
        cache_key = f"sms:code:{phone}"
        ttl = int(getattr(settings, "SMS_CODE_TTL", 300))
        _cache_set_with_session_fallback(request, cache_key, verification_code, ttl)

        ok, _ = _send_verification_via_spug(phone, verification_code)
        if not ok:
            return _response_error("短信通道异常，请稍后重试", status.HTTP_503_SERVICE_UNAVAILABLE)

        if not _is_spug_enabled():
            try:
                minutes = max(1, int(round(ttl / 60)))
            except Exception:
                minutes = 5
            sms_text = (
                getattr(settings, "SMS_TEMPLATES", {})
                .get(
                    "verification",
                    "【MTM用药助手】您的验证码是 {code}，{ttl} 分钟内有效。",
                )
                .format(code=verification_code, ttl=minutes)
            )
            if getattr(settings, "DEBUG", False) or getattr(settings, "SMS_DEV_ECHO", False):
                logger.info(f"模拟发送短信验证码: phone={phone}, content={sms_text}")
            else:
                logger.info(f"模拟发送短信验证码: phone={phone}, content=[masked]")

        resp_data = {"phone": phone}
        sms_dev_echo = getattr(settings, "SMS_DEV_ECHO", bool(getattr(settings, "DEBUG", False)))
        if sms_dev_echo:
            resp_data["code"] = verification_code

        return Response(
            {"success": True, "message": "验证码发送成功", "data": resp_data},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        logger.error(f"发送验证码失败: {str(e)}")
        return _response_error("发送失败，请稍后重试", status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        user = getattr(request, "user", None)
        if not user or not (
            getattr(user, "is_superuser", False)
            or getattr(user, "is_staff", False)
            or getattr(user, "is_admin", False)
        ):
            return _response_error("需要管理员权限", status.HTTP_403_FORBIDDEN)

        data, error_resp = _parse_request_data(request, "审批验证码")
        if error_resp is not None:
            return error_resp

        phone = str((data or {}).get("phone") or "").strip()
        code = str((data or {}).get("code") or "").strip()

        if not phone or not code:
            return _response_error("手机号和验证码均为必填", status.HTTP_400_BAD_REQUEST)

        cache_key = f"sms:code:{phone}"
        cached_code = _cache_get_with_session_fallback(request, cache_key)
        if not cached_code:
            return _response_error("验证码不存在或已过期", status.HTTP_404_NOT_FOUND)
        if str(cached_code) != str(code):
            return _response_error("验证码不匹配", status.HTTP_400_BAD_REQUEST)

        approved_key = f"sms:approved:{phone}:{code}"
        ttl = int(getattr(settings, "SMS_CODE_TTL", 300))
        _cache_set_with_session_fallback(request, approved_key, 1, ttl)

        logger.info(
            f"管理员({getattr(request.user, 'username', 'admin')})已审批验证码: phone={_mask_phone(phone)}"
        )

        return Response(
            {"success": True, "message": "已审批，验证码现在有效"}, status=status.HTTP_200_OK
        )
    except Exception:
        logger.exception("审批验证码失败")
        return _response_error("审批失败，请稍后重试", status.HTTP_500_INTERNAL_SERVER_ERROR)
