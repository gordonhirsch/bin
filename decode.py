# !/usr/bin/python

import base64

cryptotext = base64.b64decode("WfozUL/dvovXzX4e4mYV5I/56lzz81RE")

decryption_key = [0x7d, 0x89, 0x52, 0x23, 0xd2, 0xbc, 0xdd, 0xea, 0xa3, 0xb9, 0x1f]

i = 0
cleartext = ""

for ch in cryptotext:
    x = ord(ch) ^ decryption_key[i]
    print("%d" %(x))
    cleartext += chr(ord(ch) ^ decryption_key[i])
    i += 1
    i = i % len(decryption_key)
    

print("%s" %(cleartext)) 
