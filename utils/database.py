import logging

import bcrypt
from pymongo import MongoClient

import setting

logger = logging.getLogger(__name__)

if setting.MONGO_ONLINE:
    client = MongoClient(setting.MONGO_URI)
else:
    client = MongoClient(setting.MONGO_HOST, setting.MONGO_PORT)

db = client[setting.MONGO_DATABASE]


def create_user(details):
    try:
        existing_user = db.users.find_one(
            { "$or": [{ "username": details["username"] }, { "email": details["email"] }] }
        )

        if existing_user:
            err_msg = "User with same username or email already exists"
            logger.error(err_msg)
            return err_msg

        password = details["password"].encode("utf-8")
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())

        details["password"] = hashed
        db.users.insert_one(details)

    except Exception as ex:
        logger.error(f"Exception Caught! {ex}")


def check_existing_user(details):
    try:
        if details:
            username = details.get("username")
            password = details.get("password").encode("utf-8")

            user = db.users.find_one({
                "username": username
            })

            if user:
                hashed = user["password"]
                if bcrypt.checkpw(password, hashed):
                    user["_id"] = str(user["_id"])
                    return user

    except Exception as ex:
        logger.error(f"Exception Caught! {ex}")
