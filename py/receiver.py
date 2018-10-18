import socket
import threading
import errno
import struct
import logging
from encryption import Encryption
class Receiver(threading.Thread):

    def __init__(self, socket, queue):
        print('Initializing Reciever')
        threading.Thread.__init__(self)
        self.socket = socket
        self.queue = queue
        self.socket.setblocking(False) 
        self.keep_alive = True
        self.authentication = False
        self.key = None

    def run(self):
        print('Receiver Running')
        
        while (self.keep_alive):
            try:
                data = self.socket.recv(1024)
                if (data):
                    if self.authentication:
                        #dont use hmac version
                        #data = Encryption.decryptVerify(data, self.key)
                        data = Encryption.decrypt(data, self.key)
                    print('Reciever received from socket: ' + str(data))
                    self.queue.put(data)
            except:
                continue
            
    def completeAuthentication(self, key):
        self.authentication = True
        self.key = key


    def close(self):
        print('closing')
        self.keep_alive = False
