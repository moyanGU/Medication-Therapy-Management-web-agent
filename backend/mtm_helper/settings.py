"""Django settings for mtm_helper project."""

import os
import socket
import sys
from datetime import timedelta
from pathlib import Path

from corsheaders.defaults import default_headers
from django.core.exceptions import ImproperlyConfigured
from dotenv import dotenv_values, load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

_env_file = BASE_DIR / ".env"
if _env_file.exists():
    load_dotenv(dotenv_path=_env_file)

    if os.getenv("DEBUG", "True").lower() == "true":
        _vals = dotenv_values(_env_file)

        if os.getenv("DB_USER") == "monitor":
            _db_user = _vals.get("DB_USER")
            _db_password = _vals.get("DB_PASSWORD")
            if _db_user:
                os.environ["DB_USER"] = _db_user
            if _db_password:
                os.environ["DB_PASSWORD"] = _db_password

        _redis_password = _vals.get("REDIS_PASSWORD")
        if _redis_password is None:
            _redis_password = ""
        if os.getenv("REDIS_PASSWORD") != _redis_password:
            os.environ["REDIS_PASSWORD"] = _redis_password
else:
    load_dotenv()

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-change-me-in-production")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# 规范化 ALLOWED_HOSTS（逗号分隔 + 去空白）
# 默认包含本机与 api.mtm-helper.com，生产环境建议通过环境变量 ALLOWED_HOSTS 明确设置域名白名单
ALLOWED_HOSTS = [
    h.strip()
    for h in os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,api.mtm-helper.com").split(
        ","
    )
    if h.strip()
]

# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "django_extensions",
    "django_filters",
    "drf_spectacular",
]

LOCAL_APPS = [
    "apps.authentication",
    "apps.users",
    "apps.medicines",
    "apps.records",
    "apps.reminders",
    "apps.plans",
    "apps.medical_records",
    "apps.mtm",
    "apps.core",
    "apps.audit",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "apps.core.middleware.SecurityHeadersMiddleware",
    "apps.core.middleware.RateLimitMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "apps.audit.middleware.AuditMiddleware",
    "apps.core.middleware.RequestLoggingMiddleware",
    "apps.core.middleware.CacheMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "mtm_helper.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "mtm_helper.wsgi.application"

# Database
# Connection recycling seconds for persistent connections
DB_CONN_MAX_AGE = int(os.getenv("DB_CONN_MAX_AGE", "0" if DEBUG else "120"))
# MySQL connection/read/write timeouts (seconds)
DB_CONNECT_TIMEOUT = int(os.getenv("DB_CONNECT_TIMEOUT", "5"))
DB_READ_TIMEOUT = int(os.getenv("DB_READ_TIMEOUT", "15"))
DB_WRITE_TIMEOUT = int(os.getenv("DB_WRITE_TIMEOUT", str(DB_READ_TIMEOUT)))
# Redis 连接池与超时（生产默认更保守，环境变量可覆盖）
REDIS_POOL_MAX_CONNECTIONS = int(
    os.getenv("REDIS_POOL_MAX_CONNECTIONS", "50" if DEBUG else "100")
)
REDIS_SOCKET_CONNECT_TIMEOUT = float(os.getenv("REDIS_SOCKET_CONNECT_TIMEOUT", "2"))
REDIS_SOCKET_TIMEOUT = float(os.getenv("REDIS_SOCKET_TIMEOUT", "2"))
# 运行期Redis异常聚合告警参数（可通过环境变量覆盖）
REDIS_ERROR_ALERT_WINDOW_SECONDS = int(
    os.getenv("REDIS_ERROR_ALERT_WINDOW_SECONDS", "60")
)
REDIS_ERROR_ALERT_THRESHOLD = int(os.getenv("REDIS_ERROR_ALERT_THRESHOLD", "8"))
REDIS_ERROR_ALERT_COOLDOWN_SECONDS = int(
    os.getenv("REDIS_ERROR_ALERT_COOLDOWN_SECONDS", "120")
)
# 统一缓存默认TTL与Key前缀，避免跨环境键冲突（生产可通过环境变量覆盖）
CACHE_DEFAULT_TTL = int(os.getenv("CACHE_DEFAULT_TTL", "300"))
REDIS_KEY_PREFIX = os.getenv("REDIS_KEY_PREFIX", "mtm-helper")
# Redis 值压缩开关（生产默认启用 zlib 压缩）
REDIS_ENABLE_COMPRESSION = (
    os.getenv("REDIS_ENABLE_COMPRESSION", "true" if not DEBUG else "false").lower()
    == "true"
)


# 新增：Redis连接字符串构造函数，兼容IPv6地址（自动加方括号）
def build_redis_location(host: str, port: str, pwd: str | None) -> str:
    """
    构建Redis连接字符串，兼容IPv6地址。
    - 当host包含":"且不以"["开头时，自动加方括号，例如::1 -> [::1]
    - 根据是否提供密码生成 redis://:{pwd}@host:port/0 或 redis://host:port/0
    """
    host_fmt = host
    try:
        if host and (":" in host) and not host.startswith("["):
            host_fmt = f"[{host}]"
    except Exception:
        host_fmt = host
    if pwd:
        return f"redis://:{pwd}@{host_fmt}:{port}/0"
    return f"redis://{host_fmt}:{port}/0"


def get_db_host():
    host = os.getenv("DB_HOST", "db-prod.mtm-helper.com")
    private_override = os.getenv("DB_HOST_PRIVATE")
    try:
        ip = socket.gethostbyname(host)
        is_private = (
            ip.startswith("10.") or ip.startswith("172.") or ip.startswith("192.168.")
        )
        print(f"[DB_HOST] 解析 {host} -> {ip} (private={is_private})")
        if not DEBUG and not is_private and private_override:
            host = private_override
            try:
                ip2 = socket.gethostbyname(host)
                is_private2 = (
                    ip2.startswith("10.")
                    or ip2.startswith("172.")
                    or ip2.startswith("192.168.")
                )
                print(f"[DB_HOST] 使用内网优先 {host} -> {ip2} (private={is_private2})")
            except Exception as e2:
                print(f"⚠️ DB_HOST_PRIVATE解析失败: {host}, {e2}")
    except Exception as e:
        print(f"⚠️ DB_HOST解析失败: {host}, {e}")
        if DEBUG:
            host = "localhost"
    return host


IS_TESTING = (
    os.getenv("PYTEST_CURRENT_TEST") is not None
    or "pytest" in sys.modules
    or any(arg for arg in sys.argv if arg in ("test", "pytest", "py.test"))
)

DB_USER_ENV = os.getenv("DB_USER")
DB_PASSWORD_ENV = os.getenv("DB_PASSWORD")
if not IS_TESTING and (not DB_USER_ENV or not DB_PASSWORD_ENV):
    print("❌ 缺少必需的数据库环境变量：DB_USER/DB_PASSWORD。为安全起见不再提供默认 root 用户，请在 .env 中配置强口令用户。")
    raise ImproperlyConfigured("Missing DB_USER or DB_PASSWORD environment variables.")

if IS_TESTING:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.getenv("DB_NAME", "mtm_helper"),
            "USER": DB_USER_ENV,
            "PASSWORD": DB_PASSWORD_ENV,
            "HOST": get_db_host(),
            "PORT": os.getenv("DB_PORT", "3306"),
            "CONN_MAX_AGE": DB_CONN_MAX_AGE,
            "CONN_HEALTH_CHECKS": True,
            "OPTIONS": {
                "charset": "utf8mb4",
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
                "connect_timeout": DB_CONNECT_TIMEOUT,
                "read_timeout": DB_READ_TIMEOUT,
                "write_timeout": DB_WRITE_TIMEOUT,
            },
        }
    }

# Optional MySQL SSL
if os.getenv("DB_USE_SSL", "false").lower() == "true":
    ssl_ca = os.getenv("DB_SSL_CA")
    # Only add SSL options when CA is provided to avoid driver errors
    if ssl_ca:
        DATABASES["default"]["OPTIONS"]["ssl"] = {"ca": ssl_ca}

# Redis Cache
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        # 默认值只用于本地开发；生产必须通过环境变量覆盖，且默认不再提供明文密码
        "LOCATION": build_redis_location(
            os.getenv("REDIS_HOST", "localhost"),
            os.getenv("REDIS_PORT", "6379"),
            os.getenv("REDIS_PASSWORD"),
        ),
        "KEY_PREFIX": REDIS_KEY_PREFIX,
        "TIMEOUT": CACHE_DEFAULT_TTL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": REDIS_POOL_MAX_CONNECTIONS,
                "retry_on_timeout": True,
            },
            "SOCKET_CONNECT_TIMEOUT": REDIS_SOCKET_CONNECT_TIMEOUT,
            "SOCKET_TIMEOUT": REDIS_SOCKET_TIMEOUT,
            # 使用 JSON 序列化，避免 pickle 带来的安全风险
            "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
            # 启用 zlib 压缩以减少内存占用（生产默认开启）。当未启用时使用 IdentityCompressor，避免 None 触发 import_string 错误
            "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor"
            if REDIS_ENABLE_COMPRESSION
            else "django_redis.compressors.identity.IdentityCompressor",
            # 忽略缓存异常以避免请求失败（生产推荐）
            "IGNORE_EXCEPTIONS": True,
        },
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom User Model
AUTH_USER_MODEL = "users.User"

# Django REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "EXCEPTION_HANDLER": "apps.core.exceptions.custom_exception_handler",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "MTM-用药助手 API",
    "DESCRIPTION": "MTM-用药助手服务端接口文档",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# JWT Settings
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=int(os.getenv("ACCESS_TOKEN_LIFETIME_MINUTES", "15"))
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=int(os.getenv("REFRESH_TOKEN_LIFETIME_DAYS", "7"))
    ),
    "ROTATE_REFRESH_TOKENS": os.getenv("ROTATE_REFRESH_TOKENS", "true").lower()
    == "true",
    "BLACKLIST_AFTER_ROTATION": os.getenv("BLACKLIST_AFTER_ROTATION", "true").lower()
    == "true",
    "UPDATE_LAST_LOGIN": os.getenv("UPDATE_LAST_LOGIN", "true").lower() == "true",
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

API_RATE_LIMIT = int(os.getenv("API_RATE_LIMIT", "100"))
API_RATE_WINDOW = int(os.getenv("API_RATE_WINDOW", "60"))
API_RATE_LIMIT_PER_USER = int(os.getenv("API_RATE_LIMIT_PER_USER", str(API_RATE_LIMIT)))
API_RATE_LIMIT_PER_PATH = int(os.getenv("API_RATE_LIMIT_PER_PATH", str(API_RATE_LIMIT)))

# CORS Settings
# 允许通过环境变量以逗号分隔的形式传入白名单，生产环境不回退到本地清单
# 示例：CORS_ALLOWED_ORIGINS=https://mtm-helper.com,https://admin.mtm-helper.com
#       CSRF_TRUSTED_ORIGINS=https://mtm-helper.com


def _csv_env(name: str, default_list: list[str] | None = None) -> list[str]:
    value = os.getenv(name)
    if value is not None and value.strip() != "":
        return [item.strip() for item in value.split(",") if item.strip()]
    return default_list or []


DEV_CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    # 预览端口 4173（vite preview）
    "http://localhost:4173",
    "http://127.0.0.1:4173",
    # 开发端口 5173、5174、5175
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:5175",
    "http://127.0.0.1:5175",
]
DEV_CSRF_TRUSTED_ORIGINS = DEV_CORS_ALLOWED_ORIGINS

# 统一CORS/CSRF配置读取，开发环境提供默认白名单，生产环境仅从环境变量读取
CORS_ALLOWED_ORIGINS = _csv_env(
    "CORS_ALLOWED_ORIGINS", DEV_CORS_ALLOWED_ORIGINS if DEBUG else []
)
CSRF_TRUSTED_ORIGINS = _csv_env(
    "CSRF_TRUSTED_ORIGINS", DEV_CSRF_TRUSTED_ORIGINS if DEBUG else []
)

CORS_ALLOW_CREDENTIALS = True
CORS_EXPOSE_HEADERS = ["X-Request-ID"]
CORS_ALLOW_HEADERS = list(default_headers) + ["x-request-id"]

# ---------------- Security & Proxy Settings (Production-safe defaults) ----------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
# 在生产默认开启 HTTPS 重定向，可通过环境变量关闭（如只在内网HTTP）
SECURE_SSL_REDIRECT = (
    os.getenv("SECURE_SSL_REDIRECT", "true" if not DEBUG else "false").lower() == "true"
)
# Cookie 安全策略（生产环境默认启用）
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
CSRF_COOKIE_SAMESITE = os.getenv("CSRF_COOKIE_SAMESITE", "Lax")
CSRF_COOKIE_HTTPONLY = True
# HSTS 与浏览器安全策略（仅生产）
SECURE_HSTS_SECONDS = int(
    os.getenv("SECURE_HSTS_SECONDS", "31536000" if not DEBUG else "0")
)
SECURE_HSTS_INCLUDE_SUBDOMAINS = (
    os.getenv(
        "SECURE_HSTS_INCLUDE_SUBDOMAINS", "true" if not DEBUG else "false"
    ).lower()
    == "true"
)
SECURE_HSTS_PRELOAD = (
    os.getenv("SECURE_HSTS_PRELOAD", "true" if not DEBUG else "false").lower() == "true"
)
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = os.getenv("X_FRAME_OPTIONS", "DENY")
# Align with Nginx default for better privacy while preserving analytics
SECURE_REFERRER_POLICY = os.getenv(
    "SECURE_REFERRER_POLICY", "strict-origin-when-cross-origin"
)
# 会话有效期（默认14天）与后端缓存化存储，提升性能
SESSION_COOKIE_AGE = int(os.getenv("SESSION_COOKIE_AGE", "1209600"))
SESSION_ENGINE = os.getenv(
    "SESSION_ENGINE",
    "django.contrib.sessions.backends.db"
    if DEBUG
    else "django.contrib.sessions.backends.cached_db",
)

CSP_DEFAULT_SRC = os.getenv("CSP_DEFAULT_SRC", "'self'")
CSP_SCRIPT_SRC = os.getenv("CSP_SCRIPT_SRC", "'self' 'unsafe-inline' 'unsafe-eval'")
CSP_STYLE_SRC = os.getenv("CSP_STYLE_SRC", "'self' 'unsafe-inline'")
CSP_IMG_SRC = os.getenv("CSP_IMG_SRC", "'self' data: https:")
CSP_FONT_SRC = os.getenv("CSP_FONT_SRC", "'self' data:")
CSP_CONNECT_SRC = os.getenv("CSP_CONNECT_SRC", "'self' https: wss:")
CSP_FRAME_ANCESTORS = os.getenv("CSP_FRAME_ANCESTORS", "'none'")
CSP_OBJECT_SRC = os.getenv("CSP_OBJECT_SRC", "'none'")
CSP_BASE_URI = os.getenv("CSP_BASE_URI", "'self'")
CSP_FORM_ACTION = os.getenv("CSP_FORM_ACTION", "'self'")
CSP_REPORT_ONLY = (
    os.getenv("CSP_REPORT_ONLY", "true" if DEBUG else "false").lower() == "true"
)

PERMISSIONS_POLICY = os.getenv(
    "PERMISSIONS_POLICY",
    "camera=(), microphone=(), geolocation=(), payment=(), usb=()",
)
CROSS_ORIGIN_OPENER_POLICY = os.getenv("CROSS_ORIGIN_OPENER_POLICY", "same-origin")
CROSS_ORIGIN_RESOURCE_POLICY = os.getenv("CROSS_ORIGIN_RESOURCE_POLICY", "same-origin")
# -------------------------------------------------------------------------------

# ---------------- Baichuan-M3 (OpenAI Compatible) ----------------
BAICHUAN_M3_ENABLED = os.getenv("BAICHUAN_M3_ENABLED", "true").lower() == "true"
BAICHUAN_M3_API_BASE_URL = os.getenv("BAICHUAN_M3_API_BASE_URL", "").strip()
BAICHUAN_M3_API_KEY = os.getenv("BAICHUAN_M3_API_KEY", "").strip()
BAICHUAN_M3_MODEL = os.getenv(
    "BAICHUAN_M3_MODEL", "baichuan-inc/Baichuan-M3-235B"
).strip()
BAICHUAN_M3_TIMEOUT_SECONDS = float(os.getenv("BAICHUAN_M3_TIMEOUT_SECONDS", "30"))
BAICHUAN_M3_MAX_OUTPUT_TOKENS = int(os.getenv("BAICHUAN_M3_MAX_OUTPUT_TOKENS", "1024"))
BAICHUAN_M3_CLASSIFIER_MAX_TOKENS = int(
    os.getenv("BAICHUAN_M3_CLASSIFIER_MAX_TOKENS", "256")
)
# -------------------------------------------------------------------------------

# Logging
# 日志级别与滚动策略可通过环境变量调控，避免单文件无限增长
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG" if DEBUG else "INFO")
CONSOLE_LOG_LEVEL = os.getenv("CONSOLE_LOG_LEVEL", "DEBUG" if DEBUG else "INFO")
# 模块定制日志级别：提醒相关模块可单独调到 DEBUG，便于观察调度细节
REMINDERS_LOG_LEVEL = os.getenv("REMINDERS_LOG_LEVEL", "DEBUG" if DEBUG else "INFO")
REMINDER_WORKER_LOG_LEVEL = os.getenv("REMINDER_WORKER_LOG_LEVEL", REMINDERS_LOG_LEVEL)
LOG_AUTH_TOKEN_PREVIEW = os.getenv("LOG_AUTH_TOKEN_PREVIEW", "false").lower() == "true"
API_SLOW_REQUEST_SECONDS = float(os.getenv("API_SLOW_REQUEST_SECONDS", "1.5"))
DB_LOG_SLOW_QUERY = os.getenv("DB_LOG_SLOW_QUERY", "false").lower() == "true"
DB_SLOW_QUERY_SECONDS = float(os.getenv("DB_SLOW_QUERY_SECONDS", "0.5"))
DB_SLOW_QUERY_MAX = int(os.getenv("DB_SLOW_QUERY_MAX", "20"))
DB_SLOW_QUERY_SQL_MAX_LEN = int(os.getenv("DB_SLOW_QUERY_SQL_MAX_LEN", "500"))
LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", str(10 * 1024 * 1024)))  # 10MB
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "7"))
DISABLE_FILE_LOG = os.getenv("DISABLE_FILE_LOG", "false").lower() == "true"
DISABLE_FILE_LOG = DISABLE_FILE_LOG or (
    len(sys.argv) > 1
    and sys.argv[1] in {"migrate", "makemigrations", "collectstatic", "createsuperuser"}
)
LOG_HANDLER_LIST = ["console"] if DISABLE_FILE_LOG else ["console", "file"]
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": LOG_LEVEL,
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "django.log",
            "formatter": "verbose",
            "maxBytes": LOG_MAX_BYTES,
            "backupCount": LOG_BACKUP_COUNT,
        },
        "console": {
            "level": CONSOLE_LOG_LEVEL,
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": LOG_HANDLER_LIST,
        "level": LOG_LEVEL,
    },
    "loggers": {
        "django": {
            "handlers": LOG_HANDLER_LIST,
            "level": LOG_LEVEL,
            "propagate": True,
        },
        "mtm_helper": {
            "handlers": LOG_HANDLER_LIST,
            "level": LOG_LEVEL,
            "propagate": False,
        },
        # 降低数据库SQL的日志噪音，如需查看SQL细节可改为 INFO/DEBUG
        "django.db.backends": {
            "handlers": LOG_HANDLER_LIST,
            "level": "WARNING",
            "propagate": False,
        },
        # 细化：提醒相关模块日志（apps.reminders.*）
        "apps.reminders": {
            "handlers": LOG_HANDLER_LIST,
            "level": REMINDERS_LOG_LEVEL,
            "propagate": False,
        },
        "apps.reminders.scheduler": {
            "handlers": LOG_HANDLER_LIST,
            "level": REMINDERS_LOG_LEVEL,
            "propagate": False,
        },
        "apps.reminders.management.commands.run_reminder_worker": {
            "handlers": LOG_HANDLER_LIST,
            "level": REMINDER_WORKER_LOG_LEVEL,
            "propagate": False,
        },
    },
}

# Create logs directory if it doesn't exist
os.makedirs(BASE_DIR / "logs", exist_ok=True)

# ---------------- SMS/Verification Settings ----------------
# 短信验证码有效期（秒），默认5分钟。生产环境请通过环境变量覆盖。
SMS_CODE_TTL = int(os.getenv("SMS_CODE_TTL", "300"))
# 发送频率限制（秒），同一手机号两次发送之间的最小间隔，默认60秒。
SMS_RATE_LIMIT_SECONDS = int(os.getenv("SMS_RATE_LIMIT_SECONDS", "60"))
# 开发环境是否在响应中回显验证码（仅用于联调与本地测试，生产务必设为False）
SMS_DEV_ECHO = os.getenv("SMS_DEV_ECHO", "true" if DEBUG else "false").lower() == "true"
# 短信模板占位（服务商未落地前用于统一格式化文案）
SMS_TEMPLATES = {
    "verification": os.getenv(
        "SMS_TEMPLATE_VERIFICATION", "【MTM用药助手】您的验证码是 {code}，{ttl} 分钟内有效。如非本人操作，请忽略本短信。"
    ),
    "reminder": os.getenv("SMS_TEMPLATE_REMINDER", "{message}"),
}
# 注册策略：是否需要管理员审批验证码后才能注册
# 默认保守：生产环境默认启用，开发环境默认关闭；可通过环境变量 REGISTRATION_REQUIRE_APPROVAL 覆盖
REGISTRATION_REQUIRE_APPROVAL = (
    os.getenv("REGISTRATION_REQUIRE_APPROVAL", "false" if DEBUG else "true").lower()
    == "true"
)
# -----------------------------------------------------------

# ---------------- Web Push / VAPID Settings ----------------
# VAPID 公钥与私钥用于服务端签发 Web Push 令牌。
# 请在 .env 中配置：
#   VAPID_PUBLIC_KEY  = Base64-URL 编码的公钥（与前端 VITE_VAPID_PUBLIC_KEY 保持一致）
#   VAPID_PRIVATE_KEY = PEM 或 JWK 格式的私钥字符串（pywebpush 支持 PEM）
#   VAPID_SUBJECT     = 联系方式（推荐 mailto:xxx@example.com）
VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY", "")
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY", "")
VAPID_SUBJECT = os.getenv("VAPID_SUBJECT", "mailto:noreply@mtm-helper.com")

if not VAPID_PRIVATE_KEY:
    print("⚠️ 缺少 VAPID_PRIVATE_KEY，Web Push 将不可用。请在 .env 中配置。")
# ------------------------------------------------------------

# ---------------- Spug Push Settings ----------------
# 是否启用Spug推送平台发送短信
SPUG_PUSH_ENABLED = os.getenv("SPUG_PUSH_ENABLED", "false").lower() == "true"
# Spug推送平台基础URL
SPUG_PUSH_URL = os.getenv("SPUG_PUSH_URL", "https://push.spug.cc")
# Spug模板ID（必须配置，否则不会发送）
SPUG_TEMPLATE_ID = os.getenv("SPUG_TEMPLATE_ID", "")
# Spug应用名称，用于模板中展示
SPUG_APP_NAME = os.getenv("SPUG_APP_NAME", "MTM用药助手")
# 新增：Spug授权令牌（如平台需要鉴权），为空则不携带Authorization头
SPUG_PUSH_TOKEN = os.getenv("SPUG_PUSH_TOKEN", "")
# 新增：Spug推送HTTP超时（秒），避免阻塞请求线程，建议 2-5 秒
SPUG_PUSH_TIMEOUT_SECONDS = int(os.getenv("SPUG_PUSH_TIMEOUT_SECONDS", "3"))
# 额外参数（JSON字符串），用于满足模板占位符需求，例如 {"code":"123456"}
SPUG_EXTRA_PARAMS_JSON = os.getenv("SPUG_EXTRA_PARAMS_JSON", "")
# 是否要求数字验证码及长度（部分验证码模板需要）
SPUG_REQUIRE_NUMERIC_CODE = (
    os.getenv("SPUG_REQUIRE_NUMERIC_CODE", "true").lower() == "true"
)
SPUG_CODE_LENGTH = int(os.getenv("SPUG_CODE_LENGTH", "6"))
# 模板区分：注册验证码与用药提醒可使用不同模板ID；未配置时回退到通用 SPUG_TEMPLATE_ID
SPUG_TEMPLATE_ID_VERIFICATION = os.getenv(
    "SPUG_TEMPLATE_ID_VERIFICATION", os.getenv("SPUG_TEMPLATE_ID", "")
)
SPUG_TEMPLATE_ID_REMINDER = os.getenv(
    "SPUG_TEMPLATE_ID_REMINDER", os.getenv("SPUG_TEMPLATE_ID", "")
)
SPUG_REMINDER_USE_SMS_ENDPOINT = (
    os.getenv("SPUG_REMINDER_USE_SMS_ENDPOINT", "true").lower() == "true"
)
SPUG_SMS_PARAM_TO = os.getenv("SPUG_SMS_PARAM_TO", "to")
SPUG_SMS_PARAM_MESSAGE = os.getenv("SPUG_SMS_PARAM_MESSAGE", "message")
# ---------------------------------------------------
