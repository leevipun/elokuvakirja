from flask import Flask, render_template, request, flash, redirect, session, jsonify, get_flashed_messages
import sqlite3
from werkzeug.security import check_password_hash

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'your_secret_key'

import users
import movies

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        get_flashed_messages()
        return render_template('login.html')
    
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")


    if not username or not password:
        flash("Please enter both username and password")
        return redirect("/login")

    user = users.get_user(username)
    
    if not user:
        flash("Invalid username or password")
        return redirect("/login")

    if check_password_hash(user['password_hash'], password):
        session["username"] = username
        return redirect("/")
    
    flash("Invalid username or password")
    return redirect("/login")

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template('register.html')
    else:
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        password_conf = request.form.get("password_conf", "")

        if not username or not password:
            flash("Username and password are required")
            return redirect("/register")

        if password != password_conf:
            flash("Passwords do not match")
            return redirect("/register")

        try:
            users.create_user(username, password)
            session["username"] = username
            return redirect("/")
        except sqlite3.IntegrityError:
            flash("Username already exists")
            return redirect("/register")
        
@app.route('/add', methods=["POST", "GET"])
def add():
    if "username" not in session:
        return redirect("/login")
    
    user = users.get_user(session["username"])
    if not user:
        return redirect("/login")
        
    if request.method == "GET":
        return render_template("add.html")
    
    # Handle POST request to add movie
    movie_data = {
        "title": request.form.get("title", "").strip(),
        "year": request.form.get("year") or None,
        "duration": request.form.get("duration") or None,
        "director": request.form.get("director", "").strip() or None,
        "genre": request.form.get("genre") or None,
        "watch_date": request.form.get("watchDate") or None,
        "rating": request.form.get("rating") or None,
        "watched_with": request.form.get("watchedWith", "").strip() or None,
        "platform": request.form.get("platform") or None,
        "review": request.form.get("review", "").strip() or None,
        "favorite": bool(request.form.get("favorite")),
        "rewatchable": bool(request.form.get("rewatchable"))
    }
    
    if not movie_data["title"]:
        flash("Movie title is required", "error")
        return render_template("add.html")
    
    try:
        movies.add_movie(user["id"], movie_data)
        flash("Movie added successfully!", "success")
    except Exception as e:
        flash(f"Error adding movie: {str(e)}", "error")
    
    return redirect("/")


if __name__ == '__main__':
    app.run(debug=True)