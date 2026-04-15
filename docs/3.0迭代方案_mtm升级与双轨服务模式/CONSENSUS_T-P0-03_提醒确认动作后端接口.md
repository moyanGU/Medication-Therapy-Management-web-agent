# CONSENSUS_T-P0-03_提醒确认动作后端接口

## 一、任务共识

本轮正式启动的开发任务为：

- `T-P0-03 提醒确认动作后端接口`

目标共识：

- 在现有提醒模块中新增一个正式、可供前端直接调用的提醒确认动作接口
- 该接口用于承接“已服药 / 漏服 / 延迟 / 部分服用”四类业务动作
- 本任务不直接完成最终用药记录落库，记录落库在 `T-P0-04` 继续实现

---

## 二、明确需求描述

系统需要支持用户对单条提醒执行正式确认动作，而不是只有简单“已响应”计数。

本任务完成后，后端应支持：

1. 用户对自己的提醒执行确认动作
2. 动作类型包括：
   - `taken`
   - `missed`
   - `delayed`
   - `partial`
3. 系统校验动作输入是否合法
4. 系统记录这次提醒的业务响应结果
5. 系统返回结构化结果，供后续记录落库与前端刷新使用

---

## 三、接口共识

### 3.1 接口路径

- `POST /api/reminders/{id}/confirm/`

### 3.2 请求参数

- `action`: 必填
  - 可选值：`taken` / `missed` / `delayed` / `partial`
- `taken_at`: 可选
  - 用户实际服药时间
- `delay_minutes`: 条件必填
  - 当 `action=delayed` 时可传
- `quantity_taken`: 条件必填
  - 当 `action=partial` 时可传
- `notes`: 可选

### 3.3 返回结构

遵循项目统一响应结构：

- `success`
- `message`
- `data`

`data` 中至少包含：

- `reminder_id`
- `action`
- `response_recorded`
- `response_count`
- `record_payload`

说明：

- `record_payload` 是下一任务 `T-P0-04` 可直接使用的结构化结果
- 本任务不保证已经创建正式记录

---

## 四、数据语义共识

### 4.1 正式接口动作语义

对外统一使用以下四种动作：

- `taken`
- `missed`
- `delayed`
- `partial`

### 4.2 与提醒历史的内部映射

由于 `ReminderHistory` 当前使用的是：

- `taken`
- `skipped`
- `delayed`
- `ignored`

因此内部映射共识为：

- `taken -> taken`
- `missed -> skipped`
- `delayed -> delayed`
- `partial -> taken`

说明：

- `partial` 在提醒历史中没有完全等价类型
- 为避免修改历史模型和迁移，本任务先把 `partial` 视为“已响应且已服用”的一类，并在返回数据中保留原始动作
- 更细粒度的部分服用语义以后续正式记录为准

---

## 五、实现方案共识

### 5.1 后端实现位置

实现位置：

- `backend/apps/reminders/views.py`
- `backend/apps/reminders/serializers.py`

不新增独立 app，不新增独立服务。

### 5.2 校验方式

采用 DRF 官方推荐方式：

- 在 `ViewSet` 中使用 `@action(detail=True, methods=["post"])`
- 为请求体增加专用 serializer
- 由 serializer 负责动作参数校验

### 5.3 权限策略

沿用当前提醒对象权限：

- 仅已登录用户可访问
- 仅提醒所有者可执行确认动作

### 5.4 幂等策略

本任务共识：

- 首版不做复杂去重表
- 但应尽量避免单次请求内部重复加计数
- 若后续前端存在重复点击问题，再在 `T-P0-04` 或后续任务中补更严格幂等控制

### 5.5 历史记录策略

本任务优先策略：

- 如果来自已有提醒历史场景，继续兼容历史响应逻辑
- 正式 `confirm` 接口至少要完成提醒本体响应记录
- 是否创建新的 `ReminderHistory` 记录，以“最小改动、避免误造历史”为原则

---

## 六、边界限制

本任务明确不做：

- 创建 `MedicationRecord`
- 扣减库存
- 计算最终依从性
- 改首页
- 改提醒前端 UI
- 调整 `MedicationRecord` 现有字段设计

这些内容留给：

- `T-P0-04`
- `T-P0-05`
- `T-P0-06`

---

## 七、验收标准

本任务完成后，必须满足以下验收条件：

1. 存在正式接口 `POST /api/reminders/{id}/confirm/`
2. 支持 `taken / missed / delayed / partial` 四类动作
3. 非本人提醒不能执行确认
4. 非法动作参数会返回明确错误
5. 提醒响应次数会按规则更新
6. 返回结构中包含后续记录落库所需的 `record_payload`
7. 已有通知回执接口 `respond_by_subscription` 不被破坏
8. 至少补充针对新接口的定向测试

---

## 八、实施结论

`T-P0-03` 的最终实施方案确定为：

1. 新增提醒确认动作 serializer
2. 在 `ReminderViewSet` 中新增 `confirm` 详情级 POST action
3. 统一外部动作语义与内部历史语义映射
4. 更新响应计数并返回结构化 `record_payload`
5. 补充后端测试，验证四类动作中的关键路径

在此基础上，下一步可无缝进入：

- `T-P0-04 提醒确认到记录的闭环落库`
