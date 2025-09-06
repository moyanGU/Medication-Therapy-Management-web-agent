from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
import json
from django.http import HttpResponse

from .models import MedicationRecord
from .serializers import (
    MedicationRecordSerializer,
    MedicationRecordCreateSerializer,
    MedicationRecordListSerializer,
    MedicationRecordStatsSerializer
)
from .filters import MedicationRecordFilter
from apps.core.pagination import StandardResultsSetPagination
from apps.core.permissions import IsOwnerOrReadOnly
from apps.core.response import APIResponse


class MedicationRecordViewSet(viewsets.ModelViewSet):
    """
    用药记录视图集
    提供用药记录的CRUD操作、统计分析和导出功能
    """
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MedicationRecordFilter
    search_fields = ['medicine__name', 'notes', 'side_effects']
    ordering_fields = ['taken_at', 'created_at', 'adherence_score']
    ordering = ['-taken_at']
    
    def get_queryset(self):
        """
        获取当前用户的用药记录
        """
        return MedicationRecord.objects.filter(
            user=self.request.user
        ).select_related('medicine', 'user')
    
    def get_serializer_class(self):
        """
        根据动作选择序列化器
        """
        if self.action == 'create':
            return MedicationRecordCreateSerializer
        elif self.action == 'list':
            return MedicationRecordListSerializer
        return MedicationRecordSerializer
    
    def perform_create(self, serializer):
        """
        创建用药记录时自动设置用户
        """
        serializer.save(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """
        创建用药记录
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # 使用详细序列化器返回完整数据
        response_serializer = MedicationRecordSerializer(serializer.instance)
        
        return APIResponse.success(
            data=response_serializer.data,
            message="用药记录创建成功",
            status_code=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        获取用药记录统计信息
        """
        # 获取查询参数
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        medicine_id = request.query_params.get('medicine_id')
        
        # 构建查询条件
        queryset = self.get_queryset()
        
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(taken_at__date__gte=start_date)
            except ValueError:
                return Response(
                    {'error': '开始日期格式错误，请使用YYYY-MM-DD格式'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(taken_at__date__lte=end_date)
            except ValueError:
                return Response(
                    {'error': '结束日期格式错误，请使用YYYY-MM-DD格式'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if medicine_id:
            queryset = queryset.filter(medicine_id=medicine_id)
        
        # 计算统计数据
        total_records = queryset.count()
        
        if total_records == 0:
            stats_data = {
                'total_records': 0,
                'taken_count': 0,
                'missed_count': 0,
                'delayed_count': 0,
                'adherence_rate': 0.0,
                'avg_effectiveness': 0.0,
                'most_used_medicine': '',
                'daily_average': 0.0
            }
        else:
            # 按状态统计
            status_stats = queryset.values('status').annotate(count=Count('id'))
            status_dict = {item['status']: item['count'] for item in status_stats}
            
            taken_count = status_dict.get('taken', 0)
            missed_count = status_dict.get('missed', 0)
            delayed_count = status_dict.get('delayed', 0)
            
            # 计算依从性
            adherence_rate = (taken_count / total_records) * 100 if total_records > 0 else 0
            
            # 计算平均效果评分
            avg_effectiveness = queryset.filter(
                effectiveness_score__isnull=False
            ).aggregate(avg=Avg('effectiveness_score'))['avg'] or 0
            
            # 最常用药品
            most_used = queryset.values('medicine__name').annotate(
                count=Count('id')
            ).order_by('-count').first()
            most_used_medicine = most_used['medicine__name'] if most_used else ''
            
            # 计算日均用药次数
            if start_date and end_date:
                days = (end_date - start_date).days + 1
                daily_average = total_records / days if days > 0 else 0
            else:
                # 默认计算最近30天
                thirty_days_ago = timezone.now().date() - timedelta(days=30)
                recent_records = queryset.filter(taken_at__date__gte=thirty_days_ago).count()
                daily_average = recent_records / 30
            
            stats_data = {
                'total_records': total_records,
                'taken_count': taken_count,
                'missed_count': missed_count,
                'delayed_count': delayed_count,
                'adherence_rate': round(adherence_rate, 2),
                'avg_effectiveness': round(avg_effectiveness, 2),
                'most_used_medicine': most_used_medicine,
                'daily_average': round(daily_average, 2)
            }
        
        serializer = MedicationRecordStatsSerializer(stats_data)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def trends(self, request):
        """
        获取用药趋势数据
        """
        # 获取最近30天的数据
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        queryset = self.get_queryset().filter(taken_at__date__gte=thirty_days_ago)
        
        # 按日期分组统计
        daily_stats = {}
        for i in range(30):
            date = thirty_days_ago + timedelta(days=i)
            daily_stats[date.strftime('%Y-%m-%d')] = {
                'date': date.strftime('%Y-%m-%d'),
                'total': 0,
                'taken': 0,
                'missed': 0,
                'delayed': 0
            }
        
        # 填充实际数据
        records = queryset.values('taken_at__date', 'status').annotate(count=Count('id'))
        for record in records:
            date_str = record['taken_at__date'].strftime('%Y-%m-%d')
            if date_str in daily_stats:
                daily_stats[date_str]['total'] += record['count']
                daily_stats[date_str][record['status']] += record['count']
        
        # 转换为列表格式
        trend_data = list(daily_stats.values())
        
        return Response({
            'success': True,
            'data': trend_data
        })
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        """
        导出用药记录数据
        """
        # 获取查询参数
        format_type = request.query_params.get('format', 'json')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # 构建查询条件
        queryset = self.get_queryset()
        
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(taken_at__date__gte=start_date)
            except ValueError:
                return Response(
                    {'error': '开始日期格式错误'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(taken_at__date__lte=end_date)
            except ValueError:
                return Response(
                    {'error': '结束日期格式错误'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # 序列化数据
        serializer = MedicationRecordSerializer(queryset, many=True)
        
        if format_type == 'json':
            # JSON格式导出
            response = HttpResponse(
                json.dumps(serializer.data, ensure_ascii=False, indent=2),
                content_type='application/json; charset=utf-8'
            )
            response['Content-Disposition'] = 'attachment; filename="medication_records.json"'
            return response
        
        return Response(
            {'error': '不支持的导出格式'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        获取最近的用药记录
        """
        limit = int(request.query_params.get('limit', 10))
        queryset = self.get_queryset()[:limit]
        serializer = MedicationRecordListSerializer(queryset, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        })