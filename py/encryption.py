import math
import base64
from Crypto.Hash import SHA256
from Crypto import Random
from Crypto.Cipher import AES
from hash_mac import get_hmac, verify_hmac
import pickle
import logging

paddingChr = '\n'

class Encryption:

    #note: return value is a byte stream, to print use print(str(cipherText))
    @staticmethod
    def encrypt(msg, key):
        #hash the key so any key can meet the requirement
        #logging.info('Encrypting message: ' + str(msg))
        keyHash = SHA256.new(str(key).encode()).digest() 
        IV = Random.get_random_bytes(AES.block_size)
        AEShelper = AES.new(keyHash,AES.MODE_CBC, IV)
        #msg needs to be multiple of 16 bytes
        cipherText = IV + AEShelper.encrypt(Encryption.padding(msg))
        #logging.info('Encrypted message: ' + str(cipherText))
        return cipherText

    @staticmethod
    def decrypt(cipherText, key):
        #logging.info('Decrypting message: ' + str(cipherText))
        keyHash = SHA256.new(str(key).encode()).digest() 
        # first {block size} byte is IV
        IV = cipherText[0:AES.block_size]
        AEShelper = AES.new(keyHash, AES.MODE_CBC, IV)
        msg = AEShelper.decrypt(cipherText[AES.block_size:])
        #should handle padding
        plainText = Encryption.trim(msg)
        #logging.info('Decrypted message:' + str(plainText))
        return plainText

    @staticmethod
    def padding(raw):
        msg = raw
        #logging.info('Message length before padding: ' + str(len(msg)))
        paddingLen = (AES.block_size - len(raw)) % AES.block_size
        for i in range(paddingLen):
            if type(msg) is str:
                msg += paddingChr
            else:
                msg += bytes([10])
        #logging.info('Message length after padding: ' + str(len(msg)))
        return msg

    @staticmethod
    def trim(msg):
        msg = msg.rstrip()
        return msg

    #Encrypt and get HMAC value, pack to one message
    @staticmethod
    def encryptPack(msg,key):
        cipherText = Encryption.encrypt(msg, key)
        hmac = get_hmac(cipherText, key)
        packedMsg = [cipherText, hmac]
        return packedMsg
    
    #unpack the ciphtext+hmac, and decrypt and verify the hmac
    @staticmethod
    def decryptVerify(packedMsg,key):
        unpackedMsg = pickle.load(packedMsg)
        cipherText = unpackedMsg[0]
        hmac = unpackedMsg[1]
        msg = Encryption.decrypt(cipherText,key)
        if not (verify_hmac(cipherText, hmac, key)):
             msg += " (HMAC doesn't match)"
        return msg

