# TASK P2-A1 短信防刷与多通道接入最小落地

## 任务列表

### 1. 架构梳理 (Backend Gateway)
- [ ] 在 `backend/apps/core/` 下新建 `sms` 模块，提取网关与 `BaseSMSProvider`。
- [ ] 迁移现有的 `Spug` 发送逻辑到 `SpugSMSProvider`，同时实现 `MockSMSProvider`。
- [ ] 新增 `AliyunSMSProvider` 和 `TencentSMSProvider` 的占位类（基于各自的官方 Python SDK）。

### 2. 配置与依赖 (Dependencies)
- [ ] 在 `requirements.txt` 中添加阿里云短信 SDK `alibabacloud_dysmsapi20170525` 和腾讯云短信 SDK `tencentcloud-sdk-python`。
- [ ] 在 `mtm_helper/settings.py` 中增加网关配置项：
  - `SMS_PROVIDER` = 'mock' / 'spug' / 'aliyun' / 'tencent'
  - `ALIYUN_ACCESS_KEY_ID`, `ALIYUN_ACCESS_KEY_SECRET`, `ALIYUN_SMS_SIGN_NAME`
  - `TENCENT_SECRET_ID`, `TENCENT_SECRET_KEY`, `TENCENT_SMS_APP_ID`, `TENCENT_SMS_SIGN_NAME`
  - `SMS_DAILY_PHONE_LIMIT` = 5
  - `SMS_DAILY_IP_LIMIT` = 20

### 3. 防刷逻辑 (Anti-Spam Logic)
- [ ] 重构 `apps/authentication/views.py` 的 `send_verification_code`。
- [ ] 实现 `ip` 提取。
- [ ] 实现针对 `sms:daily:phone:{phone}:{date}` 的防刷：
  - 检查超限 -> 429
  - 否则原子自增 `INCR`，若首次则设 TTL = 86400 (24h)
- [ ] 实现针对 `sms:daily:ip:{ip}:{date}` 的防刷：
  - 检查超限 -> 429
  - 否则原子自增 `INCR`，若首次则设 TTL = 86400 (24h)
- [ ] Redis 异常时 Session 兜底，分别记录到 `session['sms:daily:phone']` 等。

### 4. 单元测试与验证 (Verification)
- [ ] 在 `apps/authentication/tests/test_sms.py` (如无则新建) 编写防刷用例：
  - 测试超60秒发送成功。
  - 测试同手机号每日 5 次防刷。
  - 测试同 IP 每日 20 次防刷。
- [ ] 验证 Provider 的正常装载与失败回退。
- [ ] 执行 `manage.py test apps.authentication.tests.test_sms`。
- [ ] 填写 `ACCEPTANCE_P2-A1_短信防刷与多通道接入.md`。