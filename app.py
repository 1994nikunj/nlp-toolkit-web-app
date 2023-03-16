from flask import Flask, redirect, render_template, request, url_for

import setting
import utils.log_utils as log
from utils.db_utils import check_existing_user, create_user

log.log_initializer()
app = Flask(__name__)


@app.route("/")
def home():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    # check if the user is valid
    details = {
        "username": request.form.get("username"),
        "password": request.form.get("password")
    }

    user = check_existing_user(details)

    if user:
        # login successful, redirect to the homepage
        return render_template("home.html")

    else:
        # login failed, redirect back to the login page with an error message
        error = "Invalid username or password"
        return render_template("login.html", error=error)


@app.route("/login", methods=["GET"])
def show_login():
    return render_template("login.html")


@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route("/register", methods=["POST"])
def register():
    # add the user to the database
    details = {
        "username": request.form.get("username"),
        "password": request.form.get("password"),
        "name":     request.form.get("name"),
        "email":    request.form.get("email")
    }

    existing_user = check_existing_user(details)
    if existing_user:
        # username already exists, redirect back to the signup page with an error message
        error = "Username already exists"
        return render_template("signup.html", error=error)

    error = create_user(details)
    if error:
        return render_template("signup.html", error=error)

    # registration successful, redirect to the login page
    message = f"New user created: {details['username']}"
    return render_template("login.html", message=message)


if __name__ == '__main__':
    app.logger.info('FLASK APP')
    if setting.USE_PORT:
        port = 9002
        host = "0.0.0.0"
        app.run(debug=setting.APP_DEBUG,
                port=port,
                host=host)
    else:
        app.run(debug=setting.APP_DEBUG)
