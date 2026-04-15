# CONSENSUS_T-P0-09_MTM服务基础CRUD与状态流转

## 一、任务共识

本轮正式启动的开发任务为：

- `T-P0-09 MTM 服务基础 CRUD 与状态流转`

目标共识：

- 为 `apps.mtm` 提供首批正式 API
- 让系统中第一条 MTM 服务单可以被创建、查看并流转状态

---

## 二、接口范围共识

本任务确定只做以下 4 类接口：

1. 服务单创建
2. 服务单列表
3. 服务单详情
4. 服务单状态流转

明确不做：

- 问诊 CRUD
- 评估 CRUD
- 干预计划 CRUD
- 随访 CRUD
- 服务单删除
- 服务单通用 PATCH 字段编辑

---

## 三、路由共识

本任务确定：

- 新增 `apps.mtm.urls`
- 挂载到 `/api/mtm/`

最终最小接口集合确定为：

1. `GET /api/mtm/service-cases/`
2. `POST /api/mtm/service-cases/`
3. `GET /api/mtm/service-cases/{id}/`
4. `POST /api/mtm/service-cases/{id}/transition/`

---

## 四、数据权限共识

当前项目没有正式药师权限体系，因此本轮采用最小参与者访问规则：

- 当前用户是 `patient`
- 或当前用户是 `assigned_pharmacist`

满足任一条件即可访问该服务单。

创建时确定：

- `patient` 直接使用当前登录用户
- 不允许前端传入其他患者 ID 冒充创建

---

## 五、序列化范围共识

本任务确定至少拆分以下序列化器：

1. `MTMServiceCaseCreateSerializer`
2. `MTMServiceCaseListSerializer`
3. `MTMServiceCaseDetailSerializer`
4. `MTMServiceCaseTransitionSerializer`

详情序列化器确定包含：

- 服务单主信息
- 问诊信息摘要
- 评估信息摘要
- 干预计划摘要
- 随访记录列表

目的：

- 保持详情接口首版就可直接被后续最小前端复用

---

## 六、创建接口共识

创建接口确定为：

- `POST /api/mtm/service-cases/`

首版允许创建的最小字段确定为：

- `trigger_source`
- `service_goal`
- `notes`

首版创建行为确定为：

- `patient = request.user`
- `status` 默认沿用模型默认值 `pending`
- `assigned_pharmacist` 默认为空

---

## 七、列表与详情共识

### 7.1 列表接口

列表接口确定返回：

- 当前用户参与的服务单
- 按 `created_at` 倒序
- 使用项目现有分页结构

列表字段最小确定为：

- `id`
- `case_number`
- `status`
- `trigger_source`
- `service_goal`
- `started_at`
- `completed_at`
- `created_at`
- 患者基础信息
- 主责药师基础信息

### 7.2 详情接口

详情接口确定返回：

- 列表字段
- `notes`
- `updated_at`
- `interview`
- `assessment`
- `plan`
- `follow_ups`

---

## 八、状态流转共识

状态流转接口确定为：

- `POST /api/mtm/service-cases/{id}/transition/`

请求体最小确定为：

- `target_status`

可选字段确定为：

- `notes`

首版合法流转规则确定为：

1. `pending -> interviewing`
2. `interviewing -> assessing`
3. `assessing -> intervening`
4. `intervening -> following_up`
5. `intervening -> completed`
6. `following_up -> completed`

补充规则确定为：

- 不允许跳过流程随意变更
- 已是目标状态时返回校验错误
- 当目标状态为 `completed` 时，自动写入 `completed_at`
- 当从 `completed` 变更到其他状态时不支持

---

## 九、实现方式共识

视图层确定采用：

- DRF `GenericViewSet`
- `CreateModelMixin`
- `ListModelMixin`
- `RetrieveModelMixin`
- `@action(detail=True, methods=["post"])`

原因：

- 与任务边界更匹配
- 避免默认暴露无共识的更新与删除动作

统一要求：

- 使用项目现有 `success_response` / `error_response`
- 保留关键日志
- 查询尽量使用 `select_related` / `prefetch_related`

---

## 十、测试共识

本任务至少覆盖以下验证点：

1. 当前用户可以创建第一条服务单
2. 列表只能看到自己参与的服务单
3. 详情可以返回主信息和关联摘要
4. 合法状态流转成功
5. 非法状态跳转被拦截
6. 非参与者访问详情返回不可见结果

---

## 十一、验收标准

本任务完成后，必须满足以下验收条件：

1. `/api/mtm/service-cases/` 可创建与列表
2. `/api/mtm/service-cases/{id}/` 可查看详情
3. `/api/mtm/service-cases/{id}/transition/` 可驱动最小状态流转
4. 非参与者无法查看他人服务单
5. 响应结构与项目统一格式一致
6. 不提前开放复杂问诊/评估/计划/随访编辑接口

---

## 十二、实施结论

`T-P0-09` 的最终实施方案确定为：

1. 在 `apps.mtm` 中补最小 API 层
2. 以 `MTMServiceCase` 作为首个对外服务实体
3. 只开放创建、列表、详情、状态流转四类接口
4. 用“参与者可见 + 顺序状态机”的方式保证首版可控
5. 为 `T-P0-10` 的最小入口接通真实后端能力
