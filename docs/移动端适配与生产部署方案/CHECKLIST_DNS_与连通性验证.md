# DNS 与连通性验证清单（生产）

适用域名：mtm-helper.com（主域）
数据库访问域名（CNAME）：db-prod.mtm-helper.com → [待填：RDS_ENDPOINT]
证书邮箱： [待填：CERTBOT_EMAIL]

注意
- 首次切换建议 TTL=300s（便于回滚），稳定后可提升至 1800~3600s 减少权威查询压力。
- 切勿在仓库提交任何真实密钥/密码，.env.prod 仅在服务器侧保存。

一、DNS 记录配置
1) A 记录（网站接入）
- 主机名: @
- 记录类型: A
- 值: 39.106.3.26
- TTL: 300

2) CNAME 记录（RDS 访问）
- 主机名: db-prod
- 记录类型: CNAME
- 值: [待填：RDS_ENDPOINT]（例如 rm-xxxx.mysql.rds.aliyuncs.com）
- TTL: 300

3) IPv6（可选）
- 若服务器未启用公网 IPv6 或安全组未放行，不要配置 AAAA 记录，以免 Happy Eyeballs 导致 502/超时抖动。

二、解析生效验证（本地/Windows）
PowerShell（优先）
- Resolve-DnsName mtm-helper.com
- Resolve-DnsName db-prod.mtm-helper.com
- 公网递归对比：Resolve-DnsName mtm-helper.com -Server 8.8.8.8
nslookup（备用）
- nslookup mtm-helper.com 8.8.8.8
- nslookup db-prod.mtm-helper.com 1.1.1.1
验收要点
- A 记录指向 39.106.3.26
- db-prod.mtm-helper.com 可 CNAME 链路解析至真实 RDS Endpoint
- TTL 为期望值（300s）

三、服务器侧连通性（Ubuntu/生产机）
HTTP/Nginx 监听
- curl -I http://mtm-helper.com/
- 或 nc -zv 127.0.0.1 80
RDS 解析与 3306 端口探测
- getent hosts db-prod.mtm-helper.com
- nc -zv db-prod.mtm-helper.com 3306
MySQL 握手（仅验证链路，可不输入密码）
- mysql -h db-prod.mtm-helper.com -u admin -p
容器网络连通
- docker compose exec backend sh -c "getent hosts db-prod.mtm-helper.com || ping -c1 db-prod.mtm-helper.com"
- docker compose exec backend sh -c "nc -zv db-prod.mtm-helper.com 3306 || timeout 5 bash -lc 'exit 1'"

四、依赖与白名单
- RDS 安全组/白名单放行来自服务器公网 IP 的 3306/TCP。
- 如启用 RDS SSL，需在应用端开启并导入 RDS CA；否则明确接受“非 SSL”连接风险。

五、Certbot（首发仅 HTTP）
健康检查
- 在宿主 certbot/www/health.txt 写入任意内容
- 访问 http://mtm-helper.com/.well-known/acme-challenge/health.txt 应返回同内容
签发命令（webroot 模式；注意 PowerShell 不支持 &&，分步执行）
- docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm certbot certonly --webroot -w /var/www/certbot -d mtm-helper.com --email [待填：CERTBOT_EMAIL] --agree-tos --no-eff-email
启用 HTTPS（签发成功后）
- 编辑 nginx.conf 解除 443 server 块注释，并在 80 端口开启 301 跳转
- docker compose exec nginx nginx -s reload
续期演练
- docker compose exec certbot certbot renew --dry-run
- 续期后需重载 Nginx（推荐使用系统计划任务或容器内 post-hook 方案）

六、回滚策略
- 保留旧 A/CNAME 的可恢复配置（短 TTL 缩短回滚生效时间）。
- 若错误率/超时率越过阈值，先回退 DNS，再排查应用/网络。

七、上线验收清单（勾选）
- [ ] A 记录 @→39.106.3.26 生效（TTL=300）
- [ ] CNAME db-prod→[待填：RDS_ENDPOINT] 生效（TTL=300）
- [ ] 服务器与容器内均可解析 db-prod.mtm-helper.com
- [ ] Certbot 首发 HTTP 验证通过，证书签发成功并切至 HTTPS
- [ ] RDS 白名单已放行，3306 可达；应用以 CNAME 访问而非直连 Endpoint
- [ ] .env.prod 已配置真实值（DB_PASSWORD、REDIS_PASSWORD、DEBUG=False），且未纳入 Git 版本控制

附：已对齐的默认配置（供对照）
- 主域名：mtm-helper.com
- RDS CNAME：db-prod.mtm-helper.com（值：RDS Endpoint 见占位）
- docker-compose.prod.yml：env_file=.env.prod，DB_HOST 默认 db-prod.mtm-helper.com