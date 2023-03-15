from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS
from flask_cors import cross_origin
from configparser import ConfigParser
import jwt
import uuid

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

# Connect to the database
cnx = mysql.connector.connect(user=username,
                              password=password,
                              host=hostname,
                              database=database)


def extract_hotel_id(token):
    try:
        token_parts = token.split(" ")
        if len(token_parts) != 2:
            return None
        
        actual_token = token_parts[1]
        decoded = jwt.decode(actual_token, jwt_secret, algorithms=['HS256'])
        return decoded['hotel_id']
    except jwt.exceptions.InvalidTokenError:
        return None



@app.route('/manage/rooms/create', methods=['POST'])
@cross_origin()
def add_room():
    # Get request body
    data = request.get_json()

    # Extract hotel ID from JWT token
    token = request.headers.get('Authorization')
    hotel_id = extract_hotel_id(token)

    # Check if hotel ID is valid
    if hotel_id is None:
        return jsonify({'error': 'Invalid token.'}), 401

    # Check if all required fields are provided
    if not all(field in data for field in ['room_type', 'price', 'max_occupancy', 'num_rooms']):
        return jsonify({'error': 'Please provide all required fields.'}), 400

    # Generate a UUID for the hotel room id
    room_id = str(uuid.uuid4())

    # Add hotel_id and room_id to data
    data['hotel_id'] = hotel_id
    data['room_id'] = room_id

    # Insert new room into hotel_rooms table
    query = "INSERT INTO hotel_rooms (room_id, hotel_id, room_type, price, max_occupancy, num_rooms) VALUES (%s, %s, %s, %s, %s, %s)"
    values = (data['room_id'], data['hotel_id'], data['room_type'], data['price'], data['max_occupancy'], data['num_rooms'])
    cursor = cnx.cursor()
    cursor.execute(query, values)
    cnx.commit()

    return jsonify({'message': 'Room added successfully.', 'data': data}), 201


@app.route('/manage/rooms/read', methods=['GET'])
@cross_origin()
def get_rooms():
    # Extract hotel ID from JWT token
    token = request.headers.get('Authorization')
    hotel_id = extract_hotel_id(token)

    # Check if hotel ID is valid
    if hotel_id is None:
        return jsonify({'error': 'Invalid token.'}), 401

    # Get rooms for the specified hotel
    query = "SELECT room_id, room_type, price, max_occupancy, num_rooms FROM hotel_rooms WHERE hotel_id = %s"
    values = (hotel_id,)
    cursor = cnx.cursor()
    cursor.execute(query, values)
    rows = cursor.fetchall()

    # Convert the rows to a list of dictionaries
    rooms = []
    for row in rows:
        rooms.append({
            'room_id': row[0],
            'room_type': row[1],
            'price': row[2],
            'max_occupancy': row[3],
            'num_rooms': row[4]
        })

    return jsonify({'rooms': rooms})


@app.route('/manage/rooms/update/<string:room_id>', methods=['PUT'])
@cross_origin()
def update_room(room_id):
    # Get request body
    data = request.get_json()

    # Extract hotel ID from JWT token
    token = request.headers.get('Authorization')
    hotel_id = extract_hotel_id(token)

    # Check if hotel ID is valid
    if hotel_id is None:
        return jsonify({'error': 'Invalid token.'}), 401

    # Update room data in hotel_rooms table
    query = "UPDATE hotel_rooms SET room_type = %s, price = %s, max_occupancy = %s, num_rooms = %s WHERE room_id = %s AND hotel_id = %s"
    values = (data['room_type'], data['price'], data['max_occupancy'], data['num_rooms'], room_id, hotel_id)
    cursor = cnx.cursor()
    cursor.execute(query, values)
    cnx.commit()

    return jsonify({'message': 'Room updated successfully.', 'data': data}), 200


@app.route('/manage/rooms/delete/<string:room_id>', methods=['DELETE'])
@cross_origin()
def delete_room(room_id):
    # Extract hotel ID from JWT token
    token = request.headers.get('Authorization')
    hotel_id = extract_hotel_id(token)

    # Check if hotel ID is valid
    if hotel_id is None:
        return jsonify({'error': 'Invalid token.'}), 401

    cursor = cnx.cursor()
    query = "DELETE FROM hotel_rooms WHERE room_id = %s AND hotel_id = %s"
    values = (room_id, hotel_id)
    cursor.execute(query, values)
    cnx.commit()

    if cursor.rowcount > 0:
        return jsonify({'message': 'Room deleted successfully.'}), 200
    else:
        return jsonify({'error': 'Room not found.'}), 404



@app.route('/manage/hotel', methods=['PUT'])
@cross_origin()
def update_hotel():
    # Get request body
    data = request.get_json()

    # Extract hotel ID from
    token
    token = request.headers.get('Authorization')
    hotel_id = extract_hotel_id(token)
    # Check if hotel ID is valid
    if hotel_id is None:
        return jsonify({'error': 'Invalid token.'}), 401

    # Update hotel data in hotel_manager table
    query = "UPDATE hotel_manager SET manager_name = %s, email_address = %s, password = %s, hotel_name = %s, address_location = %s, website = %s, country_id = %s WHERE hotel_id = %s"
    values = (data['manager_name'], data['email_address'], data['password'], data['hotel_name'], data['address_location'], data['website'], data['country_id'], hotel_id)
    cursor = cnx.cursor()
    cursor.execute(query, values)
    cnx.commit()

    return jsonify({'message': 'Hotel updated successfully.', 'data': data}), 200


@app.route('/healthz')
@cross_origin()
def health_check():
    return 'OK', 200

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)