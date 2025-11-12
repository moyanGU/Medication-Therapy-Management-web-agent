# 稳定性修复验收：Redis 认证与健康检查恢复

## 背景与问题
- 健康检查接口 `/api/health/` 返回 `degraded`，原因是缓存服务（Redis）不健康。
- Django 端 Redis 连接串为 `redis://:Ghp880218@localhost:6379/0`，包含密码；本机 Redis 服务此前以无密码方式启动，导致客户端发送 `AUTH` 时出现 `AuthenticationError`，被 `IGNORE_EXCEPTIONS` 吞掉，健康检查降级。

## 修复措施
1. 环境变量对齐：在 `backend/.env` 显式增加 `REDIS_PASSWORD=Ghp880218`。
2. 重启 Redis 并启用密码：
   - 释放 6379：`netstat -ano | findstr 6379` → `taskkill /F /PID <PID>`
   - 以配置文件与口令启动：`D:\Redis-x64-3.0.504\redis-server.exe E:\mtm-helper\redis.conf --requirepass <REDIS_PASSWORD>`
   - 新增脚本：`scripts/windows/start_redis_secure.ps1` 支持自动从 `backend/.env` 读取密码并启动。
3. 应用内验证：在 Django 环境通过 `django_redis.get_redis_connection('default')` 执行 `ping/set/get`；`django.core.cache.cache.set/get` 验证读写成功。

## 验收结果
- `curl -i http://127.0.0.1:8000/api/health/` 返回：
  - `{"success": true, "data": {"status": "healthy", "services": {"database": "healthy", "cache": "healthy", "application": "healthy"}}}`
- 结论：健康检查恢复正常，缓存服务健康。

## 接口四要素（健康检查）
- 地址：`GET /api/health/`
- 入参：无
- 返回结构：`{ success: true, data: { status: 'healthy'|'degraded'|'unhealthy', services: { database, cache, application }, ... }, message }`
- 业务约束：缓存异常被忽略以保障请求不失败；健康检查会据此返回 `degraded`。

## 操作指引
1. 启动 Redis（安全方式）：
   - `pwsh -File scripts/windows/start_redis_secure.ps1`
   - 或手动：`$env:REDIS_PASSWORD="***"; D:\Redis-x64-3.0.504\redis-server.exe E:\mtm-helper\redis.conf --requirepass $env:REDIS_PASSWORD`
2. 验证端口：`netstat -ano | findstr 6379`
3. 验证应用缓存：在 `E:\mtm-helper\backend` 下：
   - `set DJANGO_SETTINGS_MODULE=mtm_helper.settings`
   - `python -c "import django; django.setup(); from django_redis import get_redis_connection; from django.core.cache import cache; c=get_redis_connection('default'); print(c.ping()); c.set('k','v',ex=30); print(c.get('k')); cache.set('ck','cv',timeout=30); print(cache.get('ck'))"`

## 经验总结与建议
- 环境一致性：后端 `.env` 与 Redis 服务口令必须一致；生产环境统一通过环境变量注入，避免明文。
- 监控入口：健康检查与应用日志是首选诊断渠道；`IGNORE_EXCEPTIONS` 能保障稳态但会降低故障显性。
- 脚本化：建议统一使用 `scripts/windows/start_redis_secure.ps1` 启动本地 Redis，减少手工误差。

## 待办（如需）
- 若生产环境采用独立 Redis 服务，请在部署脚本中同步注入 `REDIS_PASSWORD` 并执行存活检测（PING/SET/GET）。