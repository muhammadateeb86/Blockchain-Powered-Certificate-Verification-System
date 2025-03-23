import generateHash
import storeVerifyHash

def process_certificate(cid,Student_id):
    hash_value = generateHash.generate_certificate_hash(cid)
    tx_id = storeVerifyHash.storeHash(cid,hash_value,Student_id)
    
    return {
        "transaction_id": tx_id
    }
