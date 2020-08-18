from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

import os

app = Flask(__name__)

IMAGE_FOLDER = os.path.join('static', 'images')
app.config['IMAGE_FOLDER'] = IMAGE_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
#db.create_all()

class reg(db.Model):
    email = db.Column(db.String(200), primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)


def convert_to_int(value):
        try:
                return int(value)
        except:
                return -1

class Listing(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(200), nullable=False)
        summary = db.Column(db.String(256), nullable=True)
        author = db.Column(db.String(256), nullable=True)
        likes = db.Column(db.Integer, nullable = False)
        date_published= db.Column(db.DateTime)
        related = db.Column(db.String(256), nullable=True)
        tags = db.Column(db.String(512), nullable=True)
        is_author = db.Column(db.Integer, nullable = False)

        def get_author(self):
                self.author = self.author.strip()
                int_list = self.author.split(' ')
                toCheck = []
                for i in range(len(int_list)):
                        toCheck.append(convert_to_int(int_list[i]))
                toRet=[]
                for i in toCheck:
                        toRet.append(Listing.query.get(i))
                return toRet

        def get_related(self):
                self.related = self.related.strip()
                int_list = self.related.split(' ')
                toCheck = []
                for i in range(len(int_list)):
                        toCheck.append(convert_to_int(int_list[i]))
                toRet=[]
                for i in toCheck:
                        toRet.append(Listing.query.get(i))
                return toRet

        def __repr__(self):
                return '<Listing %r>' % self.id


@app.route('/information/<int:id>', methods=['POST', 'GET'])
def index(id):
        l = Listing.query.get(id)
        return render_template("information.html", listing=l)


@app.route('/register',methods=['POST', 'GET'])
def about():
        if request.method == 'POST':
                username = request.form['username']
                email = request.form['email']
                password = request.form['password']
                new_username = reg(username=username,email=email,password=password)
                
                try:
                        db.session.add(new_username)                
                        db.session.commit()
                        return redirect('/login')
                except:
                        return 'There was an issue adding your task'

        else:
                new_username = reg.query.order_by(reg.username).first();   
                return render_template('register.html',new_username=new_username)
        

@app.route('/home')
def home():
        book = Listing(id=0, name="The Conquest of Bread",summary="Fluffy boi", author="1", likes=1, date_published=datetime.now().date(),related="2 3", tags="", is_author=False)
        book1 = Listing(id=2, name="Antifa The Antifascist Handbook",summary="How to get access to George Soros' bank account", author="1", likes=1, date_published=datetime.now().date(),related="1 2", tags="", is_author=False)
        book2 = Listing(id=3, name="Das Kapital",summary="The more lesbians in a videogame the more Marxist it is", author="1", likes=1, date_published=datetime.now().date(),related="0 1 2 3", tags="", is_author=False)
        kropotkin = Listing(id=1, name="Peter Kropotkin",summary="Leftist Santa", author="0 ", likes=69, date_published=datetime.now().date(),related="", tags="", is_author=True)
        
        try:
                db.session.add(book)
                db.session.add(book1)
                db.session.add(book2)
                db.session.add(kropotkin)
                db.session.commit()
                return redirect("information/0")
        except:
                return "SOMETHING WENT WRONG, PLEASE TRY AGAIN"


@app.route('/login',methods=['POST', 'GET'])
def login():
        if request.method == 'POST':
                new_username = request.form['username']
                new_password = request.form['password']
                
                user = bool(reg.query.filter_by(username=new_username,password=new_password).first())
                if user == True:
                        return redirect('/information')
                else:
                        return "user id and password is incorrect"
        else:
                return render_template("login.html")
        

if __name__ == "__main__":
        db.create_all()
        app.run(debug=True)
        
