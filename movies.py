import db


def _transform_movie(row, user_id=None):
    """Helper function to transform database row into movie dict"""
    movie_dict = dict(row)
    # Create category object for template compatibility
    if movie_dict.get("category_name"):
        movie_dict["category"] = {"name": movie_dict["category_name"]}
    # Create platform object for template compatibility
    if movie_dict.get("platform_name"):
        movie_dict["platform"] = {"name": movie_dict["platform_name"]}
    # Add favorite status
    movie_dict["is_favorite"] = bool(movie_dict.get("user_favorite"))

    # Use user's own rating if available, otherwise use average rating
    if movie_dict.get("user_rating"):
        movie_dict["rating"] = round(float(movie_dict["user_rating"]), 1)
    elif movie_dict.get("average_rating"):
        movie_dict["rating"] = round(float(movie_dict["average_rating"]), 1)
    else:
        movie_dict["rating"] = None

    movie_dict["user_watched"] = bool(movie_dict.get("user_watched"))
    return movie_dict


def get_movies(page=1, per_page=20):
    offset = (page - 1) * per_page
    sql = """
        SELECT 
            m.id,
            m.title,
            m.year,
            m.duration,
            m.owner_id,
            m.category_id,
            m.streaming_platform_id,
            m.director_id,
            m.created_at,
            c.name AS category_name,
            d.name AS director_name,
            s.name AS platform_name,
            mrs.average_rating,
            mrs.total_ratings
        FROM movies m
        LEFT JOIN categories c ON m.category_id = c.id
        LEFT JOIN directors d ON m.director_id = d.id
        LEFT JOIN streaming_platforms s ON m.streaming_platform_id = s.id
        LEFT JOIN movie_rating_stats mrs ON m.id = mrs.movie_id
        ORDER BY m.created_at DESC
        LIMIT ?
        OFFSET ?;
    """
    results = db.query(sql, [per_page, offset])

    # Convert to list of dictionaries for easier handling
    movies = [_transform_movie(row) for row in results]
    return movies if movies else []


def get_movie_by_id(movie_id, user_id=None):
    """Get a single movie by ID"""
    if user_id:
        sql = """
            SELECT 
                m.*,
                c.name AS genre,
                d.name AS director,
                s.name AS platform,
                ur.rating AS user_rating,
                ur.watched AS user_watched,
                ur.watch_date,
                ur.watched_with,
                ur.review,
                CASE WHEN uf.movie_id IS NOT NULL THEN 1 ELSE 0 END AS user_favorite,
                mrs.average_rating,
                mrs.total_ratings
            FROM movies m
            LEFT JOIN categories c ON m.category_id = c.id
            LEFT JOIN streaming_platforms s ON m.streaming_platform_id = s.id
            LEFT JOIN directors d ON m.director_id = d.id
            LEFT JOIN user_ratings ur 
                ON m.id = ur.movie_id AND ur.user_id = ?
            LEFT JOIN movie_rating_stats mrs ON m.id = mrs.movie_id
            LEFT JOIN user_favorites uf 
                ON uf.movie_id = m.id AND uf.user_id = ?
            WHERE m.id = ?
            LIMIT 1;
        """
        results = db.query(sql, [user_id, user_id, movie_id])
    else:
        sql = """
            SELECT 
                m.*,
                c.name AS genre,
                d.name AS director,
                s.name AS platform,
                mrs.average_rating,
                mrs.total_ratings
            FROM movies m
            LEFT JOIN categories c ON m.category_id = c.id
            LEFT JOIN streaming_platforms s ON m.streaming_platform_id = s.id
            LEFT JOIN directors d ON m.director_id = d.id
            LEFT JOIN movie_rating_stats mrs ON m.id = mrs.movie_id
            WHERE m.id = ?
        """
        results = db.query(sql, [movie_id])

    if not results:
        return None

    movie = dict(results[0])
    # Use average rating for display
    if movie.get("average_rating"):
        movie["rating"] = round(float(movie["average_rating"]), 1)
    movie["user_watched"] = bool(movie.get("user_watched"))
    movie["is_favorite"] = bool(movie.get("user_favorite"))

    print(movie)

    return movie


def get_movies_by_user(user_id, page=1, per_page=20):
    offset = (page - 1) * per_page
    sql = """
        SELECT m.*,
               c.name AS category_name,
               d.name AS director_name,
               s.name AS platform_name,
               ur.rating AS user_rating,
               ur.watched AS user_watched,
               ur.favorite AS user_favorite,
               ur.watch_date AS watch_date,
               mrs.average_rating,
               mrs.total_ratings
        FROM movies m
        LEFT JOIN user_ratings ur 
               ON m.id = ur.movie_id AND ur.user_id = ?
        LEFT JOIN categories c ON m.category_id = c.id
        LEFT JOIN directors d ON m.director_id = d.id
        LEFT JOIN streaming_platforms s ON m.streaming_platform_id = s.id
        LEFT JOIN movie_rating_stats mrs ON m.id = mrs.movie_id
        WHERE (m.owner_id = ? OR ur.user_id = ?) AND ur.watched = 1
        ORDER BY m.created_at DESC
        LIMIT ? OFFSET ?
    """
    results = db.query(sql, [user_id, user_id, user_id, per_page, offset])

    movies = [_transform_movie(row) for row in results]
    return movies


def get_user_movies_count(user_id):
    """Get total count of movies for a user (owned or rated)"""
    sql = """
        SELECT COUNT(DISTINCT m.id) as count
        FROM movies m
        LEFT JOIN user_ratings ur ON m.id = ur.movie_id AND ur.user_id = ?
        WHERE m.owner_id = ? OR ur.user_id = ?
    """
    result = db.query(sql, [user_id, user_id, user_id])
    return result[0]["count"] if result else 0


def add_movie(user_id, movie):
    if not user_id:
        return "User ID is required."

    # First, check if movie already exists
    sql_check = "SELECT id FROM movies WHERE LOWER(title) = LOWER(?)"
    result = db.query(sql_check, [movie["title"]])

    if result:
        # Movie exists, just add user rating
        movie_id = result[0]["id"]
    else:
        # Insert new movie into the movies table
        sql = """INSERT INTO movies
                    (title, 
                    year, 
                    duration, 
                    category_id,
                    streaming_platform_id,
                    owner_id,
                    director_id,
                    review) 
                VALUES 
                    (?, ?, ?, ?, ?, ?, ?, ?)"""

        params = (
            movie["title"],
            movie["year"] if movie["year"] else None,
            movie["duration"] if movie["duration"] else None,
            movie.get("category_id") if movie.get("category_id") else None,
            (
                movie.get("streaming_platform_id")
                if movie.get("streaming_platform_id")
                else None
            ),
            user_id,
            movie.get("director_id") if movie.get("director_id") else None,
            movie["review"] if movie["review"] else None,
        )

        movie_id = db.execute(sql, params)

    # Add user rating
    sql_rating = """INSERT OR REPLACE INTO user_ratings
                (user_id, movie_id, rating, watched, watch_date, watched_with, review, favorite)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""

    rating_value = movie.get("rating")

    params_rating = (
        user_id,
        movie_id,
        rating_value if rating_value else None,
        1,  # Mark as watched
        movie["watch_date"] if movie["watch_date"] else None,
        movie["watched_with"] if movie["watched_with"] else None,
        movie.get("review") if movie.get("review") else None,
        bool(movie.get("favorite", False)),
    )

    db.execute(sql_rating, params_rating)

    # Sync favorite status with user_favorites table
    is_favorite = bool(movie.get("favorite", False))
    if is_favorite:
        # Add to favorites if not already there
        sql_add_fav = (
            "INSERT OR IGNORE INTO user_favorites (user_id, movie_id) VALUES (?, ?)"
        )
        db.execute(sql_add_fav, [user_id, movie_id])
    else:
        # Remove from favorites if it was there
        sql_remove_fav = "DELETE FROM user_favorites WHERE user_id = ? AND movie_id = ?"
        db.execute(sql_remove_fav, [user_id, movie_id])

    return movie_id


def search_movies(user_id=None, filter_options=None, page=1, per_page=20):
    if filter_options is None:
        filter_options = {}

    offset = (page - 1) * per_page
    params = []

    query = filter_options.get("query", "").strip()
    genre = filter_options.get("genre", "").strip()
    year = filter_options.get("year", "").strip()
    platform = filter_options.get("platform", "").strip()
    rating = filter_options.get("rating", "").strip()
    sort_by = filter_options.get("sort_by", "date_added").strip()

    where = []

    # Title query
    if query:
        where.append("m.title LIKE ?")
        params.append(f"%{query}%")

    # Year filters
    year_filters = {
        "2024": "m.year = 2024",
        "2023": "m.year = 2023",
        "2022": "m.year = 2022",
        "2021": "m.year = 2021",
        "2020": "m.year = 2020",
        "2010s": "m.year BETWEEN 2010 AND 2019",
        "2000s": "m.year BETWEEN 2000 AND 2009",
        "1990s": "m.year BETWEEN 1990 AND 1999",
        "older": "m.year < 1990",
    }
    if year in year_filters:
        where.append(year_filters[year])

    # Genre
    if genre:
        where.append("c.name = ?")
        params.append(genre)

    # Platform
    if platform:
        where.append("s.name = ?")
        params.append(platform)

    # Minimum rating
    if rating:
        try:
            min_rating = float(rating)
            params.append(min_rating)
            where.append("COALESCE(mrs.average_rating, 0) >= ?")
        except ValueError:
            pass

    # WHERE clause
    where_sql = f"WHERE {' AND '.join(where)}" if where else ""

    # Sorting
    order_map = {
        "title": "m.title ASC",
        "year": "m.year DESC, m.title ASC",
        "rating": "COALESCE(mrs.average_rating, 0) DESC, m.created_at DESC",
        "date_added": "m.created_at DESC",
    }

    if sort_by == "relevance" and query:
        order_sql = (
            "CASE WHEN LOWER(m.title) = LOWER(?) THEN 0 ELSE 1 END, m.created_at DESC"
        )
        params.insert(0, query)
    else:
        order_sql = order_map.get(sort_by, "m.created_at DESC")

    sql = f"""
        SELECT
            m.id,
            m.title,
            m.year,
            m.duration,
            m.owner_id,
            m.category_id,
            m.streaming_platform_id,
            m.director_id,
            m.created_at,
            c.name AS category_name,
            d.name AS director_name,
            s.name AS platform_name,
            mrs.average_rating,
            mrs.total_ratings
        FROM movies m
        LEFT JOIN categories c ON m.category_id = c.id
        LEFT JOIN directors d ON m.director_id = d.id
        LEFT JOIN streaming_platforms s ON m.streaming_platform_id = s.id
        LEFT JOIN movie_rating_stats mrs ON m.id = mrs.movie_id
        {where_sql}
        ORDER BY {order_sql}
        LIMIT ? OFFSET ?
    """

    params.extend([per_page, offset])

    results = db.query(sql, params)
    return [_transform_movie(row) for row in results]


def get_search_count(filter_options=None):
    """Get total count of search results for accurate pagination"""
    if filter_options is None:
        filter_options = {}

    params = []

    # Extract filters
    query = filter_options.get("query", "").strip()
    genre = filter_options.get("genre", "").strip()
    year = filter_options.get("year", "").strip()
    platform = filter_options.get("platform", "").strip()
    rating = filter_options.get("rating", "").strip()

    # Build WHERE clause
    where_clauses = []

    if query:
        where_clauses.append("(m.title LIKE ?)")
        params.append(f"%{query}%")

    if year:
        year_mapping = {
            "2024": "m.year = 2024",
            "2023": "m.year = 2023",
            "2022": "m.year = 2022",
            "2021": "m.year = 2021",
            "2020": "m.year = 2020",
            "2010s": "m.year BETWEEN 2010 AND 2019",
            "2000s": "m.year BETWEEN 2000 AND 2009",
            "1990s": "m.year BETWEEN 1990 AND 1999",
            "older": "m.year < 1990",
        }
        if year in year_mapping:
            where_clauses.append(year_mapping[year])

    if genre:
        where_clauses.append("LOWER(c.name) = LOWER(?)")
        params.append(genre)

    if platform:
        where_clauses.append("LOWER(s.name) = LOWER(?)")
        params.append(platform)

    if rating:
        try:
            min_rating = float(rating)
            where_clauses.append("mrs.average_rating >= ?")
            params.append(min_rating)
        except ValueError:
            pass

    where_sql = ""
    if where_clauses:
        where_sql = " WHERE " + " AND ".join(where_clauses)

    # Optimized count query - only join necessary tables
    sql = f"""
        SELECT COUNT(DISTINCT m.id) as count
        FROM movies m
        LEFT JOIN categories c ON m.category_id = c.id
        LEFT JOIN streaming_platforms s ON m.streaming_platform_id = s.id
        LEFT JOIN movie_rating_stats mrs ON m.id = mrs.movie_id
        {where_sql}
    """

    result = db.query(sql, params)
    return result[0]["count"] if result else 0


def update_movie_owner(user_id, movie):
    if not user_id:
        return "User ID is required."

    # Update movie details owned by the user
    sql = """UPDATE movies
             SET title = ?,
                 year = ?,
                 duration = ?,
                 category_id = ?,
                 streaming_platform_id = ?,
                 director_id = ?,
                 review = ?
             WHERE id = ? AND owner_id = ?"""

    params = (
        movie["title"],
        movie["year"] if movie["year"] else None,
        movie["duration"] if movie["duration"] else None,
        movie.get("category_id") if movie.get("category_id") else None,
        (
            movie.get("streaming_platform_id")
            if movie.get("streaming_platform_id")
            else None
        ),
        movie.get("director_id") if movie.get("director_id") else None,
        movie["review"] if movie["review"] else None,
        movie["id"],
        user_id,
    )

    db.execute(sql, params)

    # Also update user_ratings if review/rating/favorite provided
    rating_value = movie.get("rating")
    if rating_value:
        if float(rating_value) > 5:
            rating_value = float(rating_value) / 2

    sql_rating = """UPDATE user_ratings
                    SET rating = ?,
                        watch_date = ?,
                        watched_with = ?,
                        review = ?,
                        favorite = ?
                    WHERE user_id = ? AND movie_id = ?"""

    params_rating = (
        rating_value if rating_value else None,
        movie["watch_date"] if movie.get("watch_date") else None,
        movie["watched_with"] if movie.get("watched_with") else None,
        movie.get("review") if movie.get("review") else None,
        bool(movie.get("favorite", False)),
        user_id,
        movie["id"],
    )

    db.execute(sql_rating, params_rating)
    return movie["id"]


def update_movie(user_id, movie):
    if not user_id:
        return "User ID is required."

    # Update user's rating for the movie
    sql = """UPDATE user_ratings
             SET rating = ?,
                 watched = ?,
                 watch_date = ?,
                 watched_with = ?,
                 favorite = ?
             WHERE user_id = ? AND movie_id = ?"""

    rating_value = movie.get("rating")

    params = (
        rating_value if rating_value else None,
        1,  # Mark as watched
        movie["watch_date"] if movie["watch_date"] else None,
        movie["watched_with"] if movie["watched_with"] else None,
        bool(movie.get("favorite", False)),
        user_id,
        movie["id"],
    )

    db.execute(sql, params)
    return movie["id"]


def delete_movie(user_id, movie_id):
    """Delete a user's rating for a movie. If no other users have rated it, delete the movie."""
    if not user_id:
        return "User ID is required."

    # First, check if the user owns this movie or has rated it
    sql_check = """SELECT m.owner_id FROM movies m
                   LEFT JOIN user_ratings ur ON m.id = ur.movie_id AND ur.user_id = ?
                   WHERE m.id = ?"""
    result = db.query(sql_check, [user_id, movie_id])

    if not result:
        return "Movie not found."

    movie_owner_id = result[0]["owner_id"]

    # If user is the owner, they can delete it
    if movie_owner_id == user_id:
        # Delete all user ratings for this movie
        sql_delete_ratings = "DELETE FROM user_ratings WHERE movie_id = ?"
        db.execute(sql_delete_ratings, [movie_id])

        # Delete the movie
        sql_delete_movie = "DELETE FROM movies WHERE id = ?"
        db.execute(sql_delete_movie, [movie_id])
    else:
        # Just delete the user's rating
        sql_delete_rating = (
            "DELETE FROM user_ratings WHERE user_id = ? AND movie_id = ?"
        )
        db.execute(sql_delete_rating, [user_id, movie_id])

    return movie_id


def add_to_favorites(user_id, movie_id):
    if not user_id:
        return "User ID is required"

    if not movie_id:
        return "Movie ID is required"

    sql = "INSERT OR IGNORE INTO user_favorites (user_id, movie_id) VALUES (?, ?)"
    db.execute(sql, [user_id, movie_id])
    return "Success"


def remove_from_favorites(user_id, movie_id):
    if not user_id:
        return "User ID is required"

    if not movie_id:
        return "Movie ID is required"

    sql = "DELETE FROM user_favorites where user_id = ? AND movie_id = ?"
    db.execute(sql, [user_id, movie_id])
    return "Success"


def get_favorites(user_id):
    if not user_id:
        return "User ID is required"

    sql = """SELECT COUNT(uf.id) as count FROM user_favorites uf WHERE user_id = ?"""
    result = db.query(sql, [user_id])
    return result[0]["count"] if result else 0


def get_favorite_movies(user_id, page=1, per_page=20):
    """Get favorite movies for a user with pagination"""
    if not user_id:
        return []

    offset = (page - 1) * per_page
    sql = """
        SELECT m.*,
               c.name AS category_name,
               d.name AS director_name,
               s.name AS platform_name,
               ur.rating AS user_rating,
               ur.watched AS user_watched,
               ur.favorite AS user_favorite,
               ur.watch_date AS watch_date,
               ur.review,
               mrs.average_rating,
               mrs.total_ratings
        FROM movies m
        INNER JOIN user_favorites uf ON m.id = uf.movie_id
        LEFT JOIN user_ratings ur 
               ON m.id = ur.movie_id AND ur.user_id = ?
        LEFT JOIN categories c ON m.category_id = c.id
        LEFT JOIN directors d ON m.director_id = d.id
        LEFT JOIN streaming_platforms s ON m.streaming_platform_id = s.id
        LEFT JOIN movie_rating_stats mrs ON m.id = mrs.movie_id
        WHERE uf.user_id = ?
        ORDER BY uf.id DESC
        LIMIT ? OFFSET ?
    """
    results = db.query(sql, [user_id, user_id, per_page, offset])
    movies = [_transform_movie(row) for row in results]
    return movies


def get_favorite_movies_count(user_id):
    """Get total count of favorite movies for a user"""
    if not user_id:
        return 0

    sql = """SELECT COUNT(uf.id) as count FROM user_favorites uf WHERE user_id = ?"""
    result = db.query(sql, [user_id])
    return result[0]["count"] if result else 0
