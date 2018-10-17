
# The mode the program is operating in
class Mode:
    SERVER = 'SERVER'
    CLIENT = 'CLIENT'

class State:
    DISCONNECTED = 'DISCONNECTED'
    AUTHENTICATING = 'AUTHENTICATING'
    COMMUNICATING = 'COMMUNICATING'