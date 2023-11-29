import os
import bleach
import pyotp
import qrcode
from flask import Flask, render_template, request, session, url_for, redirect, flash
import sqlite3
from datetime import datetime

from pyotp import totp

from static.users_functions import (create_usertable, insert_users, user_login, register_user, logout, generate_totp_uri, verify_pw, verify_totp, get_user_by_username_or_email, store_totp_secret, hash_pw)
from static.posts import create_post_table, insert_posts, get_all_posts, get_post_by_id

app = Flask(__name__)
app.secret_key = os.urandom(24)


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
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        con.close()
        #todo, change redirect
    return render_template('add_posts.html', user = user)

@app.route('/login', methods=['GET', 'POST'])
def login_screen():
    if request.method == 'POST':
        username_or_email = request.form['username_or_email']
        password = request.form['password']
        totp_input = request.form['totp_input']

        user = get_user_by_username_or_email(username_or_email)

        if user and verify_pw(user[3], user[4], password):
            totp_secret = user[5]  # Assuming the TOTP secret is stored in the sixth column

            if totp_secret:
                # Continue with TOTP verification using the retrieved secret
                if verify_totp(totp_secret, totp_input):
                    # TOTP is valid, proceed with the login
                    flash('Welcome ' + user[2], 'success')
                    session['username_or_email'] = username_or_email
                    return redirect(url_for('home'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    # Clear the username or email from the session
    session.clear()
    print("Signed out")
    return redirect(url_for('home'))


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

            # Continue with other registration steps
            # ...

            totp_uri, img_path = generate_totp_uri(email, totp_secret, app)
            return render_template("register.html", totp_uri=totp_uri, img_path=img_path)

        else:
            print("Password did not match")

    return render_template("register.html")


if __name__ == '__main__':


    #Expose the ports and host, done so dockerfile will work
    app.run(host='0.0.0.0', port=5000)
