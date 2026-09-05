import os
import base64

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def generate_session_key():
    """
    Generate one AES-256 session key.
    """
    return AESGCM.generate_key(bit_length=256)


def encrypt_field(
    plaintext: str,
    session_key: bytes
):
    aes = AESGCM(session_key)

    nonce = os.urandom(12)

    ciphertext = aes.encrypt(
        nonce,
        plaintext.encode(),
        None
    )

    return (
        base64.b64encode(ciphertext).decode(),
        base64.b64encode(nonce).decode(),
    )


def decrypt_field(
    ciphertext: str,
    nonce: str,
    session_key: bytes
):
    aes = AESGCM(session_key)

    plaintext = aes.decrypt(
        base64.b64decode(nonce),
        base64.b64decode(ciphertext),
        None,
    )

    return plaintext.decode()