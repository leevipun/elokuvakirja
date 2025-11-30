import db

def add_review(user_id, movie):
    if not user_id:
        return "User ID is required."

    # Update or insert user's rating for the movie
    sql = """INSERT OR REPLACE INTO user_ratings (rating, watched, watch_date, watched_with, review, favorite, user_id, movie_id)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """

    rating_value = movie.get("rating")

    params = (
        rating_value if rating_value else None,
        1,  # Mark as watched
        movie.get("watch_date") or None,
        movie.get("watched_with") or None,
        movie.get("review") if movie.get("review") else None,
        bool(movie.get("favorite", False)),  # Add favorite field
        user_id,
        movie["id"]
    )

    print(params)

    db.execute(sql, params)
    
    # Sync favorite status with user_favorites table
    is_favorite = bool(movie.get("favorite", False))
    movie_id = movie["id"]
    
    if is_favorite:
        # Add to favorites if not already there
        sql_add_fav = "INSERT OR IGNORE INTO user_favorites (user_id, movie_id) VALUES (?, ?)"
        db.execute(sql_add_fav, [user_id, movie_id])
    else:
        # Remove from favorites if it was there
        sql_remove_fav = "DELETE FROM user_favorites WHERE user_id = ? AND movie_id = ?"
        db.execute(sql_remove_fav, [user_id, movie_id])
    
    return movie["id"]

def get_reviews_by_user(user_id):
    sql = """SELECT ur.rating, ur.watched, ur.watch_date, ur.watched_with, ur.review,
                    m.id AS movie_id, m.title, m.duration
             FROM user_ratings ur
             JOIN movies m ON ur.movie_id = m.id
             WHERE ur.user_id = ? AND ur.rating IS NOT NULL
          """
    params = (user_id,)
    reviews = db.query(sql, params)

    return reviews
