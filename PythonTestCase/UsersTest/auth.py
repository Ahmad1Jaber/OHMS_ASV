import requests
import json

url = 'http://api-users.birdbook.live/users/register'
data = {
    'username': 'john_doe',
    'email_address': 'john.doe@example.com',
    'password': 'password123',
    'first_name': 'John',
    'last_name': 'Doe'
}
headers = {
    'Content-Type': 'application/json'
}
response = requests.post(url, data=json.dumps(data), headers=headers)

print(response.status_code) 
print(response.json())       



#######################################################

url = 'http://api-users.birdbook.live/users/login'
data = {
    'email_address': 'john.doe@example.com',
    'password': 'password123'
}
headers = {
    'Content-Type': 'application/json'
}
response = requests.post(url, data=json.dumps(data), headers=headers)

print(response.status_code)  
print(response.json())       