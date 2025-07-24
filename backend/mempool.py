import json
import os
from typing import List, Dict

MEMPOOL_FILE = "mempool.json"

class Mempool:
    def __init__(self):
        self.transactions: List[Dict] = self._load()

    def _load(self) -> List[Dict]:
        if os.path.exists(MEMPOOL_FILE):
            try:
                with open(MEMPOOL_FILE, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []

    def save(self) -> None:
        with open(MEMPOOL_FILE, "w") as f:
            json.dump(self.transactions, f, indent=4)

    def add_transaction(self, tx: Dict) -> bool:
        """
        Add a transaction to the mempool if it's not a duplicate.
        Returns True if added, False if duplicate.
        """
        if not any(t.get("hash") == tx.get("hash") for t in self.transactions):
            self.transactions.append(tx)
            self.save()
            return True
        return False

    def get_transactions(self) -> List[Dict]:
        return list(self.transactions)

    def clear(self) -> None:
        self.transactions = []
        self.save()

    def remove_transactions(self, txs: List[Dict]) -> None:
        hashes = {t.get("hash") for t in txs}
        self.transactions = [t for t in self.transactions if t.get("hash") not in hashes]
        self.save()

