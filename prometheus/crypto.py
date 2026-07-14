import base64
import hashlib

def encrypt(secret: str, password: str) -> str:
    """
    Encrypts the given password using the provided secret key.
    The encryption process includes character transformations and
    XOR operations, and the result is Base64-encoded.

    Args:
        secret (str): The secret key used for encryption.
        password (str): The plaintext password to encrypt.

    Returns:
        str: The Base64-encoded ciphertext.
    """
    # Generate a hash-based key from the secret
    key = hashlib.sha256(secret.encode('utf-8')).hexdigest()

    # Initialize position trackers for the secret and key
    secret_index = len(secret) - 1
    key_index = len(key) // 2

    # Resulting encrypted string
    encrypted_result = ""

    # Iterate over each character in the password
    for char in password:
        # Add the corresponding secret character's ordinal value
        temp = ord(char) + ord(secret[secret_index])
        
        # Apply modulus to keep the value in the byte range (0-255)
        temp = temp % 256

        # XOR the result with the key character
        temp = chr(temp ^ ord(key[key_index]))
        
        # Append the encrypted character to the result
        encrypted_result += temp

        # Update position trackers
        secret_index -= 1
        key_index -= 1

        # Wrap around the positions if they go out of bounds
        if secret_index < 0:
            secret_index = len(secret) - 1
        if key_index < 0:
            key_index = len(key) - 1

    # Return the encrypted result as a Base64-encoded string
    return base64.b64encode(encrypted_result.encode('latin1')).decode('utf-8')


def decrypt(secret: str, ciphertext: str) -> str:
    """
    Decrypts the given Base64-encoded ciphertext using the provided secret key.
    The decryption process reverses the character transformations and XOR operations
    applied during encryption.

    Args:
        secret (str): The secret key used for decryption (must match the encryption key).
        ciphertext (str): The Base64-encoded encrypted text to decrypt.

    Returns:
        str: The original plaintext password.
    """
    # Decode the Base64-encoded ciphertext into raw bytes
    encrypted_bytes = base64.b64decode(ciphertext.encode('utf-8')).decode('latin1')

    # Generate a hash-based key from the secret
    key = hashlib.sha256(secret.encode('utf-8')).hexdigest()

    # Initialize position trackers for the secret and key
    secret_index = len(secret) - 1
    key_index = len(key) // 2

    # Resulting decrypted string
    decrypted_result = ""

    # Iterate over each byte in the encrypted data
    for char in encrypted_bytes:
        # Reverse XOR with the corresponding key character
        temp = ord(char) ^ ord(key[key_index])
        
        # Reverse the addition and modulus operation applied during encryption
        temp = (temp - ord(secret[secret_index])) % 256

        # Append the decrypted character to the result
        decrypted_result += chr(temp)

        # Update position trackers
        secret_index -= 1
        key_index -= 1

        # Wrap around the positions if they go out of bounds
        if secret_index < 0:
            secret_index = len(secret) - 1
        if key_index < 0:
            key_index = len(key) - 1

    # Return the decrypted plaintext
    return decrypted_result
