#!/usr/bin/python3

# Throwing M - V - C conventions away for this quick hack.
# Apologies if it offends your sensibilities
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter import *

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

# Maintains state in the program
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

        self.debug = False

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

        # Debug Toggle Button
        self.debug_button_txt = tk.StringVar()
        self.debug_button_txt.set("Debug Mode OFF")
        self.btn_debug_toggle = tk.Button(master=self.fr_modes, textvariable=self.debug_button_txt, command=self.toggle_debug)
        self.btn_debug_toggle.pack(side='left')

        # Debug Continue Button
        self.debug_continue_button = tk.Button(master=self.fr_modes, text='Continue', command=self.step)
        self.debug_continue_button.pack(side='right')
        self.debug_continue_button.visible = False
        self.debug_continue_button.config(state=DISABLED)

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


        # Data to be Recieved
        self.lbl_received = tk.Label(master=self.fr_msg_boxes, 
                                        text='Data to be Received:')
        self.lbl_received.pack()
        self.txt_received = ScrolledText(master=self.fr_msg_boxes)
        self.txt_received.config(width=100, height=4)
<<<<<<< HEAD
        self.txt_received.pack() 


        # Step by Step Frame
        self.fr_step = tk.Frame(self)
        self.fr_step.pack()

        # Step by step data
        self.lbl_log = tk.Label(master=self.fr_step,
                                    text='Encryption logging')
        self.lbl_log.pack()
        self.txt_log = ScrolledText(master=self.fr_step)
        # TODO: Need to toggle state to normal and disabled when writing to...
        self.txt_log.config(width=100, height=6, bg=root['bg'], state='disabled')
        self.txt_log.pack()

        # Step by step button
        self.btn_step = tk.Button(master=self.fr_step,
                                        text='STEP')        
        self.btn_step.pack()
        self.chk_step_enable = tk.Checkbutton(master=self.fr_step,
                                                text='Enable Step by Step')
        self.chk_step_enable.pack()

        # Gimpy hack to push the quit button downwards
        self.fr_space = tk.Frame(self)
        self.fr_space.config(height = 100)
        self.fr_space.pack()
=======
        self.txt_received.pack()
>>>>>>> 031d4a02bd05274bbcd0838445abfdbff4f2421b

        # End Me
        self.quit = tk.Button(self, text='QUIT', fg='red', command=root.destroy)
        self.quit.place(rely=1.0, relx=1.0, x=0, y=0, anchor=tk.SE)
        self.quit.pack()


    def consume(self, root):
        """
        This is where we start reading/writing to/from the
        Receiver and Sender
        """
        if self.is_initialized():
            print('Consuming...')
            if not self.receiver_q.empty():
                print('Receiving msg')
                rec_msg = str(self.receiver_q.get())
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


    def client_connect(self):
        """
        Starts up the client
        """
        print('Client connect...')
        # TODO: Move into its own thread?
        #          this will block the UI thread
        port = self.get_port()
        ip = self.get_ip()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.connect((ip, int(port)))
        self.conn_socket = s
        self.bootstrap_connection()
        print('Client connected to server')


    def server_start(self):
        """
        Starts up the server
        """
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
            self.bootstrap_connection()
            print('Server connected to client')
            break

    def toggle_mode(self):
        """
        Toggles between the client and the server
        """
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
        # TODO: Wire this up the the Sender
        if (self.state.mode == Mode.CLIENT):
            sent_msg = self.get_msg_to_be_sent()
            if (sent_msg):
                self.sender_q.put(sent_msg)
        else:
            #Server Mode
            sent_msg = self.get_msg_to_be_sent()
            if (sent_msg):
                self.sender_q.put(sent_msg)


    def toggle_debug(self):
        if(self.debug == False):
            self.debug_continue_button.config(state=NORMAL)
            self.debug_button_txt.set("Debug Mode ON")
            self.debug = True
        else:
            self.debug_continue_button.config(state=DISABLED)
            self.debug_button_txt.set("Debug Mode OFF")
            self.debug = False

    def step(self):
        print("next step")

    #######################
    # UI HELPER FUNCTIONS #
    ######################

    def display_received_message(self, response):
        self.txt_received.insert("end-1c", response)

    def get_port(self):
        return self.txt_port.get('1.0', 'end-1c')

    def get_ip(self):
        return self.txt_ip.get('1.0', 'end-1c')

    def get_msg_to_be_sent(self):
        return self.txt_sent.get('1.0', 'end-1c')

    def set_msg_to_be_received(self, msg):
        self.txt_received.insert('end-1c', msg)

if __name__ == '__main__':
    root = tk.Tk()
    app = Application(master=root)
    app.consume(root)
    app.mainloop()
