from rest_framework import status
from rest_framework.response import Response


class APIResponse:
    """
    统一API响应格式
    """

    @staticmethod
    def success(data=None, message="操作成功", status_code=status.HTTP_200_OK):
        """
        成功响应
        """
        response_data = {"success": True, "message": message, "data": data}
        return Response(response_data, status=status_code)

    @staticmethod
    def error(message="操作失败", errors=None, status_code=status.HTTP_400_BAD_REQUEST):
        """
        错误响应
        """
        response_data = {"success": False, "message": message, "errors": errors}
        return Response(response_data, status=status_code)

    @staticmethod
    def not_found(message="资源不存在"):
        """
        404响应
        """
        return APIResponse.error(message=message, status_code=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def unauthorized(message="未授权访问"):
        """
        401响应
        """
        return APIResponse.error(
            message=message, status_code=status.HTTP_401_UNAUTHORIZED
        )

    @staticmethod
    def forbidden(message="禁止访问"):
        """
        403响应
        """
        return APIResponse.error(message=message, status_code=status.HTTP_403_FORBIDDEN)

    @staticmethod
    def server_error(message="服务器内部错误"):
        """
        500响应
        """
        return APIResponse.error(
            message=message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# 兼容旧版本的函数式API
def success_response(data=None, message="操作成功", status_code=status.HTTP_200_OK):
    """
    成功响应（函数式API）
    """
    return APIResponse.success(data=data, message=message, status_code=status_code)


def error_response(
    message="操作失败", errors=None, status_code=status.HTTP_400_BAD_REQUEST
):
    """
    错误响应（函数式API）
    """
    return APIResponse.error(message=message, errors=errors, status_code=status_code)
