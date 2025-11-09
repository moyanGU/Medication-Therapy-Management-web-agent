# TODO_老年人模式

## 1）部署文件清单
- 前端静态资源：
  - `dist/`（运行 `npm run build` 生成）
  - `index.html`
  - `assets/*`
- 部署配置：
  - `nginx.prod.conf`（或 `nginx.conf`）
  - `docker-compose.prod.yml`（或 `docker-compose.production.yml`）
  - `Dockerfile.frontend`
- 证书与域名：
  - `certbot/`（若使用 Let’s Encrypt）
  - 站点证书路径（示例：`/etc/letsencrypt/live/<domain>/fullchain.pem`、`privkey.pem`）

## 2）服务器端配置检查
- Nginx
  - 确认 `root` 指向前端 `dist/` 路径，启用 Gzip/HTTP2；静态缓存策略合理（HTML 不缓存、JS/CSS 图片按版本号缓存）。
  - 检查 `location /`、`try_files $uri $uri/ /index.html;` 确保前端路由正常。
- Docker
  - 前端镜像构建使用 `Dockerfile.frontend`；`docker-compose.prod.yml` 中映射端口与卷；资源限制（内存/CPU）按需配置。
  - 检查宿主机路径与权限（Windows: `D:\Application\Docker\docker`）。
- 证书
  - 证书与密钥路径有效；自动续期任务执行正常；Nginx配置引用路径一致。

## 3）性能监控建议
- 前端
  - 关键交互点打点：老年人模式开关、语音开关、播报触发次数与失败比例。
  - 错误上报：收集 `SpeechSynthesis` 相关异常、浏览器不支持情况。
- 服务器
  - Nginx 访问与错误日志监控；静态资源命中率；响应时间与带宽占用。
  - Docker 容器健康状态；资源利用率指标（CPU/内存）。

## 4）用户体验持续优化方向
- 语音参数
  - 暴露 `pitch` 与 `volume` 设置项，允许用户个性化调整。
  - 按内容类型（标题/提醒）设置不同的停顿与语气。
- 视觉
  - 与 `dark` 主题的对比度细化联动，避免刺眼或过暗。
  - 增加可读性辅助，例如可选更高行高、字重、间距。
- 偏好同步
  - 将 `seniorMode` 与语音开关状态同步到后端作为用户偏好（需要新增 API）。

## 5）浏览器兼容性测试清单
- 桌面
  - Chrome/Edge 最新版本：语音与样式正常；`voiceschanged` 加载语音列表。
  - Firefox：验证 `SpeechSynthesis` 与中文语音可用性；若不支持则开关禁用。
  - Safari (macOS)：验证语音可用性与路由兼容。
- 移动端
  - iOS Safari：语音支持与安装引导；不支持 `beforeinstallprompt` 已使用指引替代。
  - Android Chrome：语音与 PWA 安装流程验证；通知权限检查。
- 回退策略
  - 无语音支持时按钮禁用并提示；UI 不受影响。

---

## 待你确认的事项
- 生产域名与证书路径（如使用 Let’s Encrypt）。
- 前端 `dist/` 的目标同步目录（Nginx `root`）。
- 是否需要将 `seniorMode` 与语音开关持久化到后端（若需要请提供偏好API）。

## 操作指引（示例）
- 构建前端：
  - Windows PowerShell：分别运行
    - `npm install`
    - `npm run build`
- 部署到 Nginx（示例）
  - 将 `dist/` 同步到服务器目标目录
  - 检查 `nginx.prod.conf` 的 `root` 与路由配置
  - 重新加载 Nginx：`nginx -s reload` 或容器重启

备注：按照默认规则，避免使用 Vite 代理；敏感信息（如证书与密钥）不要入库，统一使用环境变量或服务器侧安全路径。