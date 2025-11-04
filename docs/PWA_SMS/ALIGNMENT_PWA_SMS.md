# ALIGNMENT — PWA 最小闭环 & 短信兜底集成

本文件用于对齐“前端 PWA 落地最小闭环”和“后端短信兜底模式（可开关、可接入服务商）”两项任务的当前现状、范围、原则、关键决策点与验收标准，作为后续架构与实施依据。

## 1. 项目上下文与现状
- 前端技术栈：Vue 3 + Vite（TypeScript），未发现 PWA 插件与 SW 注册代码。
  - Vite 配置：<mcfile name="vite.config.ts" path="e:\mtm-helper\vite.config.ts"></mcfile>（plugins 中未包含 vite-plugin-pwa）
  - 入口：<mcfile name="main.ts" path="e:\mtm-helper\src\main.ts"></mcfile>（未调用 registerSW 或类似注册）
- 后端技术栈：Django + MySQL（RDS），通知模块存在短信方法但当前默认未启用短信类型。
  - 通知服务：<mcfile name="notifications.py" path="e:\mtm-helper\backend\apps\reminders\notifications.py"></mcfile>
    - <mcsymbol name="NotificationService.__init__" filename="notifications.py" path="e:\mtm-helper\backend\apps\reminders\notifications.py" startline="17" type="function"></mcsymbol>：enabled_types = ['push','email']，短信未默认开启
    - <mcsymbol name="NotificationService._send_sms_notification" filename="notifications.py" path="e:\mtm-helper\backend\apps\reminders\notifications.py" startline="113" type="function"></mcsymbol>：为占位/模拟发送，未接入服务商 SDK
- 接口访问与配置：
  - 存在多处硬编码 baseURL（例：<mcfile name="http.ts" path="e:\mtm-helper\src\utils\http.ts"></mcfile> 第 61 行、<mcfile name="api.ts" path="e:\mtm-helper\src\utils\api.ts"></mcfile> 第 43 行、若干组件内拼接 http://127.0.0.1:8000）。这会影响生产部署与 SW 缓存策略。

## 2. 任务范围（明确边界）
A. PWA 最小闭环（不引入后端 Web Push、只做应用可安装与基础离线能力）
- 引入 vite-plugin-pwa，生成并注册 Service Worker；
- 提供 manifest（name、short_name、theme_color、background_color、icons）；
- Workbox 缓存策略：仅缓存静态资源与页面壳（App Shell），明确排除 API 请求；
- 注册 SW 的更新策略（skipWaiting/clientsClaim）与更新日志输出；
- 验证：Lighthouse 核心 PWA 检查通过、离线可打开首页、API 不被缓存。

B. 短信兜底模式（开关化 + 可接入）
- 后端通过环境变量开关是否启用短信通道（默认关闭，无凭据时不启用）；
- 设计 Provider 抽象/选择器（Aliyun/Tencent/Twilio 其一），先占位接口，待凭据后接入；
- 日志与失败降级策略（不影响 push/email，确保无凭据时安全降级）；
- 验证：开关关闭时不发送短信、打开且配置完整时路由至对应 Provider 调用（本阶段可先完成开关与结构，供应商接入待凭据确认）。

不在本次范围：
- 后端 Web Push（推送订阅、VAPID、公钥等）与后台推送服务；
- iOS 专用 PNG 图标适配（现阶段以 SVG 资源占位，iOS 桌面图标兼容性后续专项处理）。

## 3. 设计与实施原则
- 与现有项目风格一致，尽量复用现有工具与封装；
- SW 绝不缓存 /api 相关请求，避免数据过期与联调困扰；
- 不使用 Vite 代理；
- 后端不返回模拟响应；
- 严格使用环境变量管理敏感信息与开关（.env / .env.prod）；
- 关键位置打印日志，便于调试与回溯。

## 4. 关键决策点（需确认）
1) 短信服务商选择与接入计划
- 备选：阿里云短信、腾讯云短信、Twilio（或您指定的其他供应商）
- 需要：
  - 服务商：名称与区域
  - 访问凭据：AccessKey/Secret、签名、模板ID（按供应商要求）
  - 发送频控与重试策略（默认按供应商限流策略，更多需求可后续追加）

2) PWA manifest 关键信息
- name / short_name（中文、英文各一套是否需要？）
- theme_color / background_color（建议与品牌色一致）
- start_url（建议 '/'）
- display（建议 'standalone'）
- icons（SVG 源文件；尺寸建议含 192、512 的 maskable 版本，iOS PNG 暂不纳入本阶段）

3) 离线缓存范围与更新策略
- 页面：仅缓存应用壳与首页？是否缓存部分二级页面的 HTML？
- 资源：静态 JS/CSS/字体/图片按 revision 策略缓存
- 更新：启用 skipWaiting + clientsClaim（新版 SW 就绪后立即接管）是否接受？

4) API 访问配置改造
- 现状为多处硬编码 http://127.0.0.1:8000；是否改为使用环境变量 VITE_API_BASE_URL 并统一封装？
- 目标：开发、预发、生产可通过环境切换，无需改动代码。

## 5. 初步验收标准（可测试）
PWA：
- 构建后生成 service-worker 与 manifest；
- 首次打开后可安装（Chrome 浏览器出现安装入口）
- 断网后刷新首页仍能展示应用壳（不请求 /api 即可呈现基本 UI）；
- /api 请求不被缓存，始终直连网络；
- 控制台打印 SW 注册/更新日志。

短信兜底：
- 未配置凭据时，短信通道不开启且不会尝试发送（日志中可见“短信未启用/未配置”提示）；
- 配置 SMS_ENABLED=true 但无完整凭据 -> 记录明显错误并自动降级，不影响 push/email；
- 未来接入供应商后：凭据完整时可成功调用对应 SDK（本阶段先完成开关与结构）。

## 6. 风险与注意事项（配置安全与生产可靠性）
- 高风险：前端硬编码 baseURL，导致不同环境切换困难、与 SW 缓存策略耦合，建议改为环境变量统一管理；
- 高风险：错误的 SW 缓存范围会导致接口被缓存（数据陈旧、错乱），必须显式排除 /api；
- 兼容性：iOS 对 SVG icon/pwa 的支持与安装提示存在差异，本阶段以桌面图标兼容性为次要目标；
- 监控：建议增加前端 window.navigator.onLine 变化日志、SW 生命周期日志；后端记录短信开关状态与调用结果。

## 7. 待您确认的问题清单（优先级从高到低）
1) 短信服务商选择（阿里云/腾讯云/Twilio/其他），以及是否本阶段仅完成“开关 + 框架”，供应商接入待凭据后再做？
2) PWA manifest 具体信息（name、short_name、主题色、背景色、icons SVG 资源）是否有指定品牌规范？若暂无，可否先用临时占位信息？
3) SW 更新策略是否采用 skipWaiting + clientsClaim（快速接管）？如需更温和策略（等待关闭页面再更新），请说明。
4) API baseURL 是否同意改成环境变量（如 VITE_API_BASE_URL），并统一移除代码中的硬编码？
5) 离线缓存范围是否只缓存首页与应用壳（推荐），其他页面保持在线？

---
请您按上述问题逐项回复，我将据此输出 DESIGN、TASK 文档并开始实施。