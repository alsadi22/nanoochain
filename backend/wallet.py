import os
import hashlib
import base64
from ecdsa import SigningKey, SECP256k1, VerifyingKey
from Crypto.Hash import RIPEMD160
import base58

KEY_DIR = "wallet_keys"
PRIV_FILE = os.path.join(KEY_DIR, "private.pem")
PUB_FILE = os.path.join(KEY_DIR, "public.pem")

def generate_key_pair():
    os.makedirs(KEY_DIR, exist_ok=True)
    sk = SigningKey.generate(curve=SECP256k1)
    vk = sk.get_verifying_key()
    with open(PRIV_FILE, "wb") as f: f.write(sk.to_pem())
    with open(PUB_FILE, "wb") as f: f.write(vk.to_pem())
    address = public_key_to_address(vk.to_string().hex())
    print("Wallet generated!\nAddress:", address)
    return address

def load_private_key():
    with open(PRIV_FILE, "rb") as f:
        return SigningKey.from_pem(f.read())

def load_public_key():
    with open(PUB_FILE, "rb") as f:
        return VerifyingKey.from_pem(f.read())

def sign_message(message: str) -> str:
    sk = load_private_key()
    sig = sk.sign(message.encode())
    return base64.b64encode(sig).decode()

def verify_signature(pubkey_hex: str, message: str, signature_b64: str) -> bool:
    vk = VerifyingKey.from_string(bytes.fromhex(pubkey_hex), curve=SECP256k1)
    sig = base64.b64decode(signature_b64)
    return vk.verify(sig, message.encode())

def public_key_to_address(pubkey_hex: str) -> str:
    sha = hashlib.sha256(bytes.fromhex(pubkey_hex)).digest()
    h = RIPEMD160.new(sha).digest()
    # prepend version byte 0x00, compute checksum
    pref = b'\x00' + h
    chk = hashlib.sha256(hashlib.sha256(pref).digest()).digest()[:4]
    return base58.b58encode(pref + chk).decode()

class Wallet:
    def __init__(self):
        if not os.path.exists(PRIV_FILE):
            raise FileNotFoundError("No wallet found, run wallet.py to generate.")
        self.sk = load_private_key()
        self.vk = self.sk.get_verifying_key()
        self.pub_hex = self.vk.to_string().hex()
        self.address = public_key_to_address(self.pub_hex)

    def sign(self, message: str) -> str:
        return sign_message(message)

    def get_public_key_hex(self) -> str:
        return self.pub_hex
