from flask import Flask, render_template, request, flash, redirect, session, get_flashed_messages, abort
import sqlite3
from werkzeug.security import check_password_hash
from datetime import datetime
import os
from dotenv import load_dotenv
import secrets

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, static_url_path='/static')
app.secret_key = os.getenv("SECRET_KEY")

import users
import movies
import categories
import platforms
import directors

@app.route('/')
def index():
    session["csrf_token"] = secrets.token_hex(16)
    user_movies = []
    if "username" in session:
        user = users.get_user(session["username"])
        if user:
            user_movies = movies.get_movies()
    return render_template('index.html', movies=user_movies, csrf_token=session.get("csrf_token"))

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
        session["csrf_token"] = secrets.token_hex(16)
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
        return render_template("add.html", categories=existing_categories, directors=existing_directors, platforms=existing_platforms, current_year=datetime.now().year, csrf_token=session.get("csrf_token"))
    
    csrf_token = request.form.get("csrf_token")
    if not csrf_token or csrf_token != session.get("csrf_token"):
        abort(403, description="CSRF validation failed ❌")
    
    # Handle POST request to add movie
    title = request.form.get("title", "").strip()
    if not title:
        flash("Movie title is required", "error")
        existing_categories = categories.get_categories() or []
        existing_platforms = platforms.get_platforms() or []
        existing_directors = directors.get_directors() or []
        return render_template("add.html", categories=existing_categories, directors=existing_directors, platforms=existing_platforms, current_year=datetime.now().year, csrf_token=session.get("csrf_token"))
    
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

@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    user_id = None
    if "username" in session:
        user = users.get_user(session["username"])
        user_id = user["id"] if user else None
    
    movie = movies.get_movie_by_id(movie_id, user_id)
    if not movie:
        flash("Movie not found")
        return redirect("/")
    
    return render_template('movie_detail.html', movie=movie)

@app.route('/search', methods=["GET"])
def search():
    if "username" not in session:
        return redirect("/login")
    
    user = users.get_user(session["username"])
    if not user:
        return redirect("/login")
    
    # Get search parameters
    query = request.args.get('q', '').strip()
    genre = request.args.get('genre', '')
    year = request.args.get('year', '')
    platform = request.args.get('platform', '')
    rating = request.args.get('rating', '')
    sort_by = request.args.get('sort', 'relevance')
    
    # Get search results
    search_results = []
    if query or genre or year or platform or rating:
        search_results = movies.search_movies(
            user_id=user["id"],
            query=query,
            genre=genre,
            year=year,
            platform=platform,
            rating=rating,
            sort_by=sort_by
        )
    
    return render_template('search.html', movies=search_results)

@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")

if __name__ == '__main__':
    app.run(debug=True)