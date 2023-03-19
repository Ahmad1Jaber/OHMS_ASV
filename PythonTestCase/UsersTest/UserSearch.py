import requests
import json
url = 'http://api-users.birdbook.live/search/hotels?location=joran'

headers = {
    'Content-Type': 'application/json'
}
response = requests.get(url,headers=headers)

print(response.status_code)  
print(response.json())      