#!/usr/bin/env python
"""
API测试脚本
"""
import requests
import json

def test_api_endpoints():
    """测试API端点"""
    base_url = "http://127.0.0.1:8000"
    
    print("=== API端点测试 ===")
    
    # 测试的端点列表
    endpoints = [
        "/api/",
        "/api/auth/",
        "/api/medicines/",
        "/api/records/",
        "/api/reminders/",
        "/api/medical-records/"
    ]
    
    for endpoint in endpoints:
        try:
            url = base_url + endpoint
            print(f"测试: {url}")
            
            response = requests.get(url, timeout=5)
            print(f"  状态码: {response.status_code}")
            print(f"  响应时间: {response.elapsed.total_seconds():.3f}秒")
            
            if response.status_code == 200:
                print("  ✅ 响应正常")
            elif response.status_code == 401:
                print("  🔐 需要认证（正常）")
            elif response.status_code == 404:
                print("  ❌ 端点不存在")
            else:
                print(f"  ⚠️  状态码: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"  ❌ 连接失败 - 服务器可能未启动")
        except requests.exceptions.Timeout:
            print(f"  ⏰ 请求超时")
        except Exception as e:
            print(f"  ❌ 错误: {e}")
        
        print()

def main():
    """主函数"""
    print("API连接测试工具")
    print("=" * 50)
    test_api_endpoints()

if __name__ == '__main__':
    main()