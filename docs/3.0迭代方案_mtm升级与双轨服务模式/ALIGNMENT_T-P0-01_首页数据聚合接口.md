# ALIGNMENT_T-P0-01_首页数据聚合接口

## 一、原始任务

任务来源：`TASK_P0_正式拆分.md` 中的 `T-P0-01 首页数据聚合接口`

任务目标：

- 新增面向首页的聚合接口
- 把“今日待服药、漏服/延迟、低库存、临期、复诊提醒、依从性摘要、MTM入口提示”统一汇总给前端

---

## 二、当前项目理解

### 2.1 已有基础

当前后端已经有可复用数据源：

- `medicines/statistics/`
- `medicines/low_stock/`
- `medicines/expiring_soon/`
- `reminders/today/`
- `records/medication-records/adherence/`
- `medical-records/follow_up_due/`

当前前端首页 `DashboardPage.vue` 仍然通过多个 store 并发请求：

- 药品统计
- 提醒列表
- 今日提醒
- 未响应提醒历史

这说明首页数据已经存在，但没有统一聚合接口。

### 2.2 当前问题

现状问题主要有：

- 首页需要拼多个接口
- 首页看到的是“模块统计”，不是“今天要做什么”
- 风险信息没有统一入口
- 依从性和复诊信息还没有直接进首页
- MTM 专业入口提示没有统一后端判断

---

## 三、现有代码约束

### 3.1 接口归属

本接口不是单一业务模块的功能，而是跨：

- `reminders`
- `records`
- `medicines`
- `medical_records`

因此更适合挂在 `apps.core`，而不是硬塞进某一个业务 app。

### 3.2 返回口径需要稳定

首页后续要直接消费该接口，因此：

- 字段必须稳定
- 空数据时必须返回结构化空态
- 不应要求前端自己再组合业务判断

### 3.3 不应破坏现有接口

当前各模块已有统计接口仍在被页面使用，因此：

- 本任务新增聚合接口
- 不删除、不替换旧接口

---

## 四、需求边界确认

### 4.1 本任务要做什么

本任务负责：

- 新增首页专用聚合接口
- 输出今日任务
- 输出风险提醒
- 输出药品摘要
- 输出复诊摘要
- 输出依从性摘要
- 输出 MTM 入口提示

### 4.2 本任务不做什么

本任务不负责：

- 首页前端改版
- 提醒确认前端交互
- MTM 服务单创建
- 药师工作台

---

## 五、关键歧义与当前判断

### 5.1 “今日任务”按什么算

当前判断：

- 以“今日应该提醒的提醒项”为主
- 结合正式记录判断今天是否已完成

因此今日任务应至少包含：

- 今日总任务数
- 已完成数
- 待完成数
- 任务项列表

### 5.2 风险提醒包含什么

当前判断：

首版风险提醒只收敛到首页最有价值的四类：

- 低库存
- 即将过期
- 低依从性 / 漏服风险
- 复诊到期

不在首页首版放入过多技术指标。

### 5.3 依从性摘要用什么口径

当前判断：

- 直接复用 `T-P0-06` 新增的依从性接口结果
- 首页只取摘要部分，不再重复计算

### 5.4 MTM 入口提示如何判断

当前判断：

首版只做“提示”，不做自动创建服务单。

建议触发原因：

- 用药数量较多
- 近 7 天依从性偏低
- 存在复诊到期
- 存在多个风险提醒

### 5.5 路由路径怎么定

当前判断：

适合新增：

- `GET /api/dashboard/summary/`

挂在 `core` 下，由 `mtm_helper/urls.py` 统一纳入 `/api/` 前缀。

---

## 六、建议返回结构

建议返回：

- `today_tasks`
- `risk_alerts`
- `medication_summary`
- `followup_summary`
- `adherence_summary`
- `mtm_entry_hint`

其中：

### today_tasks

- `date`
- `total`
- `completed`
- `pending`
- `items`

### risk_alerts

- 风险列表数组
- 每条至少有：
  - `type`
  - `level`
  - `title`
  - `count`
  - `message`

### medication_summary

- `total_medicines`
- `active_reminders`
- `low_stock_count`
- `expiring_soon_count`
- `low_stock_items`
- `expiring_soon_items`

### followup_summary

- `due_count`
- `upcoming_count`
- `next_followup`
- `due_items`

### adherence_summary

- `summary_7d`
- `summary_30d`
- `current_period`

### mtm_entry_hint

- `recommended`
- `reason_count`
- `reasons`
- `message`

---

## 七、风险点

- 如果今日任务只统计提醒，不结合正式记录，会看起来“今天永远都没完成”
- 如果首页接口自己重新算依从性，会和 `T-P0-06` 口径漂移
- 如果 MTM 提示规则写在前端，后面双轨入口会分裂
- 如果返回结构不稳定，后续首页前端改造会反复改接口

---

## 八、当前结论

`T-P0-01` 应新增一条首页专用聚合接口，并放在 `core` 中统一汇总多个模块数据。

推荐实现方向：

1. 在 `apps.core.views` 中新增认证后的首页聚合函数
2. 复用现有模块查询，而不是重复造统计逻辑
3. 固定输出六块首页数据
4. MTM 入口首版只做提示，不做自动服务单创建
5. 补充接口测试，验证空态与多风险场景
