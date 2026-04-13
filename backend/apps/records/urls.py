from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MedicationRecordViewSet

# 创建路由器
router = DefaultRouter()
router.register(
    r"medication-records", MedicationRecordViewSet, basename="medication-record"
)

# URL配置
urlpatterns = [
    path("", include(router.urls)),
]

# 可用的API端点：
# GET /api/records/medication-records/ - 获取用药记录列表
# POST /api/records/medication-records/ - 创建用药记录
# GET /api/records/medication-records/{id}/ - 获取单个用药记录详情
# PUT /api/records/medication-records/{id}/ - 更新用药记录
# PATCH /api/records/medication-records/{id}/ - 部分更新用药记录
# DELETE /api/records/medication-records/{id}/ - 删除用药记录
# GET /api/records/medication-records/statistics/ - 获取统计信息
# GET /api/records/medication-records/trends/ - 获取趋势数据
# GET /api/records/medication-records/export/ - 导出数据
# GET /api/records/medication-records/recent/ - 获取最近记录
