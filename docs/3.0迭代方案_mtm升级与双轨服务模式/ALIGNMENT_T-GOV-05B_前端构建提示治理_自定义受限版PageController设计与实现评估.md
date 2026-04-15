# ALIGNMENT_T-GOV-05B_前端构建提示治理_自定义受限版PageController设计与实现评估

## 一、原始任务

任务来源：

1. `T-GOV-04` 已完成 `@page-agent/page-controller eval warning` 实施前评估
2. `T-GOV-05A` 已完成接入层能力收缩实现与验收
3. `T-GOV-05A` 验收已明确：默认主路径暴露范围已收缩，但构建期 `eval warning` 仍存在

本轮用户要求：

1. 继续做 `T-GOV-05B`
2. 当前先做“设计与实现评估”
3. 本轮未要求直接进入代码实施

---

## 二、当前项目理解

### 2.1 `T-GOV-05A` 已经解决了什么

当前已确认：

1. `src/services/pageAgentService.ts` 已收缩为轻门面
2. `src/services/pageAgentShared.ts` 承载同步轻逻辑
3. `src/services/pageAgentRuntime.ts` 承载 `PageAgentCore` 与 `PageController` 运行时
4. 构建通过，且 `pageAgentRuntime` 已作为独立运行时 chunk 出现

这说明：

1. 默认主路径的静态暴露范围问题已经被最小收口
2. `05B` 不需要再重复解决“接入层收缩”
3. `05B` 的目标应进一步收敛为“替换仍含 `eval` 的默认控制器实现”

### 2.2 `T-GOV-05B` 要解决的剩余问题

`05A` 之后，仍保留的关键事实为：

1. 构建日志仍输出 `node_modules/@page-agent/page-controller/dist/lib/page-controller.js ... Use of eval ...`
2. 根源仍然是默认 `PageController.executeJavascript()` 的内部 `eval`
3. 当前业务虽然已把 `execute_javascript` 工具设为 `null`
4. 但 `pageAgentRuntime.ts` 仍在运行时导入并实例化默认 `PageController`

因此本轮问题不再是：

- 能否缩小默认暴露范围

而是：

- 能否在不破坏当前页面助手主路径承诺的前提下，用本地受限控制器替换默认 `PageController`

### 2.3 当前 page-agent 对控制器的真实依赖边界

基于本地源码重新核对，已确认：

1. `PageAgentCore` 源码对 `PageController` 的引用是类型引用
2. 本地 `node_modules/@page-agent/core` 产物中未检索到运行时字符串 `@page-agent/page-controller`
3. `PageAgentCore` 在执行期真正会调用的控制器方法包括：
   - `getBrowserState()`
   - `showMask()`
   - `hideMask()`
   - `cleanUpHighlights()`
   - `dispose()`
4. 内部工具还会按启用情况调用：
   - `getLastUpdateTime()`
   - `scroll()`
   - `scrollHorizontally()`
   - `clickElement()`
   - `inputText()`
   - `selectOption()`
   - `executeJavascript()`

这说明两个重要结论：

1. 若本地自定义控制器能结构化满足这些方法签名，理论上可以替换默认控制器
2. 若我们不再运行时导入 `@page-agent/page-controller`，有机会将该依赖从实际构建图中剥离

### 2.4 当前业务主路径真正依赖哪些能力

结合当前 `pageAgentRuntime.ts` 配置可知：

1. `ask_user` 已禁用
2. `click_element_by_index` 已禁用
3. `input_text` 已禁用
4. `select_dropdown_option` 已禁用
5. `execute_javascript` 已禁用
6. 页面助手主路径更偏：
   - 保守分析
   - 页面快照总结
   - 草稿识别
   - 人工确认后跳转

这意味着：

1. 当前业务并不依赖默认 `PageController` 的高风险交互能力
2. `05B` 需要重点保障的是：
   - 页面观察
   - 基本滚动
   - 生命周期兼容
3. 不必为已禁用工具追求完整能力复刻

### 2.5 为什么“继承默认 PageController 再覆写 executeJavascript”不是主路径

当前判断：

- 不是推荐路径

原因：

1. 继承或包装默认 `PageController` 仍然需要运行时导入 `@page-agent/page-controller`
2. 一旦运行时导入仍存在，带 `eval` 的实现大概率仍会进入构建图
3. 这不符合 `05B` 的核心目标

因此 `05B` 的主路径不能是：

- “基于默认控制器再包一层”

而应是：

- “本地实现受限版控制器，不再运行时导入默认控制器”

### 2.6 Context7 尝试结果

按规则本轮已再次优先尝试 Context7，但当前 MCP 仍返回：

- `list tools failed`

因此本轮判断继续以本地源码、现有实现与构建证据为准。

---

## 三、需求边界确认

### 3.1 本任务要做什么

本任务负责：

1. 判断 `T-GOV-05B` 是否具备可实施性
2. 明确推荐单一路径与非推荐路径
3. 梳理本地受限控制器最小需要实现的方法集合
4. 评估对当前业务主路径承诺的影响
5. 输出本轮 `ALIGNMENT`、`CONSENSUS`、`DESIGN`

### 3.2 本任务不做什么

本任务不负责：

1. 本轮直接实现 `RestrictedPageController`
2. 修改 `pageAgentRuntime.ts`
3. 处理 `sonner` warning
4. 升级 `@page-agent/*`
5. patch 三方源码

---

## 四、关键问题与当前判断

### 4.1 `05B` 是否具备实现可行性

当前判断：

- 具备，且是后续若要继续清理 `eval warning` 的唯一合理主路径

原因：

1. `PageAgentCore` 运行时不直接依赖默认控制器包
2. 当前业务已关闭高风险工具，受限控制器只需覆盖较小能力面
3. `05A` 已把运行时边界集中到 `pageAgentRuntime.ts`，便于单点替换

### 4.2 `05B` 最小实现目标应是什么

当前判断：

- 不是“做一个完整 PageController 克隆”

而是：

1. 做一个本地 `RestrictedPageController`
2. 保证当前页面助手主路径继续可用
3. 显式禁用不在业务承诺内的高风险方法
4. 尽量让 `@page-agent/page-controller` 不再进入运行时构建图

### 4.3 `05B` 最小方法集应包含什么

当前判断：

本地受限控制器至少需要实现：

1. `getBrowserState()`
2. `getLastUpdateTime()`
3. `scroll()`
4. `showMask()`
5. `hideMask()`
6. `cleanUpHighlights()`
7. `dispose()`

建议同时显式实现但返回“已禁用”结果的方法：

1. `clickElement()`
2. `inputText()`
3. `selectOption()`
4. `executeJavascript()`
5. `scrollHorizontally()`

原因：

1. 生命周期与内部 `wait` 工具需要基础方法
2. 当前业务并未承诺点击、输入、脚本执行能力
3. 显式返回“已禁用”比缺失方法更稳定、更可诊断

### 4.4 `05B` 的主要风险是什么

当前判断：

- 风险不在“构建能否通过”，而在“观察质量是否下降”

原因：

1. 默认 `PageController` 具备成熟的 DOM 提取和简化逻辑
2. 本地受限控制器若只做极简实现，可能影响 LLM 对页面结构的理解质量
3. 当前业务依赖保守分析，若观察质量明显退化，会影响页面助手体验

所以 `05B` 的关键门控不是只看 warning：

- 还必须看页面助手分析质量是否保持在可接受范围

### 4.5 `05B` 是否需要完整迁移 page-controller 内部 DOM 管线

当前判断：

- 第一版不建议完整迁移

原因：

1. 那会把 `05B` 从“受限控制器替换”膨胀为“大段三方能力本地化”
2. 维护成本会上升
3. 容易偏离当前最小可回滚原则

更合理的第一版做法是：

1. 先用项目内已有的页面摘要能力构造受限 `BrowserState`
2. 先保住当前主路径
3. 再视质量决定是否补充更细的 DOM 提取能力

---

## 五、建议结论方向

`T-GOV-05B` 当前最合理的对齐结论为：

1. 值得继续做实施设计
2. 推荐单一路径是“本地受限控制器替换默认控制器”
3. 不推荐“继承默认控制器再覆写方法”
4. 第一版目标应是“保住主路径 + 争取移除构建图中的默认控制器运行时”
5. 本轮先停在设计与实施评估，不直接改代码
