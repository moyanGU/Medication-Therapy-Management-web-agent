# CONSENSUS_T-GOV-05A_前端构建提示治理_page-agent接入层能力收缩评估

## 一、任务共识

本轮正式启动的工程治理任务为：

- `T-GOV-05A 前端构建提示治理 - page-agent 接入层能力收缩评估`

本轮目标共识：

1. 只评估“接入层能力收缩”是否值得进入下一刀实现
2. 只判断它能否在不改业务主路径承诺的前提下，缩小 `page-agent eval` 相关实现的默认产物暴露范围
3. 本轮不直接改代码

---

## 二、范围共识

本任务确定只做以下内容：

1. 延续 `T-GOV-04` 结论，不重复争论 warning 来源
2. 核对当前 page-agent 的静态接入链路和产物暴露路径
3. 判断 `05A` 的可行目标、非目标和成功口径
4. 输出 `ALIGNMENT_T-GOV-05A` 与 `CONSENSUS_T-GOV-05A`

明确不做：

1. 直接修改 `src/App.vue`
2. 直接修改 `src/components/AiAssistant.vue`
3. 直接修改 `src/services/pageAgentService.ts`
4. 直接升级 `@page-agent/*`
5. 直接 patch 三方源码
6. 直接进入 `T-GOV-05B`

---

## 三、事实共识

当前已确认的事实为：

1. `eval warning` 的直接来源仍是 `PageController.executeJavascript()` 内部实现
2. 当前业务层已通过 `customTools.execute_javascript = null` 禁用脚本执行工具
3. `PageAgentCore` 在内部确实会删除被置空的工具，也会在未开启实验开关时删除 `execute_javascript`
4. 这些限制只影响工具可用性，不会自动移除当前项目对默认 `PageController` 的静态导入与实例化
5. `src/App.vue` 会在登录后全局挂载 `AiAssistant`
6. `src/components/AiAssistant.vue` 会静态导入 `src/services/pageAgentService.ts`
7. `src/services/pageAgentService.ts` 顶层静态导入 `@page-agent/core` 与 `@page-agent/page-controller`
8. 当前 `pageAgentService.ts` 同时承载同步 UI 轻逻辑与 page-agent 重运行时逻辑
9. 当前构建虽已存在 `vendor-page-agent` chunk，但 `page-agent` 相关产物仍处于较宽的静态可达范围

---

## 四、问题定性共识

当前共识判断为：

1. 该问题仍然值得继续治理
2. 当前主矛盾不是“业务主动调用 eval”
3. 当前主矛盾是“已禁用的高风险能力仍随着默认控制器和静态接入边界进入产物链路”
4. 因此 `05A` 的正确问题定义应是“收缩接入层静态暴露范围”，而不是“先承诺彻底清除 warning”

---

## 五、实施方向共识

后续若继续治理，`T-GOV-05A` 的优先实现方向冻结为：

1. 先拆开同步轻逻辑与 page-agent 重运行时逻辑
2. 先收缩 `PageController` 与 `PageAgentCore` 进入默认依赖图的边界
3. 先改为按需触发页面助手运行时装配
4. 不改页面助手对外入口、主流程承诺和结果语义

推荐的最小切口共识：

1. 将页面范围提示、快捷问题等纯同步逻辑从重运行时模块中分离
2. 将真正依赖 `@page-agent/core` 和 `@page-agent/page-controller` 的执行链路收口到异步运行时模块
3. 让全局 AI 助手只在进入页面助手执行链路时才装配 page-agent 运行时

---

## 六、能力边界共识

`T-GOV-05A` 可以合理承诺的收益为：

1. 缩小默认主路径和无关页面对 page-agent 运行时代码的静态暴露范围
2. 让页面助手重运行时更接近按需加载，而不是登录后全局壳层默认带入
3. 在不改业务主路径承诺的前提下，为后续更重治理保留回滚点

`T-GOV-05A` 不应承诺的结果为：

1. 单靠本任务彻底移除构建期 `eval warning`
2. 单靠本任务把 `@page-agent/page-controller` 完全移出构建图
3. 单靠本任务消除默认控制器内部 `eval`

这意味着本轮共识明确接受：

- `05A` 的目标是“缩小暴露范围”，不是“保证日志归零”

---

## 七、与 `T-GOV-05B` 的边界共识

以下情况不再属于纯 `05A`：

1. 需要自定义受限版 `PageController`
2. 需要直接替换默认控制器实现
3. 需要保证构建日志中不再出现该 warning
4. 需要让带 `eval` 的实现彻底不进入构建产物

一旦后续目标升级到以上任一条，应单独进入：

- `T-GOV-05B 自定义受限版 PageController`

---

## 八、文件边界共识

本轮仅允许涉及：

1. `ALIGNMENT_T-GOV-05A...md`
2. `CONSENSUS_T-GOV-05A...md`
3. 现有本地源码与构建产物作为证据

本轮不修改：

1. `src/App.vue`
2. `src/components/AiAssistant.vue`
3. `src/services/pageAgentService.ts`
4. `vite.config.ts`
5. `package.json`
6. `node_modules`
7. `page-agent-main` 源码

---

## 九、验收标准共识

本任务完成后，必须满足以下验收条件：

1. 已明确 `05A` 的真实目标是“产物暴露范围收缩”
2. 已明确 `05A` 的收益边界与非目标
3. 已明确 `05A` 为什么不等于“彻底消除 warning”
4. 已明确 `05A` 与 `05B` 的责任边界
5. 本轮未引入任何业务代码改动

---

## 十、实施结论

`T-GOV-05A` 的最终共识结论确定为：

1. 可以作为下一刀优先实施路径
2. 目标必须冻结为“收缩 page-agent 运行时在默认主路径中的静态产物暴露范围”
3. 后续实现时应优先走“模块分层 + 按需装配”的接入层路径
4. 本任务不承诺单独消除构建期 `eval warning`
5. 若后续治理目标升级为“彻底去除带 eval 的控制器实现”，则应转入 `T-GOV-05B`
