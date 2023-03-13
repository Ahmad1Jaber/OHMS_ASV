import unittest
import requests

class TestAddRoom(unittest.TestCase):
    
    def test_add_room(self):
        # Set up test data
        hotel_id = '211c0e0f-623c-45e5-ab8f-1fae3f13d0db'
        room_data = {
            'hotel_id': '211c0e0f-623c-45e5-ab8f-1fae3f13d0db',
            'room_id': '21123',
            'room_type': 'single',
            'price': 100,
            'max_occupancy': 1,
            'num_rooms': 10
        }

        # Send POST request to API endpoint
        response = requests.post(f'http://localhost:5000/hotel/{hotel_id}/rooms', json=room_data)
        # Check that response is successful (status code 201)
        self.assertEqual(response.status_code, 201)
        # Check that response data matches input data
        self.assertEqual(response.json()['data'], room_data)

if __name__ == '__main__':
    unittest.main()
