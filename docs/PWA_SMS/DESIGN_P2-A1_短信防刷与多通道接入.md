# DESIGN P2-A1 短信防刷与多通道接入最小落地

## 1. 架构目标

在 `backend` 中，提供一个健壮的、可扩展的短信发送服务网关。并以此为抓手，巩固“验证码”场景的安全水位（防刷）。

## 2. 详细设计

### 2.1 目录结构

```text
backend/apps/core/
  sms/
    __init__.py         # 对外暴露 get_sms_provider(), send_sms()
    base.py             # 定义 BaseSMSProvider 接口
    mock.py             # 继承 BaseSMSProvider，仅打印日志
    spug.py             # 继承 BaseSMSProvider，实现 Spug 逻辑
    aliyun.py           # 继承 BaseSMSProvider，实现阿里云短信 SDK 逻辑
    tencent.py          # 继承 BaseSMSProvider，实现腾讯云短信 SDK 逻辑
```

### 2.2 防刷逻辑 (Anti-Spam)

在 `apps.authentication.views.send_verification_code` 中增强限流检查：

```python
# settings.py
SMS_RATE_LIMIT_SECONDS = 60
SMS_DAILY_PHONE_LIMIT = 5
SMS_DAILY_IP_LIMIT = 20

# views.py 限流流程：
# 1. 提取 Client IP
ip = _get_client_ip(request)

# 2. Redis Key
key_rate = f"sms:rate:{phone}"
key_daily_phone = f"sms:daily:phone:{phone}:{today_str}"
key_daily_ip = f"sms:daily:ip:{ip}:{today_str}"

# 3. 依次校验并原子累加 (INCR / EXPIRE 86400)
# 如果 > Limit，返回 429
# 需考虑 Redis 宕机时的 Session 兜底：
# request.session[f"sms:daily:phone:{phone}"] = count + 1
```

### 2.3 `BaseSMSProvider` 设计

```python
class BaseSMSProvider(ABC):
    @abstractmethod
    def send(self, phone: str, template_code: str, template_params: dict) -> Tuple[bool, str]:
        """
        发送短信
        :return: (是否成功, 错误信息/回执ID)
        """
        pass
```

### 2.4 Aliyun / Tencent 占位实现

- **阿里云短信**：由于缺少实际的 AK/SK 凭证，本轮通过 `aliyun-python-sdk-core` 或 `alibabacloud_dysmsapi20170525` SDK 框架搭建，核心代码写好，但在 `__init__` 中校验到缺少 AK 时抛出异常被工厂捕获。
- **腾讯云短信**：同理，使用 `tencentcloud-sdk-python`，做好基础调用包装。

## 3. 前端设计

本轮为纯后端架构升级，前端无需改动，维持现有 `/api/auth/send-code/` 调用即可。前端已具备针对 429 响应的全局错误拦截和倒计时逻辑。