from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from sqlite3 import Error

app = Flask(__name__)

# A simple dictionary that stores username and password
users = {'john': 'doe'}

def create_db():
    con = sqlite3.connect("Stock.db")
    curs = con.cursor()
    # Create a table
    curs.execute('''CREATE TABLE IF NOT EXISTS stocks
                   (date text, Brand text, Product text, quantity real, price real)''')

    # Insert data into the table
    curs.execute("INSERT INTO stocks VALUES ('2006-01-05','Brand 1','Product 1',100, 35.14)")

     # Save (commit) the changes
    con.commit()

# Home route
@app.route('/')
def home():
    return render_template('home.html')


# Sign in route
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            return redirect(url_for('dashboard'))
        else:
            return render_template('signin.html', message='Invalid credentials. Please try again.')
    return render_template('signin.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users[username] = password
        return redirect(url_for('signin'))
    return render_template('signup.html')


# Dashboard route
@app.route('/dashboard')

def dashboard():
    create_db()
    return render_template('dashboard.html')
@app.route('/Store')
def Store():
    return render_template('Store.html')

if __name__ == '__main__':
    app.run(debug=True)
