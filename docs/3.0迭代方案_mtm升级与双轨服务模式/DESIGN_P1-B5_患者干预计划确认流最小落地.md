# DESIGN P1-B5 患者干预计划确认流最小落地

## 1. 架构目标

在 `MTM` 系统中，干预计划 (`MTMPlan`) 在药师起草完成后，需要由患者端阅读、知晓并反馈确认情况。这一环节标志着患者知情同意并准备好进入随访周期。

## 2. 后端设计

### 2.1 接口设计

在 `apps.mtm.views.MTMServiceCaseViewSet` 中补充 `@action(detail=True, methods=["post"], url_path="plan/confirm")`。

- **权限**：校验 `service_case.patient == request.user`。非患者本人请求应返回 403（或 400）。
- **前置条件**：计划必须已起草完成（`completed_at is not None`）。
- **Payload**:
  - `status`: `ChoiceField` (`confirmed`, `declined`)
  - `notes`: `CharField(required=False, allow_blank=True)`
- **处理**：
  - 更新 `MTMPlan` 的 `patient_confirmation_status` = `status`
  - 更新 `patient_confirmation_notes` = `notes`
  - 更新 `confirmed_at` = `timezone.now()`

### 2.2 序列化器

新增 `MTMPlanConfirmSerializer(serializers.Serializer)`
- `status = serializers.ChoiceField(choices=[('confirmed', '同意执行'), ('declined', '暂不执行')])`
- `notes = serializers.CharField(required=False, allow_blank=True, max_length=1000)`

## 3. 前端设计

### 3.1 新增路由

```ts
{
  path: 'service-cases/:id/plan/confirm',
  name: 'mtm-service-case-plan-confirm',
  component: () => import('@/pages/MtmPlanConfirmationPage.vue'),
  meta: { requiresAuth: true, title: '确认干预计划' },
  props: true,
}
```

### 3.2 `MtmPlanConfirmationPage.vue` 组件设计

- **数据绑定**：
  - `status`: `radio` 选项 ('confirmed' | 'declined')
  - `notes`: `textarea` (患者反馈)
- **展示内容**：
  - 加载服务单详情中的干预计划 `interventions` 和 `priority` 供患者阅读。
- **状态提示**：
  - 成功提交后提示“确认已提交”，返回详情页。

### 3.3 详情页入口 `MtmServiceCaseDetailPage.vue`

- **条件渲染**：
  - 角色判定：通过全局 user state 或当前 user.id 与 serviceCase.patient.id 对比判断是否为患者本人。
  - 计划状态：如果 `plan` 已完成（`completed_at` 存在）且 `patient_confirmation_status === 'pending'`，则在干预计划卡片区域显示一个非常醒目的“待您确认干预计划”按钮。
  - 如果已经确认或拒绝，则在摘要区展示 `patient_confirmation_status` 和 `confirmed_at`（该部分其实已经在详情页做过展示，本轮只需确认无误）。