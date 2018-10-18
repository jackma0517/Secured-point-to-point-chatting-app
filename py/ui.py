#!/usr/bin/python3

# Throwing M - V - C conventions away for this quick hack.
# Apologies if it offends your sensibilities
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter import *
from tkinter import messagebox

from receiver import Receiver
from sender import Sender
from listener import ServerListener
import server
import client
import text_handler

import socket
import queue
import threading
import logging

from authenticate import Authentication
from encryption import Encryption
from config import Mode, State, AuthResult


# Maintains config in the program
class Config:
    def __init__(self):
        self.state = State.DISCONNECTED
        self.mode = Mode.CLIENT
        self.is_connected = False

class Application(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.config = Config()

        # String Variables
        self.str_mode = tk.StringVar()
        self.str_mode.set(self.config.mode)

        self.create_widgets()
        self.receiver = None
        self.sender = None
        self.conn_socket = None
        self.receiver_q = queue.Queue()
        self.sender_q = queue.Queue()

        self.server_listener = None

        ############################
        # Authentication Variables #
        ############################
        self.auth_res = AuthResult()
        self.dh = None
        self.authentication = Authentication()

        self.debug = True

    def is_initialized(self):
        """
        Checks whether connections are initialized
        """
        return (self.receiver != None) & (self.sender != None)


    def create_widgets(self):
        """
        Code to generate the UI
        """

        # Frame for Mode toggles and IP/Port
        self.fr_modes = tk.Frame(self)
        self.fr_modes.pack()

        # Mode Toggle Button
        self.bt_toggle = tk.Button(master=self.fr_modes,
                                    text='Toggle Mode',
                                    command=self.toggle_mode)
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


        self.btn_client_connect = tk.Button(master=self.fr_modes,
                                            text='Connect to Server',
                                            fg='green',
                                            command=self.client_connect,
                                            height=1, width=15)
        self.btn_client_connect.pack()

        # Since client is default, don't add the server button
        self.btn_server_start = tk.Button(master=self.fr_modes,
                                            text='Start Server',
                                            fg='green',
                                            command=self.server_start,
                                            height=1, width=15)

        # Textmessage boxes
        self.fr_msg_boxes = tk.Frame(self)
        self.fr_msg_boxes.pack()

        # Shared secret key
        self.lbl_secret_key = tk.Label(master=self.fr_msg_boxes,
                                        text='Shared Secret Key:')
        self.lbl_secret_key.pack()
        self.txt_secret_key = ScrolledText(master=self.fr_msg_boxes)
        self.txt_secret_key.config(width=100, height=4)
        self.txt_secret_key.pack()

        # TODO: Default secret key, remove
        self.txt_secret_key.insert('end-1c', 'abc')

        # Data to be sent
        self.lbl_sent = tk.Label(master=self.fr_msg_boxes,
                                        text='Data to be Sent:')
        self.lbl_sent.pack()
        self.txt_sent = ScrolledText(master=self.fr_msg_boxes)
        self.txt_sent.config(width=100, height=4)
        self.txt_sent.pack()

        # Send Button
        self.send_button = tk.Button(master=self.fr_msg_boxes,
                                        text='SEND', fg='green',
                                        command=self.send_message)
        self.send_button.place(rely=2.0, relx=2.0, x=0, y=0, anchor=tk.SE)
        self.send_button.pack()


        # Data Recieved
        self.lbl_received = tk.Label(master=self.fr_msg_boxes,
                                        text='Data Received:')
        self.lbl_received.pack()
        self.txt_received = ScrolledText(master=self.fr_msg_boxes, state='disabled')
        self.txt_received.config(width=100, height=4)
        self.txt_received.pack()


        # Step by Step Frame
        self.fr_step = tk.Frame(self)
        self.fr_step.pack()

        # Step by step data
        self.lbl_log = tk.Label(master=self.fr_step,
                                    text='Encryption logging')
        self.lbl_log.pack()
        self.txt_log = ScrolledText(master=self.fr_step)
        self.txt_log.config(width=100, height=6, bg=root['bg'], state='normal')
        self.txt_log.pack()

        self.text_handler = text_handler.TextHandler(self.txt_log)
        # Logging configuration
        logging.basicConfig(filename='test.log',
            level=logging.INFO,
            format='%(levelname)s - %(message)s')
         # Add the handler to logger
        logger = logging.getLogger()
        logger.addHandler(self.text_handler)

        # Debug Toggle Button
        self.debug_button_txt = tk.StringVar()
        self.debug_button_txt.set("Debug Mode ON")
        self.btn_debug_toggle = tk.Button(master=self.fr_step, textvariable=self.debug_button_txt, command=self.toggle_debug)
        self.btn_debug_toggle.pack(side='left')

        # Debug Continue Button
        self.debug_continue_button = tk.Button(master=self.fr_step, text='Continue', command=self.step)
        self.debug_continue_button.pack(side='right')
        self.debug_continue_button.config(state='normal')

        # Gimpy hack to push the quit button downwards
        self.fr_space = tk.Frame(self)
        self.fr_space.config(height = 100)
        self.fr_space.pack()

        # End Me
        self.quit = tk.Button(self, text='QUIT', fg='red', command=root.destroy)
        self.quit.place(rely=1.0, relx=1.0, x=0, y=0, anchor=tk.SE)
        self.quit.pack()


    def consume(self, root):
        """
        This is where we start reading/writing to/from the
        Receiver and Sender
        """
        if (self.config.state != State.DISCONNECTED):
            if (self.config.state == State.UNSECURED_CONN):
                logging.info('Connected over unsecured network. Authenticating...')
                self.auth_res = AuthResult()
                # If we are disconnected, we run authentication on a thread.
                # TODO: Use the secret key rather than 'abc'
                threading.Thread(target = self.authentication.authenticate,
                                args=(  self.shared_key,    # shared secret key
                                        self.receiver_q,    # receiver queue
                                        self.sender_q,      # sender queue
                                        self.config.mode,   # SERVER vs CLIENT mode
                                        self.auth_res       # Contains authentication results
                                        )).start()
                self.config.state = State.AUTHENTICATING
            elif (self.config.state == State.AUTHENTICATING and self.auth_res.error == True):
                # If we are authenticating and we come into an error,
                # we reset back to the disconnected state and re-try authentication
                logging.info('Authentication failed')
                self.config.state = State.DISCONNECTED
                self.receiver = None
                self.sender = None
                if (self.config.mode == Mode.SERVER):
                    self.server_listener.accept_new_connection()
            elif (self.config.state == State.AUTHENTICATING and
                    self.auth_res.error == False and
                    self.auth_res.dh is None) :
                # Still authenticating, don't do anything but wait
                print('Still authenticating...')
            elif (self.config.state == State.AUTHENTICATING and
                self.auth_res.error == False and
                self.auth_res.dh is not None):
                # We are authentication, now we can send encrypted messages
                # back and forth
                logging.info('Authentication successful')
                self.config.state = State.AUTHENTICATED
                self.dh = self.auth_res.dh
                self.receiver.completeAuthentication(self.dh)
                self.sender.completeAuthentication(self.dh)
            else:
                print('Consuming...')
                print('Rec queue size: ' + str(self.receiver_q.qsize()))
                if not self.receiver_q.empty():
                    print('Receiving msg')
                    rec_msg = str(self.receiver_q.get())
                    # Message is in bit format: b'hello world'
                    # so we need to strip the first two and last char
                    rec_msg = rec_msg[2:-1]
                    self.set_msg_to_be_received(rec_msg)
                    print(rec_msg)
        root.after(250, lambda: self.consume(root))

    def bootstrap_connection(self):
        """
        Initializes the receiver and sender threads
        """
        self.receiver = Receiver(self.conn_socket, self.receiver_q)
        self.receiver.start()
        self.sender = Sender(self.conn_socket, self.sender_q)
        self.sender.start()
        self.config.state = State.UNSECURED_CONN


    def client_connect(self):
        """
        Starts up the client
        """
        print('Client connect...')
        # TODO: Move into its own thread?
        #          this will block the UI thread
        try:
            port = self.get_port()
            ip = self.get_ip()
            self.shared_key = self.get_shared_key()
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.connect((ip, int(port)))
            self.conn_socket = s
            self.bootstrap_connection()
        except ValueError:
            messagebox.showerror("Error", "Invlaid address/port number!")
    
    def server_accept_callback(self, socket):
        self.conn_socket = socket
        self.bootstrap_connection()

    def server_start(self):
        """
        Starts up the server
        """
        print('Starting server...')

        try:
            port = self.get_port()
            self.shared_key = self.get_shared_key()
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('', int(port)))
            self.server_listener = ServerListener(s, self.server_accept_callback)
            self.server_listener.start()
        except ValueError:
            messagebox.showerror("Error", "Invalid port number!")


    def toggle_mode(self):
        """
        Toggles between the client and the server
        """
        if (self.config.mode == Mode.CLIENT):
            self.config.mode = Mode.SERVER
            # Disable the IP config
            self.txt_ip.config(background=root['bg'])
            self.txt_ip.config(state='disabled')
            #server connect button
            self.btn_server_start.pack()
            self.btn_client_connect.pack_forget()
        else:
            self.config.mode = Mode.CLIENT
            # Enable the IP config
            self.txt_ip.config(background='white')
            self.txt_ip.config(state='normal')
            self.btn_client_connect.pack()
            self.btn_server_start.pack_forget()

        self.str_mode.set(self.config.mode)

    def send_message(self):
        sent_msg = self.get_msg_to_be_sent()
        if (sent_msg):
            self.sender_q.put(sent_msg)


    def toggle_debug(self):
        if(self.debug == False):
            self.debug_continue_button.config(state='normal')
            self.debug_button_txt.set("Debug Mode ON")
            self.txt_log.config(state='normal')
            self.debug = True
        else:
            self.debug_continue_button.config(state='disabled')
            self.debug_button_txt.set("Debug Mode OFF")
            self.txt_log.config(state='disabled')
            self.debug = False

    def step(self):
        print("next step")
        logging.info('Step')

    #######################
    # UI HELPER FUNCTIONS #
    ######################

    def get_port(self):
        return self.txt_port.get('1.0', 'end-1c')

    def get_ip(self):
        return self.txt_ip.get('1.0', 'end-1c')

    def get_msg_to_be_sent(self):
        return self.txt_sent.get('1.0', 'end-1c')

    def get_shared_key(self):
        return self.txt_secret_key.get('1.0', 'end-1c')

    def set_msg_to_be_received(self, msg):
        self.txt_received.config(state='normal')
        self.txt_received.insert('end-1c', msg)
        self.txt_received.config(state='disabled')

if __name__ == '__main__':
    root = tk.Tk()
    app = Application(master=root)
    app.consume(root)
    app.mainloop()
