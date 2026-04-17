# CONSENSUS P2-A1 短信防刷与多通道接入最小落地

## 1. 核心共识

- **多层防刷 (Anti-Spam)**：
  - **L1**: 60秒冷却限制 (Per Phone)。防并发点击穿透。
  - **L2**: 自然日单手机号上限 (默认 5次/天)。防薅羊毛。
  - **L3**: 自然日单 IP 上限 (默认 20次/天)。防群发机集中攻击。
  - **L4 (兜底)**: Session 回退，当 Redis 不可用时，基于当前请求会话维持基础限流，保证服务不雪崩，且不会被随意调用。

- **多通道网关 (SMS Gateway)**：
  - **抽象接口**：业务层 (`views.py`) 只负责调用 `send_sms(phone, template_id, context)`。
  - **服务商**：通过环境变量 `SMS_PROVIDER` 切换。支持 `mock`, `spug`, `aliyun`, `tencent`。
  - **异常隔离**：不管底层通道是什么，均需自行处理 `Timeout` 和 HTTP/SDK 异常，统一抛出给网关捕获，网关再统一以 `False/ErrorMsg` 形式返回给视图，绝不能造成 500。

## 2. API 接口共识

在 `apps/authentication/views.py` 中重构现有的 `send_verification_code`：
- 不改变输入/输出协议，前端完全无感。
- 修改点在于：
  - 在生成验证码前，按顺序检查并累加 `sms:daily:phone:{phone}` 和 `sms:daily:ip:{ip}`。
  - 若命中阈值，返回 `429 Too Many Requests`，提示文案诸如“今日发送次数已达上限”、“该设备今日发送次数过多”。

## 3. 后端代码组织共识

- **模块位置**：`apps/core/sms/` (或者 `apps/core/utils.py` 里，为保证整洁建议独立建包/模块)
  - `__init__.py`: 对外暴露 `send_sms`。
  - `gateway.py`: 工厂类，根据配置实例化 Provider。
  - `providers/`: 存放 `base.py`, `mock.py`, `spug.py`, `aliyun.py`, `tencent.py`。

- **凭据管理**：环境变量加载。未提供时如果指定了对应的 Provider，应在实例化阶段报错，自动降级为 Mock 并报警。