# ACCEPTANCE_T-P0-08_MTM服务最小模型与迁移

## 一、任务结论

`T-P0-08 MTM 服务最小模型与迁移` 已完成本轮最小可交付目标：

- 已建立独立 `apps.mtm`
- 已注册 Django app
- 已落地 5 个最小 MTM 模型
- 已补后台 admin 调试支持
- 已生成初始迁移文件
- 已完成定向模型测试

---

## 二、本轮完成项

### 2.1 App 与配置

- 在 `backend/mtm_helper/settings.py` 中注册 `apps.mtm`
- 建立 `backend/apps/mtm/migrations/__init__.py`
- 建立 `backend/apps/mtm/tests/__init__.py`

### 2.2 模型落地

已确认并保留以下 5 个模型：

1. `MTMServiceCase`
2. `MTMInterview`
3. `MTMAssessment`
4. `MTMPlan`
5. `MTMFollowUp`

关系符合共识：

- 服务单主实体
- 问诊/评估/计划一对一
- 随访一对多

### 2.3 Admin 支持

已新增 `backend/apps/mtm/admin.py`，支持：

- 服务单列表查看
- 关键字段筛选与搜索
- 服务单内联查看随访记录
- 问诊/评估/计划/随访独立后台维护

### 2.4 迁移与测试

已生成：

- `backend/apps/mtm/migrations/0001_initial.py`

已新增：

- `backend/apps/mtm/tests/test_models.py`

---

## 三、验证结果

### 3.1 迁移生成验证

已执行：

```bash
.\.venv\Scripts\python.exe manage.py makemigrations mtm
```

结果：

- 成功生成 `0001_initial.py`

### 3.2 无额外待生成迁移验证

已执行：

```bash
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run mtm
```

结果：

- `No changes detected in app 'mtm'`

### 3.3 定向测试验证

已执行：

```bash
.\.venv\Scripts\python.exe manage.py test apps.mtm.tests.test_models
```

结果：

- 2 个测试全部通过
- 覆盖 `case_number` 自动生成
- 覆盖问诊/评估/计划/随访与服务单关系挂接

---

## 四、已知限制

本轮未执行：

- 面向真实 MySQL 的 `manage.py migrate`

原因：

- 当前本地默认数据库 `127.0.0.1:3306` 不可连接
- `makemigrations` 与测试验证已完成，但真实库迁移需用户本地数据库可用后再执行

---

## 五、验收判断

对照 `CONSENSUS_T-P0-08_MTM服务最小模型与迁移.md`：

1. `apps.mtm` 已创建并注册：通过
2. 五个最小模型已建立：通过
3. 模型关系清晰：通过
4. `MTMServiceCase` 具备业务编号和服务状态：通过
5. 迁移文件可生成并稳定：通过
6. 未塞进现有 `plans` 或 `medical_records`：通过
7. 具备基础 admin 调试支持：通过

结论：

- `T-P0-08` 达到当前阶段可交付标准
- 可继续进入 `T-P0-09` 的 MTM 服务最小 CRUD 与状态流转实现
