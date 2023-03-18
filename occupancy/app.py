from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS
from flask_cors import cross_origin
from configparser import ConfigParser
import jwt
import json
import uuid
from datetime import date
import redis

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


cnx = mysql.connector.connect(user=username,
                              password=password,
                              host=hostname,
                              database=database)

redis_client = redis.Redis(host=redis_host, port=redis_port)

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
    
def get_hotel_occupancy_report(hotel_id, today):
    query = '''
    SELECT hr.room_type,
           SUM(hr.num_rooms) AS total_rooms,
           COALESCE(SUM(r.reserved_rooms), 0) AS reserved_rooms,
           COALESCE(SUM(r.reserved_rooms) / SUM(hr.num_rooms) * 100, 0) AS occupancy_percentage
    FROM hotel_rooms hr
    LEFT JOIN (
        SELECT room_id,
               COUNT(*) AS reserved_rooms
        FROM reservations
        WHERE hotel_id = %s
          AND checkin_date <= %s
          AND checkout_date >= %s
        GROUP BY room_id
    ) r ON hr.room_id = r.room_id
    WHERE hr.hotel_id = %s
    GROUP BY hr.room_type
    '''
    values = (hotel_id, today, today, hotel_id)
    cursor = cnx.cursor()
    cursor.execute(query, values)

    result = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    report = [dict(zip(column_names, row)) for row in result]

    return report

@app.route('/reports/occupancy', methods=['GET'])
@cross_origin()
def hotel_occupancy_report():
    token = request.headers.get('Authorization')
    hotel_id = extract_hotel_id(token)

    if hotel_id is None:
        return jsonify({'error': 'Invalid token.'}), 401

    today = date.today()

    cache_key = f"hotel_occupancy_report:{hotel_id}:{today}"
    cached_report = redis_client.get(cache_key)

    if cached_report:
        report = json.loads(cached_report)
    else:
        report = get_hotel_occupancy_report(hotel_id, today)
        redis_client.set(cache_key, json.dumps(report), ex=60*60)  # Cache for 1 hour

    return jsonify(report), 200

@app.route('/healthz')
def health_check():
    return 'OK', 200

if __name__ == '__main__':
    app.run(debug=True)
