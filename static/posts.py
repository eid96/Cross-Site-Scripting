import sqlite3
from datetime import datetime

def create_post_table():
    con = sqlite3.connect('Blog.db')
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS posts (
             id INTEGER PRIMARY KEY,
             title TEXT NOT NULL,
             text TEXT NOT NULL,
             date TEXT NOT NULL
         )''')
    con.commit()
    con.close()

def insert_posts():
    con = sqlite3.connect('Blog.db')
    cur = con.cursor()

    cur.execute("SELECT COUNT(*) FROM posts")
    data = cur.fetchone()[0]

    if data == 0:
        posts = [
            ('First Post', 'This is the text for the first post.', datetime.now()),
            ('Second Post', 'This is the text for the second post.', datetime.now()),
            ('Third Post', 'test', datetime.now())
        ]

        for post in posts:
            cur.execute("INSERT INTO posts (title, text, date) VALUES (?, ?, ?)", post)

        con.commit()
    con.close()

def get_all_posts():
    con = sqlite3.connect("Blog.db")
    curs = con.cursor()
    curs.execute("SELECT id, title FROM posts ORDER BY date DESC")
    data = curs.fetchall()
    con.close()
    return data

def get_post_by_id(post_id):
    con = sqlite3.connect("Blog.db")
    curs = con.cursor()
    curs.execute("SELECT * FROM posts WHERE id=?", (post_id,))
    data = curs.fetchone()
    con.close()
    return data
