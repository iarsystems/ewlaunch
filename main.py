import os, subprocess, locale

import ewinst, argvars, dialog, log, cfg, expand, config

def check_workspace(ws):
    if not ws: return ws
    if not os.path.isabs(ws): log.die('path not absolute: ' + ws)
    if not ws.endswith('.eww'): ws += '.eww'
    return ws

def get_workspace(ws):
    def find_eww(dr):
        for f in os.listdir(dr):
            if f.endswith('.eww'):
                return os.path.join(dr, f)
        return ''

    if not ws: return ws
    ws = os.path.abspath(ws)

    if os.path.isdir(ws):
        tmp = os.path.join(ws, os.path.basename(ws)) + '.eww'
        if os.path.isfile(tmp): return tmp
        tmp2 = find_eww(ws)
        if tmp2: return tmp2
        return tmp

    if os.path.isfile(ws):
        if ws.endswith('.eww'):
            return ws
        if ws.endswith('.custom_argvars'):
            return ws.replace('.custom_argvars', '.eww')

        log.die('Unexpected file name:' + ws)

    if os.path.isfile(ws + '.eww'):
        return ws + '.eww'

    return check_workspace(ws)

def create_workspace(ws, exp):
    if not os.path.isfile(ws):
        dn = os.path.dirname(ws)
        if not os.path.isdir(dn):
            log.debug('Making directories')
            os.makedirs(dn)
        log.debug('Writing eww: ' + ws)
        with open(ws, 'w', encoding='utf8') as f:
            f.write(exp.expand(cfg.workspace_template))

def launch(ws, ew_sel, exp):
    if cfg.subcmd == 'shell':
        initenv = os.path.join(cfg.ewlaunch_dir, 'init_shell.bat')
        exp.setenv()
        if cfg.console:
            proc = subprocess.Popen('cmd /k ' + initenv, shell=False)
            cfg.wait_after_launch = True
        else:
            proc = subprocess.Popen('start cmd /k ' + initenv, shell=True)
    else:
        os.chdir(cfg.ewlaunch_dir)
        if ew_sel.ide_exe is None: log.die('EW version does not exist')
        cmd_args = [ ew_sel.ide_exe ]
        if ws: cmd_args.append(ws)
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
                args = [os.path.join(cfg.ewlaunch_dir, 'init_env.bat'), '&&'] + cfg.rest_args
                ret = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                        encoding=locale.getpreferredencoding(), check=False)
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
        if os.path.isfile(ws):
            argvars_ver = arg_vars.read(ws, exp)
            if argvars_ver:
                ew_initial = ewinst.get(argvars_ver)
                if ew_initial:
                    selsrc = 'Using version from argvars file (' + argvars_ver + ').'
                    using_argvars = True
                else:
                    selsrc = 'WARNING: Invalid version in argvars (' + argvars_ver + '). '
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
    if not ew_sel: log.die('could not find EW version')
    ew_sel.check()
    exp.set_ws(ws)
    exp.set_ew(ew_sel)
    if ws:
        create_workspace(ws, exp)
        if selected_save:
            arg_vars.save(ew_sel.key, exp)

    launch(ws, ew_sel, exp)
