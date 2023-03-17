import os
from flask import Flask, jsonify, request
import mysql.connector
import bcrypt
from configparser import ConfigParser

app = Flask(__name__)

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

@app.route('/user/register', methods=['POST'])
def register():
    # Get the user's details from the request
    name = request.json.get('name')
    email = request.json.get('email')
    password = request.json.get('password')

    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Create a cursor object
    cursor = cnx.cursor()

    # Check if the email is already registered
    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()

    if user:
        # User already exists
        cursor.close()
        return jsonify({'message': 'User already exists'}), 409

    # Register the user
    cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))
    cnx.commit()
    cursor.close()

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/user/login', methods=['POST'])
def login():
    # Get the user's details from the request
    email = request.json.get('email')
    password = request.json.get('password')

    # Create a cursor object
    cursor = cnx.cursor()

    # Get the user's details
    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()

    if not user:
        # User does not exist
        cursor.close()
        return jsonify({'message': 'Invalid credentials'}), 401

    # Check if the password is correct
    if not bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
        # Incorrect password
        cursor.close()
        return jsonify({'message': 'Invalid credentials'}), 401

    # Login successful
    cursor.close()
    return jsonify({'message': 'Login successful'}), 200

@app.route('/healthz')
def health_check():
    return 'OK', 200

if __name__ == '__main__':
    app.run(debug=True)
