import os
import sqlite3
import hashlib
from datetime import time

import pyotp
import qrcode
from flask import Flask, request, session, url_for, redirect, render_template
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

#Function that prohibits user to sign if they type the worng password
