import requests
import json

def test_medicine_api():
    # 测试药品创建API
    base_url = "http://127.0.0.1:8000"
    
    # 首先尝试登录获取token
    login_data = {
        "username": "admin",  # 使用你的用户名
        "password": "Ghp880218"  # 使用你的密码
    }
    
    try:
        print("🔵 尝试登录...")
        login_response = requests.post(f"{base_url}/api/auth/login/", json=login_data)
        print(f"🔵 登录响应状态: {login_response.status_code}")
        print(f"🔵 登录响应内容: {login_response.text}")
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            access_token = login_result.get('data', {}).get('tokens', {}).get('access')
            
            if access_token:
                print(f"🟢 登录成功，获取到token: {access_token[:20]}...")
                
                # 准备药品数据（不包含image_url）
                medicine_data = {
                    "name": "测试药品",
                    "specification": "100mg*30片",
                    "manufacturer": "测试制药公司",
                    "medicine_type": "tablet",
                    "quantity": 50,
                    "is_prescription": False,
                    "description": "这是一个测试药品"
                }
                
                print(f"🔵 发送药品数据: {json.dumps(medicine_data, ensure_ascii=False, indent=2)}")
                print(f"🔵 数据包含字段: {list(medicine_data.keys())}")
                print(f"🔵 数据包含image_url: {'image_url' in medicine_data}")
                
                # 发送创建药品请求
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
                
                create_response = requests.post(
                    f"{base_url}/api/medicines/", 
                    json=medicine_data,
                    headers=headers
                )
                
                print(f"🔵 创建药品响应状态: {create_response.status_code}")
                print(f"🔵 创建药品响应内容: {create_response.text}")
                
                if create_response.status_code == 200 or create_response.status_code == 201:
                    print("🟢 药品创建成功！")
                else:
                    print("🔴 药品创建失败")
                    if create_response.status_code == 400:
                        error_data = create_response.json()
                        print(f"🔴 详细错误信息: {json.dumps(error_data, ensure_ascii=False, indent=2)}")
            else:
                print("🔴 无法获取访问token")
        else:
            print("🔴 登录失败")
            
    except requests.exceptions.ConnectionError:
        print("🔴 无法连接到服务器，请确保Django服务正在运行")
    except Exception as e:
        print(f"🔴 测试过程中出现错误: {e}")

if __name__ == "__main__":
    test_medicine_api()