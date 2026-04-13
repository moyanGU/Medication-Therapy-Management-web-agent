import os
import uuid

from django.conf import settings
from django.core.files.storage import default_storage
import logging
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.response import APIResponse

logger = logging.getLogger(__name__)

ALLOWED_IMAGE_CONTENT_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/heic",
    "image/heif",
    "image/bmp",
}

ALLOWED_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".heic",
    ".heif",
    ".bmp",
}


def _load_image_module():
    from PIL import Image

    return Image


class ImageUploadView(APIView):
    """
    图片上传API
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        """
        上传图片文件
        """
        try:
            # 获取上传的文件
            image_file = request.FILES.get("image")
            if not image_file:
                logger.warning("图片上传失败：缺少 image 文件字段")
                return APIResponse.error(
                    message="请选择要上传的图片文件", status_code=status.HTTP_400_BAD_REQUEST
                )

            # 验证文件类型
            content_type = (image_file.content_type or "").lower()
            extension = os.path.splitext(image_file.name or "")[1].lower()
            if (
                content_type not in ALLOWED_IMAGE_CONTENT_TYPES
                and extension not in ALLOWED_IMAGE_EXTENSIONS
            ):
                logger.warning(
                    "图片上传失败：不支持的文件类型",
                    extra={
                        "file_name": image_file.name,
                        "content_type": content_type,
                        "extension": extension,
                    },
                )
                return APIResponse.error(
                    message="只支持 JPG、PNG、GIF、WEBP、HEIC、HEIF、BMP 格式的图片",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            # 验证文件大小（限制为5MB）
            max_size = 5 * 1024 * 1024  # 5MB
            if image_file.size > max_size:
                logger.warning(
                    "图片上传失败：文件大小超限",
                    extra={"file_name": image_file.name, "file_size": image_file.size},
                )
                return APIResponse.error(
                    message="图片文件大小不能超过5MB", status_code=status.HTTP_400_BAD_REQUEST
                )

            # 生成唯一文件名
            file_extension = os.path.splitext(image_file.name)[1]
            unique_filename = f"medicine_{uuid.uuid4().hex}{file_extension}"

            # 创建保存路径
            upload_path = f"medicines/images/{unique_filename}"

            # 保存文件
            saved_path = default_storage.save(upload_path, image_file)
            logger.info(
                "图片上传成功：文件已保存",
                extra={
                    "file_name": image_file.name,
                    "content_type": content_type,
                    "saved_path": saved_path,
                },
            )

            # 压缩图片（可选）
            self._compress_image(saved_path)

            # 返回文件路径
            return APIResponse.success(
                data={
                    "image_path": saved_path,
                    "image_url": f"{settings.MEDIA_URL}{saved_path}",
                },
                message="图片上传成功",
            )

        except Exception as e:
            logger.exception("图片上传异常")
            return APIResponse.error(
                message=f"图片上传失败：{str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _compress_image(self, image_path):
        """
        压缩图片（可选功能）
        """
        try:
            image_module = _load_image_module()
            full_path = os.path.join(settings.MEDIA_ROOT, image_path)
            with image_module.open(full_path) as img:
                # 如果图片宽度大于800px，则压缩
                if img.width > 800:
                    # 计算新的高度，保持宽高比
                    new_width = 800
                    new_height = int((new_width * img.height) / img.width)

                    # 重新调整大小
                    img_resized = img.resize(
                        (new_width, new_height), image_module.Resampling.LANCZOS
                    )

                    # 保存压缩后的图片
                    img_resized.save(full_path, optimize=True, quality=85)
        except Exception:
            # 如果压缩失败，不影响主要功能
            pass
