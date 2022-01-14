import log, main, dialog_logger, cfg

cfg.exec_name = 'ewlaunch_win'
cfg.console = False

log.logger = dialog_logger.Log('EWlaunch')
log.logger.run(main.main)
if cfg.always_show_log:
    log.logger.dialog()
