import winreg, os, collections, configparser, re

import log, cfg

REG_PATH = r'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall'

installations = collections.OrderedDict()

def listsubdirs(d):
    r = []
    try:
        for f in os.listdir(d):
            if os.path.isdir(os.path.join(d, f)):
                r.append(f)
    except IOError:
        print('ERROR: could not read subdirs in ' + d)
    return r

def find_tkdir(dr, subd=None):
    if not subd: subd = listsubdirs(dr)
    if 'common' in subd: subd.remove('common')
    if 'install-info' in subd: subd.remove('install-info')
    for d in subd:
        if os.path.isfile(os.path.join(dr, d, 'bin', 'icc' + d + '.exe')):
            return os.path.join(dr, d)
    return None

def find_idepm(ew_dir):
    for p in [ os.path.join(ew_dir, 'common', 'bin', 'IarIdePm.exe') ]:
        if os.path.isfile(p):
            return p
    return None

class EwInst:
    def __init__(self, ewkey, ew_dir, src, tk=None):
        self.key = _make_unique(ewkey)
        self.info = collections.OrderedDict()
        self.ew_dir = ew_dir
        self.source = src
        self.ide_exe = None
        self.toolkit_dir = tk
        installations[self.key] = self

    def set_attr(self, k, v):
        if k == 'EW_DIR': return
        self.info[k] = str(v).strip()
        if k == 'TOOLKIT_DIR': self.toolkit_dir = v.strip()
        elif k == 'IDE_EXE': self.ide_exe = v.strip()

    def __str__(self): return self.key

    def check(self):
        if not self.ide_exe: self.ide_exe = find_idepm(self.ew_dir)
        if not self.toolkit_dir: self.toolkit_dir = find_tkdir(self.ew_dir)

    def get_info(self):
        msg = '[' + self.key + ']\n'
        for k,v in [('EW_DIR', self.ew_dir)]:
            if v: msg += '  ' + k + ': ' + str(v) + '\n'
        for k,v in self.info.items():
            msg += '  ' + k + ': ' + str(v) + '\n'
        return msg

def _shortname(ver):
    for r in cfg.shortname:
        ver = re.sub(r, cfg.shortname[r], ver, flags=re.I)
    return ver

def get(version_) -> EwInst:
    version = _shortname(version_).casefold()
    if len(version) == 0:
        return None
    found = None
    for ew in installations.values():
        ewkey = ew.key.casefold()
        if version == ewkey: return ew
        if version in ewkey:
            if found:
                log.die('Multiple versions matching ' + version_ + ': ' + found.key + ', ' + ew.key)
            found = ew
    return found

def getlist(pat):
    ret = []
    for ew in installations.values():
        if re.search(pat, ew.key, re.I):
            ret.append(ew)
    ret.sort(key=lambda ew: ew.key)
    return ret

def _make_unique(key):
    key = _shortname(key)
    if key not in installations:
        return key
    for i in range(1, 1000):
        trykey = key + ' (' + str(i) + ')'
        if trykey not in installations:
            return trykey
    log.die('could not get key')

def _handle_ewkey(subkey, subenumkey, ewkey_):
    dr = winreg.QueryValueEx(subkey, 'InstallLocation')[0].strip()
    p = 'HKEY_LOCAL_MACHINE\\' + REG_PATH + '\\' + str(subenumkey)
    ew = EwInst(ewkey_, dr, p)
    for sn in range(1000):
        try:
            v = winreg.EnumValue(subkey, sn)
            ew.set_attr(v[0], v[1])
        except OSError:
            pass

def _handle_enumkey(key, subenumkey):
    try:
        with winreg.OpenKey(key, subenumkey) as subkey:
            publisher = winreg.QueryValueEx(subkey, 'Publisher')
            if publisher[0] == 'IAR Systems':
                ewkey = winreg.QueryValueEx(subkey, 'DisplayName')[0].strip()
                dv = winreg.QueryValueEx(subkey, 'DisplayVersion')[0].strip()
                if dv not in ewkey:
                    ewkey += ' ' + dv
                if 'Workbench' in ewkey and not 'Library' in ewkey:
                    _handle_ewkey(subkey, subenumkey, ewkey)
    except OSError:
        pass

def add_from_reg():
    access_registry = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    with winreg.OpenKey(access_registry, REG_PATH) as key:
        for n in range(1000):
            try:
                _handle_enumkey(key, winreg.EnumKey(key, n))
            except OSError:
                break

def add_from_file(filename):
    if not os.path.isfile(filename):
        log.die('could not open ' + filename)

    cp = configparser.ConfigParser()
    cp.optionxform = str
    cp.read(filename)

    for sectname in cp.sections():
        sect = cp[sectname]
        ew = EwInst(sectname, sect['EW_DIR'], filename)
        for attr in sect: ew.set_attr(attr, sect[attr])

def dump(file):
    frist = True
    with open(file, 'w', encoding='utf-8') as f:
        for ew in installations.values():
            if not frist: f.write('\n')
            else: frist=False
            f.write(ew.get_info())
    print('\nWrote ' + file + ' ... Done')

def _test(dr, subd):
    tk = find_tkdir(dr, subd)
    if not tk: return False
    inst = EwInst(os.path.basename(tk) + ' ' + os.path.basename(dr), dr, 'scan', tk)
    inst.check()
    print(f'{dr}: tk={os.path.basename(inst.toolkit_dir)} ide={str(inst.ide_exe is not None)}')
    return True

def _search_dirs(root, dirs):
    found = 0
    test = False
    failed = []
    for d in dirs:
        sd = os.path.join(root, d) if root else d
        subd = listsubdirs(sd)
        r = _test(sd, subd) if subd else False
        if r:
            found += 1
            test = True
        else:
            r = _search_dirs(sd, subd)
            if r == 0: failed.append(sd)
            found += r

    # If at least one installation found, print sibblings without installation
    if test:
        for d in failed:
            log.debug('Note: No installations found in ' + d)

    return found

def scan(rootdirs):
    total = 0
    for d in rootdirs:
        r = _search_dirs(None, [ d ])
        total += r
        if r == 0: print('Note: No installations found in ' + d)
    print('total: ' + str(total) + ' installations found')
