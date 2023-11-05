from flask import Flask, render_template, request
import sqlite3
from datetime import datetime

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
    return render_template('home.html', data=data)

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


@app.route('/add_posts', methods=['GET', 'POST'])
def add_posts():
    # render html page "add_posts"
    return render_template('add_posts.html')


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
    title = request.form['title']  # Vulnerability here, as it's not sanitized
    text = request.form['text']  # Vulnerability here, as it's not sanitized
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
    return render_template('add_posts.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
