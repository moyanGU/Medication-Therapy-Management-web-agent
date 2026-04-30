from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from .models import AgentPermission
from .utils import success_response


@api_view(["GET"])
@permission_classes([AllowAny])
def agent_permission_matrix(request):
    permissions = AgentPermission.objects.all()
    matrix = {}
    for p in permissions:
        if p.role not in matrix:
            matrix[p.role] = {}
        matrix[p.role][p.action_type] = p.state

    return success_response(matrix, "获取成功")

