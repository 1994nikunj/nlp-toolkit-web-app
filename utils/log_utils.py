import logging
import logging.handlers
import sys

import setting

config = setting.log_config()

log_name = setting.APP_NAME
log_level = setting.LOGGING_LEVEL
log_format = '%(asctime)s| %(levelname)s: %(message)s |%(module)s[%(lineno)d]'


def log_initializer():
    root_logger = logging.getLogger()
    _file = 'logs/{}.log'.format(log_name.lower())

    # File Logging: RotatingFileHandler
    file_handler = logging.handlers.RotatingFileHandler(filename=_file,
                                                        maxBytes=config['max_bytes'],
                                                        backupCount=config['backup_count'])
    file_handler.setFormatter(logging.Formatter(log_format))
    file_handler.setLevel(log_level)
    root_logger.addHandler(file_handler)

    # Console Logging: StreamHandler
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.setFormatter(logging.Formatter(log_format))
    stdout_handler.setLevel(log_level)
    root_logger.addHandler(stdout_handler)
