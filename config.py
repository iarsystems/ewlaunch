import configparser, os, sys, argparse

import cfg

def _parse_command_line():
    parser = argparse.ArgumentParser(description='Open IAR Embedded Workbench', prog=cfg.exec_name)
    if cfg.console:
        parser.add_argument('--debug', action='store_true', help='print debug messages')
    subp = parser.add_subparsers(help='see "ewlaunch [sub-command] --help"', dest='subparser_name')

    def opt_installations(p):
        p.add_argument('--installations', help='Specify the name of an installations file.')
        p.add_argument('--reg',  action='store_true',
                        help='with --installations file: look also in registry')

    def opt_open_and_shell(p):
        p.add_argument('--select', action='store_true', help='always show selection dialog')
        p.add_argument('workspace', nargs='?', default='', help='path to workspace/directory')
        p.add_argument('--version', help='version (no selection dialog)')
        p.add_argument('--wait', action='store_true',
                        help='Wait around until launched EW/shell exits')
        if not cfg.console:
            p.add_argument('--log', action='store_true', help='Always show log when done')
        opt_installations(p)

    p = subp.add_parser('open', help='open an existing workspace, or create a new one')
    opt_open_and_shell(p)

    p = subp.add_parser('shell', help='open a cmd.exe shell')
    opt_open_and_shell(p)

    if cfg.console:
        p = subp.add_parser('command', help='run a command on selected version(s)')
        opt_installations(p)
        p.add_argument('filter', help='regex that selects EW versions')
        p.add_argument('command', nargs='*', help='command. If not specified, prints EW versions')
        p.add_argument('--noheading', action='store_true',
                        help="don't print EW version before command output")

        p = subp.add_parser('dump', help='write known installations to a file')
        p.add_argument('--file', nargs='?', default='dump.ini', help='output file')
        opt_installations(p)

        p = subp.add_parser('scan', help='scan directories for installations')
        p.add_argument('directories', metavar='DIR', nargs='+',
                        help='directory to search for installations')
        p.add_argument('--file', nargs='?', default='scan.ini',
                        help='output file')

    argv = sys.argv[1:]
    # pylint: disable=protected-access
    if len(argv) < 1 or argv[0] not in ['-h', '--help'] + list(subp._name_parser_map.keys()):
        argv.insert(0, 'open')

    return parser.parse_args(argv)

def _multiline(s):
    return (s.replace(s[0], '') if s[0] == '|' else s) + '\n'

def read():
    args = _parse_command_line()

    cfg.ewlaunch_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    ini = configparser.ConfigParser()
    ini.read(os.path.join(cfg.ewlaunch_dir, 'ewlaunch.ini'))

    def getarg(name, fallback=None):
        v = getattr(args, name) if name in args else None
        return v if v else fallback

    def getflag(name, fallback=False):
        return getarg(name, ini.getboolean('args', name, fallback=fallback))

    def getstr(name, fallback=None):
        return getarg(name, ini.get('args', name, fallback=fallback))

    cfg.always_show_dialog = getflag('select')
    cfg.always_show_log = getflag('log')
    cfg.wait_after_launch = getflag('wait')
    cfg.installations = getstr('installations')
    if cfg.installations and not os.path.isabs(cfg.installations):
        cfg.installations = os.path.join(cfg.ewlaunch_dir, cfg.installations)
    cfg.reg = getflag('reg', fallback=(cfg.installations is None))
    cfg.default_version = ini['gui']['default_selected_version']
    cfg.default_save = ini.getboolean('gui', 'default_selected_save_in_project')
    cfg.list_box_lines = ini.getint('gui', 'list_box_lines', fallback=10)
    cfg.min_window_width = ini.getint('gui', 'min_window_width', fallback=500)
    cfg.info_pane = ini.getboolean('gui', 'info_pane', fallback=True)
    cfg.template_header = _multiline(ini['argvars']['template_header'])
    cfg.template = _multiline(ini['argvars']['template'])
    cfg.template_footer = _multiline(ini['argvars']['template_footer'])
    cfg.argvars_path = ini['argvars']['path']
    cfg.argvars_version_re = ini['argvars']['version_re']
    cfg.workspace_template = _multiline(ini['workspace']['template'])
    cfg.shortname = ini['shortname'] if 'shortname' in ini else {}

    # command line args:
    cfg.subcmd = args.subparser_name
    cfg.ws = getarg('workspace', '')
    cfg.version = getarg('version')
    cfg.out_file = getarg('file')
    cfg.rest_args = getarg('directories')
    cfg.version_filter = getarg('filter')
    if cfg.subcmd == 'command':
        cfg.rest_args = getarg('command')
        cfg.noheading = getarg('noheading')
