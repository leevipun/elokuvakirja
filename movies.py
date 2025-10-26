from werkzeug.security import check_password_hash, generate_password_hash

import db 

def get_movies():
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
        movies.append(movie_dict)
        
    return movies if movies else []

def add_movie(user_id, movie):
    if not user_id:
        return "User ID is required."

    
    # Insert movie into the movies table
    sql = """INSERT INTO movies 
                (title, 
                year, 
                duration, 
                category,
                streaming_platform,
                director,
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
        movie.get("platform") if movie.get("platform") else None,
        movie.get("director") if movie.get("director") else None,
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