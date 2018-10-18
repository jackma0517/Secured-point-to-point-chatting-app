
import threading


class Listener(threading.Thread):

    def __init__(self, socket, port, conn_socket):
        print('Initializing UI Thread')
        threading.Thread.__init__(self)
        self.socket = socket
        self.port = port
        self.conn_socket = conn_socket

    def run(self):
        print('UI waiting for connection')
        self.socket.listen()
        print('Server listening on: ' + str(self.port))
        while True:
            c, _ = self.socket.accept()
            self.conn_socket = c
            print('Server connected to client')
            break
