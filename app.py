
import os
import pyotp
import qrcode
from flask import Flask, render_template, request, session, url_for, redirect, flash
from authlib.integrations.flask_client import OAuth
import sqlite3
from datetime import datetime, timedelta, timezone
import time
from pyotp import totp
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import jsonify


from static.users_functions import (create_usertable, insert_users, register_user, logout,
                                     verify_pw, hash_pw,  authenticate_user,
                                    incorrect_input, lock_timer)

from static.posts import create_post_table, insert_posts, get_all_posts, get_post_by_id

from static.twofa import (generate_totp_uri, get_totp_secret_for_user,
                          verify_totp, get_user_by_username_or_email,
                          store_totp_secret)

app = Flask(__name__)
app.secret_key = os.urandom(24)
limiter = Limiter(app)

#Config for oauth, can probalby be moved to seperate file
oauth = OAuth(app)
google = oauth.register(
   #Insert from overleaf/discord
)
@app.route('/google_login', methods=['GET', 'POST'])
def google_login():
    google = oauth.create_client('google')  # create the google oauth client
    redirect_uri = url_for('auth', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route("/auth")
def auth():
    # create the google oauth client
    google = oauth.create_client('google')
    # Access token from google (needed to get user info)
    token = google.authorize_access_token()
    # userinfo contains stuff u specified in the scope
    resp = google.get('userinfo')
    user = resp.json()
    #session['email'] = user_info
    session['username_or_email'] =   user
    print(user)
    # permanent session browser needs to be closed to quit, hsa to be changed
    #session.permanent = True
    return redirect(url_for('home'))



@app.before_request
def before_request():
    limiter.key_func = lambda: request.remote_addr
@app.route('/')
def home():
    #calls create_ table function
    create_usertable()
    create_post_table()
    # calls insert functions
    insert_posts()
    insert_users()

    #connect to db
    data = get_all_posts()
    user = session.get('username_or_email')
    return render_template('home.html', data=data, user=user)



@app.route('/add_posts', methods=['GET', 'POST'])
def add_posts():
    # render html page "add_posts" if user is signed in
    user = session.get('username_or_email')
    return render_template('add_posts.html', user = user)


@app.route('/Posts', methods=['GET', 'POST'])
def all_posts():
    # Function to show entire post (title and belongning text)
    # based on title pressed on home screen
    title = request.args.get('title')
    post_id = request.args.get('id')
    con = sqlite3.connect("Blog.db")
    curs = con.cursor()
    #Query that gets the given post based on title and id
    curs.execute("SELECT * FROM posts WHERE title=? AND id=?", (title, post_id))
    data = curs.fetchone()
    con.close()
    return render_template('Posts.html', data=data)

# todo: split opp denne til routing og input to db??
@app.route('/new_posts', methods=['POST'])
def new_posts():
    # Function to add new blogposts
    user = session.get('username_or_email')
    title = request.form['title']  # Vulnerability here, as it's not sanitized
    text = request.form['text']  # Vulnerability here, as it's not sanitized
    #title = escape(request.form['title']) #Sanitized imput from user
    #text = escape(request.form['text']) #Sanitized input from user
    date = datetime.now().strftime("%Y-%m-%d %H:%M")  # Convert the datetime object to string
    con = sqlite3.connect('Blog.db')
    cur = con.cursor()
    try:
        cur.execute("INSERT INTO posts (title, text, date) VALUES (?, ?, ?)", (title, text, date))
        con.commit()
        print("Added to table")
        return render_template(url_for('home'))
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        con.close()
        #todo, change redirect
    return render_template('add_posts.html', user = user)



@app.route('/login', methods=['GET', 'POST'])
#dont thinklimiter works
@limiter.limit("3 per minute", key_func=get_remote_address)
def login_screen():
    # Initialize 'lockout' there is none in session
    if 'locked_out' not in session:
        session['locked_out'] = False
        session['lockout_start_time'] = None
    # Initialize 'wrong_input' there is none in session
    if 'wrong_input' not in session:
        session['wrong_input'] = 0

    if request.method == 'POST' and not session['locked_out']:
        lock_timer_res = lock_timer()

        if lock_timer_res:
            print("User is still in lockout period.")
            return render_template('login.html')

        username_or_email = request.form['username_or_email']
        password = request.form['password']
        totp_input = request.form['totp_input']

        if authenticate_user(username_or_email, password, totp_input):
            return redirect(url_for('home'))
        else:
            print('Invalid username or password. Please try again.')
            incorrect_input()

    lock_timer_res = lock_timer()
    if lock_timer_res:
        print("User is still in lockout period.")
        return render_template('login.html')

    return render_template('login.html')

@app.route('/logout')
def logout():
    # Clear the username or email from the session
    session.clear()
    print("Signed out")
    return redirect(url_for('home'))

#todo: redo register?
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':
        register_user()
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm-password']
        # Check if passwords match
        if password == confirm_password:
            password_hashed, random_val = hash_pw(password)

            # Generate and store TOTP secret for the user
            totp_secret = pyotp.random_base32()
            store_totp_secret(email, totp_secret)  # Implement this function to store the secret


            totp_uri, img_path = generate_totp_uri(email, totp_secret, app)
            return render_template("register.html", totp_uri=totp_uri, img_path=img_path)

        else:
            print("Password did not match")



    return render_template("register.html")

#add as a function, not route perhaps?
@app.route('/server-time')
def server_time():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"Server Time: {current_time}"





@app.errorhandler(429)
def ratelimit_error(e):
    remaining_time = int(e.description.split()[3])  # Extract remaining time from the error message
    minutes, seconds = divmod(remaining_time, 60)

    if minutes > 0:
        error_message = f"Too many incorrect login attempts. Please try again in {minutes} minutes."
    else:
        error_message = f"Too many incorrect login attempts. Please try again in {seconds} seconds."

    return jsonify(error="ratelimit exceeded", message=error_message), 429






if __name__ == '__main__':

    # app.config['SESSION_COOKIE_HTTPONLY'] = False #will allow us to get session cookies if we want
    # to create a script for it

    #Expose the ports and host, done so dockerfile will work
    app.run(host='0.0.0.0', port=5000, debug = True)
