from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS
from flask_cors import cross_origin
from configparser import ConfigParser
import jwt

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

@app.route('/hotel/<string:hotel_id>/rooms', methods=['POST'])
@cross_origin()
def add_room(hotel_id):
    # Get request body
    data = request.get_json()
    
    # Check if all required fields are provided
    if not all(field in data for field in ['room_id', 'room_type', 'price', 'max_occupancy', 'num_rooms']):
        return jsonify({'error': 'Please provide all required fields.'}), 400
    
    # Add hotel_id to data
    data['hotel_id'] = hotel_id
    
    # Insert new room into hotel_rooms table
    query = "INSERT INTO hotel_rooms (room_id, hotel_id, room_type, price, max_occupancy, num_rooms) VALUES (%s, %s, %s, %s, %s, %s)"
    values = (data['room_id'], data['hotel_id'], data['room_type'], data['price'], data['max_occupancy'], data['num_rooms'])
    cursor = cnx.cursor()
    cursor.execute(query, values)
    cnx.commit()
    
    return jsonify({'message': 'Room added successfully.', 'data': data}), 201


@app.route('/hotel/<string:hotel_id>/rooms/<string:room_id>', methods=['PUT'])
@cross_origin()
def update_room(hotel_id, room_id):
    # Get request body
    data = request.get_json()
    
    # Update room data in hotel_rooms table
    query = "UPDATE hotel_rooms SET room_type = %s, price = %s, max_occupancy = %s, num_rooms = %s WHERE room_id = %s AND hotel_id = %s"
    values = (data['room_type'], data['price'], data['max_occupancy'], data['num_rooms'], room_id, hotel_id)
    cursor = cnx.cursor()
    cursor.execute(query, values)
    cnx.commit()
    
    return jsonify({'message': 'Room updated successfully.', 'data': data}), 200


@app.route('/hotel/<string:hotel_id>', methods=['PUT'])
@cross_origin()
def update_hotel(hotel_id):
    # Get request body
    data = request.get_json()
    
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