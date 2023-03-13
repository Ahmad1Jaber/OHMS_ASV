
import requests

url = "http://127.0.0.1:6000/login"

data = {
    "manager_name": "Ahmad Jaber",
    "email_address": "ahmad.jaber@Regency.com",
    "password": "p@ssword",
    "hotel_name": "Regency",
    "address_location": "Amman",
    "country_id" : "111",
    "website": "https://www.Regency.com"
}

response = requests.post(url, json=data)

print("Response status code:", response)
print("Response body:", response.text)

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