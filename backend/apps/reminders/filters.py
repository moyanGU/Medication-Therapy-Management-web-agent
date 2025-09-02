import django_filters
from django.utils import timezone
from django.db.models import Q
from .models import Reminder


class ReminderFilter(django_filters.FilterSet):
    """
    用药提醒过滤器
    """
    # 药品过滤
    medicine = django_filters.NumberFilter(field_name='medicine__id')
    medicine_name = django_filters.CharFilter(
        field_name='medicine__name',
        lookup_expr='icontains'
    )
    
    # 状态过滤
    is_active = django_filters.BooleanFilter(field_name='is_active')
    
    # 频率过滤
    frequency = django_filters.ChoiceFilter(
        field_name='frequency',
        choices=Reminder.FREQUENCY_CHOICES
    )
    
    # 餐前餐后过滤
    meal_timing = django_filters.ChoiceFilter(
        field_name='meal_timing',
        choices=Reminder.MEAL_TIMING_CHOICES
    )
    
    # 时间范围过滤
    start_date_from = django_filters.DateFilter(
        field_name='start_date',
        lookup_expr='gte'
    )
    start_date_to = django_filters.DateFilter(
        field_name='start_date',
        lookup_expr='lte'
    )
    
    end_date_from = django_filters.DateFilter(
        field_name='end_date',
        lookup_expr='gte'
    )
    end_date_to = django_filters.DateFilter(
        field_name='end_date',
        lookup_expr='lte'
    )
    
    # 提醒时间范围过滤
    reminder_time_from = django_filters.TimeFilter(
        field_name='reminder_time',
        lookup_expr='gte'
    )
    reminder_time_to = django_filters.TimeFilter(
        field_name='reminder_time',
        lookup_expr='lte'
    )
    
    # 是否过期过滤
    is_expired = django_filters.BooleanFilter(
        method='filter_expired'
    )
    
    # 今天是否提醒过滤
    remind_today = django_filters.BooleanFilter(
        method='filter_remind_today'
    )
    
    # 响应率范围过滤
    response_rate_min = django_filters.NumberFilter(
        method='filter_response_rate_min'
    )
    response_rate_max = django_filters.NumberFilter(
        method='filter_response_rate_max'
    )
    
    # 提醒次数范围过滤
    reminder_count_min = django_filters.NumberFilter(
        field_name='reminder_count',
        lookup_expr='gte'
    )
    reminder_count_max = django_filters.NumberFilter(
        field_name='reminder_count',
        lookup_expr='lte'
    )
    
    class Meta:
        model = Reminder
        fields = {
            'dosage': ['exact', 'gte', 'lte'],
            'dosage_unit': ['exact'],
            'advance_minutes': ['exact', 'gte', 'lte'],
            'repeat_interval': ['exact', 'gte', 'lte'],
            'max_repeats': ['exact', 'gte', 'lte'],
            'created_at': ['date', 'date__gte', 'date__lte'],
            'updated_at': ['date', 'date__gte', 'date__lte'],
        }
    
    def filter_expired(self, queryset, name, value):
        """
        过滤已过期的提醒
        """
        today = timezone.now().date()
        if value:
            return queryset.filter(end_date__lt=today)
        else:
            return queryset.filter(
                Q(end_date__isnull=True) | Q(end_date__gte=today)
            )
    
    def filter_remind_today(self, queryset, name, value):
        """
        过滤今天需要提醒的
        """
        today = timezone.now().date()
        
        if value:
            # 获取今天需要提醒的
            today_reminders = []
            for reminder in queryset:
                if reminder.should_remind_today():
                    today_reminders.append(reminder.id)
            return queryset.filter(id__in=today_reminders)
        else:
            # 获取今天不需要提醒的
            today_reminders = []
            for reminder in queryset:
                if not reminder.should_remind_today():
                    today_reminders.append(reminder.id)
            return queryset.filter(id__in=today_reminders)
    
    def filter_response_rate_min(self, queryset, name, value):
        """
        过滤最小响应率
        """
        filtered_ids = []
        for reminder in queryset:
            if reminder.response_rate >= value:
                filtered_ids.append(reminder.id)
        return queryset.filter(id__in=filtered_ids)
    
    def filter_response_rate_max(self, queryset, name, value):
        """
        过滤最大响应率
        """
        filtered_ids = []
        for reminder in queryset:
            if reminder.response_rate <= value:
                filtered_ids.append(reminder.id)
        return queryset.filter(id__in=filtered_ids)