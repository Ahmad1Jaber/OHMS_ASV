import requests

url = "http://localhost:5000/register"
data = {
    "hotel_name": "Marriot",
    "email": "manager@marriot.com",
    "password": "ahmadjaber"
}
response = requests.post(url, json=data)
print(response.text)