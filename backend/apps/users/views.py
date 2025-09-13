from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserProfileSerializer

@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def profile(request):
    """
    当前登录用户的资料查询与更新
    GET  -> 返回当前用户资料
    PUT  -> 全量更新（仅允许可写字段）
    PATCH-> 部分更新
    """
    user = request.user

    if request.method == 'GET':
        serializer = UserProfileSerializer(user)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': '获取成功'
        })

    # 更新
    partial = (request.method == 'PATCH')
    serializer = UserProfileSerializer(user, data=request.data, partial=partial)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'success': True,
            'data': serializer.data,
            'message': '更新成功'
        })

    return Response({
        'success': False,
        'data': None,
        'message': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)