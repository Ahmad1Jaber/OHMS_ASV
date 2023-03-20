import requests

url = "http://api.birdbook.live/manage/rooms/create"
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2NzkzNTc1MjcsImlhdCI6MTY3OTM1MzkyNywiaG90ZWxfaWQiOiIyMTFjMGUwZi02MjNjLTQ1ZTUtYWI4Zi0xZmFlM2YxM2QwZGIifQ.DZO0lSwdDfrxEmnl1dermsYJG8dhBcvVhxm8VlZ2vyg",  
    "Content-Type": "application/json"
}
data = {
    "room_type": "Villa",
    "price": 300.0,
    "max_occupancy": 4,
    "num_rooms": 5
}

response = requests.post(url, json=data, headers=headers)

if response.status_code == 201:
    print("Room added successfully.")
    print(response.json())
else:
    print(f"Error: {response.status_code}")
    print(response.json())
