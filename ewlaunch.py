import dialog, ewinst, argvars, log
from config import cfg
from expand import exp

import sys, os, argparse, subprocess, time, re


def find_eww(dir):
    for f in os.listdir(dir):
        if f.endswith(".eww"):
            return dir + '\\' + f
    return None

def main():
    log.dialog_title = "ewlaunch"
    parser = argparse.ArgumentParser(description='Open IAR Embedded Workbench')
    parser.add_argument('workspace', nargs='?', default="", help='path to an .eww file to open, or a directory to create new .eww file')
    parser.add_argument('--select', action='store_true', help='always show dialog')
    parser.add_argument('--dump',  help='write EW installation data to file')
    parser.add_argument('--noreg',  action='store_true', help='skip looking in registry')
    args = parser.parse_args()

    ws = args.workspace
    if ws: ws = os.path.abspath(ws)

    print("cwd:" + os.getcwd())
    print("argv:" + str(sys.argv))
    # when starting by associating .eww file extension with ewlaunch, cwd is win\system32 dir
    ewlaunch_dir = os.path.dirname(sys.argv[0])
    if ewlaunch_dir:
        os.chdir(ewlaunch_dir)
        print("cwd:" + os.getcwd())

    cfg.read()

    if args.select: cfg.always_show_dialog = True
    if args.noreg: cfg.noreg = True

    if not cfg.noreg:
        ewinst.add_from_reg()
    ewinst.add_from_file()
    if args.dump:
        ewinst.dump(args.dump)
        return

    ew_initial = None
    using_argvars = False
    always_show_dialog = cfg.always_show_dialog
    orig_ws_is_dir = False
    argvars_ver = None
    selsrc = ""
    if ws != "":
        if os.path.isdir(ws):
            orig_ws_is_dir = True
            ws += '\\' + os.path.basename(ws) + ".eww"
        else:
            ws = re.sub('[.][_a-zA-Z0-9]+$', '.eww', ws)

        if not os.path.isfile(ws):
            f = find_eww(os.path.dirname(ws))
            if f:
                ws = f
                if not orig_ws_is_dir: always_show_dialog = True

        if os.path.isfile(ws):
            argvars_ver = argvars.read(ws)
            if argvars_ver:
                ew_initial = ewinst.get(argvars_ver)
                if ew_initial:
                    selsrc = "Using version from argvars file (" + argvars_ver + ")."
                    using_argvars = True
                else:
                    selsrc = "WARNING: Invalid version in argvars (" + argvars_ver + "). "
            else:
                selsrc = "No version in argvars file. "

    if not ew_initial:
        ew_initial = ewinst.get(cfg.default_version)
        if not ew_initial:
            selsrc += "Default is invalid."
        else:
            selsrc += "Using default value (" + cfg.default_version + ")."

    print(selsrc)

    ew_sel = ew_initial
    selected_save = cfg.default_save
    if always_show_dialog or not using_argvars:
        dlg = dialog.Dialog()
        if not dlg.show(ws, ew_initial, selsrc):
            print("Dialog exit")
            return
        ws = dlg.ws
        ew_sel = dlg.ewi
        selected_save = dlg.selected_save

    exp.set_ws(ws)
    exp.set_ew(ew_sel)

    if ew_sel is None:
        log.die("could not find EW version")

    if ew_sel.exists() is False:
        log.die("EW version does not exist")

    if ws != "":
        if not os.path.isfile(ws):
            dn = os.path.dirname(ws)
            if not os.path.isdir(dn):
                print("Making directories")
                os.makedirs(dn)
            print("Writing eww: " + ws)
            with open(ws, "w") as f:
                f.write(exp.expand(cfg.workspace_template))

        if selected_save and not (using_argvars and (ew_sel == ew_initial)):
            argvars.save(ws, ew_sel.key())

    print("Launching: " + ew_sel.executable() + " " + ws)
    args = [ ew_sel.executable() ]
    if ws: args.append(ws)
    proc = subprocess.Popen(args, shell=False)
    if cfg.wait_after_launch: proc.wait()

def call_main():
    main()
    if cfg.always_show_log:
        log.dialog()

log.run(call_main)
