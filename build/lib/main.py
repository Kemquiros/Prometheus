# Import zone
import sys
import getpass
import importlib.resources as pkg_resources
import messages
from crypto import encrypt, decrypt
from messages import print_encrypt, print_decrypt

def read_wallpaper() -> str:
    """
    Reads and returns the contents of the wallpaper file.
    Uses importlib.resources to work both in source and installed package.
    Returns:
        str: File content or an error message if the file cannot be read.
    """
    try:
        return pkg_resources.read_text("wallpapers", "skull.txt")
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

def main() -> None:
    """Entry point for CLI."""
    wallpaper = read_wallpaper()
    print(wallpaper)

    args_count = len(sys.argv)
    if args_count == 4:
        terminal_mode(sys.argv)
    elif args_count == 1:
        interactive_mode()
    else:
        print(messages.error)


if __name__ == "__main__":
    main()
