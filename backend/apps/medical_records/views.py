from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from apps.core.pagination import StandardResultsSetPagination
from apps.core.permissions import IsOwnerOrReadOnly
from apps.core.response import success_response, error_response
import os
import uuid
import mimetypes
from .models import MedicalRecord
from .serializers import (
    MedicalRecordSerializer,
    MedicalRecordListSerializer,
    MedicalRecordCreateSerializer,
    MedicalRecordSummarySerializer,
    MedicalRecordStatisticsSerializer
)
from .filters import MedicalRecordFilter, MedicalRecordStatisticsFilter
import logging
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class MedicalRecordViewSet(viewsets.ModelViewSet):
    """
    病历记录视图集
    提供病历记录的CRUD操作、搜索、统计等功能
    """
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = MedicalRecordFilter
    ordering_fields = ['visit_date', 'visit_time', 'created_at', 'total_cost', 'satisfaction_score']
    ordering = ['-visit_date', '-visit_time']
    search_fields = ['hospital', 'department', 'doctor', 'diagnosis', 'chief_complaint']
    
    def get_queryset(self):
        """
        获取当前用户的病历记录
        """
        return MedicalRecord.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """
        根据动作选择序列化器
        """
        if self.action == 'list':
            return MedicalRecordListSerializer
        elif self.action == 'create':
            return MedicalRecordCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return MedicalRecordSerializer
        elif self.action == 'summary':
            return MedicalRecordSummarySerializer
        return MedicalRecordSerializer
    
    def perform_create(self, serializer):
        """
        创建病历记录时设置用户
        """
        try:
            serializer.save(user=self.request.user)
            logger.info(f"用户 {self.request.user.username} 创建了新的病历记录")
        except Exception as e:
            logger.error(f"创建病历记录失败: {str(e)}")
            raise
    
    def create(self, request, *args, **kwargs):
        """
        创建病历记录
        """
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                self.perform_create(serializer)
                return success_response(
                    data=serializer.data,
                    message="病历记录创建成功"
                )
            return error_response(
                message="数据验证失败",
                errors=serializer.errors
            )
        except Exception as e:
            logger.error(f"创建病历记录异常: {str(e)}")
            return error_response(message="创建病历记录失败")
    
    def update(self, request, *args, **kwargs):
        """
        更新病历记录
        """
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            
            if serializer.is_valid():
                serializer.save()
                logger.info(f"用户 {request.user.username} 更新了病历记录 {instance.id}")
                return success_response(
                    data=serializer.data,
                    message="病历记录更新成功"
                )
            return error_response(
                message="数据验证失败",
                errors=serializer.errors
            )
        except Exception as e:
            logger.error(f"更新病历记录异常: {str(e)}")
            return error_response(message="更新病历记录失败")
    
    def destroy(self, request, *args, **kwargs):
        """
        删除病历记录
        """
        try:
            instance = self.get_object()
            record_id = instance.id
            instance.delete()
            logger.info(f"用户 {request.user.username} 删除了病历记录 {record_id}")
            return success_response(message="病历记录删除成功")
        except Exception as e:
            logger.error(f"删除病历记录异常: {str(e)}")
            return error_response(message="删除病历记录失败")
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        获取最近的病历记录
        """
        try:
            days = int(request.query_params.get('days', 30))
            recent_records = MedicalRecord.get_recent_visits(request.user, days)
            
            page = self.paginate_queryset(recent_records)
            if page is not None:
                serializer = MedicalRecordListSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = MedicalRecordListSerializer(recent_records, many=True)
            return success_response(
                data=serializer.data,
                message=f"获取最近{days}天的病历记录成功"
            )
        except Exception as e:
            logger.error(f"获取最近病历记录异常: {str(e)}")
            return error_response(message="获取最近病历记录失败")
    
    @action(detail=False, methods=['get'])
    def by_hospital(self, request):
        """
        按医院获取病历记录
        """
        try:
            hospital_name = request.query_params.get('hospital')
            if not hospital_name:
                return error_response(message="请提供医院名称")
            
            records = MedicalRecord.get_visits_by_hospital(request.user, hospital_name)
            
            page = self.paginate_queryset(records)
            if page is not None:
                serializer = MedicalRecordListSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = MedicalRecordListSerializer(records, many=True)
            return success_response(
                data=serializer.data,
                message=f"获取{hospital_name}的病历记录成功"
            )
        except Exception as e:
            logger.error(f"按医院获取病历记录异常: {str(e)}")
            return error_response(message="获取病历记录失败")
    
    @action(detail=False, methods=['get'])
    def by_department(self, request):
        """
        按科室获取病历记录
        """
        try:
            department_name = request.query_params.get('department')
            if not department_name:
                return error_response(message="请提供科室名称")
            
            records = MedicalRecord.get_visits_by_department(request.user, department_name)
            
            page = self.paginate_queryset(records)
            if page is not None:
                serializer = MedicalRecordListSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = MedicalRecordListSerializer(records, many=True)
            return success_response(
                data=serializer.data,
                message=f"获取{department_name}科的病历记录成功"
            )
        except Exception as e:
            logger.error(f"按科室获取病历记录异常: {str(e)}")
            return error_response(message="获取病历记录失败")
    
    @action(detail=False, methods=['get'])
    def follow_up_due(self, request):
        """
        获取需要复诊的病历记录
        """
        try:
            today = timezone.now().date()
            due_records = self.get_queryset().filter(
                follow_up_date__isnull=False,
                follow_up_date__lte=today,
                status='completed'
            )
            
            serializer = MedicalRecordListSerializer(due_records, many=True)
            return success_response(
                data=serializer.data,
                message="获取需要复诊的病历记录成功"
            )
        except Exception as e:
            logger.error(f"获取复诊提醒异常: {str(e)}")
            return error_response(message="获取复诊提醒失败")
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        获取病历统计信息
        """
        try:
            # 应用过滤器
            filterset = MedicalRecordStatisticsFilter(request.GET, queryset=self.get_queryset())
            queryset = filterset.qs
            
            # 基础统计
            total_visits = queryset.count()
            recent_visits = queryset.filter(
                visit_date__gte=timezone.now().date() - timedelta(days=30)
            ).count()
            
            # 按医院统计
            hospitals = list(queryset.values('hospital')
                           .annotate(count=Count('id'))
                           .order_by('-count')[:10])
            
            # 按科室统计
            departments = list(queryset.values('department')
                             .annotate(count=Count('id'))
                             .order_by('-count')[:10])
            
            # 按就诊类型统计
            visit_types = list(queryset.values('visit_type')
                             .annotate(count=Count('id'))
                             .order_by('-count'))
            
            # 按月份统计（最近12个月）
            monthly_visits = []
            for i in range(12):
                month_start = timezone.now().date().replace(day=1) - timedelta(days=30*i)
                month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                count = queryset.filter(
                    visit_date__gte=month_start,
                    visit_date__lte=month_end
                ).count()
                monthly_visits.append({
                    'month': month_start.strftime('%Y-%m'),
                    'count': count
                })
            monthly_visits.reverse()
            
            # 费用统计
            cost_stats = queryset.aggregate(
                total_cost=Sum('total_cost'),
                avg_cost=Avg('total_cost')
            )
            
            # 满意度统计
            satisfaction_stats = queryset.aggregate(
                avg_satisfaction=Avg('satisfaction_score')
            )
            
            # 复诊统计
            follow_up_due_count = queryset.filter(
                follow_up_date__isnull=False,
                follow_up_date__lte=timezone.now().date()
            ).count()
            
            statistics_data = {
                'total_visits': total_visits,
                'recent_visits': recent_visits,
                'hospitals': hospitals,
                'departments': departments,
                'visit_types': visit_types,
                'monthly_visits': monthly_visits,
                'total_cost': cost_stats['total_cost'] or 0,
                'average_cost': cost_stats['avg_cost'] or 0,
                'average_satisfaction': satisfaction_stats['avg_satisfaction'] or 0,
                'follow_up_due': follow_up_due_count  # 修正字段名，与序列化器一致
            }
            
            serializer = MedicalRecordStatisticsSerializer(statistics_data)
            return success_response(
                data=serializer.data,
                message="获取病历统计信息成功"
            )
        except Exception as e:
            logger.error(f"获取病历统计异常: {str(e)}")
            return error_response(message="获取病历统计失败")
    
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """
        获取病历摘要
        """
        try:
            instance = self.get_object()
            serializer = MedicalRecordSummarySerializer(instance)
            return success_response(
                data=serializer.data,
                message="获取病历摘要成功"
            )
        except Exception as e:
            logger.error(f"获取病历摘要异常: {str(e)}")
            return error_response(message="获取病历摘要失败")
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """
        获取病历分类信息
        """
        try:
            queryset = self.get_queryset()
            
            # 按科室分类
            departments = list(queryset.values('department')
                             .exclude(department__isnull=True)
                             .exclude(department__exact='')
                             .annotate(count=Count('id'))
                             .order_by('-count'))
            
            # 按就诊类型分类
            visit_types = list(queryset.values('visit_type')
                             .annotate(count=Count('id'))
                             .order_by('-count'))
            
            # 按医院分类
            hospitals = list(queryset.values('hospital')
                           .annotate(count=Count('id'))
                           .order_by('-count')[:20])  # 限制前20个医院
            
            # 按诊断分类（提取主要疾病关键词）
            diagnoses = list(queryset.values('diagnosis')
                           .exclude(diagnosis__isnull=True)
                           .exclude(diagnosis__exact='')
                           .annotate(count=Count('id'))
                           .order_by('-count')[:30])  # 限制前30个诊断
            
            # 按紧急程度分类
            urgency_levels = list(queryset.values('urgency')
                                .annotate(count=Count('id'))
                                .order_by('-count'))
            
            # 按状态分类
            statuses = list(queryset.values('status')
                          .annotate(count=Count('id'))
                          .order_by('-count'))
            
            categories_data = {
                'departments': departments,
                'visit_types': visit_types,
                'hospitals': hospitals,
                'diagnoses': diagnoses,
                'urgency_levels': urgency_levels,
                'statuses': statuses
            }
            
            return success_response(
                data=categories_data,
                message="获取病历分类信息成功"
            )
        except Exception as e:
            logger.error(f"获取病历分类异常: {str(e)}")
            return error_response(message="获取病历分类失败")
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """
        按分类获取病历记录
        """
        try:
            category_type = request.query_params.get('type')  # department, visit_type, hospital, diagnosis
            category_value = request.query_params.get('value')
            
            if not category_type or not category_value:
                return error_response(message="请提供分类类型和值")
            
            queryset = self.get_queryset()
            
            # 根据分类类型过滤
            if category_type == 'department':
                queryset = queryset.filter(department__icontains=category_value)
            elif category_type == 'visit_type':
                queryset = queryset.filter(visit_type=category_value)
            elif category_type == 'hospital':
                queryset = queryset.filter(hospital__icontains=category_value)
            elif category_type == 'diagnosis':
                queryset = queryset.filter(diagnosis__icontains=category_value)
            elif category_type == 'urgency':
                queryset = queryset.filter(urgency=category_value)
            elif category_type == 'status':
                queryset = queryset.filter(status=category_value)
            else:
                return error_response(message="不支持的分类类型")
            
            # 分页
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = MedicalRecordListSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = MedicalRecordListSerializer(queryset, many=True)
            return success_response(
                data=serializer.data,
                message=f"获取{category_type}为{category_value}的病历记录成功"
            )
        except Exception as e:
            logger.error(f"按分类获取病历记录异常: {str(e)}")
            return error_response(message="获取病历记录失败")
    
    @action(detail=False, methods=['get'])
    def advanced_search(self, request):
        """
        高级搜索病历记录
        """
        try:
            # 获取搜索参数
            keyword = request.query_params.get('keyword', '')
            date_from = request.query_params.get('date_from')
            date_to = request.query_params.get('date_to')
            hospital = request.query_params.get('hospital', '')
            department = request.query_params.get('department', '')
            doctor = request.query_params.get('doctor', '')
            diagnosis = request.query_params.get('diagnosis', '')
            visit_type = request.query_params.get('visit_type', '')
            status = request.query_params.get('status', '')
            urgency = request.query_params.get('urgency', '')
            
            queryset = self.get_queryset()
            
            # 关键词搜索（在多个字段中搜索）
            if keyword:
                queryset = queryset.filter(
                    Q(hospital__icontains=keyword) |
                    Q(department__icontains=keyword) |
                    Q(doctor__icontains=keyword) |
                    Q(diagnosis__icontains=keyword) |
                    Q(chief_complaint__icontains=keyword) |
                    Q(present_illness__icontains=keyword) |
                    Q(treatment__icontains=keyword) |
                    Q(medical_orders__icontains=keyword) |
                    Q(notes__icontains=keyword)
                )
            
            # 日期范围搜索
            if date_from:
                try:
                    date_from_obj = timezone.datetime.strptime(date_from, '%Y-%m-%d').date()
                    queryset = queryset.filter(visit_date__gte=date_from_obj)
                except ValueError:
                    return error_response(message="开始日期格式错误，请使用YYYY-MM-DD格式")
            
            if date_to:
                try:
                    date_to_obj = timezone.datetime.strptime(date_to, '%Y-%m-%d').date()
                    queryset = queryset.filter(visit_date__lte=date_to_obj)
                except ValueError:
                    return error_response(message="结束日期格式错误，请使用YYYY-MM-DD格式")
            
            # 医院搜索
            if hospital:
                queryset = queryset.filter(hospital__icontains=hospital)
            
            # 科室搜索
            if department:
                queryset = queryset.filter(department__icontains=department)
            
            # 医生搜索
            if doctor:
                queryset = queryset.filter(doctor__icontains=doctor)
            
            # 诊断搜索
            if diagnosis:
                queryset = queryset.filter(diagnosis__icontains=diagnosis)
            
            # 就诊类型搜索
            if visit_type:
                queryset = queryset.filter(visit_type=visit_type)
            
            # 状态搜索
            if status:
                queryset = queryset.filter(status=status)
            
            # 紧急程度搜索
            if urgency:
                queryset = queryset.filter(urgency=urgency)
            
            # 排序
            ordering = request.query_params.get('ordering', '-visit_date')
            if ordering:
                queryset = queryset.order_by(ordering)
            
            # 分页
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = MedicalRecordListSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = MedicalRecordListSerializer(queryset, many=True)
            return success_response(
                data=serializer.data,
                message="高级搜索完成"
            )
        except Exception as e:
            logger.error(f"高级搜索异常: {str(e)}")
            return error_response(message="搜索失败")
    
    @action(detail=False, methods=['get'])
    def search_suggestions(self, request):
        """
        获取搜索建议
        """
        try:
            field = request.query_params.get('field')  # hospital, department, doctor, diagnosis
            query = request.query_params.get('query', '')
            
            if not field or not query:
                return error_response(message="请提供搜索字段和查询词")
            
            queryset = self.get_queryset()
            suggestions = []
            
            if field == 'hospital':
                suggestions = list(queryset.filter(hospital__icontains=query)
                                 .values_list('hospital', flat=True)
                                 .distinct()[:10])
            elif field == 'department':
                suggestions = list(queryset.filter(department__icontains=query)
                                 .exclude(department__isnull=True)
                                 .exclude(department__exact='')
                                 .values_list('department', flat=True)
                                 .distinct()[:10])
            elif field == 'doctor':
                suggestions = list(queryset.filter(doctor__icontains=query)
                                 .exclude(doctor__isnull=True)
                                 .exclude(doctor__exact='')
                                 .values_list('doctor', flat=True)
                                 .distinct()[:10])
            elif field == 'diagnosis':
                suggestions = list(queryset.filter(diagnosis__icontains=query)
                                 .exclude(diagnosis__isnull=True)
                                 .exclude(diagnosis__exact='')
                                 .values_list('diagnosis', flat=True)
                                 .distinct()[:10])
            else:
                return error_response(message="不支持的搜索字段")
            
            return success_response(
                data={'suggestions': suggestions},
                message="获取搜索建议成功"
            )
        except Exception as e:
            logger.error(f"获取搜索建议异常: {str(e)}")
            return error_response(message="获取搜索建议失败")
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_attachment(self, request, pk=None):
        """
        上传病历附件
        """
        try:
            record = self.get_object()
            uploaded_file = request.FILES.get('file')
            
            if not uploaded_file:
                return error_response(message="请选择要上传的文件")
            
            # 验证文件类型
            allowed_types = [
                'application/pdf',
                'image/jpeg',
                'image/png',
                'image/gif',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'application/vnd.ms-excel',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            ]
            
            file_type = mimetypes.guess_type(uploaded_file.name)[0]
            if file_type not in allowed_types:
                return error_response(message="不支持的文件类型")
            
            # 验证文件大小（最大10MB）
            if uploaded_file.size > 10 * 1024 * 1024:
                return error_response(message="文件大小不能超过10MB")
            
            # 生成唯一文件名
            file_extension = os.path.splitext(uploaded_file.name)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = f"medical_records/{record.user.id}/{record.id}/{unique_filename}"
            
            # 保存文件
            saved_path = default_storage.save(file_path, ContentFile(uploaded_file.read()))
            
            # 更新记录的附件信息
            attachment_info = {
                'id': str(uuid.uuid4()),
                'name': uploaded_file.name,
                'file_path': saved_path,
                'file_size': uploaded_file.size,
                'file_type': file_type,
                'upload_time': timezone.now().isoformat(),
                'description': request.data.get('description', '')
            }
            
            if not record.attachments:
                record.attachments = []
            
            record.attachments.append(attachment_info)
            record.save()
            
            logger.info(f"用户 {request.user.username} 为病历记录 {record.id} 上传了附件 {uploaded_file.name}")
            
            return success_response(
                data=attachment_info,
                message="附件上传成功"
            )
        except Exception as e:
            logger.error(f"上传附件异常: {str(e)}")
            return error_response(message="附件上传失败")
    
    @action(detail=True, methods=['delete'])
    def delete_attachment(self, request, pk=None):
        """
        删除病历附件
        """
        try:
            record = self.get_object()
            attachment_id = request.data.get('attachment_id')
            
            if not attachment_id:
                return error_response(message="请提供附件ID")
            
            if not record.attachments:
                return error_response(message="该病历记录没有附件")
            
            # 查找要删除的附件
            attachment_to_delete = None
            for attachment in record.attachments:
                if attachment.get('id') == attachment_id:
                    attachment_to_delete = attachment
                    break
            
            if not attachment_to_delete:
                return error_response(message="附件不存在")
            
            # 删除文件
            try:
                if default_storage.exists(attachment_to_delete['file_path']):
                    default_storage.delete(attachment_to_delete['file_path'])
            except Exception as e:
                logger.warning(f"删除文件失败: {str(e)}")
            
            # 从记录中移除附件信息
            record.attachments.remove(attachment_to_delete)
            record.save()
            
            logger.info(f"用户 {request.user.username} 删除了病历记录 {record.id} 的附件 {attachment_to_delete['name']}")
            
            return success_response(message="附件删除成功")
        except Exception as e:
            logger.error(f"删除附件异常: {str(e)}")
            return error_response(message="附件删除失败")
    
    @action(detail=True, methods=['get'])
    def download_attachment(self, request, pk=None):
        """
        下载病历附件
        """
        try:
            record = self.get_object()
            attachment_id = request.query_params.get('attachment_id')
            
            if not attachment_id:
                return error_response(message="请提供附件ID")
            
            if not record.attachments:
                return error_response(message="该病历记录没有附件")
            
            # 查找附件
            attachment = None
            for att in record.attachments:
                if att.get('id') == attachment_id:
                    attachment = att
                    break
            
            if not attachment:
                return error_response(message="附件不存在")
            
            # 检查文件是否存在
            if not default_storage.exists(attachment['file_path']):
                return error_response(message="文件不存在")
            
            # 返回文件下载信息
            file_url = default_storage.url(attachment['file_path'])
            
            return success_response(
                data={
                    'download_url': file_url,
                    'filename': attachment['name'],
                    'file_size': attachment['file_size'],
                    'file_type': attachment['file_type']
                },
                message="获取下载链接成功"
            )
        except Exception as e:
            logger.error(f"下载附件异常: {str(e)}")
            return error_response(message="获取下载链接失败")
    
    @action(detail=True, methods=['get'])
    def list_attachments(self, request, pk=None):
        """
        获取病历附件列表
        """
        try:
            record = self.get_object()
            
            attachments = record.attachments or []
            
            # 为每个附件添加下载URL
            for attachment in attachments:
                if default_storage.exists(attachment['file_path']):
                    attachment['download_url'] = default_storage.url(attachment['file_path'])
                else:
                    attachment['download_url'] = None
                    attachment['status'] = 'file_missing'
            
            return success_response(
                data={'attachments': attachments},
                message="获取附件列表成功"
            )
        except Exception as e:
            logger.error(f"获取附件列表异常: {str(e)}")
            return error_response(message="获取附件列表失败")
    
    @action(detail=False, methods=['get'])
    def export_data(self, request):
        """
        导出病历数据（为PDF导出准备数据）
        """
        try:
            # 应用过滤器
            filterset = MedicalRecordFilter(request.GET, queryset=self.get_queryset())
            queryset = filterset.qs
            
            # 获取导出数据
            export_data = []
            for record in queryset:
                export_data.append({
                    'id': record.id,
                    'visit_date': record.visit_date.strftime('%Y-%m-%d'),
                    'visit_time': record.visit_time.strftime('%H:%M') if record.visit_time else '',
                    'hospital': record.hospital,
                    'department': record.department or '',
                    'doctor': record.doctor or '',
                    'visit_type': record.get_visit_type_display(),
                    'chief_complaint': record.chief_complaint or '',
                    'diagnosis': record.diagnosis or '',
                    'treatment': record.treatment or '',
                    'prescribed_medicines': record.get_prescribed_medicine_names(),
                    'examinations': record.get_examination_names(),
                    'total_cost': float(record.total_cost) if record.total_cost else 0,
                    'follow_up_date': record.follow_up_date.strftime('%Y-%m-%d') if record.follow_up_date else '',
                    'satisfaction_score': record.satisfaction_score or 0,
                    'status': record.get_status_display(),
                    'urgency': record.get_urgency_display()
                })
            
            return success_response(
                data={
                    'records': export_data,
                    'total_count': len(export_data),
                    'export_time': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
                },
                message="导出数据准备成功"
            )
        except Exception as e:
            logger.error(f"导出病历数据异常: {str(e)}")
            return error_response(message="导出数据失败")