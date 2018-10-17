# Written by Sawyer
import math
import base64
from ui import Mode
from encryption import Encryption
from Crypto.Hash import SHA256
from Crypto import Random
from Crypto.Cipher import AES


client_auth_str = "I'm client"
server_auth_str = "I'm server"
NUM_BYTES_DH    = 32 # Going for 256-bit a/b values in diffie-hellman
NUM_BYTES_NONCE = 8  # Going for 64-bit nonce
TIMEOUT_DELAY   = 5  # Timeout waiting on response after 5 seconds

# Diffie-Hellman Group 14 2024-bit Key exchange values
p = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3BE39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF
g = 0x2

def authenticate(self, shared_secret_key):

    # Client Mode
    if (self.state.mode == Mode.CLIENT):

        # First message to server in the form:
        # "client_msg,ra"
        #       client_msg: "I'm client"
        #       ra        : client generated nonce
        ra = Random.get_random_bytes(NUM_BYTES_NONCE)
        msg = client_auth_str + "," + str(ra)
        try:
            self.receiver_q.put(self, msg, True, TIMEOUT_DELAY)
        except:
            print("Timed out writing client's first message")
            return False

        # Expect server response in the form:
        # "rb,E("server_msg, ra, B", Kab)
        #       rb        : new nonce from server
        #       server_msg: "I'm server"
        #       ra        : return of previously generated nonce
        #       B         : server generated half of diffie-hellman (g^b mod p)
        #       Kab       : shared secret key between client and server
        try:
            resp = self.receiver_q.get(self, True, TIMEOUT_DELAY)
        except:
            print("Timed out waiting for server's first reply")
            return False
        try:
            rb,ciphertext = resp.slit(",")
            rb = int(rb)
            plaintext = Encryption.decrypt(self, ciphertext, shared_secret_key)
        except:
            print("Message from server wasn't formatted correctly")
            return False
        
        try:
            server_msg, ra_reply, B = plaintext.split(",")
            ra_reply = int(ra_reply)
            B = int(B)
            if (server_msg != server_auth_str):
                print("Message from server didn't say 'I'm server'")
                return False
            if (ra_reply != ra):
                print("Reterned nonce ra_reply not equal sent nonce ra")
                return False
        except:
            print("Message from server wasn't formatted correctly")
            return False

        # Send final authorization message in the form:
        # E("client_msg, rb, A", Kab)
        #       client_msg: "I'm client"
        #       rb        : nonce received from server
        #       A         : client generated half of diffie-hellman (g^a mod p)
        #       Kab       : shared secret key between client and server
        a = Random.get_random_bytes(NUM_BYTES_DH)
        A = g**a % p
        plaintext = client_auth_str + "," + str(rb) + "," + str(A)
        ciphertext = Encryption.encrypt(self, plaintext, shared_secret_key)
        msg = ciphertext
        try:
            self.receiver_q.put(self, msg, True, TIMEOUT_DELAY)
        except:
            print("Timed out writing client's second message")
            return False

        # Calculate newly established session key
        dh = a**B % p

        return dh



    # Server Mode
    else:

        # Wait for message from client in the form:
        # "client_msg, ra"
        #       client_msg: "I'm client"
        #       ra        : client generated nonce
        try:
            resp = self.receiver_q.get(self, True, TIMEOUT_DELAY)
        except:
            print("Timed out waiting for client's first message")
            return False
        try:
            client_msg,ra = resp.split(",")
            ra = int(ra)
            if (client_msg != client_auth_str):
                print("Message from client didn't say 'I'm client'")
                return False
        except:
            print("Message from client wasn't formatted correctly")
            return False

        # Send reply to client in the form:
        # "rb,E("server_msg,ra,dh_b", Kab)
        #       rb        : server generated nonce
        #       server_msg: "I'm server"
        #       ra        : nonce received from client
        #       B         : server generated half of diffie-hellman (g^b mod p)
        #       Kab       : shared secret key between client and server
        rb = Random.get_random_bytes(NUM_BYTES_NONCE)
        b = Random.get_random_bytes(NUM_BYTES_DH)
        B = g**b % p
        plaintext = server_auth_str + "," + str(ra) + "," + str(B)
        ciphertext = Encryption.encrypt(self, plaintext, shared_secret_key)
        msg = rb + ciphertext
        try:
            self.receiver_q.put(self, msg, True, TIMEOUT_DELAY)
        except:
            print("Timed out writing server's first message")
            return False

        # Wait for final message from client in the form:
        # E("client_msg, rb, A", Kab)
        #       client_msg: "I'm client"
        #       rb        : return of previously generated nonce
        #       A         : client generated half of diffie-hellman (g^a mod p)
        #       Kab       : shared secret key between client and server
        try:
            resp = self.receiver_q.get(self, True, TIMEOUT_DELAY)
        except:
            print("Timed out waiting for client's second message")
            return False
        plaintext = Encryption.decrypt(self, resp, shared_secret_key)
        try:
            client_msg, rb_reply, A = plaintext.split(",")
            rb_reply = int(rb_reply)
            A = int(A)
            if (client_msg != client_auth_str):
                print("Message from client didn't say 'I'm client'")
                return False
            if (rb_reply != rb):
                print("Reterned nonce rb_reply not equal sent nonce rb")
                return False
        except:
            print("Message from client wasn't formatted correctly")
            return False
        
        dh = b**A % p
        return dh