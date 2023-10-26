from flask import Flask, render_template, request
import sqlite3
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    create_db()
    insert()
    con = sqlite3.connect("Blog.db")
    curs = con.cursor()
    curs.execute("SELECT id, title FROM posts")
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


# function that adds test post to blog
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

        # Inserting the posts into the table
        for post in posts:
            cur.execute("INSERT INTO posts (title, text, date) VALUES (?, ?, ?)", post)

        con.commit()
    con.close()

@app.route('/add_posts', methods=['GET','POST'])
def add_posts():
    return render_template('add_posts.html')


@app.route('/Posts', methods=['GET', 'POST'])
def all_posts():
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
    title = request.form['title'] # Vulnerability here, as it's not sanitized
    text = request.form['text'] # Vulnerability here, as it's not sanitized
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
    app.run()
