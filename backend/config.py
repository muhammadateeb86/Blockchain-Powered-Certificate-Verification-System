# config.py

import os

# MySQL Database configuration (update these values)
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',       # Replace with your MySQL username
    'password': '0933s@if',   # Replace with your MySQL password
    'database': 'mydata'
}

# File upload folder for generated certificates
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'issued_certificates')

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
