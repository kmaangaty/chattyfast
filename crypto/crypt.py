import base64
import os
import rsa

# Get the current working directory of the script
cwd = os.path.dirname(os.path.abspath(__file__))


def generate_keys():
    """
    Generates a pair of RSA keys (public and private) and saves them to files.

    The function generates a new 2048-bit RSA key pair using the `rsa` library.
    It then saves the public key to 'pubkey.pem' and the private key to 'privkey.pem'
    in a directory named 'keys' within the current working directory.

    Raises:
        FileNotFoundError: If the 'keys' directory does not exist.
    """
    (pubKey, privKey) = rsa.newkeys(2048)

    keys_dir = os.path.join(cwd, 'keys')
    os.makedirs(keys_dir, exist_ok=True)

    with open(f'{keys_dir}/pubkey.pem', 'wb') as f:
        f.write(pubKey.save_pkcs1('PEM'))

    with open(f'{keys_dir}/privkey.pem', 'wb') as f:
        f.write(privKey.save_pkcs1('PEM'))

def load_keys():
    """
    Loads the RSA public and private keys from the 'keys' directory.

    This function reads the public key from 'pubkey.pem' and the private key from
    'privkey.pem' files in the 'keys' directory within the current working directory.
    It returns both keys for use in encryption and decryption operations.

    Returns:
        tuple: A tuple containing the public key and private key as
               (rsa.PublicKey, rsa.PrivateKey).

    Raises:
        FileNotFoundError: If the key files do not exist.
        rsa.pkcs1.DecryptionError: If the keys are not in the correct format.
    """
    # Load the public key from 'pubkey.pem'
    with open(f'{cwd}/keys/pubkey.pem', 'rb') as f:
        pubKey = rsa.PublicKey.load_pkcs1(f.read())

    with open(f'{cwd}/keys/privkey.pem', 'rb') as f:
        privKey = rsa.PrivateKey.load_pkcs1(f.read())

    return pubKey, privKey


pubKey, privKey = load_keys()


def encrypt_rsa(msg, key):
    """
    Encrypts a message using the RSA encryption algorithm.

    Args:
        msg (str): The plaintext message to be encrypted.
        key (rsa.PublicKey): The RSA public key used for encryption.

    Returns:
        bytes: The encrypted message in bytes.
    """
    return rsa.encrypt(msg.encode('utf-8'), key)


def decrypt_rsa(ciphertext, key):
    """
    Decrypts an RSA-encrypted message.

    Args:
        ciphertext (bytes): The encrypted message in bytes.
        key (rsa.PrivateKey): The RSA private key used for decryption.

    Returns:
        str: The decrypted plaintext message if decryption is successful.
        bool: False if decryption fails.
    """
    try:
        return rsa.decrypt(ciphertext, key).decode('utf-8')
    except:
        return False


def encrypt(msg):
    """
    Encrypts a message using RSA and encodes it in Base64.

    Args:
        msg (str): The plaintext message to be encrypted.

    Returns:
        str: The Base64-encoded encrypted message.
    """
    ciphertext = encrypt_rsa(msg, pubKey)
    encoded = base64.b64encode(ciphertext)
    return encoded.decode()


def decrypt(message):
    """
    Decrypts a Base64-encoded RSA-encrypted message.

    Args:
        message (str): The Base64-encoded encrypted message.

    Returns:
        str: The decrypted plaintext message if successful, otherwise an error message.
    """
    message = base64.b64decode(message)
    plaintext = decrypt_rsa(message, privKey)
    if plaintext:
        return plaintext
    else:
        return 'Could not decrypt the message.'


