# andrej-karpathy-skills 对齐记录（v1）

本记录用于把 `andrej-karpathy-skills` 的 4 条行为原则，落到 MTM-Helper 的工程习惯、代码结构与交付物上。  
该仓库的 `CLAUDE.md` 已落地到本项目根目录：[CLAUDE.md](file:///workspace/CLAUDE.md)。

## 1) Think Before Coding（先想清楚再写）

已具备的资产：

- `docs/` 中存在大量 ALIGNMENT/CONSENSUS/ACCEPTANCE 文档体系，天然符合“先对齐再实现”的节奏。

待补齐的工程化落点：

- 把“关键歧义与决策”固化成可检索的 FAQ/Decision Log（避免每轮重新讨论同一类歧义）。
- 对高风险模块（提醒通道、AI、认证）形成“输入契约/输出契约”的最小化清单，并作为测试/验收依据。

## 2) Simplicity First（先用最小解）

当前可见风险：

- `backend/apps/core/views.py` 仍是典型的“职责过载热点”，易演化为“1000 行可以 100 行解决”的反面教材。
- 少数函数圈复杂度进入 E/F，意味着控制流已经不可直观脑补，需要模块化与测试护栏。

建议落点：

- 以“路由/职责”作为拆分边界，不引入多余抽象；每次拆分都附带“可运行的成功标准”（测试或可复现命令）。

## 3) Surgical Changes（手术刀式变更）

已具备的资产：

- 项目已有较明确的前端构建治理（T-GOV 系列）与范围约束文档，能天然限制“顺手重构”。

待补齐的工程化落点：

- 在 PR/提交规范中明确“本次变更范围”，并在验收文档里列出“未做事项”，防止扩散。
- 在高风险文件（例如 `core/views.py`）拆分时，优先做“等价重构”并保持接口行为一致，避免同时引入新需求。

## 4) Goal-Driven Execution（用可验证目标驱动）

已具备的资产：

- 多数任务文档已有验收点，但仍需要更强的“可自动验证”支撑（尤其是后端服务与提醒调度链路）。

建议落点：

- 把关键链路的验收点转为可执行脚本/测试套件：
  - 提醒调度：给定固定时间窗口与固定数据，验证应触发/不触发、失败兜底与重试策略。
  - AI 流式输出：验证 SSE 行协议、断线重连与步骤回显顺序。
  - 认证：验证码发送、注册/登录的失败分支与速率限制。

## 5) 本轮体检关联（将原则落到指标）

本轮体检报告：

- [MTM_HELPER_CODE_HEALTH_REPORT.md](file:///workspace/docs/code_health/MTM_HELPER_CODE_HEALTH_REPORT.md)

原则与指标的映射：

- Simplicity First / Surgical Changes → 关注“热点文件 LOC”与“E/F 复杂度函数”的增长趋势
- Goal-Driven Execution → 关注高风险模块的测试覆盖与可复现验证命令是否齐备

