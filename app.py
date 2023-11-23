import os
import bleach
from flask import Flask, render_template, request, session, url_for, redirect, escape
import sqlite3
from datetime import datetime
import hashlib

app = Flask(__name__)



@app.route('/')
def home():
    # function that render default homescreen with titles for each post
    # also gets id corresponding to the title, so right text is shown
    # when title is pressed and orders it by date
    create_db()
    create_usertable()
    insert()
    con = sqlite3.connect("Blog.db")
    curs = con.cursor()
    curs.execute("SELECT id, title FROM posts ORDER BY date DESC")
    data = curs.fetchall()
    con.close()
    user = session.get('username_or_email')
    return render_template('home.html', data=data, user = user)

def create_db():
    con = sqlite3.connect('Blog.db')
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS posts (
             id INTEGER PRIMARY KEY,
             title TEXT NOT NULL,
             text TEXT NOT NULL,
             date TEXT NOT NULL
         )
     ''')
    con.commit()
    con.close()

def create_usertable():
    con = sqlite3.connect('Blog.db')
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
               id INTEGER PRIMARY KEY,
               email TEXT NOT NULL,
               username TEXT NOT NULL,
               password TEXT NOT NULL
           )
       ''')
    con.commit()
    con.close()

def insert():
    con = sqlite3.connect('Blog.db')
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM posts")
    data = cur.fetchone()[0]
    if data == 0:
        # Adding test posts
        posts = [
            ('First Post', 'This is the text for the first post.', datetime.now()),
            ('Second Post', 'This is the text for the second post.', datetime.now()),
            ('Third Post', 'test', datetime.now())
        ]
        # Inserting the posts into the table if the table is empty
        for post in posts:
            cur.execute("INSERT INTO posts (title, text, date) VALUES (?, ?, ?)", post)

    cur.execute("SELECT COUNT(*) FROM users")
    da = cur.fetchone()[0]
    if da == 0:
        users = [
            ('User1@mail.com', 'user1', 'password1'),
            ('User2@mail.com', 'user2', 'password2'),
            ('User3@mail.com', 'user3', 'password3')
        ]
        for user in users:
            cur.execute("INSERT INTO users (email, username, password) VALUES (?, ?, ?)", user)

        con.commit()
    con.close()


@app.route('/add_posts', methods=['GET', 'POST'])
def add_posts():
    # render html page "add_posts"
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
    curs.execute("SELECT * FROM posts WHERE title=? AND id=?", (title, post_id))
    data = curs.fetchone()
    con.close()
    return render_template('Posts.html', data=data)


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
    return render_template('add_posts.html', user = user)

@app.route('/login', methods=['GET', 'POST'])
def login_screen():
    print("hello from login")
    if request.method == 'POST':
        username_or_email = request.form['username_or_email']
        password = request.form['password']
        if user_login(username_or_email, password):
            return redirect(url_for('home'))
    return render_template('login.html')

def user_login(identity, password):
    #connect to dv
    con = sqlite3.connect('Blog.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE email=? OR username=?", (identity, identity))
    user = cur.fetchone()
    if user and user[3] == password:
        print("welcome ", user[2])
        session['username_or_email'] = identity
        con.close()
        return True
    else:
        print("wrong input")
        return False
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
    return render_template("register.html")
def register_user():
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    confirm_password = request.form['confirm-password']
    con = sqlite3.connect('Blog.db')
    cur = con.cursor()
    if password == confirm_password:
        cur.execute("INSERT INTO users (email, username, password) VALUES (?, ?, ?)"
                    , (email, username, password) )
        con.commit()
        con.close()
        return redirect(url_for('home'))
    else:
        print("Password did not match")

def bleaching():
    print("function to bleach")

def has_password():
    print("Hashing")




if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    # app.config['SESSION_COOKIE_HTTPONLY'] = False #will allow us to get session cookies if we want
    # to create a script for it
    app.run(host='0.0.0.0', port=5000)
