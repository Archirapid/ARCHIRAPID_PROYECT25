import requests
response = requests.post('http://127.0.0.1:5000/api/generar-plano-ascii', json={'area_m2': 150, 'tipologia': 'casa', 'use_ai': False})
print('Status:', response.status_code)
if response.status_code == 200:
    data = response.json()
    print('Success:', data['success'])
    print('Plano:')
    print(data['plano'])
else:
    print('Error:', response.text)