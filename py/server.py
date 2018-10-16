import socket
import threading

class Server:

    def __init__(self, port, handler):
        print('Initializing server class')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        print('Listening on: ' + str(port))
        s.bind(('', int(port)))
        print ("Server socket binded to %s" %(int(port)))
        s.listen()

        self.connection_socket = s;
        self.handler = handler;

        while True:
            c, _ = self.connection_socket.accept()
            self.handler(c)
