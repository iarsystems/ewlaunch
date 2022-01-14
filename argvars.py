import re, os

import log, cfg

class ArgVars:
    def __init__(self):
        self.last_read = None

    def read(self, ws, exp):
        exp.set_ws(ws)
        argvars_filename = exp.expand(cfg.argvars_path)

        log.debug('reading argvars:' + argvars_filename)
        try:
            argvars_file = open(argvars_filename, 'r', encoding='utf-8')
        except IOError:
            log.debug('Failed to open argvars file: ' + argvars_filename)
            return None
        argvars = argvars_file.read()
        m = re.search(cfg.argvars_version_re, argvars, re.M)
        if not m:
            log.debug('No match in argvars')
            return None
        self.last_read = m.group(2)
        return self.last_read

    def save(self, version, exp):
        argvars_filename = exp.expand(cfg.argvars_path)
        log.debug('saving argvars:' + argvars_filename)

        if version == self.last_read:
            log.debug('version not changed, skipping save')
            return

        if not os.path.isfile(argvars_filename):
            log.debug('Argvars file does not exist, creating it')
            with open(argvars_filename, 'w', encoding='utf-8') as argvars_file:
                argvars_file.write(exp.expand(cfg.template_header))
                argvars_file.write(exp.expand(cfg.template))
                argvars_file.write(exp.expand(cfg.template_footer))
            return

        with open(argvars_filename, 'r', encoding='utf-8') as argvars_file:
            argvars = argvars_file.read()

        m = re.search(cfg.argvars_version_re, argvars, re.M)
        if not m:
            log.debug('Argvars file exists, but does not contain EW_VERSION, adding it')
            with open(argvars_filename, 'w', encoding='utf-8') as argvars_file:
                argvars = argvars.replace('<iarUserArgVars/>',
                    '<iarUserArgVars>\n</iarUserArgVars>')
                argvars_file.write(argvars.replace(
                    '<iarUserArgVars>', '<iarUserArgVars>\n' + exp.expand(cfg.template)))
            return

        replaced_argvars = re.sub(cfg.argvars_version_re, m.group(1) + version, argvars, flags=re.M)
        if replaced_argvars == argvars:
            log.debug('No change to argvars, skip writing')
            return

        log.debug('Argvars file exists, and contains EW_VERSION, replacing it')
        with open(argvars_filename, 'w', encoding='utf-8') as argvars_file:
            argvars_file.write(replaced_argvars)
