from flask import Flask, request, jsonify
import bcrypt
import uuid
from flask_cors import CORS, cross_origin
from configparser import ConfigParser
import mysql.connector
import jwt
from datetime import datetime, timedelta


def generate_token(user_id):
    try:
        payload = {
            'exp': datetime.utcnow() + timedelta(days=0, seconds=3600),
            'iat': datetime.utcnow(),
            'user_id': user_id
        }
        return jwt.encode(
            payload,
            app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )
    except Exception as e:
        return e

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
app.config['SECRET_KEY'] = config.get('jwt', 'secret_key')

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

@app.route('/users/register', methods=['POST'])
@cross_origin()
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        email_address = data.get('email_address')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        user_id = str(uuid.uuid4())

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        cursor = request.db.cursor()

        # Check if the email address already exists in the database
        query = "SELECT COUNT(*) FROM users WHERE email_address = %s"
        record = (email_address,)
        cursor.execute(query, record)
        result = cursor.fetchone()
        if result[0] > 0:
            # Email address already exists in the database
            cursor.close()
            return jsonify({'message': 'Email address already exists'}), 409

        # Insert the new user into the database
        query = """INSERT INTO users (user_id, username, email_address, password, first_name, last_name) VALUES (%s, %s, %s, %s, %s, %s)"""
        record = (user_id, username, email_address, hashed_password, first_name, last_name)
        cursor.execute(query, record)
        request.db.commit()
        cursor.close()

        return jsonify({'message': 'User registered successfully'})
    except Exception as e:
        print(f"Error while registering: {e}")
        return jsonify({'message': 'An error occurred while registering the user'}), 500
    
@app.route('/users/login', methods=['POST'])
@cross_origin()
def login():
    try:
        data = request.get_json()
        email_address = data.get('email_address')
        password = data.get('password')
        cursor = request.db.cursor()
        query = "SELECT user_id, password FROM users WHERE email_address = %s"
        record = (email_address,)
        cursor.execute(query, record)
        result = cursor.fetchone()
        cursor.close()

        if result is None:
            return jsonify({'message': 'Invalid email address or password'}), 401

        # Compare the hashed password to the user's input
        hashed_password = result[1].encode('utf-8')
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            token = generate_token(result[0])
            return jsonify({'message': 'Login successful','token':token })
        else:
            return jsonify({'message': 'Invalid email address or password'}), 401
    except Exception as e:
        print(f"Error while logging in: {e}")
        return jsonify({'message': 'An error occurred while logging in'}), 500

@app.route('/healthz')
def health_check():
    return 'OK', 200

if __name__ == '__main__':
    app.run(debug=True, port=6000)

