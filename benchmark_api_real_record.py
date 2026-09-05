import time
import statistics
import requests


# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "http://127.0.0.1:8000"

RECORD_ID = 1012

TOKEN = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZGkyOSIsInJvbGUiOiJkb2N0b3IiLCJleHAiOjE3ODcxMzA3MzZ9.G1Sq9wHCCudE7Fm_bWD_Nye1kd5M-Qa1S1RWBtals4M"
)

ITERATIONS = 1000


# ============================================================
# HEADERS
# ============================================================

HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}


# ============================================================
# TEST MEDICAL RECORD
# ============================================================

MEDICAL_RECORD = {
    "patient_id": 5,
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


# ============================================================
# API ENCRYPTION BENCHMARK
# ============================================================

def benchmark_encryption():

    url = f"{BASE_URL}/medical-records"

    times = []

    successful = 0
    failed = 0

    print()
    print("=" * 65)
    print("REAL API ENCRYPTION BENCHMARK")
    print("=" * 65)
    print()

    print("Endpoint:")
    print("POST /medical-records")
    print()

    print(f"Iterations: {ITERATIONS}")
    print()

    # --------------------------------------------------------
    # Warm-up
    # --------------------------------------------------------

    print("Running warm-up request...")

    response = requests.post(
        url,
        headers=HEADERS,
        json=MEDICAL_RECORD,
        timeout=30,
    )

    if response.status_code not in (200, 201):

        print("Warm-up request failed.")
        print("Status:", response.status_code)
        print("Response:", response.text)

        return None

    print("Warm-up request: SUCCESS")
    print()

    # --------------------------------------------------------
    # Benchmark
    # --------------------------------------------------------

    for i in range(ITERATIONS):

        start = time.perf_counter()

        response = requests.post(
            url,
            headers=HEADERS,
            json=MEDICAL_RECORD,
            timeout=30,
        )

        end = time.perf_counter()

        elapsed_ms = (end - start) * 1000

        if response.status_code in (200, 201):

            times.append(elapsed_ms)
            successful += 1

        else:

            failed += 1

        if (i + 1) % 100 == 0:

            print(
                f"Encryption: "
                f"{i + 1}/{ITERATIONS}"
            )

    if not times:

        print("No successful encryption requests.")
        return None

    stats = calculate_statistics(times)

    print()
    print("## Complete API Encryption")
    print()

    print(
        f"Successful requests : "
        f"{successful}"
    )

    print(
        f"Failed requests     : "
        f"{failed}"
    )

    print(
        f"Average             : "
        f"{stats['average']:.4f} ms"
    )

    print(
        f"Median              : "
        f"{stats['median']:.4f} ms"
    )

    print(
        f"Minimum             : "
        f"{stats['minimum']:.4f} ms"
    )

    print(
        f"Maximum             : "
        f"{stats['maximum']:.4f} ms"
    )

    print(
        f"Std deviation       : "
        f"{stats['stddev']:.4f} ms"
    )

    return stats


# ============================================================
# API DECRYPTION BENCHMARK
# ============================================================

def benchmark_decryption():

    url = (
        f"{BASE_URL}"
        f"/medical-records/{RECORD_ID}/decrypt"
    )

    times = []

    successful = 0
    failed = 0

    print()
    print("=" * 65)
    print("REAL API DECRYPTION BENCHMARK")
    print("=" * 65)
    print()

    print("Endpoint:")
    print(
        f"GET /medical-records/{RECORD_ID}/decrypt"
    )

    print()

    print(f"Iterations: {ITERATIONS}")
    print()

    # --------------------------------------------------------
    # Warm-up
    # --------------------------------------------------------

    print("Running warm-up request...")

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30,
    )

    if response.status_code != 200:

        print("Warm-up request failed.")
        print("Status:", response.status_code)
        print("Response:", response.text)

        return None

    print("Warm-up request: SUCCESS")
    print()

    # --------------------------------------------------------
    # Benchmark
    # --------------------------------------------------------

    for i in range(ITERATIONS):

        start = time.perf_counter()

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=30,
        )

        end = time.perf_counter()

        elapsed_ms = (end - start) * 1000

        if response.status_code == 200:

            times.append(elapsed_ms)
            successful += 1

        else:

            failed += 1

        if (i + 1) % 100 == 0:

            print(
                f"Decryption: "
                f"{i + 1}/{ITERATIONS}"
            )

    if not times:

        print("No successful decryption requests.")
        return None

    stats = calculate_statistics(times)

    print()
    print("## Complete API Decryption")
    print()

    print(
        f"Successful requests : "
        f"{successful}"
    )

    print(
        f"Failed requests     : "
        f"{failed}"
    )

    print(
        f"Average             : "
        f"{stats['average']:.4f} ms"
    )

    print(
        f"Median              : "
        f"{stats['median']:.4f} ms"
    )

    print(
        f"Minimum             : "
        f"{stats['minimum']:.4f} ms"
    )

    print(
        f"Maximum             : "
        f"{stats['maximum']:.4f} ms"
    )

    print(
        f"Std deviation       : "
        f"{stats['stddev']:.4f} ms"
    )

    return stats


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 65)
    print("PQC HEALTHCARE SYSTEM")
    print("REAL HTTP/API ENCRYPTION + DECRYPTION BENCHMARK")
    print("=" * 65)
    print()

    print(
        f"Record used for decryption: {RECORD_ID}"
    )

    print(
        f"Iterations: {ITERATIONS}"
    )

    # ========================================================
    # ENCRYPTION
    # ========================================================

    encryption = benchmark_encryption()

    if encryption is None:

        print()
        print("Encryption benchmark failed.")
        return

    # ========================================================
    # DECRYPTION
    # ========================================================

    decryption = benchmark_decryption()

    if decryption is None:

        print()
        print("Decryption benchmark failed.")
        return

    # ========================================================
    # FINAL RESULTS
    # ========================================================

    encryption_average = encryption["average"]
    decryption_average = decryption["average"]

    encryption_median = encryption["median"]
    decryption_median = decryption["median"]

    total_average = (
        encryption_average
        + decryption_average
    )

    total_median = (
        encryption_median
        + decryption_median
    )

    print()
    print("=" * 65)
    print("FINAL API PERFORMANCE COMPARISON")
    print("=" * 65)
    print()

    print(
        "Operation"
        "                         Average (ms)"
        "       Median (ms)"
    )

    print(
        f"API Encryption"
        f"                    "
        f"{encryption_average:>10.4f}"
        f"            "
        f"{encryption_median:>10.4f}"
    )

    print(
        f"API Decryption"
        f"                    "
        f"{decryption_average:>10.4f}"
        f"            "
        f"{decryption_median:>10.4f}"
    )

    print()

    print(
        f"Encryption + Decryption"
        f"          "
        f"{total_average:>10.4f}"
        f"            "
        f"{total_median:>10.4f}"
    )

    print()
    print("=" * 65)
    print("WHAT THIS BENCHMARK MEASURES")
    print("=" * 65)
    print()

    print("API Encryption:")

    print(
        "Client -> HTTP -> FastAPI -> JWT -> "
        "Database -> Authorization -> "
        "PQC/AES Encryption -> Database -> "
        "JSON Response"
    )

    print()

    print("API Decryption:")

    print(
        "Client -> HTTP -> FastAPI -> JWT -> "
        "Database -> Authorization -> "
        "Private-Key Decryption -> ML-KEM Decapsulation -> "
        "AES Decryption -> JSON Response"
    )

    print()

    print(
        "These measurements represent real HTTP/API "
        "performance, not cryptography-only processing."
    )

    print()
    print("=" * 65)
    print("BENCHMARK COMPLETED SUCCESSFULLY")
    print("=" * 65)


if __name__ == "__main__":
    main()