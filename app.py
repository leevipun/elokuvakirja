from flask import Flask, render_template, request, flash, redirect, session, jsonify, get_flashed_messages
import sqlite3
from werkzeug.security import check_password_hash
from datetime import datetime

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'your_secret_key'

import users
import movies
import categories
import platforms
import directors

@app.route('/')
def index():
    user_movies = []
    if "username" in session:
        user = users.get_user(session["username"])
        if user:
            user_movies = movies.get_movies()
    return render_template('index.html', movies=user_movies)

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
        # Load existing categories for the form
        existing_categories = categories.get_categories() or []
        existing_platforms = platforms.get_platforms() or []
        existing_directors = directors.get_directors() or []
        return render_template("add.html", categories=existing_categories, directors=existing_directors, platforms=existing_platforms, current_year=datetime.now().year)
    
    # Handle POST request to add movie
    title = request.form.get("title", "").strip()
    if not title:
        flash("Movie title is required", "error")
        existing_categories = categories.get_categories() or []
        existing_platforms = platforms.get_platforms() or []
        existing_directors = directors.get_directors() or []
        return render_template("add.html", categories=existing_categories, directors=existing_directors, platforms=existing_platforms, current_year=datetime.now().year)
    
    # Handle category selection or creation
    category_id = None
    selected_category = request.form.get("category")
    new_category = request.form.get("new_category", "").strip()
    
    if new_category:
        # Create new category
        try:
            category_id = categories.add_category(new_category)
        except sqlite3.IntegrityError:
            # Category already exists, find it
            existing_categories = categories.get_categories()
            for cat in existing_categories:
                if cat['name'].lower() == new_category.lower():
                    category_id = cat['id']
                    break
    elif selected_category and selected_category != "":
        category_id = int(selected_category)

    streaming_platform_id = None
    selected_platform = request.form.get("streaming_platform")
    new_platform = request.form.get("new_platform", "").strip()

    if new_platform:

        try:
            streaming_platform_id = platforms.add_platform(new_platform)
        except sqlite3.IntegrityError:

            existing_platforms = platforms.get_platforms()
            for platform in existing_platforms:
                if platform['name'].lower() == new_platform.lower():
                    streaming_platform_id = platform['id']
                    break
    elif selected_platform and selected_platform != "":
        streaming_platform_id = int(selected_platform)


    director_id = None
    selected_director = request.form.get("director")
    new_director = request.form.get("new_director", "").strip()

    if new_director:

        try:
            director_id = directors.add_director(new_director)
        except sqlite3.IntegrityError:

            existing_directors = directors.get_directors()
            for director in existing_directors:
                if director['name'].lower() == new_director.lower():
                    director_id = director['id']
                    break
    elif selected_director and selected_director != "":
        director_id = int(selected_director)
    
    movie_data = {
        "title": title,
        "year": request.form.get("year") or None,
        "duration": request.form.get("duration") or None,
        "director_id": director_id,
        "category_id": category_id,
        "streaming_platform_id": streaming_platform_id,
        "watch_date": request.form.get("watchDate") or None,
        "rating": request.form.get("rating") or None,
        "watched_with": request.form.get("watchedWith", "").strip() or None,
        "review": request.form.get("review", "").strip() or None,
        "favorite": bool(request.form.get("favorite")),
        "rewatchable": bool(request.form.get("rewatchable"))
    }
    
    try:
        movies.add_movie(user["id"], movie_data)
        flash("Movie added successfully!", "success")
        return redirect("/")
    except Exception as e:
        flash(f"Error adding movie: {str(e)}", "error")
        existing_categories = categories.get_categories() or []
        return render_template("add.html", categories=existing_categories, current_year=datetime.now().year)


if __name__ == '__main__':
    app.run(debug=True)