"""自定义中间件模块"""

import json
import logging
import re
import socket
import threading
import time
import uuid
from collections import deque
from urllib.parse import urlparse

import requests
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

logger = logging.getLogger("mtm_helper")

_redis_error_times = deque()
_redis_error_lock = threading.Lock()
_last_redis_alert_at = 0.0

_redis_probe_lock = threading.Lock()
_redis_probe_ok = True
_redis_probe_next_at = 0.0
_redis_probe_last_log_at = 0.0


def _is_redis_cache_backend() -> bool:
    backend = getattr(settings, "CACHES", {}).get("default", {}).get("BACKEND", "")
    return "django_redis" in str(backend)


def _parse_redis_host_port() -> tuple[str, int] | None:
    loc = getattr(settings, "CACHES", {}).get("default", {}).get("LOCATION")
    if isinstance(loc, (list, tuple)):
        if not loc:
            return None
        loc = loc[0]
    if not isinstance(loc, str) or not loc:
        return None
    try:
        parsed = urlparse(loc)
        host = parsed.hostname
        port = parsed.port
        if not host or not port:
            return None
        return host, int(port)
    except Exception:
        return None


def _redis_available() -> bool:
    global _redis_probe_ok
    global _redis_probe_next_at
    global _redis_probe_last_log_at

    if not _is_redis_cache_backend():
        return True

    now = time.time()
    if now < _redis_probe_next_at:
        return _redis_probe_ok

    with _redis_probe_lock:
        now2 = time.time()
        if now2 < _redis_probe_next_at:
            return _redis_probe_ok

        hp = _parse_redis_host_port()
        if not hp:
            _redis_probe_ok = False
            _redis_probe_next_at = now2 + 2.0
            return _redis_probe_ok

        host, port = hp
        ok = False
        try:
            with socket.create_connection((host, port), timeout=0.2):
                ok = True
        except Exception:
            ok = False

        prev_ok = _redis_probe_ok
        _redis_probe_ok = ok
        _redis_probe_next_at = now2 + (2.0 if not ok else 5.0)

        if (prev_ok != ok) or (not ok and (now2 - _redis_probe_last_log_at) >= 30.0):
            _redis_probe_last_log_at = now2
            if ok:
                logger.info("[RedisProbe] Redis 连接恢复，可重新启用缓存/限流")
            else:
                logger.warning("[RedisProbe] Redis 不可用，缓存/限流将降级跳过")

        return _redis_probe_ok


def _mask_redis_location():
    """
    返回脱敏后的Redis连接信息（不包含密码）。
    """
    try:
        loc = getattr(settings, "CACHES", {}).get("default", {}).get("LOCATION")
        if isinstance(loc, str) and "@" in loc:
            # 形如 redis://:pwd@host:port/0 → redis://****@host:port/0
            right = loc.split("@", 1)[1]
            return f"redis://****@{right}"
        return str(loc)
    except Exception:
        return "unknown"


def _notify_spug_alert(
    op: str, count: int, window: int, threshold: int, cooldown: int, masked_loc: str
) -> None:
    """
    向 Spug 推送 Redis 聚合告警（可选，需开启配置）。
    为避免引入不必要的风险，推送失败不会影响业务流程，仅记录日志。

    Args:
        op: 操作类型（如 'get' 或 'set'）
        count: 窗口内异常次数
        window: 时间窗口（秒）
        threshold: 告警阈值
        cooldown: 冷却时间（秒）
        masked_loc: 脱敏后的 Redis 连接信息
    """
    try:
        if not getattr(settings, "SPUG_PUSH_ENABLED", False):
            return
        template_id = getattr(settings, "SPUG_TEMPLATE_ID", "")
        base_url = getattr(settings, "SPUG_PUSH_URL", "")
        app_name = getattr(settings, "SPUG_APP_NAME", "MTM用药助手")
        token = getattr(settings, "SPUG_PUSH_TOKEN", "")
        timeout = int(getattr(settings, "SPUG_PUSH_TIMEOUT_SECONDS", 3))
        if not template_id or not base_url:
            logger.debug("[SpugPush] 未配置模板或URL，跳过推送。")
            return
        payload = {
            "template_id": template_id,
            "title": f"{app_name} Redis异常聚合告警",
            "content": {
                "op": op,
                "count": count,
                "window_seconds": window,
                "threshold": threshold,
                "cooldown_seconds": cooldown,
                "redis_location_masked": masked_loc,
                "pool_max": getattr(settings, "REDIS_POOL_MAX_CONNECTIONS", "unknown"),
                "connect_timeout": getattr(
                    settings, "REDIS_SOCKET_CONNECT_TIMEOUT", "unknown"
                ),
                "socket_timeout": getattr(settings, "REDIS_SOCKET_TIMEOUT", "unknown"),
                "key_prefix": getattr(settings, "REDIS_KEY_PREFIX", "mtm-helper"),
            },
        }
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        url = f"{base_url.rstrip('/')}/api/push"
        resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
        if resp.status_code >= 300:
            logger.warning(
                f"[SpugPush] 发送失败: status={resp.status_code}, body={resp.text[:200]}"
            )
        else:
            logger.info(f"[SpugPush] 已发送Redis聚合告警，返回: {resp.text[:200]}")
    except Exception as e:
        logger.warning(f"[SpugPush] 推送异常(已忽略): {e}")


def _inc_redis_error(op: str, exc: Exception):
    """
    记录一次Redis异常，并在达到阈值时输出聚合告警。
    Args:
        op: 操作类型，如 'get' 或 'set'
        exc: 捕获的异常对象
    """
    global _last_redis_alert_at
    now = time.time()
    window = getattr(settings, "REDIS_ERROR_ALERT_WINDOW_SECONDS", 60)
    threshold = getattr(settings, "REDIS_ERROR_ALERT_THRESHOLD", 8)
    cooldown = getattr(settings, "REDIS_ERROR_ALERT_COOLDOWN_SECONDS", 120)
    # 入队并清理窗口外事件
    with _redis_error_lock:
        _redis_error_times.append(now)
        while _redis_error_times and (now - _redis_error_times[0]) > window:
            _redis_error_times.popleft()
        count = len(_redis_error_times)
    # 仅在达到阈值且冷却时间已过时输出聚合告警（避免日志风暴）
    if count >= threshold and (now - _last_redis_alert_at) >= cooldown:
        _last_redis_alert_at = now
        masked_loc = _mask_redis_location()
        logger.error(
            f"🔴 [CacheMiddleware][Redis异常聚合告警] 最近{window}s内捕获到{count}次Redis异常(阈值={threshold}, 操作={op})；"
            f"连接(脱敏)：{masked_loc}，POOL_MAX={getattr(settings, 'REDIS_POOL_MAX_CONNECTIONS', 'unknown')}, "
            f"CONNECT_TIMEOUT={getattr(settings, 'REDIS_SOCKET_CONNECT_TIMEOUT', 'unknown')}, "
            f"SOCKET_TIMEOUT={getattr(settings, 'REDIS_SOCKET_TIMEOUT', 'unknown')}, "
            f"KEY_PREFIX={getattr(settings, 'REDIS_KEY_PREFIX', 'mtm-helper')}")
        # 可选推送至 Spug
        _notify_spug_alert(op, count, window, threshold, cooldown, masked_loc)


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    请求日志中间件
    记录所有API请求的详细信息
    """

    def process_request(self, request):
        """
        处理请求开始时的逻辑

        Args:
            request: Django请求对象
        """
        request.start_time = time.time()
        request.force_debug_cursor = False
        request.request_id = self._resolve_request_id(request)

        if getattr(settings, "DB_LOG_SLOW_QUERY", False):
            try:
                from django.db import connection

                connection.force_debug_cursor = True
                request.force_debug_cursor = True
            except Exception:
                request.force_debug_cursor = False

        # 获取Authorization头
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        has_auth_header = bool(auth_header)
        token_type = ""
        token_preview = ""

        if auth_header:
            parts = auth_header.split(" ")
            if len(parts) == 2:
                token_type = parts[0]
                if getattr(settings, "LOG_AUTH_TOKEN_PREVIEW", False):
                    token_preview = (
                        parts[1][:6] + "..." if len(parts[1]) > 6 else parts[1]
                    )

        # 尝试进行JWT认证验证
        jwt_auth_result = "Not attempted"
        jwt_user = "Unknown"

        if has_auth_header and token_type.lower() == "bearer":
            try:
                jwt_auth = JWTAuthentication()
                validated_token = jwt_auth.get_validated_token(
                    auth_header.split(" ")[1]
                )
                user = jwt_auth.get_user(validated_token)
                jwt_auth_result = "Success"
                jwt_user = user.username if user else "None"
                logger.info(f"🟢 [Auth Middleware] JWT认证成功 - 用户: {jwt_user}")
            except (InvalidToken, TokenError) as e:
                jwt_auth_result = f"Failed: {str(e)}"
                logger.error(f"🔴 [Auth Middleware] JWT认证失败: {str(e)}")
            except Exception as e:
                jwt_auth_result = f"Error: {str(e)}"
                logger.error(f"🔴 [Auth Middleware] JWT认证异常: {str(e)}")

        # 记录详细的请求信息
        logger.info(
            f"🔵 [Request] API请求开始: {request.method} {request.get_full_path()} - "
            f"Request ID: {request.request_id} - "
            f"User: {getattr(request.user, 'username', 'Anonymous')} - "
            f"IP: {self._get_client_ip(request)} - "
            f"Auth Header: {'Yes' if has_auth_header else 'No'} - "
            f"Token Type: {token_type} - "
            f"Token Preview: {token_preview} - "
            f"JWT Auth: {jwt_auth_result} - "
            f"JWT User: {jwt_user}"
        )

    def process_response(self, request, response):
        """
        处理响应时的逻辑

        Args:
            request: Django请求对象
            response: Django响应对象

        Returns:
            HttpResponse: 响应对象
        """
        request_id = getattr(request, "request_id", None)
        if request_id:
            response["X-Request-ID"] = request_id

        if hasattr(request, "start_time"):
            duration = time.time() - request.start_time

            # 记录响应信息
            logger.info(
                f"API请求完成: {request.method} {request.get_full_path()} - "
                f"Request ID: {request_id or 'unknown'} - "
                f"Status: {response.status_code} - "
                f"Duration: {duration:.3f}s - "
                f"User: {getattr(request.user, 'username', 'Anonymous')}"
            )

            slow_threshold = float(getattr(settings, "API_SLOW_REQUEST_SECONDS", 0))
            if slow_threshold > 0 and duration >= slow_threshold:
                logger.warning(
                    f"🟠 [SlowRequest] {request.method} {request.get_full_path()} - "
                    f"Request ID: {request_id or 'unknown'} - "
                    f"Status: {response.status_code} - "
                    f"Duration: {duration:.3f}s - "
                    f"User: {getattr(request.user, 'username', 'Anonymous')}"
                )

            if getattr(settings, "DB_LOG_SLOW_QUERY", False):
                try:
                    from django.db import connection

                    slow_query_seconds = float(
                        getattr(settings, "DB_SLOW_QUERY_SECONDS", 0)
                    )
                    max_items = int(getattr(settings, "DB_SLOW_QUERY_MAX", 20))
                    max_len = int(getattr(settings, "DB_SLOW_QUERY_SQL_MAX_LEN", 500))
                    if slow_query_seconds > 0:
                        slow_queries = []
                        for q in connection.queries:
                            try:
                                q_time = float(q.get("time", 0))
                            except Exception:
                                q_time = 0
                            if q_time >= slow_query_seconds:
                                sql = q.get("sql", "")
                                if max_len > 0 and len(sql) > max_len:
                                    sql = f"{sql[:max_len]}..."
                                slow_queries.append((q_time, sql))
                        if slow_queries:
                            slow_queries.sort(key=lambda x: x[0], reverse=True)
                            for q_time, sql in slow_queries[:max_items]:
                                logger.warning(
                                    f"🟠 [SlowQuery] {q_time:.3f}s {request.method} "
                                    f"{request.get_full_path()} - {sql}"
                                )
                except Exception as e:
                    logger.warning(f"🟠 [SlowQuery] 记录慢查询失败: {e}")
                finally:
                    try:
                        connection.force_debug_cursor = False
                    except Exception:
                        pass

        return response

    def _resolve_request_id(self, request):
        header_request_id = request.META.get("HTTP_X_REQUEST_ID", "")
        if isinstance(header_request_id, str) and header_request_id.strip():
            return header_request_id.strip()[:128]
        return str(uuid.uuid4())

    def _get_client_ip(self, request):
        """
        获取客户端IP地址

        Args:
            request: Django请求对象

        Returns:
            str: 客户端IP地址
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class CacheMiddleware(MiddlewareMixin):
    """
    缓存中间件
    为GET请求提供缓存功能
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.cache_timeout = getattr(settings, "API_CACHE_TIMEOUT", 300)  # 默认5分钟
        self.exclude_path_prefixes = tuple(
            getattr(
                settings,
                "API_CACHE_EXCLUDE_PATHS",
                [
                    "/api/health/",
                    "/api/ping/",
                    "/api/system-info/",
                    "/api/diagnostics/",
                    "/api/docs/",
                ],
            )
        )
        super().__init__(get_response)

    def process_request(self, request):
        """
        处理请求，检查缓存

        Args:
            request: Django请求对象

        Returns:
            HttpResponse or None: 缓存的响应或None
        """
        # 只缓存GET请求
        if request.method != "GET":
            return None

        request_path = getattr(request, "path", "") or ""
        if request_path and any(
            request_path.startswith(prefix) for prefix in self.exclude_path_prefixes
        ):
            return None

        # 跳过需要认证的请求
        if request.user.is_authenticated:
            return None

        # 生成缓存键
        cache_key = self._generate_cache_key(request)

        if not _redis_available():
            return None

        # 尝试从缓存获取响应（对Redis异常容错）
        try:
            cached_response = cache.get(cache_key)
        except Exception as e:
            _inc_redis_error("get", e)
            logger.warning(f"[CacheMiddleware] 缓存读取失败，将降级为直通请求: {e}")
            return None

        if cached_response:
            logger.debug(f"缓存命中: {cache_key}")
            return JsonResponse(cached_response)

        return None

    def process_response(self, request, response):
        """
        处理响应，设置缓存

        Args:
            request: Django请求对象
            response: Django响应对象

        Returns:
            HttpResponse: 响应对象
        """
        # 只缓存GET请求的成功响应
        request_path = getattr(request, "path", "") or ""
        if request_path and any(
            request_path.startswith(prefix) for prefix in self.exclude_path_prefixes
        ):
            return response

        if (
            request.method == "GET"
            and response.status_code == 200
            and not request.user.is_authenticated
        ):
            cache_key = self._generate_cache_key(request)

            if not _redis_available():
                return response

            try:
                # 尝试解析响应内容
                if hasattr(response, "data"):
                    cache_data = response.data
                else:
                    cache_data = json.loads(response.content.decode("utf-8"))
            except (json.JSONDecodeError, AttributeError) as e:
                logger.warning(f"缓存解析失败: {e}")
                return response

            # 设置缓存（对Redis异常容错）
            try:
                cache.set(cache_key, cache_data, self.cache_timeout)
                logger.debug(f"设置缓存: {cache_key}")
            except Exception as e:
                _inc_redis_error("set", e)
                logger.warning(f"[CacheMiddleware] 缓存写入失败(已忽略): {e}")

        return response

    def _generate_cache_key(self, request):
        """
        生成缓存键

        Args:
            request: Django请求对象

        Returns:
            str: 缓存键
        """
        path = request.get_full_path()
        return f"api_cache:{path}"


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    安全头中间件
    添加安全相关的HTTP头
    """

    def process_response(self, request, response):
        """
        处理响应，添加安全头

        Args:
            request: Django请求对象
            response: Django响应对象

        Returns:
            HttpResponse: 响应对象
        """
        # 添加安全头
        response["X-Content-Type-Options"] = "nosniff"
        response["X-Frame-Options"] = "DENY"
        response["X-XSS-Protection"] = "1; mode=block"
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response["Permissions-Policy"] = settings.PERMISSIONS_POLICY
        response["Cross-Origin-Opener-Policy"] = settings.CROSS_ORIGIN_OPENER_POLICY
        media_prefix = str(getattr(settings, "MEDIA_URL", "/media/") or "/media/")
        if not media_prefix.startswith("/"):
            media_prefix = f"/{media_prefix}"
        if request.path.startswith(media_prefix):
            response["Cross-Origin-Resource-Policy"] = "cross-origin"
        else:
            response["Cross-Origin-Resource-Policy"] = (
                settings.CROSS_ORIGIN_RESOURCE_POLICY
            )

        csp_parts = [
            f"default-src {settings.CSP_DEFAULT_SRC}",
            f"script-src {settings.CSP_SCRIPT_SRC}",
            f"style-src {settings.CSP_STYLE_SRC}",
            f"img-src {settings.CSP_IMG_SRC}",
            f"font-src {settings.CSP_FONT_SRC}",
            f"connect-src {settings.CSP_CONNECT_SRC}",
            f"frame-ancestors {settings.CSP_FRAME_ANCESTORS}",
            f"object-src {settings.CSP_OBJECT_SRC}",
            f"base-uri {settings.CSP_BASE_URI}",
            f"form-action {settings.CSP_FORM_ACTION}",
        ]
        csp_value = "; ".join(part for part in csp_parts if part)
        csp_header = (
            "Content-Security-Policy-Report-Only"
            if settings.CSP_REPORT_ONLY
            else "Content-Security-Policy"
        )
        response[csp_header] = csp_value

        # 在生产环境中添加HSTS头
        if not settings.DEBUG:
            response[
                "Strict-Transport-Security"
            ] = "max-age=31536000; includeSubDomains"

        return response


class RateLimitMiddleware(MiddlewareMixin):
    """
    限流中间件
    基于IP、用户与接口维度的限流实现
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit = getattr(settings, "API_RATE_LIMIT", 100)
        self.rate_limit_per_user = getattr(
            settings, "API_RATE_LIMIT_PER_USER", self.rate_limit
        )
        self.rate_limit_per_path = getattr(
            settings, "API_RATE_LIMIT_PER_PATH", self.rate_limit
        )
        self.rate_window = getattr(settings, "API_RATE_WINDOW", 60)
        super().__init__(get_response)

    def process_request(self, request):
        """
        处理请求，检查限流

        Args:
            request: Django请求对象

        Returns:
            HttpResponse or None: 限流响应或None
        """
        client_ip = self._get_client_ip(request)
        user_key = self._get_user_key(request)
        path_key = self._normalize_path(request.path)

        if not _redis_available():
            return None

        if self._is_rate_limited(f"rate_limit:ip:{client_ip}", self.rate_limit):
            logger.warning(f"[RateLimit] IP {client_ip} 触发限流，window={self.rate_window}")
            return self._rate_limit_response()

        if user_key and self._is_rate_limited(
            f"rate_limit:user:{user_key}", self.rate_limit_per_user
        ):
            logger.warning(f"[RateLimit] 用户 {user_key} 触发限流，window={self.rate_window}")
            return self._rate_limit_response()

        if path_key and self._is_rate_limited(
            f"rate_limit:path:{path_key}", self.rate_limit_per_path
        ):
            logger.warning(f"[RateLimit] 接口 {path_key} 触发限流，window={self.rate_window}")
            return self._rate_limit_response()

        return None

    def _is_rate_limited(self, rate_key, limit):
        """
        检查并更新指定维度的限流计数
        """
        try:
            current_requests = cache.get(rate_key, 0)
        except Exception as e:
            logger.warning(f"[RateLimit] 读取计数失败，降级放行: {e}")
            return False

        if current_requests >= limit:
            return True

        try:
            # 使用 incr 原子操作，如果键不存在则创建并设置过期时间
            if current_requests == 0:
                cache.add(rate_key, 1, self.rate_window)
            else:
                cache.incr(rate_key)
        except Exception as e:
            logger.warning(f"[RateLimit] 写入计数失败(已忽略): {e}")

        return False

    def _rate_limit_response(self):
        """
        返回限流响应
        """
        return JsonResponse(
            {
                "success": False,
                "data": None,
                "message": f"请求过于频繁，请在{self.rate_window}秒后重试",
                "error_code": "RATE_LIMIT_EXCEEDED",
                "status_code": 429,
            },
            status=429,
        )

    def _normalize_path(self, path):
        """
        标准化路径，降低动态参数对限流键的影响
        """
        if not path:
            return ""
        return re.sub(r"/\d+(?=/|$)", "/:id", path)

    def _get_user_key(self, request):
        """
        获取用户维度的限流键
        """
        user = getattr(request, "user", None)
        if user and getattr(user, "is_authenticated", False):
            return str(getattr(user, "id", ""))
        return ""

    def _get_client_ip(self, request):
        """
        获取客户端IP地址

        Args:
            request: Django请求对象

        Returns:
            str: 客户端IP地址
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
