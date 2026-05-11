# MTM-Helper 项目收口状态

更新时间：2026-05-11

## 本轮结论

本轮收口已经把项目的本地运行路线与 agent 现实状态进一步说清楚了，但仍不能把项目定义为 README 旧口径中的“完整智能用药生态池”。

更准确的状态是：

- 日常用药主链路具备基础产品能力
- MTM 最小专业链路已经存在
- AI 能力已经接入，但定位应保持在保守型辅助能力
- 项目本地开发标准路线已经统一到 **MySQL + Redis + Django**
- 本地 MySQL 基线已经按 `backend/.env` 打通并完成迁移验证

## 本轮新增完成项

### 1. 本地依赖检查入口补齐

新增：

- `scripts/windows/check_local_stack.ps1`
- `scripts/python/local_stack_smoke.py`

它们将本地检查拆成可验证步骤：

- MySQL CLI
- Redis CLI
- MySQL 连接
- Redis PING
- Django `manage.py check`
- Django DB / Cache smoke check

### 2. Redis 启动入口修复

修复并重写：

- `scripts/windows/start_redis_secure.ps1`

当前脚本可基于 `backend/.env` 读取 `REDIS_PASSWORD`，并在 Windows 本机正常启动 Redis。脚本同时支持：

- 通过常见安装路径或 `PATH` 自动发现 Redis
- 通过 `-RedisExe` 显式传入 Redis 可执行文件路径

### 3. auto_agent 结构评估产物补齐

新增：

- `scripts/python/build_agent_graph.py`
- `graphify-out/GRAPH_REPORT.md`
- `graphify-out/graph.json`
- `graphify-out/agent-targets.json`
- `docs/AUTO_AGENT_REALITY_ASSESSMENT.md`

本轮评估对象不是一个不存在的独立 `auto_agent` 模块，而是当前仓库中的 page-agent / assistant / session-memory / backend ai_* 组合实现。

## 本轮已验证结果

### 工程验证

已通过：

- `npm run lint`
- `npm run build`
- `npm run test:backend`
- `npm run verify`

后端测试结果：

- `84 passed`

### 本机基础设施验证

已确认：

- 本地数据库 `mtm_helper` 已创建
- 本地用户 `devuser@localhost` 已授权到 `mtm_helper.*`
- Redis 可通过仓库脚本启动
- Redis `PING` 返回 `PONG`
- Django `manage.py check` 可通过
- Django 数据库 / 缓存 smoke check 可通过
- `python manage.py migrate` 已成功完成

### 当前残余风险

当前没有阻塞本地启动的数据库权限问题，剩余风险主要是：

- Windows 脚本默认优先尝试常见安装路径，因此新机器若安装目录不同，应通过参数显式传入或将工具加入 `PATH`
- `users.PushSubscription.endpoint` 在 MySQL 下存在唯一 `CharField > 255` 的 Django 警告，本轮不阻塞运行，但后续应评估模型约束或字段设计

## auto_agent 现实判断

当前仓库中的 auto_agent 实际实现体是：

- 前端 `assistantEngine + pageAgentRuntime + sessionMemory + toolRegistry + restrictedPageController`
- 后端 `ai_page_agent + ai_session_memory + ai_medication + agents/base + agents/*`

本轮 graphify 报告显示的核心抽象包括：

- `RestrictedPageController`
- `BaseAgent`
- `buildCommonPageSnapshot()`
- `medication_guidance()`
- `executePageAgentTask()`
- `SessionMemoryAgent`
- `page_agent_chat_completions()`

这说明当前系统已经具备：

- 页面侧 Query Engine 风格主入口
- 会话记忆读写与摘要
- 有限工具注册
- 后端受限代理与子 Agent 基类

但仍缺少 Claude Code 级别的：

- 全量 Harness
- context compaction
- tool search / tool result storage
- 双层权限审查
- Swarm / team memory / coordinator mode

## 本轮收口后的建议口径

对外与对内都应统一为：

1. 本项目当前本地运行标准路线是 **MySQL + Redis**
2. PostgreSQL 适配未完成，不应再被描述为现成可用
3. 当前 AI 是“受限页面助手 + 用药问答 + 会话记忆”的组合，不应描述为成熟多 Agent 生态池
4. 新机器本地初始化时，应先按 `backend/.env` 创建 `mtm_helper` 与 `devuser`，再执行 `check_local_stack.ps1` 与 `manage.py migrate`

## 建议提交范围

建议纳入本轮收口提交的内容：

- `README.md`
- `docs/PROJECT_CLOSURE_STATUS.md`
- `docs/PROJECT_ARCHITECTURE.md`
- `docs/AUTO_AGENT_REALITY_ASSESSMENT.md`
- `graphify-out/GRAPH_REPORT.md`
- `graphify-out/graph.json`
- `graphify-out/agent-targets.json`
- `scripts/windows/check_local_stack.ps1`
- `scripts/windows/run_backend_tests.ps1`
- `scripts/python/local_stack_smoke.py`
- `scripts/python/build_agent_graph.py`
- `.gitignore`
- `backend/test_db.py`
- `backend/apps/core/views_dashboard.py`
- 本轮确认无引用、已删除的临时补丁/诊断/快照/本地产物

建议不纳入本轮收口提交的内容：

- `package.json`
- `src/components/AiAssistant.vue`
- `src/utils/api.ts`
- 其他与本轮 MySQL 基线、agent 评估、仓库清理无直接关系的用户既有改动
- 外部参考目录 `andrej-karpathy-skills-main/`、`claude_code_src-master/`、`graphify-5/`
