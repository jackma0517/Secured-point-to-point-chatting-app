import socket


def connect(port):

    # next create a socket object
    s = socket.socket()
    print ("Socket successfully created")


    #port = 50000

    # Next bind to the port
    # we have not typed any ip in the ip field
    # instead we have inputted an empty string
    # this makes the server listen to requests
    # coming from other computers on the network
    s.bind(('', int(port)))
    print ("socket binded to %s" %(int(port)))

    # put the socket into listening mode
    s.listen(5)
    print ("socket is listening")

    # a forever loop until we interrupt it or
    # an error occurs
    while True:

        # Establish connection with client.
        c, addr = s.accept()
        print ('Got connection from', addr)

        # Get data from client
        data=c.recv(1024)

        if not data:
            break

            # Send back data to client
            c.sendall(data)

    # Close the connection with the client
    c.close()
