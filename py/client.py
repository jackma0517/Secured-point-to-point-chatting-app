import socket
import threading

from Queue import Queue
from logger import Logger
from sender import Sender
from receiver import Receiver

class Client(object):

    def __init__(client, ip_addr, port, shared_key, broken_conn_callback, app):
        client.ip_addr = ip_addr
        client.port = port
        client.shared_key = shared_key
        client.broken_conn_callback = broken_conn_callback
        client.app = app
        client.is_server = False

        #Queue: implements multi-producer, multi-consumer queues.
        #It is especially useful in threaded programming when information must be exchanged safely between multiple threads
        client.out_queue = Queue(); #sending out queue
        client.in_queue = Queue();  #receiving queue
        client.sender = None
        client.receiver = None

    def connect(client):
        try:
            client.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #SO_REUSEADDR flag tells the kernel to reuse a local socket in TIME_WAIT state, without waiting for its natural timeout to expire
            client.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except socket.error:
            return (-1, "Failed to Create Socket")

        #authenticate with server?
        try:
            #bind socket to port
            server.socket.bind('', client.port)
        except socket.error:
            return (-1, "Failed to bind socket to port: " + str(client.port))

    def bind(client):
        #client.sender = Sender(client.socket, client.out_queue, client)
        #client.receiver = Receiver(client.socket, client.inqueue, client)

    def send(client, msg):
        #encrypted_msg =
        client.out_queue.put(encrypted_msg)

    def receive(client):
        if (not client.in_queue.empty()):
            msg = client.in_queue.get()
            #msg = decrypt(msg, server.session_key)
            #integrity check?
            return msg
        else:
            return None

    def close(client):
        Logger.log("Connection closing", client.is_server)
        client.in_queue.queue.clear()
        client.out_queue.queue.clear()
        if client.sender:
            client.sender.close()
        if client.receiver:
            client.receiver.close()
