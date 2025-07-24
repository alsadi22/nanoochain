import os
import sys
import struct
import hashlib
import binascii
import time
from optparse import OptionParser


def sha256d(data):
    """Double SHA-256 hash."""
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


def create_input_script(psz_timestamp):
    """Create coinbase input script with a custom timestamp message."""
    script_prefix = b'\x04\xff\xff\x00\x1d\x01\x04'
    timestamp_bytes = psz_timestamp.encode('utf-8')
    script = script_prefix + bytes([len(timestamp_bytes)]) + timestamp_bytes
    print("Coinbase Script:", binascii.hexlify(script).decode())
    return script


def create_output_script(pubkey):
    """Create a standard P2PK output script."""
    OP_CHECKSIG = b'\xac'
    pubkey_bytes = binascii.unhexlify(pubkey)
    script = bytes([len(pubkey_bytes)]) + pubkey_bytes + OP_CHECKSIG
    return script


def create_transaction(input_script, output_script, options):
    """Builds a raw coinbase transaction."""
    version = struct.pack('<I', 1)
    tx_in_count = b'\x01'
    prev_output = b'\x00' * 32
    prev_out_index = struct.pack('<I', 0xFFFFFFFF)
    script_length = bytes([len(input_script)])
    sequence = struct.pack('<I', 0xFFFFFFFF)

    tx_out_count = b'\x01'
    value = struct.pack('<Q', options.value)
    output_script_length = bytes([len(output_script)])

    lock_time = struct.pack('<I', 0)

    tx = (
        version +
        tx_in_count +
        prev_output +
        prev_out_index +
        script_length +
        input_script +
        sequence +
        tx_out_count +
        value +
        output_script_length +
        output_script +
        lock_time
    )
    return tx


def create_block_header(version, prev_block_hash, merkle_root, time, bits, nonce):
    """Builds the raw block header."""
    return struct.pack("<L32s32sLLL", version, prev_block_hash, merkle_root, time, bits, nonce)


def save_block(filename, header, transactions):
    """Save the genesis block to a binary file."""
    with open(filename, 'wb') as f:
        f.write(header)
        f.write(b'\x01')  # Number of transactions (varint = 1)
        f.write(transactions)
    print(f"Genesis block saved to {filename}")


def main():
    parser = OptionParser()
    parser.add_option("-z", dest="timestamp", default="The Times 03/Jan/2009 Chancellor on brink of second bailout for banks")
    parser.add_option("-p", dest="pubkey", default="04ffff001d0104")
    parser.add_option("-a", dest="algorithm", default="SHA256")
    parser.add_option("-t", dest="time", type="int", default=int(time.time()))
    parser.add_option("-n", dest="nonce", type="int", default=0)
    parser.add_option("-v", dest="version", type="int", default=1)
    parser.add_option("-b", dest="bits", type="int", default=0x207fffff)
    parser.add_option("--value", dest="value", type="int", default=50 * 100000000)  # 50 coins

    (options, args) = parser.parse_args()

    if options.algorithm.upper() != 'SHA256':
        print("Error: Only SHA256 is implemented in this version.")
        sys.exit(1)

    input_script = create_input_script(options.timestamp)
    output_script = create_output_script(options.pubkey)
    tx = create_transaction(input_script, output_script, options)

    merkle_root = sha256d(tx)
    print("Merkle Root:", binascii.hexlify(merkle_root[::-1]).decode())

    max_nonce = 0x7fffffff
    target = (options.bits & 0xffffff) * 2**(8*((options.bits >> 24) - 3))

    print("Mining genesis block...")

    for nonce in range(options.nonce, max_nonce):
        header = create_block_header(
            options.version,
            b'\x00' * 32,
            merkle_root,
            options.time,
            options.bits,
            nonce
        )
        hash = sha256d(header)
        hash_int = int.from_bytes(hash[::-1], byteorder='big')

        if hash_int < target:
            print("\n🎉 Genesis block mined!")
            print("Nonce:", nonce)
            print("Genesis Hash:", binascii.hexlify(hash[::-1]).decode())
            print("Merkle Root:", binascii.hexlify(merkle_root[::-1]).decode())
            save_block("genesis.dat", header, tx)
            break
    else:
        print("❌ Failed to find a valid genesis block.")


if __name__ == '__main__':
    main()
