# Import zone
import os
import sys
import getpass
import messages
from cryptography import encrypt, decrypt
from messages import print_encrypt, print_decrypt

# Constants definition
WALLPAPER_FILE = os.path.join("wallpapers", "skull.txt")

# Read wallpaper ascii
wallpaper = open(WALLPAPER_FILE, 'r').read()
	
# Executing main loop
print(wallpaper)

n = len(sys.argv)
# Execute as a terminal process
if n == 4:
	if sys.argv[1] == "-e":
		secret = sys.argv[2]
		password = sys.argv[3]
		answer = encrypt(secret,password)
		print_encrypt(answer)
	elif sys.argv[1] == "-d":
		secret = sys.argv[2]
		password = sys.argv[3].split("-")
		answer = decrypt(secret,password)
		print_decrypt(answer)
	else:
		print(messages.error)
# Interactive execution
elif n == 1:
	is_valid_input = False
	while not is_valid_input:
		op = input("(e) Encrypt\n(d) Decrypt\n(f) Finish program\n>> ")
		if op == "f":
			# Finish program execution
			sys.exit()
		elif op == "e" or op == "d":
			is_valid_input = True
		else:
			print(messages.wrong)
	if op == "e":
		secret = getpass.getpass("Secret:\n>> ")
		password = getpass.getpass("Password:\n>> ")
		answer =  encrypt(secret, password)
		print_encrypt(answer)
	elif op == "d":
		secret = getpass.getpass("Secret:\n>> ")
		password = getpass.getpass("Encrypted Password:\n>> ")		
		answer = decrypt(secret, password)
		print_decrypt(answer)
else:
	print(messages.error)
