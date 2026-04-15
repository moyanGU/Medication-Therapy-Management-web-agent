# CONSENSUS_T-P0-08_MTM服务最小模型与迁移

## 一、任务共识

本轮正式启动的开发任务为：

- `T-P0-08 MTM 服务最小模型与迁移`

目标共识：

- 为链路B建立独立、最小、可扩展的后端主数据骨架

---

## 二、App 共识

本任务确定：

- 新建独立 app：`apps.mtm`

并注册到：

- `mtm_helper/settings.py` 的 `LOCAL_APPS`

原因：

- 不把 MTM 服务硬塞进现有 `plans` 或 `medical_records`
- 为后续 `T-P0-09` 的 CRUD 与状态流转留出清晰边界

---

## 三、模型共识

本任务确定新增以下 5 个模型：

1. `MTMServiceCase`
2. `MTMInterview`
3. `MTMAssessment`
4. `MTMPlan`
5. `MTMFollowUp`

关系共识：

- `MTMServiceCase` 为主实体
- `MTMInterview` 与 `MTMServiceCase` 一对一
- `MTMAssessment` 与 `MTMServiceCase` 一对一
- `MTMPlan` 与 `MTMServiceCase` 一对一
- `MTMFollowUp` 与 `MTMServiceCase` 一对多

---

## 四、字段共识

### 4.1 MTMServiceCase

最小字段确定为：

- `case_number`
- `patient`
- `assigned_pharmacist`
- `status`
- `trigger_source`
- `service_goal`
- `notes`
- `started_at`
- `completed_at`
- `created_at`
- `updated_at`

状态至少支持：

- `pending`
- `interviewing`
- `assessing`
- `intervening`
- `following_up`
- `completed`

### 4.2 MTMInterview

最小字段确定为：

- `service_case`
- `basic_info_snapshot`
- `medication_history`
- `allergy_history`
- `lifestyle_info`
- `economic_context`
- `health_expectations`
- `notes`
- `completed_at`
- `created_at`
- `updated_at`

### 4.3 MTMAssessment

最小字段确定为：

- `service_case`
- `appropriateness_score`
- `effectiveness_score`
- `safety_score`
- `adherence_score`
- `economic_score`
- `problem_list`
- `summary`
- `risk_level`
- `completed_at`
- `created_at`
- `updated_at`

### 4.4 MTMPlan

最小字段确定为：

- `service_case`
- `interventions`
- `priority`
- `patient_confirmation_status`
- `patient_confirmation_notes`
- `confirmed_at`
- `created_at`
- `updated_at`

### 4.5 MTMFollowUp

最小字段确定为：

- `service_case`
- `follow_up_time`
- `follow_up_method`
- `execution_status`
- `risk_change`
- `summary`
- `next_follow_up_time`
- `created_at`
- `updated_at`

---

## 五、数据类型共识

复杂结构首版使用 `JSONField`：

- `basic_info_snapshot`
- `medication_history`
- `lifestyle_info`
- `problem_list`
- `interventions`

五维评分首版使用：

- `PositiveIntegerField`
- 评分范围 `0-100`

患者与药师当前统一使用：

- `apps.users.models.User`

---

## 六、业务编号共识

`MTMServiceCase.case_number` 必须自动生成。

首版要求：

- 唯一
- 可读
- 不直接暴露数据库主键

实现方向：

- 日期前缀 + UUID 短串

---

## 七、实现范围共识

本任务仅包含：

- app 建立
- 模型建立
- admin 注册
- 迁移文件

本任务明确不包含：

- serializer
- view
- router
- CRUD 接口
- 状态流转接口

---

## 八、验收标准

本任务完成后，必须满足以下验收条件：

1. `apps.mtm` 已创建并注册
2. 五个最小模型已建立
3. 模型关系清晰
4. `MTMServiceCase` 具备业务编号和服务状态
5. 迁移文件可执行
6. 不把链路B模型塞进现有 `plans` 或 `medical_records`
7. 至少具备基础 admin 调试支持

---

## 九、实施结论

`T-P0-08` 的最终实施方案确定为：

1. 新建独立 `mtm` app
2. 以 `MTMServiceCase` 为主实体
3. 用一对一模型承接问诊、评估、计划
4. 用一对多模型承接随访
5. 首版采用最小字段和 `JSONField` 方案，先把主骨架立住
