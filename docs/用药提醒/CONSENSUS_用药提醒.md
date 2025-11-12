# CONSENSUS_用药提醒

本文件用于在对齐阶段基础上，明确“用药提醒-手机端系统级提醒/闹钟接入”的共识结论与验收标准，确保后续架构与实现按此统一规范执行。

一、关键决策
- 运行形态：
  - 网页端/PWA：采用 Service Worker + Web Push（浏览器通知）作为网页端推送与提醒能力；立即实现推送订阅与前台/后台通知展示。
  - 移动端原生能力：建议采用 Capacitor 封装移动应用，优先使用 `@capacitor/local-notifications` 实现本地计划与到点提醒；此为后续扩展，不在本次提交中直接改动后端。
- PWA 架构：切换 VitePWA 至 injectManifest 策略，提供自定义 `src/sw.ts`，实现 precache、runtime 缓存、push 事件与 `notificationclick` 交互，支持 `SKIP_WAITING`。
- 数据契约：前后端接口统一遵循 `{ success: true, data: {...} }` 双层结构；前端访问数据时以 `response.data` 为标准解包对象，内部字段取 `response.data.xxx` 或 `response.data.data.xxx`（已在统一客户端中自动解包）。
- 权限与指引：在前端增加权限引导与推送订阅按钮，打印关键日志，避免页面展示模拟数据。
- 时区处理：后端统一采用本地时区进行调度匹配（见 scheduler.py 与相关说明）；前端在保存订阅时携带 `timeZone` 提示后端进行用户侧时区标注。

二、范围与边界（本次迭代）
- 实现网页端推送订阅（VAPID 公钥从环境变量读取）。
- Service Worker 自定义 push 与点击事件、缓存策略、更新流程。
- 前端提供“启用推送订阅/取消订阅/测试通知”操作与状态展示。
- 不中断现有提醒功能与统计功能，不引入代理配置；遵循现有代码风格与日志规范。
- 后端保存订阅与触发推送的 API 本次不修改，仅在 TODO 中明确需要后端支持的端点与四要素。

三、不确定性与决策点（需确认）
1. 后端保存 Push 订阅的具体端点：建议为 `POST /api/user/push-subscriptions/`，取消订阅为 `DELETE /api/user/push-subscriptions/{id}/` 或 `DELETE /api/user/push-subscriptions/`（按 endpoint）。
2. VAPID 公钥与私钥的生成与存储：公钥写入 `.env` 为 `VITE_VAPID_PUBLIC_KEY`；私钥由后端安全管理，不进入前端仓库。
3. 推送触发服务选择：后端采用 Web Push（pywebpush 或第三方服务），还是暂用 WebSocket/轮询过渡方案。
4. iOS PWA 推送兼容策略：iOS Safari 对 Web Push 支持的版本与限制需确认（最新文档），必要时以 Capacitor 原生本地通知作为主要方案。

四、验收标准（网页端/PWA 本次迭代）
- 能在浏览器中正常申请通知权限并展示本地测试通知。
- 能在支持 Push 的浏览器中完成订阅与取消订阅动作，前端日志明确显示成功/失败原因。
- Service Worker push 事件能弹出通知，`notificationclick` 能聚焦窗口并可选跳转。
- 构建通过、PWA 注册与缓存策略生效；无 Vite 代理配置；控制台关键日志可见。

五、交付物
- docs：CONSENSUS、DESIGN、TASK、ACCEPTANCE、FINAL、TODO 文档。
- 代码：`vite.config.ts`（injectManifest）、`src/sw.ts`、`src/services/pushService.ts`、`src/components/notifications/NotificationPermission.vue` 更新、`src/vite-env.d.ts` 类型补充。

六、质量门控
- 与现有架构一致，复用统一 API 客户端与通知服务风格；代码简洁、函数级注释齐备；关键位置打印日志。
- 接口四要素清晰，避免模拟数据；失败最多尝试 3 次后停止自动重试并记录错误。