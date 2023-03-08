import os
from flask import Flask, request, jsonify
import configparser
import mysql.connector
import bcrypt

app = Flask(__name__)
from configparser import ConfigParser

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

@app.route('/managers', methods=['POST'])
def create_manager():
    """
    Endpoint to create a new hotel manager
    """
    manager = request.get_json()
    name = manager['hotel_name']
    email = manager['email']
    password = manager['password']

    # Hash and salt the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    # Insert the manager into the database
    try:
        cursor = cnx.cursor()
        insert_query = "INSERT INTO hotel_managers (hotel_name, email, password) VALUES (%s, %s, %s)"
        insert_data = (name, email, hashed_password.decode('utf-8'))
        cursor.execute(insert_query, insert_data)
        cnx.commit()
    except mysql.connector.Error as err:
        # Handle database errors
        response = {
            'message': f"Database error: {err}"
        }
        return jsonify(response), 500

    # Return a success response
    response = {
        'message': 'Hotel manager created successfully'
    }
    return jsonify(response)


@app.route('/managers/<int:manager_id>/rooms', methods=['POST'])
def create_room(manager_id):
    """
    Endpoint to create a new room for a given hotel manager
    """
    room = request.get_json()
    room_type = room['room_type']
    price = room['price']
    capacity = room['capacity']

    # Insert the room into the database
    try:
        cursor = cnx.cursor()
        insert_query = "INSERT INTO rooms (manager_id, room_type, price, capacity) VALUES (%s, %s, %s, %s)"
        insert_data = (manager_id, room_type, price, capacity)
        cursor.execute(insert_query, insert_data)
        cnx.commit()
    except mysql.connector.Error as err:
        # Handle database errors
        response = {
            'message': f"Database error: {err}"
        }
        return jsonify(response), 500

    # Return a success response
    response = {
        'message': 'Room created successfully'
    }
    return jsonify(response)


@app.route('/managers/<int:manager_id>/rooms', methods=['GET'])
def get_rooms(manager_id):
    """
    Endpoint to get all rooms for a given hotel manager
    """
    cursor = None  # define the variable to avoid UnboundLocalError
    try:
        cursor = cnx.cursor(dictionary=True)
        select_query = "SELECT * FROM rooms WHERE manager_id = %s"
        select_data = (manager_id,)
        cursor.execute(select_query, select_data)
        rooms = cursor.fetchall()
    except mysql.connector.Error as err:
        # Handle database errors
        response = {
            'message': f"Database error: {err}"
        }
        return jsonify(response), 500
    finally:
        if cursor:
            cursor.close()

    return jsonify({'rooms': rooms})

@app.route('/healthz')
def health_check():
    return 'OK', 200

if __name__ == '__main__':
    app.run(debug=True)
