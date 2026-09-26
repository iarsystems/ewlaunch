import re
from pathlib import Path

import cfg
import log


class ArgVars:
    def __init__(self):
        self.last_read = None

    def read(self, ws, exp):
        exp.set_ws(ws)
        argvars_filename = exp.expand(cfg.argvars_path)

        log.debug('reading argvars:' + argvars_filename)
        try:
            argvars = Path(argvars_filename).read_text(encoding='utf-8')
        except OSError:
            log.debug('Failed to open argvars file: ' + argvars_filename)
            return None
        m = re.search(cfg.argvars_version_re, argvars, re.MULTILINE)
        if not m:
            log.debug('No match in argvars')
            return None
        self.last_read = m.group(2)
        return self.last_read

    def save(self, version, exp):
        argvars_filename = exp.expand(cfg.argvars_path)
        log.debug('saving argvars:' + argvars_filename)
        argvars_file = Path(argvars_filename)

        if version == self.last_read:
            log.debug('version not changed, skipping save')
            return

        if not argvars_file.is_file():
            log.debug('Argvars file does not exist, creating it')
            argvars_file.write_text(exp.expand(cfg.template_header)
                                    + exp.expand(cfg.template)
                                    + exp.expand(cfg.template_footer),
                                    encoding='utf-8')
            return

        argvars = argvars_file.read_text(encoding='utf-8')

        m = re.search(cfg.argvars_version_re, argvars, re.MULTILINE)
        if not m:
            log.debug('Argvars file exists, with no EW_VERSION, adding it')
            argvars = re.sub(
                '<iarUserArgVars */>',
                '<iarUserArgVars>\n</iarUserArgVars>',
                argvars)
            argvars_file.write_text(argvars.replace(
                '<iarUserArgVars>',
                '<iarUserArgVars>\n' + exp.expand(cfg.template)),
                encoding='utf-8')
            return

        replaced_argvars = re.sub(cfg.argvars_version_re, m.group(
            1) + version, argvars, flags=re.MULTILINE)
        if replaced_argvars == argvars:
            log.debug('No change to argvars, skip writing')
            return

        log.debug('Argvars file exists, and contains EW_VERSION, replacing it')
        argvars_file.write_text(replaced_argvars, encoding='utf-8')
