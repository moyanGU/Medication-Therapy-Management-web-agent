# ALIGNMENT P2-A1 短信防刷与多通道接入最小落地

## 1. 原始需求
- 承接生产环境真实运营的需求，进入 `P2-A1`：短信通道的接口联调、防刷机制（Anti-Spam）以及多服务商（多渠道）的架构接入。

## 2. 当前项目上下文
### 2.1 已有基础
- `backend/apps/authentication/views.py` 中已经实现了 `send_verification_code`。
- 目前具备了 **60秒的发送间隔限流（原子防穿透）** 和 Redis 异常时的 Session 降级机制。
- 短信发送目前写死了集成 `Spug` 平台，如果未启用则进入 `mock`（日志打印）模式。

### 2.2 当前缺口
- **防刷机制薄弱**：只有60秒限制，没有“单手机号自然日发送上限（如5次/天）”和“单IP自然日发送上限（如20次/天）”的防刷机制，极易被黑产进行短信轰炸。
- **通道扩展性差**：发送逻辑硬编码在 View 中，没有抽象出 Provider 层，如果要接入真实的商业服务商（如阿里云、腾讯云）代码会变得非常臃肿。

## 3. 本轮任务边界

### 3.1 本轮要做
- **防刷增强 (Anti-Spam)**：
  - 新增基于 Redis（带 Session 降级）的自然日单手机号上限限制。
  - 新增基于 Redis（带 Session 降级）的自然日单 IP 上限限制。
- **短信网关重构 (Gateway/Provider Pattern)**：
  - 提取 `apps/core/sms.py` (或 `apps/authentication/sms.py`)，实现策略模式的短信发送器。
  - 抽象出基础的 `SMSProvider` 接口，并实现：
    - `MockSMSProvider` (开发用)
    - `SpugSMSProvider` (兼容现有 Spug)
    - `AliyunSMSProvider` (阿里云短信 - 占位或实现签名调用)
    - `TencentSMSProvider` (腾讯云短信 - 占位或实现签名调用)
- **业务集成**：
  - 重构 `send_verification_code`，使其通过网关发送，解耦业务逻辑与发送通道。

### 3.2 本轮不做
- 暂时不引入图形验证码 (Captcha / 极验 / 腾讯防水墙等)，仅靠后端频率与阈值限制做第一道防刷兜底。
- 不做异步任务队列发送（Celery），验证码属于高实时性要求，继续采用同步阻塞调用并设置合理的 Timeout。

## 4. 默认主路径判断
- 客户端请求 `/api/auth/send-code/`。
- 获取手机号和 Client IP。
- 校验60秒限流 -> 校验单日手机号上限 -> 校验单日 IP 上限。
- 若任一超限，返回 HTTP 429 并给出明确提示。
- 生成验证码，通过 `SmsGateway.send(phone, code)` 分发给配置文件指定的 Provider。
- 返回发送成功响应。
