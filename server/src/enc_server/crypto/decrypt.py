from cryptography.hazmat.primitives.ciphers.aead import AESGCM

NONCE_SIZE = 12

def decrypt_bytes(data: bytes, key: bytes) -> bytes:
    """
    Decrypt data using AES-GCM.
    Expects data to be nonce + ciphertext.
    """
    if len(data) < NONCE_SIZE:
        raise ValueError("Data too short to contain nonce")
    
    nonce = data[:NONCE_SIZE]
    ciphertext = data[NONCE_SIZE:]
    
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, None)

def decrypt_string(data: bytes, key: bytes) -> str:
    """Decrypt to string."""
    return decrypt_bytes(data, key).decode('utf-8')
