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
    # Generate a new RSA key pair (public key and private key)
    (pubKey, privKey) = rsa.newkeys(2048)

    # Ensure the 'keys' directory exists; create it if it doesn't
    keys_dir = os.path.join(cwd, 'keys')
    os.makedirs(keys_dir, exist_ok=True)

    # Save the public key to a file
    with open(f'{keys_dir}/pubkey.pem', 'wb') as f:
        f.write(pubKey.save_pkcs1('PEM'))

    # Save the private key to a file
    with open(f'{keys_dir}/privkey.pem', 'wb') as f:
        f.write(privKey.save_pkcs1('PEM'))


