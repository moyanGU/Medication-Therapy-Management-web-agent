from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MTMServiceCaseViewSet

router = DefaultRouter()
router.register(r"service-cases", MTMServiceCaseViewSet, basename="mtm-service-case")

urlpatterns = [
    path("", include(router.urls)),
]
