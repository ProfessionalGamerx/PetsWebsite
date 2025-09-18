
import sqlite3
from flask import (
    Flask, render_template, g, request, redirect, url_for, session, flash
)
from flask_bcrypt import Bcrypt
from routes import routes

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
bcrypt = Bcrypt(app)
# Path to the SQLite database file
DATABASE = 'Backpack.db'



# Helper function to query the database
# query: SQL query string
# args: parameters for the query
# one: if True, return one result; else, return all

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


# Get a database connection for the current app context
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


# Close the database connection at the end of the request
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()



app.register_blueprint(routes)


# Register route using Flask-Bcrypt
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute(
            'SELECT * FROM Users WHERE username = ?', (username,)
        ).fetchone()
        if user:
            flash('Username already exists.')
            return redirect(url_for('register'))
        hashed = bcrypt.generate_password_hash(password).decode('utf-8')
        db.execute(
            'INSERT INTO Users (username, password) VALUES (?, ?)',
            (username, hashed)
        )
        db.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')


# Login route using Flask-Bcrypt
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute(
            'SELECT * FROM Users WHERE username = ?', (username,)
        ).fetchone()
        if user and bcrypt.check_password_hash(user['password'], password):
            session['user_id'] = user['ID']
            session['username'] = user['username']
            flash('Logged in successfully!')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html')


# Logout route
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out.')
    return redirect(url_for('home'))


# Route for the home page
@app.route('/', endpoint='home')
def home():
    db = get_db()
    names = []
    for table in ['Dogs', 'Cats', 'Other']:
        cur = db.execute(f'SELECT name FROM {table}')
        names += [row['name'] for row in cur.fetchall()]
        cur.close()
    return render_template('index.html', pet_names=names)


# Run the Flask app in debug mode if this file is executed directly
if __name__ == '__main__':
    app.run(debug=True)
