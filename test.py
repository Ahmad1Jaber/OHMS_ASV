import requests

# Define the API URL
url = 'http://api.birdbook.live/register'

# Define the request data
data = {
    'hotel_name': 'Hotel Mathew',
    'email': 'manager.mathew@example.com',
    'password': 'mypassword'
}

# Make the HTTP request
response = requests.post(url, json=data)

# Print the response
print(response.json())



url = 'http://api.birdbook.live/login'

# Define the request data
data = {
    'email': 'managerAhmad@example.com',
    'password': 'mypassword'
}

# Make the HTTP request
response = requests.post(url, json=data)

# Print the response
print(response.json())

"""""
url = 'http://api.birdbook.live/login'

# Define the request data
data = {
    'email': 'managerAhmad@example.com',
    'password': 'mypassword'
}

# Make the HTTP request
response = requests.post(url, json=data)

# Print the response
print(response.json())


url = 'http://api.birdbook.live/managers/3/rooms'
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print(data)
    # do something with the response data
else:
    print(f'Request failed with status code {response.status_code}')

"""