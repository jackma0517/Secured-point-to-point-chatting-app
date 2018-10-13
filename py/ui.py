#!/usr/bin/python3 

# Throwing M - V - C conventions away for this quick hack.
# Apologies if it offends your sensibilities

import tkinter as tk

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
        self.create_widgets()

    def create_widgets(self):
        # Mode Toggle Button
        self.bt_toggle = tk.Button(self, text='Toggle Mode', command=self.toggle_mode)
        self.bt_toggle.pack(side='left')

        # Mode Text UI
        self.txt_mode = tk.Text(self)
        self.txt_mode.pack(side='left')

        self.quit = tk.Button(self, text='QUIT', fg='red', command=root.destroy)
        self.quit.pack(side='bottom')
        self.refresh_ui()
    
    def refresh_ui(self):
        self.txt_mode.delete('1.0', tk.END)
        self.txt_mode.insert('1.0', self.state.mode)

    def say_hi(self):
        print('Hi folks\n')
    
    def toggle_mode(self):
        if (self.state.mode == Mode.CLIENT):
            self.state.mode = Mode.SERVER
        else:
            self.state.mode = Mode.CLIENT
        self.refresh_ui()

if __name__ == '__main__':
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()