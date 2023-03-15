import os
import time
from datetime import timedelta

from flask import Flask, g, redirect, render_template, request, session, url_for

import setting
import utils.log_utils as log
from utils import db_utils

log.log_initializer()
app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)


@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']


@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        session.pop('user', None)
        session.permanent = True
        obj_2 = db_utils.connection_2(request)
        try:
            if request.form['username'] == obj_2[0] and request.form['password'] == obj_2[1]:
                session['user'] = request.form['username']
                return redirect(url_for('home'))
        except TypeError:
            error = 'Invalid credentials'
    return render_template('login_page.html', error=error)


@app.route('/home')
def home():
    if g.user:
        curr_date, curr_time = get_date_time()
        obj_1 = db_utils.connection_1()
        return render_template('home_page.html', value=obj_1, time=curr_time, date=curr_date)
    return redirect(url_for('login'))


@app.route('/host', methods=['GET', 'POST'])
def host_info():
    if request.method == 'POST':
        tmp_host = request.form['host']
        tmp_category = request.form['category']
        tmp_oid = request.form['oid']
        tmp_site_id = request.form['siteId']
        tmp_match = request.form['submit']
        temp_data = [[tmp_host, tmp_category, tmp_oid, tmp_site_id, tmp_match]]
        return render_template('host_info_page.html', value=temp_data)


@app.route('/about/')
def about():
    return render_template('about.html')


@app.route('/logout/')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


def get_date_time():
    dt_s = list(time.localtime(time.time()))
    formatted_date = str(dt_s[1]) + "-" + str(dt_s[2]) + "-" + str(dt_s[0])
    temp = 'PM'
    if dt_s[3] <= 12:
        temp = 'AM'
    formatted_time = str(24 - dt_s[3]) + ":" + str(dt_s[4]) + ":" + str(
        dt_s[5]) + " " + temp

    return formatted_date, formatted_time


if __name__ == '__main__':
    app.logger.info('%%%%%%%%%%%%%%%%%%%%%%%% FLASK APP')
    if setting.USE_PORT:
        port = 9002
        host = "0.0.0.0"
        app.run(debug=setting.APP_DEBUG,
                port=port,
                host=host)
    else:
        app.run(debug=setting.APP_DEBUG)
