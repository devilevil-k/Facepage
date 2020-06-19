import time
from flask import Flask, session, redirect, render_template, request, jsonify, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from werkzeug.security import check_password_hash, generate_password_hash

import requests

from helpers import login_required

app = Flask(__name__)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database

# database engine object from SQLAlchemy that manages connections to the database
engine = create_engine('postgres://likybfnlvedjfi:f3c8f8a7020159c8751a179dafd45e9bcb743a6811de0b396d8fdda05f155fa8@ec2-54-75-246-118.eu-west-1.compute.amazonaws.com:5432/dt95jdu805654')

# create a 'scoped session' that ensures different users' interactions with the
# database are kept separate
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
@login_required
def index():
    return render_template("post.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    username = request.form.get("email")
    if request.method == "POST":
        if not request.form.get("email"):
            return render_template("login.html", message="must provide email")
        elif not request.form.get("password"):
            return render_template("login.html", message="must provide password")
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                            {"username": username})
        result = rows.fetchone()
        if result == None or not check_password_hash(result[2], request.form.get("password")):
            return render_template("login.html", message="invalid username and/or password")
        session["user_id"] = result[0]
        session["user_name"] = result[1]
        return redirect("/")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()
    if request.method == "POST":
        if not request.form.get("email"):
            return render_template("register.html", message="must provide email")
        userCheck = db.execute("SELECT * FROM users WHERE username = :username",
                          {"username":request.form.get("email")}).fetchone()
        if userCheck:
            return render_template("register.html", message="email already exist")
        elif not request.form.get("first_name"):
            return render_template("register.html", message="must provide first name")
        elif not request.form.get("last_name"):
            return render_template("register.html", message="must provide last name")
        elif not request.form.get("password"):
            return render_template("register.html", message="must provide password")
        elif not request.form.get("confirmation"):
            return render_template("register.html", message="must confirm password")
        elif not request.form.get("password") == request.form.get("confirmation"):
            return render_template("register.html", message="passwords didn't match")
        hashedPassword = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)
        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                            {"username":request.form.get("email"),
                             "password":hashedPassword})
        db.commit()
        flash('Account created', 'info')
        return redirect("/login")
    else:
        return render_template("register.html")

@app.route("/draw")
@login_required
def draw():
    return render_template("draw.html")

@app.route("/posts", methods=["POST"])
def posts():

    start= int(request.form.get("start") or 0)
    end = int(request.form.get("end") or (start+9))

    data = []
    for i in range(start, end+1):
        data.append(f"Post #{i} Some random content for the post to make it look like posts of twitter and facebook.")

    time.sleep(1)

    return jsonify(data)
