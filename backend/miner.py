import time
import os
from typing import Dict, Any
from blockchain import Blockchain, calculate_hash
from mempool import Mempool

DIFFICULTY = 4
BLOCK_REWARD = 50

def mine_block() -> Dict[str, Any]:
    bc = Blockchain()
    mp = Mempool()
    txs = mp.get_transactions()

    # Create coinbase tx
    miner_addr = os.getenv("MINER_ADDRESS", "")
    coinbase = {
        "sender": "COINBASE",
        "recipient": miner_addr,
        "amount": BLOCK_REWARD,
        "timestamp": time.time(),
    }
    coinbase["hash"] = calculate_hash(coinbase)
    coinbase["signature"] = ""

    # New block
    last = bc.get_last_block()
    block = {
        "index": last["index"] + 1,
        "previous_hash": last["hash"],
        "timestamp": time.time(),
        "transactions": [coinbase] + txs,
        "nonce": 0,
        "hash": ""
    }

    # Proof-of-Work
    prefix = "0" * DIFFICULTY
    while True:
        block["nonce"] += 1
        h = calculate_hash(block)
        if h.startswith(prefix):
            block["hash"] = h
            break

    # Append & clear mempool
    bc.add_block(block)
    mp.clear()
    print(f"[Miner] Block {block['index']} mined: {block['hash']}")
    return block
