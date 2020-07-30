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

class Author():
        name = "Peter Kropotkin"

class TB2:
        id = 1
        name = "Das Kapital"
        summary = "Das Kapital, also called Capital. A Critique of Political Economy, is a foundational theoretical text in materialist philosophy, economics and politics by Karl Marx."
        coversrc = os.path.join(app.config['IMAGE_FOLDER'], name + '.png')

class TB3:
        id = 3
        name = "Antifa The Antifascist Handbook"
        summary = "Antifa: The Anti-Fascist Handbook is a 2017 book by historian Mark Bray, which explores the history of anti-fascist movements since the 1920s and 1930s and their contemporary resurgence."
        coversrc = os.path.join(app.config['IMAGE_FOLDER'], name + '.png')

class TB1:
        id = 0
        likes = "100%"
        name = "The Conquest of Bread"
        summary = "The Conquest of Bread is an 1892 book by the Russian anarcho-communist Peter Kropotkin. Originally written in French, it first appeared as a series of articles in the anarchist journal Le Révolté. It was first published in Paris with a preface by Élisée Reclus, who also suggested the title."
        coversrc = os.path.join(app.config['IMAGE_FOLDER'], name + '.png')
        trivia=["I am a human", "Shahi paneer is tasty", "water is wet", "oh wait I was supposed to write about the book", "oh shit oh fu-"]
        author=[Author()]
        date=datetime.now().date()
        related = [TB2(), TB3()]


@app.route('/information', methods=['POST', 'GET'])
def index():
        book = TB1()
        return render_template("information.html", listing=book)


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