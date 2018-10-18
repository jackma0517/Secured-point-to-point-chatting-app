
# The mode the program is operating in
class Mode:
    SERVER = 'SERVER'
    CLIENT = 'CLIENT'

class State:
    DISCONNECTED = 'DISCONNECTED'
    AUTHENTICATING = 'AUTHENTICATING'
    AUTHENTICATED = 'AUTHENTICATED'
    COMMUNICATING = 'COMMUNICATING'

class AuthResult():
    def __init__(self):
        self.dh = None
        self.error = False
        self.note = None
