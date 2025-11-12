# ALIGNMENT — 用药提醒 PWA 推送对接

目标：将“用药提醒”功能的浏览器 PWA 推送能力端到端落地，形成清晰的任务上下文、需求规范、边界与问题清单，便于后续架构与实现。

## 1. 项目上下文分析
- 前端技术栈：Vite + TypeScript + Vue（含 `vite-plugin-pwa`）。
- 已有关键文件：
  - `vite.config.ts`：已启用 PWA 插件，策略为 injectManifest（根据近期改动与构建日志）。
  - `src/sw.ts`：自定义 Service Worker（Workbox 预缓存、路由策略可控）。
  - `src/services/pushService.ts`：与 Push API/VAPID 公钥相关的前端接入服务（待与后端对接）。
  - `src/components/notifications/NotificationPermission.vue`：通知权限申请 UI。
  - `src/vite-env.d.ts`：类型声明（可能包含 Service Worker 相关类型）。
- 构建与产物：构建日志显示已生成 `workbox-*.js`、`sw.js` 以及图标拷贝，PWA 功能基本连通。
- 环境与约束：
  - Windows 开发环境；PowerShell 不支持 `&&`，命令需分别执行。
  - Redis 安装路径：`D:\Redis-x64-3.0.504`（适用于队列/定时）。
  - Docker 安装路径：`D:\Application\Docker\docker`。
  - MySQL 安装路径：`C:\Program Files\MySQL\MySQL Server 8.0`。
  - 不使用 Vite 代理配置；接口请求需直接指向后端服务。
  - 前端访问后端返回结构须处理双层 `data`：后端结构 `{ success: true, data: { ... } }`，前端应访问 `response.data.data.xxx`。

## 2. 业务域与数据模型初步理解
- 业务域：用药提醒（Medication Reminders）。核心目标是在用户设定的提醒时间，向其设备推送通知。
- 推送相关实体：
  - `PushSubscription`（浏览器订阅）：字段包含 `endpoint`、`keys.auth`、`keys.p256dh`、`browser`、`device`、`userId`、`createdAt`、`lastSeenAt`、`isActive`。
  - `ReminderSchedule`（用药提醒计划）：字段包含 `userId`、`medicationId`/自定义药品名、`dosage`、`times`（每日多次或 CRON 表达式）、`timezone`、`startDate`、`endDate`、`channel`（web-push / sms / email / ios-fallback）。
  - `PushLog`（推送日志）：`subscriptionId`、`scheduleId`、`status`、`errorCode`、`errorMsg`、`sentAt`、`retryCount`、`ttl`。

## 3. 原始需求与范围边界
- 需求要点：
  1) 前端 PWA 完成订阅与权限管理，后端保存/删除订阅；
  2) 后端在提醒时间触发推送，内容包含药品名、剂量、时间等；
  3) 使用 VAPID（Web Push）自托管，不引入第三方推送模拟；
  4) iOS 兼容策略：Safari 16.4+ 已支持 PWA 推送（需安装为 Web App），老版本与不可安装场景提供降级（例如站内提醒/短信/邮件，具体需确认）；
  5) API 返回严格遵循 `{ success: boolean, data: {...} }`；不返回模拟数据；关键位置打印日志。
- 范围边界：
  - 本阶段聚焦 Web Push 后端对接与端到端联调；短信/邮件等备选通道仅设计占位与接口约定，具体实现可后续。
  - 不改动不相关业务模块；不引入 Vite 代理；不引入与现有架构冲突的模式。

## 4. 现状理解与潜在风险
- 构建已成功且 PWA 产物生成；但后端 API 尚未明确（路径/鉴权/数据存储）。
- 订阅数据存储需要关联用户与设备；重复订阅、退订与幂等性需处理。
- 推送失败重试、TTL、速率限制与合规（隐私/同意）需明确。
- 时区与提醒时间准确性（DST 与不同地区）需确认。

## 5. 关键假设（待确认）
- 后端技术栈：Node.js（Express/NestJS）优先；数据库使用 MySQL；队列/定时使用 Redis + BullMQ。
- 认证：前端可获取用户身份（JWT 或会话）并以 `userId` 传递给后端。
- 部署：后端服务将通过 Docker 运行，端口对外公开供前端直接调用。

## 6. 智能决策策略与优先问题清单
优先顺序从高到低：
1) API 设计与路径确认：
   - POST `/api/push/subscribe` 保存订阅；DELETE `/api/push/subscribe/:id` 删除订阅；POST `/api/push/test` 测试单次推送；POST `/api/reminders` 创建提醒计划；
   - 是否需要鉴权头（如 `Authorization: Bearer <token>`）？
2) VAPID 密钥与 subject：
   - `.env` 中的 `VAPID_PUBLIC_KEY`、`VAPID_PRIVATE_KEY`、`VAPID_SUBJECT` 的生成与注入；是否已有公钥？
3) 推送触发机制：
   - 采用 BullMQ（Redis）+ 定时调度（延时队列/CRON）还是数据库轮询？推荐 BullMQ。
4) 时区策略：
   - 后端统一以用户 `timezone` 进行调度；保存为 IANA TZ（如 `Asia/Shanghai`）。确认是否需要跨区提醒。
5) iOS 兼容策略：
   - 针对 iOS Safari 16.4+ 的 PWA 安装检测与订阅；旧版或不可安装时的降级通道选择（站内提醒/短信/邮件）。
6) 数据模型与持久化：
   - MySQL 表结构命名与字段；是否已有现成用户/药品表对接规范？
7) 速率限制与退订管理：
   - 每用户/设备频率限制；退订/失效订阅清理；

## 7. 待回答问题（按优先级排序）
1) 后端栈与项目路径：现有后端是 Express、NestJS、Spring Boot 还是其他？代码目录在哪里？
2) API 路径与鉴权策略：是否采用 `Authorization: Bearer`；是否需要 CSRF、防重放？
3) VAPID 公私钥是否已生成？若未生成，是否允许按指南生成并写入 `.env`？
4) Redis 与 MySQL 连接信息（主机、端口、凭证）是否有固定配置或通过 Docker Compose 提供？
5) iOS 降级通道选择：偏好短信、邮件还是仅站内提醒？各通道是否已有服务商或网关？
6) 用户时区来源：由后端账户设定还是前端上报？默认时区是什么？
7) 推送内容规范：标题、正文、动作按钮、跳转路径（如 `/medication/:id`），是否需要本地化？

## 8. 初步规范（待用户确认后可定稿）
- 前端 `.env` 注入 `VITE_VAPID_PUBLIC_KEY`（只暴露公钥）；后端 `.env` 存私钥与 subject。
- 接口响应统一：`{ success: true/false, data: {...}, error?: { code, message } }`；前端使用 `response.data.data` 访问业务数据。
- 日志：前后端关键路径均打印日志（注册、退订、调度、推送结果）。
- 安全：校验订阅对象结构；对 `endpoint` 做唯一约束；开启速率限制。

## 9. 下一步
- 待用户回答问题清单后，输出 `CONSENSUS_用药提醒.md`（最终共识）并据此更新设计与任务拆分。