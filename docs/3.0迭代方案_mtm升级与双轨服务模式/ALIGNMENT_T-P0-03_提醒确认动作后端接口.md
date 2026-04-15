# ALIGNMENT_T-P0-03_提醒确认动作后端接口

## 一、原始任务

任务来源：`TASK_P0_正式拆分.md` 中的 `T-P0-03 提醒确认动作后端接口`

任务目标：

- 为现有提醒模块补充“确认已服药 / 漏服 / 延迟 / 部分服用”的正式动作接口
- 让提醒响应不再只停留在提醒次数统计，而能进入后续记录闭环

---

## 二、当前项目理解

### 2.1 现有能力

当前提醒模块已经具备：

- 提醒 CRUD
- 今日提醒、活跃提醒、统计
- `mark_responded` 简单响应计数接口
- `respond_by_subscription` 推送订阅响应接口
- 提醒历史 `ReminderHistory`

当前记录模块已经具备：

- `MedicationRecord` 用药记录模型
- 服用状态：`taken / missed / delayed / partial`
- 记录来源：`manual / reminder / import / auto`
- 与库存扣减联动

### 2.2 当前问题

现有实现存在以下缺口：

- `mark_responded` 只有简单 `response_count +1`，没有动作类型
- `respond_by_subscription` 只能从订阅端点回写响应，不适合作为正式业务接口
- 提醒响应与正式用药记录之间没有标准映射
- “提醒响应类型”和“记录状态”命名不完全一致
- 当前没有一个适合前端直接调用的“提醒确认动作”接口

---

## 三、现有代码约束

### 3.1 现有提醒视图结构

当前 `ReminderViewSet` 已采用 DRF `ModelViewSet + @action` 模式，适合继续在同一视图集内新增 detail action。

这意味着：

- 不需要新建独立 app
- 不需要新建独立视图类
- 最适合在现有 `ReminderViewSet` 上扩展新的 POST 动作

### 3.2 现有路由结构

当前 `/api/reminders/<pk>/...` 已通过显式路由挂载多个动作接口。

因此新增提醒确认动作时，适合采用：

- 详情级动作接口
- 路径形态保持与当前 reminders action 一致

### 3.3 当前数据模型约束

`MedicationRecord.quantity_taken` 必须大于 0，但 `missed` 状态又要求数量为 0。

这说明：

- `T-P0-03` 不应直接承担完整记录落库职责
- 本任务先完成“正式提醒动作接口 + 语义规范 + 响应计数与历史更新”
- 真正的记录落库与模型适配，应在 `T-P0-04` 中一起处理

---

## 四、需求边界确认

### 4.1 本任务要做什么

本任务只负责：

- 新增正式提醒确认动作接口
- 支持动作类型：
  - `taken`
  - `missed`
  - `delayed`
  - `partial`
- 校验输入参数
- 更新提醒响应计数
- 尽量复用已有提醒历史能力
- 为下一步记录落库预留清晰返回结构

### 4.2 本任务不做什么

本任务不负责：

- 完整用药记录落库
- 库存扣减最终处理
- 首页聚合
- 依从性统计最终口径
- 提醒前端页面交互
- MTM 服务骨架

---

## 五、关键歧义与当前判断

### 5.1 动作命名歧义

提醒历史当前使用：

- `taken`
- `skipped`
- `delayed`
- `ignored`

用药记录当前使用：

- `taken`
- `missed`
- `delayed`
- `partial`

当前判断：

- 新正式接口对外统一使用业务语义更明确的：
  - `taken`
  - `missed`
  - `delayed`
  - `partial`
- 与历史模型交互时，内部可做适配：
  - `missed -> skipped`

### 5.2 是否立即创建记录

当前判断：

- 不在 `T-P0-03` 强行创建 `MedicationRecord`
- 否则会和现有记录模型校验、库存扣减、幂等逻辑缠在一起
- 本任务先把动作接口正规化
- 记录创建统一放到 `T-P0-04`

### 5.3 是否替换 `respond_by_subscription`

当前判断：

- 不删除现有 `respond_by_subscription`
- 它继续服务于通知回执场景
- 新增正式接口用于前端页面、提醒详情、未来按钮交互

### 5.4 是否保留 `mark_responded`

当前判断：

- 可以先保留，避免影响已有调用
- 但后续业务上应逐步转向新的正式动作接口

---

## 六、需要的最小接口草案

建议新增详情级 POST 动作：

- `POST /api/reminders/{id}/confirm/`

建议输入：

- `action`
  - `taken`
  - `missed`
  - `delayed`
  - `partial`
- `taken_at` 可选
- `delay_minutes` 可选
- `quantity_taken` 可选
- `notes` 可选

建议输出：

- `success`
- `message`
- `data`
  - `reminder`
  - `action`
  - `response_recorded`
  - `record_payload`

其中 `record_payload` 作为下游 `T-P0-04` 的输入参考，不代表本任务已经正式创建记录。

---

## 七、风险点

- 动作语义不统一会导致后续统计口径混乱
- 如果在本任务里过早写入 `MedicationRecord`，会和现有记录校验冲突
- 如果直接复用 `respond_by_subscription` 作为页面接口，会把“订阅端点”这种技术参数暴露给前端业务流
- 如果不处理幂等，后续前端重复点击会引发重复统计

---

## 八、当前结论

`T-P0-03` 应采用“先正规化提醒动作接口，后在 T-P0-04 补记录落库”的策略。

推荐实现方向：

1. 在 `ReminderViewSet` 中新增 `confirm` 详情动作
2. 增加专用输入校验序列化器
3. 统一动作语义映射
4. 更新提醒响应计数和必要的提醒历史
5. 返回结构化结果，为 `T-P0-04` 提供稳定输入
