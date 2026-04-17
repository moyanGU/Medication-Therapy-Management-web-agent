# DESIGN P1-B4 随访记录最小落地

## 1. 架构目标

在 `MTM` 系统中，随访 (`MTMFollowUp`) 是药师确认干预效果、评估患者用药依从性和风险变化的关键环节。与前面的“问诊、评估、计划”不同，随访是可重复的“1对多”结构。本轮需新增独立的 API 和独立的前端表单页面，实现创建与编辑随访。

## 2. 后端设计

### 2.1 路由与视图

在 `apps.mtm.urls` 中注册 `follow-ups` 的 ViewSet。

```python
# urls.py
router.register("follow-ups", MTMFollowUpViewSet, basename="mtm-followup")
```

### 2.2 `MTMFollowUpViewSet` 设计

- **权限**: 仅药师和系统管理员允许创建与修改，且应限制修改自身负责的服务单的随访（简单实现：使用统一的 IsAuthenticated 即可，进一步可以加自定义 Permission）。
- **`create` (POST)**: 创建一条随访记录，Payload 必须包含 `service_case`。
- **`update` (PUT/PATCH)**: 更新指定的随访记录。
- **`retrieve` (GET)**: 获取单条随访详情。

### 2.3 序列化器 `MTMFollowUpSerializer`

- 输入字段：
  - `service_case` (只在创建时必填)
  - `follow_up_time` (必填)
  - `follow_up_method`
  - `execution_status`
  - `risk_change`
  - `summary`
  - `next_follow_up_time`
- 输出同理。

## 3. 前端设计

### 3.1 新增路由

```ts
{
  path: 'service-cases/:caseId/follow-ups/new',
  name: 'mtm-follow-up-create',
  component: () => import('@/pages/MtmFollowUpFormPage.vue'),
  meta: { requiresAuth: true, title: '新建随访' },
  props: true,
},
{
  path: 'service-cases/:caseId/follow-ups/:followUpId',
  name: 'mtm-follow-up-edit',
  component: () => import('@/pages/MtmFollowUpFormPage.vue'),
  meta: { requiresAuth: true, title: '编辑随访' },
  props: true,
}
```

### 3.2 `MtmFollowUpFormPage.vue` 组件设计

- **数据绑定**：
  - `followUpTime` (日期选择，必填)
  - `followUpMethod` (枚举选择)
  - `executionStatus` (枚举选择：待执行, 已完成, 未完成, 已取消)
  - `riskChange` (枚举选择：改善, 稳定, 恶化, 未知)
  - `summary` (文本域)
  - `nextFollowUpTime` (日期选择，选填)
- **校验逻辑**：
  - `followUpTime` 不能为空。
- **状态提示**：
  - 成功保存后提示“随访记录已保存”，并返回服务单详情。

### 3.3 详情页入口 `MtmServiceCaseDetailPage.vue`

- **条件渲染**：
  - 未完成干预计划：不展示“添加随访”按钮（或禁用并给提示）。
  - 干预计划已完成：展示主按钮“+ 添加随访记录”。
- **卡片展示区**：
  - 已有的随访卡片增加点击事件 `goToFollowUpForm(item.id)` 或“编辑”小按钮。
