# ALIGNMENT_T-P0-08_MTM服务最小模型与迁移

## 一、原始任务

任务来源：`TASK_P0_正式拆分.md` 中的 `T-P0-08 MTM 服务最小模型与迁移`

任务目标：

- 新增链路B最小专业骨架模型
- 形成专业 MTM 服务的后端主线

---

## 二、当前项目理解

### 2.1 现状判断

当前项目虽然已经有：

- `plans`
- `medical_records`
- `records`
- `reminders`

但它们都只适合作为链路B的输入资料，不适合作为 MTM 服务主实体。

当前真正缺失的是：

- 一条独立的 MTM 服务主线
- 一组围绕服务单组织的最小专业模型

### 2.2 为什么不能塞进现有模块

不能塞进 `plans`：

- `plans` 本质上是通用用药计划
- 没有完整服务流程语义

不能塞进 `medical_records`：

- `medical_records` 本质上是就医事件记录
- 不等于 MTM 专业服务流程

不能塞进 `records`：

- `records` 是服药执行结果
- 不是专业评估与干预过程

因此本任务应新建独立 app。

---

## 三、现有代码约束

### 3.1 App 组织约束

当前后端采用：

- `backend/apps/<app_name>/`

的独立 app 组织方式，并在 `settings.py` 的 `LOCAL_APPS` 中注册。

因此本任务应新增：

- `apps.mtm`

### 3.2 用户模型约束

当前只有统一的 `User` 模型，没有独立药师模型。

因此本轮最小骨架里：

- 患者
- 主责药师

都先使用 `apps.users.models.User` 关联表示。

这不代表角色体系已经完成，只是为后续角色模型留接口。

### 3.3 数据复杂度约束

当前任务只是“最小骨架”，因此不适合一上来做：

- 多版本问诊
- 多版本评估
- 多版本计划
- 复杂协作关系
- 审批流

更适合先做：

- 一个服务单
- 一份问诊
- 一份评估
- 一份干预计划
- 多条随访记录

---

## 四、需求边界确认

### 4.1 本任务要做什么

本任务负责：

- 新建独立 `mtm` app
- 新建五个最小模型
- 注册到 Django
- 提供迁移文件
- 提供基础 admin 调试支持

### 4.2 本任务不做什么

本任务不负责：

- 序列化器
- 视图和 CRUD 接口
- 权限细化
- 药师工作台
- SOAP / PMR / MAP

这些属于后续 `T-P0-09` 及之后的任务。

---

## 五、关键歧义与当前判断

### 5.1 是否新建独立 app

当前判断：

- 必须新建
- 名称使用 `apps.mtm`

### 5.2 五个模型之间的关系

当前判断：

- `MTMServiceCase` 是主实体
- `MTMInterview`、`MTMAssessment`、`MTMPlan` 与服务单使用 `OneToOneField`
- `MTMFollowUp` 与服务单使用 `ForeignKey`

原因：

- 问诊、评估、计划在首版按“一单一份”最小化建模
- 随访天然可能多次发生

### 5.3 评分字段怎么设计

当前判断：

- 五维评估先使用 `PositiveIntegerField`
- 范围先收敛为 `0-100`

原因：

- 后续无论转成问卷分值、规则分值、AI 评分都更容易兼容

### 5.4 问诊 / 问题清单 / 干预措施如何存

当前判断：

- 首版用 `JSONField`

适合字段：

- 基本信息快照
- 用药史
- 生活方式
- 问题清单
- 干预措施

原因：

- 先让结构化信息可存
- 避免首版过度拆表

### 5.5 服务编号是否自动生成

当前判断：

- 要自动生成
- 使用日期前缀 + UUID 短串的方式

原因：

- 便于后续用户、药师、后台沟通
- 避免首版直接依赖数据库自增 ID 暴露业务编号

---

## 六、建议模型边界

### 6.1 MTMServiceCase

建议最小字段：

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

### 6.2 MTMInterview

- `service_case`
- `basic_info_snapshot`
- `medication_history`
- `allergy_history`
- `lifestyle_info`
- `economic_context`
- `health_expectations`
- `notes`
- `completed_at`

### 6.3 MTMAssessment

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

### 6.4 MTMPlan

- `service_case`
- `interventions`
- `priority`
- `patient_confirmation_status`
- `patient_confirmation_notes`
- `confirmed_at`

### 6.5 MTMFollowUp

- `service_case`
- `follow_up_time`
- `follow_up_method`
- `execution_status`
- `risk_change`
- `summary`
- `next_follow_up_time`

---

## 七、风险点

- 如果首版不新建独立 app，后面专业流程会继续纠缠在现有业务模型里
- 如果首版把字段拆得过细，后续接口和前端会跟着过重
- 如果首版不生成业务编号，后续服务单展示和沟通会不方便
- 如果 `FollowUp` 不做一对多，后续很快会返工

---

## 八、当前结论

`T-P0-08` 应采用“新建独立 mtm app + 五个最小模型 + 最小迁移”的策略。

推荐实现方向：

1. 新建 `apps.mtm`
2. 注册到 `LOCAL_APPS`
3. 建立 1 个主实体 + 3 个一对一 + 1 个一对多 模型关系
4. 首版优先用 `JSONField` 承接复杂结构
5. 提供 admin 便于后续调试
