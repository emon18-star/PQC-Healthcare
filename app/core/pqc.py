from mlkem.ml_kem import ML_KEM
from mlkem.parameter_set import ML_KEM_768

# ML-KEM-768 instance
ml_kem = ML_KEM(ML_KEM_768)


def generate_keypair():
    """
    Generate ML-KEM-768 public and private keys.
    """
    public_key, private_key = ml_kem.key_gen()

    return public_key, private_key


def encapsulate(public_key):
    """
    Encapsulate a shared secret using the public key.
    """
    shared_secret, ciphertext = ml_kem.encaps(public_key)

    return ciphertext, shared_secret


def decapsulate(ciphertext, private_key):
    """
    Recover the shared secret using the private key.
    """
    shared_secret = ml_kem.decaps(private_key, ciphertext)

    return shared_secret