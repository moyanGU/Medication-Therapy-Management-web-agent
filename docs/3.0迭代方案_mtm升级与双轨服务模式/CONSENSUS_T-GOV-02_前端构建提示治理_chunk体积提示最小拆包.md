# CONSENSUS_T-GOV-02_前端构建提示治理_chunk体积提示最小拆包

## 一、任务共识

本轮正式启动的工程治理任务为：

- `T-GOV-02 前端构建提示治理 - chunk 体积提示最小拆包`

目标共识：

- 优先处理当前构建里下一条更可控的高价值 warning
- 用最小拆包策略改善 chunk 体积提示

---

## 二、范围共识

本任务确定只做以下内容：

1. 在 `vite.config.ts` 中加入最小 `manualChunks` 策略
2. 仅按少量重依赖组进行拆包
3. 重新执行构建验证 chunk warning 是否改善

明确不做：

1. 升级或替换三方依赖
2. 修改业务页面导入方式
3. 修改接口、路由、后端和业务逻辑
4. 直接治理 `sonner` 与 `page-agent` 的实现级 warning

---

## 三、实施方式共识

本轮实施方式确定为：

1. 优先通过 `build.rollupOptions.output.manualChunks` 做最小拆包
2. 只拆明显的重依赖组
3. 不通过提高 `chunkSizeWarningLimit` 来掩盖问题

原因共识：

1. 当前项目已具备路由级动态导入
2. 最小构建配置调整风险最低
3. 适合作为工程治理第二刀

---

## 四、文件范围共识

本轮预期变动：

1. `vite.config.ts`
2. 构建日志对应结果
3. 本轮 `ALIGNMENT / CONSENSUS / ACCEPTANCE` 文档

本轮不修改：

1. `src/pages/MtmServiceCasesPage.vue`
2. 其他业务页面与组件
3. `src/utils/mtm.ts`
4. `package.json` 与依赖版本
5. 后端代码

---

## 五、验收标准

本任务完成后，必须满足以下验收条件：

1. 最小拆包策略已落地
2. 构建仍然通过
3. chunk warning 被消除或明确改善
4. 未引入无关业务代码改动
5. 本轮范围仍保持单一治理切口

---

## 六、实施结论

`T-GOV-02` 的最终实施方案确定为：

1. 继续保持单点治理、小步、可回滚
2. 只处理 chunk 体积提示
3. 只通过 `vite.config.ts` 的最小拆包策略实施
4. 用构建结果决定是否继续下一条工程治理任务
