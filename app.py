from flask import Flask, render_template, url_for, request, redirect,session
from flask import Blueprint
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.orm import relationship
import os
import re
from sqlalchemy.sql.schema import ForeignKey
from werkzeug.utils import secure_filename

import random
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
    name = db.Column(db.String(200), nullable=False)
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
        for i in range(5):
            rand = random.randrange(0, db.session.query(Listing).count()) 
            b = Listing.query.get(rand)
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
        count = 0

        to_check =db.session.query(Listing.tag).distinct()

        while True:
            rand = random.randrange(0, to_check.count())            
            m_tag = re.sub(r'[^A-Za-z0-9 ]+', '', to_check[rand][0])   
            if len(m_tag) > 0:
                bs = db.session.query(Listing).distinct(Listing.tag).filter(Listing.tag == m_tag)
                if bs.count() >= 5:
                    l = []
                    for j in bs:
                        l.append(Listing.query.get(j.id))
                    toRet[m_tag] = l
                    count += 1
            if count >= 5:
                break

        x = sorted(toRet.keys(), key=lambda k: len(toRet[k]), reverse=True)
        
        print( "==========================================================================================")
        print(x)

        tr = {}

        for i in x:
            tr[i] = toRet[i]

        return tr

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


        if likes[0] == "liked":
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
                l = Listing.get_recommendations()
                return render_template('home.html', logged_user=logged_user, listing=l)
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
    
@app.route('/contact')
def social():
    user=None
    logged_user=None
    if "username" in session:
        user = session["username"]
        if user != None:
            logged_user=Users.query.get(user)
    return render_template("social.html", logged_user=logged_user)
    
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
        book_count = 0
        db.session.flush()
        books = open("books.txt", "r")
        driver = webdriver.Chrome()
        all_books=[]
        for name in books.readlines():
            try:
                print("\n\n\nadding: " + name)
                attempt = 0
                driver.get("http://duckduckgo.com")
                inputElement = driver.find_element_by_name("q")
                inputElement.send_keys(name + " site:librarything.com\n")
                print("click")
                results = driver.find_elements_by_xpath("//div[@id='links']/div/div/h2/a[@class='result__a']")
                lenbook = len(results[0].get_attribute("href").split('/'))
                book_link = results[0].get_attribute("href").rsplit("/", lenbook - 5)[0]
                driver.get(book_link)
                while attempt < 2:
                    try:
                        print("grabbing the description")
                        description = driver.find_element_by_class_name("wslsummary").text
                        print("grabbing the title and author")
                        title_des = driver.find_element_by_class_name("headsummary").text
                        print("grabbing the tags")
                        tag_des = driver.find_elements_by_xpath('//span[@class="tag"]')
                        print("is the problem here?")
                        largest = 0
                        tags = ""
                        for i in tag_des:
                            t = int(re.findall(r'\d+', i.value_of_css_property("font-size"))[0])
                            if t > largest:
                                tags = i.text
                                largest = t

                        title = re.findall(r"(?P<name>[A-Za-z\t' -:.]+)", title_des)
                        print("grabbing the date")
                        date = driver.find_element_by_xpath('//td[@fieldname="originalpublicationdate"]').text
                        print("saving an image")
                        with open('static/images/Books/' + title[0] + '.png', "wb") as file:
                                file.write(driver.find_element_by_xpath('//div[@id="maincover"]/img').screenshot_as_png)       
                        attempt = 99                  
                    except:
                        print("Something went wrong trying again | attempt #" + str(attempt))
                        attempt += 1
                        
                print("getting the external link")
                driver.get("http://duckduckgo.com")
                inputElement = driver.find_element_by_name("q")
                inputElement.send_keys(title[0] + " site:amazon.in\n")
                
                attempt = 0
                while attempt < 2:
                    try:
                        results = driver.find_elements_by_xpath("//div[@id='links']/div/div/h2/a[@class='result__a']")
                        link = results[0].get_attribute("href")
                        attempt = 99
                    except:
                        print("Something went wrong with the link somehow")
                        attempt += 1

                print("creating the book")
                l = Listing(name = title[0], summary = description, date_published = date, author = title[1][3: len(title[1])], is_author=False, tag=tags, external_link = link)


                flag = False

                for i in all_books:
                    if i.name == l.name:
                        flag = True

                if flag == False:
                    all_books.append(l)
                else:
                    print("book was already in the list, ignoring...")
                
                print("adding the book")

            except:
                print("Couldnt get all the data required, moving on")       

            book_count += 1
            if book_count >= 50:
                book_count = 0
                db.session.add_all(all_books)
                db.session.commit()
                all_books.clear()

        if book_count != 0:
            db.session.add_all(all_books)
            db.session.commit()

        print("\n\n\nadded all the books yayyyy!\n\n\n")

        books.close()
        driver.close()

    return redirect('/')


if __name__ == "__main__":
    db.create_all()
    app.run(debug=False)
