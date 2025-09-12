# Move imports to the top
from flask import Blueprint, render_template, abort, request, jsonify
from flask import current_app as app
from flask import g
import sqlite3

routes = Blueprint('routes', __name__)

# Route to find pet by name and return its table and id
@routes.route('/find_pet')
def find_pet():
    name = request.args.get('name')
    if not name:
        return jsonify({}), 404
    db = get_db()
    for table in ['Dogs', 'Cats', 'Other']:
        cur = db.execute(f'SELECT id FROM {table} WHERE LOWER(name) = ?', (name.lower(),))
        row = cur.fetchone()
        cur.close()
        if row:
            return jsonify({'table': table, 'id': row['id']})
    return jsonify({}), 404

# Route for item details page
@routes.route('/item/<table>/<int:item_id>')
def item_detail(table, item_id):
    if table not in ['Dogs', 'Cats', 'Other']:
        abort(404)
    db = get_db()
    cur = db.execute(f'SELECT * FROM {table} WHERE id = ?', (item_id,))
    item = cur.fetchone()
    cur.close()
    if item is None:
        abort(404)
    return render_template('item_detail.html', item=item)

# Helper to get database connection im gay
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
        cur = db.execute('SELECT * FROM Other')
        results = cur.fetchall()
        cur.close()
    except sqlite3.OperationalError:
        results = []
    return render_template('other_pets.html', results=results)


# Route for all pets by breeder price
@routes.route('/breeder_price')
def breeder_price():
    db = get_db()
    pets = []
    for table, pet_type in [('Dogs', 'Dog'), ('Cats', 'Cat'), ('Other', 'Other')]:
        try:
            cur = db.execute(f'SELECT *, "{pet_type}" as type FROM {table}')
            pets += cur.fetchall()
            cur.close()
        except sqlite3.OperationalError:
            continue
    pets = [pet for pet in pets if pet['breeder_price'] is not None]
    pets.sort(key=lambda x: float(x['breeder_price']) if x['breeder_price'] else float('inf'))
    return render_template('breeder_price.html', pets=pets)


# Route for all pets by adoption price
@routes.route('/adoption_price')
def adoption_price():
    db = get_db()
    pets = []
    for table, pet_type in [('Dogs', 'Dog'), ('Cats', 'Cat'), ('Other', 'Other')]:
        try:
            cur = db.execute(f'SELECT *, "{pet_type}" as type FROM {table}')
            pets += cur.fetchall()
            cur.close()
        except sqlite3.OperationalError:
            continue
    pets = [pet for pet in pets if pet['adoption_price'] is not None]
    pets.sort(key=lambda x: float(x['adoption_price']) if x['adoption_price'] else float('inf'))
    return render_template('adoption_price.html', pets=pets)