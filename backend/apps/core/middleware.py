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
        
        # 获取Authorization头
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        has_auth_header = bool(auth_header)
        token_type = ''
        token_preview = ''
        
        if auth_header:
            parts = auth_header.split(' ')
            if len(parts) == 2:
                token_type = parts[0]
                token_preview = parts[1][:20] + '...' if len(parts[1]) > 20 else parts[1]
        
        # 尝试进行JWT认证验证
        jwt_auth_result = 'Not attempted'
        jwt_user = 'Unknown'
        
        if has_auth_header and token_type.lower() == 'bearer':
            try:
                jwt_auth = JWTAuthentication()
                validated_token = jwt_auth.get_validated_token(auth_header.split(' ')[1])
                user = jwt_auth.get_user(validated_token)
                jwt_auth_result = 'Success'
                jwt_user = user.username if user else 'None'
                logger.info(f"🟢 [Auth Middleware] JWT认证成功 - 用户: {jwt_user}")
            except (InvalidToken, TokenError) as e:
                jwt_auth_result = f'Failed: {str(e)}'
                logger.error(f"🔴 [Auth Middleware] JWT认证失败: {str(e)}")
            except Exception as e:
                jwt_auth_result = f'Error: {str(e)}'
                logger.error(f"🔴 [Auth Middleware] JWT认证异常: {str(e)}")
        
        # 记录详细的请求信息
        logger.info(
            f"🔵 [Request] API请求开始: {request.method} {request.get_full_path()} - "
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
        
        # 尝试从缓存获取响应（对Redis异常容错）
        try:
            cached_response = cache.get(cache_key)
        except Exception as e:
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
            except (json.JSONDecodeError, AttributeError) as e:
                logger.warning(f"缓存解析失败: {e}")
                return response
            
            # 设置缓存（对Redis异常容错）
            try:
                cache.set(cache_key, cache_data, self.cache_timeout)
                logger.debug(f"设置缓存: {cache_key}")
            except Exception as e:
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
        
        # 获取当前请求计数（对Redis异常容错）
        try:
            current_requests = cache.get(rate_key, 0)
        except Exception as e:
            logger.warning(f"[RateLimit] 读取计数失败，降级放行: {e}")
            return None
        
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
        
        # 增加请求计数（对Redis异常容错）
        try:
            cache.set(rate_key, current_requests + 1, self.rate_window)
        except Exception as e:
            logger.warning(f"[RateLimit] 写入计数失败(已忽略): {e}")
        
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