import django_filters
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from .history_models import ReminderHistory, ReminderStats
from apps.medicines.models import Medicine


class ReminderHistoryFilter(django_filters.FilterSet):
    """
    提醒历史记录过滤器
    """
    # 药品过滤
    medicine = django_filters.ModelChoiceFilter(
        field_name='reminder__medicine',
        queryset=Medicine.objects.all(),
        label='药品'
    )
    
    medicine_name = django_filters.CharFilter(
        field_name='reminder__medicine__name',
        lookup_expr='icontains',
        label='药品名称'
    )
    
    # 提醒状态过滤
    status = django_filters.ChoiceFilter(
        choices=ReminderHistory.STATUS_CHOICES,
        label='发送状态'
    )
    
    # 响应类型过滤
    response_type = django_filters.ChoiceFilter(
        choices=ReminderHistory.RESPONSE_TYPE_CHOICES,
        label='响应类型'
    )
    
    # 提醒类型过滤
    reminder_type = django_filters.ChoiceFilter(
        choices=ReminderHistory.REMINDER_TYPE_CHOICES,
        label='提醒类型'
    )
    
    # 时间范围过滤
    sent_date = django_filters.DateFilter(
        field_name='sent_at__date',
        label='发送日期'
    )
    
    sent_date_after = django_filters.DateFilter(
        field_name='sent_at__date',
        lookup_expr='gte',
        label='发送日期（起始）'
    )
    
    sent_date_before = django_filters.DateFilter(
        field_name='sent_at__date',
        lookup_expr='lte',
        label='发送日期（结束）'
    )
    
    sent_time_after = django_filters.TimeFilter(
        field_name='sent_at__time',
        lookup_expr='gte',
        label='发送时间（起始）'
    )
    
    sent_time_before = django_filters.TimeFilter(
        field_name='sent_at__time',
        lookup_expr='lte',
        label='发送时间（结束）'
    )
    
    # 响应时间过滤
    responded_date = django_filters.DateFilter(
        field_name='responded_at__date',
        label='响应日期'
    )
    
    responded_date_after = django_filters.DateFilter(
        field_name='responded_at__date',
        lookup_expr='gte',
        label='响应日期（起始）'
    )
    
    responded_date_before = django_filters.DateFilter(
        field_name='responded_at__date',
        lookup_expr='lte',
        label='响应日期（结束）'
    )
    
    # 响应延迟过滤
    response_delay_min = django_filters.NumberFilter(
        field_name='response_delay_minutes',
        lookup_expr='gte',
        label='响应延迟（最小分钟）'
    )
    
    response_delay_max = django_filters.NumberFilter(
        field_name='response_delay_minutes',
        lookup_expr='lte',
        label='响应延迟（最大分钟）'
    )
    
    # 布尔过滤
    is_responded = django_filters.BooleanFilter(
        method='filter_is_responded',
        label='是否已响应'
    )
    
    is_successful = django_filters.BooleanFilter(
        method='filter_is_successful',
        label='是否成功'
    )
    
    # 通知方式过滤
    has_push_notification = django_filters.BooleanFilter(
        method='filter_has_push_notification',
        label='包含推送通知'
    )
    
    has_email_notification = django_filters.BooleanFilter(
        method='filter_has_email_notification',
        label='包含邮件通知'
    )
    
    has_sms_notification = django_filters.BooleanFilter(
        method='filter_has_sms_notification',
        label='包含短信通知'
    )
    
    # 预设时间范围过滤
    time_range = django_filters.ChoiceFilter(
        method='filter_time_range',
        choices=[
            ('today', '今天'),
            ('yesterday', '昨天'),
            ('this_week', '本周'),
            ('last_week', '上周'),
            ('this_month', '本月'),
            ('last_month', '上月'),
            ('last_7_days', '最近7天'),
            ('last_30_days', '最近30天'),
        ],
        label='时间范围'
    )
    
    class Meta:
        model = ReminderHistory
        fields = [
            'medicine', 'medicine_name', 'status', 'response_type',
            'reminder_type', 'sent_date', 'sent_date_after', 'sent_date_before',
            'sent_time_after', 'sent_time_before', 'responded_date',
            'responded_date_after', 'responded_date_before',
            'response_delay_min', 'response_delay_max', 'is_responded',
            'is_successful', 'has_push_notification', 'has_email_notification',
            'has_sms_notification', 'time_range'
        ]
    
    def filter_is_responded(self, queryset, name, value):
        """
        过滤是否已响应
        """
        if value is True:
            return queryset.exclude(response_type='no_response')
        elif value is False:
            return queryset.filter(response_type='no_response')
        return queryset
    
    def filter_is_successful(self, queryset, name, value):
        """
        过滤是否成功（已发送且已响应）
        """
        if value is True:
            return queryset.filter(
                status='sent'
            ).exclude(response_type='no_response')
        elif value is False:
            return queryset.filter(
                Q(status__ne='sent') | Q(response_type='no_response')
            )
        return queryset
    
    def filter_has_push_notification(self, queryset, name, value):
        """
        过滤包含推送通知
        """
        if value is True:
            return queryset.filter(notification_methods__contains=['push'])
        elif value is False:
            return queryset.exclude(notification_methods__contains=['push'])
        return queryset
    
    def filter_has_email_notification(self, queryset, name, value):
        """
        过滤包含邮件通知
        """
        if value is True:
            return queryset.filter(notification_methods__contains=['email'])
        elif value is False:
            return queryset.exclude(notification_methods__contains=['email'])
        return queryset
    
    def filter_has_sms_notification(self, queryset, name, value):
        """
        过滤包含短信通知
        """
        if value is True:
            return queryset.filter(notification_methods__contains=['sms'])
        elif value is False:
            return queryset.exclude(notification_methods__contains=['sms'])
        return queryset
    
    def filter_time_range(self, queryset, name, value):
        """
        过滤预设时间范围
        """
        now = timezone.now()
        today = now.date()
        
        if value == 'today':
            return queryset.filter(sent_at__date=today)
        elif value == 'yesterday':
            yesterday = today - timedelta(days=1)
            return queryset.filter(sent_at__date=yesterday)
        elif value == 'this_week':
            # 本周（周一到今天）
            start_of_week = today - timedelta(days=today.weekday())
            return queryset.filter(
                sent_at__date__gte=start_of_week,
                sent_at__date__lte=today
            )
        elif value == 'last_week':
            # 上周（上周一到上周日）
            start_of_this_week = today - timedelta(days=today.weekday())
            start_of_last_week = start_of_this_week - timedelta(days=7)
            end_of_last_week = start_of_this_week - timedelta(days=1)
            return queryset.filter(
                sent_at__date__gte=start_of_last_week,
                sent_at__date__lte=end_of_last_week
            )
        elif value == 'this_month':
            # 本月
            start_of_month = today.replace(day=1)
            return queryset.filter(
                sent_at__date__gte=start_of_month,
                sent_at__date__lte=today
            )
        elif value == 'last_month':
            # 上月
            if today.month == 1:
                last_month = today.replace(year=today.year - 1, month=12, day=1)
            else:
                last_month = today.replace(month=today.month - 1, day=1)
            
            # 上月的最后一天
            if today.month == 1:
                end_of_last_month = today.replace(year=today.year - 1, month=12, day=31)
            else:
                import calendar
                last_day = calendar.monthrange(today.year, today.month - 1)[1]
                end_of_last_month = today.replace(month=today.month - 1, day=last_day)
            
            return queryset.filter(
                sent_at__date__gte=last_month,
                sent_at__date__lte=end_of_last_month
            )
        elif value == 'last_7_days':
            # 最近7天
            start_date = today - timedelta(days=6)
            return queryset.filter(
                sent_at__date__gte=start_date,
                sent_at__date__lte=today
            )
        elif value == 'last_30_days':
            # 最近30天
            start_date = today - timedelta(days=29)
            return queryset.filter(
                sent_at__date__gte=start_date,
                sent_at__date__lte=today
            )
        
        return queryset


class ReminderStatsFilter(django_filters.FilterSet):
    """
    提醒统计过滤器
    """
    # 日期范围过滤
    date = django_filters.DateFilter(
        field_name='date',
        label='统计日期'
    )
    
    date_after = django_filters.DateFilter(
        field_name='date',
        lookup_expr='gte',
        label='统计日期（起始）'
    )
    
    date_before = django_filters.DateFilter(
        field_name='date',
        lookup_expr='lte',
        label='统计日期（结束）'
    )
    
    # 响应率范围过滤
    response_rate_min = django_filters.NumberFilter(
        field_name='response_rate',
        lookup_expr='gte',
        label='响应率（最小%）'
    )
    
    response_rate_max = django_filters.NumberFilter(
        field_name='response_rate',
        lookup_expr='lte',
        label='响应率（最大%）'
    )
    
    # 服药率范围过滤
    adherence_rate_min = django_filters.NumberFilter(
        field_name='adherence_rate',
        lookup_expr='gte',
        label='服药率（最小%）'
    )
    
    adherence_rate_max = django_filters.NumberFilter(
        field_name='adherence_rate',
        lookup_expr='lte',
        label='服药率（最大%）'
    )
    
    # 提醒数量范围过滤
    sent_count_min = django_filters.NumberFilter(
        field_name='sent_count',
        lookup_expr='gte',
        label='发送数量（最小）'
    )
    
    sent_count_max = django_filters.NumberFilter(
        field_name='sent_count',
        lookup_expr='lte',
        label='发送数量（最大）'
    )
    
    # 平均响应时间范围过滤
    avg_response_time_min = django_filters.NumberFilter(
        field_name='avg_response_time',
        lookup_expr='gte',
        label='平均响应时间（最小分钟）'
    )
    
    avg_response_time_max = django_filters.NumberFilter(
        field_name='avg_response_time',
        lookup_expr='lte',
        label='平均响应时间（最大分钟）'
    )
    
    # 预设时间范围过滤
    time_range = django_filters.ChoiceFilter(
        method='filter_time_range',
        choices=[
            ('this_week', '本周'),
            ('last_week', '上周'),
            ('this_month', '本月'),
            ('last_month', '上月'),
            ('last_7_days', '最近7天'),
            ('last_30_days', '最近30天'),
            ('last_90_days', '最近90天'),
        ],
        label='时间范围'
    )
    
    # 统计质量过滤
    quality_level = django_filters.ChoiceFilter(
        method='filter_quality_level',
        choices=[
            ('excellent', '优秀（响应率≥90%）'),
            ('good', '良好（响应率≥80%）'),
            ('average', '一般（响应率≥70%）'),
            ('poor', '较差（响应率<70%）'),
        ],
        label='统计质量'
    )
    
    class Meta:
        model = ReminderStats
        fields = [
            'date', 'date_after', 'date_before',
            'response_rate_min', 'response_rate_max',
            'adherence_rate_min', 'adherence_rate_max',
            'sent_count_min', 'sent_count_max',
            'avg_response_time_min', 'avg_response_time_max',
            'time_range', 'quality_level'
        ]
    
    def filter_time_range(self, queryset, name, value):
        """
        过滤预设时间范围
        """
        now = timezone.now()
        today = now.date()
        
        if value == 'this_week':
            # 本周（周一到今天）
            start_of_week = today - timedelta(days=today.weekday())
            return queryset.filter(
                date__gte=start_of_week,
                date__lte=today
            )
        elif value == 'last_week':
            # 上周（上周一到上周日）
            start_of_this_week = today - timedelta(days=today.weekday())
            start_of_last_week = start_of_this_week - timedelta(days=7)
            end_of_last_week = start_of_this_week - timedelta(days=1)
            return queryset.filter(
                date__gte=start_of_last_week,
                date__lte=end_of_last_week
            )
        elif value == 'this_month':
            # 本月
            start_of_month = today.replace(day=1)
            return queryset.filter(
                date__gte=start_of_month,
                date__lte=today
            )
        elif value == 'last_month':
            # 上月
            if today.month == 1:
                last_month = today.replace(year=today.year - 1, month=12, day=1)
            else:
                last_month = today.replace(month=today.month - 1, day=1)
            
            # 上月的最后一天
            if today.month == 1:
                end_of_last_month = today.replace(year=today.year - 1, month=12, day=31)
            else:
                import calendar
                last_day = calendar.monthrange(today.year, today.month - 1)[1]
                end_of_last_month = today.replace(month=today.month - 1, day=last_day)
            
            return queryset.filter(
                date__gte=last_month,
                date__lte=end_of_last_month
            )
        elif value == 'last_7_days':
            # 最近7天
            start_date = today - timedelta(days=6)
            return queryset.filter(
                date__gte=start_date,
                date__lte=today
            )
        elif value == 'last_30_days':
            # 最近30天
            start_date = today - timedelta(days=29)
            return queryset.filter(
                date__gte=start_date,
                date__lte=today
            )
        elif value == 'last_90_days':
            # 最近90天
            start_date = today - timedelta(days=89)
            return queryset.filter(
                date__gte=start_date,
                date__lte=today
            )
        
        return queryset
    
    def filter_quality_level(self, queryset, name, value):
        """
        过滤统计质量等级
        """
        if value == 'excellent':
            return queryset.filter(response_rate__gte=90)
        elif value == 'good':
            return queryset.filter(
                response_rate__gte=80,
                response_rate__lt=90
            )
        elif value == 'average':
            return queryset.filter(
                response_rate__gte=70,
                response_rate__lt=80
            )
        elif value == 'poor':
            return queryset.filter(response_rate__lt=70)
        
        return queryset