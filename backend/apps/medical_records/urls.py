from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MedicalRecordViewSet

# 创建路由器
router = DefaultRouter()
router.register(r"records", MedicalRecordViewSet, basename="medical-record")

# URL配置
urlpatterns = [
    # API路由
    path("", include(router.urls)),
    # 自定义路由（如果需要）
    # path('records/export/', MedicalRecordViewSet.as_view({'get': 'export_data'}), name='medical-record-export'),
]

# 应用名称
app_name = "medical_records"
