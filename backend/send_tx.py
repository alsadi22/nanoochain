# send_tx.py

import time, requests
from wallet import Wallet, public_key_to_address

NODE_URL = "http://127.0.0.1:5000"

def main():
    w = Wallet()
    sender = w.address
    recipient = input("Recipient address: ").strip()
    amount    = float(input("Amount to send: ").strip())
    timestamp = int(time.time())
    # Message format must match node.py’s verify logic:
    msg = f"{sender}|{recipient}|{amount}|{timestamp}"
    signature = w.sign(msg)
    payload = {
      "sender": sender,
      "recipient": recipient,
      "amount": amount,
      "timestamp": timestamp,
      "signature": signature,
      "public_key": w.get_public_key_hex()
    }
    resp = requests.post(f"{NODE_URL}/transactions/new", json=payload)
    print(resp.status_code, resp.json())

if __name__ == "__main__":
    main()
