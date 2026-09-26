import locale
import os
import subprocess
from pathlib import Path

import argvars
import cfg
import config
import dialog
import ewinst
import expand
import log


def check_workspace(ws):
    if not ws:
        return ws
    if not Path(ws).is_absolute():
        log.die('path not absolute: ' + ws)
    if not ws.endswith('.eww'):
        ws += '.eww'
    return ws


def get_workspace(ws):
    def find_eww(dr):
        for f in dr.iterdir():
            if f.name.endswith('.eww'):
                return str(f)
        return ''

    if not ws:
        return ws
    # Path.resolve() would also expand subst and mapped network drives
    ws = os.path.abspath(ws)  # noqa: PTH100
    ws_path = Path(ws)

    if ws_path.is_dir():
        tmp = str(ws_path / ws_path.name) + '.eww'
        if Path(tmp).is_file():
            return tmp
        return find_eww(ws_path) or tmp

    if ws_path.is_file():
        if ws.endswith('.eww'):
            return ws
        if ws.endswith('.custom_argvars'):
            return str(ws_path.with_suffix('.eww'))

        log.die('Unexpected file name:' + ws)

    if Path(ws + '.eww').is_file():
        return ws + '.eww'

    return check_workspace(ws)


def create_workspace(ws, exp):
    ws_path = Path(ws)
    if not ws_path.is_file():
        if not ws_path.parent.is_dir():
            log.debug('Making directories')
            ws_path.parent.mkdir(parents=True)
        log.debug('Writing eww: ' + ws)
        ws_path.write_text(exp.expand(cfg.workspace_template),
                           encoding='utf8')


def launch(ws, ew_sel, exp):
    if cfg.subcmd == 'shell':
        comspec = os.environ.get('COMSPEC', 'cmd.exe')
        initenv = str(Path(cfg.ewlaunch_dir, 'init_shell.bat'))
        exp.setenv()
        if cfg.console:
            proc = subprocess.Popen([comspec, '/k', initenv])
            cfg.wait_after_launch = True
        else:
            proc = subprocess.Popen([comspec, '/k', initenv],
                                    creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        os.chdir(cfg.ewlaunch_dir)
        if ew_sel.ide_exe is None:
            log.die('EW version does not exist')
        cmd_args = [ew_sel.ide_exe]
        if ws:
            cmd_args.append(ws)
        log.debug('Launching: ' + cmd_args[0])
        proc = subprocess.Popen(cmd_args, shell=False)

    if cfg.wait_after_launch:
        proc.wait()


def main():
    config.read()
    exp = expand.Expand()
    arg_vars = argvars.ArgVars()

    if cfg.subcmd == 'scan':
        ewinst.scan(cfg.rest_args)
        ewinst.dump(cfg.out_file)
        return

    if cfg.reg:
        ewinst.add_from_reg()
    if cfg.installations:
        ewinst.add_from_file(exp.expand(cfg.installations))

    if cfg.subcmd == 'dump':
        ewinst.dump(cfg.out_file)
        return

    if cfg.subcmd == 'command':
        for ew in ewinst.getlist(cfg.version_filter):
            ew.check()
            exp.set_ew(ew)
            exp.setenv()
            if cfg.rest_args:
                if not cfg.noheading:
                    print(ew.key + ':')
                args = [str(Path(cfg.ewlaunch_dir, 'init_env.bat')),
                        '&&'] + cfg.rest_args
                ret = subprocess.run(args,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT,
                                     encoding=locale.getpreferredencoding(),
                                     check=False)
                print(ret.stdout.strip())
            else:
                print(ew.key)
        return

    ws = get_workspace(cfg.ws)
    log.debug('workspace: ' + ws)
    using_argvars = False
    argvars_ver = None

    if cfg.version:
        selsrc = 'Version specified on command line'
        ew_initial = ewinst.get(cfg.version)
    else:
        selsrc = ''
        ew_initial = None
        if Path(ws).is_file():
            argvars_ver = arg_vars.read(ws, exp)
            if argvars_ver:
                ew_initial = ewinst.get(argvars_ver)
                if ew_initial:
                    selsrc = 'Using version from argvars file'
                    using_argvars = True
                else:
                    selsrc = 'WARNING: Invalid version in argvars'
                selsrc += f' ({argvars_ver}).'
            else:
                selsrc = 'No version in argvars file. '

        if not ew_initial:
            ew_initial = ewinst.get(cfg.default_version)
            if not ew_initial:
                selsrc += 'Default is invalid.'
            else:
                selsrc += 'Using default value (' + cfg.default_version + ').'

    log.debug(selsrc)
    ew_sel = ew_initial
    if cfg.version:
        selected_save = False
    else:
        selected_save = cfg.default_save
        if cfg.always_show_dialog or not using_argvars:
            dlg = dialog.Dialog()
            if not dlg.show(ws, ew_initial, selsrc):
                log.debug('Dialog exit')
                return
            ws = dlg.ws
            ew_sel = dlg.ewi
            selected_save = dlg.selected_save

    ws = check_workspace(ws)
    if not ew_sel:
        log.die('could not find EW version')
    ew_sel.check()
    exp.set_ws(ws)
    exp.set_ew(ew_sel)
    if ws:
        create_workspace(ws, exp)
        if selected_save:
            arg_vars.save(ew_sel.key, exp)

    launch(ws, ew_sel, exp)
