import threading

class ServerListener(threading.Thread):
    """
    This thread handles socket listening of incoming connections
    from clients. It is configured to handle one client at a time
    then stop listening. To re-enable accepting new clients, you 
    must toggle the accept_new_connection() function.
    """

    def __init__(self, socket, socket_handler):
        threading.Thread.__init__(self)
        self.socket = socket
        self.cb_function = socket_handler
        self.is_listening = True
        self.keep_alive = True

    def run(self):
        self.socket.listen()
        while self.keep_alive:
            if self.is_listening:
                c, _ = self.socket.accept()
                self.cb_function(c)
                self.is_listening = False
    
    def accept_new_connection(self):
        self.is_listening = True
    
    def close(self):
        self.keep_alive = False

