# CONSENSUS_T-GOV-01_前端构建提示治理_Browserslist数据更新

## 一、任务共识

本轮正式启动的工程治理任务为：

- `T-GOV-01 前端构建提示治理 - Browserslist 数据更新`

目标共识：

- 优先处理当前构建里最明确、最小、可直接治理的 warning
- 以最小范围清掉 `Browserslist` 数据过旧提示

---

## 二、范围共识

本任务确定只做以下内容：

1. 使用官方更新方式刷新 `Browserslist / caniuse-lite` 数据
2. 接受 lockfile 的最小必要变更
3. 重新执行构建验证 warning 是否改善

明确不做：

1. 升级项目全部依赖
2. 修改 `sonner` 和 `page-agent` 相关三方依赖行为
3. 处理 chunk 拆分和体积 warning
4. 修改任何业务页面和业务逻辑

---

## 三、实施方式共识

本轮实施方式确定为：

1. 优先使用官方命令更新 Browserslist 数据
2. 不手改 lockfile
3. 更新后立刻构建验证

原因共识：

1. 该 warning 官方路径明确
2. 风险最低
3. 适合作为工程治理第一刀

---

## 四、文件范围共识

本轮预期可能变动：

1. `package-lock.json`
2. 构建日志对应结果
3. 本轮 `ALIGNMENT / CONSENSUS / ACCEPTANCE` 文档

本轮不修改：

1. `src/pages/MtmServiceCasesPage.vue`
2. `src/utils/mtm.ts`
3. `vite.config.ts`
4. `package.json` 的业务依赖声明
5. 后端代码

---

## 五、验收标准

本任务完成后，必须满足以下验收条件：

1. `Browserslist` 数据更新已执行
2. 构建仍然通过
3. 未引入无关业务代码改动
4. 如 warning 被消除或改善，结果已明确记录
5. 本轮范围仍保持单一治理切口

---

## 六、实施结论

`T-GOV-01` 的最终实施方案确定为：

1. 继续保持单点治理、小步、可回滚
2. 只处理 `Browserslist` 数据更新
3. 不混入其他构建 warning 治理
4. 用验证结果决定后续是否进入下一条工程治理任务
