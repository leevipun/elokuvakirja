import db

def get_movies():
    sql = """
    SELECT m.*,
            c.name AS category_name,
            d.name AS director_name,
            s.name AS platform_name,
            AVG(CAST(ur.rating AS FLOAT)) AS average_rating,
            COUNT(ur.id) AS total_ratings
    FROM movies m
    LEFT JOIN categories c ON m.category_id = c.id
    LEFT JOIN directors d ON m.director_id = d.id
    LEFT JOIN streaming_platforms s ON m.streaming_platform_id = s.id
    LEFT JOIN user_ratings ur ON m.id = ur.movie_id
    GROUP BY m.id
    ORDER BY m.created_at DESC
    """
    results = db.query(sql)

    # Convert to list of dictionaries for easier handling
    movies = []
    for row in results:
        movie_dict = dict(row)
        # Create category object for template compatibility
        if movie_dict.get('category_name'):
            movie_dict['category'] = {'name': movie_dict['category_name']}
        # Create platform object for template compatibility
        if movie_dict.get('platform_name'):
            movie_dict['platform'] = {'name': movie_dict['platform_name']}
        # Add favorite status
        movie_dict['is_favorite'] = bool(movie_dict.get('user_favorite'))
        # Use average rating for display
        if movie_dict.get('average_rating'):
            movie_dict['rating'] = round(float(movie_dict['average_rating']), 1)
        else:
            movie_dict['rating'] = None
        movie_dict['user_watched'] = bool(movie_dict.get('user_watched'))

        movies.append(movie_dict)

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
                ur.favorite AS user_favorite,
                AVG(CAST(ur2.rating AS FLOAT)) AS average_rating,
                COUNT(ur2.id) AS total_ratings
            FROM movies m
            LEFT JOIN categories c ON m.category_id = c.id
            LEFT JOIN streaming_platforms s ON m.streaming_platform_id = s.id
            LEFT JOIN directors d ON m.director_id = d.id
            LEFT JOIN user_ratings ur ON m.id = ur.movie_id AND ur.user_id = ?
            LEFT JOIN user_ratings ur2 ON m.id = ur2.movie_id
            WHERE m.id = ?
            GROUP BY m.id
        """
        results = db.query(sql, [user_id, movie_id])
    else:
        sql = """
            SELECT 
                m.*,
                c.name AS genre,
                d.name AS director,
                s.name AS platform,
                AVG(CAST(ur.rating AS FLOAT)) AS average_rating,
                COUNT(ur.id) AS total_ratings
            FROM movies m
            LEFT JOIN categories c ON m.category_id = c.id
            LEFT JOIN streaming_platforms s ON m.streaming_platform_id = s.id
            LEFT JOIN directors d ON m.director_id = d.id
            LEFT JOIN user_ratings ur ON m.id = ur.movie_id
            WHERE m.id = ?
            GROUP BY m.id
        """
        results = db.query(sql, [movie_id])

    if not results:
        return None

    movie = dict(results[0])
    # Use average rating for display
    if movie.get('average_rating'):
        movie['rating'] = round(float(movie['average_rating']), 1)
    movie['user_watched'] = bool(movie.get('user_watched'))
    movie['is_favorite'] = bool(movie.get('user_favorite'))

    return movie

def get_movies_by_user(user_id):
    sql = """SELECT m.*,
                    c.name AS category_name,
                    d.name AS director_name,
                    s.name AS platform_name,
                    ur.rating AS user_rating,
                    ur.watched AS user_watched,
                    ur.favorite AS user_favorite,
                    AVG(CAST(ur2.rating AS FLOAT)) AS average_rating,
                    COUNT(ur2.id) AS total_ratings
             FROM user_ratings ur
             JOIN movies m ON ur.movie_id = m.id
             LEFT JOIN categories c ON m.category_id = c.id
             LEFT JOIN directors d ON m.director_id = d.id
             LEFT JOIN streaming_platforms s ON m.streaming_platform_id = s.id
             LEFT JOIN user_ratings ur2 ON m.id = ur2.movie_id
             WHERE ur.user_id = ?
             GROUP BY m.id
          """
    params = (user_id,)
    results = db.query(sql, params)

    movies = []
    for row in results:
        movie_dict = dict(row)
        # Create category object for template compatibility
        if movie_dict.get('category_name'):
            movie_dict['category'] = {'name': movie_dict['category_name']}
        # Create platform object for template compatibility
        if movie_dict.get('platform_name'):
            movie_dict['platform'] = {'name': movie_dict['platform_name']}
        # Add favorite status
        movie_dict['is_favorite'] = bool(movie_dict.get('user_favorite'))
        # Use average rating for display
        if movie_dict.get('average_rating'):
            movie_dict['rating'] = round(float(movie_dict['average_rating']), 1)
        movie_dict['user_watched'] = bool(movie_dict.get('user_watched'))

        movies.append(movie_dict)

    return movies


def add_movie(user_id, movie):
    if not user_id:
        return "User ID is required."

    # First, check if movie already exists
    sql_check = "SELECT id FROM movies WHERE LOWER(title) = LOWER(?)"
    result = db.query(sql_check, [movie["title"]])

    if result:
        # Movie exists, just add user rating
        movie_id = result[0]['id']
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
                    review, 
                    rewatchable) 
                VALUES 
                    (?, ?, ?, ?, ?, ?, ?, ?, ?)"""

        params = (
            movie["title"],
            movie["year"] if movie["year"] else None,
            movie["duration"] if movie["duration"] else None,
            movie.get("category_id") if movie.get("category_id") else None,
            movie.get("streaming_platform_id") if movie.get("streaming_platform_id") else None,
            user_id,
            movie.get("director_id") if movie.get("director_id") else None,
            movie["review"] if movie["review"] else None,
            bool(movie.get("rewatchable", False))
        )

        movie_id = db.execute(sql, params)

    # Add user rating
    sql_rating = """INSERT OR REPLACE INTO user_ratings
                (user_id, movie_id, rating, watched, watch_date, watched_with, favorite)
                VALUES (?, ?, ?, ?, ?, ?, ?)"""

    rating_value = movie.get("rating")
    if rating_value:
        # Convert from 10-point to 5-point scale if needed
        if float(rating_value) > 5:
            rating_value = float(rating_value) / 2

    params_rating = (
        user_id,
        movie_id,
        rating_value if rating_value else None,
        1,  # Mark as watched
        movie["watch_date"] if movie["watch_date"] else None,
        movie["watched_with"] if movie["watched_with"] else None,
        bool(movie.get("favorite", False))
    )

    db.execute(sql_rating, params_rating)
    return movie_id

def search_movies(user_id=None, filter_options=None):
    """Search movies based on various criteria"""
    if filter_options is None:
        filter_options = {}

    # Base SQL query
    if user_id:
        # Get user's rated movies with their ratings
        sql = """
        SELECT
            m.*,
            c.name AS category_name,
            d.name AS director_name,
            s.name AS platform_name,
            m.year AS release_year,
            ur.rating AS user_rating,
            ur.watched AS user_watched,
            ur.favorite AS user_favorite,
            AVG(CAST(ur2.rating AS FLOAT)) AS average_rating,
            COUNT(ur2.id) AS total_ratings
        FROM movies m
        LEFT JOIN categories c ON m.category_id = c.id
        LEFT JOIN directors d ON m.director_id = d.id
        LEFT JOIN streaming_platforms s ON m.streaming_platform_id = s.id
        LEFT JOIN user_ratings ur ON m.id = ur.movie_id AND ur.user_id = ?
        LEFT JOIN user_ratings ur2 ON m.id = ur2.movie_id
        """
        params = [user_id]
    else:
        # Get all movies with average ratings
        sql = """
        SELECT
            m.*,
            c.name AS category_name,
            d.name AS director_name,
            s.name AS platform_name,
            m.year AS release_year,
            AVG(CAST(ur.rating AS FLOAT)) AS average_rating,
            COUNT(ur.id) AS total_ratings
        FROM movies m
        LEFT JOIN categories c ON m.category_id = c.id
        LEFT JOIN directors d ON m.director_id = d.id
        LEFT JOIN streaming_platforms s ON m.streaming_platform_id = s.id
        LEFT JOIN user_ratings ur ON m.id = ur.movie_id
        """
        params = []

    query = filter_options.get("query", "").strip()
    genre = filter_options.get("genre", "").strip()
    year = filter_options.get("year", "").strip()
    platform = filter_options.get("platform", "").strip()
    rating = filter_options.get("rating", "").strip()
    sort_by = filter_options.get("sort_by", "relevance").strip()

    has_filters = any([query, genre, year, platform, rating])
    if user_id or has_filters:
        if not user_id:
            sql += " WHERE 1=1"

        # Add search conditions
        if query:
            sql += """ AND (
                LOWER(m.title) LIKE LOWER(?) OR 
                LOWER(d.name) LIKE LOWER(?) OR 
                LOWER(c.name) LIKE LOWER(?) OR
                LOWER(m.review) LIKE LOWER(?)
            )"""
            query_param = f"%{query}%"
            params.extend([query_param, query_param, query_param, query_param])

        # Genre filter
        if genre:
            genre_mapping = {
                'action': 'Action',
                'comedy': 'Comedy', 
                'drama': 'Drama',
                'horror': 'Horror',
                'romance': 'Romance',
                'scifi': 'Sci-Fi',
                'thriller': 'Thriller',
                'animation': 'Animation'
            }
            if genre in genre_mapping:
                sql += " AND LOWER(c.name) = LOWER(?)"
                params.append(genre_mapping[genre])

        # Year filter
        if year:
            if year == '2024':
                sql += " AND m.year = 2024"
            elif year == '2023':
                sql += " AND m.year = 2023"
            elif year == '2022':
                sql += " AND m.year = 2022"
            elif year == '2021':
                sql += " AND m.year = 2021"
            elif year == '2020':
                sql += " AND m.year = 2020"
            elif year == '2010s':
                sql += " AND m.year >= 2010 AND m.year <= 2019"
            elif year == '2000s':
                sql += " AND m.year >= 2000 AND m.year <= 2009"
            elif year == '1990s':
                sql += " AND m.year >= 1990 AND m.year <= 1999"
            elif year == 'older':
                sql += " AND m.year < 1990"

        # Platform filter
        if platform:
            platform_mapping = {
                'netflix': 'Netflix',
                'hbo': 'HBO Max',
                'disney': 'Disney+',
                'amazon': 'Amazon Prime Video',
                'apple': 'Apple TV+',
                'theater': 'Elokuvateatteri'
            }
            if platform in platform_mapping:
                sql += " AND LOWER(s.name) = LOWER(?)"
                params.append(platform_mapping[platform])

        # Rating filter (minimum rating)
        if rating:
            try:
                min_rating = float(rating)
                if user_id:
                    sql += " AND ur.rating >= ?"
                else:
                    sql += " AND AVG(CAST(ur.rating AS FLOAT)) >= ?"
                params.append(min_rating)
            except ValueError:
                pass

    # Sorting
    sql += " GROUP BY m.id"
    if sort_by == 'title':
        sql += " ORDER BY m.title ASC"
    elif sort_by == 'year':
        sql += " ORDER BY m.year DESC"
    elif sort_by == 'rating':
        sql += " ORDER BY average_rating DESC"
    elif sort_by == 'date_added':
        sql += " ORDER BY m.created_at DESC"
    else:  # relevance or default
        sql += " ORDER BY m.created_at DESC"

    results = db.query(sql, params)

    # Convert to list of dictionaries with proper formatting
    movies = []
    for row in results:
        movie_dict = dict(row)
        # Create category object for template compatibility
        if movie_dict.get('category_name'):
            movie_dict['category'] = {'name': movie_dict['category_name']}
        # Create platform object for template compatibility
        if movie_dict.get('platform_name'):
            movie_dict['platform'] = {'name': movie_dict['platform_name']}
        # Add favorite status
        movie_dict['is_favorite'] = bool(movie_dict.get('user_favorite'))
        # Use average rating for display
        if movie_dict.get('average_rating'):
            movie_dict['rating'] = round(float(movie_dict['average_rating']), 1)
        movie_dict['user_watched'] = bool(movie_dict.get('user_watched'))

        movies.append(movie_dict)

    return movies

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

    movie_owner_id = result[0]['owner_id']

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
        sql_delete_rating = "DELETE FROM user_ratings WHERE user_id = ? AND movie_id = ?"
        db.execute(sql_delete_rating, [user_id, movie_id])

    return movie_id
