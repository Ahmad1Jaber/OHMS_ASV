import os
from flask import Flask, request, jsonify
import configparser
import mysql.connector
import bcrypt
global cnx
app = Flask(__name__)
from configparser import ConfigParser
from flask_cors import CORS
from flask_cors import cross_origin


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

@app.route('/register',methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type'])
def register():
    # Get the request data
    data = request.json

    # Extract the user details from the request data
    hotel_name = data.get('hotel_name')
    email = data.get('email')
    password = data.get('password')

    # Hash and salt the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    # Insert the user into the database
    try:
        cursor = cnx.cursor()
        insert_query = "INSERT INTO  hotel_managers (hotel_name, email, password) VALUES (%s, %s, %s)"
        insert_data = (hotel_name, email, hashed_password.decode('utf-8'))
        cursor.execute(insert_query, insert_data)
        cnx.commit()
    except mysql.connector.Error as err:
        # Handle database errors
        response = {
            'status': 'fail',
            'message': f"Database error: {err}"
        }
        return jsonify(response), 500

    # Return a success response
    response = {
        'status': 'success',
        'message': 'User registered successfully.'
    }
    return jsonify(response), 200




@app.route('/login', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type'])
def login():
    # Get the request data
    data = request.json

    # Extract the user details from the request data
    email = data.get('email')
    password = data.get('password')

    # Retrieve the user from the database
    cursor = cnx.cursor()
    select_query = "SELECT manager_id, password FROM hotel_managers WHERE email = %s"
    select_data = (email,)
    cursor.execute(select_query, select_data)
    result = cursor.fetchone()

    if result is None:
        # User not found
        response = {
            'status': 'fail',
            'message': 'Invalid email or password.'
        }
        return jsonify(response), 401

    user_id, hashed_password = result
    if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
        # Passwords match, login successful
        response = {
            'status': 'success',
            'message': 'User logged in successfully.',
            'user_id': user_id
        }
        return jsonify(response), 200
    else:
        # Passwords don't match, login failed
        response = {
            'status': 'fail',
            'message': 'Invalid email or password.'
        }
        return jsonify(response), 401
    
@app.route('/healthz')
@cross_origin(origin='*', headers=['Content-Type'])
def health_check():
    return 'OK', 200
    
if __name__ == "__main__":
    app.run()