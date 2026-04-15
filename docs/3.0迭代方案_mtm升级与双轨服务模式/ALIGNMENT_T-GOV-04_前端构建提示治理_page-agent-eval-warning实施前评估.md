# ALIGNMENT_T-GOV-04_前端构建提示治理_page-agent-eval-warning实施前评估

## 一、原始任务

任务来源：

- `T-GOV-03` 已完成三方依赖 warning 的风险分层
- 用户当前明确要求：`T-GOV-04 @page-agent/page-controller eval warning 实施前评估`

当前继续方向：

- 只针对 `@page-agent/page-controller` 的 `eval` warning 做实施前评估
- 明确该 warning 的真实来源、当前使用边界、潜在治理路径与推荐优先顺序
- 本轮先冻结结论，不直接进入代码实施

---

## 二、当前项目理解

### 2.1 当前 warning 现状

当前前端构建仍可稳定通过，但构建日志里存在：

1. `node_modules/@page-agent/page-controller/dist/lib/page-controller.js ... Use of eval ... is strongly discouraged`
2. 该提示与 `sonner` 的 `"use client"` 提示不同，更接近安全边界和可压缩性边界提醒

本轮重新执行 `npm run build` 后，warning 仍然稳定复现，说明：

- 它不是偶发日志
- 它当前已经进入正式构建产物链路

### 2.2 当前项目对 page-agent 的真实接入方式

当前项目在 `src/services/pageAgentService.ts` 中直接：

1. `import { PageController } from '@page-agent/page-controller'`
2. 在 `buildPageAgentConfig()` 中实例化 `new PageController(...)`
3. 再将实例传给 `new PageAgentCore({ pageController, ... })`

这意味着：

- warning 的来源不是仓内演示代码
- 它已被当前业务页面助手能力真实依赖
- 若后续治理不当，可能直接影响页面助手可用性

### 2.3 当前 warning 的源码来源

已在仓内 `page-agent-main/packages/page-controller/src/PageController.ts` 确认：

1. `executeJavascript(script: string)` 内部使用 `eval(\`(async () => { ${script} })\`)`
2. 该实现被打包进 `node_modules/@page-agent/page-controller/dist/lib/page-controller.js`

因此当前判断为：

- warning 的直接来源在三方库内部实现
- 不是项目业务代码直接书写 `eval`

### 2.4 官方文档侧可用边界

虽然本轮按规则先尝试了 Context7，但 MCP 仍返回 `list tools failed`，无法直接取到在线官方文档。

基于仓内 page-agent 文档源码，已确认两条重要事实：

1. `customTools` 支持将 `execute_javascript` 设为 `null`，即显式移除脚本执行工具
2. `PageAgentCore` 支持接收自定义 `PageController` 实例

这说明后续治理存在两条潜在可行路径：

1. 先从“关闭脚本执行能力”入手，验证能否降低风险而不影响当前业务
2. 若仍不足，再评估“自定义受限版 PageController”替换默认实现

---

## 三、现有代码与文件约束

### 3.1 当前相关文件

本轮评估已确认的关键文件：

1. `src/services/pageAgentService.ts`
2. `page-agent-main/packages/page-controller/src/PageController.ts`
3. `page-agent-main/packages/website/src/pages/docs/features/custom-tools/page.tsx`
4. `page-agent-main/packages/website/src/pages/docs/advanced/page-controller/page.tsx`
5. `package.json`
6. 当前构建日志

### 3.2 当前能力边界

从 `src/services/pageAgentService.ts` 可见，当前项目已经主动将以下高风险内置工具设为 `null`：

1. `ask_user`
2. `click_element_by_index`
3. `input_text`
4. `select_dropdown_option`
5. `execute_javascript`

这意味着：

1. 业务层当前已经不打算开放脚本执行能力
2. 但由于默认 `PageController` 仍被整包引入，包含 `eval` 的实现仍被打进产物
3. warning 更像“已禁用能力仍被静态打包”的工程治理问题，而不是当前业务主动使用该能力

### 3.3 当前治理方式约束

本轮应优先做：

1. 评估是否存在最小、可回滚、低扩散的治理路径
2. 判断是否值得进入下一刀实施
3. 明确推荐路径与非目标

本轮不应直接做：

1. 升级 `@page-agent/core` 或 `@page-agent/page-controller`
2. 修改 `page-agent-main` 三方源码并接本地 patch
3. 重写页面助手业务逻辑
4. 顺手处理 `sonner` warning 或其他构建问题

---

## 四、需求边界确认

### 4.1 本任务要做什么

本任务负责：

1. 确认 `eval` warning 的直接来源与当前接入边界
2. 判断该 warning 是否属于值得继续治理的高优先级问题
3. 梳理后续可能的最小实施路径
4. 输出本轮 `ALIGNMENT` 与 `CONSENSUS`

### 4.2 本任务不做什么

本任务不负责：

1. 直接消除 `eval` warning
2. 修改 `src/services/pageAgentService.ts`
3. 修改 `vite.config.ts`
4. 升级或替换 page-agent 依赖
5. 输出 `ACCEPTANCE` 或最终实施结果

---

## 五、关键歧义与当前判断

### 5.1 这个 warning 是否等同于当前存在安全漏洞

当前判断：

- 不能直接等同

原因：

1. 当前业务层已经将 `execute_javascript` 设为 `null`
2. 现有页面助手主路径是保守分析和受控草稿生成
3. 但包含 `eval` 的实现仍在产物中，仍然值得作为工程治理问题继续处理

### 5.2 是否值得立刻通过升级依赖解决

当前判断：

- 不建议直接走依赖升级

原因：

1. 当前未掌握官方已修复版本证据
2. Context7 当前不可用，无法稳定确认最新官方建议
3. 依赖升级容易把单点 warning 治理放大为兼容性回归任务

### 5.3 是否值得直接打补丁删除 `eval`

当前判断：

- 暂不建议作为第一选择

原因：

1. 需要承担三方源码维护成本
2. 后续升级时容易丢补丁
3. 还未先验证更小的配置级或接入级路径

### 5.4 后续最小实施路径应优先选哪一条

当前判断：

- 优先评估“接入侧最小替换或按需拆离”，而不是直接 patch 三方源码

当前推荐优先级：

1. 先验证是否可通过接入层改造，避免将 `PageController` 整包能力暴露给当前业务主路径
2. 再评估是否需要自定义受限版 `PageController`
3. 最后才考虑依赖升级或 patch

---

## 六、建议实现边界

### 6.1 本轮建议交付内容

建议本轮只交付：

1. `ALIGNMENT_T-GOV-04`
2. `CONSENSUS_T-GOV-04`

### 6.2 若继续实施的建议切口

后续若继续工程治理，建议单开下一轮最小实施任务，并只做以下其中一条：

1. `T-GOV-05A` 接入层收缩评估与实现
2. `T-GOV-05B` 自定义受限版 `PageController` 评估与实现

不建议把以下内容混做：

1. page-agent 依赖升级
2. 三方源码 patch
3. 页面助手功能扩展
4. 其他构建 warning 治理

### 6.3 本轮建议结论方向

当前倾向结论为：

1. `eval` warning 值得继续治理
2. 但当前更像“产物侧残留能力收缩”问题，不是业务立即故障
3. 下一刀应继续保持最小范围，只验证低扩散路径

---

## 七、风险点

### 7.1 误把“构建 warning”直接判断为“线上故障”

如果跳过边界分析：

- 会导致治理优先级失真

### 7.2 直接进入三方源码 patch

如果不先试更小路径：

- 会过早引入维护负担

### 7.3 直接升级 page-agent 依赖

如果没有官方修复证据就升级：

- 可能影响页面助手当前保守分析链路

### 7.4 把实施前评估扩成架构改造

如果本轮顺手开始改接入、改构建、改依赖：

- 会违反当前工程治理的小步可回滚原则

---

## 八、当前结论

`T-GOV-04` 最合理的最小范围确定为：

- `前端构建提示治理 - @page-agent/page-controller eval warning 实施前评估`

推荐结论方向：

1. 本轮只完成证据收集、边界判断与后续路径冻结
2. 认定 warning 来源于三方库 `PageController.executeJavascript()` 的内部 `eval`
3. 认定当前业务未主动开放该能力，但默认实现仍进入打包产物
4. 后续若继续治理，应优先尝试低扩散的接入层能力收缩路径
