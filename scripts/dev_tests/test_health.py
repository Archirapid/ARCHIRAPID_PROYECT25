import urllib.request
import json
try:
    with urllib.request.urlopen('http://127.0.0.1:5000/health') as response:
        data = json.loads(response.read().decode())
        print('Status:', response.status)
        print('Response:', data)
except Exception as e:
    print('Error:', e)