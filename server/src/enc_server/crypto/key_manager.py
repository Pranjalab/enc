import os
import json
import base64
from pathlib import Path
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
from enc_server.config import ENC_KEYS_FILE
from enc_server.crypto.encrypt import encrypt_bytes
from enc_server.crypto.decrypt import decrypt_bytes

# Constants for KDF
SALT_SIZE = 16
KEY_LEN = 32  # AES-256
N = 16384
R = 8
P = 1

def generate_salt() -> bytes:
    """Generate a random salt."""
    return os.urandom(SALT_SIZE)

def derive_key(password: str, salt: bytes) -> bytes:
    """
    Derive a 32-byte key from a password using Scrypt.
    """
    kdf = Scrypt(
        salt=salt,
        length=KEY_LEN,
        n=N,
        r=R,
        p=P,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

def generate_project_key() -> bytes:
    """Generate a random 32-byte AES key."""
    return os.urandom(KEY_LEN)

def save_master_key(master_key: bytes, password: str):
    """
    Encrypt and save the master key using the password.
    Format:
    {
        "salt": <hex>,
        "encrypted_key": <hex (nonce+ciphertext)>
    }
    """
    salt = generate_salt()
    derived_key = derive_key(password, salt)
    encrypted_master_key = encrypt_bytes(master_key, derived_key)
    
    data = {
        "salt": salt.hex(),
        "encrypted_key": encrypted_master_key.hex()
    }
    
    # Ensure parent dir exists
    ENC_KEYS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(ENC_KEYS_FILE, "w") as f:
        json.dump(data, f)

def load_master_key(password: str) -> bytes:
    """
    Load and decrypt the master key.
    Raises ValueError if password is incorrect (decryption fails).
    """
    if not ENC_KEYS_FILE.exists():
        raise FileNotFoundError("No master key found. Run 'enc init' first.")
        
    with open(ENC_KEYS_FILE, "r") as f:
        data = json.load(f)
        
    salt = bytes.fromhex(data["salt"])
    encrypted_key = bytes.fromhex(data["encrypted_key"])
    
    derived_key = derive_key(password, salt)
    
    try:
        return decrypt_bytes(encrypted_key, derived_key)
    except Exception:
        raise ValueError("Invalid password or corrupted key file.")
