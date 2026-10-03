import os
import json
import base64
from typing import Optional, Dict, Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.session_crypto import (
    generate_session_key,
    derive_key,
    derive_field_key,
    encrypt_field,
    decrypt_field,
)

from app.core.pqc import (
    encapsulate,
    decapsulate,
)

from app.core.key_manager import (
    decrypt_private_key,
)


# Domain-separated context for KEM-DEM key wrapping
KEM_DEM_CONTEXT = b"pqc-healthcare-kem-dem-v1"

# Role-Based Granular Access Control (PQC-FLGC)
ROLE_FIELD_PERMISSIONS = {
    "doctor": {"diagnosis", "symptoms", "treatment", "prescription", "doctor_notes"},
    "admin": {"diagnosis", "symptoms", "treatment", "prescription", "doctor_notes"},
    "nurse": {"symptoms", "prescription"},
    "pharmacist": {"prescription"},
    "billing": set(),  # Billing has access only to metadata, clinical fields are restricted
}


class Mediator:
    """
    Central cryptographic service implementing:
    1. Post-Quantum KEM-DEM Hybrid Encryption (ML-KEM-768 + AES-256-GCM)
    2. HKDF-SHA256 Field-Level Sub-Key Derivation (PQC-FLGC)
    3. Associated Data (AAD) Context Binding to prevent ciphertext splicing
    4. Fine-grained Role-Based Clinical Field Filtering
    5. Zero-Payload-Decryption Key Delegation
    """

    @staticmethod
    def encrypt_medical_record(
        medical_record,
        doctor_public_key: bytes,
    ) -> Dict[str, str]:
        # 1. Generate one AES-256 root session key for the record
        session_key = generate_session_key()
        patient_id = getattr(medical_record, "patient_id", 0)

        # 2. Derive field-specific keys and encrypt each field with AAD binding
        fields_data = {
            "diagnosis": getattr(medical_record, "diagnosis", "") or "",
            "symptoms": getattr(medical_record, "symptoms", "") or "",
            "treatment": getattr(medical_record, "treatment", "") or "",
            "prescription": getattr(medical_record, "prescription", "") or "",
            "doctor_notes": getattr(medical_record, "doctor_notes", "") or "",
        }

        encrypted_fields = {}
        for field_name, plaintext in fields_data.items():
            field_key = derive_field_key(session_key, field_name, patient_id)
            aad = f"patient:{patient_id}:field:{field_name}".encode("utf-8")
            ciphertext, nonce = encrypt_field(plaintext, field_key, associated_data=aad)
            encrypted_fields[field_name] = {
                "ciphertext": ciphertext,
                "nonce": nonce,
            }

        # Store encrypted fields as JSON
        encrypted_record_json = json.dumps(encrypted_fields)

        # 3. Post-quantum ML-KEM-768 encapsulation
        kem_ciphertext, shared_secret = encapsulate(doctor_public_key)

        # 4. Standard HKDF derivation for the Key Encryption Key (KEK)
        kek = derive_key(shared_secret, context_info=KEM_DEM_CONTEXT)

        # 5. Encrypt AES root session key using KEK
        aes_kek = AESGCM(kek)
        aes_key_nonce = os.urandom(12)
        encrypted_session_key = aes_kek.encrypt(
            aes_key_nonce,
            session_key,
            f"kem-session-patient:{patient_id}".encode("utf-8"),
        )

        return {
            "encrypted_record": encrypted_record_json,
            "kem_ciphertext": base64.b64encode(kem_ciphertext).decode("utf-8"),
            "encrypted_aes_key": base64.b64encode(encrypted_session_key).decode("utf-8"),
            "aes_key_nonce": base64.b64encode(aes_key_nonce).decode("utf-8"),
        }

    @staticmethod
    def recover_session_key(
        kem_ciphertext: str,
        encrypted_aes_key: str,
        aes_key_nonce: str,
        private_key: bytes,
        patient_id: Optional[int] = None,
    ) -> bytes:
        """
        Recover the 256-bit AES session key using ML-KEM decapsulation.
        """
        shared_secret = decapsulate(
            base64.b64decode(kem_ciphertext),
            private_key,
        )
        kek = derive_key(shared_secret, context_info=KEM_DEM_CONTEXT)
        aes_kek = AESGCM(kek)

        aad = f"kem-session-patient:{patient_id}".encode("utf-8") if patient_id is not None else None
        try:
            session_key = aes_kek.decrypt(
                base64.b64decode(aes_key_nonce),
                base64.b64decode(encrypted_aes_key),
                aad,
            )
        except Exception:
            # Fallback for legacy records created without AAD
            session_key = aes_kek.decrypt(
                base64.b64decode(aes_key_nonce),
                base64.b64decode(encrypted_aes_key),
                None,
            )
        return session_key

    @staticmethod
    def re_encapsulate_for_recipient(
        session_key: bytes,
        recipient_public_key: bytes,
        patient_id: Optional[int] = None,
    ) -> Dict[str, str]:
        """
        Zero-Payload-Decryption Key Delegation:
        Re-encapsulate only the 256-bit AES session key for a newly authorized doctor
        using ML-KEM-768. The medical data payload remains completely untouched.
        """
        kem_ciphertext, shared_secret = encapsulate(recipient_public_key)
        kek = derive_key(shared_secret, context_info=KEM_DEM_CONTEXT)
        aes_kek = AESGCM(kek)
        nonce = os.urandom(12)
        aad = f"kem-session-patient:{patient_id}".encode("utf-8") if patient_id is not None else None

        encrypted_session_key = aes_kek.encrypt(nonce, session_key, aad)
        return {
            "kem_ciphertext": base64.b64encode(kem_ciphertext).decode("utf-8"),
            "encrypted_aes_key": base64.b64encode(encrypted_session_key).decode("utf-8"),
            "aes_key_nonce": base64.b64encode(nonce).decode("utf-8"),
        }

    @staticmethod
    def decrypt_medical_record(
        record,
        encrypted_private_key: str,
        key_nonce: str,
        user_role: str = "doctor",
        kem_ciphertext_override: Optional[str] = None,
        encrypted_aes_key_override: Optional[str] = None,
        aes_key_nonce_override: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Decrypt medical record with fine-grained field-level role gating.
        """
        # 1. Decrypt doctor's ML-KEM private key
        private_key = decrypt_private_key(
            encrypted_private_key,
            key_nonce,
        )

        # 2. Recover AES session key (supports delegated KEM parameters if provided)
        kem_ct = kem_ciphertext_override or record.kem_ciphertext
        enc_aes = encrypted_aes_key_override or record.encrypted_aes_key
        aes_nonce = aes_key_nonce_override or record.aes_key_nonce

        session_key = Mediator.recover_session_key(
            kem_ciphertext=kem_ct,
            encrypted_aes_key=enc_aes,
            aes_key_nonce=aes_nonce,
            private_key=private_key,
            patient_id=getattr(record, "patient_id", None),
        )

        # 3. Load encrypted fields
        encrypted_record = json.loads(record.encrypted_record)
        allowed_fields = ROLE_FIELD_PERMISSIONS.get(user_role.lower(), set())

        patient_id = getattr(record, "patient_id", 0)
        decrypted = {}

        for field, value in encrypted_record.items():
            if field not in allowed_fields:
                decrypted[field] = "[RESTRICTED: Insufficient permissions for role]"
                continue

            field_key = derive_field_key(session_key, field, patient_id)
            aad = f"patient:{patient_id}:field:{field}".encode("utf-8")
            try:
                decrypted[field] = decrypt_field(
                    value["ciphertext"],
                    value["nonce"],
                    field_key,
                    associated_data=aad,
                )
            except Exception:
                # Fallback for backward compatibility with legacy records
                decrypted[field] = decrypt_field(
                    value["ciphertext"],
                    value["nonce"],
                    session_key,
                    associated_data=None,
                )

        return {
            "id": record.id,
            "patient_id": record.patient_id,
            "created_by": record.created_by,
            "created_at": record.created_at,
            "medical_data": decrypted,
        }