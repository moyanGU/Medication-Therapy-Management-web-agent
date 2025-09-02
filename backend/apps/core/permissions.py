from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    自定义权限：只有对象的所有者才能编辑它
    """
    
    def has_object_permission(self, request, view, obj):
        # 读取权限允许任何请求
        # 所以我们总是允许GET、HEAD或OPTIONS请求
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 写入权限只给对象的所有者
        return obj.user == request.user


class IsOwner(permissions.BasePermission):
    """
    自定义权限：只有对象的所有者才能访问
    """
    
    def has_object_permission(self, request, view, obj):
        # 只有对象的所有者才能访问
        return obj.user == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    自定义权限：只有管理员才能编辑，其他用户只读
    """
    
    def has_permission(self, request, view):
        # 读取权限允许任何已认证用户
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # 写入权限只给管理员
        return request.user and request.user.is_staff


class IsAuthenticatedOwner(permissions.BasePermission):
    """
    自定义权限：已认证用户只能访问自己的对象
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user