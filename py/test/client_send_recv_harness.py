import sys
sys.path.append('..')
import pickle
import socket

from receiver import Receiver
from sender import Sender


def main():
    # Create mock socket
    port = 5555
    ip = 'localhost'
    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    c.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    c.connect((ip, port))

    receiver = Receiver()


    





if __name__ == '__main__':
    main()