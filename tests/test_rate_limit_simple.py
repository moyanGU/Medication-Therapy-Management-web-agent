import requests
import time
import sys

BASE_URL = "http://127.0.0.1:8000/api"
MEDICINES_URL = f"{BASE_URL}/medicines/"
# 假设我们有一个测试用户，或者我们可以尝试访问一个不需要认证的接口来测试 IP 限流
# 如果所有接口都需要认证，我们需要先登录
LOGIN_URL = f"{BASE_URL}/auth/login/"

def test_rate_limit():
    print("Starting Rate Limit Test...")
    
    # 1. 尝试触发 IP 限流 (或者未认证用户的限流)
    # 假设 API_RATE_LIMIT 是 100 次/分钟
    # 我们发送 110 次请求
    
    # 注意：如果 medicines 接口需要认证，这里会返回 401，但这不影响限流中间件的计数
    # 因为 RateLimitMiddleware 在 AuthenticationMiddleware 之前执行 (通常)
    # 让我们检查一下 settings.py 中的顺序
    # MIDDLEWARE = [..., SecurityHeadersMiddleware, RateLimitMiddleware, ..., AuthenticationMiddleware, ...]
    # 是的，RateLimitMiddleware 在 AuthenticationMiddleware 之前，所以即使 401 也会被限流
    
    success_count = 0
    blocked_count = 0
    
    start_time = time.time()
    
    for i in range(120):
        try:
            response = requests.get(MEDICINES_URL, timeout=2)
            if response.status_code == 429:
                print(f"Request {i+1}: Blocked (429) - {response.json().get('message')}")
                blocked_count += 1
                # 一旦触发限流，我们可以停止或者继续验证是否持续被限流
                if blocked_count > 5:
                    break
            else:
                # 401 or 200 are both considered "allowed" by rate limiter
                # print(f"Request {i+1}: Allowed ({response.status_code})")
                success_count += 1
        except Exception as e:
            print(f"Request {i+1}: Error - {e}")

    duration = time.time() - start_time
    print(f"\nTest Completed in {duration:.2f} seconds")
    print(f"Total Requests: {success_count + blocked_count}")
    print(f"Allowed: {success_count}")
    print(f"Blocked: {blocked_count}")
    
    if blocked_count > 0:
        print("\n✅ Rate Limit Verified: Limit triggered successfully.")
    else:
        print("\n❌ Rate Limit Failed: No requests were blocked.")
        # 可能原因：限流阈值太高，或者中间件未生效，或者 Redis 不可用

if __name__ == "__main__":
    try:
        test_rate_limit()
    except KeyboardInterrupt:
        print("\nTest interrupted.")
