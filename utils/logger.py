import logging
import logging.handlers
import sys

from setting import APP_NAME, LOG_BACKUP_COUNT, LOG_FORMAT, LOG_LEVEL, LOG_MAX_BYTES


def log_initializer():
    root_logger = logging.getLogger()
    _file = 'logs/{}.log'.format(APP_NAME.lower())

    # File Logging: RotatingFileHandler
    file_handler = logging.handlers.RotatingFileHandler(filename=_file,
                                                        maxBytes=LOG_MAX_BYTES,
                                                        backupCount=LOG_BACKUP_COUNT)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    file_handler.setLevel(LOG_LEVEL)
    root_logger.addHandler(file_handler)

    # Console Logging: StreamHandler
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    stdout_handler.setLevel(LOG_LEVEL)
    root_logger.addHandler(stdout_handler)
