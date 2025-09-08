from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Sum
from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Reminder
from .serializers import (
    ReminderSerializer,
    ReminderCreateSerializer,
    ReminderUpdateSerializer,
    ReminderListSerializer,
    ReminderStatsSerializer
)
from .filters import ReminderFilter
from .scheduler import ReminderScheduler
from .notifications import notification_service
from apps.core.pagination import StandardResultsSetPagination
from apps.core.permissions import IsOwnerOrReadOnly
import logging

logger = logging.getLogger(__name__)


class ReminderViewSet(viewsets.ModelViewSet):
    """
    提醒视图集
    提供提醒的CRUD操作和相关功能
    """
    serializer_class = ReminderSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ReminderFilter
    search_fields = ['title', 'message', 'medicine__name']
    ordering_fields = ['reminder_time', 'created_at', 'updated_at']
    ordering = ['reminder_time']
    
    def get_queryset(self):
        """
        获取当前用户的提醒
        """
        return Reminder.objects.filter(
            user=self.request.user
        ).select_related(
            'medicine',
            'user'
        ).order_by('reminder_time')
    
    def get_serializer_class(self):
        """
        根据动作选择序列化器
        """
        if self.action == 'create':
            return ReminderCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ReminderUpdateSerializer
        elif self.action == 'list':
            return ReminderListSerializer
        return ReminderSerializer
    
    def create(self, request, *args, **kwargs):
        """
        创建新的提醒
        """
        try:
            logger.info(f"用户 {request.user.username} 创建提醒，数据: {request.data}")
            
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            reminder = serializer.save()
            
            # 返回完整的提醒信息
            response_serializer = ReminderSerializer(reminder)
            
            logger.info(f"提醒创建成功，ID: {reminder.id}")
            return Response({
                'success': True,
                'message': '提醒创建成功',
                'data': response_serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"创建提醒失败: {str(e)}")
            return Response({
                'success': False,
                'message': f'创建提醒失败: {str(e)}',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def list(self, request, *args, **kwargs):
        """
        获取提醒列表
        """
        try:
            logger.info(f"用户 {request.user.username} 获取提醒列表")
            
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                # 分页响应统一使用分页器封装，results 为纯数组
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'success': True,
                'message': '获取提醒列表成功',
                'data': serializer.data
            })
            
        except Exception as e:
            logger.error(f"获取提醒列表失败: {str(e)}")
            return Response({
                'success': False,
                'message': f'获取提醒列表失败: {str(e)}',
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, *args, **kwargs):
        """
        获取单个提醒详情
        """
        try:
            reminder = self.get_object()
            logger.info(f"用户 {request.user.username} 获取提醒详情，ID: {reminder.id}")
            
            serializer = self.get_serializer(reminder)
            return Response({
                'success': True,
                'message': '获取提醒详情成功',
                'data': serializer.data
            })
            
        except Exception as e:
            logger.error(f"获取提醒详情失败: {str(e)}")
            return Response({
                'success': False,
                'message': f'获取提醒详情失败: {str(e)}',
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)
    
    def update(self, request, *args, **kwargs):
        """
        更新提醒
        """
        try:
            reminder = self.get_object()
            logger.info(f"用户 {request.user.username} 更新提醒，ID: {reminder.id}，数据: {request.data}")
            
            serializer = self.get_serializer(reminder, data=request.data, partial=kwargs.get('partial', False))
            serializer.is_valid(raise_exception=True)
            reminder = serializer.save()
            
            # 返回完整的提醒信息
            response_serializer = ReminderSerializer(reminder)
            
            logger.info(f"提醒更新成功，ID: {reminder.id}")
            return Response({
                'success': True,
                'message': '提醒更新成功',
                'data': response_serializer.data
            })
            
        except Exception as e:
            logger.error(f"更新提醒失败: {str(e)}")
            return Response({
                'success': False,
                'message': f'更新提醒失败: {str(e)}',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """
        删除提醒
        """
        try:
            reminder = self.get_object()
            reminder_id = reminder.id
            logger.info(f"用户 {request.user.username} 删除提醒，ID: {reminder_id}")
            
            reminder.delete()
            
            logger.info(f"提醒删除成功，ID: {reminder_id}")
            return Response({
                'success': True,
                'message': '提醒删除成功',
                'data': None
            }, status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            logger.error(f"删除提醒失败: {str(e)}")
            return Response({
                'success': False,
                'message': f'删除提醒失败: {str(e)}',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """
        获取今天的提醒
        """
        try:
            logger.info(f"用户 {request.user.username} 获取今天的提醒")
            
            today = timezone.now().date()
            reminders = self.get_queryset().filter(
                is_active=True,
                start_date__lte=today
            ).filter(
                Q(end_date__isnull=True) | Q(end_date__gte=today)
            )
            
            # 过滤出今天应该提醒的
            today_reminders = [r for r in reminders if r.should_remind_today()]
            
            serializer = ReminderListSerializer(today_reminders, many=True)
            
            return Response({
                'success': True,
                'message': '获取今天的提醒成功',
                'data': serializer.data
            })
            
        except Exception as e:
            logger.error(f"获取今天的提醒失败: {str(e)}")
            return Response({
                'success': False,
                'message': f'获取今天的提醒失败: {str(e)}',
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """
        获取即将到来的提醒（未来7天）
        """
        try:
            logger.info(f"用户 {request.user.username} 获取即将到来的提醒")
            
            today = timezone.now().date()
            next_week = today + timedelta(days=7)
            
            reminders = self.get_queryset().filter(
                is_active=True,
                start_date__lte=next_week
            ).filter(
                Q(end_date__isnull=True) | Q(end_date__gte=today)
            )
            
            serializer = ReminderListSerializer(reminders, many=True)
            
            return Response({
                'success': True,
                'message': '获取即将到来的提醒成功',
                'data': serializer.data
            })
            
        except Exception as e:
            logger.error(f"获取即将到来的提醒失败: {str(e)}")
            return Response({
                'success': False,
                'message': f'获取即将到来的提醒失败: {str(e)}',
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        获取活跃的提醒
        """
        try:
            logger.info(f"用户 {request.user.username} 获取活跃的提醒")
            
            reminders = self.get_queryset().filter(is_active=True)
            serializer = ReminderListSerializer(reminders, many=True)
            
            return Response({
                'success': True,
                'message': '获取活跃的提醒成功',
                'data': serializer.data
            })
            
        except Exception as e:
            logger.error(f"获取活跃的提醒失败: {str(e)}")
            return Response({
                'success': False,
                'message': f'获取活跃的提醒失败: {str(e)}',
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def expired(self, request):
        """
        获取已过期的提醒
        """
        try:
            logger.info(f"用户 {request.user.username} 获取已过期的提醒")
            
            reminders = self.get_queryset()
            expired_reminders = [r for r in reminders if r.is_expired]
            
            serializer = ReminderListSerializer(expired_reminders, many=True)
            
            return Response({
                'success': True,
                'message': '获取已过期的提醒成功',
                'data': serializer.data
            })
            
        except Exception as e:
            logger.error(f"获取已过期的提醒失败: {str(e)}")
            return Response({
                'success': False,
                'message': f'获取已过期的提醒失败: {str(e)}',
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        获取提醒统计信息
        """
        try:
            logger.info(f"用户 {request.user.username} 获取提醒统计信息")
            
            queryset = self.get_queryset()
            
            stats = {
                'total_reminders': queryset.count(),
                'active_reminders': queryset.filter(is_active=True).count(),
                'inactive_reminders': queryset.filter(is_active=False).count(),
-                'expired_reminders': len([r for r in queryset if r.is_expired()]),
+                'expired_reminders': len([r for r in queryset if r.is_expired]),
                'today_reminders': len([r for r in queryset if r.should_remind_today()]),
                'response_rate': 0,  # 需要从历史记录计算
                'total_responses': 0,  # 需要从历史记录计算
            }
            
            # 计算响应率（如果有历史记录）
            total_reminders = queryset.aggregate(
                total_count=models.Sum('reminder_count')
            )['total_count'] or 0
            
            total_responses = queryset.aggregate(
                total_responses=models.Sum('response_count')
            )['total_responses'] or 0
            
            if total_reminders > 0:
                stats['response_rate'] = round((total_responses / total_reminders) * 100, 2)
            
            stats['total_responses'] = total_responses
            
            return Response({
                'success': True,
                'message': '获取提醒统计信息成功',
                'data': stats
            })
            
        except Exception as e:
            logger.error(f"获取提醒统计信息失败: {str(e)}")
            return Response({
                'success': False,
                'message': f'获取提醒统计信息失败: {str(e)}',
                'data': {}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """
        切换提醒的激活状态
        """
        try:
            reminder = self.get_object()
            reminder.is_active = not reminder.is_active
            reminder.save()
            
            logger.info(f"用户 {request.user.username} 切换提醒状态，ID: {reminder.id}，新状态: {reminder.is_active}")
            
            serializer = ReminderSerializer(reminder)
            
            return Response({
                'success': True,
                'message': f'提醒已{"激活" if reminder.is_active else "停用"}',
                'data': serializer.data
            })
            
        except Exception as e:
            logger.error(f"切换提醒状态失败: {str(e)}")
            return Response({
                'success': False,
                'message': f'切换提醒状态失败: {str(e)}',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def mark_responded(self, request, pk=None):
        """
        标记提醒已响应
        """
        try:
            reminder = self.get_object()
            reminder.increment_response_count()
            
            logger.info(f"用户 {request.user.username} 标记提醒已响应，ID: {reminder.id}")
            
            serializer = ReminderSerializer(reminder)
            
            return Response({
                'success': True,
                'message': '提醒已标记为已响应',
                'data': serializer.data
            })
            
        except Exception as e:
            logger.error(f"标记提醒响应失败: {str(e)}")
            return Response({
                'success': False,
                'message': f'标记提醒响应失败: {str(e)}',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def batch_toggle(self, request):
        """
        批量切换提醒状态
        """
        try:
            reminder_ids = request.data.get('reminder_ids', [])
            is_active = request.data.get('is_active', True)
            
            if not reminder_ids:
                return Response({
                    'success': False,
                    'message': '请提供提醒ID列表',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
            
            reminders = self.get_queryset().filter(id__in=reminder_ids)
            updated_count = reminders.update(is_active=is_active)
            
            logger.info(f"用户 {request.user.username} 批量切换提醒状态，更新了 {updated_count} 个提醒")
            
            return Response({
                'success': True,
                'message': f'成功更新 {updated_count} 个提醒的状态',
                'data': {'updated_count': updated_count}
            })
            
        except Exception as e:
            logger.error(f"批量切换提醒状态失败: {str(e)}")
            return Response({
                'success': False,
                'message': f'批量切换提醒状态失败: {str(e)}',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['delete'])
    def batch_delete(self, request):
        """
        批量删除提醒
        """
        try:
            reminder_ids = request.data.get('reminder_ids', [])
            
            if not reminder_ids:
                return Response({
                    'success': False,
                    'message': '请提供提醒ID列表',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
            
            reminders = self.get_queryset().filter(id__in=reminder_ids)
            deleted_count, _ = reminders.delete()
            
            logger.info(f"用户 {request.user.username} 批量删除提醒，删除了 {deleted_count} 个提醒")
            
            return Response({
                'success': True,
                'message': f'成功删除 {deleted_count} 个提醒',
                'data': {'deleted_count': deleted_count}
            })
            
        except Exception as e:
            logger.error(f"批量删除提醒失败: {str(e)}")
            return Response({
                'success': False,
                'message': f'批量删除提醒失败: {str(e)}',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def test_notification(self, request, pk=None):
        """
        测试提醒通知
        """
        try:
            reminder = self.get_object()
            
            # 发送测试通知
            success = notification_service.send_notification(
                user=request.user,
                title=f"测试提醒: {reminder.title}",
                message=f"这是一条测试通知。药品: {reminder.medicine.name}，剂量: {reminder.dosage}{reminder.get_dosage_unit_display()}",
                reminder=reminder
            )
            
            if success:
                logger.info(f"用户 {request.user.username} 测试提醒通知成功，ID: {reminder.id}")
                return Response({
                    'success': True,
                    'message': '测试通知发送成功',
                    'data': None
                })
            else:
                return Response({
                    'success': False,
                    'message': '测试通知发送失败',
                    'data': None
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"测试提醒通知失败: {str(e)}")
            return Response({
                'success': False,
                'message': f'测试提醒通知失败: {str(e)}',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)