<div align="center">
  <img src="public/images/mtm-cover-logo.svg" alt="MTM-Helper Logo" width="120" height="120" />
  <h1>MTM-Helper</h1>
  <p>面向日常用药管理与最小 MTM 服务链路的前后端一体化项目</p>
</div>

## 项目现状

MTM-Helper 当前不是 README 旧口径里“已经完成的智能用药生态池”，而是一个已经具备以下能力的单体项目：

- 日常用药管理基础链路
  - 药品管理
  - 用药提醒
  - 用药记录
  - 用药计划
  - 就医记录
- MTM 最小专业链路
  - 服务单
  - 问诊表单
  - 评估表单
  - 干预计划
  - SOAP 药历草稿
  - PMR / MAP 报告预览
- 保守型 AI 辅助能力
  - 用药问答
  - 页面助手
  - 会话记忆总结

当前仓库中的 AI 更接近“受限工具化助手”，而不是 Claude Code 那种完整多 Agent Harness。

## 已验证能力

### 工程验证

仓库内已经有统一验证入口：

```bash
npm run verify
```

本轮已验证通过：

- 前端 `lint`
- 前端 `build`
- 后端测试 `84 passed`

### 本地依赖检查入口

Windows 本地检查入口：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows\check_local_stack.ps1
```

它会按顺序检查：

- MySQL CLI
- Redis CLI
- MySQL 连接
- Redis PING
- `python manage.py check`
- Django 数据库 / 缓存 smoke check

### 本轮本机现实结果

基于你当前机器状态，本轮已经确认：

- `backend/.env` 对应的本地数据库 `mtm_helper` 已创建
- `devuser@localhost` 已授予 `mtm_helper.*` 权限
- Redis 已可通过仓库脚本启动，并返回 `PONG`
- Django `manage.py check` 可通过
- Django 数据库与缓存 smoke check 可通过
- `python manage.py migrate` 已成功跑通本地 MySQL

## 本地开发基线

### 必需环境

- Node.js 20+
- Python 3.11+
- MySQL
- Redis

### 数据库路线

本项目当前正式收口路线是：

- 本地开发标准数据库：**MySQL**
- 本地缓存：**Redis**
- 后端测试环境：**SQLite 内存库**
- **不提供 PostgreSQL 本地运行支持**

这不是技术偏好问题，而是当前项目现实：

- Django 运行时默认使用 MySQL
- `backend/mtm_helper/__init__.py` 会在非测试环境安装 PyMySQL 驱动
- `docker-compose.yml`、生产配置、运维脚本都围绕 MySQL 展开

## 快速开始

### 1. 安装前端依赖

```bash
npm install
```

### 2. 准备后端虚拟环境

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. 初始化本地 MySQL

首次在新机器上启动前，请先创建本地开发数据库和账号。下面的 SQL 与仓库当前 `backend/.env` 保持一致：

```sql
CREATE DATABASE IF NOT EXISTS mtm_helper CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'devuser'@'localhost' IDENTIFIED BY 'Ghp880218';
ALTER USER 'devuser'@'localhost' IDENTIFIED BY 'Ghp880218';
GRANT ALL PRIVILEGES ON mtm_helper.* TO 'devuser'@'localhost';
FLUSH PRIVILEGES;
```

Windows 示例：

```powershell
mysql -uroot -p
```

如果 `mysql` 不在 `PATH`，请改用实际安装路径。

### 4. 启动本地 Redis

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows\start_redis_secure.ps1
```

如果 Redis 不在默认路径，也可以显式传入：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows\start_redis_secure.ps1 -RedisExe "C:\path\to\redis-server.exe"
```

### 5. 检查本地栈状态

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows\check_local_stack.ps1
```

如果 MySQL 或 Redis CLI 不在默认路径，也可以显式传入：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows\check_local_stack.ps1 -MySqlExe "C:\path\to\mysql.exe" -RedisCli "C:\path\to\redis-cli.exe"
```

### 6. 前端与测试验证

```bash
npm run lint
npm run build
npm run test:backend
```

或直接运行：

```bash
npm run verify
```

### 7. 启动完整后端

```powershell
cd backend
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

首次迁移时会看到一个 MySQL 警告：`users.PushSubscription.endpoint` 的唯一 `CharField` 长度超过 255。它不会阻塞本轮本地启动，但应作为后续模型收敛项保留。

## auto_agent 现实定义

本项目里没有独立名为 `auto_agent` 的模块。

当前更符合“auto_agent 实际实现体”的是这组代码：

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

本轮已基于 `graphify-5` 生成最小图谱产物：

- `graphify-out/GRAPH_REPORT.md`
- `graphify-out/graph.json`

对应评估文档见：

- `docs/AUTO_AGENT_REALITY_ASSESSMENT.md`

## 当前边界

以下内容仍然不应被视为“已完全收口”：

- 统一的多 Agent 业务编排层
- Claude Code 风格的完整 Harness
- 上下文三级压缩系统
- ToolSearch / 工具发现与大输出存储体系
- 权限分类器与双层审查器
- PostgreSQL 本地运行支持

## 许可

本项目基于 [MIT License](LICENSE) 开源。
