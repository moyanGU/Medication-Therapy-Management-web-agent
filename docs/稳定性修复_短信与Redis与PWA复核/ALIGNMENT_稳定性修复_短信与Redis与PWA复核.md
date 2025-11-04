# ALIGNMENT_稳定性修复_短信与Redis与PWA复核

目标
- 将“稳定性修复_短信与Redis与PWA复核”任务的上下文、范围、技术约束与关键问题统一到一个对齐文档，作为后续 CONSENSUS/DESIGN/TASK 的依据。

一、项目上下文与架构
- 技术栈：Windows 宿主 + docker compose（生产）/本地开发，Nginx + Gunicorn + Django REST + MySQL(RDS) + Redis(Cache)
- 前端：Vue 3 + Pinia；统一 HTTP 客户端 <mcfile name="api.ts" path="e:\mtm-helper\src\utils\api.ts"></mcfile>，兼容后端双层 data 解包；路由与鉴权在 <mcfile name="auth.ts" path="e:\mtm-helper\src\stores\auth.ts"></mcfile>、<mcfile name="http.ts" path="e:\mtm-helper\src\utils\http.ts"></mcfile>
- 后端：Django 设置 <mcfile name="settings.py" path="e:\mtm-helper\backend\mtm_helper\settings.py"></mcfile>；中间件 <mcfile name="middleware.py" path="e:\mtm-helper\backend\apps\core\middleware.py"></mcfile>；应用启动自检 <mcfile name="apps.py" path="e:\mtm-helper\backend\apps\core\apps.py"></mcfile>
- 日志：RotatingFileHandler 输出至 backend/logs/django.log；控制台输出同时开启。

二、原始需求与范围边界
- 稳定性修复内容包括：
  1) 短信接口（send_verification_code）限流与容错增强（避免Redis异常导致用户层面失败）。
  2) Redis 运行期异常聚合告警（读取/写入异常计数、阈值触发聚合日志、冷却防风暴）。
  3) 前端统一响应解包与401处理，修复模块误用 response.data.xxx 的问题（应访问 response.data.data.xxx）。
  4) 监控与日志过滤 Regex 固化，提供PowerShell/Elasticsearch/Splunk查询模板。
  5) 生产 .env.prod.example 模板（不含敏感值），固化必填项与推荐默认值。
- 边界与不做事项：
  - 不引入新外部服务（如新监控平台），仅在现有日志基础上聚合与查询。
  - 不提交任何真实密钥与口令；模板仅提供占位与注释。
  - 不改变业务流程与接口契约（除修复性行为，如401统一处理与限流容错）。

三、关键约束与现状
- 后端返回结构：{ success: true, data: { ... } }；部分模块历史上直接访问 response.data.xxx，需统一为 response.data.data.xxx。
- Redis 配置项来源于环境变量：REDIS_HOST/PORT/PASSWORD、REDIS_POOL_MAX_CONNECTIONS、REDIS_SOCKET_CONNECT_TIMEOUT、REDIS_SOCKET_TIMEOUT、CACHE_DEFAULT_TTL、REDIS_KEY_PREFIX、REDIS_ENABLE_COMPRESSION；新增聚合告警参数：REDIS_ERROR_ALERT_WINDOW_SECONDS、REDIS_ERROR_ALERT_THRESHOLD、REDIS_ERROR_ALERT_COOLDOWN_SECONDS。
- 会话与安全：SESSION_ENGINE=cached_db；SIMPLE_JWT 使用 SECRET_KEY；生产安全开关默认启用（HSTS/SSL redirect 等）。

四、存在歧义与需确认项（按优先级）
1) 生产并发预算：Gunicorn workers/threads 当前计划 2×4 起步，是否与 RDS max_connections=300 保持安全余量？
2) Redis 最大连接数：REDIS_POOL_MAX_CONNECTIONS 生产建议值（现为100），是否与部署规模匹配？上限与Redis服务端 maxclients 关系？
3) Spug 推送：是否需要将聚合告警推送至 Spug？若是，需要 SPUG_PUSH_* 具体参数（模板ID、应用名）。
4) CORS/CSRF 白名单：生产域名列表确认，避免误拦截与跨域失败。
5) 监控接入：是否已有 ELK/Splunk？如果没有，临时使用 PowerShell + docker logs 即时采样方案。

五、初步决策与对齐
- 已实施：
  - 中间件 CacheMiddleware 增强：异常容错（IGNORE_EXCEPTIONS=True）、运行期异常聚合告警（计数+阈值+冷却）。
  - 前端统一响应解包与日志增强（http/api 层），并在401清除凭证、重定向登录。
  - 短信接口限流容错：Redis 不可用时回退 Session 限流，避免用户失败。
- 待实施交付：
  - CONSENSUS 文档固化验收标准与技术方案；
  - 生产 .env.prod.example 模板；
  - 监控查询与Regex汇编（补充 Redis 聚合告警与401/JWT 专项）。

六、质量门控（对齐阶段完成标准）
- 需求边界清晰：仅稳定性与监控增强，不改变业务接口契约。
- 技术方案与现有架构对齐：不新增外部依赖，复用现有 Django/Redis/日志体系。
- 验收标准明确：提供可测试的日志模式、告警触发条件、接口“四大元素”与示例查询。
- 假设已确认：双层 data 解包、Redis 环境变量命名与职责、生产安全开关默认值。

附：关键文件引用
- 设置：<mcfile name="settings.py" path="e:\mtm-helper\backend\mtm_helper\settings.py"></mcfile>
- 中间件：<mcfile name="middleware.py" path="e:\mtm-helper\backend\apps\core\middleware.py"></mcfile>
- 启动自检：<mcfile name="apps.py" path="e:\mtm-helper\backend\apps\core\apps.py"></mcfile>
- 前端 API 客户端：<mcfile name="api.ts" path="e:\mtm-helper\src\utils\api.ts"></mcfile>
- 前端 HTTP 封装：<mcfile name="http.ts" path="e:\mtm-helper\src\utils\http.ts"></mcfile>
- 认证 Store：<mcfile name="auth.ts" path="e:\mtm-helper\src\stores\auth.ts"></mcfile>


目标：对齐“生产稳定性与短信/PWA能力达标”的范围、问题与决策，形成后续架构与实施依据。

## 1. 项目上下文分析
- 技术栈
  - 前端：Vue 3 + Vite + vite-plugin-pwa，状态管理 Pinia，HTTP axios；Service Worker 通过 virtual:pwa-register 注册；相关文件：<mcfile name="vite.config.ts" path="vite.config.ts"></mcfile> <mcfile name="main.ts" path="src/main.ts"></mcfile> <mcfile name="AppHeader.vue" path="src/components/layout/AppHeader.vue"></mcfile>
  - 后端：Django 4.2 + DRF + SimpleJWT；缓存使用 django-redis；Session 使用 cached_db；日志使用 RotatingFile；相关文件：<mcfile name="settings.py" path="backend/mtm_helper/settings.py"></mcfile>
  - 生产部署：docker-compose.prod（后端、worker、redis、nginx、certbot）；Nginx反代与静态托管；相关文件：<mcfile name="docker-compose.prod.yml" path="docker-compose.prod.yml"></mcfile> <mcfile name="nginx.conf" path="nginx.conf"></mcfile>
- 关键功能
  - 短信验证码：后端API实现手机号校验、频率限制、验证码生成与缓存、模板化、Spug集成；相关符号：<mcsymbol name="send_verification_code" filename="views.py" path="backend/apps/authentication/views.py" startline="298" type="function"></mcsymbol>
  - 中间件：请求日志、缓存（GET）、安全头、限流（IP）；相关符号：<mcsymbol name="CacheMiddleware" filename="middleware.py" path="backend/apps/core/middleware.py" startline="116" type="class"></mcsymbol> <mcsymbol name="RateLimitMiddleware" filename="middleware.py" path="backend/apps/core/middleware.py" startline="242" type="class"></mcsymbol>
  - PWA：manifest、SW注册、更新提示与安装横幅；相关文件：<mcfile name="index.html" path="index.html"></mcfile> <mcfile name="vite-env.d.ts" path="src/vite-env.d.ts"></mcfile>

## 2. 需求与范围（本轮）
- 生产稳定性基线达标：Redis缓存与会话稳定、认证链路可靠、无级联故障。
- 短信验证码能力达标：真实发送或明确的临时策略（开发回显/禁用入口），频率限制在Redis异常时仍有效。
- PWA复核：更新检测、离线资源就绪、安装/更新横幅正常，无代理配置。

## 3. 关键问题清单（初步）
- Redis连接异常高频（10061/ConnectionRefused），缓存层降级导致验证码频率限制失效的边缘情况。
- 生产环境未配置短信通道变量，真实发送不可行；仅在DEBUG或SMS_DEV_ECHO时回显。
- 认证错误集中出现（InvalidToken/AuthenticationFailed/NotAuthenticated），可能与Authorization头、令牌生命周期与会话层不稳相关。
- Session Engine使用cached_db，Redis异常时退化性能与一致性风险。

## 4. 根因假设与证据
- 假设1：REDIS_PASSWORD在服务端requirepass开启但客户端未配置或不一致，导致连接拒绝（10061）。
  - 证据：<mcfile name="docker-compose.prod.yml" path="docker-compose.prod.yml"></mcfile> 中 `redis: command: redis-server --requirepass ${REDIS_PASSWORD}`；<mcfile name="settings.py" path="backend/mtm_helper/settings.py"></mcfile> 中 Redis LOCATION 根据 REDIS_PASSWORD 拼接。
- 假设2：验证码限流回退不完整（仅回退验证码，不回退rate_key），Redis异常时手机号维度限流失效。
  - 证据：<mcsymbol name="send_verification_code" filename="views.py" path="backend/apps/authentication/views.py" startline="298" type="function"></mcsymbol> 的异常分支仅将 `sms:code:{phone}` 写入 Session。
- 假设3：未配置短信通道（SPUG或供应商），生产不能真实投递；开发模式回显掩盖问题。
  - 证据：环境文件未见短信变量；<mcfile name="settings.py" path="backend/mtm_helper/settings.py"></mcfile> 中 SPUG_* 配置可用但默认禁用。

## 5. 决策点（需要确认）
1) 生产使用 docker-compose 内的 Redis 服务，还是外部 Redis（Windows本机 D:\\Redis-x64-3.0.504）？
2) 生产 .env.prod 是否将 REDIS_PASSWORD 显式设置且与服务端一致？（当前建议尽快对齐）
3) 短期短信策略：启用 SMS_DEV_ECHO 以保证流程，或暂时隐藏/禁用短信入口，待供应商接入？
4) 同意在 <mcfile name="views.py" path="backend/apps/authentication/views.py"></mcfile> 中对 rate_key 增加 Session 回退以保障限流？
5) 前端是否需要我审计并统一 response.data.data 的访问模式以防嵌套结构误用？

## 6. 监控与日志查询
- 错误提取Regex
  - Redis连接/超时：`(?i)redis.*(connection|connect).*refused|10061`；`(?i)(redis).*(timeout|timed out|socket.*timeout)`
  - 缓存容错：`\[CacheMiddleware\].*缓存读取失败|\[CacheMiddleware\].*缓存写入失败`
  - 短信验证码：`发送验证码请求: phone=\d{11}`；`sms:(code|rate):\d{11}`；`发送过于频繁`
  - 认证错误：`(?i)AuthenticationFailed|InvalidToken|NotAuthenticated`；`(?i)JWT认证失败|JWT认证异常`
- Windows日志命令示例（按需）
  - `Select-String -Path backend/logs/django.log -Pattern "redis|10061|缓存失败|发送验证码请求|AuthenticationFailed|InvalidToken|NotAuthenticated" | Select-Object Line`
  - 每小时汇总计数用于趋势分析与阈值告警。

## 7. 验收标准
- Redis：后端启动自检通过；运行期 Redis 连接错误率低于1%且无持续的10061错误；Session与缓存一致性不影响核心功能。
- 短信：在Redis异常注入情况下，手机号维度限流仍有效；生产具备明确策略（真实发送或临时回显/禁用）。
- 认证：在正常使用下登录/刷新/访问核心接口无InvalidToken/NotAuthenticated的高频告警；Authorization头格式统一。
- PWA：SW注册正常、更新提示触发、离线资源就绪；无Vite代理配置。

## 8. 时间线与关联分析方法
- 构建错误时间线：按上述Regex聚类最近24小时日志，绘制每类错误的时间分布。
- 与变更关联：将 docker-compose/.env/settings 的修改时间点叠加到时间线，评估是否存在变更后错误激增（尤其是Redis与认证相关）。
- 级联识别：观察缓存错误→认证错误→请求时延的先后出现顺序，识别是否存在级联效应。

## 9. 预防策略与配置审计要求
- Redis：在CACHES保留IGNORE_EXCEPTIONS但新增健康检查与告警；REDIS_POOL_MAX_CONNECTIONS与Gunicorn并发匹配，避免资源浪费或饥饿。
- 限流与会话：完善rate_key回退；记录频率限制命中率，避免失效。
- 安全：ALLOWED_HOSTS/CORS/CSRF在生产域名下对齐；SIMPLE_JWT时长与前端刷新策略一致。
- 文档：将决策与参数在CONSENSUS中固化，避免“魔法数字”随意更改。

---
后续：待你确认第5节的决策点后，我将生成CONSENSUS与DESIGN，并进入代码修复与测试。