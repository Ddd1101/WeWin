import requests

try:
    response = requests.get('API_BASE_URL/api/store/platforms/')
    print('Status Code:', response.status_code)
    print('Response:', response.text)
except Exception as e:
    print('Error:', e)
