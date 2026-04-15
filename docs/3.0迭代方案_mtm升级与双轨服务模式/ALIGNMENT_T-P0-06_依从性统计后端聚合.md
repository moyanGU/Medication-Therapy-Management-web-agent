# ALIGNMENT_T-P0-06_依从性统计后端聚合

## 一、原始任务

任务来源：`TASK_P0_正式拆分.md` 中的 `T-P0-06 依从性统计后端聚合`

任务目标：

- 把现有记录和提醒结果沉淀为可复用的依从性统计接口
- 用于首页和统计页统一展示

---

## 二、当前项目理解

### 2.1 已有前置能力

当前系统已经有：

- `MedicationRecord` 正式记录模型
- `ReminderHistory` 提醒历史模型
- `records/statistics/` 通用记录统计接口
- `records/trends/` 通用趋势接口
- `reminder-history/metrics/` 发送与响应指标
- `reminder-stats/summary/` 和 `reminder-stats/trend/` 基于统计表的旧接口

### 2.2 当前问题

现有统计口径是分裂的：

- `records/statistics` 更偏通用记录统计
- `reminder-history/metrics` 更偏通知链路指标
- `reminder-stats/*` 基于提醒统计表，不是本轮刚打通的正式记录闭环

这会导致：

- 首页和统计页难以复用同一接口
- “依从性”到底是按提醒算，还是按记录算，不清晰
- `taken / missed / delayed / partial` 四类状态没有统一聚合输出

---

## 三、现有代码约束

### 3.1 当前最可靠的数据源

在 `T-P0-04` 完成后，最可靠的真实服药结果来源是：

- `MedicationRecord`

原因：

- 已能承接提醒确认闭环
- 状态语义明确
- 可追踪提醒来源和计划时间

### 3.2 提醒历史仍有价值

`ReminderHistory` 仍可作为补充来源，用来提供：

- 发送量
- 响应量
- 未响应量
- 响应率

但不应再作为“正式服药结果”的唯一依据。

---

## 四、需求边界确认

### 4.1 本任务要做什么

本任务负责：

- 新增一条面向依从性的统一聚合接口
- 输出最近 7 天、最近 30 天、当前查询区间的依从性摘要
- 输出趋势数据
- 输出基础风险判断
- 输出提醒响应补充信息

### 4.2 本任务不做什么

本任务不负责：

- 首页前端展示
- 统计页前端改造
- 提醒前端交互
- MTM 服务骨架

---

## 五、关键歧义与当前判断

### 5.1 “依从性”到底按什么算

当前判断：

- 主依从性口径以 `MedicationRecord` 为准
- 只统计提醒闭环形成的正式记录：
  - `source = reminder`
  - 或 `reminder is not null`

原因：

- 这样才能代表“计划服药事件的真实执行结果”
- 手动补录记录不适合作为本轮提醒依从性主口径

### 5.2 delayed 是否算依从

当前判断：

- `delayed` 计入“已完成服药”
- 但不计入“按时服药”

因此建议同时输出：

- `adherence_rate`：完成用药率
- `on_time_rate`：按时服药率

### 5.3 partial 是否算依从

当前判断：

- `partial` 计入完成用药
- 但可在风险提示中单独识别为部分服用

### 5.4 是否仍要返回提醒链路指标

当前判断：

- 要返回
- 但作为补充字段，不作为依从性主口径

---

## 六、建议接口形态

建议新增：

- `GET /api/records/medication-records/adherence/`

建议支持参数：

- `days`
- `start_date`
- `end_date`
- `medicine_id`

建议返回结构：

- `period`
- `summary_7d`
- `summary_30d`
- `current_period`
- `trend`

其中每个 summary 至少包含：

- `total_records`
- `taken_count`
- `missed_count`
- `delayed_count`
- `partial_count`
- `completed_count`
- `adherence_rate`
- `on_time_rate`
- `avg_delay_minutes`
- `risk_level`
- `risk_flags`
- `response_summary`

---

## 七、风险点

- 如果继续沿用 `records/statistics` 的旧公式，会把“依从性”误算成“按时率”
- 如果把手动记录也混进本轮依从性统计，会稀释提醒闭环口径
- 如果不返回趋势，后续统计页仍需拼接多个旧接口
- 如果不明确风险等级阈值，首页提示会不稳定

---

## 八、当前结论

`T-P0-06` 应新增一条依从性专用聚合接口，而不是继续在旧统计接口上堆字段。

推荐实现方向：

1. 以提醒来源的 `MedicationRecord` 作为主统计源
2. 以 `ReminderHistory` 作为响应补充源
3. 同时输出 7 天、30 天、当前区间摘要
4. 输出趋势数据和风险等级
5. 保留旧统计接口，不直接破坏现有前端
