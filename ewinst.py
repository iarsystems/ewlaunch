import log
from config import cfg

import winreg, os, collections, configparser, re


REG_PATH = r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"

installations = collections.OrderedDict()

_IARIDEPM = r"\common\bin\IarIdePm.exe"

class EwInst:
    def __init__(self, dndv, exec, src):
        self.dndv = dndv
        self.info = collections.OrderedDict()
        self.info['command'] = exec
        self.info['source'] = src
        self.info['exists'] = str(os.path.isfile(self.executable()))

    def key(self):
        return self.dndv

    def __str__(self):
        return self.key()

    def executable(self):
        return self.info['command']

    def exists(self):
        return self.info['exists']

    def get_info(self):
        msg = "[" + self.key() + "]\n"
        for key in self.info.keys():
            msg += "  " + key + ": " + str(self.info[key]) + "\n"
        return msg

def _shortname(ver):
    for r in cfg.shortname:
        ver = re.sub(r, cfg.shortname[r], ver, flags=re.I)
    return ver

def get(version) -> EwInst:
    version = _shortname(version)
    if len(version) == 0:
        return None
    for key in installations.keys():
        ew = installations[key]
        if (version in ew.key()):
            return ew
    return None

def _make_unique(key):
    key = _shortname(key)
    if key not in installations:
        return key
    for i in range(1, 1000):
        trykey = key + " (" + str(i) + ")"
        if trykey not in installations:
            return trykey
    log.die("could not get key")

def _handle_ewkey(subkey, subenumkey, ewkey):
    ewkey = _make_unique(ewkey)
    il = winreg.QueryValueEx(subkey, "InstallLocation")[0].strip() + _IARIDEPM
    p = 'HKEY_LOCAL_MACHINE\\' + REG_PATH + '\\' + str(subenumkey)
    ew = EwInst(ewkey, il, p)
    installations[ewkey] = ew
    for sn in range(1000):
        try:
            v = winreg.EnumValue(subkey, sn)
            ew.info[v[0]] = v[1]
        except:
            pass

def _handle_enumkey(key, subenumkey):
    try:
        with winreg.OpenKey(key, subenumkey) as subkey:
            publisher = winreg.QueryValueEx(subkey, "Publisher")
            if (publisher[0] == "IAR Systems"):
                ewkey = winreg.QueryValueEx(subkey, "DisplayName")[0].strip() + " " + \
                        winreg.QueryValueEx(subkey, "DisplayVersion")[0].strip()
                if ("Workbench" in ewkey and not ("Library" in ewkey)):
                    _handle_ewkey(subkey, subenumkey, ewkey)
    except:
        pass

def add_from_reg():
    access_registry = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    with winreg.OpenKey(access_registry, REG_PATH) as key:
        for n in range(1000):
            try:
                _handle_enumkey(key, winreg.EnumKey(key, n))
            except:
                break

INI = 'installations.ini'
def add_from_file():
    if not os.path.isfile(INI):
        return

    cfg = configparser.ConfigParser()
    cfg.optionxform = str
    cfg.read(INI)

    for sectname in cfg.sections():
        sect = cfg[sectname]
        ewkey = _make_unique(sectname)
        ew = EwInst(ewkey, sect['command'], INI)
        installations[ewkey] = ew
        for attr in sect:
            if attr not in ew.info:
                ew.info[attr] = sect[attr]

def dump(file):
    frist = True
    with open(file, "w") as f:
        for key in installations.keys():
            if not frist: f.write("\n")
            else: frist=False
            ew = installations[key]
            f.write(ew.get_info())
