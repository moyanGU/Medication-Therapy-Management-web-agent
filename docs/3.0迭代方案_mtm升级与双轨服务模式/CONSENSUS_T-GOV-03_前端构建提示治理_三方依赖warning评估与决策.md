# CONSENSUS_T-GOV-03_前端构建提示治理_三方依赖warning评估与决策

## 一、任务共识

本轮正式启动的工程治理任务为：

- `T-GOV-03 前端构建提示治理 - 三方依赖 warning 评估与决策`

目标共识：

- 对当前剩余三方依赖 warning 做风险分类与优先级判断
- 决定下一步是否值得继续治理，以及应该怎么治理

---

## 二、范围共识

本任务确定只做以下内容：

1. 评估 `sonner` 的 `"use client"` warning
2. 评估 `@page-agent/page-controller` 的 `eval` warning
3. 对两条 warning 给出优先级与后续路径建议

明确不做：

1. 直接升级或替换依赖
2. 修改业务代码或服务逻辑
3. 修改 `vite.config.ts`
4. 修改接口、路由、后端和数据流

---

## 三、风险分层共识

当前共识判断为：

1. `sonner` 的 `"use client"` warning 暂列低优先级观察项
2. `@page-agent/page-controller` 的 `eval` warning 列为更高优先级的后续评估候选

原因共识：

1. `"use client"` 更像三方库跨运行时兼容写法带来的构建提示
2. `eval` 警告更接近潜在运行时和安全边界问题
3. 但两者当前都尚未证明存在必须立即改动的业务风险

---

## 四、实施方式共识

本轮实施方式确定为：

1. 只完成对齐与共识
2. 不预设一定立刻进入代码实施
3. 如要继续治理，需单开下一轮最小实施任务

原因共识：

1. 当前 warning 都来自三方依赖内部实现
2. 直接处理可能放大为依赖迁移任务
3. 先决策，再实施，才符合当前稳定期治理方式

---

## 五、文件范围共识

本轮仅允许涉及：

1. `ALIGNMENT_T-GOV-03...md`
2. `CONSENSUS_T-GOV-03...md`

本轮不修改：

1. `src/services/pageAgentService.ts`
2. `src/composables/useToast.ts`
3. `vite.config.ts`
4. `package.json`
5. 任何业务页面与后端代码

---

## 六、验收标准

本任务完成后，必须满足以下验收条件：

1. 已明确两条剩余 warning 的风险分层
2. 已明确是否建议继续治理
3. 已明确若继续治理，下一步应如何收敛范围
4. 本轮未引入无关代码改动

---

## 七、实施结论

`T-GOV-03` 的最终实施方案确定为：

1. 保持评估优先，不直接修复
2. 当前默认不立即处理 `sonner` warning
3. 如继续工程治理，优先单开 `page-agent eval warning` 的实施前评估任务
4. 用文档冻结决策边界，避免工程治理范围失控
