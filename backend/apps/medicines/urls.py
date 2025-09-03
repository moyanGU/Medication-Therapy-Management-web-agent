from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MedicineViewSet

# 创建路由器
router = DefaultRouter()
router.register(r'', MedicineViewSet, basename='medicine')

# URL配置
urlpatterns = [
    path('', include(router.urls)),
]

# 药品管理API路由说明：
# GET /api/medicines/ - 获取药品列表（支持搜索、筛选、分页）
# POST /api/medicines/ - 创建新药品
# GET /api/medicines/{id}/ - 获取单个药品详情
# PUT /api/medicines/{id}/ - 更新药品信息（完整更新）
# PATCH /api/medicines/{id}/ - 更新药品信息（部分更新）
# DELETE /api/medicines/{id}/ - 删除药品
# GET /api/medicines/expired/ - 获取已过期药品列表
# GET /api/medicines/low_stock/ - 获取库存不足药品列表
# GET /api/medicines/statistics/ - 获取药品统计信息
# POST /api/medicines/{id}/update_quantity/ - 更新药品库存数量