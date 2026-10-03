from app.core.pqc import (
    generate_keypair,
    encapsulate,
    decapsulate,
)

print("=" * 50)
print("Generating ML-KEM-768 key pair...")
print("=" * 50)

public_key, private_key = generate_keypair()

print("Public Key Length :", len(public_key))
print("Private Key Length:", len(private_key))

ciphertext, secret1 = encapsulate(public_key)

print("\nCiphertext Length :", len(ciphertext))
print("Shared Secret Length:", len(secret1))

secret2 = decapsulate(ciphertext, private_key)

print("\nSecrets Match:", secret1 == secret2)