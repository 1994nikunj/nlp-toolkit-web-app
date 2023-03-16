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
        # Check if user with same username or email already exists
        existing_user = db.users.find_one(
            { "$or": [{ "username": details["username"] }, { "email": details["email"] }] })

        if existing_user:
            err_msg = "User with same username or email already exists"
            logger.error(err_msg)
            return err_msg

        # Encode the password using bcrypt
        password = details["password"].encode("utf-8")
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())

        # Insert user into "users" collection with the hashed password
        details["password"] = hashed
        db.users.insert_one(details)

    except Exception as ex:
        logger.error(f"Exception Caught! {ex}")


def check_existing_user(details):
    try:
        username = details.get("username")
        password = details.get("password").encode("utf-8")

        # Find user with matching username in "users" collection
        user = db.users.find_one({ "username": username })

        if user:
            # Decode the stored hashed password and check if it matches the entered password
            hashed = user["password"]
            if bcrypt.checkpw(password, hashed):
                user["_id"] = str(user["_id"])  # convert ObjectId to string
                return user

    except Exception as ex:
        logger.error(f"Exception Caught! {ex}")
