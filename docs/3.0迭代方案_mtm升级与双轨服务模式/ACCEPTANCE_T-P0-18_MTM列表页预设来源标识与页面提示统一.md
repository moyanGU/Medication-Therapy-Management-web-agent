# ACCEPTANCE_T-P0-18_MTM列表页预设来源标识与页面提示统一

## 一、任务结论

`T-P0-18 MTM 列表页预设来源标识与页面提示统一` 已完成本轮最小可交付目标：

- 已为首页 MTM 预设入口增加正式 `preset_source` 标识
- 已让 MTM 列表页识别并展示预设来源提示
- 已让列表进入详情再返回时保留该标识
- 已让用户手动改筛选时清除该标识
- 已完成前端构建验证

---

## 二、本轮完成项

### 2.1 文档对齐

已新增：

- `ALIGNMENT_T-P0-18_MTM列表页预设来源标识与页面提示统一.md`
- `CONSENSUS_T-P0-18_MTM列表页预设来源标识与页面提示统一.md`

当前已明确：

- 本轮只做预设来源标识与列表页提示统一
- 不新增后端接口
- 不修改首页入口结构和列表页筛选模型

### 2.2 共享预设来源能力

已修改：

- `src/types/mtm.ts`
- `src/utils/mtm.ts`

当前已补齐：

- MTM 列表预设来源类型
- `preset_source` 合法值集合
- 预设来源校验函数
- 预设来源标题文案
- 预设来源说明文案

当前支持的正式来源值：

1. `all`
2. `active_status`
3. `suggested_trigger`

### 2.3 列表页来源提示

已修改：

- `src/pages/MtmServiceCasesPage.vue`

当前列表页已支持：

1. 解析 `preset_source`
2. 在页头展示来源提示条
3. 根据 `preset_source` + 当前 query 输出人话标题和说明
4. 仅翻页时继续保留该标识

### 2.4 手动筛选清除来源标识

当前列表页已支持：

1. 用户搜索时清除 `preset_source`
2. 用户切换状态筛选时清除 `preset_source`
3. 用户切换触发来源筛选时清除 `preset_source`
4. 用户切换排序时清除 `preset_source`
5. 用户重置筛选时清除 `preset_source`

说明：

- 避免页面继续展示已经失真的首页预设提示

### 2.5 详情返回恢复

已修改：

- `src/pages/MtmServiceCaseDetailPage.vue`

当前详情页已支持在返回列表页时恢复：

1. `page`
2. `search`
3. `status`
4. `trigger_source`
5. `ordering`
6. `preset_source`

说明：

- 从列表页进入详情再返回后，列表页顶部预设提示不会丢失

---

## 三、验证结果

### 3.1 编辑文件诊断

已检查：

- `src/pages/MtmServiceCasesPage.vue`
- `src/pages/MtmServiceCaseDetailPage.vue`
- `src/utils/mtm.ts`
- `src/types/mtm.ts`

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

说明：

- 当前 `preset_source` 标识、列表页提示条和详情返回恢复逻辑已通过类型检查和生产构建

---

## 四、已知限制

本轮明确未做：

- 首页显示预设来源说明
- 列表页展示更复杂的预设标签体系
- 不同来源入口的单独样式差异化
- 更多预设来源类型

原因：

- 本任务只负责最小来源标识与提示统一
- 这些内容属于后续体验增强

---

## 五、验收判断

对照 `CONSENSUS_T-P0-18_MTM列表页预设来源标识与页面提示统一.md`：

1. 首页预设入口进入列表页时会带 `preset_source`：通过
2. 列表页页头能显示与预设一致的人话提示：通过
3. 列表进入详情再返回后，提示仍然存在：通过
4. 用户手动修改筛选后，预设提示会被清除：通过
5. 前端构建通过：通过

结论：

- `T-P0-18` 达到当前阶段可交付标准
- MTM 主线已从“首页入口规则统一”推进到“列表页来源可识别、提示可解释”
