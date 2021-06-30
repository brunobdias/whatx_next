import os
import json
from flask import (
    Flask, flash, render_template, 
    redirect, request, session, url_for)
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

if os.path.exists("env.py"):
    import env
import requests
import pprint

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")
app.api_key = os.environ.get("API_KEY")
app.api_version = os.environ.get("API_VERSION")

# User session management setup
# https://flask-login.readthedocs.io/en/latest
#login_manager = LoginManager()
#login_manager.init_app(app)

mongo = PyMongo(app)

api_url_src = "https://api.themoviedb.org/"
endpoint_path = None

# GOOGLE AUTH SETUP
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = ("https://accounts.google.com/.well-known/openid-configuration")

# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

"""
    list_type: now_playing, popular, top_rated, upcoming
    URL SAMPLE# https://api.themoviedb.org/3/movie/<list_type>?api_key=<api_key>&language=en-US
"""
@app.route("/", methods=['GET', 'POST'])
@app.route("/list_movies/<list_type>", methods=['GET', 'POST'])
def list_movies(list_type="now_playing"):
    if len(list_type) == 0:
        list_type = "now_playing"
    list_name = get_list_name(list_type) #
    endpoint_path = f"/movie/{list_type}"
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
    
    return render_template("list_movies.html", movies=movies, list_name=list_name)


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


### Get list_type return list_name
def get_list_name(list_type):
    char_remove = "_"
    for i in range(0,len(char_remove)):
        list_name = list_type.replace(char_remove[i]," ").title()
    return list_name


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/login_google")
def login_google():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)


    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    return redirect(url_for("list_movies"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("list_movies"))
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