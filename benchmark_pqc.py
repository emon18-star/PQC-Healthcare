import json
import statistics
import time

from dotenv import load_dotenv

load_dotenv(".env")

from app.core.mediator import Mediator

from app.core.pqc import (
    generate_keypair,
    encapsulate,
    decapsulate,
)

from app.core.session_crypto import (
    generate_session_key,
    encrypt_field,
    decrypt_field,
)

from app.core.mediator import Mediator


# ============================================================
# CONFIGURATION
# ============================================================

ITERATIONS = 10000

TEST_TEXT = (
    "Patient has hypertension and diabetes. "
    "Prescribed medication and follow-up treatment."
)


# ============================================================
# HELPER
# ============================================================

def benchmark(function, iterations=ITERATIONS):
    """
    Run a function multiple times and return timing statistics.
    """

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


def print_result(name, result):
    print(f"\n{name}")
    print("-" * 60)

    print(f"Average      : {result['average']:.4f} ms")
    print(f"Median       : {result['median']:.4f} ms")
    print(f"Minimum      : {result['minimum']:.4f} ms")
    print(f"Maximum      : {result['maximum']:.4f} ms")
    print(f"Std deviation: {result['std_dev']:.4f} ms")


# ============================================================
# 1. ML-KEM KEY GENERATION
# ============================================================

print("=" * 70)
print("PQC HEALTHCARE SYSTEM - PERFORMANCE BENCHMARK")
print("=" * 70)

print(f"\nIterations: {ITERATIONS}")


keygen_result = benchmark(
    lambda: generate_keypair()
)

print_result(
    "ML-KEM-768 Key Generation",
    keygen_result
)


# ============================================================
# CREATE KEYPAIR FOR OTHER TESTS
# ============================================================

public_key, private_key = generate_keypair()


# ============================================================
# 2. ML-KEM ENCAPSULATION
# ============================================================

encapsulation_result = benchmark(
    lambda: encapsulate(public_key)
)

print_result(
    "ML-KEM-768 Encapsulation",
    encapsulation_result
)


# ============================================================
# 3. ML-KEM DECAPSULATION
# ============================================================

kem_ciphertext, shared_secret = encapsulate(public_key)


decapsulation_result = benchmark(
    lambda: decapsulate(
        kem_ciphertext,
        private_key
    )
)

print_result(
    "ML-KEM-768 Decapsulation",
    decapsulation_result
)


# ============================================================
# 4. AES SESSION KEY GENERATION
# ============================================================

session_key_result = benchmark(
    lambda: generate_session_key()
)

print_result(
    "AES-256 Session Key Generation",
    session_key_result
)


# ============================================================
# 5. AES FIELD ENCRYPTION
# ============================================================

aes_key = generate_session_key()


encryption_result = benchmark(
    lambda: encrypt_field(
        TEST_TEXT,
        aes_key
    )
)

print_result(
    "AES-256-GCM Field Encryption",
    encryption_result
)


# ============================================================
# 6. AES FIELD DECRYPTION
# ============================================================

encrypted_text, nonce = encrypt_field(
    TEST_TEXT,
    aes_key
)


decryption_result = benchmark(
    lambda: decrypt_field(
        encrypted_text,
        nonce,
        aes_key
    )
)

print_result(
    "AES-256-GCM Field Decryption",
    decryption_result
)


# ============================================================
# 7. MEDICAL RECORD ENCRYPTION
# ============================================================

class TestMedicalRecord:
    """
    Test object matching the fields expected by Mediator.
    """

    diagnosis = (
        "Hypertension and Type 2 Diabetes"
    )

    symptoms = (
        "Headache, dizziness and fatigue"
    )

    treatment = (
        "Lifestyle modification and medication"
    )

    prescription = (
        "Metformin 500mg twice daily"
    )

    doctor_notes = (
        "Patient should return after four weeks."
    )


medical_record = TestMedicalRecord()


medical_encryption_result = benchmark(
    lambda: Mediator.encrypt_medical_record(
        medical_record,
        public_key
    )
)

print_result(
    "Complete Medical Record Encryption",
    medical_encryption_result
)


# ============================================================
# CREATE ENCRYPTED RECORD FOR DECRYPTION TEST
# ============================================================

encrypted_record_data = Mediator.encrypt_medical_record(
    medical_record,
    public_key
)


# ============================================================
# CREATE A TEST RECORD OBJECT
# ============================================================

class TestDatabaseRecord:

    id = 1

    patient_id = 1

    created_by = 1

    created_at = None

    encrypted_record = (
        encrypted_record_data["encrypted_record"]
    )

    kem_ciphertext = (
        encrypted_record_data["kem_ciphertext"]
    )

    encrypted_aes_key = (
        encrypted_record_data["encrypted_aes_key"]
    )

    aes_key_nonce = (
        encrypted_record_data["aes_key_nonce"]
    )


test_record = TestDatabaseRecord()


# ============================================================
# 8. MEDICAL RECORD DECRYPTION
# ============================================================

# IMPORTANT:
# Your Mediator expects the private key to be encrypted
# with MASTER_KEY.
#
# Therefore we use the key_manager exactly as your
# application does.

from app.core.key_manager import encrypt_private_key


encrypted_private_key, private_key_nonce = (
    encrypt_private_key(private_key)
)


medical_decryption_result = benchmark(
    lambda: Mediator.decrypt_medical_record(
        test_record,
        encrypted_private_key,
        private_key_nonce
    )
)

print_result(
    "Complete Medical Record Decryption",
    medical_decryption_result
)


# ============================================================
# 9. SUMMARY TABLE
# ============================================================

print("\n")
print("=" * 70)
print("SUMMARY")
print("=" * 70)

results = [
    (
        "ML-KEM-768 Key Generation",
        keygen_result
    ),
    (
        "ML-KEM-768 Encapsulation",
        encapsulation_result
    ),
    (
        "ML-KEM-768 Decapsulation",
        decapsulation_result
    ),
    (
        "AES-256 Session Key Generation",
        session_key_result
    ),
    (
        "AES-256-GCM Encryption",
        encryption_result
    ),
    (
        "AES-256-GCM Decryption",
        decryption_result
    ),
    (
        "Medical Record Encryption",
        medical_encryption_result
    ),
    (
        "Medical Record Decryption",
        medical_decryption_result
    ),
]


print(
    f"\n{'Operation':<40}"
    f"{'Average (ms)':>15}"
    f"{'Median (ms)':>15}"
)

print("-" * 70)

for name, result in results:

    print(
        f"{name:<40}"
        f"{result['average']:>15.4f}"
        f"{result['median']:>15.4f}"
    )


print("\n")
print("=" * 70)
print("BENCHMARK COMPLETE")
print("=" * 70)