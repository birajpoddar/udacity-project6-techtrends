import sqlite3
import logging
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import datetime

# Metrics class
class Metrics:
    def __init__(self) -> None:
        self.db_connection_count = 0
        self.post_count = 0

    def increase_connection_count(self):
        self.db_connection_count += 1

    def get_post_count(self):
        connection = get_db_connection()
        num_posts = connection.execute('SELECT count(*) as COUNT FROM posts')\
            .fetchone()['COUNT']
        connection.close()
        return num_posts

    def set_post_count(self):
        self.post_count = self.get_post_count()

def getDateTime():
    return datetime.datetime.now().__format__('%d/%h/%Y %H:%M:%S')

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    metrics.increase_connection_count()
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.info(f'[{getDateTime()}] - No Article found!')
      return render_template('404.html'), 404
    else:
      app.logger.info(f'[{getDateTime()}] - Article \'{post["title"]}\' retrieved!')
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info(f'[{getDateTime()}] - \'About us\' retrieved!')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            app.logger.info(f'[{getDateTime()}] - New Article \'{title}\' created!')
            return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/healthz')
def healthcheck():
    try:
        metrics.set_post_count()
        resp = { "result": "OK - healthy" }
        return Flask.response_class(json.dumps(resp), status=200, mimetype="application/json")
    except:
        resp = { "result": "ERROR - unhealthy" }
        return Flask.response_class(json.dumps(resp), status=500, mimetype="application/json")

@app.route('/metrics')
def metricscheck():
    metrics.set_post_count()
    return Flask.response_class(json.dumps(metrics.__dict__), status=200, mimetype="application/json")

# start the application on port 3111
if __name__ == "__main__":
   # metrics object
   metrics = Metrics()
   
   # Logging
   logging.basicConfig(level=logging.INFO)

   app.run(host='0.0.0.0', port='3111', debug=False)
