import logging

import sqlite3 as sql

logger = logging.getLogger(__name__)


def connection_1():
    try:
        db_conn = sql.connect('static/database/rtp_response_database.db')
        cur = db_conn.cursor()
    except Exception as excp:
        logger.error("Exception Caught! {}".format(excp))
    else:
        try:
            cur.execute("SELECT * FROM tpas_scheduled_poller_tracker")
            return cur.fetchall()
        except Exception as excp:
            logger.error("Exception Caught! {}".format(excp))
        finally:
            cur.close()
            db_conn.close()


def connection_2(request):
    try:
        db_conn = sql.connect('static/database/credentials_manager.db')
        cur = db_conn.cursor()
    except Exception as excp:
        logger.error("Exception Caught! {}".format(excp))
    else:
        try:
            cur.execute("SELECT * FROM get_uname_pwd WHERE username={} AND password={}".format(
                "'" + request.form['username'] + "'",
                "'" + request.form['password'] + "'"))
            return cur.fetchone()
        except Exception as excp:
            logger.error("Exception Caught! {}".format(excp))
        finally:
            cur.close()
            db_conn.close()
