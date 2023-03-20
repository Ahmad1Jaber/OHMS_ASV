import requests

url = 'http://api.birdbook.live/reports/occupancy'
headers = {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2NzkzNDczMTcsImlhdCI6MTY3OTM0MzcxNywiaG90ZWxfaWQiOiIyMTFjMGUwZi02MjNjLTQ1ZTUtYWI4Zi0xZmFlM2YxM2QwZGIifQ.btjTEQ7-KDnZiBjqAPc7ITdwww1DpK92LDPfaxCSci4'}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print(f'Error: {response.status_code} - {response.text}')
