import os

class Expand:
    def __init__(self):
        self.ew_ver = ""
        self.ws = ""
        self.ws_fname = ""
        self.ws_bname = ""
        self.ws_dir = ""
        self.ws_bpath = ""

    def set_ew(self, ew):
        self.ew_ver = ew.key()

    def set_ws(self, ws):
        self.ws = ws
        self.ws_fname = os.path.basename(ws)
        self.ws_bname = self.ws_fname.replace(".eww", "")
        self.ws_dir = os.path.dirname(ws)
        self.ws_bpath = self.ws_dir + "\\" + self.ws_bname

    def expand(self, str):
        str = str.replace(r'$WS_PATH$', self.ws)
        str = str.replace(r'$WS_BPATH$', self.ws_bpath)
        str = str.replace(r'$WS_BNAME$', self.ws_bname)
        str = str.replace(r'$WS_DIR$', self.ws_dir)
        str = str.replace(r'$EW_VERSION$', self.ew_ver)
        return str

exp = Expand()
