# DESIGN_用药提醒

本设计文档基于 CONSENSUS，描述 PWA 推送架构、模块拆分与接口契约，并给出数据流与异常处理策略。

一、整体架构图（Mermaid）
```mermaid
flowchart TD
  A[前端 Vue/PWA] -->|registerSW + 权限| B[Service Worker sw.ts]
  B -->|Push 事件| C[浏览器通知]
  A -->|订阅请求| D[PushManager.subscribe]
  D -->|生成订阅| A
  A -->|POST 订阅| E[后端 API /user/push-subscriptions/]
  E -->|保存订阅| F[数据库]
  G[后端调度器/cron] -->|WebPush| H[Push Service (FCM/WebPush)]
  H -->|Push payload| B
  B -->|notificationclick| A
```

二、分层与核心组件
- 前端页面组件：NotificationPermission.vue（权限与订阅入口、状态展示与测试通知）
- 服务模块：pushService.ts（订阅/取消订阅/VAPID 公钥读取/后端保存订阅）
- PWA 注册：main.ts 使用 `virtual:pwa-register` 保持 `registerType=autoUpdate`
- Service Worker：sw.ts 自定义（precache、runtime 缓存、push 展示、点击交互、SKIP_WAITING）

三、接口契约定义
1) 保存订阅接口
  - URL：`POST /api/user/push-subscriptions/`
  - Headers：`Content-Type: application/json`
  - Body：
    ```json
    {
      "endpoint": "string",
      "keys": { "p256dh": "string", "auth": "string" },
      "ua": "string",
      "timeZone": "Asia/Shanghai",
      "app": "mtm-helper"
    }
    ```
  - Response：`{ "success": true, "data": { "id": 123 } }`

2) 取消订阅接口（建议）
  - URL：`DELETE /api/user/push-subscriptions/`（按 endpoint 定位）或 `DELETE /api/user/push-subscriptions/{id}/`
  - Response：`{ "success": true, "data": {} }`

3) 推送触发接口（后端）
  - URL：`POST /api/push/test`（仅开发测试）
  - Body：`{ subscriptionId: number, title: string, body: string, url?: string }`
  - Response：`{ "success": true, "data": { "queued": true } }`

四、数据流向
1. 用户点击“启用推送订阅”
   - 前端检查支持与权限 → Service Worker 就绪 → PushManager.subscribe → 生成订阅对象 → 前端 POST 至后端保存。
2. 后端调度到点触发 → 通过 WebPush 服务向浏览器发送 Push payload → Service Worker `push` 事件收到 → `showNotification()` 展示。
3. 用户点击通知 → `notificationclick` 事件聚焦现有窗口（如存在），可选跳转到提醒详情页。

五、异常处理策略
- 权限被拒绝：前端显示不可订阅状态与提示；记录日志，不进行订阅。
- 浏览器不支持：按钮不可用并显示兼容提示；记录日志。
- 订阅失败：最多尝试 3 次，失败则停止并提示用户检查网络或浏览器设置。
- 保存订阅失败：按统一响应结构解析错误，终止后续流程并提示；写入 TODO 由后端协作。
- Push payload 格式异常：Service Worker 在 `push` 中进行容错，使用默认标题与图标。

六、运行时缓存策略
- 预缓存：由 Workbox `precacheAndRoute(self.__WB_MANIFEST)` 自动注入构建产物。
- 运行时：静态资源与图标 `CacheFirst`；API 请求 `StaleWhileRevalidate`（可按需扩展）。

七、更新策略
- `registerType=autoUpdate` 自动更新；在 Service Worker 接收 `SKIP_WAITING` 消息时立刻 `skipWaiting` 并 `clients.claim`，确保新版生效。

八、兼容性与后续扩展
- iOS PWA 推送能力需确认最新支持；如受限，采用 Capacitor Local Notifications 作为主要移动端方案。
- 后端需提供 VAPID 私钥与 WebPush 服务配置，确保公网环境可达。