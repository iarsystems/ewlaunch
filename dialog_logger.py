import sys, io, traceback
import tkinter as tk
from tkinter import ttk, scrolledtext
from contextlib import redirect_stderr, redirect_stdout

class Log:
    def __init__(self, title):
        self.messages = io.StringIO()
        self.died = False
        self.dialog_title = title

    def dialog(self):
        app = tk.Tk()
        app.title(self.dialog_title)
        style = ttk.Style()
        style.theme_use('default')
        root = tk.Frame(padx=2, pady=2)
        frame = tk.Frame(root, relief=tk.RAISED, borderwidth=1)
        frame.pack(fill=tk.BOTH, expand=True)
        root.pack(fill=tk.BOTH, expand=True)

        def callback_ok(*_args):
            app.destroy()

        ok_button = tk.Button(root, text='Exit', command=callback_ok)
        ok_button.pack(side=tk.TOP, pady=2)

        scr = scrolledtext.ScrolledText(frame, width=100)
        scr.insert(tk.INSERT, self.messages.getvalue())
        scr.configure(state='disabled')
        scr.pack(fill=tk.BOTH, expand=True)

        app.mainloop()

    def debug(self, message):
        print(message)

    def die(self, message):
        if self.died: return
        self.died = True
        print()
        print('died: ' + message)
        self.dialog()
        sys.exit(1)

    def run(self, func):
        with redirect_stdout(self.messages):
            with redirect_stderr(self.messages):
                try:
                    func()
                except Exception:#pylint: disable=broad-except
                    self.die('Exception caught:\n' + traceback.format_exc())
                except SystemExit:
                    self.die('SystemExit')
