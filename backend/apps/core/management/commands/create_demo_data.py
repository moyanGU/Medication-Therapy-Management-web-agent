from datetime import date, datetime, time, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.core.models import SessionMemory
from apps.medical_records.models import MedicalRecord
from apps.medicines.models import Medicine
from apps.mtm.models import MTMAssessment, MTMFollowUp, MTMInterview, MTMPlan, MTMServiceCase
from apps.plans.models import MedicationPlan, PlanMedicine
from apps.records.models import MedicationRecord
from apps.reminders.history_models import ReminderHistory
from apps.reminders.models import Reminder


class Command(BaseCommand):
    help = "创建用于录屏演示的最小可复用数据集"

    patient_username = "demo_patient"
    pharmacist_username = "demo_pharmacist"
    default_password = "Demo123456!"

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            default=self.default_password,
            help="演示账号密码，默认 Demo123456!",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        password = options["password"]
        user_model = get_user_model()
        today = timezone.localdate()
        now = timezone.now()

        patient = self._upsert_user(
            user_model=user_model,
            username=self.patient_username,
            password=password,
            email="demo_patient@example.com",
            phone="13800000099",
            first_name="王",
            last_name="建国",
            gender="male",
            birth_date=date(1958, 8, 18),
            emergency_contact="王丽",
            emergency_phone="13900000088",
            is_staff=False,
            is_admin=False,
        )
        pharmacist = self._upsert_user(
            user_model=user_model,
            username=self.pharmacist_username,
            password=password,
            email="demo_pharmacist@example.com",
            phone="13800000100",
            first_name="李",
            last_name="药师",
            gender="female",
            birth_date=date(1989, 4, 9),
            emergency_contact="",
            emergency_phone="",
            is_staff=True,
            is_admin=True,
        )

        self._clear_existing_demo_data(patient)

        medicines = self._create_medicines(patient, today)
        reminders = self._create_reminders(patient, medicines, today, now)
        self._create_reminder_history(patient, reminders, now)
        self._create_medication_records(patient, medicines, reminders, now)
        self._create_medical_records(patient, today)
        self._create_medication_plan(patient, medicines, today)
        service_case = self._create_mtm_case(patient, pharmacist, now)
        self._create_session_memory(patient, service_case, now)

        self.stdout.write(self.style.SUCCESS("演示数据已创建完成"))
        self.stdout.write(f"患者账号: {patient.username} / {password}")
        self.stdout.write(f"药师账号: {pharmacist.username} / {password}")
        self.stdout.write(f"MTM 服务单: {service_case.case_number}")

    def _upsert_user(self, *, user_model, username, password, **fields):
        defaults = {key: value for key, value in fields.items() if key != "is_admin"}
        user, created = user_model.objects.get_or_create(username=username, defaults=defaults)

        for key, value in fields.items():
            setattr(user, key, value)
        user.set_password(password)
        user.save()

        action = "创建" if created else "更新"
        self.stdout.write(f"{action}用户: {username}")
        return user

    def _clear_existing_demo_data(self, patient):
        MTMServiceCase.objects.filter(patient=patient).delete()
        MedicationRecord.objects.filter(user=patient).delete()
        ReminderHistory.objects.filter(user=patient).delete()
        Reminder.objects.filter(user=patient).delete()
        PlanMedicine.objects.filter(plan__user=patient).delete()
        MedicationPlan.objects.filter(user=patient).delete()
        MedicalRecord.objects.filter(user=patient).delete()
        Medicine.objects.filter(user=patient).delete()
        SessionMemory.objects.filter(user=patient, session_id__startswith="mtm:").delete()

    def _create_medicines(self, patient, today):
        medicine_specs = [
            {
                "name": "阿司匹林肠溶片",
                "specification": "100mg*30片",
                "manufacturer": "拜耳医药",
                "medicine_type": "tablet",
                "quantity": 18,
                "purchase_price": 28.50,
                "purchase_date": today - timedelta(days=25),
                "expiry_date": today + timedelta(days=240),
                "batch_number": "ASP-20260401",
                "storage_conditions": "阴凉干燥保存",
                "description": "用于心血管二级预防。",
                "is_prescription": True,
            },
            {
                "name": "缬沙坦胶囊",
                "specification": "80mg*14粒",
                "manufacturer": "诺华",
                "medicine_type": "capsule",
                "quantity": 6,
                "purchase_price": 46.00,
                "purchase_date": today - timedelta(days=18),
                "expiry_date": today + timedelta(days=180),
                "batch_number": "VAL-20260315",
                "storage_conditions": "避光保存",
                "description": "用于高血压长期控制。",
                "is_prescription": True,
            },
            {
                "name": "二甲双胍片",
                "specification": "500mg*60片",
                "manufacturer": "中美上海施贵宝",
                "medicine_type": "tablet",
                "quantity": 42,
                "purchase_price": 19.80,
                "purchase_date": today - timedelta(days=12),
                "expiry_date": today + timedelta(days=120),
                "batch_number": "MET-20260502",
                "storage_conditions": "室温保存",
                "description": "用于2型糖尿病血糖控制。",
                "is_prescription": True,
            },
        ]

        medicines = {}
        for spec in medicine_specs:
            medicine = Medicine.objects.create(user=patient, **spec)
            medicines[spec["name"]] = medicine
        return medicines

    def _create_reminders(self, patient, medicines, today, now):
        reminder_specs = [
            {
                "medicine": medicines["阿司匹林肠溶片"],
                "title": "早餐后服用阿司匹林",
                "message": "请按计划服用阿司匹林肠溶片 1 片。",
                "reminder_time": time(8, 0),
                "frequency": "daily",
                "dosage": 1,
                "dosage_unit": "tablet",
                "notification_types": ["push", "sound"],
                "advance_minutes": 10,
                "repeat_interval": 15,
                "max_repeats": 1,
                "start_date": today - timedelta(days=30),
                "meal_timing": "after_meal",
                "special_instructions": "饭后半小时内服用。",
                "reminder_count": 15,
                "response_count": 13,
                "last_reminded_at": now - timedelta(hours=2),
            },
            {
                "medicine": medicines["缬沙坦胶囊"],
                "title": "晚间降压药提醒",
                "message": "睡前请服用缬沙坦胶囊 1 粒，并记录血压。",
                "reminder_time": time(21, 0),
                "frequency": "daily",
                "dosage": 1,
                "dosage_unit": "capsule",
                "notification_types": ["push"],
                "advance_minutes": 0,
                "repeat_interval": 20,
                "max_repeats": 2,
                "start_date": today - timedelta(days=20),
                "meal_timing": "before_bed",
                "special_instructions": "睡前测量血压后服用。",
                "reminder_count": 12,
                "response_count": 9,
                "last_reminded_at": now - timedelta(hours=11),
            },
            {
                "medicine": medicines["二甲双胍片"],
                "title": "午餐后血糖药提醒",
                "message": "午餐后请服用二甲双胍片 1 片。",
                "reminder_time": time(13, 0),
                "frequency": "daily",
                "dosage": 1,
                "dosage_unit": "tablet",
                "notification_types": ["push", "vibration"],
                "advance_minutes": 5,
                "repeat_interval": 0,
                "max_repeats": 0,
                "start_date": today - timedelta(days=10),
                "meal_timing": "after_meal",
                "special_instructions": "若胃部不适，请与主治医生沟通。",
                "reminder_count": 9,
                "response_count": 8,
                "last_reminded_at": now - timedelta(days=1),
            },
        ]

        reminders = {}
        for spec in reminder_specs:
            reminder = Reminder.objects.create(user=patient, is_active=True, **spec)
            reminders[reminder.title] = reminder
        return reminders

    def _create_reminder_history(self, patient, reminders, now):
        history_specs = [
            {
                "reminder": reminders["早餐后服用阿司匹林"],
                "sent_at": now - timedelta(days=1, hours=2),
                "scheduled_time": now - timedelta(days=1, hours=2),
                "response_type": "taken",
                "responded_at": now - timedelta(days=1, hours=1, minutes=54),
                "response_delay_minutes": 6,
                "notes": "按时服药。",
            },
            {
                "reminder": reminders["早餐后服用阿司匹林"],
                "sent_at": now - timedelta(days=2, hours=2),
                "scheduled_time": now - timedelta(days=2, hours=2),
                "response_type": "taken",
                "responded_at": now - timedelta(days=2, hours=1, minutes=50),
                "response_delay_minutes": 10,
                "notes": "餐后完成。",
            },
            {
                "reminder": reminders["晚间降压药提醒"],
                "sent_at": now - timedelta(days=1, hours=13),
                "scheduled_time": now - timedelta(days=1, hours=13),
                "response_type": "delayed",
                "responded_at": now - timedelta(days=1, hours=12, minutes=20),
                "response_delay_minutes": 40,
                "notes": "外出后补服。",
            },
            {
                "reminder": reminders["午餐后血糖药提醒"],
                "sent_at": now - timedelta(days=3, hours=5),
                "scheduled_time": now - timedelta(days=3, hours=5),
                "response_type": "no_response",
                "responded_at": None,
                "response_delay_minutes": None,
                "notes": "未响应提醒。",
            },
        ]

        for spec in history_specs:
            ReminderHistory.objects.create(
                user=patient,
                reminder_type="scheduled",
                title=spec["reminder"].title,
                message=spec["reminder"].message or "",
                notification_methods=["push"],
                status="sent",
                device_info={"platform": "web"},
                **spec,
            )

    def _create_medication_records(self, patient, medicines, reminders, now):
        record_specs = [
            {
                "medicine": medicines["阿司匹林肠溶片"],
                "reminder": reminders["早餐后服用阿司匹林"],
                "taken_at": now - timedelta(hours=2),
                "scheduled_time": now - timedelta(hours=2, minutes=5),
                "quantity_taken": 1,
                "administration_method": "oral",
                "status": "taken",
                "notes": "早餐后服用，无不适。",
                "symptom_score": 3,
                "effectiveness_score": 8,
                "side_effects": "",
                "is_on_time": True,
                "delay_minutes": 5,
                "source": "reminder",
            },
            {
                "medicine": medicines["缬沙坦胶囊"],
                "reminder": reminders["晚间降压药提醒"],
                "taken_at": now - timedelta(days=1, hours=12, minutes=20),
                "scheduled_time": now - timedelta(days=1, hours=13),
                "quantity_taken": 1,
                "administration_method": "oral",
                "status": "delayed",
                "notes": "忘带药，回家后补服。",
                "symptom_score": 4,
                "effectiveness_score": 7,
                "side_effects": "偶有头晕",
                "is_on_time": False,
                "delay_minutes": 40,
                "source": "reminder",
            },
            {
                "medicine": medicines["二甲双胍片"],
                "reminder": reminders["午餐后血糖药提醒"],
                "taken_at": now - timedelta(days=2, hours=5),
                "scheduled_time": now - timedelta(days=2, hours=5),
                "quantity_taken": 0,
                "administration_method": "oral",
                "status": "missed",
                "notes": "外出就餐漏服。",
                "symptom_score": 5,
                "effectiveness_score": 0,
                "side_effects": "",
                "is_on_time": False,
                "delay_minutes": None,
                "source": "reminder",
            },
        ]

        for spec in record_specs:
            MedicationRecord.objects.create(user=patient, **spec)

    def _create_medical_records(self, patient, today):
        record_specs = [
            {
                "visit_date": today - timedelta(days=12),
                "visit_time": time(9, 30),
                "hospital": "上海市第一人民医院",
                "hospital_address": "上海市虹口区海宁路100号",
                "department": "心内科",
                "doctor": "张明",
                "doctor_title": "主任医师",
                "visit_type": "follow_up",
                "chief_complaint": "近一周晨起血压偏高，偶有头晕。",
                "present_illness": "既往高血压病史10年，近期服药依从性一般。",
                "diagnosis": "高血压病 2级，血压控制欠佳",
                "diagnosis_code": "I10",
                "treatment": "继续降压治疗，优化服药时间，建议监测家庭血压。",
                "prescribed_medicines": [
                    {
                        "name": "缬沙坦胶囊",
                        "dosage": "80mg",
                        "frequency": "每日一次",
                        "duration": "30天",
                        "instructions": "睡前服用",
                    },
                    {
                        "name": "阿司匹林肠溶片",
                        "dosage": "100mg",
                        "frequency": "每日一次",
                        "duration": "长期",
                        "instructions": "早餐后服用",
                    },
                ],
                "examinations": [
                    {"name": "血压监测", "type": "vital"},
                    {"name": "血脂检查", "type": "lab"},
                ],
                "examination_results": "门诊血压 152/94 mmHg，低密度脂蛋白略高。",
                "lab_results": {
                    "LDL-C": {"value": 3.6, "unit": "mmol/L", "status": "high"},
                    "SBP": {"value": 152, "unit": "mmHg", "status": "high"},
                },
                "medical_orders": "每日晨起及睡前记录血压，2周后复诊。",
                "notes": "患者表示晚间偶有忘服情况。",
                "total_cost": 286.50,
                "insurance_coverage": 180.00,
                "self_pay_amount": 106.50,
                "follow_up_date": today + timedelta(days=5),
                "follow_up_notes": "复诊时携带家庭血压记录。",
                "symptom_score_before": 6,
                "symptom_score_after": 4,
                "satisfaction_score": 4,
                "status": "completed",
                "urgency": "routine",
                "attachments": [],
            },
            {
                "visit_date": today - timedelta(days=30),
                "visit_time": time(14, 0),
                "hospital": "上海交通大学医学院附属瑞金医院",
                "hospital_address": "上海市黄浦区瑞金二路197号",
                "department": "内分泌科",
                "doctor": "刘敏",
                "doctor_title": "副主任医师",
                "visit_type": "outpatient",
                "chief_complaint": "餐后血糖控制波动。",
                "present_illness": "2型糖尿病病史5年，近期饮食不规律。",
                "diagnosis": "2型糖尿病",
                "diagnosis_code": "E11.9",
                "treatment": "继续二甲双胍治疗，加强饮食管理。",
                "prescribed_medicines": [
                    {
                        "name": "二甲双胍片",
                        "dosage": "500mg",
                        "frequency": "每日两次",
                        "duration": "30天",
                        "instructions": "餐后服用",
                    }
                ],
                "examinations": [{"name": "糖化血红蛋白", "type": "lab"}],
                "examination_results": "糖化血红蛋白 7.8%。",
                "lab_results": {
                    "HbA1c": {"value": 7.8, "unit": "%", "status": "high"}
                },
                "medical_orders": "控制主食摄入，记录空腹和餐后血糖。",
                "notes": "近期午餐后偶有漏服。",
                "total_cost": 198.00,
                "insurance_coverage": 120.00,
                "self_pay_amount": 78.00,
                "follow_up_date": today + timedelta(days=18),
                "follow_up_notes": "复查血糖与体重。",
                "symptom_score_before": 5,
                "symptom_score_after": 4,
                "satisfaction_score": 5,
                "status": "completed",
                "urgency": "routine",
                "attachments": [],
            },
        ]

        for spec in record_specs:
            MedicalRecord.objects.create(user=patient, **spec)

    def _create_medication_plan(self, patient, medicines, today):
        plan = MedicationPlan.objects.create(
            user=patient,
            name="慢病联合用药管理计划",
            plan_type="chronic",
            start_date=today - timedelta(days=12),
            end_date=today + timedelta(days=30),
            description="针对高血压和糖尿病的联合用药与监测计划。",
            treatment_goal="稳定血压并改善血糖控制，提升用药依从性。",
            is_active=True,
            priority="high",
            source="pharmacist",
            doctor_name="张明",
            hospital_name="上海市第一人民医院",
            department="心内科",
            diagnosis="高血压病 2级，2型糖尿病",
            precautions="关注低血压风险和胃肠道不适。",
            side_effects_monitoring="注意头晕、胃部不适、低血糖症状。",
            review_date=today + timedelta(days=5),
            status="active",
        )

        PlanMedicine.objects.create(
            plan=plan,
            medicine=medicines["缬沙坦胶囊"],
            daily_dosage=1,
            frequency="once_daily",
            single_dose=1,
            instructions="睡前服用并监测血压",
            administration_times=["21:00"],
            meal_timing="anytime",
            special_requirements="漏服不补双倍剂量",
            is_required=True,
            start_day=1,
            duration_days=42,
            dosage_adjustments=[],
        )
        PlanMedicine.objects.create(
            plan=plan,
            medicine=medicines["二甲双胍片"],
            daily_dosage=2,
            frequency="twice_daily",
            single_dose=1,
            instructions="早餐后、晚餐后各 1 片",
            administration_times=["08:30", "18:30"],
            meal_timing="after_meal",
            special_requirements="胃部不适时及时反馈",
            is_required=True,
            start_day=1,
            duration_days=42,
            dosage_adjustments=[],
        )

    def _create_mtm_case(self, patient, pharmacist, now):
        service_case = MTMServiceCase.objects.create(
            patient=patient,
            assigned_pharmacist=pharmacist,
            status="completed",
            trigger_source="adherence_alert",
            service_goal="针对高血压与糖尿病联合用药依从性下降进行 MTM 干预。",
            notes="演示用案例：覆盖问诊、评估、计划、随访、SOAP 和报告预览全链路。",
            started_at=now - timedelta(days=3),
            completed_at=now - timedelta(hours=3),
        )

        MTMInterview.objects.create(
            service_case=service_case,
            basic_info_snapshot={
                "patient_name": patient.get_full_name() or patient.username,
                "age": patient.age,
                "gender": patient.get_gender_display(),
                "contact_phone": patient.phone,
                "main_diagnosis": "高血压病、2型糖尿病",
                "weight": "74kg",
                "height": "170cm",
            },
            medication_history=[
                "阿司匹林肠溶片 100mg 每日一次，早餐后服用",
                "缬沙坦胶囊 80mg 每日一次，睡前服用",
                "二甲双胍片 500mg 每日两次，餐后服用",
            ],
            allergy_history=["青霉素过敏"],
            lifestyle_info={
                "smoking": "已戒烟 5 年",
                "drinking": "偶尔饮酒",
                "exercise": "每周步行 3 次，每次 30 分钟",
                "sleep": "平均睡眠 6 小时",
            },
            economic_context="可接受长期常规慢病药物支出，但希望减少不必要检查费用。",
            health_expectations="希望血压更平稳，减少漏服情况，并改善餐后血糖波动。",
            notes="患者反映晚间外出时容易漏服降压药。",
            completed_at=now - timedelta(days=2, hours=18),
        )

        MTMAssessment.objects.create(
            service_case=service_case,
            appropriateness_score=82,
            effectiveness_score=74,
            safety_score=68,
            adherence_score=61,
            economic_score=79,
            problem_list=[
                "晚间降压药存在延迟服用，血压控制稳定性不足。",
                "午餐后口服降糖药有漏服记录，影响血糖达标。",
                "患者对联合用药长期管理缺少固定提醒策略。",
            ],
            summary="当前方案总体适宜，但依从性不足是主要风险来源，建议通过固定提醒、家庭监测和随访强化执行。",
            risk_level="high",
            completed_at=now - timedelta(days=2, hours=12),
        )

        MTMPlan.objects.create(
            service_case=service_case,
            interventions=[
                "建立早中晚固定提醒，晚间降压药设置重复提醒。",
                "建议患者连续 14 天记录晨起和睡前血压。",
                "午餐后药物与固定就餐行为绑定，减少漏服。",
                "两周后进行一次电话随访，复核依从性与不良反应。",
            ],
            priority="high",
            patient_confirmation_status="confirmed",
            patient_confirmation_notes="患者同意按建议执行，并愿意配合家庭血压记录。",
            confirmed_at=now - timedelta(days=1, hours=20),
        )

        MTMFollowUp.objects.create(
            service_case=service_case,
            follow_up_time=now - timedelta(hours=6),
            follow_up_method="phone",
            execution_status="completed",
            risk_change="improved",
            summary="患者表示过去 3 天未再漏服晚间降压药，晨起血压较前略有下降。",
            next_follow_up_time=now + timedelta(days=7),
        )

        service_case.soap_notes = {
            "subjective": "患者主诉近期晚间外出后容易忘记服用降压药，偶有头晕，担心血压波动影响日常活动。",
            "objective": "近 7 天存在 1 次漏服和 1 次延迟服药记录；门诊血压 152/94 mmHg；糖化血红蛋白 7.8%。",
            "assessment": "主要药物治疗问题为依从性不足导致血压和血糖控制稳定性下降，当前总体存在中高风险。",
            "plan": "优化提醒策略，强化家庭监测，保持现有核心药物方案，两周内完成电话随访并复核记录。",
        }
        service_case.save(update_fields=["soap_notes", "updated_at"])
        return service_case

    def _create_session_memory(self, patient, service_case, now):
        SessionMemory.objects.create(
            user=patient,
            session_id=f"mtm:{service_case.id}:page-agent",
            summary="AI 已总结：患者晚间降压药依从性较差，午餐后降糖药偶有漏服，建议通过提醒、监测和短期随访强化管理。",
            messages=[
                {
                    "role": "user",
                    "content": "我最近晚上总忘记吃降压药。",
                    "timestamp": (now - timedelta(days=2, hours=19)).isoformat(),
                },
                {
                    "role": "assistant",
                    "content": "已记录依从性风险，建议把晚间服药和睡前血压测量绑定。",
                    "timestamp": (now - timedelta(days=2, hours=19, minutes=-2)).isoformat(),
                },
            ],
        )
