"""核心应用视图"""

import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.db import connection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .utils import success_response, error_response

logger = logging.getLogger('mtm_helper')


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    健康检查接口
    检查系统各组件的运行状态
    
    Returns:
        Response: 健康检查结果
    """
    health_status = {
        'status': 'healthy',
        'timestamp': None,
        'services': {
            'database': 'unknown',
            'cache': 'unknown',
            'application': 'healthy'
        },
        'version': '1.0.0'
    }
    
    try:
        from datetime import datetime
        health_status['timestamp'] = datetime.now().isoformat()
        
        # 检查数据库连接
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                health_status['services']['database'] = 'healthy'
        except Exception as e:
            logger.error(f"数据库健康检查失败: {e}")
            health_status['services']['database'] = 'unhealthy'
            health_status['status'] = 'degraded'
        
        # 检查缓存连接
        try:
            cache.set('health_check', 'ok', 10)
            cache_result = cache.get('health_check')
            if cache_result == 'ok':
                health_status['services']['cache'] = 'healthy'
            else:
                health_status['services']['cache'] = 'unhealthy'
                health_status['status'] = 'degraded'
        except Exception as e:
            logger.error(f"缓存健康检查失败: {e}")
            health_status['services']['cache'] = 'unhealthy'
            health_status['status'] = 'degraded'
        
        # 如果所有服务都不健康，标记为不健康
        if all(service == 'unhealthy' for service in health_status['services'].values()):
            health_status['status'] = 'unhealthy'
        
        status_code = 200 if health_status['status'] == 'healthy' else 503
        
        return Response({
            'success': True,
            'data': health_status,
            'message': '健康检查完成'
        }, status=status_code)
        
    except Exception as e:
        logger.error(f"健康检查异常: {e}")
        return Response({
            'success': False,
            'data': {
                'status': 'unhealthy',
                'error': str(e)
            },
            'message': '健康检查失败'
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def system_info(request):
    """
    系统信息接口
    返回系统基本信息
    
    Returns:
        Response: 系统信息
    """
    try:
        import platform
        import sys
        from django import get_version
        
        from django.conf import settings
        
        system_info = {
            'application': {
                'name': 'MTM-用药助手',
                'version': '1.0.0',
                'environment': 'development' if settings.DEBUG else 'production'
            },
            'system': {
                'platform': platform.platform(),
                'python_version': sys.version,
                'django_version': get_version()
            },
            'database': {
                'engine': 'MySQL',
                'version': None
            },
            'cache': {
                'backend': 'Redis',
                'version': None
            }
        }
        
        # 获取数据库版本
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT VERSION()")
                db_version = cursor.fetchone()[0]
                system_info['database']['version'] = db_version
        except Exception as e:
            logger.warning(f"获取数据库版本失败: {e}")
        
        # 获取Redis版本
        try:
            import redis
            from django.conf import settings as django_settings
            
            # 从缓存配置中获取Redis连接信息
            cache_config = django_settings.CACHES['default']
            location = cache_config['LOCATION']
            
            # 解析Redis连接URL
            if location.startswith('redis://'):
                import re
                match = re.match(r'redis://(?::([^@]+)@)?([^:]+):([^/]+)/(.+)', location)
                if match:
                    password, host, port, db = match.groups()
                    r = redis.Redis(host=host, port=int(port), db=int(db), password=password)
                    redis_info = r.info()
                    system_info['cache']['version'] = redis_info.get('redis_version')
        except Exception as e:
            logger.warning(f"获取Redis版本失败: {e}")
        
        return success_response(system_info, '系统信息获取成功')
        
    except Exception as e:
        logger.error(f"获取系统信息异常: {e}")
        return error_response('系统信息获取失败', 'SYSTEM_INFO_ERROR', 500)


@csrf_exempt
@require_http_methods(["GET"])
def ping(request):
    """
    简单的ping接口
    用于快速检查服务是否可用
    
    Returns:
        JsonResponse: ping响应
    """
    from datetime import datetime
    
    return JsonResponse({
        'success': True,
        'data': {
            'message': 'pong',
            'timestamp': datetime.now().isoformat()
        },
        'message': '服务正常'
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def api_docs(request):
    """
    API文档接口
    返回API文档信息
    
    Returns:
        Response: API文档信息
    """
    docs_info = {
        'title': 'MTM-用药助手 API Documentation',
        'version': '1.0.0',
        'description': 'MTM-用药助手药品管理系统API文档',
        'base_url': request.build_absolute_uri('/api/'),
        'endpoints': {
            'authentication': {
                'login': 'POST /api/auth/login/',
                'register': 'POST /api/auth/register/',
                'refresh': 'POST /api/auth/refresh/',
                'logout': 'POST /api/auth/logout/'
            },
            # 与实际路由一致，使用 /api/user/profile/
            'user': {
                'profile': 'GET /api/user/profile/',
                'update_profile': 'PUT /api/user/profile/',
                'change_password': 'POST /api/user/change-password/'
            },
            'medicines': {
                'list': 'GET /api/medicines/',
                'create': 'POST /api/medicines/',
                'detail': 'GET /api/medicines/{id}/',
                'update': 'PUT /api/medicines/{id}/',
                'delete': 'DELETE /api/medicines/{id}/',
                'search': 'GET /api/medicines/search/'
            },
            # 修正 records 文档端点，准确反映 DRF Router 挂载的 medication-records 子路由
            'records': {
                'list': 'GET /api/records/medication-records/',
                'create': 'POST /api/records/medication-records/',
                'detail': 'GET /api/records/medication-records/{id}/',
                'update': 'PUT /api/records/medication-records/{id}/',
                'delete': 'DELETE /api/records/medication-records/{id}/',
                'statistics': 'GET /api/records/medication-records/statistics/',
                'trends': 'GET /api/records/medication-records/trends/',
                'export': 'GET /api/records/medication-records/export/',
                'recent': 'GET /api/records/medication-records/recent/'
            },
            'reminders': {
                'list': 'GET /api/reminders/',
                'create': 'POST /api/reminders/',
                'detail': 'GET /api/reminders/{id}/',
                'update': 'PUT /api/reminders/{id}/',
                'delete': 'DELETE /api/reminders/{id}/',
                'today': 'GET /api/reminders/today/',
                'stats': 'GET /api/reminders/stats/',
                'upcoming': 'GET /api/reminders/upcoming/'
            }
        }
    }
    # 统一返回格式：success/data/message
    return success_response(docs_info, 'API文档获取成功')


@api_view(['POST'])
def clear_cache(request):
    """
    清除缓存接口
    需要管理员权限
    
    Returns:
        Response: 清除结果
    """
    if not request.user.is_staff:
        return error_response('权限不足', 'PERMISSION_DENIED', 403)
    
    try:
        cache.clear()
        logger.info(f"管理员 {request.user.username} 清除了所有缓存")
        return success_response(None, '缓存清除成功')
    except Exception as e:
        logger.error(f"清除缓存失败: {e}")
        return error_response('缓存清除失败', 'CACHE_CLEAR_ERROR', 500)