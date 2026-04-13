from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MedicationPlanViewSet

router = DefaultRouter()
router.register(r"", MedicationPlanViewSet, basename="plans")

urlpatterns = [
    path("", include(router.urls)),
]

# 用药计划API路由：
# GET /api/plans/ - 获取计划列表（搜索/筛选/排序/分页）
# POST /api/plans/ - 创建计划
# GET /api/plans/{id}/ - 计划详情
# PUT/PATCH /api/plans/{id}/ - 更新计划
# DELETE /api/plans/{id}/ - 删除计划
