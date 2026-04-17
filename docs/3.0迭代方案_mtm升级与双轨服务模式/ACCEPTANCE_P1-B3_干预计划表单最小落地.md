# ACCEPTANCE P1-B3 干预计划表单最小落地

## 1. 验收目标

本轮完成了 P1-B3 的所有任务，为 MTM 干预计划 (`MTMPlan`) 补充了最小闭环能力：从详情页进入、手动起草保存草稿，直到完成计划，并在详情页显示已完成摘要。

## 2. 验收内容

### 2.1 后端改动
- **模型**：`apps.mtm.models.MTMPlan` 新增了 `completed_at` 字段。
- **接口**：在 `MTMServiceCaseViewSet` 中新增了 `GET/PUT /plan/` 和 `POST /plan/complete/`。
- **序列化器**：新增 `MTMPlanFormSerializer`、`MTMPlanDraftSerializer`、`MTMPlanCompleteSerializer`。
- **测试**：在 `test_api.py` 中补充了计划起草、草稿保存、计划完成的端到端接口测试，且全部通过。

### 2.2 前端改动
- **API**：在 `src/api/mtm.ts` 补充了对应的 3 个干预计划接口方法。
- **类型**：在 `src/types/mtm.ts` 补充了 `MtmPlanDraftPayload` 并修改了 `MtmPlanSummary`。
- **独立页**：新增了 `MtmPlanFormPage.vue` 组件与对应的路由。
- **详情页接入**：在 `MtmServiceCaseDetailPage.vue` 引入了 `planEntryMeta` 与对应的 UI 展示区，实现了状态徽标与计划措施列表的回看。

## 3. 验收结果

- [x] 后端 `makemigrations` 正常生成 `0002_mtmplan_completed_at.py`。
- [x] 后端接口 `python manage.py test apps.mtm.tests.test_api` 全部通过。
- [x] 前端 `npm run build` 构建通过，无类型或语法错误。
- [x] 成功闭环了从起草、暂存草稿到标记完成的全过程。

## 4. 下一步建议

- P1-B3 成功收口。当前主线可以继续推进，比如干预计划在患者端的确认（如适用），或是干预后的跟进随访 (`following_up`) 环节最小落地。