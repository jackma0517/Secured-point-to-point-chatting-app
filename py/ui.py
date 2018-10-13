#!/usr/bin/python3 

# Throwing M - V - C conventions away for this quick hack.
# Apologies if it offends your sensibilities

import tkinter as tk
from tkinter.scrolledtext import ScrolledText

# The mode the program is operating in
class Mode:
    SERVER = 'SERVER'
    CLIENT = 'CLIENT'

class State:
    def __init__(self):
        self.mode = Mode.CLIENT

class Application(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.state = State()
        
        # String Variables
        self.str_mode = tk.StringVar()
        self.str_mode.set(self.state.mode)

        self.create_widgets()

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

        self.lbl_ip = tk.Label(master=self.fr_modes, text='IP: ')
        self.lbl_ip.pack(side='left')
        self.txt_ip = tk.Text(master=self.fr_modes)
        self.txt_ip.config(width=15, height=1)
        self.txt_ip.pack(side='left')

        self.lbl_port = tk.Label(master=self.fr_modes, text='Port: ')
        self.lbl_port.pack(side='left')
        self.txt_port = tk.Text(master=self.fr_modes)
        self.txt_port.config(width=15, height=1)
        self.txt_port.pack(side='left')

        # Shared secret key
        self.txt_secret_key = ScrolledText(self)
        self.txt_secret_key.config(width=100, height=4)
        self.txt_secret_key.pack(side='top')


        # End Me
        self.quit = tk.Button(self, text='QUIT', fg='red', command=root.destroy)
        self.quit.place(rely=1.0, relx=1.0, x=0, y=0, anchor=tk.SE)
        self.quit.pack()
        self.refresh_ui()
    

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
        else:
            self.state.mode = Mode.CLIENT
            # Enable the IP config
            self.txt_ip.config(background='white')
            self.txt_ip.config(state='normal')
        self.str_mode.set(self.state.mode)

if __name__ == '__main__':
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()