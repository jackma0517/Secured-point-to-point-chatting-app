# Written by Sawyer

import math
import base64
import codecs # base64
from encryption import Encryption
from hash_mac import *
from Crypto.Hash import SHA256
from Crypto import Random
from Crypto.Cipher import AES
from config import Mode, AuthResult
from debug import wait_if_debug
import pickle
import logging

class Authentication:


    def authenticate(self, shared_secret_key, receiver_q, sender_q, mode, auth_res, token):
        """
        Authenticates server and client, returns a session key
        """
        client_auth_str = "I'm client"
        server_auth_str = "I'm server"
        NUM_BYTES_DH    = 32 # Going for 256-bit a/b values in diffie-hellman
        NUM_BYTES_NONCE = 8  # Going for 64-bit nonce
        TIMEOUT_DELAY   = 5  # Timeout waiting on response after 5 seconds
        logging.info('Authenticating')

        # Diffie-Hellman Group 14 2024-bit Key exchange values
        p = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3BE39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF
        g = 0x2

        # Client Mode
        if (mode == Mode.CLIENT):

            # First message to server in the form:
            # "client_msg, ra"
            #       client_msg: "I'm client"
            #       ra        : client generated nonce
            ra   = Random.get_random_bytes(NUM_BYTES_NONCE)
            msg  = [client_auth_str, ra]
            msg = pickle.dumps(msg)
            wait_if_debug(token)
            logging.info("Message to send: " + client_auth_str + "," + str(ra))
            try:
                wait_if_debug(token)
                sender_q.put(msg, True, TIMEOUT_DELAY)
            except :
                auth_res.error = True
                logging.info("Timed out writing client's first message")
                return

            # Expect server response in the form:
            # "rb, E("server_msg, ra, B", Kab)"
            #       rb        : new nonce from server
            #       server_msg: "I'm server"
            #       ra        : return of previously generated nonce
            #       B         : server generated half of diffie-hellman (g^b mod p)
            #       Kab       : shared secret key between client and server
            try:
                if (token.debug):
                    resp = receiver_q.get(True)
                else:
                    resp = receiver_q.get(True, TIMEOUT_DELAY)
            except:
                auth_res.error = True
                wait_if_debug(token)
                logging.info("Timed out waiting for server's first reply")
            try:
                resp       = pickle.loads(resp)
                rb         = resp[0]
                ciphertext = resp[1]
                logging.info("Ciphertext received from server: " + str(ciphertext))
                plaintext = Encryption.decrypt(ciphertext, shared_secret_key)
                wait_if_debug(token)
            except Exception as e:
                logging.info("Message from server wasn't formatted correctly")
                logging.info('Error: ' + str(e))
                auth_res.error = True
                return
            
            try:
                plaintext = pickle.loads(plaintext)
                server_msg = plaintext[0]
                ra_reply   = plaintext[1]
                B          = int(plaintext[2])
                logging.info("Plaintext received: ")
                logging.info('Server message: ' + str(server_msg))
                logging.info('ra returned: ' + str(ra_reply))
                logging.info('Server B: ' + str(B))
                wait_if_debug(token)
                if (server_msg != server_auth_str):
                    logging.info("Message from server didn't say 'I'm server'")
                    auth_res.error = True
                    return
                if (ra_reply != ra):
                    logging.info("Reterned nonce ra_reply not equal sent nonce ra")
                    auth_res.error = True
                    return
            except Exception as e:
                logging.info("Message from server wasn't formatted correctly")
                logging.info('Error: ' + str(e))
                wait_if_debug(token)
                auth_res.error = True
                return

            # Send final authorization message in the form:
            # "E("client_msg, rb, A", Kab)"
            #       client_msg: "I'm client"
            #       rb        : nonce received from server
            #       A         : client generated half of diffie-hellman (g^a mod p)
            #       Kab       : shared secret key between client and server
            a = Random.get_random_bytes(NUM_BYTES_DH)
            a_int = int.from_bytes(a, byteorder='big')
            A = pow(g, a_int, p)
            plaintext  = [client_auth_str, rb, A]
            logging.info("Plaintext to be sent: ")
            logging.info('Client message: ' + str(client_auth_str))
            logging.info('rb returned : ' + str(rb))
            logging.info('Client A: ' + str(A))
            wait_if_debug(token)
            plaintext  = pickle.dumps(plaintext)
            ciphertext = Encryption.encrypt(plaintext, shared_secret_key)
            logging.info("Ciphertext to be sent: " + str(ciphertext))
            wait_if_debug(token)
            msg        = [ciphertext]
            msg        = pickle.dumps(msg)
            try:
                sender_q.put(msg, True, TIMEOUT_DELAY)
                logging.info("Sending message to server...")
            except:
                logging.info("Timed out writing client's second message")
                auth_res.error = True
                return

            # Calculate newly established session key
            auth_res.dh = pow(B, a_int, p)
            logging.info("Session key: " + str(auth_res.dh))
            wait_if_debug(token)
            auth_res.error = False

        # Server Mode
        else:

            # Wait for message from client in the form:
            # "client_msg, ra"
            #       client_msg: "I'm client"
            #       ra        : client generated nonce
            while (1):
                try:
                    if (token.debug):
                        resp = receiver_q.get(True)
                        break
                    else:
                        resp = receiver_q.get(True, TIMEOUT_DELAY)
                        break
                except:
                    logging.info("Still waiting for client's first message")
                    continue
            try:
                resp = pickle.loads(resp)
                client_msg = resp[0]
                ra         = resp[1]
                logging.info("Message recieved from client")
                logging.info('Client message: ' + str(client_msg))
                logging.info('ra: ' + str(ra))
                wait_if_debug(token)
                if (client_msg != client_auth_str):
                    logging.info("Message from client didn't say 'I'm client'")
                    wait_if_debug(token)
                    auth_res.error = True
                    return
            except Exception as e:
                logging.info("Message from client wasn't formatted correctly")
                logging.info('Exception: ' + str(e))
                wait_if_debug(token)
                auth_res.error = True
                return

            # Send reply to client in the form:
            # "rb, E("server_msg,ra,dh_b", Kab)
            #       rb        : server generated nonce
            #       server_msg: "I'm server"
            #       ra        : nonce received from client
            #       B         : server generated half of diffie-hellman (g^b mod p)
            #       Kab       : shared secret key between client and server
            rb = Random.get_random_bytes(NUM_BYTES_NONCE)
            b = Random.get_random_bytes(NUM_BYTES_DH)
            b_int = int.from_bytes(b, byteorder='big')
            B = pow(g, b_int, p)
            plaintext  = [server_auth_str, ra, B]
            logging.info("Plaintext to be sent: ")
            logging.info('rb: ' + str(rb))
            logging.info('server_mgs: ' + server_auth_str)
            logging.info('ra: ' + str(ra)) 
            logging.info('B: ' + str(B))
            wait_if_debug(token)
            plaintext  = pickle.dumps(plaintext)
            ciphertext = Encryption.encrypt(plaintext, shared_secret_key)
            msg        = [rb, ciphertext]
            msg        = pickle.dumps(msg)
            logging.info('Server: Message: ' + str(rb) + ',' + str(ciphertext))
            wait_if_debug(token)
            try:
                sender_q.put(msg, True, TIMEOUT_DELAY)
                logging.info("Sending message to client...")
            except:
                logging.info("Timed out writing server's first message")
                wait_if_debug(token)
                auth_res.error = True
                return

            # Wait for final message from client in the form:
            # "E("client_msg, rb, A", Kab)"
            #       client_msg: "I'm client"
            #       rb        : return of previously generated nonce
            #       A         : client generated half of diffie-hellman (g^a mod p)
            #       Kab       : shared secret key between client and server
            try:
                if (token.debug):
                    resp = receiver_q.get(True)
                else:
                    resp = receiver_q.get(True, TIMEOUT_DELAY)
            except:
                logging.info("Timed out waiting for client's second message")
                wait_if_debug(token)
                auth_res.error = True
                return
            try:
                resp = pickle.loads(resp)
                ciphertext = resp[0]
                logging.info('Ciphertext received: ' + str(ciphertext))
                wait_if_debug(token)
                plaintext  = Encryption.decrypt(ciphertext, shared_secret_key)
                plaintext  = pickle.loads(plaintext)
                client_msg = plaintext[0]
                rb_reply   = plaintext[1]
                A          = int(plaintext[2])
                logging.info('Plaintext received: ')
                logging.info('client_msg: ' + client_msg)
                logging.info('rb: ' + str(rb))
                logging.info('A: ' + str(A))
                # TODO: For some reason adding the wait below would hang the system
                #self.wait_if_debug(debug, token)
                if (client_msg != client_auth_str):
                    logging.info("Message from client didn't say 'I'm client'")
                    wait_if_debug(token)
                    auth_res.error = True
                    return
                if (rb_reply != rb):
                    logging.info("Returned nonce rb_reply not equal sent nonce rb")
                    wait_if_debug(token)
                    auth_res.error = True
                    return
            except Exception as e:
                logging.info("Message from client wasn't formatted correctly")
                logging.info(e)
                wait_if_debug(token)
                auth_res.error = True
                return 

            auth_res.dh = pow(A, b_int, p)
            logging.info("Session key: " + str(auth_res.dh))
            wait_if_debug(token)
            auth_res.error = False
            return