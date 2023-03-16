# FLASK
APP_NAME = 'FLASK-APP'
USE_PORT = False
APP_DEBUG = False

# LOGGING:
LOG_MAX_BYTES = 50 * 1000 * 1000  # Size in bytes
LOG_BACKUP_COUNT = 20  # Max count of log files allowed to be created when rotating
LOG_FORMAT = '%(asctime)s| %(levelname)s: %(message)s |%(module)s[%(lineno)d]'
LOG_LEVEL = 'INFO'

# DATABASE:
MONGO_ONLINE = False
MONGO_DATABASE = "credentials"
if MONGO_ONLINE:
    MONGO_URI = "mongodb+srv://<username>:<password>@<cluster>.mongodb.net/<dbname>?retryWrites=true&w=majority"
else:
    MONGO_HOST = 'localhost'
    MONGO_PORT = 27017
