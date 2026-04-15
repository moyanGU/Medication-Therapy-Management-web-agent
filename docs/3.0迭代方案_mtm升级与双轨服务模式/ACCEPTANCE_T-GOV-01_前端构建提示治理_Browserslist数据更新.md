# ACCEPTANCE_T-GOV-01_前端构建提示治理_Browserslist数据更新

## 一、任务结论

`T-GOV-01 前端构建提示治理 - Browserslist 数据更新` 已完成本轮最小可交付目标：

- 已完成 `Browserslist / caniuse-lite` 数据刷新
- 最新构建输出中已不再出现 `Browserslist: browsers data ... is old` 提示
- 已保持业务代码不变
- 已完成构建验证并确认当前首个工程治理切口可行

---

## 二、本轮完成项

### 2.1 文档对齐

已新增：

- `ALIGNMENT_T-GOV-01_前端构建提示治理_Browserslist数据更新.md`
- `CONSENSUS_T-GOV-01_前端构建提示治理_Browserslist数据更新.md`

当前已明确：

- 本轮只处理 `Browserslist` 数据过旧提示
- 不处理 `sonner`、`@page-agent/page-controller` 和 chunk warning
- 不修改业务页面、业务逻辑、接口、路由和后端

### 2.2 实施结果

本轮已执行：

1. 使用官方推荐路径刷新 `Browserslist` 数据
2. 约束变更范围，只保留 `package-lock.json` 中的必要更新
3. 移除更新命令带出的无价值 `package.json` 根依赖副作用

当前最终实际变更为：

1. `package-lock.json` 中 `node_modules/caniuse-lite` 版本从 `1.0.30001739` 更新为 `1.0.30001788`

说明：

- 初次更新命令曾临时把 `caniuse-lite` 和 `baseline-browser-mapping` 挂到根依赖
- 已在本轮内收回该副作用
- 最终未保留无关业务依赖声明变更

---

## 三、验证结果

### 3.1 前端生产构建

已执行：

```bash
npm run build
```

结果：

- 构建成功
- `vue-tsc` 通过
- `vite build` 通过
- `postbuild` 正常完成

### 3.2 warning 结果

本轮治理前存在：

- `Browserslist: browsers data (caniuse-lite) is 8 months old`

本轮治理后结果：

- 该提示已消失

当前仍保留的既有 warning：

1. `sonner` 的 `"use client"` bundling 提示
2. `@page-agent/page-controller` 的 `eval` 警告
3. chunk 体积提示

说明：

- 这些 warning 不属于本轮治理范围
- 可作为后续工程治理候选项

---

## 四、已知限制

本轮明确未做：

1. 升级项目全部依赖
2. 修改 `sonner` 或 `page-agent` 相关三方依赖行为
3. 处理 chunk 拆分和体积 warning
4. 修改任何业务代码

原因：

- 本轮只负责首个最小工程治理切口
- 需要避免把多个构建问题混在一轮内处理

---

## 五、验收判断

对照 `CONSENSUS_T-GOV-01_前端构建提示治理_Browserslist数据更新.md`：

1. `Browserslist` 数据更新已执行：通过
2. 构建仍然通过：通过
3. 未引入无关业务代码改动：通过
4. warning 被消除或改善，结果已明确记录：通过
5. 本轮范围仍保持单一治理切口：通过

结论：

- `T-GOV-01` 达到当前阶段可交付标准
- 工程治理路线已验证可行，可以继续按同样方式处理下一条高价值构建提示
