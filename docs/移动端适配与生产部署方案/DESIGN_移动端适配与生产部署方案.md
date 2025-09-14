# DESIGN_移动端适配与生产部署方案

本设计文档在 ALIGNMENT 与 CONSENSUS 基础上，输出系统架构、模块设计、接口契约与异常处理策略，指导后续实现与验证。

## 1. 整体架构图
```mermaid
flowchart LR
  subgraph Client[移动端/浏览器]
    PWA[Vue3 PWA\nService Worker\n通知授权/安装引导]
  end

  subgraph Edge[Nginx Gateway]
    NGINX[Nginx\nTLS/HTTP2\nHSTS/安全头\n静态托管 dist\n/api 反代]
    ACME[/.well-known/acme-challenge]
  end

  subgraph Backend[后端集群]
    API[Gunicorn+Django+DRF\nREST API]
    WORKER[Reminder Worker\n(独立容器)]
  end

  subgraph Infra[基础设施]
    REDIS[(Redis)]
    MYSQL[(MySQL)]
    CERTBOT[Certbot\n自动签发/续期]
  end

  PWA<-->NGINX
  NGINX-->|/api|API
  NGINX-->|ACME HTTP-01|ACME
  ACME-->|验证/写证书卷|CERTBOT
  API<-->REDIS
  API<-->MYSQL
  WORKER<-->REDIS
  WORKER<-->MYSQL
  WORKER-->|Web Push|PWA
```

## 2. 分层设计与核心模块
- Web 层（Nginx）
  - 职责：TLS 终止、静态资源托管、反向代理、ACME 验证、缓存与压缩、安全头。
- 应用层（Django+DRF, Gunicorn）
  - 模块：
    - SubscriptionService（Web Push 订阅注册/更新/退订）
    - NotificationService（下发 Web Push/生成 ICS 链接）
    - ReminderAPI（提醒 CRUD、贪睡、确认、跳过回执）
- 调度层（Worker）
  - 模块：
    - Scheduler（按分钟扫描待触发提醒）
    - Executor（执行通道：Web Push→ICS；失败重试/退避/死信计数）
    - Deduplicator（Redis 分布式锁）
- 数据与缓存层
  - MySQL（业务数据、订阅表、提醒表）
  - Redis（锁、去重键、短期状态）

## 3. 数据模型补充
- WebPushSubscription（新表）
  - user_id(FK, 索引)、endpoint(varchar, 唯一)、p256dh(varchar)、auth(varchar)、ua(varchar, 可选)、created_at、updated_at、is_active(bool, 索引)
  - 复合索引：(user_id, is_active)
  - 约束：endpoint 唯一；软失效（is_active=false）

## 4. 接口契约（REST，响应统一为 {success: boolean, data: {...}}）
- POST /api/push/subscribe
  - 入参：{ endpoint: string, keys: { p256dh: string, auth: string }, ua?: string }
  - 出参：{ id: string, is_active: true }
  - 401 未登录；409 重复；422 参数错误
- POST /api/push/unsubscribe
  - 入参：{ endpoint: string }
  - 出参：{ unsubscribed: true }
  - 幂等：多次退订返回 unsubscribed: true
- POST /api/push/heartbeat
  - 入参：{ endpoint: string, last_seen_at?: ISODate }
  - 出参：{ ok: true }
- POST /api/reminders/{id}/ack
  - 入参：{ status: "confirmed" | "skipped" }
  - 出参：{ next_at?: ISODate }
- POST /api/reminders/{id}/snooze
  - 入参：{ minutes: number }（范围 5-60）
  - 出参：{ next_at: ISODate }
- GET  /api/calendar/ics
  - 入参：query: token(签名)、user
  - 出参：text/calendar（缓存 5m）

错误响应示例：{ success: false, error: { code: "INVALID_PARAM", message: "...", details?: any } }

## 5. 关键流程
- 订阅流程（前端）
  1) PWA 请求通知权限 → 注册 Service Worker → 获取 subscription
  2) 调用 /api/push/subscribe 保存
  3) 服务端返回 id 与激活状态
- 调度触达
  1) Worker 每分钟扫描 due reminders → Redis 锁去重
  2) 构造通知 payload（含 reminder_id、action 链接）
  3) 首选 Web Push；失败分类（4xx 退订、429 节流、5xx 重试）
  4) 不满足条件时提供 ICS 兜底
- 回执与贪睡
  1) 用户点击通知 action → /ack 或 /snooze
  2) 更新提醒状态；计算 next_at 并持久化

## 6. 配置与“魔法数字”论证
- Gunicorn：workers=3, threads=2, timeout=60s, graceful-timeout=30s
  - 理由：日活 30，连接上限 100，后端并发预算保守 < 12
- DB：CONN_MAX_AGE=120s，connect_timeout=5s，read_timeout=15s
  - 理由：减少握手成本，避免长尾阻塞
- Nginx：proxy_read_timeout=60s，client_max_body_size=10m；静态 fingerprint 资源 cache 1y immutable，HTML 60s
- 贪睡：默认 15 分钟；可配置范围 5-60 分钟（越界 400）

## 7. 安全与合规
- HTTPS 强制；HSTS max-age=15552000 includeSubDomains preload（首发阶段可不带 preload）
- 安全头：X-Frame-Options:DENY, X-Content-Type-Options:nosniff, Referrer-Policy:no-referrer-when-downgrade, Permissions-Policy（限制通知/地理位置）
- CSRF/CORS：基于域名白名单；仅允许必要方法与头；跨域凭证按需开启
- Cookie：Secure+HttpOnly+SameSite=Lax
- SECURE_SSL_REDIRECT=True，SECURE_PROXY_SSL_HEADER=("HTTP_X_FORWARDED_PROTO","https")

## 8. Nginx 与 Certbot 策略
- server_name 使用提供域名；80 提供 ACME 验证与到 443 的 301 跳转
- /.well-known/acme-challenge 直通 certbot 卷
- 证书与密钥挂载只读到 Nginx；续期计划任务 crond + certbot renew + reload

## 9. 观测与日志
- 日志格式：JSON 行，字段：ts, level, svc, request_id, user_id, reminder_id, channel, status, latency_ms, error_type, error_msg
- 错误提取 Regex（后端）
  - Web Push 错误：/(PushError|WebPushException)[:\s]+(?<reason>.+)/
  - DB 超时：/(OperationalError).*?(timeout|lock wait)/i
  - 连接池枯竭：/(Too many connections|MySQL server has gone away)/i
- 关键指标：
  - push_success_rate、push_latency_p95、scheduler_lag_s、backend_5xx_rate、db_conn_in_use

## 10. 部署与运行
- docker-compose（production profile）
  - services: nginx, certbot, frontend(builder 产物作为卷), backend(gunicorn), worker, mysql, redis
  - healthcheck：/api/healthz、Redis PING、MySQL SELECT 1
  - 卷：证书卷、acme-challenge 卷、前端 dist 只读卷、日志卷

## 11. 异常处理策略
- 重试：指数退避（1s→2s→4s→8s, 上限 5 次）；非幂等操作使用幂等键（reminder_id + attempt）
- 死信：超过重试阈值写入 dead_letter 表或日志并报警
- 熔断：连续 5xx 上升时短暂熔断推送通道（60s）并转 ICS

## 12. 与现有系统对齐
- 不使用 Vite 代理（已移除）；生产静态由 Nginx 提供
- 保持后端响应结构双层 data；前端统一解构 response.data.data

## 13. 待确认项（阻断级）
- 正式域名清单（主域/子域）——用于 Nginx、证书、CSRF/CORS/ALLOWED_HOSTS
- 邮件通道暂不启用（确认）

## 14. 环境/依赖/验证
- 环境
  - OS: Ubuntu 22.04 LTS（已确认采用）
  - Docker: 28.4.0；Compose: v2.39.2（与目标服务器版本对齐）
  - 镜像加速器: https://qztpf1t5.mirror.aliyuncs.com（已写入 daemon.json）
- 依赖
  - 数据库：外部 RDS MySQL（不在 Compose 内启动 mysql 容器）
    - 运行时通过环境变量注入：DB_HOST, DB_PORT=3306, DB_NAME, DB_USER, DB_PASSWORD
    - 建议开启连接参数：CONN_MAX_AGE=120s, connect_timeout=5s, read_timeout=15s（与本设计“魔法数字”一致）
    - 安全：凭据仅放到宿主/CI 的 .env 中，严禁提交仓库
  - 缓存：Redis（容器），REDIS_PASSWORD 通过环境变量注入
  - 域名与证书：需提供正式域名清单，Nginx 使用 server_name，Certbot 按域名签发
  - 通知兜底：短信通道参数待提供；在未就绪前，ICS 作为兜底
- 验证
  - 版本校验
    - docker --version 应显示 28.4.0
    - docker compose version 应显示 v2.39.2
  - 编排校验（仅合并配置，不实际启动）
    - docker compose -f docker-compose.yml -f docker-compose.prod.yml config
  - RDS 连通性（在宿主或容器内）
    - mysql -h $DB_HOST -u $DB_USER -p -P ${DB_PORT:-3306} -e "SELECT 1;"（确认返回 1）
  - Redis 连通性
    - docker compose run --rm redis redis-cli -a "$REDIS_PASSWORD" PING（返回 PONG）

- ... existing code ...