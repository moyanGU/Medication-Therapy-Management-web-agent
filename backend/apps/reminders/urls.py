from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReminderViewSet
from .history_views import ReminderHistoryViewSet, ReminderStatsViewSet

router = DefaultRouter()
router.register(r'reminders', ReminderViewSet, basename='reminder')
router.register(r'reminder-history', ReminderHistoryViewSet, basename='reminder-history')
router.register(r'reminder-stats', ReminderStatsViewSet, basename='reminder-stats')

urlpatterns = [
    path('', include(router.urls)),
]