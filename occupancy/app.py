from flask import Flask, jsonify
import mysql.connector
from configparser import ConfigParser

# Initialize Flask app
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

# Endpoint to get occupancy report for a hotel
@app.route('/hotels/<int:hotel_id>/occupancy', methods=['GET'])
def get_occupancy_report(hotel_id):
    cursor = cnx.cursor()
    cursor.execute("""
        SELECT room_type, COUNT(*) AS total_rooms, 
            SUM(CASE WHEN reservations.check_in <= %(check_out)s AND reservations.check_out >= %(check_in)s THEN 1 ELSE 0 END) AS occupied_rooms
        FROM rooms 
        LEFT JOIN reservations ON rooms.room_id = reservations.room_id
        WHERE rooms.hotel_id = %(hotel_id)s
        GROUP BY room_type
    """, {'check_in': request.args.get('check_in'), 'check_out': request.args.get('check_out'), 'hotel_id': hotel_id})

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

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
