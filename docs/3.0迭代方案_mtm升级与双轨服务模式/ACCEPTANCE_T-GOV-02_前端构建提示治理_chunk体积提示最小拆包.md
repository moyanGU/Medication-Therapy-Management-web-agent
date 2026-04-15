# ACCEPTANCE_T-GOV-02_前端构建提示治理_chunk体积提示最小拆包

## 一、任务结论

`T-GOV-02 前端构建提示治理 - chunk 体积提示最小拆包` 已完成本轮最小可交付目标：

- 已在 `vite.config.ts` 中加入最小 `manualChunks` 拆包策略
- 最新构建输出中已不再出现 `Some chunks are larger than 500 kB after minification` 提示
- 已保持业务代码不变
- 已完成构建验证并确认当前第二刀工程治理可行

---

## 二、本轮完成项

### 2.1 文档对齐

已新增：

- `ALIGNMENT_T-GOV-02_前端构建提示治理_chunk体积提示最小拆包.md`
- `CONSENSUS_T-GOV-02_前端构建提示治理_chunk体积提示最小拆包.md`

当前已明确：

- 本轮只处理 chunk 体积提示
- 不处理 `sonner`、`@page-agent/page-controller` 的实现级 warning
- 不修改业务页面、业务逻辑、接口、路由和后端

### 2.2 实施结果

本轮已执行：

1. 在 `vite.config.ts` 中新增最小 `manualChunks` 策略
2. 首先按 `pdf / page-agent / toast` 三组重依赖拆包
3. 发现 `vendor-pdf` 仍超过 500k 后，再将 `jspdf` 和 `html2canvas` 进一步拆开

当前最终拆包策略包括：

1. `vendor-page-agent`
2. `vendor-toast`
3. `vendor-jspdf`
4. `vendor-html2canvas`

说明：

- 本轮只改了 `vite.config.ts`
- 未改业务导入方式
- 未提高 `chunkSizeWarningLimit`
- 未通过隐藏 warning 的方式“假治理”

---

## 三、验证结果

### 3.1 配置文件诊断

已检查：

- `vite.config.ts`

结果：

- 无新增诊断错误

### 3.2 前端生产构建

已执行：

```bash
npm run build
```

结果：

- 构建成功
- `vue-tsc` 通过
- `vite build` 通过
- `postbuild` 正常完成

### 3.3 warning 结果

本轮治理前仍存在：

- `Some chunks are larger than 500 kB after minification`

本轮治理后结果：

- 该提示已消失

当前仍保留的既有 warning：

1. `sonner` 的 `"use client"` bundling 提示
2. `@page-agent/page-controller` 的 `eval` 警告

说明：

- 这些 warning 不属于本轮治理范围
- 可作为后续工程治理候选项

---

## 四、已知限制

本轮明确未做：

1. 升级或替换三方依赖
2. 修改业务页面导入方式
3. 修改业务逻辑、接口、路由和后端
4. 直接治理 `sonner` 与 `page-agent` 的实现级 warning

原因：

- 本轮只负责 chunk 体积提示这一条单一治理切口
- 需要继续保持工程治理单点推进

---

## 五、验收判断

对照 `CONSENSUS_T-GOV-02_前端构建提示治理_chunk体积提示最小拆包.md`：

1. 最小拆包策略已落地：通过
2. 构建仍然通过：通过
3. chunk warning 被消除或明确改善：通过
4. 未引入无关业务代码改动：通过
5. 本轮范围仍保持单一治理切口：通过

结论：

- `T-GOV-02` 达到当前阶段可交付标准
- 工程治理第二刀已验证可行，下一步可转向三方库构建 warning 的评估与治理
