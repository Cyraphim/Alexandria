from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

import os

app = Flask(__name__)

IMAGE_FOLDER = os.path.join('static', 'images')
app.config['IMAGE_FOLDER'] = IMAGE_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Book(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(200), nullable=False)
        summary = db.Column(db.String(256), nullable=True)
        coversrc = db.Column(db.String(256))

        def __repr__(self):
                return '<Task %r>' % self.id

class Author(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(200), nullable=False)
        summary = db.Column(db.String(256), nullable=True)
        coversrc = db.Column(db.String(256))

        def __repr__(self):
                return '<Task %r>' % self.id

class TempBook:
        id = 0
        name = "The Conquest of Bread"
        summary = "TCOB is an 1892 book by the Russian Anarcho Communist Peter Kropotkin, Originally written in French...\n READ MORE >>"
        coversrc = os.path.join(app.config['IMAGE_FOLDER'], name + '.png')

@app.route('/information', methods=['POST', 'GET'])
def index():
        book = TempBook();
        return render_template("information.html", book=book)


@app.route('/register')
def about():
    return render_template('register.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    return render_template("to.html")

if __name__ == "__main__":
    app.run(debug=True)


if __name__ == "__main__":
        app.run(debug=True)