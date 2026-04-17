# TASK P1-B4 随访记录最小落地

## 任务列表

### 1. 后端 API 与序列化 (Backend API)

- [ ] 在 `apps/mtm/serializers.py` 中新增 `MTMFollowUpSerializer`（用于读写）。
- [ ] 在 `apps/mtm/views.py` 中新增 `MTMFollowUpViewSet`，实现 `create`、`retrieve`、`update` 方法。
- [ ] 在 `apps/mtm/urls.py` 中注册 `follow-ups` 的路由。
- [ ] 确保模型中 `follow_up_time` 和 `next_follow_up_time` 支持正确的时区时间格式。

### 2. 后端测试 (Backend Tests)

- [ ] 在 `apps/mtm/tests/test_api.py` 中补充新增随访、修改随访的接口测试。
- [ ] 执行 `manage.py test apps.mtm.tests.test_api` 确保通过。

### 3. 前端类型与 API 封装 (Frontend Types & API)

- [ ] 在 `src/types/mtm.ts` 中补充 `MtmFollowUpPayload` 类型。
- [ ] 在 `src/api/mtm.ts` 中补充 `createFollowUp`, `updateFollowUp`, `getFollowUp` 方法。

### 4. 前端页面实现 (Frontend Page)

- [ ] 新建 `src/pages/MtmFollowUpFormPage.vue`。
- [ ] 实现新增态和编辑态的表单复用，绑定时间和枚举选择器。
- [ ] 注册新路由 `/mtm/service-cases/:caseId/follow-ups/new` 和 `:followUpId`。

### 5. 前端详情页收口 (Frontend Detail Page)

- [ ] 在 `MtmServiceCaseDetailPage.vue` 随访区右上角添加 `+ 新增随访` 按钮（计划完成后可用）。
- [ ] 改造 `followUpCards` 中的元素，使它们可点击或带有一个编辑图标进入修改模式。

### 6. 验收与构建 (Verification)

- [ ] 浏览器端到端测试（详情页新增 -> 保存 -> 详情页列表显示 -> 点击进入编辑 -> 再次保存）。
- [ ] 运行 `npm run build` 确保无报错。
- [ ] 填写 `ACCEPTANCE_P1-B4_随访记录最小落地.md`。
