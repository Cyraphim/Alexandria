from flask import Flask, render_template, url_for, request, redirect,session
from flask import Blueprint
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.orm import relationship
import os
from sqlalchemy.sql.schema import ForeignKey


app = Flask(__name__)
app.secret_key = 'Hello'

IMAGE_FOLDER = os.path.join('static', 'images')
app.config['IMAGE_FOLDER'] = IMAGE_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
# db.create_all()


class reg(db.Model):
    
    email = db.Column(db.String(200),nullable=False)
    username = db.Column(db.String(100), unique=True,primary_key=True)
    password = db.Column(db.String(100), nullable=False)
    
    #comments = relationship("Comment")
    #comments = relationship("Comment", back_populates="regs")


def convert_to_int(value):
    try:
        return int(value)
    except:
        return -1


class Comment(db.Model):

    _tablename_ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), ForeignKey("reg.username"),nullable=False)
    #username = db.Column(db.String(100), nullable=False)
    comment = db.Column(db.String(200), nullable=False)
    #regs = relationship("reg", back_populates="comments")
    regs = relationship("reg", foreign_keys="Comment.username")
    db.listing = db.Column(db.Integer,ForeignKey("Listing.id"))
    db.listt = db.relationship("Listing", foreign_keys="Listing.id")


class Listing(db.Model):
   # _tablename_ = 'listts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    summary = db.Column(db.String(256), nullable=True)
    author = db.Column(db.String(256), nullable=True)
    likes = db.Column(db.Integer, nullable=False)
    date_published = db.Column(db.DateTime)
    related = db.Column(db.String(256), nullable=True)
    tags = db.Column(db.String(512), nullable=True)
    is_author = db.Column(db.Integer, nullable=False)

    comment = db.Column(db.String(200), nullable=True)

    

    def get_author(self):
        self.author = self.author.strip()
        int_list = self.author.split(' ')
        toCheck = []
        for i in range(len(int_list)):
            toCheck.append(convert_to_int(int_list[i]))
        toRet = []
        for i in toCheck:
            toRet.append(Listing.query.get(i))
        return toRet

    def get_related(self):
        self.related = self.related.strip()
        int_list = self.related.split(' ')
        toCheck = []
        for i in range(len(int_list)):
            toCheck.append(convert_to_int(int_list[i]))
        toRet = []
        for i in toCheck:
            toRet.append(Listing.query.get(i))
        return toRet

    def __repr__(self):
        return '<Listing %r>' % self.id


@app.route('/information/<int:id>', methods=['POST', 'GET'])

def index(id):
    
    l = Listing.query.get(id)
    c = Comment.query.get(id)
    user = None
    if "username" in session:
        user = session['username']
        
        
    return render_template("information.html", listing=l,user = user)
    
        
#    def main_route():
#     if current_user.is_authenticated:
#          return render_template("information.html")
#     else:
#          return render_template("login.html")



@app.route('/register', methods=['POST', 'GET'])
def about():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user = reg.query.filter_by(email=email).first() 
        new_username = reg(username=username, email=email, password=password)

        try:
            db.session.add(new_username)
            db.session.commit()
            return redirect('/login')
        except:
            return 'There was an issue adding your task'

    else:
        new_username = reg.query.order_by(reg.username).first()
        return render_template('register.html', new_username=new_username)


@app.route('/home')
def home():
    book = Listing(id=0, name="The Conquest of Bread", summary="Fluffy boi", author="1", likes=1,
                   date_published=datetime.now().date(), related="2 3", tags="", is_author=False, comment="1")
    book1 = Listing(id=2, name="Antifa The Antifascist Handbook", summary="How to get access to George Soros' bank account",
                    author="1", likes=1, date_published=datetime.now().date(), related="1 2", tags="", is_author=False, comment="1")
    book2 = Listing(id=3, name="Das Kapital", summary="The more lesbians in a videogame the more Marxist it is", author="1",
                    likes=1, date_published=datetime.now().date(), related="0 1 2 3", tags="", is_author=False, comment="1")
    kropotkin = Listing(id=1, name="Peter Kropotkin", summary="Leftist Santa", author="0 ", likes=69,
                        date_published=datetime.now().date(), related="", tags="", is_author=True, comment="")

    comm = Comment(id=0, username="Abhinav", comment="giggity")

    try:
        db.session.add(book)
        db.session.add(book1)
        db.session.add(book2)
        db.session.add(kropotkin)
        db.session.add(comm)
        db.session.commit()
        return redirect("information/0")
    except:
        return "SOMETHING WENT WRONG, PLEASE TRY AGAIN"


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        new_username = request.form['username']
        new_password = request.form['password']

        user =  (reg.query.filter_by(
            username=new_username, password=new_password).first())
        session["username"] = user.username

        return redirect("/information/1")
    else:
        return render_template("login.html")
@app.route('/test')
def test():
    return render_template("test.html")
    
@app.route('/')

def search():
    return render_template("search.html")

if __name__ == "__main__":
    
    app.run(debug=True)
