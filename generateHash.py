import hashlib
import requests

# IPFS API URL for retrieving files
IPFS_GATEWAY_URL = "http://127.0.0.1:8080/ipfs/"  # Read-only IPFS Gateway

def read_file_from_local_ipfs(cid):
    """Reads a file from the local IPFS node using HTTP Gateway."""
    try:
        response = requests.get(f"{IPFS_GATEWAY_URL}{cid}")
        response.raise_for_status()  # Raise error for HTTP issues

        return response.content  # Return file content as bytes
    except requests.exceptions.RequestException as e:
        raise Exception(f"IPFS Read Failed: {str(e)}")

def generate_certificate_hash(cid):
    """Generates a SHA-256 hash of a certificate stored in IPFS."""
    file_data = read_file_from_local_ipfs(cid)
    hash_value = hashlib.sha256(file_data).hexdigest()
    return hash_value
