from rest_framework import serializers
from django.utils import timezone
from .models import MedicalRecord


class MedicalRecordSerializer(serializers.ModelSerializer):
    """
    病历记录序列化器
    """
    # 只读字段
    visit_datetime = serializers.ReadOnlyField()
    days_since_visit = serializers.ReadOnlyField()
    days_until_follow_up = serializers.ReadOnlyField()
    symptom_improvement = serializers.ReadOnlyField()
    
    # 自定义字段
    prescribed_medicine_names = serializers.ReadOnlyField(source='get_prescribed_medicine_names')
    examination_names = serializers.ReadOnlyField(source='get_examination_names')
    out_of_pocket_cost = serializers.ReadOnlyField(source='calculate_out_of_pocket_cost')
    is_follow_up_due = serializers.ReadOnlyField()
    
    class Meta:
        model = MedicalRecord
        fields = [
            'id', 'user', 'visit_date', 'visit_time', 'hospital', 'hospital_address',
            'department', 'doctor', 'doctor_title', 'visit_type', 'chief_complaint',
            'present_illness', 'diagnosis', 'diagnosis_code', 'treatment',
            'prescribed_medicines', 'examinations', 'examination_results',
            'lab_results', 'medical_orders', 'notes', 'total_cost',
            'insurance_coverage', 'self_pay_amount', 'follow_up_date',
            'follow_up_notes', 'symptom_score_before', 'symptom_score_after',
            'satisfaction_score', 'status', 'urgency', 'attachments',
            'created_at', 'updated_at', 'visit_datetime', 'days_since_visit',
            'days_until_follow_up', 'symptom_improvement', 'prescribed_medicine_names',
            'examination_names', 'out_of_pocket_cost', 'is_follow_up_due'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def validate_visit_date(self, value):
        """
        验证就诊日期不能是未来日期
        """
        if value > timezone.now().date():
            raise serializers.ValidationError("就诊日期不能是未来日期")
        return value
    
    def validate_follow_up_date(self, value):
        """
        验证复诊日期必须在就诊日期之后
        """
        if value and self.instance:
            if value <= self.instance.visit_date:
                raise serializers.ValidationError("复诊日期必须在就诊日期之后")
        elif value and 'visit_date' in self.initial_data:
            visit_date = self.initial_data['visit_date']
            if isinstance(visit_date, str):
                visit_date = timezone.datetime.strptime(visit_date, '%Y-%m-%d').date()
            if value <= visit_date:
                raise serializers.ValidationError("复诊日期必须在就诊日期之后")
        return value
    
    def validate_symptom_score_before(self, value):
        """
        验证就诊前症状评分
        """
        if value is not None and (value < 1 or value > 10):
            raise serializers.ValidationError("症状评分必须在1-10之间")
        return value
    
    def validate_symptom_score_after(self, value):
        """
        验证就诊后症状评分
        """
        if value is not None and (value < 1 or value > 10):
            raise serializers.ValidationError("症状评分必须在1-10之间")
        return value
    
    def validate_satisfaction_score(self, value):
        """
        验证满意度评分
        """
        if value is not None and (value < 1 or value > 5):
            raise serializers.ValidationError("满意度评分必须在1-5之间")
        return value
    
    def validate_total_cost(self, value):
        """
        验证总费用
        """
        if value is not None and value < 0:
            raise serializers.ValidationError("总费用不能为负数")
        return value
    
    def validate_insurance_coverage(self, value):
        """
        验证医保报销金额
        """
        if value is not None and value < 0:
            raise serializers.ValidationError("医保报销金额不能为负数")
        return value
    
    def validate_self_pay_amount(self, value):
        """
        验证自费金额
        """
        if value is not None and value < 0:
            raise serializers.ValidationError("自费金额不能为负数")
        return value
    
    def validate(self, attrs):
        """
        交叉验证
        """
        # 验证医保报销不能超过总费用
        total_cost = attrs.get('total_cost')
        insurance_coverage = attrs.get('insurance_coverage')
        
        if total_cost and insurance_coverage and insurance_coverage > total_cost:
            raise serializers.ValidationError({
                'insurance_coverage': '医保报销金额不能超过总费用'
            })
        
        return attrs


class MedicalRecordCreateSerializer(serializers.ModelSerializer):
    """
    病历记录创建序列化器
    """
    class Meta:
        model = MedicalRecord
        fields = [
            'visit_date', 'visit_time', 'hospital', 'hospital_address',
            'department', 'doctor', 'doctor_title', 'visit_type', 'chief_complaint',
            'present_illness', 'diagnosis', 'diagnosis_code', 'treatment',
            'prescribed_medicines', 'examinations', 'examination_results',
            'lab_results', 'medical_orders', 'notes', 'total_cost',
            'insurance_coverage', 'self_pay_amount', 'follow_up_date',
            'follow_up_notes', 'symptom_score_before', 'symptom_score_after',
            'satisfaction_score', 'status', 'urgency', 'attachments'
        ]
    
    def validate_visit_date(self, value):
        """
        验证就诊日期不能是未来日期
        """
        if value > timezone.now().date():
            raise serializers.ValidationError("就诊日期不能是未来日期")
        return value
    
    def validate_follow_up_date(self, value):
        """
        验证复诊日期必须在就诊日期之后
        """
        if value and 'visit_date' in self.initial_data:
            visit_date = self.initial_data['visit_date']
            if isinstance(visit_date, str):
                visit_date = timezone.datetime.strptime(visit_date, '%Y-%m-%d').date()
            if value <= visit_date:
                raise serializers.ValidationError("复诊日期必须在就诊日期之后")
        return value
    
    def create(self, validated_data):
        """
        创建病历记录
        """
        # 从请求中获取当前用户
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        
        return super().create(validated_data)


class MedicalRecordListSerializer(serializers.ModelSerializer):
    """
    病历记录列表序列化器（简化版）
    """
    days_since_visit = serializers.ReadOnlyField()
    days_until_follow_up = serializers.ReadOnlyField()
    is_follow_up_due = serializers.ReadOnlyField()
    
    class Meta:
        model = MedicalRecord
        fields = [
            'id', 'visit_date', 'visit_time', 'hospital', 'department',
            'doctor', 'visit_type', 'diagnosis', 'status', 'urgency',
            'total_cost', 'follow_up_date', 'days_since_visit',
            'days_until_follow_up', 'is_follow_up_due', 'created_at'
        ]


class MedicalRecordSummarySerializer(serializers.ModelSerializer):
    """
    病历记录摘要序列化器
    """
    visit_summary = serializers.ReadOnlyField(source='get_visit_summary')
    
    class Meta:
        model = MedicalRecord
        fields = ['id', 'visit_summary']


class MedicalRecordStatisticsSerializer(serializers.Serializer):
    """
    病历统计序列化器
    """
    total_visits = serializers.IntegerField()
    recent_visits = serializers.IntegerField()
    hospitals = serializers.ListField(child=serializers.DictField())
    departments = serializers.ListField(child=serializers.DictField())
    visit_types = serializers.ListField(child=serializers.DictField())
    monthly_visits = serializers.ListField(child=serializers.DictField())
    total_cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    average_cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    follow_up_due = serializers.IntegerField()