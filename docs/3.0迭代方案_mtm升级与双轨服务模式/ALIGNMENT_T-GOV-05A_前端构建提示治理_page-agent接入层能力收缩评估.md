# ALIGNMENT_T-GOV-05A_前端构建提示治理_page-agent接入层能力收缩评估

## 一、原始任务

任务来源：

- `T-GOV-04` 已完成 `@page-agent/page-controller eval warning` 的实施前评估
- 已冻结结论：优先路径为 `T-GOV-05A 接入层能力收缩`，备选路径为 `T-GOV-05B 自定义受限版 PageController`

本轮用户要求：

- 继续当前项目，严格按 `6A` 和 `high-standard-agent-playbook` 先做对齐与共识
- 只评估 `T-GOV-05A`
- 只判断“接入层能力收缩”能否在不改业务主路径承诺的前提下，最小化 `page-agent eval warning` 的产物暴露范围
- 本轮不要直接改代码

---

## 二、当前项目理解

### 2.1 问题源头没有变化

延续 `T-GOV-04` 已确认事实：

1. 构建 warning 直接来源于 `page-agent-main/packages/page-controller/src/PageController.ts`
2. 具体为 `PageController.executeJavascript()` 内部使用 `eval(...)`
3. 当前业务代码没有主动书写 `eval`
4. 当前业务层已经通过 `customTools.execute_javascript = null` 禁用了脚本执行工具

因此本轮不再重新讨论“warning 从哪来”，而是只讨论：

- 为什么它仍然进入当前产物链路
- 是否能通过接入层收缩减少默认主路径暴露

### 2.2 当前 page-agent 的真实接入边界

本轮重新核对本地代码后，确认：

1. `src/components/AiAssistant.vue` 静态导入 `src/services/pageAgentService.ts`
2. `src/App.vue` 在登录后全局挂载 `AiAssistant`
3. `src/services/pageAgentService.ts` 顶层静态导入 `@page-agent/core` 与 `@page-agent/page-controller`
4. `buildPageAgentConfig()` 中会运行时实例化 `new PageController(...)`

这说明当前不是“用户进入页面助手模式时才开始接触 page-agent”，而是：

- 只要登录后全局 AI 助手进入应用壳层
- `pageAgentService.ts` 就已经成为默认主路径静态依赖的一部分

### 2.3 当前 page-agent 运行时与同步展示逻辑被放在同一个模块

`src/services/pageAgentService.ts` 当前同时承担三类职责：

1. 页面助手运行时能力装配：`PageAgentCore`、`PageController`、`customTools`
2. 页面范围与快捷问题文案：`getCurrentPageAgentScopeDescription()`、`getPageAgentQuickActions()`
3. 页面任务执行入口：`executePageAgentTask()`

这带来一个关键工程事实：

- 即便 UI 当前只想同步读取“页面范围提示”和“快捷问题”
- 也必须静态引入包含 `PageController` 运行时代码的整个模块

所以当前问题不只是“默认控制器被用了”，更是：

- 轻量展示职责和重运行时职责没有分层

### 2.4 PageAgentCore 本身支持禁用工具，但不等于移除控制器产物

从本地 `page-agent-main` 源码可确认：

1. `PageAgentCore` 会在初始化时根据 `customTools` 将命名相同的内部工具删除
2. 当 `experimentalScriptExecutionTool` 未开启时，也会删除 `execute_javascript`
3. `PageAgentCore` 对 `PageController` 的引用在源码中是类型引用

这说明：

1. 当前“禁用脚本执行工具”的业务策略是有效的
2. 但它只影响 Agent 可调用工具集合
3. 不会自动移除我们自己在接入层显式导入并实例化的默认 `PageController`

### 2.5 当前构建产物暴露方式更像“全局壳层静态带入”

本轮结合现有 `dist` 结果观察到：

1. 已存在独立的 `vendor-page-agent` chunk
2. 但该 chunk 当前被多个页面产物链路间接引用
3. 根因更接近“全局 AI 助手壳层 + 静态导入 pageAgentService”导致的默认依赖扩散

因此本轮要评估的最小问题不是：

- 能不能一刀删除 `eval`

而是：

- 能不能先把 `page-agent` 运行时代码从默认主路径和无关页面的静态依赖中收出去

### 2.6 Context7 尝试结果

按规则本轮已优先尝试 Context7，但当前 MCP 仍返回：

- `list tools failed`

因此本轮结论仍以本地源码、现有文档和当前产物证据为准。

---

## 三、需求边界确认

### 3.1 本任务要做什么

本任务负责：

1. 判断 `T-GOV-05A` 是否值得作为下一刀最小治理路径
2. 判断它能改善什么，不能改善什么
3. 冻结“接入层能力收缩”的目标边界、非目标和验收口径
4. 输出本轮 `ALIGNMENT` 与 `CONSENSUS`

### 3.2 本任务不做什么

本任务不负责：

1. 直接改 `src/components/AiAssistant.vue`
2. 直接改 `src/services/pageAgentService.ts`
3. 直接新增动态导入实现
4. 直接升级 `@page-agent/*`
5. 直接改三方源码或打 patch
6. 直接进入 `T-GOV-05B`

---

## 四、关键问题与当前判断

### 4.1 `T-GOV-05A` 能否在不改业务主路径承诺的前提下缩小产物暴露范围

当前判断：

- 可以，且值得优先评估

原因：

1. 当前主问题是接入层把 page-agent 运行时代码和轻量 UI 展示逻辑绑在一起
2. 这类问题通常可以通过模块拆分与按需加载先做最小收口
3. 页面助手对外承诺仍可保持为“同一个全局 AI 助手入口、同一套页面助手能力、同样的任务结果形式”

也就是说，`05A` 的目标不是改业务行为，而是改：

- 运行时代码进入默认依赖图的时机
- 轻重职责的模块边界

### 4.2 `T-GOV-05A` 能否直接消除构建期 eval warning

当前判断：

- 大概率不能作为单独手段直接达成

原因：

1. 只要 `@page-agent/page-controller` 仍在构建依赖图中被打包
2. 其内部 `eval` 仍会被构建器扫描到
3. 即便改为延迟加载或独立 chunk，warning 仍可能继续出现在构建日志

因此必须明确：

- `05A` 的主要收益是“缩小默认产物暴露范围”
- 不是“承诺本轮一定让 warning 消失”

### 4.3 `T-GOV-05A` 的最小可行切口是什么

当前判断：

- 优先做“接入层分层 + 运行时异步装配”

建议后续实现时只评估以下最小切口：

1. 将页面范围提示、快捷问题等纯同步轻逻辑从 `pageAgentService.ts` 中拆出
2. 将 `PageAgentCore`、`PageController`、`executePageAgentTask()` 相关运行时代码收敛到单独异步模块
3. 在 `AiAssistant.vue` 中仅在真正进入页面助手执行链路时才触发运行时加载

这样做的目标是：

1. 保留现有页面助手主路径承诺
2. 限制 `page-agent` 运行时代码进入默认主包和无关页面路径
3. 先验证“暴露范围收缩”这个更小、更可回滚的目标

### 4.4 什么情况下 `T-GOV-05A` 会滑向 `T-GOV-05B`

当前判断：

- 一旦目标变成“完全把带 eval 的控制器实现移出构建图”，就不再属于纯 `05A`

会滑向 `05B` 或更重路径的信号包括：

1. 需要自己实现受限版 `PageController`
2. 需要改三方源码或 patch `executeJavascript`
3. 需要保证构建 warning 完全消失

### 4.5 是否需要顺手调整 vite 拆包

当前判断：

- 暂不作为 `05A` 主路径

原因：

1. 当前已有 `vendor-page-agent` 最小拆包
2. 本轮核心问题更像依赖图入口位置，而不是 chunk 命名策略
3. 若先改构建配置，容易把“接入层治理”做成“构建策略治理”

---

## 五、建议实现边界

### 5.1 `T-GOV-05A` 未来实施的单一路径建议

若后续进入实现，建议冻结以下单一路径：

1. 不动业务承诺，不改页面助手对外入口
2. 只收缩 page-agent 运行时的静态导入边界
3. 只做同步轻逻辑与重运行时逻辑分层
4. 只验证默认主路径的产物暴露范围是否收缩

### 5.2 `T-GOV-05A` 的明确非目标

后续实现时应明确不承诺：

1. 本轮彻底消除构建日志 warning
2. 本轮移除 `@page-agent/page-controller` 依赖
3. 本轮自定义新的受限控制器
4. 本轮扩展页面助手功能

### 5.3 本轮建议交付内容

本轮建议只交付：

1. `ALIGNMENT_T-GOV-05A`
2. `CONSENSUS_T-GOV-05A`

---

## 六、风险点

### 6.1 把“暴露范围收缩”误写成“warning 消失承诺”

如果目标口径不冻结：

- 后续很容易误判 `05A` 失败

### 6.2 为了追求日志干净，过早滑向 `05B`

如果后续实现时一开始就追求彻底去掉 `eval`：

- 任务会从接入层收缩膨胀成控制器替换任务

### 6.3 把同步文案函数继续留在重运行时模块里

如果只给执行函数做异步化，而 `AiAssistant.vue` 仍静态依赖整个 `pageAgentService.ts`：

- 默认主路径暴露范围不会真正收缩

### 6.4 顺手混入其他构建治理项

如果实现时同时处理：

1. `sonner` warning
2. 依赖升级
3. 构建配置重排

则会破坏当前最小治理切口

---

## 七、当前结论

`T-GOV-05A` 当前最合理的对齐结论为：

1. 值得作为下一刀优先实施路径
2. 目标应收敛为“缩小 page-agent eval 能力在默认主路径中的产物暴露范围”
3. 不应把目标误设为“单靠接入层收缩就彻底消除构建 warning”
4. 若后续仍要求彻底移除 warning，则需要单独进入 `T-GOV-05B` 或更重路径评估
