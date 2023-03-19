import requests

url = 'http://api.birdbook.live/reports/occupancy'
headers = {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2NzkyNTY3MzEsImlhdCI6MTY3OTI1MzEzMSwiaG90ZWxfaWQiOiIyMTFjMGUwZi02MjNjLTQ1ZTUtYWI4Zi0xZmFlM2YxM2QwZGIifQ.KH3Ws53EVzaMzqklHX-8I0HJx3G09f9ddQmJ-6tay6A'}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print(f'Error: {response.status_code} - {response.text}')
