# DESIGN P1-B3 干预计划表单最小落地

## 1. 架构目标

在 `MTM` 系统中，干预计划 (`MTMPlan`) 是药师为患者开具的核心行动指南。本次迭代将在现有基础上实现“起草 -> 暂存草稿 -> 完成填写”的最小闭环，并对齐 `P1-B2` 的交互与 API 模式。

## 2. 后端设计

### 2.1 模型更新

为 `apps.mtm.models.MTMPlan` 补充 `completed_at` 字段，以标识药师是否已经完成了该计划的起草。

```python
completed_at = models.DateTimeField(
    blank=True,
    null=True,
    verbose_name="完成时间",
    help_text="干预计划完成起草的时间",
)
```

### 2.2 接口设计

1. **`GET /api/mtm/service-cases/{id}/plan/`**
   - 行为：查询对应服务单的 `MTMPlan` 记录。如果不存在，则实例化一条空记录（默认 `priority` 等于 `medium`），返回序列化数据。

2. **`PUT /api/mtm/service-cases/{id}/plan/`**
   - 行为：保存计划草稿，放宽字段校验（如 `interventions` 可以为空）。

3. **`POST /api/mtm/service-cases/{id}/plan/complete/`**
   - 行为：校验 `interventions` 是否有效（非空且项数 >= 1）。
   - 将当前时间写入 `completed_at`。
   - 返回更新后的记录。

### 2.3 序列化器

复用并扩展 `MTMPlanFormSerializer`：
- 输入字段：`interventions`, `priority`
- 只读字段：`completed_at`, `patient_confirmation_status`

## 3. 前端设计

### 3.1 新增路由

```ts
{
  path: 'service-cases/:id/plan',
  name: 'mtm-service-case-plan',
  component: () => import('@/pages/MtmPlanFormPage.vue'),
  meta: { requiresAuth: true, title: '干预计划' }
}
```

### 3.2 `MtmPlanFormPage.vue` 组件设计

- **数据绑定**：
  - `priority`: 选项组件 (低, 中, 高, 紧急)
  - `interventionsText`: `textarea` (每行一项)
- **校验逻辑**：
  - `保存草稿`：跳过所有校验
  - `完成计划`：至少填写一项干预措施
- **状态提示**：
  - 读取时显示“草稿已加载”
  - 保存后提示“草稿已保存”
  - 完成后提示“计划已完成”，路由后退

### 3.3 详情页入口 `MtmServiceCaseDetailPage.vue`

- **条件渲染**：
  - 未完成评估：入口禁用，提示“请先完成评估”
  - 评估已完成 & 计划未开始/草稿中：显示主按钮“起草干预计划”或“继续干预计划”
  - 计划已完成：显示次要按钮“查看已填计划”
- **摘要展示区**：
  - 计划完成后，展示 `priority`、`completed_at` 和 `interventions` 列表。
