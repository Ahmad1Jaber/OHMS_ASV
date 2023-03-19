import requests
import json

url = 'http://api.birdbook.live/reservations/past'
headers = {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2NzkxNzY2NDQsImlhdCI6MTY3OTE3MzA0NCwiaG90ZWxfaWQiOiIyMTFjMGUwZi02MjNjLTQ1ZTUtYWI4Zi0xZmFlM2YxM2QwZGIifQ._YdOqXuY1y6GVRwIgmA1N38SX0xaQFaN1Ooy8--25Ac'}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = json.loads(response.text)
    reservations = data['reservations']
    for reservation in reservations:
        print(reservation)
else:
    print(f'Error: {response.status_code} - {response.text}')
