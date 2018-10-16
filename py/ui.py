#!/usr/bin/python3

# Throwing M - V - C conventions away for this quick hack.
# Apologies if it offends your sensibilities
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

from receiver import Receiver
from sender import Sender
import server
import client

import socket
import queue

# The mode the program is operating in
class Mode:
    SERVER = 'SERVER'
    CLIENT = 'CLIENT'

class State:
    def __init__(self):
        self.mode = Mode.CLIENT
        self.is_connected = False

class Application(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.state = State()

        # String Variables
        self.str_mode = tk.StringVar()
        self.str_mode.set(self.state.mode)

        self.create_widgets()
        self.receiver = None
        self.sender = None
        self.conn_socket = None
        self.receiver_q = queue.Queue()
        self.sender_q = queue.Queue()

    
    def is_initialized(self):
        """
        Checks whether connections are initialized
        """
        # return (self.receiver != None) & (self.sender != None)
        return self.conn_socket != None


    def create_widgets(self):

        # Frame for Mode toggles and IP/Port
        self.fr_modes = tk.Frame(self)
        self.fr_modes.pack()

        # Mode Toggle Button
        self.bt_toggle = tk.Button(master=self.fr_modes, text='Toggle Mode', command=self.toggle_mode)
        self.bt_toggle.pack(side='left')

        # Mode Text UI
        self.lbl_mode = tk.Label(master=self.fr_modes, textvariable=self.str_mode)
        self.lbl_mode.config(bg=root.cget('bg'), width=15, height=1)
        self.lbl_mode.pack(side='left')

        # IP Config
        self.lbl_ip = tk.Label(master=self.fr_modes, text='IP: ')
        self.lbl_ip.pack(side='left')
        self.txt_ip = tk.Text(master=self.fr_modes)
        self.txt_ip.config(width=15, height=1)
        self.txt_ip.pack(side='left')

        # Port Config
        self.lbl_port = tk.Label(master=self.fr_modes, text='Port: ')
        self.lbl_port.pack(side='left')
        self.txt_port = tk.Text(master=self.fr_modes)
        self.txt_port.config(width=15, height=1)
        self.txt_port.pack(side='left')


        # Textmessage boxes
        self.fr_msg_boxes = tk.Frame(self)
        self.fr_msg_boxes.pack()

        # Shared secret key
        self.lbl_secret_key = tk.Label(master=self.fr_msg_boxes, text='Shared Secret Key:')
        self.lbl_secret_key.pack()
        self.txt_secret_key = ScrolledText(master=self.fr_msg_boxes)
        self.txt_secret_key.config(width=100, height=4)
        self.txt_secret_key.pack()

        self.lbl_sent = tk.Label(master=self.fr_msg_boxes, text='Data to be Sent:')
        self.lbl_sent.pack()
        self.txt_sent = ScrolledText(master=self.fr_msg_boxes)
        self.txt_sent.config(width=100, height=4)
        self.txt_sent.pack()

        # Send Button
        self.send_button = tk.Button(self, text='SEND', fg='green', command=self.send_message)
        self.send_button.place(rely=2.0, relx=2.0, x=0, y=0, anchor=tk.SE)
        self.send_button.pack()


        self.lbl_received = tk.Label(master=self.fr_msg_boxes, text='Data to be Received:')
        self.lbl_received.pack()
        self.txt_received = ScrolledText(master=self.fr_msg_boxes)
        self.txt_received.config(width=100, height=4)
        self.txt_received.pack()
        
        # End Me
        self.quit = tk.Button(self, text='QUIT', fg='red', command=root.destroy)
        self.quit.place(rely=1.0, relx=1.0, x=0, y=0, anchor=tk.SE)
        self.quit.pack()
        self.refresh_ui()

        self.btn_client_connect = tk.Button(self, text='Connect to Server', fg='green', command=self.client_connect)
        self.btn_client_connect.pack()

        # Since client is default, don't add the server button
        self.btn_server_start = tk.Button(self, text='Start Server', fg='green', command=self.server_start)


    def consume(self, root):
        """
        This is where we start reading/writing to the
        Receiver and Sender
        """
        if self.is_initialized():
            print('Consuming...')
            # if not self.receiver_q.empty():
            #     print('Receiving msg')
            # if not 
            
        root.after(250, lambda: self.consume(root))
        

    def bootstrap_connection(self):
        self.receiver = Receiver(self.conn_socket, self.receiver_q)
        self.sender = Sender(self.conn_socket, self.sender_q)

    def get_port(self):
        return self.txt_port.get('1.0', 'end-1c')

    def get_ip(self):
        return self.txt_ip.get('1.0', 'end-1c')


    def client_connect(self):
        print('Client connect...')
        # TODO: Move into its own thread?  
        #          this will block the UI thread
        port = self.get_port()
        ip = self.get_ip()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.connect((ip, int(port)))
        self.conn_socket = s
        print('Client connected to server')

    def server_start(self):
        print('Starting server...')
        # TODO: Move into its own thread?  
        #          this will block the UI thread
        port = self.get_port()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', int(port)))
        s.listen()
        print('Server listening on: ' + str(port))
        while True:
            c, _ = s.accept()
            self.conn_socket = c
            print('Server connected to client')
            break


    def refresh_ui(self):
        print('why do i exist')

    def say_hi(self):
        print('Hi folks\n')

    def toggle_mode(self):
        if (self.state.mode == Mode.CLIENT):
            self.state.mode = Mode.SERVER
            # Disable the IP config
            self.txt_ip.config(background=root['bg'])
            self.txt_ip.config(state='disabled')
            #server connect button
            self.btn_server_start.pack()
            self.btn_client_connect.pack_forget()
        else:
            self.state.mode = Mode.CLIENT
            # Enable the IP config
            self.txt_ip.config(background='white')
            self.txt_ip.config(state='normal')
            self.btn_client_connect.pack()
            self.btn_server_start.pack_forget()

        self.str_mode.set(self.state.mode)

    def send_message(self):
        if (self.state.mode == Mode.CLIENT):
            print('Client Mode')
        else:
            print('Server Mode')

    def display_received_message(self, response):
        self.txt_received.insert("end-1c", response)

    def server_connect(self):
        # Threading? 
        print('Connecting server')




if __name__ == '__main__':
    root = tk.Tk()
    app = Application(master=root)
    app.consume(root)
    app.mainloop()
