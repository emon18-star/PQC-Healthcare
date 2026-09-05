import os
import json
import base64

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.session_crypto import (
    generate_session_key,
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


class Mediator:
    """
    Central cryptographic service.

    All encryption and decryption of medical
    records passes through this class.
    """

    @staticmethod
    def encrypt_medical_record(
        medical_record,
        doctor_public_key: bytes,
    ):
        # Generate one AES session key
        session_key = generate_session_key()

        # Encrypt each medical field
        diagnosis, diagnosis_nonce = encrypt_field(
            medical_record.diagnosis,
            session_key,
        )

        symptoms, symptoms_nonce = encrypt_field(
            medical_record.symptoms,
            session_key,
        )

        treatment, treatment_nonce = encrypt_field(
            medical_record.treatment,
            session_key,
        )

        prescription, prescription_nonce = encrypt_field(
            medical_record.prescription or "",
            session_key,
        )

        doctor_notes, doctor_notes_nonce = encrypt_field(
            medical_record.doctor_notes or "",
            session_key,
        )

        # Store encrypted fields as JSON
        encrypted_record = json.dumps(
            {
                "diagnosis": {
                    "ciphertext": diagnosis,
                    "nonce": diagnosis_nonce,
                },
                "symptoms": {
                    "ciphertext": symptoms,
                    "nonce": symptoms_nonce,
                },
                "treatment": {
                    "ciphertext": treatment,
                    "nonce": treatment_nonce,
                },
                "prescription": {
                    "ciphertext": prescription,
                    "nonce": prescription_nonce,
                },
                "doctor_notes": {
                    "ciphertext": doctor_notes,
                    "nonce": doctor_notes_nonce,
                },
            }
        )

        # ML-KEM encapsulation
        kem_ciphertext, shared_secret = encapsulate(
            doctor_public_key
        )

        # Encrypt AES session key using shared secret
        aes = AESGCM(shared_secret[:32])

        aes_key_nonce = os.urandom(12)

        encrypted_session_key = aes.encrypt(
            aes_key_nonce,
            session_key,
            None,
        )

        return {
            "encrypted_record": encrypted_record,
            "kem_ciphertext": base64.b64encode(
                kem_ciphertext
            ).decode(),
            "encrypted_aes_key": base64.b64encode(
                encrypted_session_key
            ).decode(),
            "aes_key_nonce": base64.b64encode(
                aes_key_nonce
            ).decode(),
        }

    @staticmethod
    def decrypt_medical_record(
        record,
        encrypted_private_key: str,
        key_nonce: str,
    ):
        # Decrypt doctor's ML-KEM private key
        private_key = decrypt_private_key(
            encrypted_private_key,
            key_nonce,
        )

        # Recover shared secret
        shared_secret = decapsulate(
            base64.b64decode(record.kem_ciphertext),
            private_key,
        )

        # Recover AES session key
        aes = AESGCM(shared_secret[:32])

        session_key = aes.decrypt(
            base64.b64decode(record.aes_key_nonce),
            base64.b64decode(record.encrypted_aes_key),
            None,
        )

        # Load encrypted medical record
        encrypted_record = json.loads(
            record.encrypted_record
        )

        decrypted = {}

        for field, value in encrypted_record.items():
            decrypted[field] = decrypt_field(
                value["ciphertext"],
                value["nonce"],
                session_key,
            )

        return {
            "id": record.id,
            "patient_id": record.patient_id,
            "created_by": record.created_by,
            "created_at": record.created_at,
            "medical_data": decrypted,
        }