from configparser import ConfigParser
import os
from flask import Flask, request, jsonify
import configparser
import mysql.connector
import bcrypt
global cnx
# Initialize Flask app
app = Flask(__name__)
from configparser import ConfigParser
from flask_cors import CORS
from flask_cors import cross_origin
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

# Endpoint to get occupancy report for a hotel
@app.route('/occupancy', methods=['GET'])
@cross_origin()
def get_occupancy_report():
    # Get the authenticated hotel manager's credentials from the request headers
    email = request.headers.get('email')
    password = request.headers.get('password')

    # Verify the credentials and retrieve the manager_id
    cursor = cnx.cursor()
    cursor.execute("SELECT manager_id, password FROM hotel_managers WHERE email = %(email)s", {'email': email})
    result = cursor.fetchone()
    cursor.close()

    if not result or not bcrypt.checkpw(password.encode('utf-8'), result[1].encode('utf-8')):
        return jsonify({'error': 'Invalid credentials'}), 401

    manager_id = result[0]

    # Retrieve the occupancy report for all rooms associated with the manager_id
    cursor = cnx.cursor()
    cursor.execute("""
        SELECT room_type, COUNT(*) AS total_rooms, 
            SUM(CASE WHEN reservations.check_in <= %(check_out)s AND reservations.check_out >= %(check_in)s THEN 1 ELSE 0 END) AS occupied_rooms
        FROM rooms 
        LEFT JOIN reservations ON rooms.room_id = reservations.room_id
        WHERE rooms.manager_id = %(manager_id)s
        GROUP BY room_type
    """, {'check_in': request.args.get('check_in'), 'check_out': request.args.get('check_out'), 'manager_id': manager_id})

    results = cursor.fetchall()
    cursor.close()

    report = []
    for row in results:
        occupancy = 0 if row['total_rooms'] == 0 else round(row['occupied_rooms'] / row['total_rooms'] * 100, 2)
        report.append({
            'room_type': row['room_type'],
            'total_rooms': row['total_rooms'],
            'occupied_rooms': row['occupied_rooms'],
            'occupancy_percentage': occupancy
        })

    return jsonify({'occupancy_report': report})


@app.route('/healthz')
@cross_origin()
def health_check():
    return 'OK', 200

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
