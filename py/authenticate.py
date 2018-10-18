# Written by Sawyer

import math
import base64
import codecs # base64
from encryption import Encryption
from hash_mac import *
from Crypto.Hash import SHA256
from Crypto import Random
from Crypto.Cipher import AES
from config import Mode
import pickle

import logging
import text_handler

class Authentication:

    def authenticate(self, shared_secret_key, receiver_q, sender_q, mode, dh, auth_error):
        """
        Authenticates server and client, returns a session key
        """
        client_auth_str = "I'm client"
        server_auth_str = "I'm server"
        NUM_BYTES_DH    = 32 # Going for 256-bit a/b values in diffie-hellman
        NUM_BYTES_NONCE = 8  # Going for 64-bit nonce
        TIMEOUT_DELAY   = 5  # Timeout waiting on response after 5 seconds

        print('Authenticating')
        logging.info('Authenticating')
        # Diffie-Hellman Group 14 2024-bit Key exchange values
        p = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3BE39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF
        g = 0x2

        # Client Mode
        if (mode == Mode.CLIENT):

            # First message to server in the form:
            # "client_msg, ra, HMAC"
            #       client_msg: "I'm client"
            #       ra        : client generated nonce
            #       HMAC      : HMAC of all previous bytes with shared secret key Kab
            ra   = Random.get_random_bytes(NUM_BYTES_NONCE)

            print('Client DEBUG')
            print(type(ra))
            print(list(ra))
            print(str(ra))
            print('Client DEBUG')

            #hmac = get_hmac(client_auth_str + str(ra), shared_secret_key)
            msg  = [client_auth_str, ra]#, hmac]
            # msg  = codecs.encode(pickle.dumps(msg), 'base64').decode()
            msg = pickle.dumps(msg)
            print('Client: Sent ' + (client_auth_str + "," + str(ra)))
            try:
                sender_q.put(msg)#, True, TIMEOUT_DELAY)
            except :
                print("Timed out writing client's first message")
                return None

            # Expect server response in the form:
            # "rb, E("server_msg, ra, B", Kab), HMAC"
            #       rb        : new nonce from server
            #       server_msg: "I'm server"
            #       ra        : return of previously generated nonce
            #       B         : server generated half of diffie-hellman (g^b mod p)
            #       Kab       : shared secret key between client and server
            #       HMAC      : HMAC of all previous bytes with shared secret key Kab
            try:
                resp = receiver_q.get(True, TIMEOUT_DELAY)
            except:
                auth_error = True
                print("Timed out waiting for server's first reply")
                return None
            try:
                print('CLIENT')
                print(resp)
                resp       = pickle.loads(resp)
                print('Loaded pickle')
                print(resp)
                rb         = resp[0]
                ciphertext = resp[1]
                # hmac       = resp[2]
                # if (verify_hmac(ciphertext, hmac, shared_secret_key)):
                #     print("HMAC is incorrect")
                #     return None
                plaintext = Encryption.decrypt(ciphertext, shared_secret_key)
            except Exception as e:
                print("Message from server wasn't formatted correctly")
                print('Error: ' + str(e))
                auth_error = True
                return None

            try:
                plaintext = pickle.loads(plaintext)
                server_msg = plaintext[0]
                ra_reply   = plaintext[1]
                B          = int(plaintext[2])
                if (server_msg != server_auth_str):
                    print("Message from server didn't say 'I'm server'")
                    return None
                if (ra_reply != ra):
                    print("Reterned nonce ra_reply not equal sent nonce ra")
                    return None
            except Exception as e:
                print("Message from server wasn't formatted correctly")
                print('Error: ' + str(e))
                auth_error = True
                return None

            # Send final authorization message in the form:
            # "E("client_msg, rb, A", Kab), HMAC"
            #       client_msg: "I'm client"
            #       rb        : nonce received from server
            #       A         : client generated half of diffie-hellman (g^a mod p)
            #       Kab       : shared secret key between client and server
            #       HMAC      : HMAC of all previous bytes with shared secret key Kab
            a = Random.get_random_bytes(NUM_BYTES_DH)
            a_int = int.from_bytes(a, byteorder='big')
            print('Client: a generated ' + str(a_int))
            A = pow(g, a_int, p)
            print('Client: A generated ' + str(A))
            plaintext  = [client_auth_str, rb, A]
            plaintext  = pickle.dumps(plaintext)
            ciphertext = Encryption.encrypt(plaintext, shared_secret_key)
            print('Client: ciphertext: ' + str(ciphertext))
            #hmac       = get_hmac(ciphertext, shared_secret_key)
            msg        = [ciphertext]#, hmac]
            msg        = pickle.dumps(msg)
            print('Client: Generated ciphertext ' + str(ciphertext))
            try:
                sender_q.put(msg)#self, msg, True, TIMEOUT_DELAY)
            except:
                print("Timed out writing client's second message")
                auth_error = True
                return None

            # Calculate newly established session key
            dh = pow(B, a_int, p)
            print('Client: session key - ' + str(dh))
            logging.info('Client: session key - ' + str(dh))

            return dh



        # Server Mode
        else:

            # Wait for message from client in the form:
            # "client_msg, ra, HMAC"
            #       client_msg: "I'm client"
            #       ra        : client generated nonce
            #       HMAC      : HMAC of all previous bytes with shared secret key Kab
            while (1):
                try:
                    resp = receiver_q.get(True, TIMEOUT_DELAY)#self, True)#, TIMEOUT_DELAY)
                    break
                except:
                    print("Still waiting for client's first message")
                    continue
            try:
                print('Server received ' + str(resp))
                resp = pickle.loads(resp)
                client_msg = resp[0]
                ra         = resp[1]
                #hmac       = resp[2]
                if (client_msg != client_auth_str):
                    print("Message from client didn't say 'I'm client'")
                    return None
                # if (hmac != get_hmac(client_msg + ra, shared_secret_key)):
                #     print("HMAC is incorrect")
                #     return None
            except Exception as e:
                print("Message from client wasn't formatted correctly")
                print('Exception: ' + str(e))
                auth_error = True
                return None

            # Send reply to client in the form:
            # "rb, E("server_msg,ra,dh_b", Kab), hmac
            #       rb        : server generated nonce
            #       server_msg: "I'm server"
            #       ra        : nonce received from client
            #       B         : server generated half of diffie-hellman (g^b mod p)
            #       Kab       : shared secret key between client and server
            #       HMAC      : HMAC of all previous bytes with shared secret key Kab
            rb = Random.get_random_bytes(NUM_BYTES_NONCE)
            b = Random.get_random_bytes(NUM_BYTES_DH)
            b_int = int.from_bytes(b, byteorder='big')
            print('Server: b generated ' + str(b_int))
            B = pow(g, b_int, p)
            print('Server generated B: ' + str(B))
            plaintext  = [server_auth_str, ra, B]
            # Make sure that it can be represented as a string
            plaintext  = pickle.dumps(plaintext)
            ciphertext = Encryption.encrypt(plaintext, shared_secret_key)
            print('Server: ciphertext: ' + str(ciphertext))
            hmac       = get_hmac(str(rb) + str(ciphertext), shared_secret_key)
            msg        = [rb, ciphertext]#, hmac]
            msg        = pickle.dumps(msg)
            print('Server: Message: ' + str(rb) + ',' + str(ciphertext))
            try:
                sender_q.put(msg)#, msg, True, TIMEOUT_DELAY)
            except:
                print("Timed out writing server's first message")
                auth_error = True
                return None

            # Wait for final message from client in the form:
            # "E("client_msg, rb, A", Kab), HMAC"
            #       client_msg: "I'm client"
            #       rb        : return of previously generated nonce
            #       A         : client generated half of diffie-hellman (g^a mod p)
            #       Kab       : shared secret key between client and server
            #       HMAC      : HMAC of all previous bytes with shared secret key Kab
            try:
                resp = receiver_q.get()#self, True, TIMEOUT_DELAY)
            except:
                print("Timed out waiting for client's second message")
                auth_error = True
                return None
            try:
                resp = pickle.loads(resp)
                ciphertext = resp[0]
                #hmac       = resp[1]
                # if (verify_hmac(ciphertext, hmac, shared_secret_key)):
                #     print("HMAC is incorrect")
                #     return None
                plaintext  = Encryption.decrypt(ciphertext, shared_secret_key)
                plaintext  = pickle.loads(plaintext)
                client_msg = plaintext[0]
                rb_reply   = plaintext[1]
                A          = int(plaintext[2])
                print('Server: ' + str(A))
                print('Server: plaintext received: ' + str(plaintext))
                if (client_msg != client_auth_str):
                    print("Message from client didn't say 'I'm client'")
                    return None
                if (rb_reply != rb):
                    print("Reterned nonce rb_reply not equal sent nonce rb")
                    return None
            except Exception as e:
                print("Message from client wasn't formatted correctly")
                print(e)
                auth_error = True
                return None

            dh = pow(A, b_int, p)
            print('Server: session key - ' + str(dh))
            logging.info('Server: session key - ' + str(dh))
            return dh
