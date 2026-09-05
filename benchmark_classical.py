import os
import time
import statistics
import base64

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


# ============================================================
# CONFIGURATION
# ============================================================

ITERATIONS = 1000


# ============================================================
# TEST MEDICAL DATA
# ============================================================

MEDICAL_DATA = {
    "diagnosis": "string",
    "symptoms": "string",
    "treatment": "string",
    "prescription": "string",
    "doctor_notes": "string",
}


# ============================================================
# STATISTICS
# ============================================================

def calculate_statistics(times):

    return {
        "average": statistics.mean(times),
        "median": statistics.median(times),
        "minimum": min(times),
        "maximum": max(times),
        "stddev": (
            statistics.stdev(times)
            if len(times) > 1
            else 0
        ),
    }


def print_statistics(stats):

    print(
        f"Average      : "
        f"{stats['average']:.4f} ms"
    )

    print(
        f"Median       : "
        f"{stats['median']:.4f} ms"
    )

    print(
        f"Minimum      : "
        f"{stats['minimum']:.4f} ms"
    )

    print(
        f"Maximum      : "
        f"{stats['maximum']:.4f} ms"
    )

    print(
        f"Std deviation: "
        f"{stats['stddev']:.4f} ms"
    )


# ============================================================
# RSA-2048 KEY GENERATION
# ============================================================

def benchmark_rsa_key_generation():

    times = []

    print()
    print("## RSA-2048 Key Generation")
    print()

    for i in range(ITERATIONS):

        start = time.perf_counter()

        rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        end = time.perf_counter()

        times.append(
            (end - start) * 1000
        )

    stats = calculate_statistics(times)

    print_statistics(stats)

    return stats


# ============================================================
# CREATE RSA KEYPAIR FOR OTHER TESTS
# ============================================================

print()
print("Generating RSA-2048 key pair for benchmark...")
print()

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

public_key = private_key.public_key()

print("RSA key pair generated successfully.")


# ============================================================
# RSA-2048 KEY WRAPPING
# ============================================================

def benchmark_rsa_encryption():

    times = []

    # Generate one AES session key
    session_key = AESGCM.generate_key(
        bit_length=256
    )

    print()
    print("## RSA-2048 Session-Key Encryption")
    print()

    for i in range(ITERATIONS):

        start = time.perf_counter()

        public_key.encrypt(
            session_key,
            padding.OAEP(
                mgf=padding.MGF1(
                    algorithm=hashes.SHA256()
                ),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

        end = time.perf_counter()

        times.append(
            (end - start) * 1000
        )

    stats = calculate_statistics(times)

    print_statistics(stats)

    return stats


# ============================================================
# RSA-2048 KEY UNWRAPPING
# ============================================================

def benchmark_rsa_decryption():

    times = []

    session_key = AESGCM.generate_key(
        bit_length=256
    )

    encrypted_key = public_key.encrypt(
        session_key,
        padding.OAEP(
            mgf=padding.MGF1(
                algorithm=hashes.SHA256()
            ),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    print()
    print("## RSA-2048 Session-Key Decryption")
    print()

    for i in range(ITERATIONS):

        start = time.perf_counter()

        private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(
                    algorithm=hashes.SHA256()
                ),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

        end = time.perf_counter()

        times.append(
            (end - start) * 1000
        )

    stats = calculate_statistics(times)

    print_statistics(stats)

    return stats


# ============================================================
# AES-256 SESSION KEY GENERATION
# ============================================================

def benchmark_aes_key_generation():

    times = []

    print()
    print("## AES-256 Session Key Generation")
    print()

    for i in range(ITERATIONS):

        start = time.perf_counter()

        AESGCM.generate_key(
            bit_length=256
        )

        end = time.perf_counter()

        times.append(
            (end - start) * 1000
        )

    stats = calculate_statistics(times)

    print_statistics(stats)

    return stats


# ============================================================
# AES-256-GCM FIELD ENCRYPTION
# ============================================================

def benchmark_aes_encryption():

    times = []

    session_key = AESGCM.generate_key(
        bit_length=256
    )

    plaintext = "string".encode()

    print()
    print("## AES-256-GCM Field Encryption")
    print()

    for i in range(ITERATIONS):

        aes = AESGCM(session_key)

        nonce = os.urandom(12)

        start = time.perf_counter()

        aes.encrypt(
            nonce,
            plaintext,
            None,
        )

        end = time.perf_counter()

        times.append(
            (end - start) * 1000
        )

    stats = calculate_statistics(times)

    print_statistics(stats)

    return stats


# ============================================================
# AES-256-GCM FIELD DECRYPTION
# ============================================================

def benchmark_aes_decryption():

    times = []

    session_key = AESGCM.generate_key(
        bit_length=256
    )

    aes = AESGCM(session_key)

    nonce = os.urandom(12)

    ciphertext = aes.encrypt(
        nonce,
        b"string",
        None,
    )

    print()
    print("## AES-256-GCM Field Decryption")
    print()

    for i in range(ITERATIONS):

        start = time.perf_counter()

        aes.decrypt(
            nonce,
            ciphertext,
            None,
        )

        end = time.perf_counter()

        times.append(
            (end - start) * 1000
        )

    stats = calculate_statistics(times)

    print_statistics(stats)

    return stats


# ============================================================
# COMPLETE CLASSICAL MEDICAL RECORD ENCRYPTION
# ============================================================

def classical_encrypt_record():

    # Generate AES-256 session key
    session_key = AESGCM.generate_key(
        bit_length=256
    )

    aes = AESGCM(session_key)

    encrypted_fields = {}

    # Encrypt all medical fields

    for field, value in MEDICAL_DATA.items():

        nonce = os.urandom(12)

        ciphertext = aes.encrypt(
            nonce,
            value.encode(),
            None,
        )

        encrypted_fields[field] = {
            "ciphertext": ciphertext,
            "nonce": nonce,
        }

    # RSA encrypt/wrap AES session key

    encrypted_session_key = public_key.encrypt(
        session_key,
        padding.OAEP(
            mgf=padding.MGF1(
                algorithm=hashes.SHA256()
            ),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    return (
        encrypted_fields,
        encrypted_session_key,
    )


def benchmark_complete_classical_encryption():

    times = []

    print()
    print("## Complete Classical Medical Record Encryption")
    print()

    for i in range(ITERATIONS):

        start = time.perf_counter()

        classical_encrypt_record()

        end = time.perf_counter()

        times.append(
            (end - start) * 1000
        )

    stats = calculate_statistics(times)

    print_statistics(stats)

    return stats


# ============================================================
# COMPLETE CLASSICAL MEDICAL RECORD DECRYPTION
# ============================================================

encrypted_fields, encrypted_session_key = (
    classical_encrypt_record()
)


def classical_decrypt_record():

    # RSA decrypt/wrap recovery

    session_key = private_key.decrypt(
        encrypted_session_key,
        padding.OAEP(
            mgf=padding.MGF1(
                algorithm=hashes.SHA256()
            ),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    aes = AESGCM(session_key)

    decrypted = {}

    for field, value in encrypted_fields.items():

        plaintext = aes.decrypt(
            value["nonce"],
            value["ciphertext"],
            None,
        )

        decrypted[field] = plaintext.decode()

    return decrypted


def benchmark_complete_classical_decryption():

    times = []

    print()
    print("## Complete Classical Medical Record Decryption")
    print()

    for i in range(ITERATIONS):

        start = time.perf_counter()

        classical_decrypt_record()

        end = time.perf_counter()

        times.append(
            (end - start) * 1000
        )

    stats = calculate_statistics(times)

    print_statistics(stats)

    return stats


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 65)
    print("CLASSICAL HEALTHCARE CRYPTOGRAPHY BENCHMARK")
    print("=" * 65)
    print()

    print(
        f"Iterations: {ITERATIONS}"
    )

    print()

    # --------------------------------------------------------
    # RSA
    # --------------------------------------------------------

    rsa_keygen = benchmark_rsa_key_generation()

    rsa_encrypt = benchmark_rsa_encryption()

    rsa_decrypt = benchmark_rsa_decryption()

    # --------------------------------------------------------
    # AES
    # --------------------------------------------------------

    aes_keygen = benchmark_aes_key_generation()

    aes_encrypt = benchmark_aes_encryption()

    aes_decrypt = benchmark_aes_decryption()

    # --------------------------------------------------------
    # Complete record
    # --------------------------------------------------------

    record_encrypt = (
        benchmark_complete_classical_encryption()
    )

    record_decrypt = (
        benchmark_complete_classical_decryption()
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print()
    print("=" * 65)
    print("FINAL CLASSICAL CRYPTOGRAPHY RESULTS")
    print("=" * 65)
    print()

    print(
        "Operation"
        "                              Average (ms)"
        "       Median (ms)"
    )

    results = [
        (
            "RSA-2048 Key Generation",
            rsa_keygen,
        ),
        (
            "RSA-2048 Session-Key Encryption",
            rsa_encrypt,
        ),
        (
            "RSA-2048 Session-Key Decryption",
            rsa_decrypt,
        ),
        (
            "AES-256 Session Key Generation",
            aes_keygen,
        ),
        (
            "AES-256-GCM Encryption",
            aes_encrypt,
        ),
        (
            "AES-256-GCM Decryption",
            aes_decrypt,
        ),
        (
            "Medical Record Encryption",
            record_encrypt,
        ),
        (
            "Medical Record Decryption",
            record_decrypt,
        ),
    ]

    for name, stats in results:

        print(
            f"{name:<45}"
            f"{stats['average']:>10.4f}"
            f"{stats['median']:>20.4f}"
        )

    # --------------------------------------------------------
    # Complete cycle
    # --------------------------------------------------------

    total_average = (
        record_encrypt["average"]
        + record_decrypt["average"]
    )

    total_median = (
        record_encrypt["median"]
        + record_decrypt["median"]
    )

    print()

    print(
        f"{'Encryption + Decryption':<45}"
        f"{total_average:>10.4f}"
        f"{total_median:>20.4f}"
    )

    print()
    print("=" * 65)
    print("BENCHMARK COMPLETED")
    print("=" * 65)


if __name__ == "__main__":
    main()