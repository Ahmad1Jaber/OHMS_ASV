import json
import requests
# Define the URL of the API endpoint
url = 'http://api.birdbook.live/register'

# Define the data to be inserted as a dictionary
data = {
    'hotel_name': 'Marriot',
    'email': 'manager@marriot.com',
    'password': 'p@ssword'
}

# Convert the data to JSON format
json_data = json.dumps(data)

# Define the headers for the request
headers = {'Content-Type': 'application/json'}

# Send the HTTP POST request to the API
response = requests.post(url, headers=headers, data=json_data)

# Print the status code and any data returned by the API
print('Status Code:', response.status_code)
print('Response Data:', response.text)
