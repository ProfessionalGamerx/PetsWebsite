# Move imports to the top
from flask import Blueprint, render_template, abort
from flask import current_app as app
from flask import g
import sqlite3

routes = Blueprint('routes', __name__)
# Define Blueprint before any route decorators
routes = Blueprint('routes', __name__)

# Route for item details page (now includes table name)
@routes.route('/item/<table>/<int:item_id>')
def item_detail(table, item_id):
    if table not in ['Dogs', 'Cats', 'OtherPets']:
        abort(404)
    db = get_db()
    cur = db.execute(f'SELECT * FROM {table} WHERE id = ?', (item_id,))
    item = cur.fetchone()
    cur.close()
    if item is None:
        abort(404)
    return render_template('item_detail.html', item=item)

# Helper to get DB connection (reuse from app.py if possible)
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('Backpack.db')
        db.row_factory = sqlite3.Row
    return db



# Route for cats page
@routes.route('/cats')
def cats():
    db = get_db()
    try:
        cur = db.execute('SELECT * FROM Cats')
        results = cur.fetchall()
        cur.close()
    except sqlite3.OperationalError:
        results = []
    return render_template('cats.html', results=results)

# Route for dogs page
@routes.route('/dogs')
def dogs():
    db = get_db()
    try:
        cur = db.execute('SELECT * FROM Dogs')
        results = cur.fetchall()
        cur.close()
    except sqlite3.OperationalError:
        results = []
    return render_template('dogs.html', results=results)

# Route for other pets page
@routes.route('/other_pets')
def other_pets():
    db = get_db()
    try:
        cur = db.execute('SELECT * FROM OtherPets')
        results = cur.fetchall()
        cur.close()
    except sqlite3.OperationalError:
        results = []
    return render_template('other_pets.html', results=results)