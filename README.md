# PROMETHEUS

## Password Encryption and Decryption Tool

### Key Sections:
1. **Overview**: Briefly describes the project.
2. **Features**: Lists the main features of the tool.
3. **Requirements**: Specifies the prerequisites for running the tool.
4. **Installation**: Guides the user through cloning the repository and installing dependencies.
5. **Code Structure**: Provides an overview of the project's file structure.
6. **Usage**: Explains how to use the tool, both in terminal and interactive modes, with example commands.
7. **License and Contributing**: Information about contributing and the license.

## Overview
This project provides a simple command-line tool for encrypting and decrypting passwords using a symmetric encryption algorithm. The tool leverages a secret key to securely encrypt and decrypt passwords with XOR and modulus operations. It supports both terminal-based and interactive modes for ease of use.

:shipit:
![alt tag](https://raw.githubusercontent.com/Kemquiros/Prometheus/master/img/prometheus.png)

## Features
- **Symmetric Encryption**: The same secret key is used for both encryption and decryption.
- **Base64 Encoding**: Encrypted data is returned in Base64 format to make it safe for storage and transmission.
- **Interactive Mode**: Encrypt or decrypt passwords directly from the command line with user prompts.
- **Terminal Mode**: Execute encryption or decryption with command-line arguments.
- **Password Security**: The secret key and passwords are never logged or printed in plaintext.

## Requirements
- Python 3.x
- `cryptography` library (for encryption/decryption)

## Installation

### Clone the Repository

```bash
git clone https://github.com/kemquirs/prometheus.git
cd password-encryption-tool
```

## Code Structure
* `main.py`: Main entry point of the program. Handles both terminal and interactive modes.
* `cryptography.py`: Contains the encryption and decryption functions.
* `messages.py`: Stores the messages shown to the user (e.g., error messages).
* `wallpapers/`: Contains ASCII art displayed when the program starts.

## Usage
You can use the tool in either Terminal Mode or Interactive Mode.

### 1. Terminal Mode

In this mode, you provide the necessary arguments directly in the command line. You can encrypt or decrypt a password by passing the following arguments:

```bash
python main.py -e <secret_key> <password>  # Encrypt a password
python main.py -d <secret_key> <encrypted_password>  # Decrypt a password
```
**Example:**
```bash
python main.py -e "123" "my_password"  # Encrypt
```
The output will be a Base64-encoded ciphertext.

To decrypt a password:
```bash
python main.py -d "123" "Base64-encoded-ciphertext"
```
### 2. Interactive Mode

In Interactive Mode, you can run the program without command-line arguments. The program will prompt you for inputs interactively.
```bash
python main.py
```

You will be asked to:

* Choose an operation: Encrypt, Decrypt, or Finish the program.
* Enter the secret key and password to encrypt or decrypt.

**Example:**
```text
(e) Encrypt
(d) Decrypt
(f) Finish program
>> e
Secret:
>> 123
Password:
>> my_password
Encrypted result: XYZ123==
```
### 3. Error Handling

If an error occurs (e.g., invalid input, encryption failure), the program will print an error message and allow you to try again.

## Example Workflow

### Encryption Example:

```bash
python main.py -e "secret_key" "my_password"
```

Output (Base64-encoded):
```bash
Encrypted result: XYZ123==
```

### Decryption Example:

```bash
python main.py -d "secret_key" "XYZ123=="
```

Output:
```bash
Decrypted password: my_password
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing
We welcome contributions to improve the tool! To contribute:
1. Fork the repository.
1. Create a new branch (`git checkout -b feature/your-feature`).
1. Make your changes and commit them (`git commit -am 'Add new feature'`).
1. Push to your forked repository (`git push origin feature/your-feature`).
1. Submit a pull request.
