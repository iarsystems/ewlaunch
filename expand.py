import os
import cfg

_KEYS = {
    'WS_PATH' : 'Full path of .eww file',
    'WS_BPATH' : 'Path of .eww file, excluding file extension',
    'WS_FNAME' : 'File name of .eww file',
    'WS_BNAME' : 'File name of .eww file, excluding file extension',
    'WS_DIR' : 'Directory of .eww file',
    'EW_VERSION' : 'The version of IAR Embedded Workbench',
    'EW_DIR' : 'Top directory of IAR Embedded Workbench',
    'TOOLKIT' : 'Name of toolkit directory, e.g. "arm"',
    'TOOLKIT_DIR' : 'Full path of toolkit directory',
    'EWLAUNCH_DIR' : 'Full path fo EWLaunch directory'
}

class Expand:
    def __init__(self):
        self.attrs = {}
        for key in _KEYS:
            self.attrs[key] = ''
        self.set('EWLAUNCH_DIR', cfg.ewlaunch_dir)

    def set(self, k, v):
        self.attrs[k] = v

    def get(self, k):
        return self.attrs[k]

    def set_ew(self, ew):
        self.set('EW_VERSION', ew.key)
        self.set('EW_DIR', ew.ew_dir)
        self.set('TOOLKIT', os.path.basename(ew.toolkit_dir))
        self.set('TOOLKIT_DIR', ew.toolkit_dir)

    def set_ws(self, ws):
        self.set('WS_PATH', ws)
        self.set('WS_FNAME', os.path.basename(ws))
        self.set('WS_BNAME', self.get('WS_FNAME').replace('.eww', ''))
        self.set('WS_DIR', os.path.dirname(ws))
        self.set('WS_BPATH', os.path.join(self.get('WS_DIR'), self.get('WS_BNAME')))

    def expand(self, s):
        for key, val in self.attrs.items():
            s = s.replace(r'$' + key + r'$', val)
        return s

    def setenv(self):
        for key, val in self.attrs.items():
            os.environ[key] = val
