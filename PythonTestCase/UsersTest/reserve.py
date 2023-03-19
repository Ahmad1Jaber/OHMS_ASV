import requests
import json

# Replace these variables with the appropriate values
api_base_url = 'http://localhost:5000'  # Replace with your Flask API app URL
jwt_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2NzkyMzM0MzQsImlhdCI6MTY3OTIyOTgzNCwidXNlcl9pZCI6IjU3Njk4MWQ3LTZlNWQtNDg5OS04ZjRhLWRhYzhhM2Y3NzcwYiJ9.bVoCLMOXrDCjCefJgD5oD2bh7hj194pWVhS2G8Zuy4M'  # Replace with the JWT token for the user
room_id = 'your_room_id'  # Replace with the room_id you want to reserve
check_in_date = '2023-04-01'
check_out_date = '2023-04-05'

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {jwt_token}'
}

# Reserve a room
reserve_payload = {
    'room_id': room_id,
    'check_in_date': check_in_date,
    'check_out_date': check_out_date
}
reserve_response = requests.post(f'{api_base_url}/reserve', headers=headers, data=json.dumps(reserve_payload))

if reserve_response.status_code == 201:
    print('Room reserved successfully!')
    reservation_id = reserve_response.json()['reservation_id']
    print(f'Reservation ID: {reservation_id}')
else:
    print('Error reserving room:', reserve_response.text)

# View reservations
view_reservations_response = requests.get(f'{api_base_url}/reservations', headers=headers)

if view_reservations_response.status_code == 200:
    reservations = view_reservations_response.json()['reservations']
    print('Reservations:')
    for reservation in reservations:
        print(f"Reservation ID: {reservation['reservation_id']}")
        print(f"Room ID: {reservation['room_id']}")
        print(f"Room Type: {reservation['room_type']}")
        print(f"Check-in Date: {reservation['check_in_date']}")
        print(f"Check-out Date: {reservation['check_out_date']}")
        print(f"Status: {reservation['status']}")
        print()
else:
    print('Error fetching reservations:', view_reservations_response.text)
