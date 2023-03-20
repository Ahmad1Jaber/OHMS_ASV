from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS,cross_origin
from configparser import ConfigParser
import jwt
import redis
import json
import datetime
import uuid

app = Flask(__name__)
CORS(app)

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

cnx = mysql.connector.connect(user=username,
                              password=password,
                              host=hostname,
                              database=database)

def extract_user_info(token):
    try:
        token_parts = token.split(" ")
        if len(token_parts) != 2:
            return None

        actual_token = token_parts[1]
        decoded = jwt.decode(actual_token, jwt_secret, algorithms=['HS256'])
        return decoded['user_id']
    except jwt.exceptions.InvalidTokenError:
        return None

@app.route('/reserve', methods=['POST'])
def make_reservation():
    token = request.headers.get('Authorization')
    user_id = extract_user_info(token)

    if not user_id:
        return jsonify({'error': 'Invalid token or missing user_id'}), 401

    data = request.json
    hotel_id = data.get('hotel_id')
    room_id = data.get('room_id')
    check_in_date = data.get('check_in_date')
    check_out_date = data.get('check_out_date')

    if not all([hotel_id, room_id, check_in_date, check_out_date]):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        check_in_date = datetime.datetime.strptime(check_in_date, '%Y-%m-%d').date()
        check_out_date = datetime.datetime.strptime(check_out_date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

    reservation_id = str(uuid.uuid4())
    cursor = cnx.cursor()
    query = '''
        INSERT INTO reservations (reservation_id, hotel_id, room_id, user_id, checkin_date, checkout_date)
        VALUES (%s, %s, %s, %s, %s, %s)
    '''
    values = (reservation_id, hotel_id, room_id, user_id, check_in_date, check_out_date)
    cursor.execute(query, values)
    cnx.commit()
    
    return jsonify({'message': 'Reservation successfully created', 'reservation_id': reservation_id}), 201

@app.route('/reservations', methods=['GET'])
def view_reservations():
    token = request.headers.get('Authorization')
    user_id = extract_user_info(token)

    if not user_id:
        return jsonify({'error': 'Invalid token or missing user_id'}), 401

    hotel_id = request.args.get('hotel_id')  # Get the hotel_id from query string

    if not hotel_id:
        return jsonify({'error': 'Missing hotel_id'}), 400

    cursor = cnx.cursor()
    query = '''
        SELECT r.reservation_id, r.room_id, hr.room_type, r.checkin_date, r.checkout_date, r.status
        FROM reservations r
        JOIN hotel_rooms hr ON r.room_id = hr.room_id
        WHERE r.hotel_id = %s AND r.user_id = %s
    '''
    values = (hotel_id, user_id)
    cursor.execute(query, values)
    rows = cursor.fetchall()
    reservations = []
    for row in rows:
        reservations.append({
            'reservation_id': row[0],
            'room_id': row[1],
            'room_type': row[2],
            'check_in_date': row[3].strftime('%Y-%m-%d'),
            'check_out_date': row[4].strftime('%Y-%m-%d'),
            'status': row[5]
        })

    return jsonify({'reservations': reservations}), 200

@app.route('/healthz')
@cross_origin()
def health_check():
    return 'OK', 200

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)