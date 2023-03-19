from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS
from flask_cors import cross_origin
from configparser import ConfigParser
import jwt
import uuid
import redis
import json
import decimal
import logging
from fuzzywuzzy import fuzz, process

app = Flask(__name__)
# enable CORS
CORS(app)
# Read the credentials from the config file
config = ConfigParser()
config.read('config.ini')

username = config.get('mysql', 'user')
password = config.get('mysql', 'password')
hostname = config.get('mysql', 'host')
database = config.get('mysql', 'database')
jwt_secret = config.get('jwt', 'secret_key')
redis_host = config.get('redis', 'redishost')
redis_port = config.get('redis', 'redisport')
redis_client = redis.Redis(host=redis_host, port=redis_port)

# Connect to the database
cnx = mysql.connector.connect(user=username,
                              password=password,
                              host=hostname,
                              database=database)

#Configure Logging
logging.basicConfig(level=logging.DEBUG)
# Get the list of all countries from the database
def get_country_names():
    cursor = cnx.cursor()
    cursor.execute("SELECT name FROM countries")
    rows = cursor.fetchall()
    return [row[0] for row in rows]

country_names = get_country_names()

def extract_user_id(token):
    try:
        token_parts = token.split(" ")
        if len(token_parts) != 2:
            return None
        
        actual_token = token_parts[1]
        decoded = jwt.decode(actual_token, jwt_secret, algorithms=['HS256'])
        return decoded['user_id']
    except jwt.exceptions.InvalidTokenError:
        return None

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)

@app.route('/search/hotels', methods=['GET'])
@cross_origin()
def search_hotels():
    location = request.args.get('location')

    if not location:
        return jsonify({'error': 'Please provide a location to search for hotels.'}), 400

    # Use fuzzywuzzy to find the closest match for the user's input
    closest_country = process.extractOne(location, country_names)

    if closest_country and closest_country[1] >= 75:  # Set a threshold for the match score (e.g., 75)
        location = closest_country[0]
    else:
        return jsonify({'error': 'Invalid location. Please provide a valid country name.'}), 400

    if not location:
        return jsonify({'error': 'Please provide a location to search for hotels.'}), 400

    # Check if the search result is already in Redis cache
    search_data = redis_client.get(f'search_{location}')
    if search_data:
        # Convert the cached data from bytes to a list of dictionaries
        hotels = json.loads(search_data.decode('utf-8'))
    else:
        # Get hotels based on the location from the database
        query = '''
            SELECT hotel_manager.hotel_id, hotel_name, manager_name, email_address, address_location, website
            FROM hotel_manager
            JOIN countries ON hotel_manager.country_id = countries.id
            WHERE countries.name = %s OR address_location LIKE %s
        '''
        values = (location, f'%{location}%')
        cursor = cnx.cursor()
        cursor.execute(query, values)
        rows = cursor.fetchall()

        # Convert the rows to a list of dictionaries
        hotels = []
        for row in rows:
            hotels.append({
                'hotel_id': row[0],
                'hotel_name': row[1],
                'address_location': row[4],
                'website': row[5]
            })

        # Cache the search result in Redis
        redis_client.set(f'search_{location}', json.dumps(hotels, cls=DecimalEncoder))

    return jsonify({'hotels': hotels})

@app.route('/search/rooms', methods=['GET'])
@cross_origin()
def get_hotel_rooms():
    hotel_id = request.args.get('hotel_id')

    if not hotel_id:
        return jsonify({'error': 'Please provide a hotel_id to get the rooms.'}), 400

    # Check if the room data is already in Redis cache
    room_data = redis_client.get(f'rooms_{hotel_id}')
    if room_data:
        # Convert the cached data from bytes to a list of dictionaries
        rooms = json.loads(room_data.decode('utf-8'))
    else:
        # Get rooms based on the hotel_id from the database
        query = '''
            SELECT room_id, room_type, price, max_occupancy, num_rooms
            FROM hotel_rooms
            WHERE hotel_id = %s
        '''
        cursor = cnx.cursor()
        cursor.execute(query, (hotel_id,))
        rows = cursor.fetchall()

        # Convert the rows to a list of dictionaries
        rooms = []
        for row in rows:
            rooms.append({
                'room_id': row[0],
                'room_type': row[1],
                'price': float(row[2]),
                'max_occupancy': row[3],
                'num_rooms': row[4]
            })

        # Cache the room data in Redis
        redis_client.set(f'rooms_{hotel_id}', json.dumps(rooms, cls=DecimalEncoder))

    return jsonify({'rooms': rooms})

@app.route('/healthz')
@cross_origin()
def health_check():
    return 'OK', 200

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)