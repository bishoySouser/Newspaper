import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///news.db")

@app.route("/")
def index():
    posts = db.execute("SELECT title, decription, name, created_at FROM posts JOIN authors ON posts.author_id=authors.id ORDER BY created_at DESC")
    return render_template("index.html", posts=posts)

@app.route("/create", methods=["GET", "POST"])
def create():
    # Check method request
    if request.method == "POST":
        # Check request
        if not request.form.get("title"):
            return apology("must provide title", 403)
        elif not request.form.get("decription"):
            return apology("must provide decription", 403)
        else:
            db.execute("INSERT INTO posts (author_id, title, decription) VALUES(:author_id, :title, :decription)",
                        author_id = request.form.get("author_id"),
                        title = request.form.get("title"),
                        decription = request.form.get("decription"))
            return redirect("/")
    else:
        authors = db.execute("SELECT * FROM authors")
        return render_template("create.html", authors=authors)

@app.route("/delete", methods=["GET", "POST"])
def delete():
    # Check method request
    if request.method == "POST":
        db.execute("DELETE FROM posts WHERE id=:id", id=request.form.get("post_id"))
        return redirect("/")
    else:
        posts = db.execute("SELECT posts.id, title, name, created_at FROM posts JOIN authors ON posts.author_id=authors.id")
        return render_template("delete.html", posts=posts)

@app.route("/author", methods=["GET", "POST"])
def author():
    # Check method request
    if request.method == "POST":
        # Check request
        if not request.form.get("name"):
            return apology("must provide author", 403)
        else:
            db.execute("INSERT INTO authors (name) VALUES(:name)",
                        name = request.form.get("name").capitalize())
            return redirect("/")
    else:
        return render_template("author.html")

@app.route("/statistics")
def statistic():
    # post count
    post = db.execute("SELECT COUNT(id) as p FROM posts")
    p_count = post[0]["p"]

    # author count
    author = db.execute("SELECT COUNT(id) as a FROM authors")
    a_count = author[0]["a"]

    return render_template("statistics.html", p_count=p_count, a_count=a_count)

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
