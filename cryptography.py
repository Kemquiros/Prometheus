# Imports
import base64
import hashlib

# Encrypt function definition
def encrypt(secret, password):
		key = hashlib.sha256(secret.encode('utf-8')).hexdigest()
		pos1 = len(secret) - 1
		pos2 = len(key)//2
		result = ""
		for elem in password:
			temp = ord(elem)+(ord(secret[pos1]))
			temp = temp % 256
			temp = chr(temp ^ ord(key[pos2]))
			result = result + temp
			pos1 -= 1
			pos2 -= 1
			if pos1 < 0:
				pos1 = len(secret) - 1
			if pos2 < 0:
				pos2 = len(key) - 1
		return base64.b64encode(bytes(result,'utf-8'))

# Decrypt function definition
def decrypt(secret, text):
		text = base64.b64decode(bytes(text,'utf-8')).decode('utf-8')
		key = hashlib.sha256(secret.encode('utf-8')).hexdigest()
		pos1 = len(secret) - 1
		pos2 = len(key)//2
		result = ""
		for elem in text:
			temp = chr(ord(elem) ^ ord(key[pos2]))
			temp = ord(temp)-(ord(secret[pos1]))
			temp = temp % 256
			result = result + chr(temp)
			pos1 -= 1
			pos2 -= 1
			if pos1 < 0:
				pos1 = len(secret) - 1
			if pos2 < 0:
				pos2 = len(key) - 1
		return result