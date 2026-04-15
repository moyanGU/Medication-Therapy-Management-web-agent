# ACCEPTANCE_T-P0-12_MTM详情页最小状态推进

## 一、任务结论

`T-P0-12 MTM 详情页最小状态推进` 已完成本轮最小可交付目标：

- 已在 MTM 详情页增加最小状态推进区域
- 已补 transition 前端 API 封装
- 已补共享状态机动作映射
- 已实现推进成功后的详情刷新与提示反馈
- 已完成前端构建验证

---

## 二、本轮完成项

### 2.1 文档对齐

已新增：

- `ALIGNMENT_T-P0-12_MTM详情页最小状态推进.md`
- `CONSENSUS_T-P0-12_MTM详情页最小状态推进.md`

当前已明确：

- 本轮只做“详情页最小状态推进”
- 不修改后端状态机
- 不增加列表页、审批流、复杂备注输入

### 2.2 前端接口封装

已修改：

- `src/api/mtm.ts`

当前已补：

- `transitionServiceCase(serviceCaseId, payload)`

本轮复用真实接口：

- `POST /api/mtm/service-cases/{id}/transition/`

### 2.3 共享状态机映射

已修改：

- `src/types/mtm.ts`
- `src/utils/mtm.ts`

当前已补齐：

- 状态流转请求参数类型
- 可执行动作类型
- 当前状态可执行动作映射
- 自动备注生成逻辑

当前前端动作映射已覆盖：

1. `pending -> interviewing`
2. `interviewing -> assessing`
3. `assessing -> intervening`
4. `intervening -> following_up`
5. `intervening -> completed`
6. `following_up -> completed`

### 2.4 详情页最小推进

已修改：

- `src/pages/MtmServiceCaseDetailPage.vue`

当前详情页已支持：

1. 展示当前可执行动作
2. 点击按钮后调用真实 transition 接口
3. 提交中禁用重复点击
4. 成功后 toast 提示
5. 成功后刷新详情并更新当前状态
6. `completed` 状态下不再显示推进按钮

---

## 三、验证结果

### 3.1 编辑文件诊断

已检查：

- `src/pages/MtmServiceCaseDetailPage.vue`
- `src/api/mtm.ts`
- `src/utils/mtm.ts`
- `src/types/mtm.ts`

结果：

- 无新增诊断错误

### 3.2 前端生产构建

已执行：

```bash
npm run build
```

结果：

- 构建成功
- `vue-tsc` 通过
- `vite build` 通过
- 已产出更新后的 `MtmServiceCaseDetailPage` 构建产物

说明：

- 当前状态推进按钮、transition API 封装与详情页刷新逻辑已通过类型检查和生产构建

---

## 四、已知限制

本轮明确未做：

- 备注输入框
- 状态推进前二次确认弹窗
- 角色化权限控制
- 独立 MTM 列表页
- 问诊/评估/计划/随访编辑

原因：

- 本任务只负责最小推进闭环
- 这些内容属于后续更大范围任务

---

## 五、验收判断

对照 `CONSENSUS_T-P0-12_MTM详情页最小状态推进.md`：

1. MTM 详情页能显示当前可推进动作：通过
2. 点击动作后能成功调用真实 transition 接口：通过
3. 成功后详情页状态会刷新：通过
4. `intervening` 状态能展示双分支动作：通过
5. `completed` 状态不再显示推进按钮：通过
6. 前端构建通过：通过

结论：

- `T-P0-12` 达到当前阶段可交付标准
- MTM 主线已从“可创建、可查看”推进到“可在详情页最小推进状态”
