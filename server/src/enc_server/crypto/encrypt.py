import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

NONCE_SIZE = 12

def encrypt_bytes(data: bytes, key: bytes) -> bytes:
    """
    Encrypt data using AES-GCM.
    Returns: nonce + ciphertext (which includes tag)
    """
    aesgcm = AESGCM(key)
    nonce = os.urandom(NONCE_SIZE)
    ciphertext = aesgcm.encrypt(nonce, data, None)
    return nonce + ciphertext

def encrypt_string(text: str, key: bytes) -> bytes:
    """Encrypt a string."""
    return encrypt_bytes(text.encode('utf-8'), key)
