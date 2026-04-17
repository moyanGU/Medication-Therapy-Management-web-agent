# CONSENSUS P1-B4 随访记录最小落地

## 1. 核心共识

- **关系转变**：随访模型（`MTMFollowUp`）是 `1对多` 关系，不再使用单一草稿更新模式，而是明确的创建 (`create`) 和修改 (`update`) 动作。
- **交互极简**：不再引入“保存草稿”和“完成”的双按钮机制。通过表单里的 `execution_status` (执行情况：待执行、已完成、已取消等) 来标识随访状态。只提供一个“保存随访记录”的按钮。
- **入口条件**：只有在干预计划完成后，详情页才会在随访区域显示“添加随访”按钮。已有随访记录可点击编辑。

## 2. API 接口共识

在 `MTMServiceCaseViewSet` 中不适合把 `1对多` 的子资源全部堆进去，或者可以通过 DRF 的 `@action` 实现，但更清晰的做法是：

- **`GET /api/mtm/service-cases/{id}/follow-ups/`**: 列表查询（目前可通过详情接口直接获取，可不单独实现）
- **`POST /api/mtm/service-cases/{id}/follow-ups/`**: 创建随访
- **`PUT /api/mtm/service-cases/{id}/follow-ups/{follow_up_id}/`**: 更新指定随访
- **`GET /api/mtm/service-cases/{id}/follow-ups/{follow_up_id}/`**: 获取单条随访详情用于回填编辑表单

*(若 DRF 路由配置嵌套麻烦，也可独立 `MTMFollowUpViewSet` 暴露 `/api/mtm/follow-ups/`)*

**最终共识**：为了方便，在 `apps/mtm/urls.py` 中注册 `MTMFollowUpViewSet`：
- `POST /api/mtm/follow-ups/`
- `GET /api/mtm/follow-ups/{id}/`
- `PUT /api/mtm/follow-ups/{id}/`
- 创建时 Payload 需要带有 `service_case` 的 ID。

## 3. 前端共识

- **新页面**：`MtmFollowUpFormPage.vue`
- **新路由**：
  - 新增：`/mtm/service-cases/:caseId/follow-ups/new`
  - 编辑：`/mtm/service-cases/:caseId/follow-ups/:followUpId`
- **详情页入口**：
  - 随访记录区右上角：新增按钮 `+ 添加随访`
  - 单张随访卡片：增加点击交互或 `编辑` 图标
- **展示**：保存成功后回到详情页，重新拉取服务单数据，列表自然刷新。
