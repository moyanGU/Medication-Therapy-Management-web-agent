# MTM-Helper 代码体检报告（v1）

体检对象：`/workspace`（以 `backend/apps` 为主要度量范围）  
度量工具：`radon`、`pydeps`（依赖图输出为 DOT）  
参考对齐：`andrej-karpathy-skills`（作为工程行为与变更纪律基线）  

## 1. 总览结论

- 代码整体复杂度处于健康区间：平均圈复杂度（CC）约 **3.39**，大部分函数在 A 段（低复杂度）。
- 存在少量“热点”文件与“极高复杂度”函数，集中在提醒通道、统计聚合、以及核心 AI 入口聚合视图。
- 当前最大风险不是“普遍烂”，而是“局部超级集中”：一旦这些热点继续增长，将显著拖累可维护性与迭代速度。

## 2. 规模指标（radon raw）

后端 Python 文件统计（`backend/apps`）：

- 文件数：**144**
- LOC：**23427**
- SLOC：**18037**
- 注释行：**763**
- 空行：**2851**

LOC Top 10（越靠前越需要模块化拆分）：

1. `backend/apps/core/views.py`：1681
2. `backend/apps/reminders/views.py`：973
3. `backend/apps/medical_records/views.py`：831
4. `backend/apps/reminders/notifications.py`：803
5. `backend/apps/authentication/views.py`：800
6. `backend/apps/mtm/views.py`：741
7. `backend/apps/core/middleware.py`：700
8. `backend/apps/mtm/migrations/0001_initial.py`：647
9. `backend/apps/mtm/serializers.py`：567
10. `backend/apps/records/views.py`：520

## 3. 圈复杂度（radon cc）

统计口径：`radon cc -s -a backend/apps`

- 分析文件数：**108**
- 分析代码块数（函数/方法/类）：**762**
- 平均 CC：**3.39**
- Rank 分布：
  - A：648
  - B：74
  - C：33
  - D：4
  - E：1
  - F：2

### 3.1 高风险代码块（Top）

以下为最突出热点（建议优先拆分/重构/加测试护栏）：

- CC 52 (F) `Reminders.notifications._send_sms_notification`  
  文件：`backend/apps/reminders/notifications.py`
- CC 49 (F) `Reminders.history_views.metrics`  
  文件：`backend/apps/reminders/history_views.py`
- CC 31 (E) `Reminders.notifications.send_notification`  
  文件：`backend/apps/reminders/notifications.py`
- CC 28 (D) `authentication.views.register`  
  文件：`backend/apps/authentication/views.py`
- CC 24 (D) `reminders.scheduler.check_and_send_reminders`  
  文件：`backend/apps/reminders/scheduler.py`
- CC 24 (D) `authentication.views.send_verification_code`  
  文件：`backend/apps/authentication/views.py`
- CC 22 (D) `core.views._openai_chat_completion`  
  文件：`backend/apps/core/views.py`

## 4. 可维护性（radon mi）

统计口径：`radon mi -s backend/apps`

- 参与统计文件数：**144**
- 平均 MI：**82.15**
- Rank 分布：
  - A：143
  - C：1

异常点：

- `backend/apps/core/views.py` 的 MI 为 **0.00 (C)**，但文件可编译通过，说明该文件的“可维护性结构性风险”极高（通常来自：文件超大、职责过载、复杂控制流混杂、异常/分支过多）。  
  该文件建议作为“下一阶段最优先拆分对象”，并把 AI 入口、流式 SSE、领域子代理编排拆到独立模块。

## 5. 模块依赖图（pydeps）

输出产物：

- 依赖分析 JSON：`reports/code_health/pydeps_deps.txt`
- DOT 图：`reports/code_health/pydeps.dot`

说明：

- 当前环境未安装 Graphviz（`dot`），因此未生成 svg/png 图。  
- 如需生成图形文件，可在具备 Graphviz 的环境运行：`pydeps backend/apps -T svg -o pydeps.svg`

## 6. 参照 claude_code_src 的可借鉴点（可落地项）

对 `claude_code_src`（提取自 `cli.js.map` 的源码）做抽样检索后，下面这些模式对 MTM-Helper 的下一阶段“工程化”提升最有直接收益：

- **流式通道治理：单写出口 + 行协议解析器**
  - 借鉴“唯一 outbound 队列写出口”避免 SSE/WS 多路写入乱序。
  - 借鉴“增量换行解析 + 支持 prepend 插队”，用于系统通知/补充上下文不打断主流。
- **工具编排：并发安全标注 + 中断语义**
  - 将工具（或子代理）声明为 concurrency-safe / exclusive，并在执行器里做保守降级。
  - 支持“语义化取消结果”而非抛裸错误，降低前端体验成本。
- **错误分级：TelemetrySafeError**
  - 分离“用户可见错误”与“遥测错误”，避免把敏感信息写进日志/埋点（对医疗合规非常关键）。
- **记忆体系：索引文件 + 小模型挑选 Top-K**
  - 先用索引结构缩小候选，再用小模型/规则挑选 Top-K 记忆注入，避免上下文膨胀。
- **插件系统：可开关的能力模块**
  - 以“内置插件 + 市场插件”的统一抽象推进能力扩展，避免核心服务越长越臃肿。

## 7. 建议的整改优先级（从收益/风险比出发）

P0（立即做，防止热点继续爆炸）：

- 拆分 `backend/apps/core/views.py`：按“路由职责”拆分为 AI、诊断、代理编排、流式工具等子模块。
- 对 `reminders/notifications.py` 和 `reminders/history_views.py` 的高 CC 函数进行拆分，并补齐单元测试覆盖关键分支（短信通道、统计聚合）。

P1（提升“生态池”的工程韧性）：

- 建立“工具执行器/子代理执行器”统一的并发与取消语义（参考 claude_code_src 的 ToolExecutor）。
- 引入 “TelemetrySafeError” 风格的错误分级与日志屏蔽策略（尤其是 AI、认证、提醒通道）。

P2（长期演化方向）：

- 记忆索引与会话存档规范化（用于审计回放与跨端同步）。
- 插件化能力开关（把可选能力移出核心路径）。

## 8. 产物与复现命令

产物目录：

- `reports/code_health/`（原始输出与图谱）
- `docs/code_health/MTM_HELPER_CODE_HEALTH_REPORT.md`（本报告）

复现命令：

```bash
python3 -m pip install radon pydeps
radon cc -s -a backend/apps
radon mi -s backend/apps
radon raw backend/apps
pydeps backend/apps --max-bacon 2 --show-deps --deps-output reports/code_health/pydeps_deps.txt --show-dot --dot-output reports/code_health/pydeps.dot --nodot --no-output
```

