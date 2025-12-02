from datetime import datetime
import sqlite3
import secrets
import os
import time
from math import ceil

from flask import (
    Flask,
    render_template,
    request,
    flash,
    redirect,
    session,
    get_flashed_messages,
    abort,
    g,
)
from werkzeug.security import check_password_hash


import users
import movies
import categories
import platforms
import directors
import review

app = Flask(__name__, static_url_path="/static")
app.secret_key = os.getenv("SECRET_KEY") or "fallback-secret-key-for-development-only"
app.config['DEBUG'] = True


def check_csrf(request=None):
    if request.method == "POST":
        print("Checking CSRF token...")
        csrf_token = request.form.get("csrf_token")
        if not csrf_token or csrf_token != session.get("csrf_token"):
            abort(403, description="Forbidden")

@app.before_request
def before_request():
    check_csrf(request)
    g.start_time = time.time()


@app.after_request
def after_request(response):
    elapsed_time = round(time.time() - g.start_time, 2)
    print("elapsed time:", elapsed_time, "s")
    return response


# Add Jinja2 filter for date formatting
@app.template_filter("dateformat")
def dateformat(date_value):
    """Format date for HTML date input (YYYY-MM-DD)"""
    if not date_value:
        return ""
    # If it's already a string in YYYY-MM-DD format, return it
    if isinstance(date_value, str):
        return date_value
    # If it's a datetime object, format it
    if isinstance(date_value, datetime):
        return date_value.strftime("%Y-%m-%d")
    return str(date_value)


# Add global functions to Jinja2 context
@app.context_processor
def inject_globals():
    return {"max": max, "min": min, "range": range}


@app.route("/")
def index():
    session["csrf_token"] = secrets.token_hex(16)
    user_id = None
    if "username" in session:
        user = users.get_user(session["username"])
        if user:
            user_id = user["id"]
            session["user_id"] = user_id

    # Get page number from request, default to 1
    page = request.args.get("page", 1, type=int)
    per_page = 20  # Movies per page

    user_movies = movies.get_movies(page=page, per_page=per_page)

    # Calculate total items (simple query for count)
    import db

    count_result = db.query("SELECT COUNT(*) as total FROM movies")
    total_items = count_result[0]["total"] if count_result else 0
    total_pages = ceil(total_items / per_page) if total_items > 0 else 1

    pagination = {
        "total_pages": total_pages,
        "current_page": page,
        "total_items": total_items,
        "has_prev": page > 1,
        "has_next": page < total_pages,
        "prev_page": page - 1 if page > 1 else None,
        "next_page": page + 1 if page < total_pages else None,
    }

    return render_template(
        "index.html",
        movies=user_movies,
        pagination=pagination,
        csrf_token=session.get("csrf_token"),
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        session["csrf_token"] = secrets.token_hex(
            16
        )  # Generate CSRF token for login page
        get_flashed_messages()
        return render_template("login.html", csrf_token=session.get("csrf_token"))

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if not username or not password:
        flash("Please enter both username and password")
        return redirect("/login")

    user = users.get_user(username)

    if not user:
        flash("Invalid username or password")
        return redirect("/login")

    if check_password_hash(user["password_hash"], password):
        session["username"] = username
        session["user_id"] = user["id"]  # Add this line
        session["csrf_token"] = secrets.token_hex(16)
        return redirect("/")

    flash("Invalid username or password")
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        session["csrf_token"] = secrets.token_hex(
            16
        )  # Generate CSRF token for register page
        return render_template("register.html", csrf_token=session.get("csrf_token"))

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
        users.create_user(username, password)  # Create user first
        user = users.get_user(username)  # Then get the user
        session["username"] = username
        session["user_id"] = user["id"]
        session["csrf_token"] = secrets.token_hex(16)
        return redirect("/")
    except sqlite3.IntegrityError:
        flash("Username already exists")
        return redirect("/register")


def _get_form_entities():
    """Cache entity lookups to avoid duplicate queries"""
    return {
        "categories": categories.get_categories() or [],
        "platforms": platforms.get_platforms() or [],
        "directors": directors.get_directors() or [],
    }


@app.route("/add", methods=["POST", "GET"])
def add():
    if "username" not in session:
        return redirect("/login")

    user = users.get_user(session["username"])
    if not user:
        return redirect("/login")

    if request.method == "GET":
        # Load existing categories for the form
        entities = _get_form_entities()
        session["csrf_token"] = secrets.token_hex(16)
        return render_template(
            "add.html",
            categories=entities["categories"],
            directors=entities["directors"],
            platforms=entities["platforms"],
            current_year=datetime.now().year,
            movie_data=None,
            csrf_token=session.get("csrf_token"),
        )

    # Handle POST request to add movie
    title = request.form.get("title", "").strip()
    if not title:
        flash("Movie title is required", "error")
        entities = _get_form_entities()
        return render_template(
            "add.html",
            categories=entities["categories"],
            directors=entities["directors"],
            platforms=entities["platforms"],
            movie_data=None,
            current_year=datetime.now().year,
            csrf_token=session.get("csrf_token"),
        )

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
                if cat["name"].lower() == new_category.lower():
                    category_id = cat["id"]
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
                if platform["name"].lower() == new_platform.lower():
                    streaming_platform_id = platform["id"]
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
                if director["name"].lower() == new_director.lower():
                    director_id = director["id"]
                    break
    elif selected_director and selected_director != "":
        director_id = int(selected_director)

    movie_data = {
        "title": request.form.get("title") or None,
        "year": request.form.get("year") or None,
        "duration": request.form.get("duration") or None,
        "director_id": director_id,
        "category_id": category_id,
        "streaming_platform_id": streaming_platform_id,
        "watch_date": request.form.get("watchDate") or None,
        "rating": request.form.get("rating") or None,
        "watched_with": request.form.get("watchedWith", "").strip() or None,
        "owner_id": user["id"],
        "review": request.form.get("review", "").strip() or None,
        "favorite": bool(request.form.get("favorite")),
    }

    try:
        movies.add_movie(user["id"], movie_data)
        flash("Movie added successfully!", "success")
        return redirect("/")
    except Exception as e:
        flash(f"Error adding movie: {str(e)}", "error")
        entities = _get_form_entities()
        
        # Add entity names to movie_data so template can display them properly
        if category_id:
            for cat in entities["categories"]:
                if cat["id"] == category_id:
                    movie_data["category_name"] = cat["name"]
                    movie_data["category_id_only"] = category_id  # Keep ID for selection
                    break
        
        if streaming_platform_id:
            for platform in entities["platforms"]:
                if platform["id"] == streaming_platform_id:
                    movie_data["platform_name"] = platform["name"]
                    movie_data["platform_id_only"] = streaming_platform_id  # Keep ID for selection
                    break
        
        if director_id:
            for director in entities["directors"]:
                if director["id"] == director_id:
                    movie_data["director_name"] = director["name"]
                    movie_data["director_id_only"] = director_id  # Keep ID for selection
                    break
        
        return render_template(
            "add.html",
            categories=entities["categories"],
            directors=entities["directors"],
            platforms=entities["platforms"],
            movie_data=movie_data,
            current_year=datetime.now().year,
            csrf_token=session.get("csrf_token"),
        )


@app.route("/movie/<int:movie_id>")
def movie_detail(movie_id):
    user_id = None
    if "username" in session:
        user = users.get_user(session["username"])
        user_id = user["id"] if user else None

    movie = movies.get_movie_by_id(movie_id, user_id)
    if not movie:
        flash("Movie not found")
        return redirect("/")

    return render_template("movie_detail.html", movie=movie)


@app.route("/add-review/<int:movie_id>", methods=["POST", "GET"])
def add_review(movie_id):
    if "username" not in session:
        return redirect("/login")
    if request.method == "GET":
        session["csrf_token"] = secrets.token_hex(16)
        user = users.get_user(session["username"])
        movie = movies.get_movie_by_id(
            movie_id, user["id"]
        )  # Pass user_id to get user's rating data
        if not movie:
            flash("Movie not found")
            return redirect("/")
        return render_template(
            "edit.html", movie=movie, csrf_token=session.get("csrf_token")
        )

    user = users.get_user(session["username"])

    movie_data = {
        "id": movie_id,
        "watch_date": request.form.get("watchDate") or None,
        "rating": request.form.get("rating") or None,
        "watched_with": request.form.get("watchedWith", "").strip() or None,
        "review": request.form.get("review", "").strip() or None,
        "favorite": bool(request.form.get("favorite")),
    }

    try:
        review.add_review(user["id"], movie_data)
        flash("Review added successfully!", "success")
        return redirect(f"/movie/{movie_id}")
    except Exception as e:
        flash(f"Error adding review: {str(e)}", "error")
        return redirect(f"/add-review/{movie_id}")


@app.route("/search", methods=["GET"])
def search():
    user_id = None
    if "username" in session:
        user = users.get_user(session["username"])
        if user:
            user_id = user["id"]

    # Get page number from request, default to 1
    page = request.args.get("page", 1, type=int)
    per_page = 20

    # Extract and normalize filter options
    filter_options = {
        "query": request.args.get("q", "").strip(),
        "genre": request.args.get("genre", "").strip(),
        "year": request.args.get("year", "").strip(),
        "platform": request.args.get("platform", "").strip(),
        "rating": request.args.get("rating", "").strip(),
        "sort_by": request.args.get("sort", "date_added").strip(),
    }

    # Get filter options for the form (always needed)
    entities = _get_form_entities()

    # Get total count for accurate pagination
    total_items = movies.get_search_count(filter_options)
    total_pages = ceil(total_items / per_page) if total_items > 0 else 1

    # Get search results with pagination (always show results)
    search_results = movies.search_movies(
        user_id=user_id, filter_options=filter_options, page=page, per_page=per_page
    )

    pagination = {
        "current_page": page,
        "total_pages": total_pages,
        "total_items": total_items,
        "per_page": per_page,
        "has_prev": page > 1,
        "has_next": page < total_pages,
        "prev_page": page - 1 if page > 1 else None,
        "next_page": page + 1 if page < total_pages else None,
    }

    return render_template(
        "search.html",
        movies=search_results,
        pagination=pagination,
        categories=entities["categories"],
        platforms=entities["platforms"],
    )


@app.route("/edit/<int:movie_id>", methods=["POST", "GET"])
def edit(movie_id):
    if "username" not in session:
        return redirect("/login")

    user = users.get_user(session["username"])
    if not user:
        return redirect("/login")

    if request.method == "GET":
        session["csrf_token"] = secrets.token_hex(16)  # Generate CSRF token
        movie = movies.get_movie_by_id(movie_id, user["id"])
        if not movie:
            flash("Movie not found")
            return redirect("/")
        if movie["owner_id"] != user["id"]:
            return render_template(
                "edit.html", movie=movie, csrf_token=session.get("csrf_token")
            )
        entities = _get_form_entities()
        return render_template(
            "edit_owner.html",
            movie=movie,
            categories=entities["categories"],
            directors=entities["directors"],
            platforms=entities["platforms"],
            current_year=datetime.now().year,
            csrf_token=session.get("csrf_token"),
        )

    # Get the existing movie
    existing_movie = movies.get_movie_by_id(movie_id, user["id"])
    if not existing_movie:
        flash("Movie not found")
        return redirect("/")

    # Check if user is the owner
    is_owner = existing_movie["owner_id"] == user["id"]

    # Helper function to handle category/platform/director selection
    def get_entity_id(selected_value, new_value, add_func, get_func):
        entity_id = None
        if new_value:
            try:
                entity_id = add_func(new_value)
            except sqlite3.IntegrityError:
                entities = get_func()
                for entity in entities:
                    if entity["name"].lower() == new_value.lower():
                        entity_id = entity["id"]
                        break
        elif selected_value and selected_value != "":
            entity_id = int(selected_value)
        return entity_id

    if is_owner:
        # Owner is editing the movie details
        category_id = get_entity_id(
            request.form.get("category"),
            request.form.get("new_category", "").strip(),
            categories.add_category,
            categories.get_categories,
        )

        streaming_platform_id = get_entity_id(
            request.form.get("streaming_platform"),
            request.form.get("new_platform", "").strip(),
            platforms.add_platform,
            platforms.get_platforms,
        )

        director_id = get_entity_id(
            request.form.get("director"),
            request.form.get("new_director", "").strip(),
            directors.add_director,
            directors.get_directors,
        )

        # Prepare movie data for owner update (full edit)
        movie_data = {
            "id": movie_id,
            "title": request.form.get("title", "").strip(),
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
        }

        try:
            movies.update_movie_owner(user["id"], movie_data)
            flash("Movie updated successfully!", "success")
            return redirect(f"/movie/{movie_id}")
        except Exception as e:
            flash(f"Error updating movie: {str(e)}", "error")
            return redirect(f"/edit/{movie_id}")
    else:
        # Non-owner is adding a review/rating
        movie_data = {
            "id": movie_id,
            "watch_date": request.form.get("watchDate") or None,
            "rating": request.form.get("rating") or None,
            "watched_with": request.form.get("watchedWith", "").strip() or None,
            "review": request.form.get("review", "").strip() or None,
            "favorite": bool(request.form.get("favorite")),
        }

        print(movie_data)

        try:
            review.add_review(user["id"], movie_data)
            flash("Review added successfully!", "success")
            return redirect(f"/movie/{movie_id}")
        except Exception as e:
            flash(f"Error adding review: {str(e)}", "error")
            return redirect(f"/edit/{movie_id}")


@app.route("/delete/<int:movie_id>", methods=["POST"])
def delete(movie_id):
    if "username" not in session:
        return redirect("/login")

    user = users.get_user(session["username"])
    if not user:
        return redirect("/login")

    # Check if user owns or has rated the movie
    movie = movies.get_movie_by_id(movie_id, user["id"])
    if not movie:
        flash("Movie not found")
        return redirect("/")

    try:
        movies.delete_movie(user["id"], movie_id)
        flash("Movie deleted successfully!", "success")
        return redirect("/")
    except Exception as e:
        flash(f"Error deleting movie: {str(e)}", "error")
        return redirect(f"/movie/{movie_id}")


@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect("/login")

    user = users.get_user(session["username"])
    if not user:
        return redirect("/login")

    # Get page number from request, default to 1
    page = request.args.get("page", 1, type=int)
    per_page = 10  # Movies per page in dashboard

    user_movies = movies.get_movies_by_user(user["id"], page=page, per_page=per_page)
    user_reviews = review.get_reviews_by_user(user["id"])

    # Get total count for pagination
    total_movies_count = movies.get_user_movies_count(user["id"])
    total_pages = ceil(total_movies_count / per_page) if total_movies_count > 0 else 1

    # Fetch all stats from materialized user_stats table (optimized by triggers)
    import db

    user_stats_result = db.query(
        """SELECT 
           total_movies_watched,
           avg_rating,
           total_favorites,
           total_watch_hours,
           total_ratings_given,
           total_reviews_written
        FROM user_stats
        WHERE user_id = ?""",
        (user["id"],),
    )

    # Use stats from materialized table if available, otherwise use defaults
    if user_stats_result:
        stats = user_stats_result[0]
        total_movies = stats["total_movies_watched"] or 0
        avg_rating = round(float(stats["avg_rating"]) or 0, 2)
        total_favorites = stats["total_favorites"] or 0
        total_watch_time = round(float(stats["total_watch_hours"]) or 0, 1)
        total_ratings_given = stats["total_ratings_given"] or 0
        total_reviews_written = stats["total_reviews_written"] or 0
    else:
        # Fallback if no stats exist yet
        total_movies = total_movies_count
        total_ratings_given = len(user_reviews)
        ratings = [r["rating"] for r in user_reviews if "rating" in r and r["rating"]]
        avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else 0
        total_favorites = movies.get_favorites(user["id"])
        total_watch_time = 0
        total_reviews_written = len(
            [r for r in user_reviews if "review" in r and r["review"]]
        )

    # Convert created_at string to datetime object
    created_at = datetime.fromisoformat(user["created_at"])
    member_since = (datetime.now() - created_at).days

    pagination = {
        "current_page": page,
        "total_pages": total_pages,
        "total_items": total_movies,
        "has_prev": page > 1,
        "has_next": page < total_pages,
        "prev_page": page - 1 if page > 1 else None,
        "next_page": page + 1 if page < total_pages else None,
    }

    user_data = {
        "total_movies": total_movies,
        "total_favorites": total_favorites,
        "total_watch_time": total_watch_time,
        "total_ratings_given": total_ratings_given,
        "total_reviews_written": total_reviews_written,
        "avg_rating": avg_rating,
        "member_since": member_since,
        "movies": user_movies,
        "reviews": user_reviews,
    }

    return render_template(
        "user-dashboard.html", user_data=user_data, pagination=pagination
    )


@app.route("/favorites/<int:movie_id>", methods=["POST"])
def favorites(movie_id):
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    method = request.form.get("_method", "").upper()

    if method == "DELETE":
        movies.remove_from_favorites(user_id, movie_id)
    else:
        movies.add_to_favorites(user_id, movie_id)

    return redirect(f"/movie/{movie_id}")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/favorites")
def view_favorites():
    if "username" not in session:
        return redirect("/login")

    user = users.get_user(session["username"])
    if not user:
        return redirect("/login")

    # Get page number from request, default to 1
    page = request.args.get("page", 1, type=int)
    per_page = 12  # Movies per page in favorites

    favorite_movies = movies.get_favorite_movies(
        user["id"], page=page, per_page=per_page
    )

    # Get total count for pagination
    total_favorites_count = movies.get_favorite_movies_count(user["id"])
    total_pages = (
        ceil(total_favorites_count / per_page) if total_favorites_count > 0 else 1
    )

    pagination = {
        "current_page": page,
        "total_pages": total_pages,
        "total_items": total_favorites_count,
        "has_prev": page > 1,
        "has_next": page < total_pages,
        "prev_page": page - 1 if page > 1 else None,
        "next_page": page + 1 if page < total_pages else None,
    }

    return render_template(
        "favorites.html", movies=favorite_movies, pagination=pagination
    )


if __name__ == "__main__":
    app.run(debug=True)
