import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.pqc import generate_keypair


MASTER_KEY = base64.b64decode(os.getenv("MASTER_KEY"))


def encrypt_private_key(private_key: bytes):
    """
    Encrypt the ML-KEM private key using AES-256-GCM.
    """

    aes = AESGCM(MASTER_KEY)

    nonce = os.urandom(12)

    encrypted = aes.encrypt(
        nonce,
        private_key,
        None
    )

    return (
        base64.b64encode(encrypted).decode(),
        base64.b64encode(nonce).decode(),
    )


def decrypt_private_key(encrypted_key: str, nonce: str):
    """
    Decrypt the ML-KEM private key.
    """

    aes = AESGCM(MASTER_KEY)

    decrypted = aes.decrypt(
        base64.b64decode(nonce),
        base64.b64decode(encrypted_key),
        None
    )

    return decrypted


def create_user_keypair():
    """
    Generate an ML-KEM key pair and encrypt the private key.
    """

    public_key, private_key = generate_keypair()

    encrypted_private_key, nonce = encrypt_private_key(private_key)

    return (
        base64.b64encode(public_key).decode(),
        encrypted_private_key,
        nonce,
    )