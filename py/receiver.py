import socket
import threading
import errno
import struct
import logging
from encryption import Encryption
from debug import wait_if_debug, Token

class Receiver(threading.Thread):
    """
    This thread abstracts all the socket communication between
    the client and the server using a queue. 
    It is responsible for receiving messages through the socket
    and inserting them into the queue
    """

    def __init__(self, socket, queue, debug_token):
        logging.info('Initializing receiver thread...')
        threading.Thread.__init__(self)
        self.socket = socket
        self.queue = queue
        self.socket.setblocking(False) 
        self.keep_alive = True
        self.authentication = False
        self.key = None
        self.debug_token = debug_token

    def run(self):
        while (self.keep_alive):
            try:
                data = self.socket.recv(1024)
                if (data):
                    logging.info('RECEIVER: Recieved data: ' + str(data))
                    wait_if_debug(self.debug_token)
                    if self.authentication:
                        #dont use hmac version
                        #data = Encryption.decryptVerify(data, self.key)
                        data = Encryption.decrypt(data, self.key)
                        logging.info('RECEIVER: Decrypted data: ' + str(data))
                        wait_if_debug(self.debug_token)
                    self.queue.put(data)
            except Exception as e:
                # Nonblocking socket will always throw an 
                # exception here, it can't be separated since it
                # is propagated from the underlying implementation. 
                # So we're ignoring exceptions here for now
                # logging.info('Receiver exception: ' + str(e))
                continue
            
    def completeAuthentication(self, key):
        self.authentication = True
        self.key = key

    def close(self):
        self.keep_alive = False
