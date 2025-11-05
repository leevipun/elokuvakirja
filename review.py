import db

def add_review(user_id, movie):
    if not user_id:
        return "User ID is required."

    # Update user's rating for the movie
    sql = """INSERT INTO user_ratings (rating, watched, watch_date, watched_with, favorite, user_id, movie_id)
             VALUES (?, ?, ?, ?, ?, ?, ?)
            """

    rating_value = movie.get("rating")
    if rating_value:
        # Convert from 10-point to 5-point scale if needed
        if float(rating_value) > 5:
            rating_value = float(rating_value) / 2

    params = (
        rating_value if rating_value else None,
        1,  # Mark as watched
        movie["watch_date"] if movie["watch_date"] else None,
        movie["watched_with"] if movie["watched_with"] else None,
        bool(movie.get("favorite", False)),
        user_id,
        movie["id"]
    )

    print(params)

    db.execute(sql, params)
    return movie["id"]

def get_reviews_by_user(user_id):
    sql = """SELECT ur.rating, ur.watched, ur.watch_date, ur.watched_with, ur.favorite,
                    m.id AS movie_id, m.title, m.duration
             FROM user_ratings ur
             JOIN movies m ON ur.movie_id = m.id
             WHERE ur.user_id = ?
          """
    params = (user_id,)
    reviews = db.query(sql, params)
    
    return reviews
