from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MTMFollowUpViewSet, MTMServiceCaseViewSet

router = DefaultRouter()
router.register(r"service-cases", MTMServiceCaseViewSet, basename="mtm-service-case")
router.register(r"follow-ups", MTMFollowUpViewSet, basename="mtm-follow-up")

urlpatterns = [
    path("", include(router.urls)),
]
