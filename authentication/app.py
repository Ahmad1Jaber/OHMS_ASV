from flask import Flask, request, jsonify
import bcrypt
import uuid
from flask_cors import CORS
from flask_cors import cross_origin
from configparser import ConfigParser
import mysql.connector

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

try:
    # Connect to the database
    cnx = mysql.connector.connect(user=username,
                                  password=password,
                                  host=hostname,
                                  database=database)
    print("Connected to database")
except mysql.connector.Error as e:
    print(f"Error connecting to database: {e}")
    exit(1)

@app.route('/register', methods=['POST'])
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

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        cursor = cnx.cursor()

        # Check if the email address already exists in the database
        query = "SELECT COUNT(*) FROM hotel_manager WHERE email_address = %s"
        record = (email_address,)
        cursor.execute(query, record)
        result = cursor.fetchone()
        if result[0] > 0:
            # Email address already exists in the database
            cursor.close()
            return jsonify({'message': 'Email address already exists'}), 409

        # Check if the provided country_id exists in the countries table
        query = "SELECT COUNT(*) FROM countries WHERE id = %s"
        record = (country_id,)
        cursor.execute(query, record)
        result = cursor.fetchone()
        if result[0] == 0:
            # Country ID doesn't exist in the countries table
            cursor.close()
            return jsonify({'message': 'Invalid country ID'}), 400

        # Insert the new hotel manager into the database
        query = """INSERT INTO hotel_manager (hotel_id, manager_name, email_address, password, hotel_name, address_location, website, country_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        record = (hotel_id, manager_name, email_address, hashed_password, hotel_name, address_location, website, country_id)
        cursor.execute(query, record)
        cnx.commit()
        cursor.close()

        return jsonify({'message': 'Hotel manager registered successfully'})
    except Exception as e:
        print(f"Error while registering: {e}")
        return jsonify({'message': 'An error occurred while registering the hotel manager'}), 500



@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email_address = data.get('email_address')
        password = data.get('password')

        cursor = cnx.cursor()
        query = "SELECT password FROM hotel_manager WHERE email_address = %s"
        record = (email_address,)
        cursor.execute(query, record)
        result = cursor.fetchone()
        cursor.close()

        if result is None:
            return jsonify({'message': 'Invalid email address or password'}), 401

        # Compare the hashed password to the user's input
        hashed_password = result[0].encode('utf-8')
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            return jsonify({'message': 'Login successful'})
        else:
            return jsonify({'message': 'Invalid email address or password'}), 401
    except Exception as e:
        print(f"Error while logging in: {e}")
        return jsonify({'message': 'An error occurred while logging in'}), 500
    
if __name__ == '__main__':
    app.run(debug=True)
