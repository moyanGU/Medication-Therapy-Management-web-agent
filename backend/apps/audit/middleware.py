import threading

_thread_locals = threading.local()


def get_current_request():
    """获取当前线程的请求对象"""
    return getattr(_thread_locals, 'request', None)


def get_current_user():
    """获取当前线程的用户对象"""
    request = get_current_request()
    if request:
        return getattr(request, 'user', None)
    return None


class AuditMiddleware:
    """
    审计日志中间件
    将当前请求对象存储在线程局部变量中，供 Signal 使用
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request
        response = self.get_response(request)
        # 清理线程局部变量
        if hasattr(_thread_locals, 'request'):
            del _thread_locals.request
        return response
