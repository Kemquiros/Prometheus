error = """Correct use:
					Dynamic -> prometheus
					Encrypt -> prometheus -e <SecretWord> <Password>
					Decrypt -> prometheus -d <SecretWord> <EncryptedPassword>"""

wrong = """
--------------------- 
     :(  Wrong  :(
---------------------"""

def print_message(result, message):
	print("-----------------------------------------------")
	print(message)
	print(result)
	print("-----------------------------------------------\n\n")

def print_encrypt(result):
	print_message(result, "Encrypted Password:")

def print_decrypt(result):
	print_message(result, "Decrypted Password:")
