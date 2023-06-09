import datetime

from flask import Flask, render_template, request

import setting
import utils.logger as log
from utils.database import check_existing_user, create_user
from utils.nlp import TextAnalysis

log.log_initializer()
app = Flask(__name__)


@app.route("/")
def home():
    return render_template("login.html")


def get_datetime():
    return datetime.datetime.now().strftime("%d-%b-%Y %I:%M %p")


@app.route("/login", methods=["POST"])
def login():
    # check if the user is valid
    details = {
        "username": request.form.get("username"),
        "password": request.form.get("password")
    }

    user = check_existing_user(details)
    if user:
        _name = str(user['name']).strip().split(' ')[0]
        return render_template("home.html", user=_name, date_time=get_datetime())

    else:
        # login failed, redirect back to the login page with an error message
        error = "Invalid username or password"
        return render_template("login.html", error=error, date_time=get_datetime())


@app.route("/results", methods=["POST"])
def results():
    data = {
        # Files
        # [val.decode('utf-8') for val in data.get('input_raw')]
        'input_file': str(request.files['input_file'].filename),
        'input_raw': [val.decode('utf-8') for val in request.files.get('input_file').read().split()],
        'stopword_file': str(request.files['stopword_file'].filename),
        'stopword_raw': [val.decode('utf-8') for val in request.files.get('stopword_file').read().split()],
        'additional_stopwords': list(request.form.get('additional_stopwords').split()),

        # Checkboxes
        'save_graph': bool(request.form.get('save_graph')),
        'save_wordcloud': bool(request.form.get('save_wordcloud')),
        'save_text_statistics': bool(request.form.get('save_text_statistics')),

        # Inputs
        'ngram_size': int(request.form.get('ngram_size')),
        'number_of_topics': int(request.form.get('number_of_topics')),
        'min_word_length': int(request.form.get('min_word_length')),
        'word_window': int(request.form.get('word_window')),
        'n_sim_element': int(request.form.get('n_sim_element'))
    }

    try:
        text_analysis = TextAnalysis(data)
        result = text_analysis.run_analysis()
    except Exception as e:
        print(f'Error during NLP analysis: {e}')
        error = 'Error while performing NLP analysis'
        return render_template("results.html", error=error, date_time=get_datetime())
    else:
        return render_template("results.html", results=result, date_time=get_datetime())


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
        "name": request.form.get("name"),
        "email": request.form.get("email")
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
