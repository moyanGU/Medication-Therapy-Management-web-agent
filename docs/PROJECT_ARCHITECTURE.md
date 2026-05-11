# MTM-Helper 项目架构总览

更新时间：2026-05-11

## 项目定位

MTM-Helper 当前是一个前后端一体化单体项目，覆盖：

- 日常用药管理
- 提醒、记录、计划、就医记录
- MTM 最小专业服务链路
- 受限页面助手、用药问答、会话记忆

当前 AI 形态是“受限辅助 Agent 组合体”，不是完整多 Agent 编排平台。

## 目录分层

### 根目录

- `src/`
  前端 Vue 3 + TypeScript 主工程
- `backend/`
  Django + DRF 后端主工程
- `scripts/`
  构建、校验、本地运维、图谱生成脚本
- `docs/`
  项目设计、阶段文档、收口文档
- `public/`
  静态资源

### 前端 `src/`

- `pages/`
  页面级视图
- `components/`
  复用 UI 组件
- `services/`
  当前 page-agent / assistant 主链路
- `stores/`
  状态管理
- `api/`
  API 封装
- `router/`
  路由
- `utils/` / `types/`
  工具与类型

### 后端 `backend/`

- `mtm_helper/settings.py`
  全局配置
- `mtm_helper/urls.py`
  全局路由装配
- `apps/authentication`
  认证与验证码
- `apps/users`
  用户资料与订阅
- `apps/medicines`
  药品管理
- `apps/reminders`
  提醒、通知、调度、历史
- `apps/records`
  服药记录
- `apps/medical_records`
  就医记录
- `apps/plans`
  用药计划
- `apps/mtm`
  MTM 服务单、问诊、评估、计划、SOAP
- `apps/core`
  公共基础、AI 代理、页面助手后端入口

## 当前 auto_agent 实际落点

当前仓库没有独立的 `auto_agent` 模块。

当前 agent 主链路主要在：

- 前端
  - `src/services/assistantEngine.ts`
  - `src/services/pageAgentRuntime.ts`
  - `src/services/pageAgentService.ts`
  - `src/services/pageAgentShared.ts`
  - `src/services/sessionMemory.ts`
  - `src/services/toolRegistry.ts`
  - `src/services/restrictedPageController.ts`
- 后端
  - `backend/apps/core/ai_page_agent.py`
  - `backend/apps/core/ai_session_memory.py`
  - `backend/apps/core/ai_medication.py`
  - `backend/apps/core/agents/*.py`

更多见：

- `graphify-out/GRAPH_REPORT.md`
- `docs/AUTO_AGENT_REALITY_ASSESSMENT.md`

## 脚本分工

### `scripts/windows/`

- `check_local_stack.ps1`
  本地 MySQL / Redis / Django 检查
- `start_redis_secure.ps1`
  本地 Redis 启动
- `run_backend_tests.ps1`
  后端测试统一入口

### `scripts/python/`

- `local_stack_smoke.py`
  Django 数据库 / 缓存 smoke check
- `build_agent_graph.py`
  当前 agent 主链路最小 graphify 入口

## 当前主文档

- `README.md`
  项目现实口径与启动说明
- `docs/PROJECT_CLOSURE_STATUS.md`
  收口状态
- `docs/AUTO_AGENT_REALITY_ASSESSMENT.md`
  agent 现实评估

## 本轮清理原则

本轮只清理：

- 仓库内无功能性引用
- 已被现有脚本或文档替代
- 明显属于一次性补丁、诊断、快照、残留产物

本轮不做：

- 大范围目录重组
- 业务模块重构
- PostgreSQL 路线扩展
