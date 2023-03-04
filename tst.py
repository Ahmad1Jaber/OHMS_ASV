import unittest
import json
from app import app

class TestApp(unittest.TestCase):

    # Setup test client
    def setUp(self):
        app.testing = True
        self.client = app.test_client()

    # Test create_manager endpoint
    def test_create_manager(self):
        data = {
            "hotel_name": "Example Hotel",
            "email": "example@example.com",
            "password": "password123"
        }
        response = self.client.post('/register', json=data)
        self.assertEqual(response.status_code, 200)

    # Test login endpoint
    def test_login(self):
        data = {
            "email": "example@example.com",
            "password": "password123"
        }
        response = self.client.post('/login', json=data)
        self.assertEqual(response.status_code, 200)

    # Test create_room and get_rooms endpoints
    def test_create_and_get_rooms(self):
        # Create a manager
        manager_data = {
            "hotel_name": "Example Hotel",
            "email": "example@example.com",
            "password": "password123"
        }
        manager_response = self.client.post('/register', json=manager_data)
        manager_id = json.loads(manager_response.data)['user_id']

        # Create a room
        room_data = {
            "room_type": "single",
            "price": 100,
            "capacity": 1
        }
        create_room_response = self.client.post(f'/managers/{manager_id}/rooms', json=room_data)
        self.assertEqual(create_room_response.status_code, 200)

        # Get all rooms for the manager
        get_rooms_response = self.client.get(f'/managers/{manager_id}/rooms')
        self.assertEqual(get_rooms_response.status_code, 200)
        self.assertEqual(len(json.loads(get_rooms_response.data)['rooms']), 1)

if __name__ == '__main__':
    unittest.main()
