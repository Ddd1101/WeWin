import requests

try:
    API_BASE_URL = "http://127.0.0.1:8000"
    response = requests.get(API_BASE_URL + "/api/store/platforms/")
    print('Status Code:', response.status_code)
    print('Response:', response.text)
except Exception as e:
    print('Error:', e)
