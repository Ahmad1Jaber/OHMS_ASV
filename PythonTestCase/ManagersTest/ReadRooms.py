import requests
import json
import time

# Replace the <YOUR_HOSTNAME> and <YOUR_TOKEN> placeholders with your actual values
hostname = "api.birdbook.live"
token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2NzkzNTc1MjcsImlhdCI6MTY3OTM1MzkyNywiaG90ZWxfaWQiOiIyMTFjMGUwZi02MjNjLTQ1ZTUtYWI4Zi0xZmFlM2YxM2QwZGIifQ.DZO0lSwdDfrxEmnl1dermsYJG8dhBcvVhxm8VlZ2vyg"

headers = {'Authorization': token}

url = f"http://{hostname}/manage/rooms/read"

start_time = time.time()
response = requests.get(url, headers=headers)
end_time = time.time()

# Expecting a 200 response code
assert response.status_code == 200

# Expecting a JSON response with rooms data
response_json = response.json()
assert 'rooms' in response_json

# Print the rooms data
print(json.dumps(response_json['rooms'], indent=4))

# Calculate and print the latency
latency = end_time - start_time
print(f"Latency: {latency:.2f} seconds")
