import socket
import threading

from ui import *
from Queue import Queue
from sender import Sender
from receiver import Receiver
from logger import Logger

class Server(object):

    def __init__(self, port, shared_key, connected_callback, debug, debug_continue):
    #ToDo: authentication??
    self.port = port
    self.shared_key = shared_key
    self.connected_callback = connected_callback
    self.debug_continue = debug_continue
    self.debug = debug
    self.session_key = ""
    self.is_server = True
    self.waiting = True
    self.authenticated = False

    #Queue: implements multi-producer, multi-consumer queues.
    #It is especially useful in threaded programming when information must be exchanged safely between multiple threads
    self.out_queue = Queue(); #sending out queue
    self.in_queue = Queue();  #receiving queue
    self.sender = None
    self.receiver = None

    def setup(self):
        try:
            #create socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #SO_REUSEADDR flag tells the kernel to reuse a local socket in TIME_WAIT state, without waiting for its natural timeout to expire
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except socket.error:
            return (-1, "Failed to Create Socket")

        try:
            #bind socket to port
            self.socket.bind('', self.port)
            #listens for connection made with socket
            Logger.log("Listening for connections...", self.is_server)
            self.socket.listen(1)
        except socket.error:
            return (-1, "Failed to bind socket to port: " + str(self.port))

        return (0, "VPN server setup to listen on port: " + str(self.port))

    def send(self, msg):
        #authentication?
        #encrypted_msg =
        print(msg)
        self.out_queue.put(msg)

    def receive(self):
        #check if there are messaging in receiving queue
        if not self.in_queue.empty():
            msg = self.in_queue.get();
            #msg = decrypt(msg, self.session_key)
            #integrity check?
            Logger.log("message: " =  msg, self.is_server)
            return msg
        else:
            return None

     def start(self, callback=None):
        self.listener = Listener(self.socket, self.shared_key, self, self.connected_callback)
        self.listener.start()

    def bind(self, client_socket):
        self.debug_contine.disabled = self.debug
        #server sender and receiver
        self.sender = Sender(client_socket, self.out_queue, self)
        self.receiver = Receiver(client_socket, self.in_queue, self)
        self.sender.start();
        self.receiver.start()

    def close(self):
        Logger.log("Connection closing", self.is_self)
        self.in_queue.queue.clear()
        self.out_queue.queue.clear()
        self.socket.close()
        if self.sender:
            self.sender.close()
        if self.receiver:
            self.receiver.close()
