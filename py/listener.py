import threading

class ServerListener(threading.Thread):

    def __init__(self, socket, socket_handler):
        threading.Thread.__init__(self)
        self.socket = socket
        self.cb_function = socket_handler
        self.is_listening = True

    def run(self):
        print('ServerListener: waiting for connection')
        self.socket.listen()
        while True:
            if self.is_listening:
                c, _ = self.socket.accept()
                self.cb_function(c)
                self.is_listening = False
    
    def accept_new_connection(self):
        self.is_listening = True

