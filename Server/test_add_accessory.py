import requests
import json

# API URL
url = 'http://127.0.0.1:8000/api/store/products/create/'

# 请求头
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImFkbWluIiwidXNlcl90eXBlIjoic3VwZXJfYWRtaW4iLCJleHAiOjE3NzUzOTA3Mzh9.FICV4kgsXQFlzqRRxbHrxiCdnUU6BcqqcjWeuVAeC9s'
}

# 请求数据
data = {
    "code": "ACC001",
    "name": "测试配件",
    "product_type": "ACCESSORY",
    "cost_price": 10.0,
    "selling_price": 20.0,
    "location": "仓库A",
    "supplier": "供应商A",
    "company_id": 1,
    "material": "金属",
    "size": "M",
    "color": "银色"
}

# 发送请求
try:
    response = requests.post(url, headers=headers, data=json.dumps(data))
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
