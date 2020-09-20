from flask import Flask, render_template, url_for, request, redirect,session
from flask import Blueprint
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.orm import relationship
import os
import re
from sqlalchemy.sql.schema import ForeignKey
from werkzeug.utils import secure_filename

from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
import re
import shutil

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

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

db = SQLAlchemy(app)
# db.create_all()

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    dislikes = db.Column(db.Integer, nullable=False, default=0)
    date_published = db.Column(db.String(20))
    author = db.Column(db.String(256), nullable=True)
    is_author = db.Column(db.Integer, nullable=False)    
    comments = db.relationship('Comment', backref='listing', lazy='dynamic')
    __searchable__ = ['name']
    tag= db.Column(db.String(256), nullable=False, default="temp")
    external_link=db.Column(db.String(256), nullable=False, default="")

    def get_ratings(self):
        try:
            return int((self.likes / (self.likes + self.dislikes)) * 5)
        except:
            return 0

    def get_author_count(self):
        return  db.session.query(Listing.id).distinct().filter(Listing.is_author==True).count()

    def get_author_id(self):
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
            book =re.sub(r'[^A-Za-z0-9 ]+', '', book[0])
            if len(book) > 0:
                if book not in toRet:
                    bs = db.session.query(Listing.id).distinct().filter(Listing.tag == book)
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
    liked = db.Column(db.Integer, nullable=False, default=1)
    def get_user(self):
        toRet = Users.query.get(self.username)
        return toRet
        

@app.route('/information/<int:id>', methods=['POST', 'GET'])
def information(id):  
    user = None
    logged_user = None
    if "username" in session:
        user = session['username']   
    if user != None:
        logged_user = Users.query.get(user)   
    review_error=""

    if request.method == "POST":
        review = request.form['review']
        user = session['username'] 
        likes = request.form.getlist('likes')

        l = Listing.query.get(id)
        
        review_error=""
        error_check = False

        if len(likes) <= 0:
            review_error="Please tell us whether you recommend it or not before submitting!"
            error_check = True

        if len(review) <= 0:
            review_error="Please tell us your thoughts in the review box before submitting!"
            error_check = True
        
        if user == None or l == None:
            return redirect("/logout")

        if error_check:
            return render_template("information.html", listing=l, logged_user=logged_user,  review_error=review_error)


        if likes == "liked":
            l.likes +=1
            liked = 1
        else:
            l.dislikes +=1
            liked = 0

        c = Comment(comment=review, username=user, listing_id=id, liked=liked)
        db.session.add(c)
        db.session.commit()
        return redirect(request.url)
    else:
        l = Listing.query.get(id)
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


        shutil.copy("static/images/user_images/default.png", "static/images/user_images/" + username + ".png")
            
        try:            
            db.session.add(new_username)
            db.session.commit()
            session["username"] = new_username.username
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
    
    return render_template("results.html", res=posts, query=name,logged_user=logged_user)

@app.route('/user', methods=['POST', 'GET'])
def userpage():  
    user=None
    logged_user=None
    if "username" in session:
        user = session["username"]
        if user != None:
            logged_user=Users.query.get(user)
            if logged_user != None:
                    email_error = ""
                    user_error = ""
                    if request.method == "POST":
                        file = request.files['image']
                        if file and allowed_file(file.filename):
                            filename = secure_filename(file.filename)
                            file.save(os.path.join(app.config['IMAGE_FOLDER'] + "/user_images/", logged_user.username + ".png"))
                                        
                    return render_template("Profile.html", logged_user=logged_user)

    return redirect("/")
        
@app.route('/fill')
def fill():
    if app.debug:
        driver = webdriver.Chrome()
        books = open("books.txt", "r")
        for name in books.readlines():
            try:
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
                db.session.commit()


                print(link)
                print(title[0])
                print(title[1][3:len(title[1])])
                print(date)
                print(tags)
                print(description)
            except:
                print("unable to add" + name)
            
        books.close()
        driver.close()

    return redirect('/')


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)