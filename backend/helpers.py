import hashlib
import datetime
import os
import requests  # Use requests instead of ipfsapi (deprecated)
from config import UPLOAD_FOLDER
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# IPFS API URL
IPFS_API_URL = "http://127.0.0.1:5001/api/v0/add"

def compute_sha256(file_content):
    """Compute the SHA-256 hash of the provided file content."""
    return hashlib.sha256(file_content).hexdigest()

def upload_to_ipfs(file_content):
    """
    Upload file content to IPFS using an HTTP API request.
    Returns the CID (content identifier).
    """
    files = {'file': ('certificate.pdf', file_content)}
    try:
        response = requests.post(IPFS_API_URL, files=files)
        response.raise_for_status()  # Raise error for HTTP issues

        return response.json()["Hash"]  # Extract CID from response
    except requests.exceptions.RequestException as e:
        raise Exception(f"IPFS Upload Failed: {str(e)}")

def generate_certificate_pdf(student_name, course, issue_date):
    """
    Generate a digital certificate PDF using ReportLab.
    Returns the file path of the generated certificate.
    """
    timestamp = int(datetime.datetime.now().timestamp())
    safe_student_name = student_name.replace(' ', '_')
    file_name = f"{safe_student_name}_{timestamp}.pdf"
    file_path = os.path.join(UPLOAD_FOLDER, file_name)
    
    c = canvas.Canvas(file_path, pagesize=letter)
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(300, 700, "Certificate of Completion")
    
    c.setFont("Helvetica", 16)
    text = f"This certifies that {student_name} has successfully completed the {course} course."
    c.drawCentredString(300, 650, text)
    
    c.setFont("Helvetica", 12)
    c.drawCentredString(300, 600, f"Issue Date: {issue_date}")
    
    c.showPage()
    c.save()
    
    return file_path
