# routes.py
import sys
import os

# Add the parent directory to Python’s import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from flask import Blueprint, request, jsonify, send_from_directory
from db import execute_query
from config import UPLOAD_FOLDER
from helpers import upload_to_ipfs, generate_certificate_pdf
# Import Member 1’s integration functions from the member1 folder:
from certificate_process import process_certificate
from generateHash import generate_certificate_hash

routes = Blueprint('routes', __name__)

@routes.route('/register-user', methods=['POST'])
def register_user():
    """
    Endpoint to register a new user (student, admin, or employer).
    Expects JSON data with user_id, name, email, and role.
    """
    data = request.get_json()
    
    # Required fields check
    required_fields = ['user_id', 'name', 'email', 'role']
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": "user_id, name, email, and role are required"}), 400

    user_id = data['user_id']
    name = data['name']
    email = data['email']
    role = data['role'].lower()

    # Role validation
    valid_roles = {'student', 'admin', 'employer'}
    if role not in valid_roles:
        return jsonify({"error": f"Invalid role. Choose from {valid_roles}"}), 400

    # Insert user into database
    insert_query = """
    INSERT INTO users (user_id, name, email, role)
    VALUES (%s, %s, %s, %s)
    """
    try:
        execute_query(insert_query, (user_id, name, email, role))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "User registered successfully!"}), 201

@routes.route('/upload-degree-certificate', methods=['POST'])
def upload_degree_certificate():
    if 'certificate' not in request.files or 'student_id' not in request.form:
        return jsonify({"error": "certificate file and student_id are required"}), 400

    certificate_file = request.files['certificate']
    student_id = request.form["student_id"]

    try:
        file_content = certificate_file.read()
        cid = upload_to_ipfs(file_content)
        tx_result = process_certificate(cid, student_id)
        tx_id = tx_result["transaction_id"]
        cert_hash = generate_certificate_hash(cid)

        insert_query = """
        INSERT INTO certificates (student_id, certificate_type, certificate_hash, blockchain_tx_id, ipfs_hash)
        VALUES (%s, %s, %s, %s, %s)
        """
        certificate_id = execute_query(insert_query, (student_id, 'degree', cert_hash, tx_id, cid))

        return jsonify({
            "message": "Degree certificate stored successfully!",
            "certificate_id": certificate_id,
            "certificate_hash": cert_hash,
            "blockchain_tx_id": tx_id,
            "ipfs_hash": cid
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Ensure errors are returned as JSON
    """
    Endpoint to securely store a degree certificate.
    Expects a certificate file and student_id as form-data.
    """
    if 'certificate' not in request.files or 'student_id' not in request.form:
        return jsonify({"error": "certificate file and student_id are required"}), 400

    certificate_file = request.files['certificate']
    student_id = request.form["student_id"]

    # Read file content and upload to IPFS to get CID
    file_content = certificate_file.read()
    cid = upload_to_ipfs(file_content)
    
    # Process certificate via Member 1’s integration to store hash on blockchain
    tx_result = process_certificate(cid, student_id)
    tx_id = tx_result["transaction_id"]
    
    # Retrieve the certificate hash using Member 1's generate_certificate_hash function
    cert_hash = generate_certificate_hash(cid)

    # Insert certificate record into the database (certificate_type = 'degree')
    insert_query = """
    INSERT INTO certificates (student_id, certificate_type, certificate_hash, blockchain_tx_id, ipfs_hash)
    VALUES (%s, %s, %s, %s, %s)
    """
    try:
        certificate_id = execute_query(insert_query, (student_id, 'degree', cert_hash, tx_id, cid))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "message": "Degree certificate stored successfully!",
        "certificate_id": certificate_id,
        "certificate_hash": cert_hash,
        "blockchain_tx_id": tx_id,
        "ipfs_hash": cid
    })

@routes.route('/issue-certificate', methods=['POST'])
def issue_certificate():
    """
    Endpoint to issue a digital certificate.
    Expects JSON data with student_id, student_name, course, and issue_date.
    Generates a PDF certificate, uploads it to IPFS, and stores metadata in the database.
    """
    data = request.get_json()
    required_fields = ['student_id', 'student_name', 'course', 'issue_date']
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": "student_id, student_name, course, and issue_date are required"}), 400

    student_id = data['student_id']
    student_name = data['student_name']
    course = data['course']
    issue_date = data['issue_date']

    # Generate PDF certificate and read its content
    pdf_file_path = generate_certificate_pdf(student_name, course, issue_date)
    with open(pdf_file_path, 'rb') as f:
        pdf_content = f.read()
    
    # Upload PDF to IPFS and get CID
    cid = upload_to_ipfs(pdf_content)
    
    # Process certificate via Member 1’s integration
    tx_result = process_certificate(cid, student_id)
    tx_id = tx_result["transaction_id"]
    
    # Compute certificate hash using Member 1’s generate_certificate_hash function
    cert_hash = generate_certificate_hash(cid)
    
    # Construct a download link for the generated PDF
    download_link = request.host_url + "download-certificate/" + pdf_file_path.split('/')[-1]

    # Insert record into the database (certificate_type = 'digital')
    insert_query = """
    INSERT INTO certificates (student_id, certificate_type, certificate_hash, blockchain_tx_id, ipfs_hash, download_link)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    try:
        certificate_id = execute_query(insert_query, (student_id, 'digital', cert_hash, tx_id, cid, download_link))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "message": "Digital certificate issued successfully!",
        "certificate_id": certificate_id,
        "certificate_hash": cert_hash,
        "blockchain_tx_id": tx_id,
        "ipfs_hash": cid,
        "download_link": download_link
    })

@routes.route('/download-certificate/<filename>', methods=['GET'])
def download_certificate(filename):
    """
    Endpoint to download the issued digital certificate.
    """
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

@routes.route('/get-certificate/<int:certificate_id>', methods=['GET'])
def get_certificate(certificate_id):
    """
    Retrieve certificate details from the database.
    """
    select_query = "SELECT * FROM certificates WHERE certificate_id = %s"
    
    try:
        certificate = execute_query(select_query, (certificate_id,), fetchone=True)

        if not certificate:
            return jsonify({"error": "Certificate not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(certificate)

