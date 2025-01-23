# Import zone
import os
import sys
import getpass
import messages
from cryptography import encrypt, decrypt
from messages import print_encrypt, print_decrypt

# Constants
WALLPAPER_FILE = os.path.join("wallpapers", "skull.txt")

def read_wallpaper(file_path: str) -> str:
    """
    Reads and returns the contents of the specified file.
    Args:
        file_path (str): Path to the file to read.
    Returns:
        str: File content or an error message if the file cannot be read.
    """
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return "Error: Wallpaper file not found."
    except Exception as e:
        return f"Error: Unable to load wallpaper. Details: {e}"

def process_encryption(secret: str, password: str) -> None:
    """
    Handles encryption logic and prints the result.
    Args:
        secret (str): Secret key for encryption.
        password (str): Plaintext password to encrypt.
    """
    try:
        encrypted = encrypt(secret, password)
        print_encrypt(encrypted)
    except Exception as e:
        print(f"Encryption failed: {e}")

def process_decryption(secret: str, ciphertext: str) -> None:
    """
    Handles decryption logic and prints the result.
    Args:
        secret (str): Secret key for decryption.
        ciphertext (str): Encrypted text to decrypt.
    """
    try:
        decrypted = decrypt(secret, ciphertext)
        print_decrypt(decrypted)
    except Exception as e:
        print(f"Decryption failed: {e}")

def interactive_mode() -> None:
    """
    Runs the interactive mode where users can encrypt or decrypt data.
    """
    while True:
        operation = input("(e) Encrypt\n(d) Decrypt\n(f) Finish program\n>> ").strip().lower()
        if operation == "f":
            print("Exiting program. Goodbye!")
            sys.exit()
        elif operation in ["e", "d"]:
            secret = getpass.getpass("Secret:\n>> ")
            if operation == "e":
                password = getpass.getpass("Password:\n>> ")
                process_encryption(secret, password)
            elif operation == "d":
                ciphertext = getpass.getpass("Encrypted Password:\n>> ")
                process_decryption(secret, ciphertext)
        else:
            print(messages.wrong)

def terminal_mode(args: list) -> None:
    """
    Runs the terminal mode based on command-line arguments.
    Args:
        args (list): Command-line arguments.
    """
    operation = args[1]
    secret = args[2]
    data = args[3]

    if operation == "-e":
        process_encryption(secret, data)
    elif operation == "-d":
        process_decryption(secret, data)
    else:
        print(messages.error)

# Main Execution
if __name__ == "__main__":
    wallpaper = read_wallpaper(WALLPAPER_FILE)
    print(wallpaper)

    args_count = len(sys.argv)
    if args_count == 4:
        terminal_mode(sys.argv)
    elif args_count == 1:
        interactive_mode()
    else:
        print(messages.error)
