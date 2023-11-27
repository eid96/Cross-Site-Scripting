import sqlite3

from flask import Flask, render_template, request, session, url_for, redirect, escape


def create_usertable():
    con = sqlite3.connect('Blog.db')
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
               id INTEGER PRIMARY KEY,
               email TEXT NOT NULL,
               username TEXT NOT NULL,
               password TEXT NOT NULL
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
            ('User1@mail.com', 'user1', 'password1'),
            ('User2@mail.com', 'user2', 'password2'),
            ('User3@mail.com', 'user3', 'password3')
        ]
        for user in users:
            cur.execute("INSERT INTO users (email, username, password) VALUES (?, ?, ?)", user)

        con.commit()
    con.close()


def user_login(identity, password):
    con = sqlite3.connect('Blog.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE email=? OR username=?", (identity, identity))
    user = cur.fetchone()

    if user and user[3] == password:
        print("Welcome ", user[2])
        session['username_or_email'] = identity
        con.close()
        return True
    else:
        print("Wrong input")
        return False

def register_user():
    #sets userinput for registering new user
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    confirm_password = request.form['confirm-password']
    con = sqlite3.connect('Blog.db')
    cur = con.cursor()
    #checks if passwords are the same
    if password == confirm_password:
        cur.execute("INSERT INTO users (email, username, password) VALUES (?, ?, ?)"
                    , (email, username, password) )
        con.commit()
        con.close()
        #redirects home if passwords match
        return redirect(url_for('home'))
    else:
        print("Password did not match")


def logout():
    session.clear()
    print("Signed out")
