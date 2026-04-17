# ACCEPTANCE P1-B4 随访记录最小落地

## 1. 验收目标

本轮完成了 P1-B4 任务，即 MTM 服务中 **随访环节 (`following_up`)** 的最小落地。与前几个环节的“单服务单 1 对 1”模型不同，随访采用“1对多”模式，支持对同一服务单添加多次随访记录，并在详情页独立展示和进入编辑。

## 2. 验收内容

### 2.1 后端改动
- **模型**：复用现有的 `MTMFollowUp`。
- **接口**：在 `apps.mtm.views` 新增 `MTMFollowUpViewSet`，支持 `create`、`update` 和 `retrieve` 操作，并注册到 `/api/mtm/follow-ups/`。
- **序列化器**：新增 `MTMFollowUpSerializer`。
- **测试**：在 `test_api.py` 中补充了 `test_create_follow_up_creates_new_record` 和 `test_update_follow_up_modifies_existing_record` 测试用例，且全部通过。

### 2.2 前端改动
- **API**：在 `src/api/mtm.ts` 中补充了 `createFollowUp`、`updateFollowUp` 和 `getFollowUp` 方法。
- **类型**：在 `src/types/mtm.ts` 补充了 `MtmFollowUpPayload`。
- **独立页**：新增了 `MtmFollowUpFormPage.vue` 组件，支持 `新增` 和 `编辑` 两种模式。
- **详情页接入**：在 `MtmServiceCaseDetailPage.vue` 引入了随访记录的 UI 卡片区，仅当干预计划 `completed_at` 存在时，右上角展示 `+ 添加随访` 按钮。点击已有的随访记录卡片上的“编辑”按钮可进入修改模式。

## 3. 验收结果

- [x] 后端 API 的新增与编辑接口已实现，并添加了相应的单测，`python manage.py test apps.mtm.tests.test_api` 全部通过。
- [x] 前端 `npm run build` 构建通过，无类型或语法错误。
- [x] 在浏览器端到端交互逻辑已闭环：详情页根据计划状态正确控制添加随访按钮；点击进入表单支持日期、枚举的正确收集并保存；保存后回退至详情页能正确展示多条随访记录。

## 4. 下一步建议

- P1-B4 成功收口。随访记录作为 MTM 闭环服务的最末端环节，标志着 MTM 的核心业务骨架（问诊 -> 评估 -> 计划 -> 随访）的基础链条已经完全打通。
- 下一步可考虑**患者端干预计划的接收确认流**（即在计划和随访之间的患者确认动作），或是推进全局维度的优化与缺陷修复。