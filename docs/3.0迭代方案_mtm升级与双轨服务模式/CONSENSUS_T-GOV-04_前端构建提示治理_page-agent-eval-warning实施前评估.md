# CONSENSUS_T-GOV-04_前端构建提示治理_page-agent-eval-warning实施前评估

## 一、任务共识

本轮正式启动的工程治理任务为：

- `T-GOV-04 前端构建提示治理 - @page-agent/page-controller eval warning 实施前评估`

目标共识：

- 只对 `@page-agent/page-controller` 的 `eval` warning 做实施前评估
- 明确 warning 来源、项目接入边界、风险性质和后续推荐治理路径

---

## 二、范围共识

本任务确定只做以下内容：

1. 确认构建 warning 的稳定复现情况
2. 确认业务接入点在 `src/services/pageAgentService.ts`
3. 确认库内 `PageController.executeJavascript()` 的 `eval` 来源
4. 梳理后续可能的最小治理路径

明确不做：

1. 直接修改页面助手业务逻辑
2. 直接升级 `@page-agent/*` 依赖
3. 直接 patch 三方源码
4. 直接修改 `vite.config.ts`
5. 处理其他构建 warning

---

## 三、事实判断共识

当前已确认的事实为：

1. 当前构建会稳定输出 `@page-agent/page-controller` 的 `eval` warning
2. warning 来源于三方库内部，不是项目业务代码直接书写 `eval`
3. 具体来源是 `PageController.executeJavascript()` 内部对脚本字符串执行 `eval`
4. 当前项目业务层已经把 `execute_javascript` 设为 `null`
5. 因为默认 `PageController` 仍被整包实例化，该实现仍被打进产物

---

## 四、风险性质共识

当前共识判断为：

1. 该 warning 值得继续治理
2. 但当前更接近“产物中存在不希望保留的能力实现”问题
3. 目前还不能直接判断为线上已发生的安全故障

原因共识：

1. 当前业务路径未主动开放脚本执行能力
2. 但构建产物仍携带 `eval` 相关实现，存在治理价值
3. 该问题比 `sonner` 的 `"use client"` warning 优先级更高

---

## 五、实施路径共识

后续若继续治理，当前推荐优先级为：

1. 优先评估接入层能力收缩方案
2. 其次评估自定义受限版 `PageController`
3. 最后才考虑依赖升级或 patch 三方源码

原因共识：

1. 接入层路径更小、更易回滚
2. 自定义受限版 `PageController` 仍属于项目可控边界
3. 升级依赖或 patch 三方源码的不确定性和维护成本更高

---

## 六、文件范围共识

本轮仅允许涉及：

1. `ALIGNMENT_T-GOV-04...md`
2. `CONSENSUS_T-GOV-04...md`
3. 构建日志作为验证证据

本轮不修改：

1. `src/services/pageAgentService.ts`
2. `vite.config.ts`
3. `package.json`
4. `node_modules`
5. `page-agent-main` 源码

---

## 七、验收标准

本任务完成后，必须满足以下验收条件：

1. 已明确 warning 的真实来源
2. 已明确当前业务是否实际开放该能力
3. 已明确该问题是否值得继续治理
4. 已明确后续应优先走哪类最小实施路径
5. 本轮未引入任何无关代码改动

---

## 八、实施结论

`T-GOV-04` 的最终实施方案确定为：

1. 本轮停在实施前评估，不直接改代码
2. 认定 `eval` warning 为应继续治理的高优先级工程问题
3. 认定当前最合理的下一步是单开最小实施任务，优先验证低扩散的接入层收缩方案
4. 暂不进入 page-agent 依赖升级或三方源码 patch
