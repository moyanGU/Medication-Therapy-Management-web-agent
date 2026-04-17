# MTM 项目质量治理计划 (Quality Governance Plan)

## 1. 背景与目标

在完成了 MTM 双轨服务模式（从问诊、评估、干预计划、患者确认到随访）的核心功能最小闭环后，项目代码量和复杂度有了显著提升。为了保证系统长期可维护、减少隐藏的运行时错误，以及保证多端协作代码的一致性，本项目正式开启第一阶段的**质量治理计划 (QGP, Quality Governance Plan)**。

本计划的核心目标为：**消灭代码异味、提升测试覆盖、规范化开发链路**。

## 2. 治理维度与具体任务

### 2.1 代码规范与静态检查 (Linting & Formatting)
- **前端治理**：
  - [x] 消除所有的 `eslint` 错误和警告，实现 `npm run lint` 零容忍（`--max-warnings=0`）。
  - [ ] 确保 `TypeScript` 的 `no-unused-vars`、类型声明不再成为负担，删除未使用的冗余组件（如 `emptyState` 废弃代码）。
- **后端治理**：
  - [x] 运行 `flake8` 清理所有 PEP8 格式问题（如多余的空行、缩进不一致等）。
  - [ ] 结合 `black` 与 `isort` 建立 Python 自动格式化标准。

### 2.2 单元测试与测试覆盖率 (Test Coverage)
- **后端治理**：
  - [ ] 使用 `pytest-cov` / `coverage` 工具检查 `apps.mtm` 目录的测试覆盖率。
  - [ ] 核心 API 视图层（`MTMServiceCaseViewSet`, `MTMFollowUpViewSet`）需达到 > 80% 的行覆盖率。
  - [ ] 对复杂的业务逻辑（如干预计划确认的权限判断）补充防御性用例。

### 2.3 性能优化与隐患清理 (Performance & Tech Debt)
- **前端治理**：
  - [x] 在 `vite.config.ts` 中拦截不必要的第三方库编译告警（如 Sonner 的 `"use client"`），保持控制台输出干净。
  - [ ] 移除 `PageAgent` 相关的旧时代代码残骸，减小构建体积并降低维护心智负担。
- **后端治理**：
  - [x] N+1 查询防范：复查 `get_queryset()` 等核心入口的 `select_related` 与 `prefetch_related` 是否正确配置。目前 `MTMServiceCaseViewSet` 已良好覆盖。

## 3. 本轮治理排期

1. **Phase 1 (Day 1)**：处理静态检查告警（ESLint / Flake8）与控制台干扰信息。
2. **Phase 2 (Day 2)**：后端单元测试盲区补全（Test Coverage）与前端遗留旧代码下线（PageAgent 等）。
3. **Phase 3 (Day 3)**：集成 CI / Git Hooks，使得质量规范固化。

---
> 编制日期：2026-04-17
> 状态：**执行中 (In Progress)**