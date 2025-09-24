"""Django settings for mtm_helper project."""

import os
from pathlib import Path
from dotenv import load_dotenv
import socket

# Load environment variables
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-me-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# 规范化 ALLOWED_HOSTS（逗号分隔 + 去空白）
ALLOWED_HOSTS = [h.strip() for h in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if h.strip()]

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_extensions',
]

LOCAL_APPS = [
    'apps.authentication',
    'apps.users',
    'apps.medicines',
    'apps.records',
    'apps.reminders',
    'apps.plans',
    'apps.medical_records',
    'apps.core',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'apps.core.middleware.SecurityHeadersMiddleware',
    'apps.core.middleware.RateLimitMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'apps.core.middleware.RequestLoggingMiddleware',
    'apps.core.middleware.CacheMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mtm_helper.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mtm_helper.wsgi.application'

# Database
# Connection recycling seconds for persistent connections
DB_CONN_MAX_AGE = int(os.getenv('DB_CONN_MAX_AGE', '0'))
# MySQL connection/read/write timeouts (seconds)
DB_CONNECT_TIMEOUT = int(os.getenv('DB_CONNECT_TIMEOUT', '5'))
DB_READ_TIMEOUT = int(os.getenv('DB_READ_TIMEOUT', '15'))
DB_WRITE_TIMEOUT = int(os.getenv('DB_WRITE_TIMEOUT', str(DB_READ_TIMEOUT)))

def get_db_host():
    """
    返回数据库主机地址。
    优先使用环境变量 DB_HOST；若未设置，默认使用 RDS 内网域名 'db-prod.mtm-helper.com'。
    在非生产环境（DEBUG=True）且无法解析时，回退到 'localhost' 以防开发阻塞。
    同时打印解析结果，便于确认是否为内网地址（RFC1918）。
    """
    host = os.getenv('DB_HOST', 'db-prod.mtm-helper.com')
    try:
        ip = socket.gethostbyname(host)
        is_private = (
            ip.startswith('10.') or
            ip.startswith('172.') or
            ip.startswith('192.168.')
        )
        print(f"[DB_HOST] 解析 {host} -> {ip} (private={is_private})")
        # 如果是生产且解析到公网IP，给出告警
        if not DEBUG and not is_private:
            print("⚠️ 警告：DB_HOST解析到公网IP，请确认使用RDS内网域名并启用内网白名单。")
    except Exception as e:
        print(f"⚠️ DB_HOST解析失败: {host}, {e}")
        if DEBUG:
            host = 'localhost'
    return host

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'mtm_helper'),
        'USER': os.getenv('DB_USER', 'root'),
-        'PASSWORD': os.getenv('DB_PASSWORD', '{Ghp880218}.'),
+        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': get_db_host(),
        'PORT': os.getenv('DB_PORT', '3306'),
        'CONN_MAX_AGE': DB_CONN_MAX_AGE,
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            # Timeouts effective for PyMySQL/MySQLdb (PyMySQL installed_as_MySQLdb)
            'connect_timeout': DB_CONNECT_TIMEOUT,
            'read_timeout': DB_READ_TIMEOUT,
            'write_timeout': DB_WRITE_TIMEOUT,
        }
    }
}

# Optional MySQL SSL
if os.getenv('DB_USE_SSL', 'false').lower() == 'true':
    ssl_ca = os.getenv('DB_SSL_CA')
    # Only add SSL options when CA is provided to avoid driver errors
    if ssl_ca:
        DATABASES['default']['OPTIONS']['ssl'] = {'ca': ssl_ca}

# Redis Cache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        # 默认值仅用于本地开发；生产环境必须通过环境变量覆盖
        'LOCATION': f"redis://:{os.getenv('REDIS_PASSWORD', 'ghp880218')}@{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', '6379')}/0",
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            # 连接与操作超时，避免请求长期阻塞
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'SOCKET_CONNECT_TIMEOUT': 2,  # 连接超时秒
            'SOCKET_TIMEOUT': 2,          # 读写超时秒
        }
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'users.User'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'EXCEPTION_HANDLER': 'apps.core.exceptions.custom_exception_handler',
}

# JWT Settings
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# CORS Settings
# 允许通过环境变量以逗号分隔的形式传入白名单，生产环境不回退到本地清单
# 示例：CORS_ALLOWED_ORIGINS=https://mtm-helper.com,https://admin.mtm-helper.com
#       CSRF_TRUSTED_ORIGINS=https://mtm-helper.com

def _csv_env(name: str, default_list: list[str] | None = None) -> list[str]:
    value = os.getenv(name)
    if value is not None and value.strip() != '':
        return [item.strip() for item in value.split(',') if item.strip()]
    return (default_list or [])

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
CORS_ALLOWED_ORIGINS = _csv_env('CORS_ALLOWED_ORIGINS', DEV_CORS_ALLOWED_ORIGINS if DEBUG else [])
CSRF_TRUSTED_ORIGINS = _csv_env('CSRF_TRUSTED_ORIGINS', DEV_CSRF_TRUSTED_ORIGINS if DEBUG else [])

CORS_ALLOW_CREDENTIALS = True

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'mtm_helper': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Create logs directory if it doesn't exist
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# ---------------- SMS/Verification Settings ----------------
# 短信验证码有效期（秒），默认5分钟。生产环境请通过环境变量覆盖。
SMS_CODE_TTL = int(os.getenv('SMS_CODE_TTL', '300'))
# 发送频率限制（秒），同一手机号两次发送之间的最小间隔，默认60秒。
SMS_RATE_LIMIT_SECONDS = int(os.getenv('SMS_RATE_LIMIT_SECONDS', '60'))
# 开发环境是否在响应中回显验证码（仅用于联调与本地测试，生产务必设为False）
SMS_DEV_ECHO = os.getenv('SMS_DEV_ECHO', 'true' if DEBUG else 'false').lower() == 'true'
# 短信模板占位（服务商未落地前用于统一格式化文案）
SMS_TEMPLATES = {
    'verification': os.getenv('SMS_TEMPLATE_VERIFICATION', '【MTM用药助手】您的验证码是 {code}，{ttl} 分钟内有效。如非本人操作，请忽略本短信。'),
    'reminder': os.getenv('SMS_TEMPLATE_REMINDER', '【MTM用药助手】{title}：{message}')
}
# -----------------------------------------------------------

# ---------------- Spug Push Settings ----------------
# 是否启用Spug推送平台发送短信
SPUG_PUSH_ENABLED = os.getenv('SPUG_PUSH_ENABLED', 'false').lower() == 'true'
# Spug推送平台基础URL
SPUG_PUSH_URL = os.getenv('SPUG_PUSH_URL', 'https://push.spug.cc')
# Spug模板ID（必须配置，否则不会发送）
SPUG_TEMPLATE_ID = os.getenv('SPUG_TEMPLATE_ID', '')
# Spug应用名称，用于模板中展示
SPUG_APP_NAME = os.getenv('SPUG_APP_NAME', 'MTM用药助手')
# ---------------------------------------------------