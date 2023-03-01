from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from datetime import datetime, timedelta

app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'hotels'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


@app.route('/managers', methods=['POST'])
def create_manager():
    """
    Endpoint to create a new hotel manager
    """
    manager = request.get_json()
    name = manager['hotel_name']
    email = manager['email']
    password = manager['password']

    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO hotel_managers (hotel_name, email, password) VALUES (%s, %s, %s)",
        (name, email, password)
    )
    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'Hotel manager created successfully'})


@app.route('/managers/<int:manager_id>/rooms', methods=['POST'])
def create_room(manager_id):
    """
    Endpoint to create a new room for a given hotel manager
    """
    room = request.get_json()
    room_type = room['room_type']
    price = room['price']
    capacity = room['capacity']

    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO rooms (manager_id, room_type, price, capacity) VALUES (%s, %s, %s, %s)",
        (manager_id, room_type, price, capacity)
    )
    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'Room created successfully'})


@app.route('/managers/<int:manager_id>/rooms', methods=['GET'])
def get_rooms(manager_id):
    """
    Endpoint to get all rooms for a given hotel manager
    """
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM rooms WHERE manager_id = %s", (manager_id,))
    rooms = cur.fetchall()
    cur.close()

    return jsonify({'rooms': rooms})



if __name__ == '__main__':
    app.run(debug=True)
