import os
from pathlib import Path

import cfg

_KEYS = {
    "WS_PATH": "Full path of .eww file",
    "WS_BPATH": "Path of .eww file, excluding file extension",
    "WS_FNAME": "File name of .eww file",
    "WS_BNAME": "File name of .eww file, excluding file extension",
    "WS_DIR": "Directory of .eww file",
    "EW_VERSION": "The version of IAR Embedded Workbench",
    "EW_DIR": "Top directory of IAR Embedded Workbench",
    "TOOLKIT": 'Name of toolkit directory, e.g. "arm"',
    "TOOLKIT_DIR": "Full path of toolkit directory",
    "EWLAUNCH_DIR": "Full path of EWLaunch directory",
}


class Expand:
    def __init__(self):
        self.attrs = {}
        for key in _KEYS:
            self.attrs[key] = ""
        self.set("EWLAUNCH_DIR", cfg.ewlaunch_dir)

    def set(self, k, v):
        self.attrs[k] = v

    def get(self, k):
        return self.attrs[k]

    def set_ew(self, ew):
        self.set("EW_VERSION", ew.key)
        self.set("EW_DIR", ew.ew_dir)
        tk = ew.toolkit_dir or ""
        self.set("TOOLKIT", Path(tk).name)
        self.set("TOOLKIT_DIR", tk)

    def set_ws(self, ws):
        p = Path(ws)
        self.set("WS_PATH", ws)
        self.set("WS_FNAME", p.name)
        self.set("WS_BNAME", p.stem)
        # Path('').parent is '.', keep these empty without workspace
        self.set("WS_DIR", str(p.parent) if ws else "")
        self.set("WS_BPATH", str(p.with_suffix("")) if ws else "")

    def expand(self, s):
        for key, val in self.attrs.items():
            s = s.replace(r"$" + key + r"$", val)
        return s

    def setenv(self):
        for key, val in self.attrs.items():
            os.environ[key] = val
