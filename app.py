from flask import Flask, render_template, url_for, request, redirect,session
from flask import Blueprint
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.orm import relationship
import os
from sqlalchemy.sql.schema import ForeignKey
from flask_msearch import Search


app = Flask(__name__)
app.secret_key = 'Hello'

#search = Search()
#search.init_app(app)

IMAGE_FOLDER = os.path.join('static', 'images')

app.config['IMAGE_FOLDER'] = IMAGE_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
# db.create_all()



class Users(db.Model):
    _tablename_ = "Users"
    email = db.Column(db.String(200),nullable=False)
    username = db.Column(db.String(50), unique=True,primary_key=True)
    password = db.Column(db.String(100), nullable=False)
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

class Listing(db.Model):
    _tablename_ = "Listing"
   
    id = db.Column(db.Integer, primary_key=True, autoincrement=True) 
    name = db.Column(db.String(200), nullable=False, unique=True)
    summary = db.Column(db.String(256), nullable=True)
    likes = db.Column(db.Integer, nullable=False, default=0)
    date_published = db.Column(db.DateTime, default=datetime.now)
    is_author = db.Column(db.Integer, nullable=False)    
    comments = db.relationship('Comment', backref='listing', lazy='dynamic')
    __searchable__ = ['name']

    def get_author_count(self):
        return  db.session.query(Listing.id).distinct().filter(Listing.is_author==True).count()

    def get_author(self):
        toRet=[]
        for book in db.session.query(Listing.id).distinct().filter(Listing.is_author==True):
            b = Listing.query.get(book.id)
            toRet.append(b)
        return toRet

    def get_related_count(self):
        return  db.session.query(Listing.id).distinct().filter(Listing.is_author==False).count()

    def get_related(self):
        toRet=[]
        for book in db.session.query(Listing.id).distinct().filter(Listing.is_author==False):
            b = Listing.query.get(book.id)
            toRet.append(b)
        return toRet

    def get_comment_count(self):
        return  db.session.query(Comment.id).filter_by(listing_id = self.id).count()

    def get_comments(self):
        toRet = []
        for comm in db.session.query(Comment.id).filter_by(listing_id = self.id):
            c = Comment.query.get(comm.id)
            toRet.append(c)
        return toRet

    def __repr__(self):
        return '<Listing %r>' % self.id

class Comment(db.Model):
    _tablename_ = "Comment"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    comment = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(50), db.ForeignKey(Users.username))
    listing_id = db.Column(db.Integer,db.ForeignKey(Listing.id))

@app.route('/information/<int:id>', methods=['POST', 'GET'])
def information(id):  
    if request.method == "POST":
        review = request.form['review']
        user = session['username'] 
        c = Comment(comment=review, username=user, listing_id=id)
        db.session.add(c)
        db.session.commit()
        return redirect(request.url)
    else:
        l = Listing.query.get(id)
        user = None
        logged_user = None
        if "username" in session:
            user = session['username']   
        if user != None:
            logged_user = Users.query.get(user)      
        return render_template("information.html", listing=l, logged_user=logged_user)
    
@app.route('/register', methods=['POST', 'GET'])
def about():
    if request.method == 'POST':
        username = request.form['username'].lower()
        email = request.form['email'].lower()
        password = request.form['password']
        user = Users.query.filter_by(email=email).first() 
        new_username = Users(username=username, email=email, password=password)

        try:
            db.session.add(new_username)
            db.session.commit()
            return redirect('/login')
        except:
            return 'The actual username and password was : ' + u.username + " | " + u.password

    else:
        new_username = Users.query.order_by(Users.username).first()
        return render_template('register.html', new_username=new_username, logged_user=None)


@app.route('/home')
def home():
    book = Listing(name="The Conquest of Bread", summary="Fluffy boi", is_author=False)
    book1 = Listing(name="Antifa The Antifascist Handbook", summary="How to get access to George Soros' bank account",  is_author=False)
    book2 = Listing(name="Das Kapital", summary="The more lesbians in a videogame the more Marxist it is", is_author=False)
    kropotkin = Listing(name="Peter Kropotkin", summary="Leftist Santa", is_author=True)

    try:
        db.session.add(book)
        db.session.add(book1)
        db.session.add(book2)
        db.session.add(kropotkin)
        db.session.commit()
        return redirect("/register")
    except:
        return "SOMETHING WENT WRONG, PLEASE TRY AGAIN"


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        new_username = request.form['username'].lower()
        new_password = request.form['password'].lower()

        user =  (Users.query.filter_by(
            username=new_username, password=new_password).first())
        session["username"] = user.username

        return redirect("/information/1")
    else:
        return render_template("login.html", logged_user=None)

@app.route('/logout')
def test():
    session['username'] = None
    session.pop('username', None)
    return redirect("/information/1")
    
@app.route('/', methods=['POST', 'GET'])
def search():
    return render_template("search.html")
    
@app.route('/results')
def results():  
    
    name = request.form["SearchItem"]
    search = "%{}%".format(name)
        
    posts = Listing.query.filter(Listing.name.like(search)).all()
    if (posts != None):
        str = " "
        for i in posts:
            str += i.name

            

        return " Books " + str

    return render_template("results.html", res=posts, new_username="daserialgenius", logged_user=None)

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
