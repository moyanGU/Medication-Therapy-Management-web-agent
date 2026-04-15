# CONSENSUS_T-GOV-05B_前端构建提示治理_自定义受限版PageController设计与实现评估

## 一、任务共识

本轮正式启动的工程治理任务为：

- `T-GOV-05B 前端构建提示治理 - 自定义受限版 PageController 设计与实现评估`

本轮目标共识：

1. 只评估 `05B` 是否具备可实施性
2. 只冻结推荐实现方向、最小方法集和风险边界
3. 本轮不直接改代码

---

## 二、范围共识

本任务确定只做以下内容：

1. 基于 `T-GOV-04` 与 `T-GOV-05A` 的现有结果继续分析
2. 核对 `PageAgentCore` 与当前业务对控制器的真实依赖
3. 判断 `05B` 的主路径方案与非主路径方案
4. 输出 `ALIGNMENT_T-GOV-05B`、`CONSENSUS_T-GOV-05B`、`DESIGN_T-GOV-05B`

明确不做：

1. 直接实现 `RestrictedPageController`
2. 直接修改 `pageAgentRuntime.ts`
3. 直接删掉 `@page-agent/page-controller`
4. 直接处理其他 warning
5. 升级依赖或 patch 三方源码

---

## 三、事实共识

当前已确认的事实为：

1. `T-GOV-05A` 已完成接入层收缩，但 `eval warning` 仍存在
2. warning 根因仍是默认 `PageController.executeJavascript()` 的内部 `eval`
3. 当前业务层已禁用 `ask_user`、`click_element_by_index`、`input_text`、`select_dropdown_option`、`execute_javascript`
4. 当前页面助手主路径更偏保守分析、快照总结、草稿识别和人工确认跳转
5. `PageAgentCore` 源码中对 `PageController` 的引用是类型引用
6. 本地 `node_modules/@page-agent/core` 产物中未检索到 `@page-agent/page-controller` 运行时字符串
7. 这说明若项目侧不再运行时导入默认 `PageController`，理论上有机会将其从实际构建图中剥离

---

## 四、主路径共识

`T-GOV-05B` 的唯一推荐主路径确定为：

1. 在项目内实现本地 `RestrictedPageController`
2. 由 `pageAgentRuntime.ts` 用该本地受限控制器替换默认 `PageController`
3. 明确保留当前主路径必需能力
4. 明确屏蔽当前业务不承诺的高风险交互能力

明确不选以下路径：

1. 继承默认 `PageController` 后只覆写 `executeJavascript()`
2. 包装默认 `PageController` 再透传大部分方法
3. 第一版就完整迁移三方 `page-controller` DOM 管线

原因共识：

1. 只要运行时仍导入默认控制器，就很难真正达成 `05B` 目标
2. 完整迁移三方管线会把任务放大为高维护成本工程
3. 受限版本地实现更符合当前小步可回滚原则

---

## 五、最小方法集共识

`RestrictedPageController` 第一版最小必需方法共识为：

1. `getBrowserState()`
2. `getLastUpdateTime()`
3. `scroll()`
4. `showMask()`
5. `hideMask()`
6. `cleanUpHighlights()`
7. `dispose()`

第一版建议显式实现为“禁用返回”的方法共识为：

1. `clickElement()`
2. `inputText()`
3. `selectOption()`
4. `executeJavascript()`
5. `scrollHorizontally()`

原因共识：

1. 生命周期与内部基础工具仍需要稳定方法面
2. 当前业务并不依赖点击、输入、脚本执行能力
3. 显式禁用比缺失方法更稳定、更可诊断

---

## 六、观察质量共识

当前共识判断为：

1. `05B` 的主要风险是页面观察质量下降
2. 第一版不应追求完整复刻默认控制器输出
3. 第一版应优先复用项目现有页面摘要能力，构造可接受的 `BrowserState`
4. 后续是否需要补充更细的 DOM 提取能力，应以实际分析质量为准

这意味着：

- `05B` 的验收不能只看 warning 是否变化，还要看页面助手分析结果是否保持可用

---

## 七、文件边界共识

本轮仅允许涉及：

1. `ALIGNMENT_T-GOV-05B...md`
2. `CONSENSUS_T-GOV-05B...md`
3. `DESIGN_T-GOV-05B...md`
4. 本地源码与构建证据作为评估材料

本轮不修改：

1. `src/services/pageAgentRuntime.ts`
2. `src/services/pageAgentService.ts`
3. `src/services/pageAgentShared.ts`
4. `vite.config.ts`
5. `node_modules`
6. `page-agent-main` 源码

---

## 八、验收标准共识

本任务完成后，必须满足以下验收条件：

1. 已明确 `05B` 的唯一推荐主路径
2. 已明确为何不采用“继承默认控制器再覆写”路径
3. 已明确第一版受限控制器的最小方法集合
4. 已明确 `05B` 的核心风险是观察质量而非仅构建成败
5. 本轮未引入业务代码改动

---

## 九、实施结论

`T-GOV-05B` 的当前共识结论确定为：

1. 具备实施可行性
2. 下一步应进入详细实现设计，而不是直接写代码
3. 推荐目标是“本地受限控制器替换默认控制器，并争取将默认控制器运行时移出构建图”
4. 第一版只需覆盖当前主路径实际所需能力
