import socket
import threading
import struct
import logging

class Sender(threading.Thread):

    def __init__(self, socket, queue):
        print('Initializing Sender')
        threading.Thread.__init__(self)
        self.socket = socket
        self.queue = queue
        self.keep_alive = True
        self.socket.setblocking(False)

    def run(self):
        print('Sender Running')
        while (self.keep_alive):
            if not self.queue.empty():
                print('Sender has item in queue')
                msg = self.queue.get()
                try:
                    self.socket.send(msg.encode())
                    print('Sender sent msg successfuly')
                except socket.error:
                    print('Sender socket error')
        self.socket.close()

    def close(self):
        print('closing')
        self.keep_alive = False
