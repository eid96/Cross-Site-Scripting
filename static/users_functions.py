import os
import sqlite3
import hashlib
import pyotp
import qrcode
from flask import Flask, request, session, url_for, redirect, render_template
from werkzeug.security import check_password_hash

def create_usertable():
    con = sqlite3.connect('Blog.db')
    cur = con.cursor()
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
    random_val = os.urandom(60).hex().encode('ascii')
    password_hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), random_val, 100000)
    print("print hash from hash_pw: ", password_hashed)
    return password_hashed, random_val



def verify_pw(db_pw, db_random_val, ipw):
    # Hash the input password using the stored random value
    password_hashed = hashlib.pbkdf2_hmac('sha256', ipw.encode('utf-8'), db_random_val, 100000)
    print("og password : ", password_hashed)
    print("db password: ", db_pw)
    # Compare hashed password
    return password_hashed == db_pw


# Function to generate TOTP URI
def generate_totp_uri(email, key, app):
    totp = pyotp.totp.TOTP(key)
    uri = totp.provisioning_uri(name=email, issuer_name='FlaskProject')

    # Save QR code image to a file
    img = qrcode.make(uri)
    img_path = os.path.join(app.static_folder, 'qrcodes', 'QRcode.png')
    img.save(img_path)

    return uri, img_path

# Verify a Time-based One-Time Password (TOTP)
def verify_totp(totp_secret, totp_input):
    print("TOTP Secret:", totp_secret)
    print("Input TOTP:", totp_input)

    totp = pyotp.TOTP(totp_secret)
    result = totp.verify(totp_input)

    print("Verification Result:", result)

    return result
# Retrieve user information based on email or username
def get_user_by_username_or_email(identity):
    con = sqlite3.connect('Blog.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE email=? OR username=?", (identity, identity))
    user = cur.fetchone()
    con.close()
    return user

# Store the TOTP secret in the database
def store_totp_secret(email, totp_secret):
    con = sqlite3.connect('Blog.db')
    cur = con.cursor()
    cur.execute("UPDATE users SET totp_secret=? WHERE email=?", (totp_secret, email))
    con.commit()
    con.close()
