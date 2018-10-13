import socket
import threading

from ui import *
from Queue import Queue
from sender import Sender
from receiver import Receiver
from logger import Logger

class Client(object):

    def __init__(self, ip_addr, port, shared_key):
        self.ip_addr = ip_addr
        self.port = port
        self.shared_key = shared_key
        self.is_server = False

        #Queue: implements multi-producer, multi-consumer queues.
        #It is especially useful in threaded programming when information must be exchanged safely between multiple threads
        self.out_queue = Queue(); #sending out queue
        self.in_queue = Queue();  #receiving queue
        self.sender = None
        self.receiver = None

        self.waiting = True
        self.authenticated = False


    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #SO_REUSEADDR flag tells the kernel to reuse a local socket in TIME_WAIT state, without waiting for its natural timeout to expire
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except socket.error:
            return (-1, "Failed to Create Socket")

        #authenticate with server?
        try:
            self.socket.settimeout(10)
            self.socket.connect(self.ip_addr, self.port)
            self.waiting = False
            self.bind()

            Logger.log("connected to server", self.is_server)
            self.clear_queues()
            return (0, "Connected to (%s, %i)" % (self.ip_addr, self.port))
        except socket.error:
            self.authenticated = False
            return (-1, "Could not connect to (%s, %i)" % (self.ip_addr, self.port))

        return (-1, "Could not connect to (%s, %i)" % (self.ip_addr, self.port))


    def clear_queues(self):
        self.in_queue.queue.clear()
        self.out_queue.queue.clear()

    def bind(self):
        self.sender = Sender(self.socket, self.send_queue, self)
        self.receiver = Receiver(self.socket, self.receive_queue, self)
        self.sender.start()
        self.receiver.start()

    def send(self, msg):
        #encrypted_msg =
        self.out_queue.put(msg)
        Logger.log("put message in send queue: " + msg, self.is_server)

    def receive(self):
        if (not self.in_queue.empty()):
            msg = self.in_queue.get()
            Logger.log("Received decrypted msg: "+ msg, self.is_server)
            #msg = decrypt(msg, server.session_key)
            #integrity check?
            return msg
        else:
            return None

    def close(self):
        Logger.log("Connection closing", self.is_server)
        self.in_queue.queue.clear()
        self.out_queue.queue.clear()
        if self.sender:
            self.sender.close()
        if self.receiver:
            self.receiver.close()
        self.waiting = True
        self.authenticated = False
