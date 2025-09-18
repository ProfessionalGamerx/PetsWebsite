import sqlite3
from flask import (
    Flask, render_template, g, request, redirect, url_for, session, flash
)
from flask_bcrypt import Bcrypt
from routes import routes

app = Flask(__name__)
# Secret key for session management,
# for future me all this does basically is it keeps the users login info safe
# and secure. Flask uses it to encrypt session data and protect against
# certain attacks like CSRF but mainly it's required for user sessions to work.
# I've generated a random string of 100 characters to use as the secret key.
app.secret_key = (
    'dNaA4BYy._VemwghLk]!LN)UAP7nGFaz0xkWn6_yi7^sp6%*pX=Mppau2EMwZX_*Pc'
    'PP^tZ,Lc8H7LH!LvZnhpf!_>d#39puijt'
)
bcrypt = Bcrypt(app)
# Path to the SQLite database file
DATABASE = 'Backpack.db'


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


# Logout route
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out.')
    return redirect(url_for('home'))


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


# Register route using Flask-Bcrypt
@app.route('/register', methods=['GET', 'POST'])
def register():
    # sign up stuff for registering a new user
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
        # Hash password with bcrypt and store in database
        hashed = bcrypt.generate_password_hash(password).decode('utf-8')
        db.execute(
            'INSERT INTO Users (username, password) VALUES (?, ?)',
            (username, hashed)
        )
        db.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')


app.register_blueprint(routes)


# Close the database connection at the end of the request
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# Get a database connection for the current app context
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


# Helper function to query the database
# query: SQL query string
# args: parameters for the query
# one: if True, return one result; else, return all
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


# Favorite/Unfavorite Pet
# (Flake8 compliance makes this look much more complicated)
# (The stupid "line too long" thing is really annoying)

# Refers to the pet type (Dogs, Cats, Other) and pet ID.
# For example, if the pet type is "Dog" and the pet ID is 5,
# it inserts the dog with ID 5 from the Dogs table into the favorites table
# And the session['user_id'] is the ID of the logged in user
# So it links the pet to the account of the user in the Favorites table
@app.route('/favorite/<pet_type>/<int:pet_id>', methods=['POST'])
def favorite_pet(pet_type, pet_id):
    if 'user_id' not in session:
        flash('You must be logged in to do that.')
        return redirect(url_for('login'))
    db = get_db()
    user_id = session['user_id']
    exists = db.execute(
        'SELECT 1 FROM Favorites WHERE user_id = ? '
        'AND pet_id = ? AND pet_type = ?',
        (user_id, pet_id, pet_type)
    ).fetchone()
    if not exists:
        # If not already in favorites, add it
        db.execute(
            'INSERT INTO Favorites (user_id, pet_id, pet_type) '
            'VALUES (?, ?, ?)',
            (user_id, pet_id, pet_type)
        )
        db.commit()
        flash('Added to favorites!')
    else:
        # If already in favorites, just flash a message
        flash('Already in favorites.')
    return redirect(request.referrer or url_for('home'))


@app.route('/unfavorite/<pet_type>/<int:pet_id>', methods=['POST'])
def unfavorite_pet(pet_type, pet_id):
    if 'user_id' not in session:
        flash('You must be logged in to do that.')
        return redirect(url_for('login'))
    db = get_db()
    user_id = session['user_id']
    db.execute(
        'DELETE FROM Favorites WHERE user_id = ? '
        'AND pet_id = ? AND pet_type = ?',
        (user_id, pet_id, pet_type)
    )
    db.commit()
    flash('Removed from favorites.')
    return redirect(request.referrer or url_for('home'))


# View Favorites
@app.route('/favorites')
def favorites():
    if 'user_id' not in session:
        flash('You must be logged in to do that.')
        return redirect(url_for('login'))
    db = get_db()
    user_id = session['user_id']
    favs = db.execute(
        'SELECT pet_id, pet_type FROM Favorites WHERE user_id = ?', (user_id,)
    ).fetchall()
    pets = []
    # For each favorite, get the pet details from the appropriate table
    for fav in favs:
        table = None
        if fav['pet_type'] == 'Dog':
            table = 'Dogs'
        elif fav['pet_type'] == 'Cat':
            table = 'Cats'
        elif fav['pet_type'] == 'Other':
            table = 'Other'
        if table:
            pet = db.execute(
                f'SELECT * FROM {table} WHERE id = ?',
                (fav['pet_id'],)
            ).fetchone()
            # Only add if the pet still exists
            if pet:
                pets.append({'type': fav['pet_type'], 'data': pet})
    return render_template('favorites.html', pets=pets)


# Run the Flask app in debug mode if this file is executed directly

if __name__ == '__main__':
    app.run(debug=True)
