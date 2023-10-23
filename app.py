from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from sqlite3 import Error

app = Flask(__name__)

# A simple dictionary that stores username and password
users = {'john': 'doe'}


def create_db():
    con = sqlite3.connect("Stock.db")
    curs = con.cursor()
    curs.execute("DELETE FROM stocks")
    # Create a table
    curs.execute('''CREATE TABLE IF NOT EXISTS stocks
                   (Brand text, Product text, quantity real, price real)''')

    curs.execute("INSERT INTO stocks VALUES ('Brand1', 'ProductA', 100, 25.5)")
    curs.execute("INSERT INTO stocks VALUES ('Brand2', 'ProductB', 150, 30.2)")
    curs.execute("INSERT INTO stocks VALUES ('Brand3', 'ProductC', 200, 20.0)")
    curs.execute("INSERT INTO stocks VALUES ('Brand4', 'ProductD', 75, 15.6)")
    curs.execute("INSERT INTO stocks VALUES ('Brand5', 'ProductE', 120, 18.8)")
    curs.execute("INSERT INTO stocks VALUES ('Brand6', 'ProductF', 180, 22.1)")
    curs.execute("INSERT INTO stocks VALUES ('Brand7', 'ProductG', 90, 26.4)")
    curs.execute("INSERT INTO stocks VALUES ('Brand8', 'ProductH', 110, 27.9)")
    curs.execute("INSERT INTO stocks VALUES ('Brand9', 'ProductI', 130, 19.5)")
    curs.execute("INSERT INTO stocks VALUES ('Brand10', 'ProductJ', 160, 32.0)")

    # Commit the changes
    con.commit()

    # Save (commit) the changes
    con.commit()
    con.close()


# Home route
# @app.route('/Shop')
# def create_shop_html():


@app.route('/home')
def home():
    # create_shop_html()
    create_db()
    return render_template('home.html')


# Sign in route
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # userInput = "<script>alert('xss attack!!') </script>"
        # document.getElementById('username').value = userInput;
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
    return render_template('dashboard.html')


@app.route('/Store', methods=['GET', 'POST'])
def Store():
    return render_template('Store.html')


if __name__ == '__main__':
    app.run(debug=True)
