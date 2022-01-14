import re, os

import tkinter as tk
from tkinter import Listbox, StringVar, IntVar, filedialog
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Frame, Button, Checkbutton, PanedWindow, Entry, Scrollbar, Label, LabelFrame

import ewinst, log, cfg

_EWSN = tk.E + tk.W + tk.S + tk.N

class Dialog:
    def __init__(self):
        self.selected_version = None
        self.current_lbox_item = 0
        self.ok_pressed = False
        self.selected_save = False
        self.ws = ''
        self.ewi = None

    def show(self, ws, ew_initial, selsrc):
        lbox = None

        def lbox_select(_e):
            if len(lbox.curselection()) > 0:
                self.current_lbox_item = lbox.curselection()[0]
                select_inst(lbox.get(lbox.curselection()[0]))
            else:
                lbox.selection_set(self.current_lbox_item)
                lbox.see(self.current_lbox_item)
                lbox.activate(self.current_lbox_item)

        def validate_ws_entry(inp):
            if inp == '':
                check_save.config(state=tk.DISABLED)
            else:
                check_save.config(state=tk.ACTIVE)
            return True

        def validate_entry(inp):
            pat = re.escape(inp)
            pat = pat.replace('\\*', '.*')

            lbox.delete(0, tk.END)
            for opt in optlist:
                if inp=='' or re.search(pat, opt, re.I):
                    lbox.insert(tk.END, opt)
            ents = lbox.get(0,tk.END)
            if len(ents) == 1:
                lbox.select_set(0)
                select_inst(lbox.get(0))
            else:
                deselect_inst()
            return True

        def callback_ok(*_args):
            self.ok_pressed = True
            app.destroy()

        def select_inst(key):
            ew = ewinst.get(key)
            if ew:
                ew.check()
                ok_button.configure(state=tk.ACTIVE)
                self.selected_version = key
                app.iconbitmap(ew.ide_exe)
                if cfg.info_pane:
                    info.configure(state=tk.NORMAL)
                    info.replace('1.0', tk.END, ew.get_info())
                    info.configure(state=tk.NORMAL)

        def deselect_inst():
            ok_button.configure(state=tk.DISABLED)
            self.selected_version = None
            if cfg.info_pane:
                info.configure(state=tk.NORMAL)
                info.replace('1.0', tk.END, '(select version)')
                info.configure(state=tk.DISABLED)

        def key_pressed(event):
            if event.char == '\r':
                if self.selected_version:
                    log.debug('<enter> pressed')
                    callback_ok(None)

        def callback_select(*_args):
            p = ws_var.get()
            if p: p = os.path.dirname(p)
            f = filedialog.askopenfilename(
                initialdir = p, title='Open file', filetypes=[('Workspace files', '*.eww')])
            if f: ws_var.set(f)

        app = tk.Tk()

        x = app.winfo_pointerx() - 100
        if x < 0: x = 0
        y = app.winfo_pointery() - 100
        if y < 0: y = 0
        app.geometry('+' +  str(x) + '+' + str(y))
        app.title('Select IAR Embedded Workbench version')
        app.minsize(cfg.min_window_width, 0)

        #style = Style()
        #style.theme_use('vista')

        root = Frame()
        root.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        frame = Frame(root, relief=tk.RAISED, borderwidth=1)
        frame.grid(row=0, column=0, sticky=_EWSN)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        subf = Frame(root)
        subf.grid(row=1, column=0, padx=2, pady=2)
        ok_button = Button(subf, text='Start Embedded Workbench', command=callback_ok)
        ok_button.pack()

        if cfg.info_pane:
            subf = PanedWindow(frame, orient=tk.HORIZONTAL)
            subf.grid(row=0, column=0, sticky=_EWSN)
            f2 = Frame(subf, relief=tk.RAISED, borderwidth=2)
            f3 = Frame(subf, borderwidth=1)
            subf.add(f2)
            subf.add(f3)
            info = ScrolledText(f3, foreground='SystemDisabledText', wrap=tk.NONE,width=1,height=10)
            info.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
            info.insert(tk.INSERT, '(select version)')
            info.configure(state=tk.DISABLED)
        else:
            f2 = Frame(frame, relief=tk.RAISED, borderwidth=2)
            f2.grid(row=0, column=0, sticky=_EWSN)

        entry = Entry(f2)
        entry.pack(side=tk.TOP, fill=tk.X, padx=2, pady=2)
        entry.focus_set()

        f21 = Frame(f2, height=100)
        f21.pack(fill=tk.BOTH, expand=True)
        optlist = list(ewinst.installations.keys())
        optlist.sort()
        lbox = Listbox(f21, selectmode=tk.SINGLE, height=cfg.list_box_lines)
        for opt in optlist: lbox.insert(tk.END, opt)

        sb = Scrollbar(f21)
        sb.pack(side = tk.RIGHT, fill = tk.BOTH)
        reg = app.register(validate_entry)
        entry.config(validate ='key', validatecommand =(reg, '%P'))
        lbox.pack(side = tk.TOP, fill=tk.BOTH, expand=True)
        lbox.config(yscrollcommand = sb.set)
        sb.config(command = lbox.yview)
        lbox.bind('<<ListboxSelect>>', lbox_select)
        if ew_initial:
            idx = optlist.index(ew_initial.key)
            lbox.selection_set(idx)
            lbox.see(idx)
            lbox_select(None)

        subf = Frame(frame)
        subf.grid(row=1, column=0, padx=2, pady=(7,2), sticky=tk.E+tk.W)
        infolbl = Label(subf, text='Initial selection: ' + selsrc)
        if 'WARN' in selsrc or 'ERR' in selsrc:
            infolbl.configure(foreground='red')
        infolbl.pack(side=tk.LEFT)

        fr = LabelFrame(frame, text='Workspace')
        fr.grid(row=2, column=0, padx=2, pady=2, sticky=tk.E+tk.W)
        subf = Frame(fr)
        subf.pack(fill=tk.X, padx=2, pady=2)
        clbl = Label(subf, text='Path:')
        clbl.pack(side=tk.LEFT, padx=2, pady=2)
        ws_var = StringVar(value=ws)
        ws_entry = Entry(subf, textvariable = ws_var)
        ws_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, pady=2)
        reg = app.register(validate_ws_entry)
        ws_entry.config(validate ='key', validatecommand =(reg, '%P'))

        file_select = Button(subf, text='Browse', command=callback_select)
        file_select.pack(side=tk.RIGHT, padx=2, pady=2)

        subf = Frame(fr)
        subf.pack(fill=tk.X, padx=2)
        check_save_var = IntVar(value=cfg.default_save)
        check_save = Checkbutton(subf,
                        variable=check_save_var, text='Save selected version in argvars')

        if not ws: check_save.config(state=tk.DISABLED)
        check_save.pack(side=tk.LEFT)

        app.bind('<Key>', key_pressed)
        app.update()
        app.minsize(root.winfo_width(), root.winfo_height())
        app.mainloop()

        if not self.ok_pressed: return False
        self.selected_save = check_save_var.get() == 1
        self.ws = ws_var.get()
        self.ewi = ewinst.get(self.selected_version)
        log.debug('Dialog ws: ' + str(self.ws))
        log.debug('Dialog version: ' + str(self.ewi))
        log.debug('Dialog save: ' + str(self.selected_save))
        return True
