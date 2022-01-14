import sys

import log, main, cfg

class Logger:
    def __init__(self):
        self.print_debug = False

    def debug(self, message):
        if self.print_debug:
            print(message)

    def die(self, message):
        print('died: ' + message)
        sys.exit(1)

cfg.exec_name = 'ewlaunch'
cfg.console = True

log.logger = Logger()
if '--debug' in sys.argv:
    log.logger.print_debug = True
    sys.argv.remove('--debug')

main.main()
