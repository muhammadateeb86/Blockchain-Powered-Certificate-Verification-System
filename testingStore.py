import json
from web3 import Web3

# 🔹 Step 1: Connect to Ethereum Sepolia Testnet
INFURA_URL = "https://sepolia.infura.io/v3/f780ee3111ee4d86b79062a69c03d65b"  # Replace with your Infura Project ID
w3 = Web3(Web3.HTTPProvider(INFURA_URL))

if not w3.is_connected():
    raise Exception("⚠️ Failed to connect to Sepolia Testnet")

print("✅ Connected to Sepolia Testnet")

# 🔹 Step 2: Load Contract ABI from abi.json
with open("abi.json", "r") as file:
    CONTRACT_ABI = json.load(file)

# 🔹 Step 3: Load Contract Address
CONTRACT_ADDRESS = "0x12742839cda172ae62ae1a14be3fca6bb7ee9b1c"
CHECKSUM_ADDRESS = Web3.to_checksum_address(CONTRACT_ADDRESS)

contract = w3.eth.contract(address=CHECKSUM_ADDRESS, abi=CONTRACT_ABI)

# 🔹 Step 4: Wallet Details
WALLET_ADDRESS = "0x6107dF8C3197286982A624198748d50BF0bd88B6"  # Replace with your wallet address
PRIVATE_KEY = "0fb8f04ce5e17b0f96cf592c799d2b4cb82c8d85837dbce83206c773e9eee8fa"  # ⚠️ Never share your private key publicly

# 🔹 Step 5: Store Certificate Hash (Requires Admin Role)
def store_certificate(cid, cert_hash, student_id):
    nonce = w3.eth.get_transaction_count(WALLET_ADDRESS)
    
    txn = contract.functions.storeHash(cid, cert_hash, student_id).build_transaction({
        'from': WALLET_ADDRESS,
        'nonce': nonce,
        'gas': 300000,
        'gasPrice': w3.eth.gas_price,
        'chainId': 11155111  # Sepolia Testnet Chain ID
    })

    # Sign transaction
    signed_txn = w3.eth.account.sign_transaction(txn, PRIVATE_KEY)

    # Send transaction
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)  # ✅ Corrected
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print(f"✅ Transaction successful! Hash: {receipt.transactionHash.hex()}")


# 🔹 Step 6: Verify Certificate Hash
def verify_certificate(cid):
    stored_hash = contract.functions.verifyHash(cid).call()
    print(f"✅ Stored Hash for CID {cid}: {stored_hash}")
    return stored_hash


# 🔹 Step 7: Run the Tests
if __name__ == "__main__":
    print("\n🔹 Storing certificate...")
    store_certificate("Qm123Hash", "HASH_VALUE_123", "STUDENT_123")

    print("\n🔹 Verifying certificate...")
    verify_certificate("Qm123Hash")
