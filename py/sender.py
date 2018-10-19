import socket
import threading
import struct
import logging
from encryption import Encryption
from debug import wait_if_debug, Token


class Sender(threading.Thread):
    """
    This thread abstracts all the socket communication between
    the client and the server using a queue. 
    It is responsible for sending all the messages in the queue
    through the socket.
    """

    def __init__(self, socket, queue, debug_token):
        logging.info('Initializing sender thread...')
        threading.Thread.__init__(self)
        self.socket = socket
        self.queue = queue
        self.keep_alive = True
        self.socket.setblocking(False)
        self.authentication = False
        self.key = None
        self.debug_token = debug_token

    def run(self):
        while (self.keep_alive):
            if not self.queue.empty():
                msg = self.queue.get()
                logging.info('SENDING: Message to be sent: ' + str(msg))
                wait_if_debug(self.debug_token)
                if self.authentication:
                    #dont use hmac version
                    #msg = Encryption.encryptPack(msg, self.key)
                    msg = Encryption.encrypt(msg ,self.key)
                    logging.info('SENDING: Message encrypted: ' + str(msg))
                    wait_if_debug(self.debug_token)
                try:
                    self.socket.send(msg)
                except socket.error as e:
                    logging.error('Socket error' + str(e))
        self.socket.close()

    def completeAuthentication(self, key):
            self.authentication = True
            self.key = key

    def close(self):
        self.keep_alive = False
