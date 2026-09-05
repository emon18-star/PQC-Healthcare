from app.core.encryption import (
    generate_aes_key,
    encrypt_text,
    decrypt_text,
)

# Generate a random AES-256 key
key = generate_aes_key()

print("=" * 50)
print("AES KEY GENERATED")
print("=" * 50)

plaintext = "Dengue Fever"

print("\nOriginal Text:")
print(plaintext)

encrypted = encrypt_text(
    plaintext,
    key
)

print("\nEncrypted Data:")
print(encrypted)

decrypted = decrypt_text(
    encrypted["ciphertext"],
    encrypted["nonce"],
    key
)

print("\nDecrypted Text:")
print(decrypted)

print("\nSuccess:", plaintext == decrypted)