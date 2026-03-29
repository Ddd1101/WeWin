import requests
import json

# 登录API URL
login_url = 'http://127.0.0.1:8000/api/account/login/'

# 登录数据
data = {
    "username": "admin",
    "password": "admin123"
}

# 发送登录请求
try:
    response = requests.post(login_url, headers={'Content-Type': 'application/json'}, data=json.dumps(data))
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # 如果登录成功，保存token
    if response.status_code == 200:
        token = response.json().get('token')
        print(f"Token: {token}")
        # 将token保存到文件
        with open('token.txt', 'w') as f:
            f.write(token)
        print("Token saved to token.txt")
except Exception as e:
    print(f"Error: {e}")
