# CONSENSUS_T-P0-01_首页数据聚合接口

## 一、任务共识

本轮正式启动的开发任务为：

- `T-P0-01 首页数据聚合接口`

目标共识：

- 提供一条首页专用聚合接口
- 让首页后续只请求一次就能拿到任务、风险和摘要信息

---

## 二、接口共识

新增接口：

- `GET /api/dashboard/summary/`

权限要求：

- 必须登录

返回结构：

- `success`
- `message`
- `data`

`data` 中固定包含：

- `today_tasks`
- `risk_alerts`
- `medication_summary`
- `followup_summary`
- `adherence_summary`
- `mtm_entry_hint`

---

## 三、今日任务共识

今日任务主口径确定为：

- 今日应提醒的提醒项

完成判断规则：

- 若同一提醒在今天已有正式记录：
  - `taken`
  - `delayed`
  - `partial`
  - `missed`
  均视为“已处理”

待完成判断：

- 今日提醒存在
- 但今天尚无对应正式记录

返回字段至少包括：

- `date`
- `total`
- `completed`
- `pending`
- `items`

---

## 四、风险提醒共识

首页风险提醒首版只聚合以下四类：

1. `low_stock`
2. `expiring_soon`
3. `adherence_risk`
4. `followup_due`

每条风险包含：

- `type`
- `level`
- `title`
- `count`
- `message`

---

## 五、药品与复诊摘要共识

### 5.1 medication_summary

至少包含：

- `total_medicines`
- `active_reminders`
- `low_stock_count`
- `expiring_soon_count`
- `low_stock_items`
- `expiring_soon_items`

### 5.2 followup_summary

至少包含：

- `due_count`
- `upcoming_count`
- `next_followup`
- `due_items`

其中：

- `due_count`：已到期复诊数量
- `upcoming_count`：未来 7 天内需要复诊数量
- `next_followup`：最近一条未过期复诊

---

## 六、依从性摘要共识

首页依从性摘要直接复用：

- `GET /api/records/medication-records/adherence/`

首页只透出其摘要部分，不在首页接口中重新定义新口径。

首版返回：

- `summary_7d`
- `summary_30d`
- `current_period`

---

## 七、MTM 提示共识

首页只返回“是否建议进入专业服务”的提示，不创建服务单。

首版推荐规则：

- 药品总数 `>= 5`
- 最近 7 天依从性 `< 70`
- 存在复诊到期
- 风险提醒数量 `>= 2`

返回字段：

- `recommended`
- `reason_count`
- `reasons`
- `message`

---

## 八、实现方案共识

实施位置：

- `backend/apps/core/views.py`
- `backend/apps/core/urls.py`

实施方式：

1. 新增首页聚合函数
2. 直接查询各业务模型或复用既有聚合逻辑
3. 保持统一响应结构
4. 补充定向测试

---

## 九、验收标准

本任务完成后，必须满足以下验收条件：

1. 新接口 `GET /api/dashboard/summary/` 可用
2. 接口返回固定六块数据结构
3. 今日任务能区分已完成和待完成
4. 风险提醒至少覆盖低库存、临期、依从性、复诊到期
5. 依从性摘要来自正式记录闭环口径
6. MTM 提示能根据规则返回推荐结果
7. 空数据用户也能返回结构化空态
8. 至少补充定向测试并通过

---

## 十、实施结论

`T-P0-01` 的最终实施方案确定为：

1. 在 `core` 中新增首页聚合接口
2. 固定输出六块首页数据
3. 用正式记录判断今日任务完成状态
4. 复用 `T-P0-06` 的依从性聚合结果
5. 用规则生成 MTM 入口提示

完成后，首页前端即可从“多接口拼装”切换为“单接口渲染”。
