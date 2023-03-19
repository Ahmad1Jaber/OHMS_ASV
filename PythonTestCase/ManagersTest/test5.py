import requests

url = 'http://localhost:5000/reports/occupancy'
headers = {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2NzkxNzUwMDgsImlhdCI6MTY3OTE3MTQwOCwiaG90ZWxfaWQiOiIyMTFjMGUwZi02MjNjLTQ1ZTUtYWI4Zi0xZmFlM2YxM2QwZGIifQ.KmlFQzxbvlXe_4j1I903zbtBu9EooEl0ewcEdtnDi9g'}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print(f'Error: {response.status_code} - {response.text}')
