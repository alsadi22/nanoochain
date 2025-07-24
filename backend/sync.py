import requests
import json

def sync_with_peers(blockchain, mempool, peers):
    """Sync local blockchain and mempool from peers"""
    for peer in peers:
        try:
            # Sync blockchain
            res = requests.get(f"{peer}/chain")
            if res.status_code == 200:
                peer_chain = res.json()["chain"]
                if len(peer_chain) > len(blockchain.chain):
                    blockchain.load_chain(peer_chain)

            # Sync mempool
            res = requests.get(f"{peer}/mempool")
            if res.status_code == 200:
                peer_mempool = res.json()["mempool"]
                for tx in peer_mempool:
                    if tx not in mempool.transactions:
                        mempool.add_transaction(tx)

        except Exception as e:
            print(f"[sync] Failed to sync with {peer}: {e}")

