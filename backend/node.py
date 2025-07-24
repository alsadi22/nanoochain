from flask import Flask, request, jsonify
from flask_cors import CORS
import os, requests, time

from blockchain import Blockchain, calculate_hash, load_chain, save_chain
from wallet import Wallet, verify_signature
from mempool import Mempool
from miner import mine_block

app = Flask(__name__)
CORS(app)

# Initialize blockchain, mempool, wallet
bc = Blockchain()
mp = Mempool()
try:
    wallet = Wallet()
except FileNotFoundError:
    wallet = None

PEERS = set()
PORT = int(os.environ.get("PORT", 5000))
SELF_URL = f"http://127.0.0.1:{PORT}"

@app.route("/")
def home():
    return jsonify({
        "message": "NanooChain Node",
        "you": wallet.address if wallet else None
    }), 200

@app.route("/chain", methods=["GET"])
def get_chain():
    return jsonify(bc.chain), 200

@app.route("/mempool", methods=["GET"])
def get_mempool():
    return jsonify(mp.get_transactions()), 200

@app.route("/balance/<address>", methods=["GET"])
def balance(address):
    bal = bc.get_balance(address)
    return jsonify({"address": address, "balance": bal}), 200

@app.route("/transactions/new", methods=["POST"])
def new_transaction():
    data = request.get_json() or {}
    required = ["sender", "recipient", "amount", "signature", "public_key", "timestamp"]
    if not all(k in data for k in required):
        return jsonify({"message": "Missing fields"}), 400

    # Reconstruct message for verification
    msg = f"{data['sender']}|{data['recipient']}|{data['amount']}|{data['timestamp']}"
    if not verify_signature(data["public_key"], msg, data["signature"]):
        return jsonify({"message": "Invalid signature"}), 400

    # Build transaction and compute its hash
    tx = {
        "sender": data["sender"],
        "recipient": data["recipient"],
        "amount": data["amount"],
        "timestamp": data["timestamp"],
        "signature": data["signature"],
        "public_key": data["public_key"],
    }
    tx["hash"] = calculate_hash(tx)

    if not mp.add_transaction(tx):
        return jsonify({"message": "Duplicate transaction"}), 409

    # Broadcast to peers
    for peer in PEERS:
        try:
            requests.post(f"{peer}/transactions/new", json=data, timeout=2)
        except:
            pass

    return jsonify({"message": "Transaction added"}), 201

@app.route("/mine", methods=["GET"])
def mine_route():
    # Mine a new block (writes to disk)
    block = mine_block()

    # Reload this app's blockchain to include the new block
    bc.chain = load_chain()

    # Broadcast new block to peers
    for peer in PEERS:
        try:
            requests.post(f"{peer}/blocks/new", json=block, timeout=2)
        except:
            pass

    return jsonify(block), 200

@app.route("/blocks/new", methods=["POST"])
def receive_block():
    block = request.get_json() or {}
    if not bc.add_block(block):
        return jsonify({"message": "Rejected block"}), 400
    mp.remove_transactions(block.get("transactions", []))
    return jsonify({"message": "Block added"}), 201

@app.route("/peers", methods=["GET"])
def get_peers():
    return jsonify(list(PEERS)), 200

@app.route("/peers/add", methods=["POST"])
def add_peer():
    peer = request.get_json().get("peer")
    if peer and peer != SELF_URL:
        PEERS.add(peer)
        return jsonify({"message": "Peer added", "peer": peer}), 201
    return jsonify({"message": "Invalid peer"}), 400

def discover_peers():
    seed = os.environ.get("SEED_NODE")
    if seed and seed != SELF_URL:
        try:
            requests.post(f"{seed}/peers/add", json={"peer": SELF_URL}, timeout=2)
            PEERS.add(seed)
        except:
            pass

if __name__ == "__main__":
    discover_peers()
    print(f"[discovery] peers={PEERS}")
    app.run(host="0.0.0.0", port=PORT, debug=True)
