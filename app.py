import os
from flask import (
    Flask, flash, render_template, 
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import json
import pprint
import requests
if os.path.exists("env.py"):
    import env

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")
app.api_key = os.environ.get("API_KEY")
app.api_version = os.environ.get("API_VERSION")

mongo = PyMongo(app)

api_url_src = "https://api.themoviedb.org/"
endpoint_path = None


### URL SAMPLE - GET /movie/now_playing
# https://api.themoviedb.org/3/movie/now_playing?api_key=<api_key>&language=en-US
@app.route("/", methods=['GET', 'POST'])
@app.route("/now_playing", methods=['GET', 'POST'])
def now_playing():
    endpoint_path = "/movie/now_playing"
    endpoint_api_key = f"?api_key={app.api_key}"
    endpoint_lang = "&language=en-US"
    img_url_endpoint_size = "https://image.tmdb.org/t/p/w500"
    endpoint = f"{api_url_src}{app.api_version}{endpoint_path}{endpoint_api_key}{endpoint_lang}"
    req = requests.get(endpoint)
    pprint.pprint(endpoint)
    if req.status_code == 200:
        data = req.json()
        results = data['results']
        if len(results) > 0:
            print(results[0].keys())
            movie_ids = set()
            for result in results:
                img_url = f"{img_url_endpoint_size}{result['poster_path']}"
                result['poster_path'] = img_url
                result['overview'] = "Now Playing Movies"
                _id = result['id']
                title = result['title']
                print(title, _id)
                movie_ids.add(_id)
            movies = results
        else:    
            flash("Fail Trying to Loading List")
    
    return render_template("list_movies.html", movies=movies)

### URL SAMPLE - GET /movie/popular
# https://api.themoviedb.org/3/movie/popular?api_key=cb840be2847e004061e5c0d2c9f0f0aa&language=en-US&page=1
@app.route("/top_rated", methods=['GET', 'POST'])
def top_rated():
    endpoint_path = "/movie/top_rated"
    endpoint_api_key = f"?api_key={app.api_key}"
    endpoint_lang = "&language=en-US"
    img_url_endpoint_size = "https://image.tmdb.org/t/p/w500"
    endpoint = f"{api_url_src}{app.api_version}{endpoint_path}{endpoint_api_key}{endpoint_lang}"
    req = requests.get(endpoint)
    pprint.pprint(endpoint)
    if req.status_code == 200:
        data = req.json()
        results = data['results']
        if len(results) > 0:
            print(results[0].keys())
            movie_ids = set()
            for result in results:
                img_url = f"{img_url_endpoint_size}{result['poster_path']}"
                result['poster_path'] = img_url
                result['overview'] = "TMDB - Top Rated Movies"
                _id = result['id']
                title = result['title']
                print(title)
                movie_ids.add(_id)
            movies = results
        else:    
            flash("Fail Trying to Loading List")
    
    return render_template("list_movies.html", movies=movies)

### URL SAMPLE - GET /movie/{movie_id}
#https://api.themoviedb.org/3/movie/{movie_id}?api_key=<api_key>
@app.route("/view_movie/<movie_id>", methods=["GET", "POST"])
def view_movie(movie_id):
    endpoint_path = f"/movie/{movie_id}"
    endpoint_api_key = f"?api_key={app.api_key}"
    endpoint_lang = "&language=en-US"
    img_url_endpoint_size = "https://image.tmdb.org/t/p/w500"
    endpoint = f"{api_url_src}{app.api_version}{endpoint_path}{endpoint_api_key}{endpoint_lang}"
    req = requests.get(endpoint)
    pprint.pprint(endpoint)
    if req.status_code == 200:
        data = req.json()
        img_url = f"{img_url_endpoint_size}{data['poster_path']}"
        data['poster_path'] = img_url
        pprint.pprint(data['poster_path'])
        movies = data
    return render_template("view_movies.html", movies=movies)
    """
    if req.status_code == 200:
        data = req.json()
        results = data['results']
        if len(results) > 0:
            print(results[0].keys())
            movie_ids = set()
            for result in results:
                img_url = f"{img_url_endpoint_size}{result['poster_path']}"
                result['poster_path'] = img_url
                _id = result['id']
                title = result['title']
                print(title)
                movie_ids.add(_id)
            movies = results
        else:    
            flash("Fail Trying to Loading List")
    """
    #return render_template("view_movies.html")
    #return render_template("view_movies.html", movies=movies)

    """
GET
/movie/latest
Get the most newly created movie. This is a live response and will continuously change.

@app.route("/search", methods=["GET", "POST"])
def search():
    query = requests.get("query")
    tasks = list(mongo.db.tasks.find({"$text":{"$search": query}}))
    return render_template("get_movies.html", tasks=tasks)


    GET
/search/movie

https://api.themoviedb.org/3/search/movie?api_key=cb840be2847e004061e5c0d2c9f0f0aa&language=en-US&query=army&page=1&include_adult=false

    req = requests.get("https://dog-facts-api.herokuapp.com/api/v1/resources/dogs/all")
    print(json.loads(req.content))
    movies = json.loads(req.content)
    return render_template("get_movies.html", movies=movies)
    """

if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True) #Change to debug to false before deployment final version