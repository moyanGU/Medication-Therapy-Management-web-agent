# 生产部署与运维指南（docker-compose.production.yml）

本文档说明如何使用 `docker-compose.production.yml` 部署与运维 MTM-用药助手的生产环境，包括前端一次性构建、Nginx 挂载验证、服务启动与常见问题处理。

## 1. 概述

- 生产编排文件：`docker-compose.production.yml`
- 角色与职责：
  - `frontend`：在容器内进行一次性前端构建，产物挂载到共享卷 `app_dist`
  - `nginx`：提供 HTTPS 入口、静态资源服务、反向代理 `/api/` 到 `backend:8000`
  - `backend`：Django + Gunicorn 应用服务
  - `redis`：缓存/消息队列
  - `certbot`：证书自动续期（容器常驻）

## 2. 关键配置（节选）

`docker-compose.production.yml` 关键点：

- `frontend.command` 已内置构建回退逻辑：
  - 依赖安装：优先 `npm ci --include=dev`，失败回退到 `npm install --include=dev`
  - 构建命令：优先 `npm run build`，失败回退到 `npm run build:fast`（跳过 TS 检查，仅用 Vite 构建）
- 共享卷：
  - `app_dist`（前端构建产物） → 挂载到 Nginx `/var/www/app`
  - `backend_static`、`backend_media` → 分别挂载到 Nginx `/var/www/static`、`/var/www/media`
- Nginx 配置文件：`./nginx.prod.conf` 挂载到容器 `/etc/nginx/nginx.conf`

## 3. 前置准备

在进行部署/重构建前，请确保以下文件已同步到服务器并保持一致：

- `package.json`、`package-lock.json`（锁文件必须与 `package.json` 同步，推荐在本地通过 `npm install --package-lock-only` 重新生成后再上传）
- `vite.config.ts`（需包含 `build.outDir: 'dist'`、`emptyOutDir: true`、`base: '/'` 等）
- `nginx.prod.conf`（建议包含以下优化：
  - `listen 443 ssl default_server;`（将 HTTPS 设为默认服务）
  - `location ^~ /webui/ { try_files $uri $uri/ /index.html; }`（支持前端路由的回退）
）

示例（Linux/macOS，本地到服务器）：
```bash
scp package.json package-lock.json vite.config.ts nginx.prod.conf \
  <user>@<server>:/opt/mtm-helper/
```

## 4. 一次性前端构建（推荐）

在服务器项目根目录（如 `/opt/mtm-helper`）执行：
```bash
docker compose -f docker-compose.production.yml run --rm frontend \
  sh -lc "(npm ci --include=dev || npm install --include=dev) && (npm run build || npm run build:fast)"
```

验证构建产物是否被 Nginx 获取：
```bash
docker compose -f docker-compose.production.yml exec nginx ls -lah /var/www/app
```

## 5. 启动服务与验证

启动所有生产服务：
```bash
docker compose -f docker-compose.production.yml up -d
```

查看服务与日志：
```bash
docker compose -f docker-compose.production.yml ps
docker compose -f docker-compose.production.yml logs -f nginx
```

如更新了 `nginx.prod.conf`，请校验并热重载：
```bash
docker compose -f docker-compose.production.yml exec nginx nginx -t
docker compose -f docker-compose.production.yml exec nginx nginx -s reload
```

站点验证（生产域名已确认）：
- 浏览器访问 `https://mtm-helper.com/` 或 `https://www.mtm-helper.com/` 应返回首页，静态资源 `/assets/*.css|*.js` 正常加载
- 如需容器内验证，可使用：
  - `docker compose -f docker-compose.production.yml exec nginx wget -qO- https://localhost/`（如启用 HTTPS）

## 6. 常见问题与处理

1) 使用错误的 Compose 文件/路径
- 现象：`backend has neither image nor build context specified` 等
- 处理：确保所有命令均带 `-f docker-compose.production.yml`，且在正确的项目目录执行

2) `npm ci` 失败（锁文件不同步）
- 处理：在本地执行 `npm install --package-lock-only` 重新生成锁文件；或在服务器上回退到 `npm install --include=dev`

3) `/webui/` 访问 500 或日志出现 `rewrite or internal redirection cycle`
- 原因：SPA 路由未设置回退或未命中正确 `server_name`
- 处理：在 `nginx.prod.conf` 中添加：`location ^~ /webui/ { try_files $uri $uri/ /index.html; }`，并确保 `listen 443 ssl default_server;`

4) 容器内 `wget http://localhost/` 报 `Connection refused`
- 原因：HTTP(80) 未启用或仅启用 HTTPS(443)，或安全策略限制
- 处理：改用 `https://localhost/` 验证，或从外部浏览器访问正式域名

## 7. 运维建议

- 前端构建体积优化：如遇到过大 JS chunk，可在 `vite.config.ts` 中启用分包策略（`rollupOptions.output.manualChunks`）
- 依赖安全与升级：定期执行 `npm audit` / `npm audit fix`，并在本地验证后再上传锁文件
- 日志与监控：Nginx 访问日志、后端应用日志应纳入统一监控；发现 5xx 与重定向异常应及时处理

## 8. 术语与约定

- 服务器项目路径为 `/opt/mtm-helper`
- 生产域名为 `https://mtm-helper.com` 与 `https://www.mtm-helper.com`，API 域名为 `https://api.mtm-helper.com`
- 所有 `docker compose` 命令均显式指定 `-f docker-compose.production.yml`，以避免误用其他编排文件

---

如需进一步的生产环境优化或自动化部署（CI/CD、蓝绿发布、零停机重启等），请联系运维或提交 Issue 以获得支持。