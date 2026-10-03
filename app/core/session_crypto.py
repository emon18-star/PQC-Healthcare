import os
import base64
from typing import Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes


def generate_session_key() -> bytes:
    """
    Generate one AES-256 session key (32 bytes).
    """
    return AESGCM.generate_key(bit_length=256)


def derive_key(
    source_key: bytes,
    context_info: bytes,
    salt: Optional[bytes] = None,
    length: int = 32,
) -> bytes:
    """
    Cryptographically derive sub-keys from a root key using HKDF-SHA256.
    Ensures uniform entropy and domain separation.
    """
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=length,
        salt=salt,
        info=context_info,
    )
    return hkdf.derive(source_key)


def derive_field_key(
    root_key: bytes,
    field_name: str,
    patient_id: Optional[int] = None,
) -> bytes:
    """
    Derive a dedicated AES-256 key for a specific clinical field.
    Includes field_name and patient context to guarantee field-level domain separation.
    """
    context = f"pqc-field:{field_name}".encode()
    if patient_id is not None:
        context += f":patient:{patient_id}".encode()
    return derive_key(root_key, context_info=context)


def encrypt_field(
    plaintext: str,
    field_key: bytes,
    associated_data: Optional[bytes] = None,
):
    """
    Encrypt plaintext using AES-256-GCM with a fresh 12-byte random nonce
    and optional authenticated associated data (AAD) to prevent ciphertext splicing.
    """
    aes = AESGCM(field_key)
    nonce = os.urandom(12)

    ciphertext = aes.encrypt(
        nonce,
        plaintext.encode("utf-8"),
        associated_data,
    )

    return (
        base64.b64encode(ciphertext).decode("utf-8"),
        base64.b64encode(nonce).decode("utf-8"),
    )


def decrypt_field(
    ciphertext: str,
    nonce: str,
    field_key: bytes,
    associated_data: Optional[bytes] = None,
) -> str:
    """
    Decrypt AES-256-GCM ciphertext and authenticate against associated data.
    """
    aes = AESGCM(field_key)

    plaintext = aes.decrypt(
        base64.b64decode(nonce),
        base64.b64decode(ciphertext),
        associated_data,
    )

    return plaintext.decode("utf-8")