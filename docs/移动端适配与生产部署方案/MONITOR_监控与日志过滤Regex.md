# 监控与日志过滤（Regex 指南）- 生产

目标
- 快速发现并定位常见故障：Nginx 5xx、上游超时、证书签发失败、RDS 解析/连接异常、Redis 连接/鉴权失败。
- 给出命令行过滤示例（容器/宿主），以及日志平台（ELK/Splunk）查询模板。

告警阈值建议
- Nginx 5xx 比例 > 1% 持续 5 分钟 → 警报
- DB 连接失败/解析失败 > 3 次/分钟 → 警报
- 证书续期失败 任意出现 → 警报
- Redis 连接/鉴权失败 > 3 次/分钟 → 警报

一、容器日志（docker compose logs）
Nginx 502/504（access.log）
- docker compose logs nginx -f | grep -E '" (GET|POST|PUT|DELETE|PATCH|HEAD) .*" 50(2|4) '
Nginx upstream 典型错误（error.log）
- docker compose logs nginx -f | grep -E 'upstream (prematurely closed connection|timed out)|connect\(\) failed'
Certbot 签发/续期失败
- docker compose logs certbot -f | grep -E 'acme:error:(rateLimited|unauthorized|dns)|Invalid response from|Timeout during connect'
MySQL 解析/连接失败（后端/worker）
- docker compose logs backend -f | grep -Ei 'getaddrinfo|ENOTFOUND|EAI_AGAIN|Name or service not known|Can\'t connect to MySQL server|Too many connections|Communications link failure|Lost connection to MySQL'
Redis 典型错误（后端/worker）
- docker compose logs backend -f | grep -Ei 'NOAUTH Authentication required|WRONGPASS|DENIED Redis is running in protected mode|Connection refused|getaddrinfo (EAI_AGAIN|ENOTFOUND)'

二、Windows（宿主）PowerShell 过滤示例
- docker compose logs nginx | Select-String -Pattern '" (GET|POST|PUT|DELETE|PATCH|HEAD) .*" 50(2|4) '
- docker compose logs certbot | Select-String -Pattern 'acme:error:(rateLimited|unauthorized|dns)|Invalid response from|Timeout during connect'
- docker compose logs backend | Select-String -Pattern 'getaddrinfo|ENOTFOUND|EAI_AGAIN|Name or service not known|Can\'t connect to MySQL server|Too many connections|Communications link failure|Lost connection to MySQL'

三、日志平台查询模板
ELK（Kibana - KQL/Lucene 示例）
- Nginx 5xx：nginx.access.status:>=500 AND url.domain:"mtm-helper.com"
- DB 连接/解析异常：message:/getaddrinfo|ENOTFOUND|EAI_AGAIN|Can't connect to MySQL|Too many connections|Communications link failure/
- Certbot：message:/acme:error:(rateLimited|unauthorized|dns)|Invalid response from|Timeout during connect/
- Redis：message:/NOAUTH|WRONGPASS|protected mode|Connection refused/

四、异常时间线与聚合
Nginx 5xx 按分钟聚合（容器内）
- awk '($9 ~ /^50[24]$/){ts=$4; gsub(/\[|\]/,"",ts); m=substr(ts,1,17); c[m]++} END{for (k in c) print k,c[k]}' /var/log/nginx/access.log | sort
证书续期失败定位
- grep -nE 'renew.*(failed|error)' /var/log/letsencrypt/letsencrypt.log

五、建议的监控指标
- Nginx：5xx 比例、P95/P99 响应时间、Upstream 响应时间、活动连接数
- 后端：请求数、错误率、DB 连接池使用率、超时率
- MySQL：连接数（Threads_connected）、拒绝连接数、慢查询、Buffer Pool 命中率
- Redis：连接数、拒绝连接/鉴权失败数、命中率、内存使用、逐出次数

六、常见根因速查
- Nginx 502：后端未启动/端口错误、upstream 超时（proxy_read_timeout 过短）、容器 DNS 不通
- Nginx 504：后端处理超时（检查应用超时、DB 慢查询、上游依赖）
- Certbot 失败：ACME 路径不可读/DNS 误配/防火墙阻断/速率限制
- DB 连接失败：RDS 白名单未放行/密码错误/连接池饱和（Too many connections）/DNS 解析失败
- Redis 失败：密码错误/未开启 requirepass/网络不可达

占位信息
- CERTBOT_EMAIL: [待填：CERTBOT_EMAIL]
- RDS_ENDPOINT: [待填：RDS_ENDPOINT]