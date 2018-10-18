from encryption import Encryption
import hashlib
import hmac
import base64

def get_hmac(msg, key):
    msg = bytes(msg, 'utf-8')
    key = bytes(key, 'utf-8')

    hash = hmac.new(key, msg, hashlib.sha256)
    return hash.hexdigest() #this hmac is 64

def verify_hmac(msg, hmac, key):
    msg     = bytes(msg, 'utf-8')
    key     = bytes(key, 'utf-8')

    #get expected hmac
    expected_hmac = get_hmac(msg, key)

    return hmac.compare_digest(expected_hmac, hmac)
