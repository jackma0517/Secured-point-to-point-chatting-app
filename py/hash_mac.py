import hashlib
import hmac
import base64

def get_hmac(msg, key):
    if type(msg) is not bytes:
        msg = bytes(msg, 'utf-8')
    if type(key) is not bytes:
        key = bytes(str(key), 'utf-8')

    hash = hmac.new(key, msg, hashlib.sha256)
    return hash.hexdigest() #this hmac is 64

def verify_hmac(msg, hmac, key):
    if type(msg) is not bytes:
        msg = bytes(msg, 'utf-8')
    if type(key) is not bytes:
        key = bytes(str(key), 'utf-8')

    #get expected hmac
    expected_hmac = get_hmac(msg, key)
    same = (hmac == expected_hmac)
    #hmac_cmp_dig = hmac.compare_digest(expected_hmac, hmac)
    #print('cpm dig: ' + str(hmac_cmp_dig))
    return same
