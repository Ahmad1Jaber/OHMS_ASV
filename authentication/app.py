from flask import Flask, request, jsonify
import bcrypt
import uuid
from flask_cors import CORS
from flask_cors import cross_origin
from configparser import ConfigParser
import mysql.connector
import redis
import jwt
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

redishost = config.get('redis', 'redishost')
redisport = config.get('redis', 'redisport')
app.config['SECRET_KEY'] = config.get('jwt', 'secret_key')

# Connect to Redis
r = redis.Redis(host=redishost, port=redisport)

def get_db():
    """Helper function to get a new database connection"""
    return mysql.connector.connect(user=username, password=password, host=hostname, database=database)

@app.before_request
def before_request():
    """Establish a new database connection before each request"""
    request.db = get_db()

@app.teardown_request
def teardown_request(exception):
    """Close the database connection after each request"""
    request.db.close()

@app.route('/register', methods=['POST'])
@cross_origin()
def register():
    try:
        data = request.get_json()
        manager_name = data.get('manager_name')
        email_address = data.get('email_address')
        password = data.get('password')
        hotel_name = data.get('hotel_name')
        address_location = data.get('address_location')
        website = data.get('website')
        country_id = data.get('country_id')
        hotel_id = str(uuid.uuid4())

        # Store the hotel manager details in Redis
        r.hmset(hotel_id, {
            'manager_name': manager_name,
            'email_address': email_address,
            'hotel_name': hotel_name,
            'address_location': address_location,
            'website': website,
            'country_id': country_id
        })

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Store the hotel manager login credentials in MySQL
        cursor = request.db.cursor()
        query = """INSERT INTO hotel_manager (hotel_id, email_address, password) VALUES (%s, %s, %s)"""
        record = (hotel_id, email_address, hashed_password)
        cursor.execute(query, record)
        request.db.commit()
        cursor.close()

        return jsonify({'message': 'Hotel manager registered successfully'})
    except Exception as e:
        print(f"Error while registering: {e}")
        return jsonify({'message': 'An error occurred while registering the hotel manager'}), 500
    
@app.route('/login', methods=['POST'])
@cross_origin()
def login():
    try:
        data = request.get_json()
        email_address = data.get('email_address')
        password = data.get('password')

        # Check Redis for the hotel manager details using the provided email address
        hotel_id = r.get(email_address)
        if hotel_id is not None:
            # Get the hotel manager details from Redis using the hotel ID
            manager_details = r.hgetall(hotel_id)

            # Compare the hashed password to the user's input
            hashed_password = manager_details.get('password').encode('utf-8')
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                # Generate a JWT token for the hotel manager
                token = generate_token(hotel_id)

                # Merge the hotel manager details from Redis with the login credentials from MySQL
                manager_details.update({'email_address': email_address})
                manager_details.update({'password': hashed_password})

                return jsonify({'message': 'Login successful', 'token': token, 'manager_details': manager_details})
            else:
                return jsonify({'message': 'Invalid email address or password'}), 401
        else:
            # Query MySQL for the hotel manager login credentials using the provided email address
            cursor = request.db.cursor()
            query = "SELECT hotel_id, password FROM hotel_manager WHERE email_address = %s"
            record = (email_address,)
            cursor.execute(query, record)
            result = cursor.fetchone()
            cursor.close()

            if result is None:
                return jsonify({'message': 'Invalid email address or password'}), 401

            # Compare the hashed password to the user's input
            hashed_password = result[1].encode('utf-8')
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                # Store the hotel manager details in Redis using the provided email address as the key
                hotel_id = result[0]
                manager_details = r.hgetall(hotel_id)
                r.set(email_address, hotel_id)
                
                # Generate a JWT token for the hotel manager
                token = generate_token(hotel_id)

                # Merge the hotel manager details from Redis with the login credentials from MySQL
                manager_details.update({'email_address': email_address})
                manager_details.update({'password': hashed_password})

                return jsonify({'message': 'Login successful', 'token': token, 'manager_details': manager_details})
            else:
                return jsonify({'message': 'Invalid email address or password'}), 401
    except Exception as e:
        print(f"Error while logging in: {e}")
        return jsonify({'message': 'An error occurred while logging in'}), 500



@app.route('/healthz')
def health_check():
    return 'OK', 200

def generate_token(hotel_id):
    try:
        payload = {
            'exp': datetime.utcnow() + timedelta(days=0, seconds=3600),
            'iat': datetime.utcnow(),
            'hotel_id': hotel_id
        }
        return jwt.encode(
            payload,
            app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )
    except Exception as e:
        return e
if __name__ == '__main__':
    app.run(debug=True) 