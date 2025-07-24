import hashlib
import json
import os
import time
from typing import List, Dict, Any

CHAIN_FILE = "chain.json"
DIFFICULTY = 4

def calculate_hash(block: Dict[str, Any]) -> str:
    b = block.copy()
    b.pop("hash", None)
    s = json.dumps(b, sort_keys=True).encode()
    return hashlib.sha256(s).hexdigest()

def load_chain() -> List[Dict[str, Any]]:
    if os.path.exists(CHAIN_FILE):
        with open(CHAIN_FILE, "r") as f:
            return json.load(f)
    return []

def save_chain(chain: List[Dict[str, Any]]) -> None:
    with open(CHAIN_FILE, "w") as f:
        json.dump(chain, f, indent=4)

class Blockchain:
    def __init__(self):
        self.chain = load_chain()
        if not self.chain:
            self.chain = [self.create_genesis_block()]

    def create_genesis_block(self) -> Dict[str, Any]:
        block = {
            "index": 0,
            "timestamp": time.time(),
            "transactions": [],
            "previous_hash": "0",
            "nonce": 0
        }
        block["hash"] = calculate_hash(block)
        save_chain([block])
        return block

    def get_last_block(self) -> Dict[str, Any]:
        return self.chain[-1]

    def add_block(self, block: Dict[str, Any]) -> bool:
        last = self.get_last_block()
        if block["previous_hash"] != last["hash"]:
            return False
        if calculate_hash(block) != block.get("hash"):
            return False
        if not block["hash"].startswith("0" * DIFFICULTY):
            return False
        self.chain.append(block)
        save_chain(self.chain)
        return True

    def is_valid_chain(self, chain: List[Dict[str, Any]]) -> bool:
        for i in range(1, len(chain)):
            prev, cur = chain[i-1], chain[i]
            if cur["previous_hash"] != prev["hash"]:
                return False
            if calculate_hash(cur) != cur.get("hash"):
                return False
            if not cur["hash"].startswith("0" * DIFFICULTY):
                return False
        return True

    def replace_chain(self, new_chain: List[Dict[str, Any]]) -> bool:
        if len(new_chain) > len(self.chain) and self.is_valid_chain(new_chain):
            self.chain = new_chain
            save_chain(self.chain)
            return True
        return False

    def get_balance(self, address: str) -> float:
        balance = 0.0
        for block in self.chain:
            for tx in block["transactions"]:
                if tx["sender"] == address:
                    balance -= tx["amount"]
                if tx["recipient"] == address:
                    balance += tx["amount"]
        return balance
