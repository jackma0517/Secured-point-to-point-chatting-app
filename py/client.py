#CLIENT
import socket


# Create a socket object
def send(ip, port, msg):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Define the port on which you want to connect
    #port = 50000

    # connect to the server on computer in LAN
    # Uses IPv4 Address wireless
    # can be found with command "ipconfig" in command prompt
    addr = (ip)
    s.connect((ip, int(port)))
    s.sendall(msg.encode())

    # receive data from the server
    #print (s.recv(1024))
    return s.recv(1024)
# close the connection
#s.close()
