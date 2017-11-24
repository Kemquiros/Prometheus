import sys
import hashlib

wallpaper = """
                      :::!~!!!!!:.
                  .xUHWH!! !!?M88WHX:.
                .X*#M@$!!  !X!M$$$$$$WWx:.
               :!!!!!!?H! :!$!$$$$$$$$$$8X:
              !!~  ~:~!! :~!$!#$$$$$$$$$$8X:
             :!~::!H!<   ~.U$X!?R$$$$$$$$MM!
             ~!~!!!!~~ .:XW$$$U!!?$$$$$$RMM!
               !:~~~ .:!M"T#$$$$WX??#MRRMMM!
               ~?WuxiW*`   `"#$$$$8!!!!??!!!
             :X- M$$$$       `"T#$T~!8$WUXU~
            :%`  ~#$$$m:        ~!~ ?$$$$$$
          :!`.-   ~T$$$$8xx.  .xWW- ~""##*"
.....   -~~:<` !    ~?T#$$@@W@*?$$      /`
W$@@M!!! .!~~ !!     .:XUW$W!~ `"~:    :
#"~~`.:x%`!!  !H:   !WM$$$$Ti.: .!WUn+!`
:::~:!!`:X~ .: ?H.!u "$$$B$$$!W:U!T$$M~
.~~   :X@!.-~   ?@WTWo("*$$$W$TH$! `
Wi.~!X$?!-~    : ?$$$B$Wu("**$RM!
$R@i.~~ !     :   ~$$$$$B$$en:``
?MXT@Wx.~    :     ~"##*$$$$M~
-----------------------------------------------
-----------------------------------------------
             WELCOME TO PROMETHEUS
-----------------------------------------------
                          written by: Kemquiros
-----------------------------------------------
"""

error = """Correct use:
					Dynamic -> prometheus
					Encrypt -> prometheus -e <SecretWord> <Password>
					Decrypt -> prometheus -d <SecretWord> <EncryptedPassword>"""
wrong = """
--------------------- 
     :(  Wrong  :(
---------------------"""

def encryptPrometheus(secret,password):
		key = hashlib.sha256(secret).hexdigest()
		pos1 = len(secret) - 1
		pos2 = len(key)/2
		resul = ""
		for elem in password:
			temp = ord(elem)+(ord(secret[pos1]))
			temp = temp % 256
			temp = chr(temp ^ ord(key[pos2]))
			resul = resul + temp
			pos1 -= 1
			pos2 -= 1
			if pos1 < 0:
				pos1 = len(secret) - 1
			if pos2 < 0:
				pos2 = len(key) - 1
		return resul.encode('base64')

def decryptPrometheus(secret,text):
		text = text.decode('base64')
		key = hashlib.sha256(secret).hexdigest()
		pos1 = len(secret) - 1
		pos2 = len(key)/2
		resul = ""
		for elem in text:
			temp = chr(ord(elem) ^ ord(key[pos2]))
			temp = ord(temp)-(ord(secret[pos1]))
			temp = temp % 256
			resul = resul + chr(temp)
			pos1 -= 1
			pos2 -= 1
			if pos1 < 0:
				pos1 = len(secret) - 1
			if pos2 < 0:
				pos2 = len(key) - 1
		return resul

def printEncrypt(r):
	print "-----------------------------------------------"
	print "Encrypted Password:"
	print r
	print "-----------------------------------------------\n\n"

def printDecrypt(r):
	print "-----------------------------------------------"
	print "Decrypted Password:"
	print r
	print "-----------------------------------------------\n\n"
	

print wallpaper

n= len(sys.argv)
if n == 4:
	if sys.argv[1] == "-e":
		secret = sys.argv[2]
		password = sys.argv[3]
		answer = encryptPrometheus(secret,password)
		printEncrypt(answer)
	elif sys.argv[1] == "-d":
		secret = sys.argv[2]
		password = sys.argv[3].split("-")
		answer = decryptPrometheus(secret,password)
		printDecrypt(answer)
	else:
		print error
elif n == 1:
	flag = False
	while not flag:
		op = raw_input("(e)Encrypt\n(d)Decrypt\n>>")
		if op == "e" or op == "d":
			flag = True
		else:			
			print wrong
	if op == "e":
		secret = raw_input("Secret:\n>>")
		password = raw_input("Password:\n>>")
		answer =  encryptPrometheus(secret,password)
		printEncrypt(answer)
	elif op == "d":
		secret = raw_input("Secret:\n>>")
		password = raw_input("Encrypted Password:\n>>")		
		answer = decryptPrometheus(secret,password)
		printDecrypt(answer)
else:
	print error

