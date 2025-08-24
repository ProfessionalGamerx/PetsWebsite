
# Import necessary modules from Flask and sqlite3 for web app and database
from flask import Flask, render_template, g
import sqlite3


# Create the Flask application
app = Flask(__name__)


# Helper function to query the database
# query: SQL query string
# args: parameters for the query
# one: if True, return one result; else, return all
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


# Path to the SQLite database file
DATABASE = 'Backpack.db'


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


############################################################################################################
from routes import routes
app.register_blueprint(routes)

# Route for the home page
@app.route("/", endpoint="home")
def home():
    return render_template("index.html")
###########################################################################################################

# Run the Flask app in debug mode if this file is executed directly
if __name__ == "__main__":
    app.run(debug=True)