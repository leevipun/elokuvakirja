from werkzeug.security import check_password_hash, generate_password_hash

import db 

def get_movies(user_id=None):
    if user_id:
        sql = """
        SELECT m.*,
               c.name AS category_name,
               d.name AS director_name,
               s.name AS platform_name
        FROM movies m
        LEFT JOIN categories c ON m.category_id = c.id
        LEFT JOIN directors d ON m.director_id = d.id
        LEFT JOIN streaming_platforms s ON m.streaming_platform_id = s.id
        WHERE m.user_id = ?
        ORDER BY m.created_at DESC
        """
        results = db.query(sql, [user_id])
    else:
        sql = """
        SELECT m.*
        FROM movies m
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
        movie_dict['is_favorite'] = bool(movie_dict.get('favorite'))
        
        # Convert rating to 5-star scale for display if rating exists
        if movie_dict.get('rating'):
            movie_dict['rating'] = int(movie_dict['rating'] / 2)
        
        movies.append(movie_dict)
        
    return movies if movies else []

def get_movie_by_id(movie_id, user_id=None):
    """Get a single movie by ID"""    
    sql = """
        SELECT 
            m.*,
            c.name AS genre,
            d.name AS director,
            s.name AS platform
        FROM movies m
        LEFT JOIN categories c ON m.category_id = c.id
        LEFT JOIN streaming_platforms s ON m.streaming_platform_id = s.id
        LEFT JOIN directors d ON m.director_id = d.id
        WHERE m.id = ?
    """
    results = db.query(sql, [movie_id])
    
    if not results:
        return None
    
    movie = dict(results[0])
    
    return movie


def add_movie(user_id, movie):
    if not user_id:
        return "User ID is required."

    
    # Insert movie into the movies table
    sql = """INSERT INTO movies 
                (title, 
                year, 
                duration, 
                category_id,
                streaming_platform_id,
                director_id,
                watch_date, 
                rating, 
                watched_with,
                review, 
                favorite, 
                rewatchable, 
                user_id) 
            VALUES 
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    
    params = (
        movie["title"],
        movie["year"] if movie["year"] else None,
        movie["duration"] if movie["duration"] else None,
        movie.get("category_id") if movie.get("category_id") else None,
        movie.get("streaming_platform_id") if movie.get("streaming_platform_id") else None,
        movie.get("director_id") if movie.get("director_id") else None,
        movie["watch_date"] if movie["watch_date"] else None,
        movie["rating"] if movie["rating"] else None,
        movie["watched_with"] if movie["watched_with"] else None,
        movie["review"] if movie["review"] else None,
        bool(movie.get("favorite", False)),
        bool(movie.get("rewatchable", False)),
        user_id
    ) 
    
    db.execute(sql, params)
    return db.last_insert_id()

def search_movies(user_id, query="", genre="", year="", platform="", rating="", sort_by="relevance"):
    """Search movies based on various criteria"""
    
    # Base SQL query
    sql = """
    SELECT 
        m.*,
        c.name AS category_name,
        d.name AS director_name,
        s.name AS platform_name,
        m.year AS release_year
    FROM movies m
    LEFT JOIN categories c ON m.category_id = c.id
    LEFT JOIN directors d ON m.director_id = d.id
    LEFT JOIN streaming_platforms s ON m.streaming_platform_id = s.id
    WHERE m.user_id = ?
    """
    
    params = [user_id]
    
    # Add search conditions
    if query:
        sql += """ AND (
            LOWER(m.title) LIKE LOWER(?) OR 
            LOWER(d.name) LIKE LOWER(?) OR 
            LOWER(c.name) LIKE LOWER(?) OR
            LOWER(m.review) LIKE LOWER(?) OR
            LOWER(m.watched_with) LIKE LOWER(?)
        )"""
        query_param = f"%{query}%"
        params.extend([query_param, query_param, query_param, query_param, query_param])
    
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
            min_rating = float(rating) * 2  # Convert from 5-star to 10-point scale
            sql += " AND m.rating >= ?"
            params.append(min_rating)
        except ValueError:
            pass
    
    # Sorting
    if sort_by == 'title':
        sql += " ORDER BY m.title ASC"
    elif sort_by == 'year':
        sql += " ORDER BY m.year DESC"
    elif sort_by == 'rating':
        sql += " ORDER BY m.rating DESC"
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
        movie_dict['is_favorite'] = bool(movie_dict.get('favorite'))
        
        # Convert rating to 5-star scale for display
        if movie_dict.get('rating'):
            movie_dict['rating'] = int(movie_dict['rating'] / 2)
        
        movies.append(movie_dict)
    
    return movies