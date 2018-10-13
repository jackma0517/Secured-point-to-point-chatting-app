import socket
import threading

from Queue import Queue
from logger import Logger
from sender import Sender
from receiver import Receiver

class Server(object):

    def __init__(server, port, shared_key, connected_callback, broken_conn_callback,
                 debug, debug_continue, app):
    #ToDo: authentication??
    server.port = port
    server.shared_key = shared_key
    server.connected_callback = connected_callback
    server.broken_conn_callback = broken_conn_callback
    server.debug_continue = debug_continue
    server.debug = debug
    server.debug_continue = debug_continue
    server.session_key = ""
    server.app = app
    server.is_server = True

    #Queue: implements multi-producer, multi-consumer queues.
    #It is especially useful in threaded programming when information must be exchanged safely between multiple threads
    server.out_queue = Queue(); #sending out queue
    server.in_queue = Queue();  #receiving queue
    server.sender = None
    server.receiver = None

    def setup(s):
        try:
            #create socket
            server.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #SO_REUSEADDR flag tells the kernel to reuse a local socket in TIME_WAIT state, without waiting for its natural timeout to expire
            server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except socket.error:
            return (-1, "Failed to Create Socket")

        try:
            #bind socket to port
            server.socket.bind('', server.port)
            #listens for connection made with socket
            server.socket.listen(1)
        except socket.error:
            return (-1, "Failed to bind socket to port: " + str(server.port))

        return (0, "VPN server setup to listen on port: " + str(server.port))

    def send(sever, msg):
        #authentication?
        #encrypted_msg =
        server.out_queue.put(encrypted_msg)

    def receive(server):
        #check if there are messaging in receiving queue
        if not server.in_queue.empty():
            encrypted_msg = server.in_queue.get();
            #msg = decrypt(msg, server.session_key)
            #integrity check?
            return msg
        else:
            return None

    def bind(server, client_socket):
        server.debug_contine.disabled = self.debug
        #server sender and receiver
        #server.sender = Sender(client_socket, server.out_queue, server)
        #server.receiver = Receiver(client_socket, server.in_queue, server)

    def close(server):
        Logger.log("Connection closing", server.is_server)
        server.in_queue.queue.clear()
        server.out_queue.queue.clear()
        server.socket.close()
        if server.sender:
            server.sender.close()
        if server.receiver:
            server.receiver.close()
