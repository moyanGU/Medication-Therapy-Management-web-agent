# CONSENSUS P1-B3 干预计划表单最小落地

## 1. 核心共识

- **延续 P1-B2 风格**：本轮不引入新的复杂组件，继续复用“文本域按行分割收集 JSON 数组”和“基础选择器收集枚举值”的表单方式。
- **引入完成时间字段**：`MTMPlan` 原有模型没有记录药师端填写的 `completed_at`，本轮必须添加该字段，用以判断计划是否进入了“已完成填写”状态。
- **解耦状态流转**：完成干预计划不等于服务状态自动进入“随访中 (following_up)”，这保留了人工确认与干预实施周期的弹性。

## 2. API 接口共识

在 `MTMServiceCaseViewSet` 中补充：

- `GET /api/mtm/service-cases/{id}/plan/`
  - 获取草稿或已完成数据，无数据时自动初始化
- `PUT /api/mtm/service-cases/{id}/plan/`
  - 保存草稿，校验放宽，允许全空
- `POST /api/mtm/service-cases/{id}/plan/complete/`
  - 完成填写，严格校验必填项，写入 `completed_at`

## 3. 前端共识

- **新页面**：`MtmPlanFormPage.vue`
- **新路由**：`/mtm/service-cases/:id/plan`
- **详情页入口**：
  - 未评估或评估未完成：提示先完成评估
  - 评估已完成：显示“起草干预计划”或“继续干预计划”
  - 计划已完成：显示“查看已填计划”
- **展示**：计划完成后，详情页摘要区应当显示优先级、完成时间、干预措施列表。
