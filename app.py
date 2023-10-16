from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# A simple dictionary that stores username and password
users = {'john': 'doe'}


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
    return render_template('dashboard.html')


if __name__ == '__main__':
    app.run(debug=True)
