import os
import json
import requests
import pprint
from flask import (
    Flask, flash, render_template, 
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
if os.path.exists("env.py"):
    import env

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")
app.api_key = os.environ.get("API_KEY")

mongo = PyMongo(app)

@app.route("/", methods=['GET'])
@app.route("/get_movies", methods=['GET'])
def get_movies():
    req = requests.get("https://dog-facts-api.herokuapp.com/api/v1/resources/dogs/all")
    print(json.loads(req.content))
    movies = json.loads(req.content)
    return render_template("get_movies.html", movies=movies)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True) #Change to debug to false before deployment final version