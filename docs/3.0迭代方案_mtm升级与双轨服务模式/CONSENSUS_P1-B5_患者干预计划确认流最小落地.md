# CONSENSUS P1-B5 患者干预计划确认流最小落地

## 1. 核心共识

- **权限分离**：只有患者本人可以对计划进行确认。药师可以起草计划，但不能代患者确认（至少在本轮不考虑代确认）。
- **确认选项**：患者必须选择 `confirmed` (已确认/同意执行) 或 `declined` (已拒绝/暂不执行)。
- **交互方式**：采用独立路由页面 `MtmPlanConfirmationPage.vue` 来承接患者的阅读与确认动作，确保信息展示清晰，便于患者阅读干预措施后再做决定。

## 2. API 接口共识

在 `MTMServiceCaseViewSet` 中补充动作：

- **`POST /api/mtm/service-cases/{id}/plan/confirm/`**
  - 校验当前用户是否为服务单的患者（`service_case.patient == request.user`）。
  - 接收 payload: `{"status": "confirmed" | "declined", "notes": "..."}`。
  - 写入 `patient_confirmation_status`, `patient_confirmation_notes` 和 `confirmed_at`。

## 3. 前端共识

- **新页面**：`MtmPlanConfirmationPage.vue`
- **新路由**：`/mtm/service-cases/:id/plan/confirm`
- **详情页入口**：
  - 如果当前用户是患者，且 `plan` 已完成但 `patient_confirmation_status` 为 `pending`，在“干预计划”卡片区展示高亮按钮“前往确认”。
  - （可选）如果已确认/已拒绝，展示确认时间与说明。
- **展示**：确认页上方展示明确的干预措施清单，下方为单选框（同意/拒绝）和补充说明文本域。
