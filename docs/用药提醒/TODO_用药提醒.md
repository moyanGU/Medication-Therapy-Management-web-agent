# 用药提醒 - TODO 与缺失配置

## 待办事项
1) 后端 .env：确认并填写
   - DB_USER（建议使用 mtm_helper_dev）
   - DB_PASSWORD
   - VAPID_PUBLIC_KEY / VAPID_PRIVATE_KEY（来自 `npx web-push generate-vapid-keys --json`）

2) 前端 .env：确认并填写
   - VITE_API_BASE_URL=http://127.0.0.1:8000/api
   - VITE_VAPID_PUBLIC_KEY（与后端公钥一致）

3) 数据库初始化
   - 使用具备权限的账户运行 backend/test_db.py，自动创建 mtm_helper 数据库（若不存在）

4) 迁移与服务
   - python manage.py migrate
   - 启动后端服务（占用检测后）
   - npm run dev 启动前端，进行推送回归测试

## 需要用户提供/确认的信息
- 是否使用已有 MySQL 账户（用户名/密码）或允许创建新账户（示例：mtm_helper_dev / 自定义强密码）
- VAPID 公私钥是否已生成并可写入 .env

## 操作指引
1) 生成 VAPID 密钥（Node 环境已安装）：
   - 在项目根目录执行：
     - `npx web-push generate-vapid-keys --json`
   - 将输出中的 publicKey/privateKey 分别填入后端/前端 .env。

2) MySQL 创建账户与授权（如需新账户，示例 SQL）：
   - 使用 root 登录并执行：
     - `CREATE USER 'mtm_helper_dev'@'localhost' IDENTIFIED BY '你的强密码';`
     - `GRANT ALL PRIVILEGES ON mtm_helper.* TO 'mtm_helper_dev'@'localhost';`
     - `FLUSH PRIVILEGES;`
   - 若使用现有账户，请直接告知 DB_USER/DB_PASSWORD。