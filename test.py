"""
import requests

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


"""

import asyncio
import aiohttp

url = 'http://api.birdbook.live/login'

# Define the login data
data = {
    'email': 'managerAhmad@example.com',
    'password': 'mypassword'
}

# Specify the number of times to make the request
num_requests = 250

async def make_request(session):
    async with session.post(url, json=data) as response:
        result = await response.json()
        print(result)

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(num_requests):
            task = asyncio.create_task(make_request(session))
            tasks.append(task)
        await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())


"""""
# Define the API URL
url = 'http://127.0.0.1:5000/register'

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

"""""
url = 'http://api.birdbook.live/managers/3/rooms'
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print(data)
    # do something with the response data
else:
    print(f'Request failed with status code {response.status_code}')
"""