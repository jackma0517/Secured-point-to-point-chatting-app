import socket
import threading
import errno
import struct

from logger import Logger

class Receiver(threading.Thead):

    def __init__(receiver, socket, queue, conn):
        threading.Thread.__init__(self)
        receiver.socket = socket
        receiver.queue = queue
        receiver.conn = conn
        receiver.keep_alive = True

    #ToDo:
