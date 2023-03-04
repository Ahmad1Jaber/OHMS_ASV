import requests

url = "http://34.154.225.231/login"

for i in range(10):
    data = {
        "email": f"manager{i}@hilton.com",
        "password": f"ahmadjaber{i}"
    }
    response = requests.post(url, json=data)
    print(f"Response {i+1}: {response.text}")
