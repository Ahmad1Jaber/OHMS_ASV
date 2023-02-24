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
    cursor = cnx.cursor()
    insert_query = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
    insert_data = (username, email, hashed_password.decode('utf-8'))
    cursor.execute(insert_query, insert_data)
    cnx.commit()

    # Return a success response
    response = {
        'status': 'success',
        'message': 'User registered successfully.'
    }
    return jsonify(response), 200
