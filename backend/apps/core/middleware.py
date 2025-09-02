"""自定义中间件模块"""

import logging
import time
import json
from django.core.cache import cache
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

logger = logging.getLogger('mtm_helper')


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
        
        # 记录请求信息
        logger.info(
            f"API请求开始: {request.method} {request.get_full_path()} - "
            f"User: {getattr(request.user, 'username', 'Anonymous')} - "
            f"IP: {self._get_client_ip(request)}"
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
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # 记录响应信息
            logger.info(
                f"API请求完成: {request.method} {request.get_full_path()} - "
                f"Status: {response.status_code} - "
                f"Duration: {duration:.3f}s - "
                f"User: {getattr(request.user, 'username', 'Anonymous')}"
            )
        
        return response
    
    def _get_client_ip(self, request):
        """
        获取客户端IP地址
        
        Args:
            request: Django请求对象
            
        Returns:
            str: 客户端IP地址
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class CacheMiddleware(MiddlewareMixin):
    """
    缓存中间件
    为GET请求提供缓存功能
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.cache_timeout = getattr(settings, 'API_CACHE_TIMEOUT', 300)  # 默认5分钟
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
        if request.method != 'GET':
            return None
        
        # 跳过需要认证的请求
        if request.user.is_authenticated:
            return None
        
        # 生成缓存键
        cache_key = self._generate_cache_key(request)
        
        # 尝试从缓存获取响应
        cached_response = cache.get(cache_key)
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
        if (request.method == 'GET' and 
            response.status_code == 200 and 
            not request.user.is_authenticated):
            
            cache_key = self._generate_cache_key(request)
            
            try:
                # 尝试解析响应内容
                if hasattr(response, 'data'):
                    cache_data = response.data
                else:
                    cache_data = json.loads(response.content.decode('utf-8'))
                
                # 设置缓存
                cache.set(cache_key, cache_data, self.cache_timeout)
                logger.debug(f"设置缓存: {cache_key}")
                
            except (json.JSONDecodeError, AttributeError) as e:
                logger.warning(f"缓存设置失败: {e}")
        
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


class JWTAuthenticationMiddleware(MiddlewareMixin):
    """
    JWT认证中间件
    在请求处理前验证JWT令牌
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_auth = JWTAuthentication()
        super().__init__(get_response)
    
    def process_request(self, request):
        """
        处理请求，验证JWT令牌
        
        Args:
            request: Django请求对象
        """
        # 跳过不需要认证的路径
        if self._should_skip_auth(request):
            return None
        
        try:
            # 尝试从请求中获取用户
            auth_result = self.jwt_auth.authenticate(request)
            if auth_result:
                user, token = auth_result
                request.user = user
                request.auth = token
                logger.debug(f"JWT认证成功: {user.username}")
            
        except (InvalidToken, TokenError) as e:
            logger.warning(f"JWT认证失败: {e}")
            return JsonResponse({
                'success': False,
                'data': None,
                'message': '身份验证失败，请重新登录',
                'error_code': 'AUTHENTICATION_FAILED',
                'status_code': 401
            }, status=401)
        
        except Exception as e:
            logger.error(f"JWT认证异常: {e}")
            return JsonResponse({
                'success': False,
                'data': None,
                'message': '认证服务异常',
                'error_code': 'AUTHENTICATION_ERROR',
                'status_code': 500
            }, status=500)
        
        return None
    
    def _should_skip_auth(self, request):
        """
        判断是否应该跳过认证
        
        Args:
            request: Django请求对象
            
        Returns:
            bool: 是否跳过认证
        """
        # 跳过的路径列表
        skip_paths = [
            '/api/auth/login/',
            '/api/auth/register/',
            '/api/auth/refresh/',
            '/admin/',
            '/static/',
            '/media/',
            '/health/',
        ]
        
        path = request.path
        return any(path.startswith(skip_path) for skip_path in skip_paths)


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
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # 在生产环境中添加HSTS头
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """
    限流中间件
    基于IP地址的简单限流实现
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit = getattr(settings, 'API_RATE_LIMIT', 100)  # 每分钟100次请求
        self.rate_window = getattr(settings, 'API_RATE_WINDOW', 60)  # 时间窗口60秒
        super().__init__(get_response)
    
    def process_request(self, request):
        """
        处理请求，检查限流
        
        Args:
            request: Django请求对象
            
        Returns:
            HttpResponse or None: 限流响应或None
        """
        # 获取客户端IP
        client_ip = self._get_client_ip(request)
        
        # 生成限流键
        rate_key = f"rate_limit:{client_ip}"
        
        # 获取当前请求计数
        current_requests = cache.get(rate_key, 0)
        
        # 检查是否超过限制
        if current_requests >= self.rate_limit:
            logger.warning(f"IP {client_ip} 触发限流，当前请求数: {current_requests}")
            return JsonResponse({
                'success': False,
                'data': None,
                'message': f'请求过于频繁，请在{self.rate_window}秒后重试',
                'error_code': 'RATE_LIMIT_EXCEEDED',
                'status_code': 429
            }, status=429)
        
        # 增加请求计数
        cache.set(rate_key, current_requests + 1, self.rate_window)
        
        return None
    
    def _get_client_ip(self, request):
        """
        获取客户端IP地址
        
        Args:
            request: Django请求对象
            
        Returns:
            str: 客户端IP地址
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip