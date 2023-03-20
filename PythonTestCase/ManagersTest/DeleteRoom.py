import requests

room_id = "46b034fb-0df8-4612-8ff9-43472f6a90c1" 

url = f"http://api.birdbook.live/manage/rooms/delete/{room_id}"
headers = {
    "Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2NzkxNTM5MTgsImlhdCI6MTY3OTE1MDMxOCwiaG90ZWxfaWQiOiIyMTFjMGUwZi02MjNjLTQ1ZTUtYWI4Zi0xZmFlM2YxM2QwZGIifQ.3D4g4YOzNU-bKxSAX_eKMh0iYv76wHMW9A6RYkZXZUk", 
}

response = requests.delete(url, headers=headers)

if response.status_code == 200:
    print("Room deleted successfully.")
else:
    print(f"Error: {response.status_code}")
    print(response.json())
