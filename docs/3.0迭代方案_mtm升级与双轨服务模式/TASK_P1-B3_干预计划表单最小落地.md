# TASK P1-B3 干预计划表单最小落地

## 任务列表

### 1. 后端模型与迁移 (Backend Models)

- [ ] 在 `MTMPlan` 模型中添加 `completed_at` 字段
- [ ] 生成数据迁移文件并执行 `migrate`
- [ ] 确保模型中 `interventions` 的 JSON 结构处理正常

### 2. 后端 API 与序列化 (Backend API)

- [ ] 创建/更新 `MTMPlanFormSerializer` 序列化器
- [ ] 在 `MTMServiceCaseViewSet` 中实现 `@action(detail=True, methods=["get", "put"]) def plan(self, request, pk=None)`
- [ ] 在 `MTMServiceCaseViewSet` 中实现 `@action(detail=True, methods=["post"], url_path="plan/complete") def complete_plan(self, request, pk=None)`
- [ ] 补充或调整对应的权限控制与错误日志记录

### 3. 后端测试 (Backend Tests)

- [ ] 在 `apps/mtm/tests/test_api.py` 中补充获取计划、保存计划草稿、完成计划的单测
- [ ] 执行 `manage.py test apps.mtm.tests.test_api` 并确保通过

### 4. 前端类型与 API 封装 (Frontend Types & API)

- [ ] 在 `src/types/mtm.ts` 中补充 `MtmPlanDraftPayload` 类型
- [ ] 在 `src/api/mtm.ts` 中补充 `getServiceCasePlan`, `saveServiceCasePlanDraft`, `completeServiceCasePlan`

### 5. 前端页面实现 (Frontend Page)

- [ ] 新建 `src/pages/MtmPlanFormPage.vue`
- [ ] 实现 `textarea` 按行收集 `interventions` 的逻辑
- [ ] 实现草稿保存与完成的校验交互
- [ ] 注册页面到 `src/router/index.ts`

### 6. 前端详情页收口 (Frontend Detail Page)

- [ ] 在 `MtmServiceCaseDetailPage.vue` 中添加对“计划”环节的主入口渲染逻辑
- [ ] 在详情页完善计划完成后的“摘要”卡片展示
- [ ] 避免旧有的状态推进按钮与表单入口形成认知冲突

### 7. 验收与构建 (Verification)

- [ ] 在浏览器执行端到端手工测试（从详情页进入、保存草稿、完成计划、回看摘要）
- [ ] 运行 `npm run build` 确保无新增类型与构建错误
- [ ] 填写 `ACCEPTANCE_P1-B3_干预计划表单最小落地.md`
