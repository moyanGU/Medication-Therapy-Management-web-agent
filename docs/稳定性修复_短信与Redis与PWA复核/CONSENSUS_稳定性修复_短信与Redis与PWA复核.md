# CONSENSUS_稳定性修复_短信与Redis与PWA复核

一、明确需求
- 运行期 Redis 异常聚合告警：在 <mcfile name="middleware.py" path="e:\mtm-helper\backend\apps\core\middleware.py"></mcfile> 的 CacheMiddleware 中，对读取/写入异常进行计数与聚合，阈值触发日志，冷却抑制风暴；参数由 <mcfile name="settings.py" path="e:\mtm-helper\backend\mtm_helper\settings.py"></mcfile> 提供。
- 前端统一响应解包：<mcfile name="api.ts" path="e:\mtm-helper\src\utils\api.ts"></mcfile> 统一处理 { success, data } 的双层结构，兼容 { data: { data: [] } }；401 时清除 token 并跳转登录。
- 短信接口限流容错：Redis 失败时回退 Session 维度限流，确保“验证码发送”接口不因缓存故障中断。
- 监控与Regex：补充生产查询模板（PowerShell/Elasticsearch/Splunk），包含 Redis 聚合告警、401/JWT、CacheMiddleware 异常读写模式。
- 生产 .env.prod.example：固化环境变量与推荐值，不含任何敏感真实值。

二、验收标准（可测试）
1) Redis 聚合告警：在压力/故障注入条件下，日志出现“Redis异常聚合告警”字样，包含窗口内错误次数、阈值、冷却信息；非风暴条件下仅按计数/限频输出。
2) CacheMiddleware 异常容错：READ/WRITE 异常不导致请求失败（IGNORE_EXCEPTIONS=True），业务流程继续。
3) 前端解包一致性：随机抽取 3 个接口（含列表与详情），均从 response.data.data.* 读取；401 触发后清除 token、跳转登录；控制台有关键日志。
4) 短信接口“四大元素”一致：
   - 方法/路径：POST /api/auth/send_verification_code
   - 请求参数：{ phone: string }（JSON）
   - 响应结构：{ success: boolean, data: { sent: boolean } }
   - 认证与状态码：匿名可用，限流 429；Redis 失败仍返回 200 且 sent=true（DEV_ECHO 可控）
5) 监控查询落地：在 docs/MONITOR_生产监控查询与Regex操作指引.md 中新增 Redis/401/JWT/CacheMiddleware 模式，并能通过 docker logs 或 ELK/Splunk 实际过滤到样例日志。
6) 不引入新代理与模拟：无 Vite 代理；接口均真实调用，页面不显示模拟数据。

三、技术实现方案
- 中间件：新增 _inc_redis_error() 与全局状态（计数 + 锁 + 冷却时间），在 CacheMiddleware 的 try/except 中调用；日志统一使用 mtm_helper logger。
- 配置：settings.py 中添加 REDIS_ERROR_ALERT_WINDOW_SECONDS/REDIS_ERROR_ALERT_THRESHOLD/REDIS_ERROR_ALERT_COOLDOWN_SECONDS，支持 env 覆盖。
- 前端：ApiClient.handleResponse 统一解包、处理401；在HTTP层打印关键日志（请求/响应摘要、错误栈）。
- 短信接口：Redis 不可用时走 Session 限流（读/写容错）；DEV_ECHO 在 DEBUG 下输出验证码（仅供开发）。
- 监控：文档中固化 Regex 与查询模板，Windows 上提供 Select-String 示例。

四、任务边界与限制
- 不提交任何真实密钥；.env.prod.example 使用占位值。
- 不改变业务接口契约，仅修复性增强；如需新增外部告警推送（Spug），需后续批准与参数提供。

五、风险与回滚
- 连接池与并发：若观察到 DB Threads_connected 接近上限，立即降低并发（workers/threads），下调 CONN_MAX_AGE。
- Redis 异常持续：若错误率持续升高，临时禁用压缩与降低 max_connections，确认网络与密码一致。
- 回滚策略：移除聚合告警计数（保持容错不变）、恢复原监控阈值、保留日志过滤模板。

六、依赖与集成
- docker-compose.prod.yml 读取 .env.prod，应用 gunicorn 并发与超时；Nginx 反向代理保持不变。
- 日志位置：backend/logs/django.log；需要确保目录存在（settings.py 已创建）。

七、完成标记
- 当上述验收标准 1-6 均达成，标记本任务为完成并转入评估阶段。