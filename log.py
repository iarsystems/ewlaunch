import tkinter as tk
import tkinter.ttk as ttk
import tkinter.scrolledtext as scrolledtext
import sys, io, traceback
from contextlib import redirect_stderr, redirect_stdout

run_from_console = False
messages = io.StringIO()
died = False
dialog_title = ""

def dialog():
    app = tk.Tk()
    app.title(dialog_title)
    style = ttk.Style()
    style.theme_use("default")
    root = tk.Frame(padx=2, pady=2)
    frame = tk.Frame(root, relief=tk.RAISED, borderwidth=1)
    frame.pack(fill=tk.BOTH, expand=True)
    root.pack(fill=tk.BOTH, expand=True)

    def callback_ok(*args):
        app.destroy()

    ok_button = tk.Button(root, text="Exit", command=callback_ok)
    ok_button.pack(side=tk.TOP, pady=2)

    scr = scrolledtext.ScrolledText(frame, width=100)
    scr.insert(tk.INSERT, messages.getvalue())
    scr.configure(state='disabled')
    scr.pack(fill=tk.BOTH, expand=True)

    app.mainloop()

def die(message):
    global died
    if died: return
    died = True
    print("\ndied: " + message)
    if not run_from_console:
        dialog()
    sys.exit(1)

def run(func):
    with redirect_stdout(messages):
        with redirect_stderr(messages):
            try:
                return func()
            except Exception:
                die("Exception caught:\n" + traceback.format_exc())
            except SystemExit:
                die("SystemExit")
