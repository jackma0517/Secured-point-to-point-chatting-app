import socket
import threading
import errno
import struct
import logging

class Receiver(threading.Thead):

    def __init__(receiver, socket, queue, conn):
        #threading.Thread.__init__(self)
        #receiver.socket = socket
        #receiver.queue = queue
        #receiver.conn = conn
        #receiver.keep_alive = True

    def run(self):
        #self.socket.setblocking(0)

        #while (self.keep_alive):
            #try:

            #except socket.error as e:
                #Logger.log("error receiving message over socket: " + socket.error.args[0])
        #self.socket.close()

    def close(self):
        #self.keep_alive = False
