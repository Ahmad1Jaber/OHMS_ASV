import requests
import json

# Replace the <YOUR_HOSTNAME> and <YOUR_TOKEN> placeholders with your actual values
hostname = "api.birdbook.live"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2Nzg5MTAwMzgsImlhdCI6MTY3ODkwNjQzOCwiaG90ZWxfaWQiOiIyMTFjMGUwZi02MjNjLTQ1ZTUtYWI4Zi0xZmFlM2YxM2QwZGIifQ.t7nEKc0oAvQMg0pfgn7oGE52Kt4KRojiWtu50QFCDCI"

headers = {'Authorization': token}

url = f"http://{hostname}/manage/rooms/read"

response = requests.get(url, headers=headers)

# Expecting a 200 response code
assert response.status_code == 200

# Expecting a JSON response with rooms data
response_json = response.json()
assert 'rooms' in response_json

# Print the rooms data
print(json.dumps(response_json['rooms'], indent=4))