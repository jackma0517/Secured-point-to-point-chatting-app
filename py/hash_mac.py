from encryption import Encryption

import hashlib
import hmac
import base64

def get_hmac(key, msg):
    message = bytes(msg, 'utf-8')
    secret_key = bytes(key, 'utf-8')

    hash = hmac.new(secret_key, message, hashlib.sha256)
    return hash.hexdigest() #this hmac is 64 bits

def verify_hmac(key, ciphertext):
    #get last block of ciphertext which is the HMAC
    encrypted_hmac = ciphertext[-64:] #only the last block
    hmac = Encryption.decrypt(encrypted_hmac)

    #get expected hmac
    plaintext = Encryption.decrypt(ciphertext[:-64])#everything except the last block
    expected_hmac = get_hmac(key, plaintext)

    return HMAC.compare_digest(expected_hmac, hmac)
