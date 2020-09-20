from flask import Flask, render_template, url_for, request, redirect,session
from flask import Blueprint
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.orm import relationship
import os
import re
from sqlalchemy.sql.schema import ForeignKey

from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
import re

email_regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
# for custom mails use: '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$' 


app = Flask(__name__)
app.secret_key = 'Hello'

#search = Search()
#search.init_app(app)

IMAGE_FOLDER = os.path.join('static', 'images')

app.config['IMAGE_FOLDER'] = IMAGE_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
# db.create_all()



class Users(db.Model):
    _tablename_ = "Users"
    email = db.Column(db.String(200),nullable=False)
    username = db.Column(db.String(50), unique=True,primary_key=True)
    password = db.Column(db.String(100), nullable=False)
    userimage = db.Column(db.String(200), nullable=False, default="default.png")
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

class Listing(db.Model):
    _tablename_ = "Listing"
   
    id = db.Column(db.Integer, primary_key=True, autoincrement=True) 
    name = db.Column(db.String(200), nullable=False, unique=True)
    summary = db.Column(db.String(256), nullable=True)
    likes = db.Column(db.Integer, nullable=False, default=0)
    date_published = db.Column(db.String(20))
    author = db.Column(db.String(256), nullable=True)
    is_author = db.Column(db.Integer, nullable=False)    
    comments = db.relationship('Comment', backref='listing', lazy='dynamic')
    __searchable__ = ['name']
    tag= db.Column(db.String(256), nullable=False, default="temp")
    external_link=db.Column(db.String(256), nullable=False, default="")
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

    
    def get_recommendations():
        toRet={}
        for book in db.session.query(Listing.tag).distinct().filter(Listing.is_author==False):
            if book not in toRet:
                bs = db.session.query(Listing.id).distinct().filter(Listing.is_author==False)
                l = []
                for i in bs:
                    l.append(Listing.query.get(i.id))
                toRet[book] = l
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
    user=None
    logged_user=None
    if "username" in session:
        user = session["username"]
        if user != None:
            logged_user=Users.query.get(user)
            if logged_user != None:
                return redirect("/")

    if request.method == 'POST':
        username = request.form['username'].lower()
        email = request.form['email'].lower()
        password = request.form['password']

        user_check =  (Users.query.filter_by(
            username=username).first())
        if user_check != None:
            return render_template('register.html', logged_user=None, error_message="User with that username already exists")

        new_username = Users(username=username, email=email, password=password)

        if not (re.search(email_regex, email)):  
            return render_template('register.html', logged_user=None, error_message="Invalid Email")

        try:
            db.session.add(new_username)
            db.session.commit()
            return redirect('/login')
        except:
            return render_template('register.html', logged_user=logged_user, error_message="Something went wrong, please try again!")

    else:
        return render_template('register.html', logged_user=logged_user)


@app.route('/')
def home():    
    user=None
    logged_user=None
    if "username" in session:
        user = session["username"]
        if user != None:
            logged_user=Users.query.get(user)
            if logged_user != None:
                return render_template('home.html', logged_user=logged_user, listing=Listing)
    return redirect('/search')

@app.route('/login', methods=['POST', 'GET'])
def login():    
    if request.method == 'POST':
        new_username = request.form['username'].lower()
        new_password = request.form['password']

        user =  (Users.query.filter_by(
            username=new_username, password=new_password).first())
        if user != None:
            session["username"] = user.username
            return redirect("/")
        else:
            return render_template("login.html", logged_user=None, error_message="Incorrect username/password")
    else:
        user=None
        logged_user=None
        if "username" in session:
            user = session["username"]
            if user != None:
                logged_user=Users.query.get(user)
                if logged_user != None:
                    return redirect("/")

        return render_template("login.html", logged_user=logged_user)

@app.route('/logout')
def logout():
    session['username'] = None
    session.pop('username', None)
    return redirect("/")
    
@app.route('/search', methods=['POST', 'GET'])
def search():
    return render_template("search.html")
    
@app.route('/results', methods=['POST', 'GET'])
def results():  
    user=None
    logged_user=None
    if "username" in session:
        user = session["username"]
        if user != None:
            logged_user=Users.query.get(user)

    name = request.form["SearchItem"]
    search = "%{}%".format(name)
        
    posts = Listing.query.filter(Listing.name.like(search)).all()
    
    return render_template("results.html", res=posts, logged_user=logged_user)

@app.route('/user', methods=['POST', 'GET'])
def userpage():  
    user=None
    logged_user=None
    if "username" in session:
        user = session["username"]
        if user != None:
            logged_user=Users.query.get(user)

    name = request.form["SearchItem"]
    search = "%{}%".format(name)
    posts = Listing.query.filter(Listing.name.like(search)).all()
    
    return render_template("results.html", res=posts, logged_user=logged_user)

@app.route('/fill')
def fill():    
        driver = webdriver.Chrome()
        books = open("books.txt", "r")


        for name in books.readlines():
                driver.get("http://google.com")
                inputElement = driver.find_element_by_name("q")
                inputElement.send_keys(name + " site:librarything.com\n")
                driver.find_element_by_tag_name("cite").click()

                description = driver.find_elements_by_class_name("wslsummary")[0].text
                title_des = driver.find_elements_by_class_name("headsummary")[0].text
                tag_des = driver.find_elements_by_class_name("tag")

                largest = 0
                tags = ""
                for i in tag_des:
                        t = int(re.findall(r'\d+', i.value_of_css_property("font-size"))[0])
                        if t > largest:
                                tags = i.text
                                largest = t

                title = re.findall(r"(?P<name>[A-Za-z\t' -:.]+)", title_des)
                date = driver.find_element_by_xpath('//td[@fieldname="originalpublicationdate"]').text
                
                with open('static/images/Books/' + title[0] + '.png', "wb") as file:
                        file.write(driver.find_element_by_xpath('//div[@id="maincover"]/img').screenshot_as_png)

                driver.get("http://google.com")
                inputElement = driver.find_element_by_name("q")
                inputElement.send_keys(name + " site:amazon.in\n")
                driver.find_element_by_tag_name("cite").click()
                link = driver.current_url
  
                l = Listing(name = title[0], summary = description, date_published = date, author = title[1][3: len(title[1])], is_author=False, tag=tags, external_link = link)

                db.session.add(l)


                print(link)
                print(title[0])
                print(title[1][3: len(title[1])])
                print(date)
                print(tags)
                print(description)
        

        books.close()
        driver.close()
        db.session.commit()

        return redirect('/')


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)