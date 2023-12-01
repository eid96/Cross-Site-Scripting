import os
import sqlite3
import hashlib
from datetime import time
from datetime import datetime, timedelta, timezone
import pyotp
import qrcode
from flask import Flask, request, session, url_for, redirect, render_template, flash
from static.twofa import (verify_totp, get_user_by_username_or_email,
                          store_totp_secret)


def create_usertable():
    con = sqlite3.connect('Blog.db')
    cur = con.cursor()
    # adding the random value to db (salt)
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
               id INTEGER PRIMARY KEY,
               email TEXT NOT NULL,
               username TEXT NOT NULL,
               password TEXT NOT NULL,
               random_value TEXT NOT NULL,
               totp_secret TEXT
           )''')
    con.commit()
    con.close()


def insert_users():
    con = sqlite3.connect('Blog.db')
    cur = con.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    data = cur.fetchone()[0]

    if data == 0:
        users = [
            ('User1@mail.com', 'user1', 'password1', 'totp_secret_1'),
            ('User2@mail.com', 'user2', 'password2', 'totp_secret_2'),
            ('User3@mail.com', 'user3', 'password3', 'totp_secret_3')
        ]
        for user in users:
            password_hashed, random_val = hash_pw(user[2])  # Hashing the plain text password
            cur.execute(
                "INSERT INTO users (email, username, password, random_value, totp_secret) VALUES (?, ?, ?, ?, ?)",
                (user[0], user[1], password_hashed, random_val, user[3])
            )

        con.commit()
    con.close()


def user_login(identity, password):
    con = sqlite3.connect('Blog.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE email=? OR username=?", (identity, identity))
    user = cur.fetchone()

    if user and verify_totp(user[5], password):
        session['username_or_email'] = identity
        con.close()
        return user
    else:
        con.close()
        return None


def register_user():
    # sets user input for registering a new user
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    confirm_password = request.form['confirm-password']
    con = sqlite3.connect('Blog.db')
    cur = con.cursor()
    # checks if passwords are the same
    if password == confirm_password:
        password_hashed, random_val = hash_pw(password)

        # Generate TOTP secret for the user
        totp_secret = pyotp.random_base32()

        cur.execute("INSERT INTO users (email, username, password, random_value, totp_secret) VALUES (?, ?, ?, ?, ?)",
                    (email, username, password_hashed, random_val, totp_secret))
        con.commit()
        con.close()
        print("User registered")

    else:
        print("Password did not match")


def logout():
    session.clear()
    print("Signed out")


# Implementation of hashing using hasblib
def hash_pw(password):
    # random_val= salt, went away from tranditional naming
    # Generates and stores a 32*2 bytes of random characters
    random_val = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    # Computes the hash for the given password and adds the random val
    password_hashed = hashlib.pbkdf2_hmac('sha256',
                                          password.encode('utf-8'), random_val, 100000)

    return password_hashed, random_val


def verify_pw(db_pw, db_random_val, ipw):
    # Hash the input password using the stored random value
    password_hashed = hashlib.pbkdf2_hmac('sha256', ipw.encode('utf-8'), db_random_val, 100000)
    # Compare hashed password with plain text password
    return password_hashed == db_pw


def authenticate_user(username_or_email, password, totp_input):
    user = get_user_by_username_or_email(username_or_email)

    if user and verify_pw(user[3], user[4], password):
        totp_secret = user[5]

        if totp_secret and verify_totp(totp_secret, totp_input):
            flash('Welcome ' + user[2], 'success')
            session['username_or_email'] = username_or_email
            # Authentication successful
            return True
            # Authentication failed
    return False

def incorrect_input():
    # Initialize 'wrong_input' there is none in session
    if 'wrong_input' not in session:
        session['wrong_input'] = 0

    # Increase counter for wrong inputs
    session['wrong_input'] += 1
    print("sign-in attempts: ", session['wrong_input'])

    if session['wrong_input'] == 3:
        session['locked_out'] = True
        session['lockout_start_time'] = datetime.utcnow().replace(tzinfo=timezone.utc)



def lock_timer():
    # Check if the user is still in the lockout period
    if session['lockout_start_time']:
        time_elapsed = (datetime.utcnow().replace(tzinfo=timezone.utc) - session['lockout_start_time']).seconds
        #Check how much time has gone and print
        if time_elapsed <= 60:
            remaining_time = 60 - time_elapsed
            print(f'Remaining lockout time: {remaining_time} seconds')  # Added countdown print statement
            flash(
                f'Too many failed attempts.  Try again later in {int(remaining_time)} seconds.',
                'error')
            return True  # User is still in lockout period
        else:
            # Reset the wrong input count and lockout
            session['wrong_input'] = 0
            session['locked_out'] = False
            session['lockout_start_time'] = None
    # No lockout
    return False
