from flask import Flask, jsonify, request
import mysql.connector
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Read the credentials from the config file
config = {
    'user': 'username',
    'password': 'password',
    'host': 'hostname',
    'database': 'database'
}

# Connect to the database
cnx = mysql.connector.connect(**config)

@app.route('/register', methods=['POST'])
def register():
    # Get the user's details from the request
    name = request.json.get('name')
    email = request.json.get('email')
    password = request.json.get('password')

    # Hash the password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

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

@app.route('/login', methods=['POST'])
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
    if not bcrypt.check_password_hash(user[3], password):
        # Incorrect password
        cursor.close()
        return jsonify({'message': 'Invalid credentials'}), 401

    # Login successful
    cursor.close()
    return jsonify({'message': 'Login successful'}), 200

if __name__ == '__main__':
    app.run(debug=True)
