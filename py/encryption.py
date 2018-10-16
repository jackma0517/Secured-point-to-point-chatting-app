# written by jack
import math
import base64
from Crypto.Hash import SHA256
from Crypto import Random
from Crypto.Cipher import AES

paddingChr = '\n'

#note: return value is a byte stream, to print use print(str(cipherText))
def encrypt(msg, key):
    #hash the key so any key can meet the requirement
    keyHash = SHA256.new(key.encode()).digest() 
    IV = Random.get_random_bytes(AES.block_size)
    AEShelper = AES.new(keyHash,AES.MODE_CBC, IV)
    #msg needs to be multiple of 16 bytes
    cipherText = IV + AEShelper.encrypt(padding(msg))
    return cipherText

def decrypt(cipherText, key):
    keyHash = SHA256.new(key.encode()).digest() 
    # first {block size} byte is IV
    IV = cipherText[0:AES.block_size]
    AEShelper = AES.new(keyHash, AES.MODE_CBC, IV)
    msg = AEShelper.decrypt(cipherText[AES.block_size:])
    #should handle padding
    return str(trim(msg))


def padding(raw):
    msg = raw
    paddingLen = (AES.block_size - len(raw)) % AES.block_size
    msg += paddingChr * paddingLen
    return msg


def trim(msg):
    msg = msg.rstrip()
    return msg

