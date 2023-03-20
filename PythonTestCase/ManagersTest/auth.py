import requests
import time

url = "http://api.birdbook.live/login"

data = {
    "email_address": "ahmad.jaber@Regency.com",
    "password": "p@ssword"
}

start_time = time.time()
response = requests.post(url, json=data)
end_time = time.time()

latency = end_time - start_time

print("Response status code:", response.status_code)
print("Response body:", response.text)



"""
try:
    # Decode the token using the PyJWT library and the secret key
    decoded = jwt.decode(token, 'atyponisthebest', algorithms=['HS256'])
    print(decoded)
except jwt.exceptions.InvalidTokenError:
    print('Invalid token')


"""
"""

from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
import uuid
from configparser import ConfigParser
import bcrypt



config = ConfigParser()
config.read('config.ini')

username = config.get('mysql', 'user')
password = config.get('mysql', 'password')
hostname = config.get('mysql', 'host')
database = config.get('mysql', 'database')

def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            user=username,
            password=password,
            host=hostname,
            database=database
        )
    except Error as e:
        print(f"The error '{e}' occurred while connecting to MySQL")
    return connection


database_Con = create_connection()
print(database_Con)
print(str(uuid.uuid4()))
print(username)
print(database)
print(hostname)
"""