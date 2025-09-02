import django_filters
from django.db import models
from .models import MedicationRecord


class MedicationRecordFilter(django_filters.FilterSet):
    """
    用药记录筛选器
    """
    # 日期范围筛选
    start_date = django_filters.DateFilter(
        field_name='taken_at__date',
        lookup_expr='gte',
        help_text='开始日期（格式：YYYY-MM-DD）'
    )
    end_date = django_filters.DateFilter(
        field_name='taken_at__date',
        lookup_expr='lte',
        help_text='结束日期（格式：YYYY-MM-DD）'
    )
    
    # 创建时间范围筛选
    created_start = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text='创建开始时间'
    )
    created_end = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text='创建结束时间'
    )
    
    # 药品筛选
    medicine = django_filters.NumberFilter(
        field_name='medicine__id',
        help_text='药品ID'
    )
    medicine_name = django_filters.CharFilter(
        field_name='medicine__name',
        lookup_expr='icontains',
        help_text='药品名称（模糊匹配）'
    )
    
    # 服用状态筛选
    status = django_filters.ChoiceFilter(
        choices=MedicationRecord.STATUS_CHOICES,
        help_text='服用状态'
    )
    
    # 服药方式筛选
    administration_method = django_filters.ChoiceFilter(
        choices=MedicationRecord.ADMINISTRATION_CHOICES,
        help_text='服药方式'
    )
    
    # 是否按时服药
    is_on_time = django_filters.BooleanFilter(
        help_text='是否按时服药'
    )
    
    # 记录来源筛选
    source = django_filters.ChoiceFilter(
        choices=MedicationRecord.SOURCE_CHOICES,
        help_text='记录来源'
    )
    
    # 效果评分范围
    effectiveness_min = django_filters.NumberFilter(
        field_name='effectiveness_score',
        lookup_expr='gte',
        help_text='最低效果评分'
    )
    effectiveness_max = django_filters.NumberFilter(
        field_name='effectiveness_score',
        lookup_expr='lte',
        help_text='最高效果评分'
    )
    
    # 症状评分范围
    symptom_min = django_filters.NumberFilter(
        field_name='symptom_score',
        lookup_expr='gte',
        help_text='最低症状评分'
    )
    symptom_max = django_filters.NumberFilter(
        field_name='symptom_score',
        lookup_expr='lte',
        help_text='最高症状评分'
    )
    
    # 服药数量范围
    quantity_min = django_filters.NumberFilter(
        field_name='quantity_taken',
        lookup_expr='gte',
        help_text='最少服药数量'
    )
    quantity_max = django_filters.NumberFilter(
        field_name='quantity_taken',
        lookup_expr='lte',
        help_text='最多服药数量'
    )
    
    # 延迟时间范围
    delay_min = django_filters.NumberFilter(
        field_name='delay_minutes',
        lookup_expr='gte',
        help_text='最少延迟时间（分钟）'
    )
    delay_max = django_filters.NumberFilter(
        field_name='delay_minutes',
        lookup_expr='lte',
        help_text='最多延迟时间（分钟）'
    )
    
    # 是否有副作用
    has_side_effects = django_filters.BooleanFilter(
        method='filter_has_side_effects',
        help_text='是否有副作用记录'
    )
    
    # 是否有备注
    has_notes = django_filters.BooleanFilter(
        method='filter_has_notes',
        help_text='是否有备注'
    )
    
    class Meta:
        model = MedicationRecord
        fields = {
            'taken_at': ['exact', 'gte', 'lte'],
            'created_at': ['exact', 'gte', 'lte'],
            'medicine': ['exact'],
            'status': ['exact'],
            'administration_method': ['exact'],
            'is_on_time': ['exact'],
            'source': ['exact'],
        }
    
    def filter_has_side_effects(self, queryset, name, value):
        """
        筛选是否有副作用记录
        """
        if value is True:
            return queryset.exclude(side_effects__isnull=True).exclude(side_effects__exact='')
        elif value is False:
            return queryset.filter(models.Q(side_effects__isnull=True) | models.Q(side_effects__exact=''))
        return queryset
    
    def filter_has_notes(self, queryset, name, value):
        """
        筛选是否有备注
        """
        if value is True:
            return queryset.exclude(notes__isnull=True).exclude(notes__exact='')
        elif value is False:
            return queryset.filter(models.Q(notes__isnull=True) | models.Q(notes__exact=''))
        return queryset