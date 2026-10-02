import ctypes
import re
import sys
import tkinter as tk
from ctypes import wintypes
from pathlib import Path
from tkinter import IntVar, Listbox, StringVar, filedialog
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import (
    Button,
    Checkbutton,
    Entry,
    Frame,
    Label,
    LabelFrame,
    PanedWindow,
    Scrollbar,
    Style,
)

import cfg
import ewinst
import log

_EWSN = tk.E + tk.W + tk.S + tk.N


def _work_area(x, y):
    """Work area (screen minus taskbar) of the monitor containing (x, y) as (left, top, right, bottom)."""

    class MonitorInfo(ctypes.Structure):
        _fields_ = [
            ("cbSize", wintypes.DWORD),
            ("rcMonitor", wintypes.RECT),
            ("rcWork", wintypes.RECT),
            ("dwFlags", wintypes.DWORD),
        ]

    user32 = ctypes.windll.user32
    user32.MonitorFromPoint.argtypes = [wintypes.POINT, wintypes.DWORD]
    user32.MonitorFromPoint.restype = wintypes.HANDLE
    user32.GetMonitorInfoW.argtypes = [wintypes.HANDLE, ctypes.POINTER(MonitorInfo)]
    mon = user32.MonitorFromPoint(wintypes.POINT(x, y), 2)  # MONITOR_DEFAULTTONEAREST
    info = MonitorInfo()
    info.cbSize = ctypes.sizeof(MonitorInfo)
    if not mon or not user32.GetMonitorInfoW(mon, ctypes.byref(info)):
        return None
    r = info.rcWork
    return r.left, r.top, r.right, r.bottom


def _place_window(app, px, py):
    """Position the window near the pointer; if it would not fit in the work area, center it on that monitor."""
    app.update_idletasks()
    w = max(app.winfo_width(), app.winfo_reqwidth())
    h = max(app.winfo_height(), app.winfo_reqheight())
    try:
        area = _work_area(px, py)
    except (AttributeError, OSError):
        area = None
    if area is None:
        area = (0, 0, app.winfo_screenwidth(), app.winfo_screenheight())
    left, top, right, bottom = area
    x, y = px - 100, py - 100
    if x < left or y < top or x + w > right or y + h > bottom:
        x = left + (right - left - w) // 2
        y = top + (bottom - top - h) // 2
    app.geometry(f"+{max(x, left)}+{max(y, top)}")


def _own_icon_path():
    """The icon embedded in the frozen exe, or ewlaunch.ico when running from source."""
    return Path(sys.executable) if getattr(sys, "frozen", False) else Path(__file__).with_name("ewlaunch.ico")


def _extract_icons(path):
    """Return (large, small) HICONs of the first icon in path; either may be None."""
    shell32 = ctypes.windll.shell32
    shell32.ExtractIconExW.argtypes = [
        wintypes.LPCWSTR,
        ctypes.c_int,
        ctypes.POINTER(wintypes.HANDLE),
        ctypes.POINTER(wintypes.HANDLE),
        wintypes.UINT,
    ]
    large, small = wintypes.HANDLE(), wintypes.HANDLE()
    if shell32.ExtractIconExW(str(path), 0, ctypes.byref(large), ctypes.byref(small), 1) < 1:
        return None, None
    return large.value, small.value


def _set_window_icons(app, large_src=None, small_src=None):
    """Set the taskbar (large) icon from large_src and the titlebar (small) icon from small_src.

    Both default to the ewlaunch icon. Only the large icon is used for the taskbar button and pinning, so the
    titlebar can follow the selected EW version while the taskbar stays ewlaunch.
    """
    user32 = ctypes.windll.user32
    user32.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPVOID]
    user32.GetParent.argtypes = [wintypes.HWND]
    user32.GetParent.restype = wintypes.HWND
    hwnd = user32.GetParent(app.winfo_id()) or app.winfo_id()
    wm_seticon, icon_small, icon_big = 0x0080, 0, 1
    own = _own_icon_path()
    big = _extract_icons(large_src or own)[0]
    small = _extract_icons(small_src or own)[1]
    if big:
        user32.SendMessageW(hwnd, wm_seticon, icon_big, big)
    if small:
        user32.SendMessageW(hwnd, wm_seticon, icon_small, small)


def _set_default_icon(app):
    try:
        app.iconbitmap(default=str(_own_icon_path()))
        _set_window_icons(app)
    except (tk.TclError, AttributeError, OSError) as e:
        log.debug("Could not set window icon: " + str(e))


class Dialog:
    def __init__(self):
        self.selected_version = None
        self.current_lbox_item = 0
        self.ok_pressed = False
        self.selected_save = False
        self.ws = ""
        self.ewi = None

    def show(self, ws, ew_initial, selsrc):
        def lbox_select(_e):
            if len(lbox.curselection()) > 0:
                self.current_lbox_item = lbox.curselection()[0]
                select_inst(lbox.get(lbox.curselection()[0]))
            else:
                lbox.selection_set(self.current_lbox_item)
                lbox.see(self.current_lbox_item)
                lbox.activate(self.current_lbox_item)

        def validate_ws_entry(inp):
            if inp == "":
                check_save.config(state=tk.DISABLED)
            else:
                check_save.config(state=tk.ACTIVE)
            return True

        def validate_entry(inp):
            pat = re.escape(inp)
            pat = pat.replace("\\*", ".*")

            lbox.delete(0, tk.END)
            for opt in optlist:
                if inp == "" or re.search(pat, opt, re.IGNORECASE):
                    lbox.insert(tk.END, opt)
            ents = lbox.get(0, tk.END)
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
                try:
                    _set_window_icons(app, small_src=ew.ide_exe)
                except (AttributeError, OSError) as e:
                    log.debug("Could not set titlebar icon: " + str(e))
                if cfg.info_pane:
                    info.configure(state=tk.NORMAL)
                    info.replace("1.0", tk.END, ew.get_info())
                    info.configure(state=tk.DISABLED)

        def deselect_inst():
            ok_button.configure(state=tk.DISABLED)
            self.selected_version = None
            if cfg.info_pane:
                info.configure(state=tk.NORMAL)
                info.replace("1.0", tk.END, "(select version)")
                info.configure(state=tk.DISABLED)

        def key_pressed(event):
            if event.char == "\r" and self.selected_version:
                log.debug("<enter> pressed")
                callback_ok(None)

        def callback_select(*_args):
            p = ws_var.get()
            if p:
                p = str(Path(p).parent)
            f = filedialog.askopenfilename(initialdir=p, title="Open file", filetypes=[("Workspace files", "*.eww")])
            if f:
                ws_var.set(f)

        app = tk.Tk()

        pointer = (app.winfo_pointerx(), app.winfo_pointery())
        app.attributes("-alpha", 0)  # hidden until positioned
        _set_default_icon(app)
        app.title("Select IAR Embedded Workbench version")
        app.minsize(cfg.min_window_width, 0)

        if cfg.ttk_style:
            style = Style()
            style.theme_use(cfg.ttk_style)

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
        ok_button = Button(subf, text="Start Embedded Workbench", command=callback_ok)
        ok_button.pack()

        if cfg.info_pane:
            subf = PanedWindow(frame, orient=tk.HORIZONTAL)
            subf.grid(row=0, column=0, sticky=_EWSN)
            f2 = Frame(subf, relief=tk.RAISED, borderwidth=2)
            f3 = Frame(subf, borderwidth=1)
            subf.add(f2)
            subf.add(f3)
            info = ScrolledText(f3, foreground="SystemDisabledText", wrap=tk.NONE, width=1, height=10)
            info.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
            info.insert(tk.INSERT, "(select version)")
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
        for opt in optlist:
            lbox.insert(tk.END, opt)

        sb = Scrollbar(f21)
        sb.pack(side=tk.RIGHT, fill=tk.BOTH)
        reg = app.register(validate_entry)
        entry.config(validate="key", validatecommand=(reg, "%P"))
        lbox.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        lbox.config(yscrollcommand=sb.set)
        sb.config(command=lbox.yview)
        lbox.bind("<<ListboxSelect>>", lbox_select)
        if ew_initial:
            idx = optlist.index(ew_initial.key)
            lbox.selection_set(idx)
            lbox.see(idx)
            lbox_select(None)

        subf = Frame(frame)
        subf.grid(row=1, column=0, padx=2, pady=(7, 2), sticky=tk.E + tk.W)
        infolbl = Label(subf, text="Initial selection: " + selsrc)
        if "WARN" in selsrc or "ERR" in selsrc:
            infolbl.configure(foreground="red")
        infolbl.pack(side=tk.LEFT)

        fr = LabelFrame(frame, text="Workspace")
        fr.grid(row=2, column=0, padx=2, pady=2, sticky=tk.E + tk.W)
        subf = Frame(fr)
        subf.pack(fill=tk.X, padx=2, pady=2)
        clbl = Label(subf, text="Path:")
        clbl.pack(side=tk.LEFT, padx=2, pady=2)
        ws_var = StringVar(value=ws)
        ws_entry = Entry(subf, textvariable=ws_var)
        ws_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, pady=2)
        reg = app.register(validate_ws_entry)
        ws_entry.config(validate="key", validatecommand=(reg, "%P"))

        file_select = Button(subf, text="Browse", command=callback_select)
        file_select.pack(side=tk.RIGHT, padx=2, pady=2)

        subf = Frame(fr)
        subf.pack(fill=tk.X, padx=2)
        check_save_var = IntVar(value=cfg.default_save)
        check_save = Checkbutton(subf, variable=check_save_var, text="Save selected version in argvars")

        if not ws:
            check_save.config(state=tk.DISABLED)
        check_save.pack(side=tk.LEFT)

        app.bind("<Key>", key_pressed)
        app.update()
        app.minsize(root.winfo_width(), root.winfo_height())
        _place_window(app, *pointer)
        app.attributes("-alpha", 1)
        # Icons set before the window is mapped are lost, so (re)apply them now, for the preselected version if any
        ew = ewinst.get(self.selected_version) if self.selected_version else None
        try:
            _set_window_icons(app, small_src=ew.ide_exe if ew else None)
        except (AttributeError, OSError) as e:
            log.debug("Could not set window icons: " + str(e))
        app.mainloop()

        if not self.ok_pressed:
            return False
        self.selected_save = check_save_var.get() == 1
        self.ws = ws_var.get()
        self.ewi = ewinst.get(self.selected_version)
        log.debug("Dialog ws: " + str(self.ws))
        log.debug("Dialog version: " + str(self.ewi))
        log.debug("Dialog save: " + str(self.selected_save))
        return True
