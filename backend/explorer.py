#!/usr/bin/env python3
"""
CLI Block Explorer for NanooChain
Usage:
  explorer.py blocks               # List all block indices and hashes
  explorer.py block <index>        # Show details for a specific block
  explorer.py tx <txid>            # Show details for a transaction
  explorer.py address <address>    # Show all TXs and balance for an address
"""
import json
import os
import sys
import argparse

CHAIN_FILE = 'chain_data/chain.json'


def load_chain():
    if not os.path.exists(CHAIN_FILE):
        print(f"Error: Chain file not found at {CHAIN_FILE}")
        sys.exit(1)
    with open(CHAIN_FILE, 'r') as f:
        return json.load(f)


def list_blocks(chain):
    print("Index    Hash")
    print("-----    ----")
    for block in chain:
        print(f"{block['index']:>5}    {block['hash']}")


def show_block(chain, index):
    try:
        block = next(b for b in chain if b['index'] == index)
    except StopIteration:
        print(f"Block {index} not found.")
        return
    print(json.dumps(block, indent=2))


def find_tx(chain, txid):
    for block in chain:
        for tx in block['transactions']:
            core = f"{tx['sender']}|{tx['recipient']}|{tx['amount']}|{tx.get('fee',0)}|{tx['timestamp']}"
            import hashlib
            if hashlib.sha256(core.encode()).hexdigest() == txid:
                print(f"Found in Block {block['index']}: ")
                print(json.dumps(tx, indent=2))
                return
    print(f"Transaction {txid} not found.")


def address_info(chain, address):
    txs = []
    balance = 0
    for block in chain:
        for tx in block['transactions']:
            if tx['recipient'] == address:
                balance += tx['amount']
                txs.append((block['index'], 'IN', tx))
            if tx['sender'] == address:
                balance -= tx['amount'] + tx.get('fee', 0)
                txs.append((block['index'], 'OUT', tx))
    print(f"Address: {address}")
    print(f"Balance: {balance} Nanoo")
    print("Transactions:")
    for idx, direction, tx in txs:
        print(f"  Block {idx} [{direction}] {tx['sender']} -> {tx['recipient']} : {tx['amount']} (fee {tx.get('fee',0)}) at {tx['timestamp']}")


def main():
    parser = argparse.ArgumentParser(prog='explorer.py')
    sub = parser.add_subparsers(dest='cmd')

    sub.add_parser('blocks', help='List all blocks')
    p_block = sub.add_parser('block', help='Show block details')
    p_block.add_argument('index', type=int, help='Block index')

    p_tx = sub.add_parser('tx', help='Show transaction details')
    p_tx.add_argument('txid', help='Transaction ID (SHA256)')

    p_addr = sub.add_parser('address', help='Show address history and balance')
    p_addr.add_argument('address', help='Nanoo address')

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        sys.exit(1)

    chain = load_chain()
    if args.cmd == 'blocks':
        list_blocks(chain)
    elif args.cmd == 'block':
        show_block(chain, args.index)
    elif args.cmd == 'tx':
        find_tx(chain, args.txid)
    elif args.cmd == 'address':
        address_info(chain, args.address)

if __name__ == '__main__':
    main()
