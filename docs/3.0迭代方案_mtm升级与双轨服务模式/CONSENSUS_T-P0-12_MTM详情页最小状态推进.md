# CONSENSUS_T-P0-12_MTM详情页最小状态推进

## 一、任务共识

本轮正式启动的开发任务为：

- `T-P0-12 MTM 详情页最小状态推进`

目标共识：

- 让 MTM 服务单可以在前端详情页被最小推进
- 让用户在推进后立即看到新的状态结果

---

## 二、范围共识

本任务确定只做以下内容：

1. 新增 transition 前端 API 封装
2. 在 MTM 详情页展示合法下一步动作
3. 点击动作后调用状态流转接口
4. 成功后刷新详情与提示结果

明确不做：

- 修改后端状态机
- 新增状态
- 增加审批流
- 增加复杂备注输入
- 新增独立 MTM 列表页
- 问诊/评估/计划/随访编辑

---

## 三、数据来源与接口共识

本任务确定继续复用现有真实接口：

1. `GET /api/mtm/service-cases/{id}/`
2. `POST /api/mtm/service-cases/{id}/transition/`

`transition` 请求体共识：

- 必填：`target_status`
- 可选：`notes`

首版前端确定：

- 自动生成最小备注文案
- 不增加备注输入框

---

## 四、状态规则共识

前端展示逻辑必须严格遵守后端当前最小状态机：

1. `pending -> interviewing`
2. `interviewing -> assessing`
3. `assessing -> intervening`
4. `intervening -> following_up`
5. `intervening -> completed`
6. `following_up -> completed`

详情页按钮共识：

- `pending` 显示“进入问诊”
- `interviewing` 显示“进入评估”
- `assessing` 显示“进入干预”
- `intervening` 显示“进入随访”和“直接完成”
- `following_up` 显示“完成本次服务”
- `completed` 不显示推进按钮

---

## 五、页面交互共识

详情页首版状态推进区域确定具备以下能力：

1. 显示当前状态说明
2. 显示可执行动作按钮
3. 提交中禁用重复点击
4. 成功后 toast 提示
5. 成功后重新获取详情
6. 失败时显示明确错误

说明共识：

- 本轮定位是“最小推进”
- 不增加额外弹窗和多步确认

---

## 六、实现文件共识

本任务确定修改：

1. `src/api/mtm.ts`
2. `src/types/mtm.ts`
3. `src/utils/mtm.ts`
4. `src/pages/MtmServiceCaseDetailPage.vue`

本轮不修改：

1. 后端 `apps.mtm.views`
2. 后端 `apps.mtm.serializers`
3. 首页 `DashboardPage.vue`

---

## 七、类型与工具共识

本任务确定补充：

- transition 请求参数类型
- 状态推进动作类型
- 共享状态机映射工具

统一要求：

- 继续使用现有人话状态文案
- 关键位置打印日志
- 不重复散落写多套状态机映射

---

## 八、验收标准

本任务完成后，必须满足以下验收条件：

1. MTM 详情页能显示当前可推进动作
2. 点击动作后能成功调用真实 transition 接口
3. 成功后详情页状态会刷新
4. `intervening` 状态能展示双分支动作
5. `completed` 状态不再显示推进按钮
6. 前端构建通过

---

## 九、实施结论

`T-P0-12` 的最终实施方案确定为：

1. 在详情页原地补最小推进能力
2. 以前端按钮驱动现有 transition 接口
3. 用共享状态机映射保证前后端一致
4. 不扩展额外页面和复杂交互
