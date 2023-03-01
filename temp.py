"""
@app.route('/users', methods=['POST'])
def create_user():
    """
    Endpoint to create a new user
    """
    user = request.get_json()
    name = user['name']
    email = user['email']
    password = user['password']

    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
        (name, email, password)
    )
    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'User created successfully'})


@app.route('/users/<int:user_id>/reservations', methods=['POST'])
def create_reservation(user_id):
    """
    Endpoint to create a new reservation for a given user
    """
    reservation = request.get_json()
    room_id = reservation['room_id']
    check_in = datetime.strptime(reservation['check_in'], '%Y-%m-%d')
    check_out = datetime.strptime(reservation['check_out'], '%Y-%m-%d')

    # Check if the room is available for the given dates
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM reservations WHERE room_id = %s AND ((check_in <= %s AND check_out >= %s) OR (check_in <= %s AND check_out >= %s) OR (check_in >= %s AND check_out <= %s))",
        (room_id, check_in, check_in, check_out, check_out, check_in, check_out)
    )
    count = cur.fetchone()['COUNT(*)']
    cur.close()

    if count > 0:
        return jsonify({'message': 'The room is not available for the given dates'})

    # Create the reservation
    cur = mysql.connection.cursor()
    cur.execute(
    "INSERT INTO reservations (user_id, room_id, check_in, check_out) VALUES (%s, %s, %s, %s)",
    (user_id, room_id, check_in, check_out)
    )
    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'Reservation created successfully'})


@app.route('/users/<int:user_id>/reservations', methods=['GET'])
def get_reservations(user_id):
    """
    Endpoint to get all reservations for a given user
    """
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM reservations WHERE user_id = %s", (user_id,))
    reservations = cur.fetchall()
    cur.close()

    return jsonify({'reservations': reservations})


@app.route('/managers/<int:manager_id>/reservations', methods=['GET'])
def get_manager_reservations(manager_id):
    """
    Endpoint to get all reservations for a given hotel manager
    """
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT r.*, u.name AS user_name, u.email AS user_email, rm.room_type FROM reservations r JOIN users u ON r.user_id = u.user_id JOIN rooms rm ON r.room_id = rm.room_id WHERE rm.manager_id = %s",
        (manager_id,)
    )
    reservations = cur.fetchall()
    cur.close()

    return jsonify({'reservations': reservations})
"""
