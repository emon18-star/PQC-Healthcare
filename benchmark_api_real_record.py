import os
import sys
import time
from datetime import datetime, timedelta, date
import statistics
import requests
from dotenv import load_dotenv
from jose import jwt

# Load environment configuration
load_dotenv(".env")

from app.database.database import SessionLocal
from app.models.user import User
from app.models.patient import Patient
from app.models.medical_record import MedicalRecord

# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_ME_LATER")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# Default iterations (can be overridden via CLI argument, e.g. python benchmark_api_real_record.py 100)
ITERATIONS = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 1000


# ============================================================
# AUTOMATED SETUP
# ============================================================

def setup_benchmark_environment():
    """
    Automatically prepares:
    1. A valid doctor user with PQC keys
    2. A fresh JWT access token signed with current SECRET_KEY
    3. A valid test patient for foreign key integrity
    """
    print("=" * 65)
    print("AUTOMATED BENCHMARK ENVIRONMENT SETUP")
    print("=" * 65)

    # 1. Check if backend API is reachable
    print(f"Checking API server at {BASE_URL}...")
    try:
        health_resp = requests.get(f"{BASE_URL}/health", timeout=5)
        if health_resp.status_code != 200:
            print(f"[ERROR] API returned status {health_resp.status_code}")
            return None
        print("API server is RUNNING and HEALTHY.")
    except Exception as e:
        print(f"[ERROR] Cannot connect to API server at {BASE_URL}: {e}")
        print("Please ensure your server is running with: uvicorn main:app --reload")
        return None

    # 2. Database connection & doctor lookup
    db = SessionLocal()
    try:
        doctor = (
            db.query(User)
            .filter(
                User.role == "doctor",
                User.public_key.isnot(None),
                User.private_key.isnot(None),
            )
            .first()
        )

        if not doctor:
            print("[ERROR] No doctor found with valid cryptographic keys in database.")
            return None

        print(f"Doctor account found: '{doctor.username}' (ID: {doctor.id})")

        from datetime import timezone
        token_payload = {
            "sub": doctor.username,
            "role": doctor.role,
            "exp": datetime.now(timezone.utc) + timedelta(hours=24),
        }
        token = jwt.encode(token_payload, SECRET_KEY, algorithm=ALGORITHM)
        print("Fresh JWT token generated successfully.")

        # 4. Check or create test patient
        patient = db.query(Patient).first()
        if not patient:
            print("No existing patient found. Creating benchmark test patient...")
            patient = Patient(
                full_name="Benchmark Test Patient",
                date_of_birth=date(1990, 1, 1),
                gender="Male",
                blood_group="O+",
                phone="01700000000",
                email="benchmark@test.local",
                created_by=doctor.id,
            )
            db.add(patient)
            db.commit()
            db.refresh(patient)
            print(f"Test patient created with ID: {patient.id}")
        else:
            print(f"Using existing patient ID: {patient.id}")

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        medical_record_payload = {
            "patient_id": patient.id,
            "diagnosis": "Automated Benchmark Diagnosis",
            "symptoms": "Systematic load testing and latency measurement",
            "treatment": "Quantum-resistant encryption validation",
            "prescription": "ML-KEM-768 key encapsulation + AES-256-GCM",
            "doctor_notes": "Standardized benchmark payload for API latency profiling.",
        }

        return {
            "headers": headers,
            "medical_record": medical_record_payload,
            "doctor": doctor,
            "patient_id": patient.id,
        }

    finally:
        db.close()


# ============================================================
# STATISTICS
# ============================================================

def calculate_statistics(times):
    return {
        "average": statistics.mean(times),
        "median": statistics.median(times),
        "minimum": min(times),
        "maximum": max(times),
        "stddev": statistics.stdev(times) if len(times) > 1 else 0,
    }


# ============================================================
# API ENCRYPTION BENCHMARK
# ============================================================

def benchmark_encryption(env, iterations=ITERATIONS):
    url = f"{BASE_URL}/medical-records"
    headers = env["headers"]
    payload = env["medical_record"]

    session = requests.Session()
    session.headers.update(headers)

    times = []
    successful = 0
    failed = 0
    created_record_id = None

    print()
    print("=" * 65)
    print("REAL API ENCRYPTION BENCHMARK")
    print("=" * 65)
    print(f"Endpoint   : POST /medical-records")
    print(f"Iterations : {iterations}")
    print()

    # Warm-up request
    print("Running warm-up request...", flush=True)
    warmup_res = session.post(url, json=payload, timeout=30)

    if warmup_res.status_code not in (200, 201):
        print(f"Warm-up request failed. Status: {warmup_res.status_code}", flush=True)
        print(f"Response: {warmup_res.text}", flush=True)
        return None, None

    created_record_id = warmup_res.json().get("id")
    print(f"Warm-up request: SUCCESS (Created record ID: {created_record_id})", flush=True)
    print()

    # Benchmark loop
    print_interval = max(1, iterations // 10)
    for i in range(iterations):
        start = time.perf_counter()
        res = session.post(url, json=payload, timeout=30)
        end = time.perf_counter()

        elapsed_ms = (end - start) * 1000

        if res.status_code in (200, 201):
            times.append(elapsed_ms)
            successful += 1
            if created_record_id is None:
                created_record_id = res.json().get("id")
        else:
            failed += 1

        if (i + 1) % print_interval == 0 or (i + 1) == iterations:
            print(f"Encryption Progress: {i + 1}/{iterations} completed (last: {elapsed_ms:.1f}ms)", flush=True)

    if not times:
        print("No successful encryption requests.")
        return None, None

    stats = calculate_statistics(times)

    print()
    print("## Complete API Encryption")
    print(f"Successful requests : {successful}")
    print(f"Failed requests     : {failed}")
    print(f"Average             : {stats['average']:.4f} ms")
    print(f"Median              : {stats['median']:.4f} ms")
    print(f"Minimum             : {stats['minimum']:.4f} ms")
    print(f"Maximum             : {stats['maximum']:.4f} ms")
    print(f"Std deviation       : {stats['stddev']:.4f} ms")

    return stats, created_record_id


# ============================================================
# API DECRYPTION BENCHMARK
# ============================================================

def benchmark_decryption(env, record_id, iterations=ITERATIONS):
    url = f"{BASE_URL}/medical-records/{record_id}/decrypt"
    headers = env["headers"]

    session = requests.Session()
    session.headers.update(headers)

    times = []
    successful = 0
    failed = 0

    print()
    print("=" * 65)
    print("REAL API DECRYPTION BENCHMARK")
    print("=" * 65)
    print(f"Endpoint   : GET /medical-records/{record_id}/decrypt")
    print(f"Iterations : {iterations}")
    print()

    # Warm-up request
    print("Running warm-up request...", flush=True)
    warmup_res = session.get(url, timeout=30)

    if warmup_res.status_code != 200:
        print(f"Warm-up request failed. Status: {warmup_res.status_code}", flush=True)
        print(f"Response: {warmup_res.text}", flush=True)
        return None

    print(f"Warm-up request: SUCCESS", flush=True)
    print()

    # Benchmark loop
    print_interval = max(1, iterations // 10)
    for i in range(iterations):
        start = time.perf_counter()
        res = session.get(url, timeout=30)
        end = time.perf_counter()

        elapsed_ms = (end - start) * 1000

        if res.status_code == 200:
            times.append(elapsed_ms)
            successful += 1
        else:
            failed += 1

        if (i + 1) % print_interval == 0 or (i + 1) == iterations:
            print(f"Decryption Progress: {i + 1}/{iterations} completed (last: {elapsed_ms:.1f}ms)", flush=True)

    if not times:
        print("No successful decryption requests.")
        return None

    stats = calculate_statistics(times)

    print()
    print("## Complete API Decryption")
    print(f"Successful requests : {successful}")
    print(f"Failed requests     : {failed}")
    print(f"Average             : {stats['average']:.4f} ms")
    print(f"Median              : {stats['median']:.4f} ms")
    print(f"Minimum             : {stats['minimum']:.4f} ms")
    print(f"Maximum             : {stats['maximum']:.4f} ms")
    print(f"Std deviation       : {stats['stddev']:.4f} ms")

    return stats


# ============================================================
# MAIN
# ============================================================

def main():
    print()
    print("=" * 65)
    print("PQC HEALTHCARE SYSTEM")
    print("AUTOMATED REAL HTTP/API BENCHMARK")
    print("=" * 65)
    print()

    # 1. Environment and credentials setup
    env = setup_benchmark_environment()
    if env is None:
        print("\nBenchmark setup failed. Exiting.")
        return

    # 2. Encryption Benchmark
    encryption, record_id = benchmark_encryption(env, iterations=ITERATIONS)
    if encryption is None:
        print("\nEncryption benchmark failed.")
        return

    # 3. Decryption Benchmark
    decryption = benchmark_decryption(env, record_id=record_id, iterations=ITERATIONS)
    if decryption is None:
        print("\nDecryption benchmark failed.")
        return

    # 4. Final Comparison Results
    encryption_average = encryption["average"]
    decryption_average = decryption["average"]
    encryption_median = encryption["median"]
    decryption_median = decryption["median"]

    total_average = encryption_average + decryption_average
    total_median = encryption_median + decryption_median

    print()
    print("=" * 65)
    print("FINAL API PERFORMANCE COMPARISON")
    print("=" * 65)
    print(f"{'Operation':<35} {'Average (ms)':>12} {'Median (ms)':>14}")
    print("-" * 65)
    print(f"{'API Encryption':<35} {encryption_average:>12.4f} {encryption_median:>14.4f}")
    print(f"{'API Decryption':<35} {decryption_average:>12.4f} {decryption_median:>14.4f}")
    print("-" * 65)
    print(f"{'Encryption + Decryption':<35} {total_average:>12.4f} {total_median:>14.4f}")
    print("=" * 65)
    print()
    print("WHAT THIS BENCHMARK MEASURES:")
    print("1. Encryption: Client -> HTTP -> FastAPI -> JWT Auth -> PQC Encapsulation + AES -> DB -> Response")
    print("2. Decryption: Client -> HTTP -> FastAPI -> JWT Auth -> Private-Key Unlock -> ML-KEM Decap + AES -> Response")
    print()
    print("BENCHMARK COMPLETED SUCCESSFULLY")
    print("=" * 65)


if __name__ == "__main__":
    main()