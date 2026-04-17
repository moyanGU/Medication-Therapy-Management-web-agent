# ALIGNMENT P1-B5 患者端干预计划接收确认流最小落地

## 1. 原始需求

- 承接 `P1-B3` 和 `P1-B4`，进入 `P1-B5`：患者端对干预计划的接收与确认（接收确认流）最小落地。

## 2. 当前项目上下文

### 2.1 已有基础

- 后端 `apps.mtm` 中的 `MTMPlan` 模型已经存在患者确认相关的字段：
  - `patient_confirmation_status` (状态，默认 `pending`)
  - `patient_confirmation_notes` (患者反馈说明)
  - `confirmed_at` (确认时间)
- 前端详情页目前只做了展示，没有给患者提供确认的入口。
- MTM 系统的参与者主要是 `患者 (patient)` 和 `药师 (assigned_pharmacist)`。

### 2.2 流程衔接

- 药师在起草干预计划并标记完成 (`completed_at`) 后，计划即对患者可见并可被确认。
- 患者进入服务单详情，如果发现干预计划状态为 `待确认 (pending)`，则可以进行确认（或拒绝），并填写反馈。

## 3. 当前缺口

- 后端缺少让患者专门提交确认操作的 API。
- 前端没有提供给患者的确认交互弹窗或独立页面。

## 4. 本轮任务边界

### 4.1 本轮要做

- 在 `MTMServiceCaseViewSet` 中补充针对干预计划确认的 API `@action(detail=True, methods=["post"], url_path="plan/confirm")`。
- 在前端详情页 `MtmServiceCaseDetailPage.vue` 补充“患者确认计划”的交互入口。
- 新增独立的确认页面 `MtmPlanConfirmationPage.vue`（考虑到移动端或者更好的表单体验，采用独立页面而非弹窗）。

### 4.2 本轮不做

- 不做复杂的通知推送（如短信/微信推送通知患者去确认）。
- 不强制将服务状态推到 `following_up`，维持原有的解耦设计。

## 5. 默认主路径判断

- 患者登录后，进入服务单详情，若当前登录人是患者本人，且干预计划已完成且状态为 `pending`，则显示“确认干预计划”的大按钮。
- 点击按钮进入 `MtmPlanConfirmationPage`。
- 表单包含：只读的计划摘要（优先级、干预措施列表），以及可交互的：
  - 确认状态（同意执行 / 暂不执行(拒绝)）
  - 补充说明（文本域）
- 提交后写入 `patient_confirmation_status`, `patient_confirmation_notes`, `confirmed_at`，返回详情页。
