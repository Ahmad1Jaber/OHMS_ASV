import os
from flask import Flask, request, jsonify
import configparser
import mysql.connector
import bcrypt

app = Flask(__name__)

# Get Cloud SQL credentials
config = configparser.ConfigParser()
config.read('config.ini')

cnx = mysql.connector.connect(
    user=config['mysql']['user'],
    password=config['mysql']['password'],
    host=config['mysql']['host'],
    database=config['mysql']['database']
)


@app.route('/register', methods=['POST'])
def register():
    # Get the request data
    data = request.json

    # Extract the user details from the request data
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Hash and salt the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    # Insert the user into the database
    try:
        cursor = cnx.cursor()
        insert_query = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
        insert_data = (username, email, hashed_password.decode('utf-8'))
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
def login():
    # Get the request data
    data = request.json

    # Extract the user details from the request data
    email = data.get('email')
    password = data.get('password')

    # Retrieve the user from the database
    cursor = cnx.cursor()
    select_query = "SELECT id, password FROM users WHERE email = %s"
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
