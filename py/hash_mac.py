from encryption import Encryption
import hashlib
import hmac
import base64

def get_hmac(msg, hmac_key):
    message = bytes(msg, 'utf-8')
    hmackey = bytes(hmac_key, 'utf-8')

    hash = hmac.new(hmackey, message, hashlib.sha256)
    return hash.hexdigest() #this hmac is 64

def verify_hmac(hmac_key, ciphertext, shared_secret_key):
    #get last block of ciphertext which is the HMAC
    encrypted_hmac = ciphertext[-64:] #only the last block
    hmacValue = Encryption.decrypt(encrypted_hmac, shared_secret_key)

    #get expected hmac
    plaintext = Encryption.decrypt(ciphertext[:-64], shared_secret_key)#everything except the last block
    expected_hmac = get_hmac(hmac_key, plaintext)

    return hmac.compare_digest(expected_hmac, hmacValue)
