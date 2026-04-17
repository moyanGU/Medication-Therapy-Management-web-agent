# MTM-Helper 医院内网私有化部署手册 (On-Premise Deployment Guide)

> **文档状态**: Draft (初稿)
> **适用场景**: 医院内网、物理隔离机房 (Air-gapped)、对公网受限的高隐私等级医疗信息网络。

---

## 1. 架构与安全优势概述

MTM-Helper 系统在设计之初即考虑到患者医疗数据的隐私保护（HIPAA / 数据安全法合规要求），天然具备优秀的私有化（On-Premise）基因：

- **数据绝对本地化**：不依赖云数据库（RDS）或云对象存储（OSS）。患者上传的病历、处方及所有的结构化业务数据，均通过 Docker Volumes 挂载至宿主机本地文件系统，确保数据不出院。
- **字段级加密**：诊断结果等核心敏感字段（如 `EncryptedTextField`）已在数据库层面进行落盘加密，防止内网数据库文件泄露导致的信息还原。
- **无状态内网认证**：基于本地派发的 JWT Token 进行会话维持，无需依赖微信开放平台等外部 OAuth 服务。

---

## 2. 推荐的内网部署拓扑 (DMZ 隔离架构)

为了同时满足“**药师在内网办公**”与“**患者在家中/外网使用**”的矛盾需求，推荐采用 **DMZ (非军事化隔离区)** 部署架构：

1. **核心数据区 (深层内网)**：
   - 部署 MySQL (业务数据) 和 Redis (缓存与队列)。
   - **安全策略**：禁止任何公网入站与出站访问，仅允许 DMZ 区的后端服务器 IP 通过 3306 和 6379 端口进行内网直连。
2. **应用服务区 (DMZ)**：
   - 部署 Django 后端 (API/Worker) 和前端 Nginx (静态资源代理)。
   - **安全策略**：后端服务器可通过防火墙白名单访问深层内网的数据区。
3. **网络边界与入口**：
   - **药师 (内网)**：通过医院局域网 (LAN) 直接访问 DMZ 区的应用服务，无需绕行公网。
   - **患者 (外网)**：通过医院对外网开放的安全网关（如 WAF、反向代理服务器）穿透至 DMZ 区。所有的 HTTPS 卸载与流量清洗均在网关层完成。

---

## 3. 离线化打包与交付策略 (Offline Docker Strategy)

当前开源仓库的 `docker-compose.production.yml` 为公网云端环境设计，包含了公网依赖（如运行时 `npm install`、`certbot` 证书申请等）。
**在正式向医院机房交付前，必须按照以下步骤制作“离线镜像包 (Tarball)”：**

### 3.1 在有外网的开发机上构建全量镜像

1. **前端静态化构建**：
   在开发机上执行 `npm ci && npm run build`，将生成的 `dist/` 目录挂载或直接打入 Nginx 镜像中，彻底移除在医院服务器上运行时执行 `npm` 命令的过程。
2. **后端 Python 依赖打包**：
   在开发机的 Dockerfile 中完成所有的 `pip install -r requirements.txt`，生成包含所有依赖的胖镜像（Fat Image）。
3. **导出镜像 (Save)**：
   ```bash
   docker save -o mtm_frontend.tar mtm_helper_frontend:latest
   docker save -o mtm_backend.tar mtm_helper_backend:latest
   docker save -o mtm_mysql.tar mysql:8.0
   docker save -o mtm_redis.tar redis:7.0
   ```

### 3.2 在医院内网服务器上导入与启动

1. 通过 U盘或堡垒机将 `.tar` 镜像包传输至医院内网服务器。
2. **导入镜像 (Load)**：
   ```bash
   docker load -i mtm_frontend.tar
   docker load -i mtm_backend.tar
   # ... 其他基础镜像
   ```
3. **剥离公网配置 (修改 docker-compose.yml)**：
   - 移除所有的 `build` 指令，改为直接引用本地 `image`。
   - 移除 `certbot` 服务及其卷挂载（改用医院信息科分配的内网 SSL 证书，或配置为纯 HTTP 由上层网关处理 HTTPS）。
   - 移除后端容器中可能硬编码的公网 DNS（如 `100.100.2.136`），让容器继承宿主机的内网 DNS。

---

## 4. 外部网络依赖降级清单 (Graceful Degradation)

在完全断网（Air-gapped）的内网环境下，系统部分高级功能将自动降级。请在部署时于 `.env` 中做好相应配置：

### 4.1 短信网关 (SMS)
- **现象**：无法连接阿里云/腾讯云或 Spug 等公网短信 API，会导致请求卡死或不断重试。
- **降级配置**：将后端 `.env` 中的 `SMS_PROVIDER` 设置为 `mock`。
  ```env
  SMS_PROVIDER=mock
  ```
- **影响**：患者无法接收真实的验证码短信。需改由系统管理员在后台手动预设密码，或配合医院的内部短信网关（需二次开发内网 Provider）。

### 4.2 浏览器推送 (PWA Web Push)
- **现象**：由于底层依赖 Google (FCM)、Apple (APNs) 等公网推送服务器，内网下 Service Worker 的推送订阅将失败或超时。
- **降级配置**：保持默认配置，但在断网下，患者将无法在息屏状态下收到系统级服药提醒弹窗。
- **影响**：提醒触达率下降。患者必须保持 MTM 网页处于打开状态，依靠前端的轮询/WebSocket 机制接收响铃提醒。

### 4.3 AI 药学助手 (Page Agent & LLM)
- **现象**：调用公网的 OpenAPI (如 OpenAI/Qwen) 会报 Network Error。
- **降级配置**：
  - **方案 A (关闭 AI)**：若医院无内网算力，在前端配置中增加环境变量 `VITE_ENABLE_AI=false`，隐藏 AI 对话框入口。
  - **方案 B (私有化大模型)**：若医院配备了 GPU 服务器，可通过 Ollama 或 vLLM 在内网本地运行一个开源医疗大模型（如 Qwen2-7B），然后将前端 Agent 的 API Base URL 环境变量指向该内网推理端点（如 `http://192.168.x.x:11434/v1`）。

---

## 5. 运维与数据备份建议

1. **定时备份脚本 (Cron)**：
   利用 `mysqldump` 定期将挂载在宿主机的 MySQL 数据卷备份至医院的 NAS 存储池中。由于字段已加密，备份文件的流转也相对安全。
2. **静态文件清理**：
   对于患者上传的大量病历图片（位于 `/app/media` 挂载卷），需设置定期巡检机制，防范宿主机磁盘爆满。
3. **日志审计**：
   后端的审计日志 (`AuditLog`) 会记录所有敏感数据的变更行为，供信息安全科随时追溯。