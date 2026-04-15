# ACCEPTANCE_T-P0-09_MTM服务基础CRUD与状态流转

## 一、任务结论

`T-P0-09 MTM 服务基础 CRUD 与状态流转` 已完成本轮最小可交付目标：

- 已新增 MTM 服务单创建接口
- 已新增 MTM 服务单列表接口
- 已新增 MTM 服务单详情接口
- 已新增 MTM 服务单状态流转接口
- 已补最小权限范围控制
- 已补定向接口测试

---

## 二、本轮完成项

### 2.1 新增接口层

已新增：

- `backend/apps/mtm/serializers.py`
- `backend/apps/mtm/views.py`
- `backend/apps/mtm/urls.py`

已挂载：

- `backend/mtm_helper/urls.py`

当前可用最小接口：

1. `GET /api/mtm/service-cases/`
2. `POST /api/mtm/service-cases/`
3. `GET /api/mtm/service-cases/{id}/`
4. `POST /api/mtm/service-cases/{id}/transition/`

### 2.2 状态流转规则

本轮已落地的合法流转：

1. `pending -> interviewing`
2. `interviewing -> assessing`
3. `assessing -> intervening`
4. `intervening -> following_up`
5. `intervening -> completed`
6. `following_up -> completed`

同时已实现：

- 非法跳转拦截
- 相同状态重复提交拦截
- `completed` 自动写入 `completed_at`
- 状态备注按时间追加到服务单 `notes`

### 2.3 权限与范围

本轮已实现最小参与者可见规则：

- 当前用户是 `patient`
- 或当前用户是 `assigned_pharmacist`

创建时已固定：

- `patient = request.user`

因此前端不能伪造“替别人创建”。

### 2.4 详情内容

详情接口已返回：

- 服务单主信息
- 问诊摘要
- 评估摘要
- 干预计划摘要
- 随访记录列表

这使得后续 `T-P0-10` 可以直接复用真实详情接口。

---

## 三、验证结果

### 3.1 模型变更检查

已执行：

```bash
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run mtm
```

结果：

- `No changes detected in app 'mtm'`

说明：

- 本轮仅新增 API 层与模型方法，没有新增字段迁移

### 3.2 定向测试

已执行：

```bash
.\.venv\Scripts\python.exe manage.py test apps.mtm.tests.test_models apps.mtm.tests.test_api
```

结果：

- 共 8 个测试全部通过

覆盖点包括：

1. 当前用户创建第一条服务单
2. 列表只返回当前用户参与的服务单
3. 详情返回关联摘要块
4. 合法状态流转成功
5. 非法状态跳转被拦截
6. 非参与者无法查看他人服务单

---

## 四、已知限制

本轮明确未做：

- 问诊独立 CRUD
- 评估独立 CRUD
- 干预计划独立 CRUD
- 随访独立 CRUD
- 服务单删除
- 任意字段通用 PATCH
- 药师分配规则与正式角色体系

原因：

- 本任务只负责最小可运行主线
- 这些内容不应提前侵入 `T-P0-10` 之前的范围

---

## 五、验收判断

对照 `CONSENSUS_T-P0-09_MTM服务基础CRUD与状态流转.md`：

1. `/api/mtm/service-cases/` 可创建与列表：通过
2. `/api/mtm/service-cases/{id}/` 可查看详情：通过
3. `/api/mtm/service-cases/{id}/transition/` 可驱动状态流转：通过
4. 非参与者无法查看他人服务单：通过
5. 响应结构与项目统一格式一致：通过
6. 未提前开放复杂编辑接口：通过

结论：

- `T-P0-09` 达到当前阶段可交付标准
- 可继续进入 `T-P0-10` 的 MTM 最小入口与触发提示
