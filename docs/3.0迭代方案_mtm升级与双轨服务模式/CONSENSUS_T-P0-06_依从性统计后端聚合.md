# CONSENSUS_T-P0-06_依从性统计后端聚合

## 一、任务共识

本轮正式启动的开发任务为：

- `T-P0-06 依从性统计后端聚合`

目标共识：

- 提供一条新的依从性专用聚合接口
- 让首页和统计页后续可以复用同一口径

---

## 二、接口共识

新增接口：

- `GET /api/records/medication-records/adherence/`

支持参数：

- `days`：默认 30
- `start_date`：可选，格式 `YYYY-MM-DD`
- `end_date`：可选，格式 `YYYY-MM-DD`
- `medicine_id`：可选

参数规则：

- 如果传 `start_date/end_date`，则 `current_period` 按该区间统计
- 如果不传日期区间，则按 `days` 生成当前区间
- `summary_7d` 和 `summary_30d` 固定按最近 7 天、30 天计算，不受当前区间影响

---

## 三、统计口径共识

### 3.1 主统计源

主统计源确定为：

- 提醒来源的 `MedicationRecord`

筛选规则：

- `source = reminder`
- 或 `reminder is not null`

### 3.2 状态口径

状态统计包括：

- `taken`
- `missed`
- `delayed`
- `partial`

汇总规则：

- `completed_count = taken + delayed + partial`
- `adherence_rate = completed_count / total_records * 100`
- `on_time_rate = taken / total_records * 100`

### 3.3 风险等级

本轮风险等级共识：

- `low`
  - `adherence_rate >= 90`
  - 且 `missed_count = 0`
- `medium`
  - `adherence_rate >= 70` 且 `< 90`
  - 或存在少量漏服 / 延迟
- `high`
  - `adherence_rate < 70`
  - 或连续存在明显漏服

### 3.4 响应补充信息

返回 `response_summary`，补充展示：

- `scheduled_count`
- `responded_count`
- `unresponded_count`
- `response_rate`

其来源为 `ReminderHistory`，用于补充说明提醒链路表现。

---

## 四、趋势共识

趋势数据按天返回，默认覆盖当前区间。

每个日期项至少包含：

- `date`
- `total`
- `taken`
- `missed`
- `delayed`
- `partial`
- `completed`
- `adherence_rate`
- `on_time_rate`

日期归属规则：

- 优先使用 `scheduled_time`
- 若为空，则回退到 `taken_at`

---

## 五、实现方案共识

实现位置：

- `backend/apps/records/views.py`

实现方式：

1. 在 `MedicationRecordViewSet` 中新增 `adherence` 的 detail=False GET action
2. 抽取内部聚合方法，统一生成 summary
3. 抽取趋势聚合方法，生成按天数据
4. 补充参数校验和错误处理
5. 补充定向测试

---

## 六、返回结构共识

统一响应结构仍为：

- `success`
- `message`
- `data`

`data` 中包含：

- `period`
- `summary_7d`
- `summary_30d`
- `current_period`
- `trend`

---

## 七、验收标准

本任务完成后，必须满足以下验收条件：

1. 新接口 `GET /api/records/medication-records/adherence/` 可用
2. 返回最近 7 天和 30 天依从性摘要
3. 返回当前查询区间依从性摘要
4. 返回趋势数据
5. 正确统计 `taken / missed / delayed / partial`
6. `adherence_rate` 与 `on_time_rate` 口径清晰且正确
7. 返回 `risk_level`
8. 返回提醒响应补充信息 `response_summary`
9. 至少补充定向测试并通过

---

## 八、实施结论

`T-P0-06` 的最终实施方案确定为：

1. 新增依从性专用聚合接口
2. 以提醒来源正式记录作为主统计源
3. 以提醒历史作为响应补充源
4. 输出多周期摘要、趋势和风险等级
5. 保持旧统计接口可继续使用

完成后，后端将首次具备统一、可复用的依从性聚合能力。
