# MTM-Helper auto_agent 现实评估

更新时间：2026-05-10

## 评估对象

仓库中并不存在独立的 `auto_agent` 模块。

本轮按项目现实将以下代码视为“当前 auto_agent 实际实现体”：

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
  - `backend/apps/core/agents/base.py`
  - `backend/apps/core/agents/memory_agent.py`
  - `backend/apps/core/agents/medication_agent.py`
  - `backend/apps/core/agents/soap_agent.py`

图谱产物：

- `graphify-out/GRAPH_REPORT.md`
- `graphify-out/graph.json`

## graphify 结果摘要

本轮最小 graphify 扫描结果：

- 141 nodes
- 240 edges
- 8 个社区

图谱里的核心抽象：

1. `RestrictedPageController`
2. `BaseAgent`
3. `buildCommonPageSnapshot()`
4. `medication_guidance()`
5. `executePageAgentTask()`
6. `MedicationAgent`
7. `_execute_page_agent_fallback()`
8. `page_agent_chat_completions()`
9. `session_memory_summarize()`
10. `SessionMemoryAgent`

这说明当前系统中心并不是统一编排器，而是：

- 页面受限控制器
- 页面助手执行入口
- 后端 AI 代理接口
- 一个轻量子 Agent 基类

## 与 Claude Code 的能力映射

参考的 Claude Code 相关实现线索来自：

- `claude_code_src-master/src/services/compact/*`
- `claude_code_src-master/src/utils/permissions/*`
- `claude_code_src-master/src/tools/ToolSearchTool/*`
- `claude_code_src-master/src/utils/toolResultStorage.ts`
- `claude_code_src-master/src/tools/AgentTool/*`
- `claude_code_src-master/src/coordinator/coordinatorMode.ts`

### 1. Query Engine 主循环

已具备：

- 页面侧存在明确任务入口：`executePageAgentTask()`
- 后端存在代理入口：`page_agent_chat_completions()`
- 后端药学问答入口：`medication_guidance()`

缺失：

- 没有统一的、跨模式共享的主 while-loop Agent Runtime
- 没有统一的“模型输出 -> 工具调用 -> 回灌模型 -> 终止”抽象层
- 当前前端 page-agent 与后端 medication/session-memory 仍是分散入口

结论：

- **具备局部 Query Engine 形态，但还不是统一骨架**

### 2. 上下文 / 会话记忆

已具备：

- `assistantEngine.ts` 中有 route-based session id
- `sessionMemory.ts` 提供前端读写接口
- `ai_session_memory.py` 提供后端存取与 summarize 入口
- `SessionMemoryAgent` 负责摘要生成
- `assistantEngine.ts` 有 `globalContextMemory` 这一层全局记忆拼接

缺失：

- 没有 Claude Code 那样的微压缩 / 会话记忆压缩 / 完整压缩三级体系
- 没有自动 compaction 触发器
- 没有 post-compact reinjection
- 没有 file/tool result cache invalidation 体系

结论：

- **已经有会话记忆，但仍是轻量摘要型，不是完整上下文管理系统**

### 3. 工具注册与工具契约

已具备：

- `toolRegistry.ts` 提供最小注册表
- `pageAgentRuntime.ts` 能把已注册工具桥接给 `PageAgentCore`
- 前端存在受限页面快照工具与业务快照工具

缺失：

- 没有 ToolSearch
- 没有工具分层加载
- 没有大输出存储与摘要指针
- 没有统一的工具元信息结构
  - 输入校验
  - 权限声明
  - 并发安全
  - collapse / summary 规则

结论：

- **当前工具系统是最小注册表，不是 Claude Code 级工具平台**

### 4. 权限与约束边界

已具备：

- `RestrictedPageController` 明确限制页面可执行动作
- `pageAgentRuntime.ts` 明确禁掉自动提交类能力
- `ai_medication.py` 有意图分类与阻断
- `BaseAgent` 和后端入口整体仍采取保守能力边界

缺失：

- 没有 Bash classifier
- 没有 YOLO classifier
- 没有编码化的多级 permission mode
- 没有统一 Hook Registry
- 没有通用的“生成与审查分离”执行链

结论：

- **当前有场景化限制，但还没有通用权限框架**

## 已具备 / 缺失 / 本轮不做

### 已具备

- 页面助手任务入口
- 受限页面控制器
- 会话记忆读写与摘要
- 后端子 Agent 基类
- 保守型问答与页面代理能力

### 缺失

- 统一 Query Engine 主循环
- 上下文三级压缩
- ToolSearch
- Tool result storage
- 通用权限分类器
- 多 Agent 协调与 team memory

### 本轮不做

- 不照搬 Claude Code 源码
- 不实现完整 Harness
- 不实现 Swarm / Coordinator Mode
- 不大改当前 page-agent 架构
- 不为未来能力提前搭建过度抽象层

## 本轮结论

如果按现实口径定义，MTM-Helper 当前的 auto_agent 不是“生态池”，而是一个：

- 以前端 page-agent 为入口
- 以后端受限 AI 代理为补充
- 带轻量会话记忆
- 带有限工具注册
- 带场景化权限收缩

的 **受限辅助 Agent 组合体**。

这是一个可以继续演进的基础，但距离 Claude Code 风格的完整 Agent Harness 还有明显差距。
