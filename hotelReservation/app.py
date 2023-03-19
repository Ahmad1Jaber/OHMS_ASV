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
from datetime import datetime, timedelta

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

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)

@app.route('/reservations/upcoming', methods=['GET'])
@cross_origin()
def get_upcoming_reservations():
    # Extract hotel ID from JWT token
    token = request.headers.get('Authorization')
    hotel_id = extract_hotel_id(token)

    # Check if hotel ID is valid
    if hotel_id is None:
        return jsonify({'error': 'Invalid token.'}), 401

    query = """SELECT r.reservation_id, r.room_id, r.user_id, r.checkin_date, r.checkout_date, r.status
               FROM reservations r
               WHERE r.hotel_id = %s AND r.checkin_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 2 DAY) AND r.status != 'canceled'
               ORDER BY r.checkin_date"""
    cursor = cnx.cursor()
    cursor.execute(query, (hotel_id,))
    rows = cursor.fetchall()

    reservations = []
    for row in rows:
        reservations.append({
            'reservation_id': row[0],
            'room_id': row[1],
            'user_id': row[2],
            'checkin_date': row[3].strftime('%Y-%m-%d'),
            'checkout_date': row[4].strftime('%Y-%m-%d'),
            'status': row[5]
        })

    return jsonify({'reservations': reservations})

@app.route('/reservations/past', methods=['GET'])
@cross_origin()
def get_past_reservations():
    # Extract hotel ID from JWT token
    token = request.headers.get('Authorization')
    hotel_id = extract_hotel_id(token)

    # Check if hotel ID is valid
    if hotel_id is None:
        return jsonify({'error': 'Invalid token.'}), 401

    query = """SELECT r.reservation_id, r.room_id, r.user_id, r.checkin_date, r.checkout_date, r.status
               FROM reservations r
               WHERE r.hotel_id = %s AND r.checkout_date < CURDATE()
               ORDER BY r.checkout_date DESC"""
    cursor = cnx.cursor()
    cursor.execute(query, (hotel_id,))
    rows = cursor.fetchall()

    reservations = []
    for row in rows:
        reservations.append({
            'reservation_id': row[0],
            'room_id': row[1],
            'user_id': row[2],
            'checkin_date': row[3].strftime('%Y-%m-%d'),
            'checkout_date': row[4].strftime('%Y-%m-%d'),
            'status': row[5]
        })

    return jsonify({'reservations': reservations})


@app.route('/reservations/all', methods=['GET'])
@cross_origin()
def get_all_reservations():
    # Extract hotel ID from JWT token
    token = request.headers.get('Authorization')
    hotel_id = extract_hotel_id(token)

    # Check if hotel ID is valid
    if hotel_id is None:
        return jsonify({'error': 'Invalid token.'}), 401

    query = """SELECT r.reservation_id, r.room_id, r.user_id, r.checkin_date, r.checkout_date, r.status
               FROM reservations r
               WHERE r.hotel_id = %s
               ORDER BY r.checkout_date DESC"""
    cursor = cnx.cursor()
    cursor.execute(query, (hotel_id,))
    rows = cursor.fetchall()

    reservations = []
    for row in rows:
        reservations.append({
            'reservation_id': row[0],
            'room_id': row[1],
            'user_id': row[2],
            'checkin_date': row[3].strftime('%Y-%m-%d'),
            'checkout_date': row[4].strftime('%Y-%m-%d'),
            'status': row[5]
        })

    return jsonify({'reservations': reservations})


@app.route('/reservations/cancel/<string:reservation_id>', methods=['PUT'])
@cross_origin()
def cancel_reservation(reservation_id):
    # Extract hotel ID from JWT token
    token = request.headers.get('Authorization')
    hotel_id = extract_hotel_id(token)

    # Check if hotel ID is valid
    if hotel_id is None:
        return jsonify({'error': 'Invalid token.'}), 401

    query = "UPDATE reservations SET status = 'canceled' WHERE reservation_id = %s AND hotel_id = %s AND status = 'booked'"
    cursor = cnx.cursor()
    cursor.execute(query, (reservation_id, hotel_id))
    cnx.commit()

    if cursor.rowcount > 0:
        return jsonify({'message': 'Reservation canceled successfully.'}), 200
    else:
        return jsonify({'error': 'Reservation not found or already canceled/checked in.'}), 404

@app.route('/reservations/checkin/<string:reservation_id>', methods=['PUT'])
@cross_origin()
def checkin_reservation(reservation_id):
    # Extract hotel ID from JWT token
    token = request.headers.get('Authorization')
    hotel_id = extract_hotel_id(token)

    # Check if hotel ID is valid
    if hotel_id is None:
        return jsonify({'error': 'Invalid token.'}), 401

    query = "UPDATE reservations SET status = 'checked_in' WHERE reservation_id = %s AND hotel_id = %s AND status = 'booked'"
    cursor = cnx.cursor()
    cursor.execute(query, (reservation_id, hotel_id))
    cnx.commit()

    if cursor.rowcount > 0:
        return jsonify({'message': 'Reservation checked in successfully.'}), 200
    else:
        return jsonify({'error': 'Reservation not found or already checked in/canceled.'}), 404

@app.route('/reservations/checkout/<string:reservation_id>', methods=['PUT'])
@cross_origin()
def checkout_reservation(reservation_id):
    # Extract hotel ID from JWT token
    token = request.headers.get('Authorization')
    hotel_id = extract_hotel_id(token)

    # Check if hotel ID is valid
    if hotel_id is None:
        return jsonify({'error': 'Invalid token.'}), 401

    query = "UPDATE reservations SET status = 'checked_out' WHERE reservation_id = %s AND hotel_id = %s AND status = 'checked_in'"
    cursor = cnx.cursor()
    cursor.execute(query, (reservation_id, hotel_id))
    cnx.commit()

    if cursor.rowcount > 0:
        return jsonify({'message': 'Reservation checked out successfully.'}), 200
    else:
        return jsonify({'error': 'Reservation not found or not checked in.'}), 404
    
@app.route('/healthz')
@cross_origin()
def health_check():
    return 'OK', 200

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)