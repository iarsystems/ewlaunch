import ewinst
import configparser, time

def _multiline(str):
    return (str.replace(str[0], "") if str[0] == '|' else str) + "\n"

class Config:
    def read(self):
        cfg = configparser.ConfigParser()
        cfg.read('ewlaunch.ini')
        self.always_show_dialog = cfg.getboolean('flags', 'select', fallback=False)
        self.noreg = cfg.getboolean('flags', 'noreg', fallback=False)
        self.always_show_log = cfg.getboolean('flags', 'log', fallback=False)
        self.wait_after_launch = cfg.getboolean('flags', 'wait', fallback=False)
        self.default_version = cfg['gui']['default_selected_version']
        self.default_save = cfg.getboolean('gui', 'default_selected_save_in_project')
        self.list_box_lines = cfg.getint('gui', 'list_box_lines', fallback=10)
        self.min_window_width = cfg.getint('gui', 'min_window_width', fallback=500)
        self.info_pane = cfg.getboolean('gui', 'info_pane', fallback=True)

        self.template_header = _multiline(cfg['argvars']['template_header'])
        self.template = _multiline(cfg['argvars']['template'])
        self.template_footer = _multiline(cfg['argvars']['template_footer'])
        self.argvars_path = cfg['argvars']['path']
        self.argvars_version_re = cfg['argvars']['version_re']
        self.workspace_template = _multiline(cfg['workspace']['template'])
        self.shortname = cfg['shortname'] if 'shortname' in cfg else {}

cfg = Config()
