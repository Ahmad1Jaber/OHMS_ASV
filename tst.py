import requests

url = "http://localhost:5000/login"
data = {
    "email": "manager@hilton.com",
    "password": "ahmadjaber"
    
}
response = requests.post(url, json=data)
print(response.text)