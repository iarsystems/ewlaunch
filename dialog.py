import ewinst
from config import cfg

import re, os
from tkinter import *
from tkinter.ttk import *
import tkinter.scrolledtext as scrolledtext
import tkinter.filedialog as filedialog

class Dialog:

    def show(self, ws, ew_initial, selsrc):
        self.selected_version = None
        self.current_lbox_item = 0
        self.ok_pressed = False
        lbox = None

        def lbox_select(e):
            if len(lbox.curselection()) > 0:
                self.current_lbox_item = lbox.curselection()[0]
                select_inst(lbox.get(lbox.curselection()[0]))
            else:
                lbox.selection_set(self.current_lbox_item)
                lbox.see(self.current_lbox_item)
                lbox.activate(self.current_lbox_item)

        def validate_ws_entry(input):
            if input == "":
                check_save.config(state=DISABLED)
            else:
                check_save.config(state=ACTIVE)
            return True

        def validate_entry(input):
            pat = re.escape(input)
            pat = pat.replace("\\*", ".*")

            lbox.delete(0, END)
            for opt in optlist:
                if input=="" or re.search(pat, opt, re.I):
                    lbox.insert(END, opt)
            ents = lbox.get(0,END)
            if len(ents) == 1:
                lbox.select_set(0)
                select_inst(lbox.get(0))
            else:
                deselect_inst()
            return True

        def callback_ok(*args):
            self.ok_pressed = True
            app.destroy()

        def select_inst(key):
            ew = ewinst.get(key)
            if ew:
                ok_button.configure(state=ACTIVE)
                self.selected_version = key
                app.iconbitmap(ew.executable())
                if cfg.info_pane:
                    info.configure(state=NORMAL)
                    info.replace("1.0", END, ew.get_info())
                    info.configure(state=NORMAL)

        def deselect_inst():
            ok_button.configure(state=DISABLED)
            self.selected_version = None
            if cfg.info_pane:
                info.configure(state=NORMAL)
                info.replace("1.0", END, "(select version)")
                info.configure(state=DISABLED)

        def key_pressed(event):
            if event.char == '\r':
                if self.selected_version:
                    print("<enter> pressed")
                    callback_ok(None)

        def callback_select(*args):
            p = ws_var.get()
            if p: p = os.path.dirname(p)
            f = filedialog.askopenfilename(initialdir = p, title="Open file", filetypes=[("Workspace files", "*.eww")])
            if f: ws_var.set(f)

        app = Tk()

        x = app.winfo_pointerx() - 100
        if x < 0: x = 0
        y = app.winfo_pointery() - 100
        if y < 0: y = 0
        app.geometry("+" +  str(x) + "+" + str(y))
        app.title("Select IAR Embedded Workbench version")
        app.minsize(cfg.min_window_width, 0)

        #style = Style()
        #style.theme_use('vista')

        root = Frame()
        root.pack(fill=BOTH, expand=True, padx=2, pady=2)
        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        frame = Frame(root, relief=RAISED, borderwidth=1)
        frame.grid(row=0, column=0, sticky=E+W+S+N)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        subf = Frame(root)
        subf.grid(row=1, column=0, padx=2, pady=2)
        ok_button = Button(subf, text="Start Embedded Workbench", command=callback_ok)
        ok_button.pack()

        if cfg.info_pane:
            subf = PanedWindow(frame, orient=HORIZONTAL)
            subf.grid(row=0, column=0, sticky=E+W+S+N)
            f2 = Frame(subf, relief=RAISED, borderwidth=2)
            f3 = Frame(subf, borderwidth=1)
            subf.add(f2)
            subf.add(f3)
            info = scrolledtext.ScrolledText(f3, foreground="SystemDisabledText", wrap=NONE, width=1, height=10)
            info.pack(side=TOP, fill=BOTH, expand=1)
            info.insert(INSERT, "(select version)")
            info.configure(state=DISABLED)
        else:
            f2 = Frame(frame, relief=RAISED, borderwidth=2)
            f2.grid(row=0, column=0, sticky=E+W+S+N)

        entry = Entry(f2)
        entry.pack(side=TOP, fill=X, padx=2, pady=2)
        entry.focus_set()

        f21 = Frame(f2, height=100)
        f21.pack(fill=BOTH, expand=True)
        optlist = list(ewinst.installations.keys())
        optlist.sort()
        lbox = Listbox(f21, selectmode=SINGLE, height=cfg.list_box_lines)
        for opt in optlist: lbox.insert(END, opt)

        sb = Scrollbar(f21)
        sb.pack(side = RIGHT, fill = BOTH)
        reg = app.register(validate_entry)
        entry.config(validate ="key", validatecommand =(reg, '%P'))
        lbox.pack(side = TOP, fill=BOTH, expand=True)
        lbox.config(yscrollcommand = sb.set)
        sb.config(command = lbox.yview)
        lbox.bind('<<ListboxSelect>>', lbox_select)
        if ew_initial:
            idx = optlist.index(ew_initial.key())
            lbox.selection_set(idx)
            lbox.see(idx)
            lbox_select(None)

        subf = Frame(frame)
        subf.grid(row=1, column=0, padx=2, pady=(7,2), sticky=E+W)
        infolbl = Label(subf, text="Initial selection: " + selsrc)
        if "WARN" in selsrc or "ERR" in selsrc:
            infolbl.configure(foreground="red")
        infolbl.pack(side=LEFT)

        fr = LabelFrame(frame, text="Workspace")
        fr.grid(row=2, column=0, padx=2, pady=2, sticky=E+W)
        subf = Frame(fr)
        subf.pack(fill=X, padx=2, pady=2)
        clbl = Label(subf, text="Path:")
        clbl.pack(side=LEFT, padx=2, pady=2)
        ws_var = StringVar(value=ws)
        ws_entry = Entry(subf, textvariable = ws_var)
        ws_entry.pack(side=LEFT, fill=X, expand=True, padx=2, pady=2)
        reg = app.register(validate_ws_entry)
        ws_entry.config(validate ="key", validatecommand =(reg, '%P'))

        file_select = Button(subf, text="Browse", command=callback_select)
        file_select.pack(side=RIGHT, padx=2, pady=2)

        subf = Frame(fr)
        subf.pack(fill=X, padx=2)
        check_save_var = IntVar(value=cfg.default_save)
        check_save = Checkbutton(subf, variable=check_save_var, text="Save selected version in argvars")

        if not len(ws): check_save.config(state=DISABLED)
        check_save.pack(side=LEFT)

        app.bind("<Key>", key_pressed)
        app.update()
        app.minsize(root.winfo_width(), root.winfo_height())
        app.mainloop()

        if not self.ok_pressed: return False
        self.selected_save = check_save_var.get() == 1
        self.ws = ws_var.get()
        if self.ws:
            if not self.ws.endswith(".eww"):
                self.ws += ".eww"
            if not os.path.isabs(ws):
                raise ValueError("path not absolute: " + self.ws)
        self.ewi = ewinst.get(self.selected_version)
        print("Dialog ws: " + str(self.ws))
        print("Dialog version: " + str(self.ewi))
        print("Dialog save: " + str(self.selected_save))
        return True
