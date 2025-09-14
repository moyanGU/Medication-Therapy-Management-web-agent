# ALIGNMENT_移动端适配与生产部署方案

本文档用于对齐“移动端适配 + 生产环境部署 + 闹钟型提醒服务”的需求，基于现有代码与配置进行规范化定义、范围界定与关键决策点识别。

## 1. 项目上下文分析
- 技术栈与结构
  - 前端：Vue3 + Vite + Tailwind（无 PWA 依赖）；实际使用的构建配置为 `vite1.config.ts`（package.json 指定）。
  - 后端：Django + DRF，MySQL，Redis；已存在提醒模块（models/views/scheduler/notifications）。
  - 部署：docker-compose 提供 backend/frontend/mysql/redis/nginx 五服务；其中 nginx 期望挂载 `./nginx.conf` 但文件缺失（部署会失败）。
- 关键代码与配置参考
  - 前端路由与通知：`src/router/index.ts`、`src/composables/useNotification.ts`
  - 后端提醒：`backend/apps/reminders/` 下 `models.py / views.py / scheduler.py / notifications.py`
  - 环境与依赖：`backend/.env(.example)`、`backend/requirements.txt`
  - 构建与部署：`vite1.config.ts`、`docker-compose.yml`、`backend/Dockerfile`、`Dockerfile.frontend`
- 现状评述
  - 无 PWA 与 Web Push（VAPID）支持；useNotification 仅能前台弹出通知。
  - docker-compose 生产环境仍以 dev server 方式运行前端，后端用 runserver（不适合生产）。
  - `docker-compose.yml` 中 DEBUG=True、明文凭据、缺少健康检查与重启策略、安全头/HTTPS 未配置。

## 2. 需求理解与范围
- 目标能力
  1) 移动端适配：在手机浏览器/PWA 安装后稳定使用，UI 触控友好，离线可用性与缓存策略完善。
  2) 闹钟型提醒：在移动端“可靠触达”，主通道为 Web Push（PWA 安装 + 通知授权），提供确认/贪睡/跳过交互；
     Fallback 通道为短信（以及可选邮件）；再补充 ICS 订阅/写入系统日历作为兜底。
  3) 生产部署方案：Nginx 前置（TLS/反代/静态托管/缓存/安全头），后端 gunicorn，调度 worker 独立容器，分环境与密钥管理，观测与告警。
  4) 稳定与安全：数据库/Redis/连接池/超时/限速策略，安全头、Cookie 安全属性、DEBUG 关闭、ALLOWED_HOSTS/CORS/CSRF 规范化。
- 非目标（本阶段不做）
  - 原有业务域的大幅扩展；
  - 引入额外的消息队列/流系统（如 Kafka/RabbitMQ），除非后续负载评估确认必要。

## 3. 现有文档/约定对齐
- 默认规则：不使用 Vite 代理；接口返回为 `{success: true, data: {...}}`（前端访问注意 data.data）；
  生产只保留一个后端虚拟环境；不返回模拟响应；关键位置打印日志便于调试。

## 4. 初步技术方案概览
- 前端 PWA 化：vite-plugin-pwa + manifest + Service Worker（缓存策略、离线提示、更新策略）；安装引导与权限引导。
- Web Push：后端新增订阅模型与 API（订阅/退订/心跳），VAPID 密钥管理，服务端主动推送；通知 action 回执接口（确认/贪睡/跳过）。
- 调度：将 scheduler 从 web 进程剥离，独立 worker 容器；Redis 分布式锁防重，失败重试与指数退避；贪睡触发后续计划。
- 部署：Nginx 托管前端 dist + 反代后端；后端 gunicorn；compose 使用 production profile、env_file、健康检查与只读卷；HTTPS 与安全头。
- 观测：统一结构化日志（包含 request_id/user_id/reminder_id/channel/retry/latency/error_type），推送失败率/调度滞后等告警。

## 5. 关键风险与假设
- 缺少 nginx.conf（CRITICAL）：无法启动 Nginx 容器。
- 生产模式仍用 dev server 与 runserver（CRITICAL）：性能与稳定性不可接受。
- 明文凭据与 DEBUG=True（CRITICAL）：需分环境/密钥管理与关闭 DEBUG。
- iOS Web Push 需 PWA 安装且 iOS 16.4+：需通过 UI 引导与短信/ICS 兜底。

## 6. 待确认的关键决策点（优先级排序）
1) 域名与证书
   - 拟上线域名（主/备）？是否使用 Let’s Encrypt 自动签发，还是已有正式证书？
2) 部署环境与拓扑
   - 生产运行平台是单机 docker-compose 还是云服务器/容器服务？系统为 Linux 还是 Windows？是否需要高可用？
3) 推送通道与服务商
   - 短信服务是否有既定供应商与可用凭据？是否同时启用邮件作为三级兜底？
4) PWA 要求与体验
   - 是否接受“必须安装 PWA 后 iOS 才能接收推送”的前提？未安装时默认走短信/ICS 兜底是否可行？
5) 调度与扩缩容
   - 预期是否会水平扩展多个 worker 实例？是否需要跨机房/多副本防重策略？
6) 数据库与容量
   - 预计日活与高峰并发？MySQL 最大连接数与规格？允许的最大推送吞吐目标？
7) 安全与跨域
   - ALLOWED_HOSTS、CSRF_TRUSTED_ORIGINS 与 CORS 白名单的目标配置？是否有管理端或额外子域？
8) 监控栈
   - 是否已有 ELK/Loki/Prometheus/Grafana 设施？如无，是否接受最小可行的日志采集与告警方案？
9) 交互细节
   - 贪睡默认时长（如 5/10/15 分钟）？通知 action 的精确定义与统计口径？
10) 数据备份与留存
   - 数据库备份策略（频率/保留天数）与日志留存周期？

## 7. 验收标准（初版草案）
- 构建与部署
  - 生产环境通过 Nginx 提供前端静态资源并反代后端；全站 HTTPS；安全头/HSTS 启用；健康检查 OK。
  - 后端使用 gunicorn；调度 worker 独立容器；Redis/MySQL 连接稳定无错误峰值；DEBUG=False；日志结构化。
- 功能与体验
  - 移动端访问与安装 PWA 顺畅；首访权限引导明确；断网可用提示；长列表/图片加载优化。
  - 提醒可按计划触达：PWA Web Push 主通道，未授权/未安装时短信/ICS 兜底；通知 action 能回执并更新状态。
- 稳定与安全
  - 基础监控与告警上线；5xx 率/P95 延迟符合阈值；推送失败率 < 2%；调度滞后 < 60s。

## 8. 下一步
- 等待第 6 节关键决策点的回复后：
  - 生成 CONSENSUS 文档与详细架构设计（DESIGN），并进入任务分解（TASK）与实施（Automate）。