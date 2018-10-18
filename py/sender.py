import socket
import threading
import struct
import logging
from encryption import Encryption

class Sender(threading.Thread):

    def __init__(self, socket, queue):
        print('Initializing Sender')
        threading.Thread.__init__(self)
        self.socket = socket
        self.queue = queue
        self.keep_alive = True
        self.socket.setblocking(False)
        self.authentication = False
        self.key = None

    def run(self):
        print('Sender Running')
        while (self.keep_alive):
            if not self.queue.empty():
                msg = self.queue.get()
                if self.authentication:
                    msg = Encryption.encryptPack(msg, self.key)
                try:
                    self.socket.send(msg)
                    print('Sender sent msg successfuly')
                except socket.error:
                    print('Sender socket error')
        self.socket.close()

    def completeAuthentication(self, key):
            self.authentication = True
            self.key = key

    def close(self):
        print('closing')
        self.keep_alive = False
