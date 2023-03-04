import requests
import json

# Define the URL of the API endpoint
url = 'http://localhost:5000/managers/100/rooms'

# Make a GET request to retrieve the rooms
response = requests.get(url)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the JSON response
    rooms = json.loads(response.content)['rooms']
    # Print the list of rooms
    print(rooms)
else:
    print(f"Request failed with status code {response.status_code}")
