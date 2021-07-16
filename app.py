import os
import json
from flask import (
    Flask, flash, render_template, 
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import  (
    generate_password_hash, 
    check_password_hash)
from flask_toastr import Toastr
from datetime import datetime

if os.path.exists("env.py"):
    import env
import requests
import babel.numbers
import decimal

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")
app.api_key = os.environ.get("API_KEY")
app.api_version = os.environ.get("API_VERSION")

mongo = PyMongo(app)
toastr = Toastr(app)


api_url_src = "https://api.themoviedb.org/"
endpoint_path = None

toastr = Toastr()
# initialize toastr on the app within create_app()
toastr.init_app(app)


""" list_type: now_playing, popular, top_rated, upcoming
    URL SAMPLE# https://api.themoviedb.org/3/movie/<list_type>?api_key=<api_key>&language=en-US
"""
@app.route("/", methods=['GET', 'POST'])
@app.route("/list_movies/<list_type>/<list_name>", methods=['GET', 'POST'])
def list_movies(list_type="movie", list_name="now_playing"):
    #if len(list_type) == 0:
    #    list_type = "movie/now_playing"
    lists_name = get_list_name(list_name) #Remove Character from List Name
    endpoint_path = f"/{list_type}/{list_name}"
    endpoint_api_key = f"?api_key={app.api_key}"
    endpoint_lang = "&language=en-US"
    img_url_endpoint_size = "https://image.tmdb.org/t/p/w500"
    endpoint = f"{api_url_src}{app.api_version}{endpoint_path}{endpoint_api_key}{endpoint_lang}"
    req = requests.get(endpoint)
    if req.status_code == 200:
        data = req.json()
        results = data['results']
        if len(results) > 0:
            movie_ids = set()
            for result in results:
                img_url = f"{img_url_endpoint_size}{result['poster_path']}"
                result['poster_path'] = img_url
            movies = results
        else:    
            flash("Fail on Loading List", 'error')
    
    watchlist = []
    watched_list = []
    liked_list = []
    favorite_list = []
    my_movies = []
    if session.get('user'):
        if session['user']:
            user_id = get_user_id()
            watchlist = load_watchlist(user_id)
            watched_list = load_watched_list(user_id)
            liked_list = load_liked_list(user_id)
            favorite_list = load_favorite_list(user_id)
            my_movies = load_my_movies(user_id)

    return render_template("list_movies.html", movies=movies, 
        list_name=lists_name, list_type=list_type, 
        watchlist=watchlist, watched_list=watched_list, 
        liked_list=liked_list, favorite_list=favorite_list,
        my_movies=my_movies )


@app.route("/search_results/<list_type>/<list_name>/<page>/<query>", methods=['GET', 'POST'])
def search_results(list_type, list_name, query, page=1):
    lists_name = get_list_name(list_name) #Remove Character from List Name
    endpoint_path = f"/{list_type}/{list_name}"
    endpoint_api_key = f"?api_key={app.api_key}"
    endpoint_lang = "&language=en-US"
    endpoint_query = f"&language=en-US&query={query}"
    img_url_endpoint_size = "https://image.tmdb.org/t/p/w500"
    endpoint = f"{api_url_src}{app.api_version}{endpoint_path}{endpoint_api_key}{endpoint_lang}{endpoint_query}&page={page}&include_adult=false"
    req = requests.get(endpoint)

    movies=[]

    if req.status_code == 200:
        data = req.json()
        total_pages = data['total_pages']
        results = data['results']
        if len(results) > 0:
            movie_ids = set()
            for result in results:
                if (result['media_type'] == "movie" or result['media_type'] == "tv") :
                    img_url = f"{img_url_endpoint_size}{result['poster_path']}"
                    result['poster_path'] = img_url
            movies = results
        else:    
            flash("Fail on Loading List, No results found", 'error')
    else:    
        flash("Fail on Loading List, Req. Status Code:" + req.status_code , 'error')

    return render_template("search_results.html", movies=movies, total_pages=total_pages, query=query, page_active=page)


def load_watchlist(user_id):
    watchlist = mongo.db.movies_users.find({"user_id": ObjectId(user_id),
        "to_watch": "on"})
    return watchlist


def load_watched_list(user_id):
    watched_list = mongo.db.movies_users.find({"user_id": ObjectId(user_id),
        "watched": "on"})
    return watched_list


def load_liked_list(user_id):
    liked_list = mongo.db.movies_users.find({"user_id": ObjectId(user_id),
        "liked": "on"})
    return liked_list


def load_favorite_list(user_id):
    favorite_list = mongo.db.movies_users.find({"user_id": ObjectId(user_id),
        "favorite": "on"})
    return favorite_list

def load_my_movies(user_id):
    my_movies_list = mongo.db.movies_users.find({"user_id": ObjectId(user_id)})
    return my_movies_list

def load_reviews(movie_id, user_id=""):
    if user_id == "":
        reviews_list = mongo.db.movies_users_reviews.find({
        "movie_id": movie_id})
    else:
        reviews_list = mongo.db.movies_users_reviews.find_one({
        "user_id": ObjectId(user_id),
        "movie_id": movie_id})

    return reviews_list


def get_user_id():
    if session.get('user'):
        if session['user']:
            user_id = mongo.db.users.find_one(
                {"username": session["user"]})["_id"]
    return user_id

def user_must_log_in():
    flash("You must log in first", 'warning')
    return redirect(url_for("login"))


### URL SAMPLE - GET /movie/{movie_id}
#https://api.themoviedb.org/3/movie/{movie_id}?api_key=<api_key>
@app.route("/view_movie/<list_type>/<movie_id>", methods=["GET", "POST"])
def view_movie(list_type, movie_id):
    movies_users = ''
    user_id = ''
    if session.get('user'):
        if session['user']:
            user_id = get_user_id()

            movies_users = mongo.db.movies_users.find_one({"movie_id": movie_id, 
                        "user_id": ObjectId(user_id)})
    
    endpoint_path = f"/{list_type}/{movie_id}"
    endpoint_api_key = f"?api_key={app.api_key}"
    endpoint_lang = "&language=en-US"
    img_url_endpoint_size = "https://image.tmdb.org/t/p/w500"
    endpoint = f"{api_url_src}{app.api_version}{endpoint_path}{endpoint_api_key}{endpoint_lang}"
    req = requests.get(endpoint)
    movies = []
    reviews = []
    if req.status_code == 200:
        data = req.json()
        img_url = f"{img_url_endpoint_size}{data['poster_path']}"
        data['poster_path'] = img_url
        if list_type == 'movie' :
            if data['release_date'] != "":
                date_str = datetime.strptime(data['release_date'], '%Y-%m-%d').date()
                data['release_date'] = datetime.strftime(date_str, '%d/%m/%Y')
            if data['budget'] != "":
                budget = int(data['budget'])
                if budget > 0 :
                    data['budget'] = str(babel.numbers.format_currency( decimal.Decimal(data['budget']), "USD" ))
                else:
                    data['budget'] = ""
            if data['revenue'] != "":
                revenue = int(data['revenue'])
                if revenue > 0 :
                    data['revenue'] = str(babel.numbers.format_currency( decimal.Decimal(data['revenue']), "USD" ))
                else:
                    data['revenue'] = ""
        movies = data
        reviews = load_reviews(movie_id)
        review_movie_user = ""
        if user_id != '':
            review_movie_user = load_reviews(movie_id, user_id)
    else:    
        flash("Fail on Loading Title", 'error')
        return redirect(url_for("list_movies"))
    return render_template("view_movies.html", movies=movies, 
        list_type=list_type, movies_users=movies_users, reviews=reviews,
        review_movie_user=review_movie_user)


### Get list_type return list_name
def get_list_name(list_type):
    char_remove = "_"
    for i in range(0,len(char_remove)):
        list_name = list_type.replace(char_remove[i]," ").title()
    return list_name


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db 
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        
        if existing_user:
            flash("Username already exists", 'warning')
            return redirect(url_for("register"))
        
        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password")),
            "full_name": request.form.get("full_name").title(),
            "email": request.form.get("email").lower()
        }

        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Succesfull", 'success')
        
        return redirect(url_for("profile", username=session["user"]))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        #Check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matched user input
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                
                flash("Welcome, {}".format(
                    request.form.get("username")), 'success')
                return redirect(url_for(
                    "profile", username=session["user"]))
            else:
                #invalid password match
                flash("Incorret Password", 'warning')
                return redirect(url_for("login"))
        else:
            # username doesn't exist
            flash("Incorret Username and/or Password", 'warning')
            return redirect(url_for("login"))

    return render_template("login.html")

    
@app.route("/logout")
def logout():
    # remove user from session cookies
    flash("You have been logged out", 'success')
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    
    if session['user']:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))

@app.route("/edit_profile_page/<username>", methods=["GET", "POST"])
def edit_profile_page(username):
    # grab the session user's username from db
    user = mongo.db.users.find_one(
        {"username": session["user"]})
    
    if session['user']:
        return render_template("edit_profile.html", user=user)

    return redirect(url_for("login"))

@app.route("/edit_profile/<user_id>", methods=["GET", "POST"])
def edit_profile(user_id):
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"_id": ObjectId(user_id)})
                
        # ensure hashed password matched user input
        if check_password_hash(existing_user["password"],
            request.form.get("password")):
            if len(request.form.get("new_password")) > 0 :
                password = request.form.get("new_password")
            else:
                password = request.form.get("password")
            submit = {
                "username": request.form.get("username"),
                "password": generate_password_hash(password),
                "full_name": request.form.get("full_name").title(),
                "email": request.form.get("email")
            }
            mongo.db.users.update({"_id": ObjectId(user_id)},submit)
            flash("Profile Successfully Updated", 'success')
        else:
            #invalid password match
            flash("Incorret Password", 'warning')

    username = mongo.db.users.find_one(
            {"_id": ObjectId(user_id)})["username"]
    
    # put the new user into 'session' cookie
    session["user"] = username
    return redirect(url_for("edit_profile_page", username=username))


@app.route("/add_list/<movie_id>/<list_type>/<title>/", methods=["GET", "POST"])
def add_list(movie_id, list_type, title):

    if session.get('user'):
        if len(session["user"]) > 0:
            if request.method == "POST":
                
                user_id = mongo.db.users.find_one(
                    {"username": session["user"]})["_id"]
                list = {
                        "movie_id": movie_id,
                        "poster_path": request.form.get("poster_path"),
                        "title": title,
                        "list_type": list_type,
                        "user_id": ObjectId(user_id),
                        "to_watch": request.form.get("edt_to_watch"),
                        "watched": request.form.get("edt_watched"),
                        "liked": request.form.get("edt_liked"),
                        "favorite": request.form.get("edt_favorite")
                    }
                mongo.db.movies_users.update({"movie_id": movie_id, 
                    "user_id": ObjectId(user_id)}, list, upsert=True)
                
                flash("Lists Updated", 'success')
    else:
        flash("You must log in first", 'warning')
        return redirect(url_for("login"))

    return redirect(url_for("view_movie", list_type=list_type,
         movie_id=movie_id))


@app.route("/add_review/<movie_id>/<list_type>/<title>/", methods=["GET", "POST"])
def add_review(movie_id, list_type, title):

    if session.get('user'):
        if len(session["user"]) > 0:

            if request.method == "POST":
                
                user_name = session["user"]
                user_id = mongo.db.users.find_one(
                    {"username": session["user"]})["_id"]
                         
                list = {
                        "movie_id": movie_id,
                        "poster_path": request.form.get("poster_path"),
                        "title": title,
                        "list_type": list_type,
                        "user_id": ObjectId(user_id),
                        "user_name": user_name.title(),
                        "review": request.form.get("review")
                    }
                mongo.db.movies_users_reviews.update({"movie_id": movie_id, 
                    "user_id": ObjectId(user_id)}, list, upsert=True)
                
                flash("Review Updated", 'success')
    else:
        flash("You must log in first", 'warning')
        return redirect(url_for("login"))

    return redirect(url_for("view_movie", list_type=list_type,
         movie_id=movie_id))


@app.route("/delete_review/<movie_id>/<list_type>/<title>/<review_id>")
def delete_review(movie_id, list_type, title, review_id):
    
    mongo.db.movies_users_reviews.remove({"_id": ObjectId(review_id)})
        
    flash("Review Removed", 'success')
    
    return redirect(url_for("view_movie", list_type=list_type,
        movie_id=movie_id))


@app.route("/delete_movie/<movie_id>")
def delete_movie(movie_id):

    mongo.db.movies_users.remove({"_id": ObjectId(movie_id)})
        
    flash("Title Removed", 'success')
    return redirect(url_for("list_movies", _anchor="my_movies"))


@app.route("/delete_user")
def delete_user():
    
    if session.get('user'):
        if session['user']:
            user_id = get_user_id()

            mongo.db.movies_users_reviews.remove({"user_id": ObjectId(user_id)})
            mongo.db.movies_users.remove({"user_id": ObjectId(user_id)})
            mongo.db.users.remove({"_id": ObjectId(user_id)})
            
    flash("User Account Deleted", 'success')
    return redirect(url_for("logout"))


@app.route("/email_sent/")
def email_sent():
    flash("Email Sent", 'success')
    return redirect(url_for("list_movies", _anchor="contact"))


#Source:
#https://flask.palletsprojects.com/en/1.1.x/patterns/errorpages/
@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404     


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=False)