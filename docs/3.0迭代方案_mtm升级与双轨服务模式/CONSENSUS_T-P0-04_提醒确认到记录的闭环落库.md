# CONSENSUS_T-P0-04_提醒确认到记录的闭环落库

## 一、任务共识

本轮正式启动的开发任务为：

- `T-P0-04 提醒确认到记录的闭环落库`

目标共识：

- 让 `confirm` 接口在记录提醒响应后，同步创建或更新正式 `MedicationRecord`
- 让提醒确认真正进入后续统计链路

---

## 二、明确需求描述

本任务完成后，系统应支持：

1. 用户确认提醒后，系统同步产生正式用药记录
2. 记录可识别来源于哪条提醒
3. 记录可识别该次确认对应的计划时间
4. 已服药、漏服、延迟、部分服用都能进入正式记录
5. 库存扣减与记录状态保持一致

---

## 三、模型共识

### 3.1 `MedicationRecord` 需要新增字段

新增：

- `reminder`
- `scheduled_time`

用途：

- `reminder`：标识该记录来自哪条提醒
- `scheduled_time`：标识该次提醒原计划的服药时间

### 3.2 `quantity_taken` 规则调整

共识：

- `missed` 允许 `quantity_taken = 0`
- `taken / delayed / partial` 必须 `quantity_taken > 0`

---

## 四、动作映射共识

正式记录状态映射如下：

- `taken -> taken`
- `missed -> missed`
- `delayed -> delayed`
- `partial -> partial`

具体规则：

- `taken`
  - `taken_at` 为实际服药时间，未传则使用当前时间
  - `quantity_taken` 使用提醒剂量
- `missed`
  - `taken_at` 使用计划时间
  - `quantity_taken = 0`
- `delayed`
  - `taken_at` 优先使用用户传入时间
  - 未传时用 `scheduled_time + delay_minutes`
  - `quantity_taken` 使用提醒剂量
- `partial`
  - `taken_at` 为实际服药时间，未传则使用当前时间
  - `quantity_taken` 为用户传入的部分剂量

---

## 五、幂等共识

本任务共识：

- 使用 `user + reminder + scheduled_time` 作为本轮闭环记录的自然定位键
- 在代码层采用 `update_or_create`
- 不在本任务额外引入复杂唯一索引或额外幂等表

效果：

- 同一提醒同一计划时间重复确认时，更新同一条记录
- 不重复插入多条记录

---

## 六、库存规则共识

库存规则确定为：

- `taken`：扣减库存
- `partial`：按实际部分剂量扣减库存
- `delayed`：扣减库存
- `missed`：不扣减库存

实现要求：

- 不能继续使用“每次保存都直接扣”的粗放逻辑
- 必须改成“基于新旧记录差值修正库存”

这样才能避免：

- 同一记录更新时库存重复扣减
- 状态切换后库存失真

---

## 七、接口共识

继续沿用：

- `POST /api/reminders/{id}/confirm/`

本任务完成后，返回结构在原有基础上补充：

- `record_id`
- `record_created`
- `record_payload`

说明：

- `record_payload` 继续保留，方便前端与后续任务复用
- 但本任务完成后，它已不再只是预留数据，而是已被正式落库

---

## 八、实现方案共识

实施位置：

- `backend/apps/records/models.py`
- `backend/apps/records/serializers.py`
- `backend/apps/reminders/views.py`
- `backend/apps/records/migrations/`

实施方式：

1. 调整记录模型字段与库存逻辑
2. 调整记录序列化器校验规则
3. 在 `confirm` 接口中创建 / 更新正式记录
4. 补充定向测试，覆盖：
   - taken 落库
   - missed 落库且不扣库存
   - delayed 落库并保留延迟时间
   - partial 落库并按部分剂量扣库存
   - 重复确认不重复造记录

---

## 九、验收标准

本任务完成后，必须满足以下验收条件：

1. `confirm` 接口会同步创建或更新 `MedicationRecord`
2. `MedicationRecord` 能追踪提醒来源和计划时间
3. `taken / missed / delayed / partial` 四类动作都能合法入记录
4. `missed` 不扣库存
5. `partial` 按部分剂量扣库存
6. `delayed` 保留 `delay_minutes`
7. 重复确认同一提醒同一计划时间，不重复新增记录
8. 至少补充定向测试并通过

---

## 十、实施结论

`T-P0-04` 的最终实施方案确定为：

1. 扩展 `MedicationRecord` 以支持提醒闭环场景
2. 修正 `missed` 与数量校验冲突
3. 在 `confirm` 接口中正式落库
4. 修正库存扣减逻辑，确保更新安全
5. 用测试验证提醒闭环可用

完成后，系统将首次具备真正的：

- 提醒 -> 确认 -> 正式记录

闭环基础。
