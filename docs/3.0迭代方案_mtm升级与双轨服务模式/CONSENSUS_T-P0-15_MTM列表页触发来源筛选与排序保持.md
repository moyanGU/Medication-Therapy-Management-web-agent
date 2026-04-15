# CONSENSUS_T-P0-15_MTM列表页触发来源筛选与排序保持

## 一、任务共识

本轮正式启动的开发任务为：

- `T-P0-15 MTM 列表页触发来源筛选与排序保持`

目标共识：

- 让 MTM 列表页可以按触发来源筛选
- 让 MTM 列表页可以按最小排序方式查看
- 让这两个新状态也能在 URL 和详情返回中保持

---

## 二、范围共识

本任务确定只做以下内容：

1. 新增触发来源筛选
2. 新增排序方式选择
3. `trigger_source` 和 `ordering` 同步到路由查询参数
4. 详情页返回时恢复这两个新上下文

明确不做：

- 新增后端接口
- 新增更多复杂筛选
- 新增组合排序面板
- 重构列表页整体布局

---

## 三、查询参数共识

本轮需要正式保留的列表查询参数为：

1. `page`
2. `search`
3. `status`
4. `trigger_source`
5. `ordering`

详情页附加来源标记继续沿用：

1. `from=mtm-list`

---

## 四、触发来源筛选共识

列表页首版确定暴露以下触发来源选项：

1. `manual`
2. `self_requested`
3. `adherence_alert`
4. `followup_due`
5. `polypharmacy`
6. `referral`

展示共识：

- 使用当前已有的人话文案映射
- 不新增模拟标签体系

---

## 五、排序方式共识

列表页首版确定暴露以下排序选项：

1. `-created_at` 最新创建优先
2. `created_at` 最早创建优先
3. `-started_at` 最近启动优先
4. `-completed_at` 最近完成优先

共识说明：

- 仅使用后端已允许的排序字段
- 默认排序继续保持当前后端默认值 `-created_at`

---

## 六、列表页交互共识

列表页确定具备以下行为：

1. 首次进入时解析 `trigger_source` 和 `ordering`
2. 切换触发来源时更新 URL
3. 切换排序方式时更新 URL
4. 刷新页面后恢复这两个状态
5. 浏览器前进后退时恢复这两个状态

实现共识：

- 继续优先使用 `router.replace`
- 排序变化不算空态里的“筛选条件”

---

## 七、详情页返回共识

详情页返回逻辑确定为：

1. 如果来自列表页，则继续返回 `/mtm/service-cases`
2. 返回时恢复：
   - `page`
   - `search`
   - `status`
   - `trigger_source`
   - `ordering`
3. 非列表入口继续保持原有返回逻辑

---

## 八、实现文件共识

本任务确定修改：

1. `src/pages/MtmServiceCasesPage.vue`
2. `src/pages/MtmServiceCaseDetailPage.vue`
3. `src/types/mtm.ts`

本轮不修改：

1. `src/api/mtm.ts`
2. `src/router/index.ts`
3. 后端 `apps.mtm` 列表接口代码

---

## 九、验收标准

本任务完成后，必须满足以下验收条件：

1. 列表页可按触发来源筛选
2. 列表页可切换排序方式
3. `trigger_source` 与 `ordering` 会同步到 URL
4. 刷新列表页后这两个状态仍能恢复
5. 从列表进入详情再返回时，这两个状态不会丢
6. 前端构建通过

---

## 十、实施结论

`T-P0-15` 的最终实施方案确定为：

1. 在现有列表页上增量补充触发来源与排序控件
2. 将这两个字段纳入现有 URL 联动框架
3. 将这两个字段纳入详情页返回上下文
4. 不新增新的后端接口和复杂筛选体系
