import requests

url = "http://localhost:5000/login"
data = {
    "email": "manager@post.com",
    "password": "ahmadjaber"
}
response = requests.post(url, json=data)
print(response.text)