# CONSENSUS_移动端适配与生产部署方案

本共识文档依据 ALIGNMENT 文档与您的确认答复，明确范围、技术路线、参数与验收标准，为后续架构设计与实施提供基线。

## 1. 关键决策确认
1) 证书与 HTTPS
- 采用 Let’s Encrypt 自动签发/续期。
- 将使用 Nginx + Certbot（HTTP-01）方案；上线后以 80 端口完成 ACME 验证并自动续期，443 提供 TLS 服务。
- 正式域名已确认：mtm-helper.com（用于 server_name、证书与 CSRF/CORS 配置）。

2) 部署环境
- 使用云容器服务，目标宿主系统为 Ubuntu 22.04 LTS（由您确认，已冻结为正式目标）。
- 运行形态：docker compose v2（Linux 容器镜像）。说明：启用阿里云 registry-mirrors，加速拉取；按 Ubuntu 基线进行安全加固（UFW、fail2ban 可选）。
- 网络：公网 IP 39.106.3.26；主私网 IP 172.31.217.45（用于安全组/白名单对齐）。

3) 推送与兜底
- 短信：启用作为兜底通道；需提供短信服务商凭据（AK/SK、签名、模板 ID），未配置则默认关闭。
- 邮件：不启用（由短信替代，可在后续阶段按需追加）。
- 接受“iOS 需安装 PWA 才能接收 Web Push”的前提；未安装/未授权时默认提供 ICS（系统日历）作为兜底。

4) 提醒交互
- 贪睡默认 15 分钟；在设置中允许自定义（存储为用户偏好）。

5) 调度与扩缩容
- 近期不横向扩更多 worker；但需要跨实例防重（使用 Redis 分布式锁 + 去重键）。

6) 规模预估
- 预计日活 30；MySQL 最大连接数 100（使用托管 RDS）。

7) 域名与跨域
- 已确认主域名：mtm-helper.com。
- 反向代理策略：同域部署，/api 由 Nginx 反代后端。
- Django 安全基线：ALLOWED_HOSTS=mtm-helper.com；CSRF_TRUSTED_ORIGINS=https://mtm-helper.com；CORS 白名单与之对齐。

8) 观测与告警
- 暂无现成 ELK/Loki/Prometheus/Grafana；我们提供最小可行的结构化日志 + 关键指标采集与阈值告警方案（可先基于日志/状态页）。

9) 备份与留存
- 数据库与日志留存周期 30 天；按此制定备份频率与清理策略。

## 2. 技术实现方案（与现有架构对齐）
1) 前端（Vue3 + Vite）
- 引入 PWA：vite-plugin-pwa + manifest + Service Worker，启用离线缓存、更新策略与安装引导。
- 移动端体验：触控区域优化、骨架屏、网络状态提示；禁止使用 dev 代理（已符合）。
- 构建产物由 Nginx 托管：dist 中带指纹资源启用长缓存（immutable），HTML 适度缓存（短时）。

2) 后端（Django + DRF）
- 进程模型：gunicorn 多 worker（建议 3 workers × 2 threads = 6 并发，保守占用 DB 连接 < 100）。
- 连接参数：CONN_MAX_AGE 120s；MySQL connect_timeout 5s，read_timeout 15s（保持与上游/下游超时一致性）。
- 安全：DEBUG=False、严格 ALLOWED_HOSTS/CSRF/CORS、Secure/HttpOnly/SameSite=Lax Cookie、SECURE_SSL_REDIRECT=True、SECURE_PROXY_SSL_HEADER 设置。
- 日志：统一 JSON，关键字段 request_id/user_id/reminder_id/channel/retry/latency/error_type。

3) 调度（独立 worker 容器）
- 将 scheduler 从 web 进程剥离，新建 worker 服务（compose 独立 service）。
- 防重：Redis 分布式锁（集群可扩展），按用户/提醒维度去重键；失败指数退避与死信计数。
- 通道：主 Web Push；兜底 ICS；（短信作为兜底，凭据就绪后启用）。
- 回执：确认/贪睡/跳过接口更新提醒状态并触发后续计划。

4) 网关（Nginx）
- 反代后端 /api，托管前端 dist；启用 gzip/br 压缩与缓存策略；设置安全头（HSTS、X-Frame-Options、X-Content-Type-Options、Referrer-Policy、CSP 可选）。
- Let’s Encrypt：http-01 验证路径 /.well-known/acme-challenge 直通；证书与密钥通过共享卷挂载。

5) docker-compose（production profile）
- frontend 构建镜像仅产出 dist；运行时不暴露 3000 端口。
- backend 使用 gunicorn；增加 healthcheck；env_file 管理生产变量。
- worker 独立 service；Redis 沿用现有镜像；MySQL 使用外部 RDS（不再在 compose 启动 mysql 容器）。
- restart 策略：always/ unless-stopped；资源限制按宿主规格设置。

## 3. 参数与边界（“魔法数字”校验）
- Gunicorn：workers=3、threads=2（初始值，依据 CPU/负载再调），timeout=60s，graceful-timeout=30s。
  - 依据：最大 DB 连接 100，当前并发需求低；总连接预算（web） < 12（含预留）。
- Django DB：CONN_MAX_AGE=120s（避免频繁握手）；连接超时 5s、读超时 15s；重试策略由业务层控制。
- Nginx：proxy_read_timeout 60s；client_max_body_size 10m（按上传需求可调）。
- 缓存：静态 fingerprint 资源 Cache-Control: public, max-age=31536000, immutable；HTML 60s。
- 贪睡：默认 15 分钟，可在设置界面覆盖（5-60 分钟区间）。

以上均为安全初值，后续以压测与观测指标微调。

## 4. 验收标准（可测试）
- HTTPS 与安全
  - 80→443 强制跳转；TLS 有效；HSTS 启用；安全头检查通过（至少 X-Frame-Options/ X-Content-Type-Options/ Referrer-Policy）。
- 部署与健康
  - Nginx 提供 dist + 反代 /api；backend gunicorn 运行；worker 按分钟扫描并执行推送；三个服务健康检查通过。
- 功能与体验
  - 移动端可安装 PWA，离线可浏览主要页面；首访权限与安装引导正常；网络切换有提示。
  - 提醒准时触达：已安装且授权→Web Push；未安装→可生成 ICS；贪睡 15 分钟生效并可自定义；短信兜底在凭据配置后验证可用。
- 观测与稳定
  - 结构化日志落地；推送失败率 < 2%；调度滞后 < 60s；后端 5xx 率低；无明显连接池耗尽或超时级联。

## 5. 集成点与改动清单
- 新增文件
  - nginx.conf（生产模板）
  - 前端 manifest 与 Service Worker（PWA）
  - 后端：Web Push 订阅模型与迁移、订阅/退订/心跳 API、回执 API、管理命令 run_reminder_worker
- 变更文件
  - docker-compose.yml：生产段落（profile=production）完善 healthcheck、env_file、certbot sidecar、卷与只读策略；移除 mysql 容器，改为 RDS 连接。
  - backend/Dockerfile：切换到 gunicorn 启动
  - backend/settings.py：生产安全项与连接参数（指向 RDS）
  - 前端：安装 vite-plugin-pwa 并配置

## 6. 依赖与前置条件
- 已提供正式域名清单：
  - 业务入口：mtm-helper.com（A 记录指向 39.106.3.26）
  - 数据库应用层 CNAME：db-prod.mtm-helper.com（指向“实际 RDS Endpoint”，稍后由您提供后配置）
  - 说明：当前阶段采用同域 /api 反代，无需单独 api/static 子域；若后续拆分，可追加 api.mtm-helper.com 与 static.mtm-helper.com。
- 云容器服务开放 80/443；DNS 解析正确指向宿主；RDS 安全组放行来自宿主公网/私网的访问（39.106.3.26/172.31.217.45）。

## 7. 风险与回滚
- 风险：证书签发受限（DNS/防火墙/端口）；解决：临时关闭 443，仅开放 80 完成 http-01；或切换 DNS-01（需 DNS API）。
- 风险：Web Push 在 iOS 未安装 PWA 不触达；解决：清晰引导 + ICS 兜底；短信为最终兜底（凭据就绪后）。
- 回滚：保留当前 dev 方案可快速切回；compose 使用 profile 切换，生产失败可回退到开发配置进行故障隔离。

## 8. 下一步
- 域名与解析：
  1) 在 DNS 服务商为 mtm-helper.com 创建 A 记录 → 39.106.3.26
  2) 创建 CNAME：db-prod.mtm-helper.com → <RDS_Endpoint_待提供>
  3) 我方生成 Nginx/Certbot 最小模板并提交
- 待提供短信服务凭据后：
  1) 追加短信通道实现与配置
  2) 测试与验收用例补充（失败策略/重试/报警）