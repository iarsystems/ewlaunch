import log
from config import cfg
from expand import exp
import re, os

def read(ws):
    exp.set_ws(ws)
    argvars_filename = exp.expand(cfg.argvars_path)
    print("reading argvars:" + argvars_filename)

    try:
        argvars_file = open(argvars_filename, "r")
    except:
        print("Failed to open argvars file: " + argvars_filename)
        return None
    argvars = argvars_file.read()
    m = re.search(cfg.argvars_version_re, argvars, re.M)
    if not m:
        print("No match in argvars")
        return None
    return m.group(2)

def save(ws, version):
    argvars_filename = exp.expand(cfg.argvars_path)
    print("saving argvars:" + argvars_filename)

    if not os.path.isfile(argvars_filename):
        print("Argvars file does not exist, creating it")
        with open(argvars_filename, "w") as argvars_file:
            argvars_file.write(exp.expand(cfg.template_header))
            argvars_file.write(exp.expand(cfg.template))
            argvars_file.write(exp.expand(cfg.template_footer))
        return

    with open(argvars_filename, "r") as argvars_file:
        argvars = argvars_file.read()

    m = re.search(cfg.argvars_version_re, argvars, re.M)
    if not m:
        print("Argvars file exists, but does not contain EW_VERSION, adding it")
        with open(argvars_filename, "w") as argvars_file:
            argvars = argvars.replace("<iarUserArgVars/>", "<iarUserArgVars>\n</iarUserArgVars>")
            argvars_file.write(argvars.replace("<iarUserArgVars>", "<iarUserArgVars>\n" + exp.expand(cfg.template)))
        return

    replaced_argvars = re.sub(cfg.argvars_version_re, m.group(1) + version, argvars, flags=re.M)
    if replaced_argvars == argvars:
        print("No change to argvars, skip writing")
        return

    print("Argvars file exists, and contains EW_VERSION, replacing it")
    with open(argvars_filename, "w") as argvars_file:
        argvars_file.write(replaced_argvars)
    return
