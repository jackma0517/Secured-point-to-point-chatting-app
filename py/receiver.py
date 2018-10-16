import socket
import threading
import errno
import struct
import logging

class Receiver(threading.Thread):

    def __init__(self, socket, queue):
        print('Initializing Reciever')
        threading.Thread.__init__(self)
        self.socket = socket
        self.queue = queue
        
        # TODO: What if we set to True?
        self.socket.setblocking(False) 
        self.keep_alive = True

    def run(self):
        print('Receiver Running')
        # TODO: Does this work? 
        while (self.keep_alive):
            try:
                data = self.socket.recv(1024).decode()
                if (data):
                    print('Reciever received from socket: ' + str(data))
            except:
                continue
            

    def close(self):
        print('closing')
        self.keep_alive = False
