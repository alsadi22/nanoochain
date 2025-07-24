import json
import sys
import hashlib
from wallet import sign_message, load_public_key

def tx_hash(tx):
    """
    Generate a unique hash for the transaction.
    """
    tx_string = json.dumps(tx, sort_keys=True).encode()
    return hashlib.sha256(tx_string).hexdigest()

def create_transaction(sender, recipient, amount):
    """
    Create a transaction dictionary with a signature.
    """
    message = f"{sender}{recipient}{amount}"
    signature = sign_message(message)
    
    tx = {
        'from': sender,
        'to': recipient,
        'amount': amount,
        'signature': signature
    }

    if verify_transaction(tx):
        filename = "transaction.json"
        with open(filename, "w") as f:
            json.dump(tx, f, indent=4)
        print("✅ Transaction is valid!")
        print(f"✅ Transaction saved to {filename}")
    else:
        print("❌ Invalid transaction. Not saved.")

def verify_transaction(tx):
    """
    Verify the transaction's signature using the sender's public key.
    """
    try:
        pubkey = load_public_key("wallet/public.key")
        message = f"{tx['from']}{tx['to']}{tx['amount']}".encode()
        signature = bytes.fromhex(tx['signature'])
        return pubkey.verify(signature, message)
    except Exception as e:
        print(f"❌ Transaction verification error: {e}")
        return False

# CLI interface
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 transaction.py <from_address> <to_address> <amount>")
        sys.exit(1)

    from_address = sys.argv[1]
    to_address = sys.argv[2]
    amount = float(sys.argv[3])

    create_transaction(from_address, to_address, amount)
