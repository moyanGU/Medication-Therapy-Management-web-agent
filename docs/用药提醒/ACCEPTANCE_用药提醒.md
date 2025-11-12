# 用药提醒 - 回归测试验收记录

时间: 当前执行会话
负责人: AI助理（与用户协作）

## 验收目标
- 浏览器通知权限与本地通知链路可用
- PWA Push 订阅可生成，后端保存接口返回成功
- 后端能够触发 Web Push 并成功送达浏览器（日志与前端提示均确认）

## 环境与依赖
- 操作系统: Windows
- 前端开发端口: 5173（空闲）
- 后端开发端口: 8000（空闲）
- 数据库: MySQL80 服务已运行
- 关键环境变量: backend/.env 中 DB_USER/DB_PASSWORD、VAPID_PUBLIC_KEY/PRIVATE_KEY；frontend/.env 中 VITE_API_BASE_URL、VITE_VAPID_PUBLIC_KEY

## 执行步骤与结果
1) 数据库连接与初始化
   - 执行 backend/test_db.py 第1次：失败，用户 devuser 无权限或密码错误。
   - 待用户确认/创建具备权限的 DB_USER/DB_PASSWORD 后重试。

2) Django 迁移
   - 待数据库连接成功后执行 `python manage.py migrate`。

3) 后端服务启动
   - 端口检测：8000 未占用。
   - 待迁移完成后启动并观察日志。

4) 前端服务启动与回归测试
   - 端口检测：5173 未占用。
   - 待 VITE_API_BASE_URL/VITE_VAPID_PUBLIC_KEY 写入真实值后，启动 `npm run dev` 并进行以下测试：
     - 请求通知权限：预期成功
     - 启用推送订阅：预期成功，后端保存返回 {success:true}
     - 手动触发推送：预期浏览器收到通知

## 当前结论
- 数据库凭据与 VAPID 密钥需要最终确认与写入，尚未完成端到端回归。

## 后续动作
- 用户确认 DB_USER/DB_PASSWORD 与 VAPID_PUBLIC_KEY/PRIVATE_KEY。
- 更新前后端 .env 并重试 test_db、migrate、服务启动与回归测试。