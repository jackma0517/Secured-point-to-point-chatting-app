import socket
import threading
import struct

from logger import Logger

class Sender(threading.Thread):

    def __init__(sender, socket, queue, conn):
        threading.Thread.__init__(self)
        sender.socket = socket
        sender.queue = queue
        sender.conn = conn
        sender.keep_alive = True

    def run(sender):
        #set socket to non-blocking
        sender.socket.setblocking(0)
        while (sender.keep_alive):
            if not sender.queue.empty():
                msg = sender.queue.get()
                try:
                    sender.socket.sendall(msg)
                    Logger.log("Sending message over socket: "+ msg, sender.conn.is_server)
                except socket.error:
                    sender.conn.broken_conn_callback()
        sender.socket.close()
