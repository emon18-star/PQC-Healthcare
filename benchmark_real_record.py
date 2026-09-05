import base64
import statistics
import time

from dotenv import load_dotenv

load_dotenv(".env")

from app.database.database import SessionLocal
from app.models.user import User
from app.models.medical_record import MedicalRecord
from app.core.mediator import Mediator


ITERATIONS = 1000
RECORD_ID = 10


def benchmark(function, iterations=ITERATIONS):
    times = []

    for _ in range(iterations):
        start = time.perf_counter()

        function()

        end = time.perf_counter()

        times.append((end - start) * 1000)

    return {
        "average": statistics.mean(times),
        "median": statistics.median(times),
        "minimum": min(times),
        "maximum": max(times),
        "std_dev": statistics.stdev(times) if len(times) > 1 else 0,
    }


def print_result(title, result):
    print(f"\n## {title}")
    print(f"Iterations      : {ITERATIONS}")
    print(f"Average         : {result['average']:.4f} ms")
    print(f"Median          : {result['median']:.4f} ms")
    print(f"Minimum         : {result['minimum']:.4f} ms")
    print(f"Maximum         : {result['maximum']:.4f} ms")
    print(f"Std deviation   : {result['std_dev']:.4f} ms")


def main():

    print("=" * 65)
    print("PQC HEALTHCARE SYSTEM")
    print("REAL DATABASE MEDICAL RECORD")
    print("ENCRYPTION + DECRYPTION BENCHMARK")
    print("=" * 65)

    db = SessionLocal()

    try:

        # ==========================================================
        # LOAD REAL MEDICAL RECORD
        # ==========================================================

        record = (
            db.query(MedicalRecord)
            .filter(MedicalRecord.id == RECORD_ID)
            .first()
        )

        if record is None:
            print(f"\nERROR: Medical record {RECORD_ID} not found.")
            return

        doctor = (
            db.query(User)
            .filter(User.id == record.created_by)
            .first()
        )

        if doctor is None:
            print("\nERROR: Creator doctor not found.")
            return

        if doctor.public_key is None:
            print("\nERROR: Doctor has no public key.")
            return

        if doctor.private_key is None:
            print("\nERROR: Doctor has no private key.")
            return

        if doctor.key_nonce is None:
            print("\nERROR: Doctor key nonce is missing.")
            return

        print("\n## Selected Medical Record")
        print(f"\nRecord ID : {record.id}")
        print(f"Patient ID : {record.patient_id}")
        print(f"Created By : {record.created_by}")
        print(f"Doctor     : {doctor.username}")

        # ==========================================================
        # DECRYPT REAL RECORD
        # ==========================================================

        print("\nTesting real-record decryption...")

        try:

            decrypted = Mediator.decrypt_medical_record(
                record,
                doctor.private_key,
                doctor.key_nonce,
            )

            print("Decryption test: SUCCESS")

            print("\n## Recovered Medical Data")

            medical_data = decrypted.get("medical_data", {})

            for field, value in medical_data.items():
                print(f"{field}: {value}")

        except Exception as e:

            print("Decryption test: FAILED")
            print(f"Error: {type(e).__name__}: {e}")
            return

        # ==========================================================
        # PREPARE ORIGINAL DATA FOR ENCRYPTION TEST
        # ==========================================================

        print("\n" + "=" * 65)
        print("ENCRYPTION TEST")
        print("=" * 65)

        class MedicalRecordData:
            pass

        medical_record_data = MedicalRecordData()

        medical_record_data.patient_id = record.patient_id

        medical_record_data.diagnosis = medical_data.get(
            "diagnosis",
            ""
        )

        medical_record_data.symptoms = medical_data.get(
            "symptoms",
            ""
        )

        medical_record_data.treatment = medical_data.get(
            "treatment",
            ""
        )

        medical_record_data.prescription = medical_data.get(
            "prescription",
            ""
        )

        medical_record_data.doctor_notes = medical_data.get(
            "doctor_notes",
            ""
        )

        doctor_public_key = base64.b64decode(
            doctor.public_key
        )

        # ==========================================================
        # TEST ENCRYPTION
        # ==========================================================

        try:

            encrypted = Mediator.encrypt_medical_record(
                medical_record_data,
                doctor_public_key,
            )

            print("\nEncryption test: SUCCESS")

            print("\nGenerated encrypted components:")

            print(
                "Encrypted record      :",
                encrypted["encrypted_record"] is not None
            )

            print(
                "KEM ciphertext        :",
                encrypted["kem_ciphertext"] is not None
            )

            print(
                "Encrypted AES key     :",
                encrypted["encrypted_aes_key"] is not None
            )

            print(
                "AES key nonce         :",
                encrypted["aes_key_nonce"] is not None
            )

        except Exception as e:

            print("\nEncryption test: FAILED")
            print(f"Error: {type(e).__name__}: {e}")
            return

        # ==========================================================
        # VERIFY ENCRYPTION -> DECRYPTION
        # ==========================================================

        print("\n" + "=" * 65)
        print("ENCRYPTION -> DECRYPTION VERIFICATION")
        print("=" * 65)

        class EncryptedRecord:
            pass

        test_record = EncryptedRecord()

        test_record.id = record.id
        test_record.patient_id = record.patient_id
        test_record.created_by = record.created_by
        test_record.created_at = record.created_at

        test_record.encrypted_record = encrypted[
            "encrypted_record"
        ]

        test_record.kem_ciphertext = encrypted[
            "kem_ciphertext"
        ]

        test_record.encrypted_aes_key = encrypted[
            "encrypted_aes_key"
        ]

        test_record.aes_key_nonce = encrypted[
            "aes_key_nonce"
        ]

        try:

            decrypted_test = Mediator.decrypt_medical_record(
                test_record,
                doctor.private_key,
                doctor.key_nonce,
            )

            recovered_data = decrypted_test["medical_data"]

            encryption_decryption_success = True

            for field in [
                "diagnosis",
                "symptoms",
                "treatment",
                "prescription",
                "doctor_notes",
            ]:

                original = medical_data.get(field, "")
                recovered = recovered_data.get(field, "")

                if original != recovered:
                    encryption_decryption_success = False

                    print(
                        f"\nMismatch in field: {field}"
                    )

            if encryption_decryption_success:

                print(
                    "\nEncryption -> Decryption: SUCCESS"
                )

                print(
                    "Original medical data was successfully "
                    "recovered."
                )

            else:

                print(
                    "\nEncryption -> Decryption: FAILED"
                )

        except Exception as e:

            print(
                "\nEncryption -> Decryption: FAILED"
            )

            print(
                f"Error: {type(e).__name__}: {e}"
            )

            return

        # ==========================================================
        # BENCHMARK ENCRYPTION
        # ==========================================================

        print("\n" + "=" * 65)
        print("PERFORMANCE BENCHMARK")
        print("=" * 65)

        print(
            "\nRunning real-record encryption benchmark..."
        )

        def encrypt_record():

            Mediator.encrypt_medical_record(
                medical_record_data,
                doctor_public_key,
            )

        encryption_result = benchmark(
            encrypt_record
        )

        print_result(
            "Complete Medical Record Encryption",
            encryption_result,
        )

        # ==========================================================
        # BENCHMARK DECRYPTION
        # ==========================================================

        print(
            "\nRunning real-record decryption benchmark..."
        )

        def decrypt_record():

            Mediator.decrypt_medical_record(
                record,
                doctor.private_key,
                doctor.key_nonce,
            )

        decryption_result = benchmark(
            decrypt_record
        )

        print_result(
            "Complete Medical Record Decryption",
            decryption_result,
        )

        # ==========================================================
        # SUMMARY
        # ==========================================================

        print("\n" + "=" * 65)
        print("FINAL PERFORMANCE SUMMARY")
        print("=" * 65)

        print(
            f"\nOperation"
            f"{'Average (ms)':>20}"
            f"{'Median (ms)':>20}"
        )

        print(
            f"{'Medical Record Encryption':<35}"
            f"{encryption_result['average']:>12.4f}"
            f"{encryption_result['median']:>20.4f}"
        )

        print(
            f"{'Medical Record Decryption':<35}"
            f"{decryption_result['average']:>12.4f}"
            f"{decryption_result['median']:>20.4f}"
        )

        total_average = (
            encryption_result["average"]
            + decryption_result["average"]
        )

        print(
            f"\n{'Encryption + Decryption':<35}"
            f"{total_average:>12.4f} ms"
        )

        print("\nBenchmark completed successfully.")

    finally:

        db.close()


if __name__ == "__main__":
    main()