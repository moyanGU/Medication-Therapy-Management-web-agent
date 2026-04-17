# TASK P1-B5 患者干预计划确认流最小落地

## 任务列表

### 1. 后端 API 与序列化 (Backend API)

- [ ] 在 `apps/mtm/serializers.py` 中新增 `MTMPlanConfirmSerializer`。
- [ ] 在 `apps/mtm/views.py` 的 `MTMServiceCaseViewSet` 中新增 `confirm_plan` 动作。
- [ ] 在 `confirm_plan` 中校验请求用户必须为服务单的患者。
- [ ] 确保在更新时写入 `patient_confirmation_status`, `patient_confirmation_notes`, `confirmed_at`。

### 2. 后端测试 (Backend Tests)

- [ ] 在 `apps/mtm/tests/test_api.py` 中补充患者确认计划的端到端单测。
- [ ] 验证非患者用户无法确认。
- [ ] 验证未完成的计划无法确认。
- [ ] 执行 `manage.py test apps.mtm.tests.test_api` 并确保通过。

### 3. 前端类型与 API 封装 (Frontend Types & API)

- [ ] 在 `src/types/mtm.ts` 中补充 `MtmPlanConfirmPayload` 类型。
- [ ] 在 `src/api/mtm.ts` 中补充 `confirmPlan` 方法。

### 4. 前端页面实现 (Frontend Page)

- [ ] 新建 `src/pages/MtmPlanConfirmationPage.vue`。
- [ ] 实现干预计划摘要的只读展示。
- [ ] 实现同意/拒绝的单选逻辑和反馈输入框。
- [ ] 注册页面到路由中。

### 5. 前端详情页收口 (Frontend Detail Page)

- [ ] 在 `MtmServiceCaseDetailPage.vue` 中获取当前登录用户信息（可以从 auth store 中获取），判断是否为当前服务单的患者。
- [ ] 在干预计划区块，针对患者角色且待确认状态，新增 `前往确认` 的入口按钮。

### 6. 验收与构建 (Verification)

- [ ] 浏览器执行端到端手工测试（患者视角登录 -> 进入详情 -> 确认计划 -> 查看确认结果）。
- [ ] 运行 `npm run build` 确保无报错。
- [ ] 填写 `ACCEPTANCE_P1-B5_患者干预计划确认流最小落地.md`。
