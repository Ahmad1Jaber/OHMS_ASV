from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS
from flask_cors import cross_origin
from configparser import ConfigParser

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

# Connect to the database
cnx = mysql.connector.connect(user=username,
                              password=password,
                              host=hostname,
                              database=database)

@app.route('/occupancy/available_rooms/<string:hotel_id>', methods=['GET'])
@cross_origin()
def available_rooms_report(hotel_id):
    # Query the database to get the room types and the number of available rooms for each
    query = "SELECT room_type, SUM(num_rooms) - COALESCE(SUM(CASE WHEN checkin_date <= CURDATE() AND checkout_date >= CURDATE() THEN 1 ELSE 0 END), 0) AS available_rooms FROM hotel_rooms LEFT JOIN reservations ON hotel_rooms.room_id = reservations.room_id AND reservations.checkout_date >= CURDATE() AND reservations.checkin_date <= CURDATE() WHERE hotel_rooms.hotel_id = %s GROUP BY room_type"
    cursor = cnx.cursor()
    cursor.execute(query, (hotel_id,))
    results = cursor.fetchall()

    # Convert the results to a list of dictionaries and return as JSON
    report = [{'room_type': row[0], 'available_rooms': row[1]} for row in results]
    return jsonify(report), 200

@app.route('/occupancy/profits/<string:hotel_id>', methods=['GET'])
@cross_origin()
def profits_report(hotel_id):
    # Query the database to get the room types and the profits for each
    query = """
        SELECT room_type, 
               SUM(num_rooms) AS total_rooms, 
               SUM(num_rooms * price) AS total_revenue,
               SUM(num_rooms * price) - COALESCE(SUM(CASE WHEN checkin_date <= CURDATE() AND checkout_date >= CURDATE() THEN num_rooms * price ELSE 0 END), 0) AS total_profits
        FROM hotel_rooms 
        LEFT JOIN reservations ON hotel_rooms.room_id = reservations.room_id AND reservations.checkout_date >= CURDATE() AND reservations.checkin_date <= CURDATE() 
        WHERE hotel_rooms.hotel_id = %s 
        GROUP BY room_type
    """
    cursor = cnx.cursor()
    cursor.execute(query, (hotel_id,))
    results = cursor.fetchall()

    # Convert the results to a list of dictionaries and return as JSON
    report = [
        {
            'room_type': row[0], 
            'total_rooms': row[1], 
            'total_revenue': float(row[2]), 
            'total_profits': float(row[3])
        } 
        for row in results
    ]
    return jsonify(report), 200

@app.route('/healthz')
@cross_origin()
def health_check():
    return 'OK', 200

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)