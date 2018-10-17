# written by jack
import math
import base64
from Crypto.Hash import SHA256
from Crypto import Random
from Crypto.Cipher import AES

paddingChr = '\n'

class Encryption:

    #note: return value is a byte stream, to print use print(str(cipherText))
    @staticmethod
    def encrypt(msg, key):
        #hash the key so any key can meet the requirement
        keyHash = SHA256.new(key.encode()).digest() 
        IV = Random.get_random_bytes(AES.block_size)
        AEShelper = AES.new(keyHash,AES.MODE_CBC, IV)
        #msg needs to be multiple of 16 bytes
        cipherText = IV + AEShelper.encrypt(Encryption.padding(msg))
        return cipherText

    @staticmethod
    def decrypt(cipherText, key):
        keyHash = SHA256.new(key.encode()).digest() 
        # first {block size} byte is IV
        IV = cipherText[0:AES.block_size]
        AEShelper = AES.new(keyHash, AES.MODE_CBC, IV)
        msg = AEShelper.decrypt(cipherText[AES.block_size:])
        #should handle padding
        return Encryption.trim(msg).decode('UTF-8')

    @staticmethod
    def padding(raw):
        msg = raw
        paddingLen = (AES.block_size - len(raw)) % AES.block_size
        msg += paddingChr * paddingLen
        return msg

    @staticmethod
    def trim(msg):
        msg = msg.rstrip()
        return msg

