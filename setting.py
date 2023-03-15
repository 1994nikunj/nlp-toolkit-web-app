APP_NAME = 'FLASK-APP'
USE_PORT = False
LOGGING_LEVEL = 'INFO'
APP_DEBUG = True


def log_config():
    return {
        'max_bytes': 50 * 1000 * 1000,  # Size in bytes
        'backup_count': 20  # Max count of log files allowed to be created when rotating
    }
