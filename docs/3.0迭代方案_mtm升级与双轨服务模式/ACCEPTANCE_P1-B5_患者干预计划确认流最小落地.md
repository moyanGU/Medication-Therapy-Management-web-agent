# ACCEPTANCE P1-B5 患者干预计划确认流最小落地

## 1. 验收目标

本轮完成了 P1-B5 任务：打通患者端的干预计划接收确认流。这一环节标志着患者对药师制定的干预方案知情并反馈执行意愿，为后续随访定下基调。

## 2. 验收内容

### 2.1 后端改动
- **接口**：在 `apps.mtm.views.MTMServiceCaseViewSet` 中新增了 `POST /api/mtm/service-cases/{id}/plan/confirm/`。
- **校验**：实现了强权限校验，只有当前服务单的关联患者（`patient`）才能确认。未起草完成的计划不可确认。
- **序列化器**：新增 `MTMPlanConfirmSerializer`，限定 `status` 为 `confirmed` 或 `declined`。
- **测试**：在 `test_api.py` 中补充了患者正常确认及非本人拒绝确认等测试用例。

### 2.2 前端改动
- **API**：在 `src/api/mtm.ts` 补充了 `confirmPlan` 方法，并在 `src/types/mtm.ts` 增加对应 Payload 类型。
- **独立页**：新增了 `MtmPlanConfirmationPage.vue` 组件。该页面首先为患者以只读模式清晰展示了“药师制定的干预措施”，随后提供了单选框组（同意执行 / 暂不执行）以及可选的补充反馈文本域。
- **详情页接入**：在 `MtmServiceCaseDetailPage.vue` 获取当前登录用户，如果当前用户是患者且干预计划处于 `pending` 状态，将干预计划区块的入口替换为高亮的“前往确认”按钮。

## 3. 验收结果

- [x] 后端 `test_api.py` 共计 19 条测试用例（包括新增的确认用例及 403 用例）全部通过。
- [x] 前端 `npm run build` 修复了 `useAuthStore` 的引入缺失后成功通过构建。
- [x] 端到端交互逻辑已闭环：不同角色（药师/患者）能看到不同的入口，患者本人能进入专属确认页并完成反馈。

## 4. 下一步建议

- P1-B5 成功收口。整个 MTM “双轨服务模式”的业务流已经实现了全主线的贯通。
- 下一步可考虑：
  1. 清理现有控制台的 warning，例如 `sonner` 带来的 `"use client"` 构建提示或 PageAgent 等遗留技术债务。
  2. 补充 MTM 服务列表或总览页的相关展示优化。